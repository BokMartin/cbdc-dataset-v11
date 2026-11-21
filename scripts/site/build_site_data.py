#!/usr/bin/env python3
"""Build the data files of the website from the committed manifests (no network, no model, deterministic).

What the site shows, and only that:
  * the analytic frame (44 projects) and the official project status of 17 Oct 2026 with its source;
  * every document the project holds (776 rows of TIERS, 4 of them candidates awaiting an author), with the authors' decision on it
    (evidence / companion / dropped / wholesale), who made the decision (an author, or a model proposal not yet
    confirmed), language, how an English text was obtained, the issuer's URL and the SHA-256 of the file we hold;
  * corpus counts per project (documents, years, tiers).

What it never shows (AGENTS.md): source text, unit texts, translations other than those listed under ADR-008, dictionary or candidate counts per project
(no ranking by amount of talk), any model label, any result of the sealed screens of 2 Nov, any F-cell value.
Internal notes of the registry and of the pre-screen are not copied either.

Inputs (all under data/):
  manifest/TIERS_2026-11-21.csv               one row per document, decision of record, tier, language, SHA-256
                                              (rows with decision CANDIDATE await an author: CANDIDATES_NIJSSE_PINTO_2026-11-21.csv)
  manifest/CORPUS_DOCUMENTS_2026-11-17.csv    evidence documents with English text: issuer, kind, text route
  manifest/ISSUERS_2026-11-13.csv             issuer and kind of evidence documents (model pre-fill, under review)
  manifest/COMPANION_LINKS_2026-11-13.csv     companions: kind, role, URL, linked evidence
  manifest/GAP_CHECK_2026-11-02.csv           gap-check candidates (CAND-<row>): issuer, type, URL
  manifest/MANUAL_DOWNLOADS_2026-11-10.csv    download provenance (URL by SHA-256)
  manifest/DOC_TITLES_2026-11-21.csv          titles read from the held files where no title was recorded
  registry/REGISTRY_v2_2.csv, registry/SOURCE_URL_AMENDMENT_2026-11-02.csv, registry/REGISTRY_ADDITIONS_2026-11-02.csv
  registry/DOC_LICENCES_2026-11-02.csv, registry/LICENCES_BY_INSTITUTION_2026-11-02.csv
  translation/ENGLISH_EDITIONS_2026-11-10.csv issuer English editions (route B) with URL
  frame/projects.csv, jurisdictions/JURISDICTION_STATUS_2026-10-17.csv
  site/PUBLISHED_TRANSLATIONS_2026-11-21.csv   machine translations an author chose to publish (ADR-008: only where the
                                              issuer's licence allows reuse); each file in site/translations/ must match
                                              the SHA-256 of its translation manifest, or the build fails

Outputs:
  site/assets/projects.json, site/assets/documents.json   read by the site
  site/data/documents.csv                                  the same document list for download

usage: python scripts/site/build_site_data.py [--check]   (--check: fail if the committed outputs are stale)
"""
import csv, hashlib, io, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
D = lambda *p: os.path.join(ROOT, "data", *p)
TIERS = "TIERS_2026-11-21.csv"
CORPUS = "CORPUS_DOCUMENTS_2026-11-17.csv"


def read(path):
    with open(path, encoding="utf-8") as f:
        return list(csv.DictReader(f))


EURO = ["AT", "BE", "BG", "HR", "CY", "EE", "FI", "FR", "DE", "GR", "IE", "IT", "LV", "LT", "LU", "MT", "NL", "PT", "SK", "SI", "ES"]
ECCU = ["AG", "DM", "GD", "KN", "LC", "VC"]
WAEMU = ["BJ", "BF", "CI", "GW", "ML", "NE", "SN", "TG"]
MEMBERS = {"EU": EURO, "ECCU": ECCU, "BCEAO": WAEMU}
NAMES = {"EU": "Euro area", "ECCU": "Eastern Caribbean Currency Union", "BCEAO": "West African Economic and Monetary Union",
         "HK": "Hong Kong SAR", "MO": "Macao SAR", "XK": "Kosovo",
         "BIS": "Bank for International Settlements", "UN": "United Nations"}
NOT_GEO = {"BIS", "UN"}
STATUS_ORDER = ["LIVE", "PILOT", "PREPARATION", "EXPLORATION", "PAUSED", "DISCONTINUED", "UNRESEARCHED", "NONE", "BANNED", "NA"]
CATEGORY = {"KEEP": "evidence", "BORDERLINE": "evidence", "COMPANION": "companion", "DROP": "dropped", "WHOLESALE": "wholesale", "CANDIDATE": "candidate", "INCLINED": "inclined"}
LANG = {"en": "English", "es": "Spanish", "zh": "Chinese", "sl": "Slovenian", "ru": "Russian", "fr": "French", "de": "German",
        "nl": "Dutch", "fi": "Finnish", "cs": "Czech", "pt": "Portuguese", "nb": "Norwegian", "no": "Norwegian", "is": "Icelandic",
        "ja": "Japanese", "id": "Indonesian", "ne": "Nepali", "hr": "Croatian", "hu": "Hungarian", "tr": "Turkish", "sk": "Slovak",
        "sv": "Swedish", "th": "Thai", "lt": "Lithuanian", "rw": "Kinyarwanda", "uk": "Ukrainian", "ar": "Arabic", "mk": "Macedonian",
        "it": "Italian", "el": "Greek", "lv": "Latvian", "et": "Estonian", "pl": "Polish", "ro": "Romanian", "bg": "Bulgarian",
        "ko": "Korean", "kk": "Kazakh", "he": "Hebrew", "da": "Danish", "sr": "Serbian", "hy": "Armenian", "mt": "Maltese"}
ISO = {  # code -> (ISO 3166 numeric = id in site/assets/vendor/countries-50m.json, English short name); Kosovo has no numeric code
    "AE": ("784", "United Arab Emirates"), "AG": ("028", "Antigua and Barbuda"), "AM": ("051", "Armenia"), "AT": ("040", "Austria"),
    "AU": ("036", "Australia"), "AW": ("533", "Aruba"), "BB": ("052", "Barbados"), "BE": ("056", "Belgium"),
    "BF": ("854", "Burkina Faso"), "BG": ("100", "Bulgaria"), "BJ": ("204", "Benin"), "BO": ("068", "Bolivia"),
    "BR": ("076", "Brazil"), "BS": ("044", "Bahamas"), "BT": ("064", "Bhutan"), "BY": ("112", "Belarus"),
    "CA": ("124", "Canada"), "CH": ("756", "Switzerland"), "CI": ("384", "Côte d'Ivoire"), "CL": ("152", "Chile"),
    "CN": ("156", "China"), "CO": ("170", "Colombia"), "CR": ("188", "Costa Rica"), "CY": ("196", "Cyprus"),
    "CZ": ("203", "Czechia"), "DE": ("276", "Germany"), "DK": ("208", "Denmark"), "DM": ("212", "Dominica"),
    "DO": ("214", "Dominican Republic"), "EC": ("218", "Ecuador"), "EE": ("233", "Estonia"), "EG": ("818", "Egypt"),
    "ES": ("724", "Spain"), "FI": ("246", "Finland"), "FR": ("250", "France"), "GD": ("308", "Grenada"),
    "GH": ("288", "Ghana"), "GN": ("324", "Guinea"), "GR": ("300", "Greece"), "GW": ("624", "Guinea-Bissau"),
    "HK": ("344", "Hong Kong"), "HR": ("191", "Croatia"), "HT": ("332", "Haiti"), "HU": ("348", "Hungary"),
    "ID": ("360", "Indonesia"), "IE": ("372", "Ireland"), "IL": ("376", "Israel"), "IN": ("356", "India"),
    "IS": ("352", "Iceland"), "IT": ("380", "Italy"), "JM": ("388", "Jamaica"), "JP": ("392", "Japan"),
    "KE": ("404", "Kenya"), "KN": ("659", "Saint Kitts and Nevis"), "KZ": ("398", "Kazakhstan"), "LC": ("662", "Saint Lucia"),
    "LT": ("440", "Lithuania"), "LU": ("442", "Luxembourg"), "LV": ("428", "Latvia"), "MA": ("504", "Morocco"),
    "MG": ("450", "Madagascar"), "MK": ("807", "North Macedonia"), "ML": ("466", "Mali"), "MO": ("446", "Macao"),
    "MT": ("470", "Malta"), "MU": ("480", "Mauritius"), "NA": ("516", "Namibia"), "NE": ("562", "Niger"),
    "NG": ("566", "Nigeria"), "NL": ("528", "Netherlands"), "NO": ("578", "Norway"), "NP": ("524", "Nepal"),
    "NZ": ("554", "New Zealand"), "PE": ("604", "Peru"), "PH": ("608", "Philippines"), "PL": ("616", "Poland"),
    "PT": ("620", "Portugal"), "PW": ("585", "Palau"), "PY": ("600", "Paraguay"), "RO": ("642", "Romania"),
    "RS": ("688", "Serbia"), "RU": ("643", "Russia"), "RW": ("646", "Rwanda"), "SE": ("752", "Sweden"),
    "SG": ("702", "Singapore"), "SI": ("705", "Slovenia"), "SK": ("703", "Slovakia"), "SN": ("686", "Senegal"),
    "SZ": ("748", "Eswatini"), "TG": ("768", "Togo"), "TH": ("764", "Thailand"), "TR": ("792", "Türkiye"),
    "TT": ("780", "Trinidad and Tobago"), "TW": ("158", "Taiwan"), "UA": ("804", "Ukraine"), "UK": ("826", "United Kingdom"),
    "US": ("840", "United States"), "UY": ("858", "Uruguay"), "VC": ("670", "Saint Vincent and the Grenadines"), "VE": ("862", "Venezuela"),
    "ZA": ("710", "South Africa"),
}


def iso(code):
    n, name = ISO.get(code, (None, code))
    return n, NAMES.get(code, name)


def decided_by(src):
    s = (src or "").lower()
    if "author" in s or s.startswith("mb"):
        return "author"
    return "model"


def clean_title(row_title, fname, did):
    t = (row_title or "").strip()
    if t and t != did and not re.fullmatch(r"[A-Z]{2,5}_[A-Za-z0-9_\-\.]+", t):
        return t, False
    base = os.path.splitext(fname or did)[0]
    base = re.sub(r"^[A-Z]{2,5}_+([A-Za-z]+_)?", "", base)
    base = re.sub(r"[_\-]+", " ", base).strip()
    return (base or did), True


def build():
    tiers = read(D("manifest", TIERS))
    corpus = {r["id"]: r for r in read(D("manifest", CORPUS))}
    issuers = {r["id"]: r for r in read(D("manifest", "ISSUERS_2026-11-13.csv"))}
    comp = {r["id"]: r for r in read(D("manifest", "COMPANION_LINKS_2026-11-13.csv"))}
    gap = read(D("manifest", "GAP_CHECK_2026-11-02.csv"))
    reg = {r["doc_id"]: r for r in read(D("registry", "REGISTRY_v2_2.csv"))}
    lic_doc = {r["doc_id"]: r for r in read(D("registry", "DOC_LICENCES_2026-11-02.csv"))}
    editions = {}
    for r in read(D("translation", "ENGLISH_EDITIONS_2026-11-10.csv")):
        if r["url"].startswith("http"):
            editions.setdefault(r["parallel_of"], r["url"])

    url = {}
    def add(i, u):
        if i and u and u.startswith("http"):
            url.setdefault(i, u.strip())
    for r in read(D("registry", "SOURCE_URL_AMENDMENT_2026-11-02.csv")):
        add(r["doc_id"], r["url"])
    for r in reg.values():
        add(r["doc_id"], r["url"] or r["source_landing_url"])
    for r in read(D("registry", "REGISTRY_ADDITIONS_2026-11-02.csv")):
        add(r["doc_id"], r["url"])
    for r in comp.values():
        add(r["id"], r["url"])
    np_cand = {r["cand_id"]: r for r in read(D("manifest", "CANDIDATES_NIJSSE_PINTO_2026-11-21.csv"))}
    for r in np_cand.values():
        add(r["cand_id"], r["pdf_url"] or r["url"])
    by_sha = {}
    for r in read(D("manifest", "MANUAL_DOWNLOADS_2026-11-10.csv")):
        if r["sha256"] and r["url"].startswith("http"):
            by_sha.setdefault(r["sha256"], r["url"])

    def cand(i):
        if i.startswith("CAND-") and i[5:].isdigit() and int(i[5:]) <= len(gap):
            return gap[int(i[5:]) - 1]
        return None

    # titles read from the documents where the manifests hold none (dated file, model reading until an author checks it)
    read_titles = {r["id"]: r for r in read(D("manifest", "DOC_TITLES_2026-11-21.csv"))}

    published = {}
    man = {}
    for f in sorted(os.listdir(D("translation"))):
        if f.startswith("TRANSLATION_MANIFEST_") and f.endswith(".csv"):
            for r in read(D("translation", f)):
                man.setdefault(r["id"], set()).add(r["translation_sha256"])
    for r in read(D("site", "PUBLISHED_TRANSLATIONS_2026-11-21.csv")):
        fp = os.path.join(ROOT, "site", "translations", r["file"])
        if not os.path.exists(fp):
            raise SystemExit(f"published translation missing: site/translations/{r['file']}")
        h = hashlib.sha256(open(fp, "rb").read()).hexdigest()
        if h != r["translation_sha256"] or h not in man.get(r["id"], set()):
            raise SystemExit(f"{r['file']}: SHA-256 {h} does not match the listed hash or any translation manifest of {r['id']}")
        published[r["id"]] = {"f": "translations/" + r["file"], "lic": r["issuer_licence"], "lu": r["licence_url"], "run": r["run"]}
    stray = set(os.listdir(os.path.join(ROOT, "site", "translations"))) - {v["f"].split("/")[1] for v in published.values()}
    if stray:
        raise SystemExit("files in site/translations/ not listed for publication: " + ", ".join(sorted(stray)))

    docs = []
    for t in tiers:
        i = t["id"]
        g = cand(i)
        if g and g["project"] != t["project"]:
            raise SystemExit(f"{i}: gap-check row {i[5:]} belongs to {g['project']}, not {t['project']}")
        if g:
            add(i, g["url"])
        if i not in url and t["sha256"] in by_sha:
            add(i, by_sha[t["sha256"]])
        c, s, k, r = corpus.get(i, {}), issuers.get(i, {}), comp.get(i, {}), reg.get(i, {})
        title, title_from_file = clean_title(t["title"], r.get("fname") or os.path.basename(t["master_path"]), i)
        title_read = 0
        if title_from_file and i in read_titles:
            title, title_from_file = read_titles[i]["title"], False
            title_read = 0 if read_titles[i]["checked_by_author"] == "yes" else 1
        lang = (t["language"] or "").replace("mixed:", "")
        issuer = c.get("issuer") or s.get("issuer") or (g or {}).get("issuer") or np_cand.get(i, {}).get("issuer") or lic_doc.get(i, {}).get("institution") or ""
        kind = c.get("kind") or s.get("kind") or k.get("kind") or (g or {}).get("doc_type") or np_cand.get(i, {}).get("doc_type") or r.get("doc_kind") or ""
        cat = CATEGORY[t["decision_v12"]]
        text = c.get("text_read", "")
        if cat == "evidence" and not text:
            text = "no English text yet"
        docs.append({
            "id": i, "p": t["project"], "y": int(t["year"]) if t["year"].isdigit() else None,
            "t": title, "tf": 1 if title_from_file else 0, "tm": title_read,
            "iss": issuer, "k": kind.replace("_", " "),
            "c": cat, "bl": 1 if t["decision_v12"] == "BORDERLINE" else 0,
            "by": decided_by(t["decision_source"]),
            "l": lang, "pg": int(t["pages"]) if (t["pages"] or "").isdigit() else None,
            "en": text, "u": url.get(i, ""), "ue": editions.get(i, ""),
            "same": t["same_publication_as"], "role": k.get("role", "").replace("_", " "),
            "link": [x for x in (k.get("linked_evidence_ids") or "").split(";") if x],
            "sha": t["sha256"], "tr": published.get(i), "ext": os.path.splitext(t["master_path"])[1].lstrip(".").lower(),
        })
    docs.sort(key=lambda d: (d["p"], -(d["y"] or 0), d["t"].lower()))

    # ---------- projects ----------
    frame = {r["project"]: r for r in read(D("frame", "projects.csv"))}
    status = {r["jur"]: r for r in read(D("jurisdictions", "JURISDICTION_STATUS_2026-10-17.csv"))}
    codes = sorted({d["p"] for d in docs} | {c for c, r in frame.items() if r["analytic_frame"] == "True"})
    projects = []
    for code in codes:
        fr = frame.get(code, {})
        st = status.get(code, {})
        mine = [d for d in docs if d["p"] == code]
        ev = [d for d in mine if d["c"] == "evidence"]
        pubs = {d["same"] or d["id"] for d in ev}
        tier = next((t["tier"] for t in tiers if t["project"] == code and t["tier"]), "")
        members = MEMBERS.get(code, [] if code in NOT_GEO else [code])
        ids = [n for n in (iso(m)[0] for m in members) if n]
        stat = (st.get("status") or fr.get("status") or "").split(" ")[0]
        ev_years = sorted({d["y"] for d in ev if d["y"]})
        projects.append({
            "code": code, "name": iso(code)[1],
            "project_name": st.get("project_name", ""),
            "frame": fr.get("analytic_frame") == "True",
            "status": stat, "status_date": st.get("status_date", ""), "status_url": st.get("source_url", ""),
            "tier": tier if fr.get("analytic_frame") == "True" else "",
            "geo": ids, "members": members if code in MEMBERS else [],
            "n": {c: sum(1 for d in mine if d["c"] == c) for c in ("evidence", "inclined", "companion", "dropped", "wholesale", "candidate")},
            "pubs": len(pubs),
            "ev_years": [ev_years[0], ev_years[-1]] if ev_years else [],
            "ev_by_year": {str(y): len({d["same"] or d["id"] for d in ev if d["y"] == y}) for y in ev_years},
            "first_year": min((d["y"] for d in mine if d["y"]), default=None),
            "english": {k: sum(1 for d in ev if d["en"] == k) for k in ("English original", "issuer's English edition", "machine translation", "no English text yet")},
        })
    meta = {
        "as_of": TIERS.split("_")[1].split(".")[0],
        "status_as_of": "2026-10-17",
        "sources": [f"data/manifest/{TIERS}", f"data/manifest/{CORPUS}", "data/manifest/COMPANION_LINKS_2026-11-13.csv",
                    "data/jurisdictions/JURISDICTION_STATUS_2026-10-17.csv"],
        "languages": LANG,
        "status_order": STATUS_ORDER,
    }
    proj_json = json.dumps({"meta": meta, "projects": projects}, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    doc_json = json.dumps({"meta": meta, "documents": docs}, ensure_ascii=False, separators=(",", ":"), sort_keys=True)

    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(["id", "project", "year", "title", "title_from_filename", "title_read_by_model_unchecked", "issuer", "kind", "decision", "borderline", "decided_by",
                "language", "pages", "english_text", "published_translation", "url", "issuer_english_edition_url", "same_publication_as", "companion_role",
                "linked_evidence", "sha256"])
    for d in docs:
        w.writerow([d["id"], d["p"], d["y"] or "", d["t"], d["tf"], d["tm"], d["iss"], d["k"], d["c"], d["bl"], d["by"], d["l"], d["pg"] or "",
                    d["en"], d["tr"]["f"] if d["tr"] else "", d["u"], d["ue"], d["same"], d["role"], ";".join(d["link"]), d["sha"]])
    return {"site/assets/projects.json": proj_json + "\n", "site/assets/documents.json": doc_json + "\n",
            "site/data/documents.csv": buf.getvalue()}, docs, projects


def main():
    outs, docs, projects = build()
    check = "--check" in sys.argv
    stale = []
    for rel, content in outs.items():
        p = os.path.join(ROOT, rel)
        old = open(p, encoding="utf-8").read() if os.path.exists(p) else None
        if old != content:
            stale.append(rel)
            if not check:
                os.makedirs(os.path.dirname(p), exist_ok=True)
                with open(p, "w", encoding="utf-8", newline="") as f:
                    f.write(content)
    frame = [p for p in projects if p["frame"]]
    from collections import Counter
    print(f"site data: {len(docs)} documents ({dict(Counter(d['c'] for d in docs))}), {len(frame)} projects in the frame, "
          f"{sum(1 for d in docs if d['u'])} with an issuer URL")
    if check and stale:
        raise SystemExit("stale site data, run python scripts/site/build_site_data.py: " + ", ".join(stale))


if __name__ == "__main__":
    main()
