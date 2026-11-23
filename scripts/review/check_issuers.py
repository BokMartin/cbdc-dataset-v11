#!/usr/bin/env python3
"""Machine check of issuer, issuer type and document kind of every unitised document (MB, 23 Nov 2026: "tohle ručně dělat
nebudeme - to musí jít lépe strojově"). No model and no paid call: every signal is read from files.

The pre-fill (data/manifest/ISSUERS_<date>.csv, made by a model from title pages on 13 Nov) is compared with independent signals:
  issuer       A. the issuer's name, its short form or its acronym occurs on pages 1-6 of the unit text (the text itself);
               B. the web domain the document was downloaded from (source manifest, manual downloads) belongs to the same issuer
                  as the other documents from that domain (majority of the pre-fill per domain, at least 2 other documents);
  issuer_type  C. the type follows from the issuer's name by the written rule of record_issuers.norm();
  kind         D. the first word in the title that names the genre without doubt (press release, speech, annual report,
                  act or notice, minutes, FAQ, consultation, responses to a consultation) contradicts the recorded kind.
                  Report-like kinds (report, pilot, progress, technical, white paper, design note) are not checked: no title word
                  decides between them.
A row is `agree` when no signal contradicts it, `conflict` when one does (the reason is given), `no_signal` when no signal could be
read (then the pre-fill stands, as for a row that agrees). For the issuer, `agree_weak` means that the only support is one word of
the name on the first pages (often the country) and no domain check was possible: not contradicted, but not shown either.
Only conflicts go to the authors.

Output: data/manifest/ISSUERS_CHECK_<date>.csv (one row per document: the three statuses and the reasons; no source text beyond
the issuer's name). Unit texts are read from --units and never copied.

usage: check_issuers.py --units <units dir> --date 2026-11-23 [--issuers data/manifest/ISSUERS_2026-11-13.csv]
"""
import argparse
import collections
import csv
import glob
import os
import re
import sys
from urllib.parse import urlparse

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)

STOP = {"of", "the", "and", "for", "de", "del", "la", "le", "du", "van", "der", "des", "on", "in", "a"}

# D: genre words. A rule fires on the title (or page 1) and names the kinds it allows.
KIND_RULES = [
    ("press release", re.compile(r"(?<!with )\b(press|news|media) (release|statement)\b|新聞稿", re.I), {"press_release"}),
    ("speech", re.compile(r"\bspeech\b|\bremarks\b|\bkeynote\b|\baddress (by|at)\b|\binterview\b|演講|講演|致辞", re.I), {"speech"}),
    ("annual report", re.compile(r"\bannual report\b|年報|年次報告", re.I), {"annual_report", "annual_report_chapter"}),
    ("act, bill or notice", re.compile(r"\b(Act|Bill|Notice|Regulations?|Decree|Gazette),? (No\.? ?)?\d{4}\b|\bOfficial Gazette\b|\bBill\b \d|\bLaw\b (No|on)\b|Federal Law", 0), {"legislation", "consultation", "decision"}),
    ("minutes", re.compile(r"\bminutes\b|\bsummary of (the )?discussion\b|\bmeeting (record|summary)\b", re.I), {"minutes"}),
    ("FAQ", re.compile(r"\bFAQs?\b|frequently asked questions", re.I), {"faq", "explainer"}),
    ("responses to a consultation", re.compile(r"\b(response|responses|reply|feedback) (to|on)\b.{0,90}\bconsultation\b|\bsummary of responses\b|\bfeedback statement\b|survey results|問卷調查結果", re.I), {"consultation_response"}),
    ("consultation paper", re.compile(r"\bconsultation (paper|document)\b|\bpublic consultation on\b", re.I), {"consultation", "legislation"}),
]


def domain(url):
    h = urlparse(url).netloc.lower().split(":")[0]
    h = re.sub(r"^www\d?\.", "", h)
    parts = h.split(".")
    # keep the registrable part: bankofengland.co.uk, boj.or.jp, rbnz.govt.nz, ecb.europa.eu
    if len(parts) >= 3 and (parts[-2] in ("co", "or", "ac", "gov", "govt", "go", "com", "org", "gob", "gv", "europa") or len(parts[-1]) == 2 and len(parts[-2]) <= 3):
        return ".".join(parts[-3:])
    return ".".join(parts[-2:])


def name_keys(issuer):
    """Strings that, found on the first pages, show the issuer: the name before any bracket, its acronym, and the bracketed short form."""
    s = issuer or ""
    main = re.split(r"\s*[(/;]|\s+(?:and|with)\s+", s)[0].strip()
    keys = {main} if len(main) > 3 else set()
    words = [w for w in re.findall(r"[A-Za-zÀ-ž]+", main) if w.lower() not in STOP]
    if len(words) >= 2:
        acr = "".join(w[0] for w in words).upper()
        if len(acr) >= 3:
            keys.add(acr)
    for b in re.findall(r"\(([^)]+)\)", s):
        if len(b) <= 60:
            keys.add(b.strip())
    if re.search(r"Taiwan|Republic of China", s):
        keys |= {"中央銀行", "Central Bank of the Republic of China"}
    if s.startswith("Government of Japan") or "Ministry of Finance" in s and "Japan" in s:
        keys |= {"財務省", "Ministry of Finance"}
    if "Bank of Japan" in s:
        keys |= {"日本銀行"}
    # a distinctive word of the name (not a generic institution word), as a stem: "Riksbank", "Sloven", "Itali", "Kazakhstan"
    for w in words:
        if len(w) >= 5 and w.lower() not in GENERIC:
            keys.add(w[:6] if len(w) > 7 else w)
    return {k for k in keys if k}


GENERIC = {"bank", "banka", "banco", "banque", "banca", "banky", "central", "centrale", "national", "nationale", "reserve", "monetary",
           "authority", "republic", "ministry", "ministerie", "finance", "financial", "government", "federal", "state", "people",
           "royal", "corporation", "payment", "foiben", "commission", "council", "treasury", "digital"}


def found(keys, text):
    for k in keys:
        if re.fullmatch(r"[A-Z]{3,}", k):
            if re.search(r"\b" + re.escape(k) + r"\b", text):
                return k
        elif k.lower() in text.lower():
            return k
    return ""


def urls_by_id():
    out = {}
    sm = os.path.join(ROOT, "data/manifest/SOURCE_MANIFEST_v12_DRAFT.csv")
    for r in csv.DictReader(open(sm, encoding="utf-8")):
        u = r.get("url_amended") or r.get("url") or ""
        if u.startswith("http") and domain(u) not in ("", "web.archive.org"):
            out[r["doc_id"]] = u
    sha_url = {}
    for f in sorted(glob.glob(os.path.join(ROOT, "data/manifest/MANUAL_DOWNLOADS_*.csv"))):
        for r in csv.DictReader(open(f, encoding="utf-8")):
            if r.get("sha256") and (r.get("url") or "").startswith("http"):
                sha_url[r["sha256"]] = r["url"]
    tiers = sorted(glob.glob(os.path.join(ROOT, "data/manifest/TIERS_*.csv")))[-1]
    for r in csv.DictReader(open(tiers, encoding="utf-8")):
        if r["id"] not in out and r.get("sha256") in sha_url:
            out[r["id"]] = sha_url[r["sha256"]]
    return out


BATCH = re.compile(r"v1_corpus|_fetch_|web_supplement|wave1|^$")  # registry rows that carry the acquisition batch, not an issuer
CB_WORD = re.compile(r"\b(bank|banka|banco|banque|banca|pank|banky|riksbank|monetary authority)\b", re.I)


def same_issuer(x, y):
    cut = lambda s: re.split(r"\s*[(,/;]|\s+(?:and|with)\s+", s)[0].strip().lower()
    return cut(x) == cut(y) or cut(x) in y.lower() or cut(y) in x.lower()


def main(argv=None):
    from record_issuers import norm
    ap = argparse.ArgumentParser()
    ap.add_argument("--units", required=True)
    ap.add_argument("--date", required=True)
    ap.add_argument("--issuers", default=os.path.join(ROOT, "data/manifest/ISSUERS_2026-11-13.csv"))
    a = ap.parse_args(argv)
    man = {r["id"]: r for r in csv.DictReader(open(sorted(glob.glob(os.path.join(ROOT, "data/units/UNITS_MANIFEST_*.csv")))[-1], encoding="utf-8"))}
    pre = {r["id"]: r for r in csv.DictReader(open(a.issuers, encoding="utf-8"))}
    tiers = {r["id"]: r for r in csv.DictReader(open(sorted(glob.glob(os.path.join(ROOT, "data/manifest/TIERS_*.csv")))[-1], encoding="utf-8"))}
    titles = {r["id"]: r["title"] for r in csv.DictReader(open(os.path.join(ROOT, "data/manifest/DOC_TITLES_2026-11-21.csv"), encoding="utf-8"))}
    url = urls_by_id()
    rows = []
    for i, m in man.items():
        p = pre.get(i, {"issuer": m["issuer"], "issuer_type": m["issuer_type"], "kind": m["kind"]})
        issuer, typ, kind = p["issuer"], p["issuer_type"], p["kind"]
        units = list(csv.DictReader(open(os.path.join(a.units, m["doc_key"] + ".units.csv"), encoding="utf-8")))
        head = " ".join(u["text"] for u in units if u["page"].isdigit() and int(u["page"]) <= 6)
        page1 = " ".join(u["text"] for u in units if u["page"] == min((x["page"] for x in units), key=lambda x: int(x) if x.isdigit() else 9999))
        title = titles.get(i) or tiers.get(i, {}).get("title", "")
        rows.append({"id": i, "project": m["project"], "issuer": issuer, "issuer_type": typ, "kind": kind, "title": title,
                     "head": head, "page1": page1[:3000], "url": url.get(i, ""), "in_prefill": i in pre})
    by_dom = collections.defaultdict(list)
    for r in rows:
        if r["url"]:
            by_dom[domain(r["url"])].append(r)
    out = []
    for r in rows:
        why_i, why_t, why_k = [], [], []
        sig_i = []
        if BATCH.search(r["issuer"]):
            why_i.append(f"no issuer recorded (the field holds the acquisition batch {r['issuer']!r})")
        keys = name_keys(r["issuer"]) if not BATCH.search(r["issuer"]) else set()
        hit = found(keys, r["head"]) if r["head"] and keys else ""
        if r["head"] and keys:
            sig_i.append("name on pages 1-6: " + (hit if hit else "not found"))
            if not hit:
                why_i.append("the issuer's name, short form or acronym is not on pages 1-6")
        d = domain(r["url"]) if r["url"] else ""
        if d:
            others = [o["issuer"] for o in by_dom[d] if o is not r]
            if len(others) >= 2:
                top, n = collections.Counter(others).most_common(1)[0]
                sig_i.append(f"domain {d}: {n} of {len(others)} other documents by {top}")
                if not any(same_issuer(r["issuer"], o) for o in others) and n / len(others) >= 0.6:
                    why_i.append(f"downloaded from {d}, where the other documents are by {top}")
            else:
                sig_i.append(f"domain {d}: too few other documents")
        full = re.split(r"\s*[(/;]|\s+(?:and|with)\s+", r["issuer"])[0].strip()
        dom_ok = any(x.startswith("domain") and "too few" not in x for x in sig_i)
        strong = dom_ok or (hit and (hit == full or re.fullmatch(r"[A-Z]{3,}", hit) or len(hit) > 12))
        t_rule = norm(r["issuer"], r["kind"])[0]
        if t_rule == "other" and CB_WORD.search(re.split(r"\s*[(/;]|\s+(?:and|with)\s+", r["issuer"])[0]):
            t_rule = "central_bank"  # norm() misses "Eesti Pank", "Banca d'Italia": its central-bank pattern needs a word it lacks
        if BATCH.search(r["issuer"]):
            pass  # the type cannot be checked without an issuer; the issuer conflict says so
        elif t_rule != r["issuer_type"]:
            why_t.append(f"the name gives {t_rule} by the rule of record_issuers.norm()")
        for label, rx, allowed in KIND_RULES:
            if rx.search(r["title"]):  # the first genre word of the title decides; page text names other genres too often
                if r["kind"] not in allowed:
                    why_k.append(f"title says {label}")
                break
        st = lambda why, sig: "conflict" if why else ("agree" if sig else "no_signal")
        out.append({"id": r["id"], "project": r["project"], "issuer": r["issuer"], "issuer_type": r["issuer_type"], "kind": r["kind"], "title": r["title"],
                    "issuer_check": st(why_i, sig_i) if why_i or not sig_i else ("agree" if strong else "agree_weak"), "issuer_type_check": st(why_t, True), "kind_check": st(why_k, True),
                    "reasons": "; ".join(why_i + why_t + why_k), "signals": "; ".join(sig_i),
                    "prefill": "ISSUERS_2026-11-13" if r["in_prefill"] else "unit manifest (not in the pre-fill)"})
    f = os.path.join(ROOT, "data/manifest", f"ISSUERS_CHECK_{a.date}.csv")
    with open(f, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, list(out[0]))
        w.writeheader()
        w.writerows(sorted(out, key=lambda x: (x["project"], x["id"])))
    c = {k: collections.Counter(o[k] for o in out) for k in ("issuer_check", "issuer_type_check", "kind_check")}
    print(f"{len(out)} documents;", {k: dict(v) for k, v in c.items()}, "; rows with a conflict:", sum(bool(o["reasons"]) for o in out))
    return out


if __name__ == "__main__":
    main()
