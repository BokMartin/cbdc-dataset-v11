#!/usr/bin/env python3
"""Unitisation for the unit-based privacy-talk instrument (v13 draft; MB agreed to the unit-based design on 12 Nov 2026).

Splits every evidence document (decision KEEP / BORDERLINE, 43-frame) that has English text into numbered sentence units BEFORE any
model sees it. English text, in this order of preference: the English original (route A), the issuer's English edition (route B),
the machine translation of record (route D). Units, not model output, are what is counted, sampled, hashed and compared.

Per document (written OUTSIDE the repository, issuers' copyright): <out>/<doc_key>.units.csv with
  unit_id (<doc_key>:p<page>:s<n>, n running through the document) · page · para (paragraph number on the page) · n_words · text
Text mode (corrected 13 Nov 2026): PDFs of routes A and B are read in READING ORDER (`pdftotext -enc UTF-8`, no -layout). The first
unitisation (12 Nov) used the `-layout` text cache, which keeps side-by-side columns on one line, so sentences of two columns were
interleaved in multi-column documents (about 25 of 250 documents heavily). HTML sources keep their visible text. Route-D text is the
machine translation of record, which was made from the -layout text layer: `layout_gap_share` in the manifest (share of long lines of
the layout text with a column gap) flags the documents where that matters; they are not re-translated here.
Rules (deterministic): page markers of the text layer are kept; lines that repeat on more than half of the pages (running heads,
footers) and bare page numbers are dropped; a paragraph is a block separated by a blank line, hyphenation at line ends is undone;
sentences are split at . ! ? ; : followed by whitespace and an upper-case letter, digit, quote or bracket; units of fewer than 4
words are attached to the previous unit of the same paragraph (headings stay as their own unit when they open a paragraph);
bracketed source terms and translator notes of route-D text stay in the unit text (they are evidence), and are ignored by dictionaries.
Repository: data/units/UNITS_MANIFEST_<date>.csv, one row per document: doc_key, id, project, tier, year, kind, issuer, issuer_type
(central_bank / government / legislature / other from the issuer string; not_recorded for registry documents, whose issuer field holds
the acquisition batch: the issuing institution of those documents still has to be recorded), route, source text SHA-256, pages, units, words, SHA-256
of the units file. Any later step can prove it coded exactly these units.

usage: unitise.py --tiers data/manifest/TIERS_2026-11-10.csv --workbook <ALL xlsx> --cache <text cache> --translations <dir> [...] --out <units dir> --date 2026-11-12
"""
import argparse, csv, glob, hashlib, json, os, re, subprocess, collections
import openpyxl
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
SPLIT = re.compile(r"(?<=[.!?;:])\s+(?=[A-Z0-9“\"(\[])")
ABBR = re.compile(r"\b(e\.g|i\.e|cf|No|Nos|Art|para|paras|p|pp|Fig|Sec|vs|etc|Dr|Mr|Ms|Mrs|Prof|Inc|Ltd|approx|incl|al)\.$")


def issuer_type(s):
    s = (s or "").lower()
    if not s.strip() or re.search(r"v1_corpus|_fetch_|web_supplement|wave1", s): return "not_recorded"  # registry rows carry the acquisition batch, not the issuer
    if re.search(r"parliament|legislat|congress|duma|assembly|national people|gazette|law\b|riksdag|storting|kamer", s): return "legislature"
    if re.search(r"ministr|treasury|government|department of|cabinet|president|finance\b|ministerie|council of ministers", s): return "government"
    if re.search(r"bank|monetary|reserve|riksbank|authority|banco|banque|banka|nbk|boj|ecb|eurosystem|payment corporation|bis\b", s): return "central_bank"
    return "other"


GAP = re.compile(r"\S.{24,}\S {3,}\S.{24,}\S")


def gap_share(layout_text):
    L = [l for l in layout_text.split("\n") if len(l.strip()) > 40]
    return round(sum(bool(GAP.search(l)) for l in L) / max(1, len(L)), 3)


def reading_order(pdf, cache_dir, sha):
    """Reading-order text of a PDF with the same page markers as the layout cache; cached as <sha>.txt in cache_dir."""
    f = os.path.join(cache_dir, sha + ".txt")
    if not os.path.exists(f):
        raw = subprocess.run(["pdftotext", "-enc", "UTF-8", pdf, "-"], capture_output=True).stdout.decode("utf-8", "replace")
        pages = raw.split("\f"); pages = pages[:-1] if pages and not pages[-1].strip() else pages
        open(f, "w", encoding="utf-8").write("".join(f"=== PAGE {i} ===\n{t}\n" for i, t in enumerate(pages, 1)))
    return f


def units_of(text):
    text = re.sub(r"(?m)^#.*\n", "", text); parts = re.split(r"=== PAGE ([\d.]+) ===\n?", text)[1:]
    pages = collections.OrderedDict()
    for n, t in zip(parts[0::2], parts[1::2]): pages.setdefault(n.split(".")[0], []).append(t)
    pages = {n: "\n".join(v) for n, v in pages.items()}
    cnt = collections.Counter()
    for t in pages.values():
        for l in {re.sub(r"\d+", "#", l.strip()) for l in t.split("\n") if l.strip()}: cnt[l] += 1
    rep = {l for l, c in cnt.items() if len(pages) >= 6 and c > len(pages) / 2}
    out = []; k = 0
    for n, t in pages.items():
        lines = [l for l in t.split("\n") if not (l.strip() and (re.sub(r"\d+", "#", l.strip()) in rep or re.fullmatch(r"[\s\d.\-–|/ivxIVX]+", l)))]
        t = re.sub(r"(\w)-\n\s*(?=[a-z])", r"\1", "\n".join(lines))
        for pi, para in enumerate([p for p in re.split(r"\n\s*\n", t) if p.strip()], 1):
            para = re.sub(r"\s+", " ", para).strip(); sents = []
            for s in SPLIT.split(para):
                if sents and (ABBR.search(sents[-1]) or len(s.split()) < 4): sents[-1] += " " + s
                else: sents.append(s)
            for s in sents:
                k += 1; out.append((n, pi, k, s))
    return out, len(pages)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--tiers", required=True); ap.add_argument("--workbook", required=True); ap.add_argument("--cache", required=True); ap.add_argument("--translations", nargs="+", required=True)
    ap.add_argument("--editions", default=os.path.join(ROOT, "data/translation/ENGLISH_EDITIONS_2026-11-10.csv")); ap.add_argument("--out", required=True); ap.add_argument("--date", required=True)
    ap.add_argument("--pdfmap", required=True, help="JSON sha256 -> local path of the master file"); ap.add_argument("--rocache", required=True, help="directory for reading-order text of PDFs")
    a = ap.parse_args(); os.makedirs(a.out, exist_ok=True); os.makedirs(a.rocache, exist_ok=True); local = json.load(open(a.pdfmap))
    ws = openpyxl.load_workbook(a.workbook, read_only=True)["ALL_DOCUMENTS"]; R = list(ws.iter_rows(values_only=True)); h = R[0]; W = {r[h.index("id")]: dict(zip(h, r)) for r in R[1:]}
    tr = {}
    for d in a.translations:
        for f in glob.glob(os.path.join(d, "*.en.txt")): tr[os.path.basename(f)[:-7]] = f
    ed = {e["parallel_of"]: e for e in csv.DictReader(open(a.editions, encoding="utf-8")) if e["sha256"]}
    # audit of 13 Nov 2026, item 2: a benchmark translation is never production text, and a publication is read once, through its English edition
    bench = {q["doc_key"] for f in glob.glob(os.path.join(ROOT, "data/translation/TRANSLATION_QUEUE_*.csv")) for q in csv.DictReader(open(f, encoding="utf-8")) if q["priority"] == "BENCH"}
    tr = {k: v for k, v in tr.items() if k not in bench}
    link = {r["original_id"]: r["english_id"] for r in csv.DictReader(open(os.path.join(ROOT, "data/manifest/EDITION_LINKS.csv"), encoding="utf-8"))}
    T = list(csv.DictReader(open(a.tiers, encoding="utf-8"))); evid = {r["id"] for r in T if r["decision_v12"] in ("KEEP", "BORDERLINE")}
    rows = []; skipped = []
    for r in csv.DictReader(open(a.tiers, encoding="utf-8")):
        if r["decision_v12"] not in ("KEEP", "BORDERLINE") or r["tier"] == "out_of_frame": continue
        if link.get(r["id"]) in evid: skipped.append({"id": r["id"], "project": r["project"], "reason": "same publication as its English edition " + link[r["id"]] + " (read there)"}); continue
        key = re.sub(r"[^A-Za-z0-9_-]+", "-", f"{r['project']}_{r['id']}")[:70]; path = route = None
        if r["language"] == "en" and r["sha256"] and (os.path.exists(os.path.join(a.cache, r["sha256"] + ".txt")) or os.path.exists(local.get(r["sha256"], "-"))): path, route = os.path.join(a.cache, r["sha256"] + ".txt"), ("B" if r["id"] in link.values() else "A")
        elif r["id"] in ed and os.path.exists(os.path.join(a.cache, ed[r["id"]]["sha256"] + ".txt")): path, route = os.path.join(a.cache, ed[r["id"]]["sha256"] + ".txt"), "B"
        elif key in tr: path, route = tr[key], "D"
        if not path: skipped.append({"id": r["id"], "project": r["project"], "reason": r["language"] and r["language"] != "en" and "no English text (" + r["language"] + ")" or r["text_flag"] or "no file"}); continue
        src_sha = r["sha256"] if (route != "B" or r["language"] == "en") else ed[r["id"]]["sha256"]; lay = os.path.join(a.cache, r["sha256"] + ".txt") if route == "D" else path
        gs = gap_share(open(lay, encoding="utf-8").read()) if os.path.exists(lay) else ""; mode = "translation_of_layout_text" if route == "D" else "layout_or_html"
        lp = local.get(src_sha, "")
        if route in "AB" and lp.lower().endswith(".pdf") and os.path.exists(lp): path = reading_order(lp, a.rocache, src_sha); mode = "reading_order"
        elif route in "AB": mode = "html_visible_text" if lp.lower().endswith((".html", ".htm")) else "layout"
        raw = open(path, encoding="utf-8").read(); U, np_ = units_of(raw)
        if len(U) < 3: skipped.append({"id": r["id"], "project": r["project"], "reason": "text layer too thin"}); continue
        f = os.path.join(a.out, key + ".units.csv")
        with open(f, "w", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh); w.writerow(["unit_id", "page", "para", "n_words", "text"])
            for n, pi, k, s in U: w.writerow([f"{key}:p{n}:s{k}", n, pi, len(s.split()), s])
        w_ = W.get(r["id"], {})
        rows.append({"doc_key": key, "id": r["id"], "project": r["project"], "tier": r["tier"], "year": r["year"], "kind": w_.get("kind") or "", "issuer": w_.get("issuer") or "", "issuer_type": issuer_type(w_.get("issuer")), "route": route, "text_mode": mode, "layout_gap_share": gs,
                     "text_sha256": hashlib.sha256(raw.encode("utf-8")).hexdigest(), "pages": np_, "units": len(U), "words": sum(len(u[3].split()) for u in U), "units_sha256": hashlib.sha256(open(f, "rb").read()).hexdigest()})
    for name, data in ((f"UNITS_MANIFEST_{a.date}.csv", rows), (f"UNITS_NOT_UNITISED_{a.date}.csv", skipped)):
        with open(os.path.join(ROOT, "data/units", name), "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=list(data[0].keys())); w.writeheader(); w.writerows(data)
    print(len(rows), "documents,", sum(r["units"] for r in rows), "units,", len({r["project"] for r in rows}), "projects;", dict(collections.Counter(r["route"] for r in rows)), dict(collections.Counter(r["issuer_type"] for r in rows)), "; not unitised:", len(skipped))


if __name__ == "__main__": main()
