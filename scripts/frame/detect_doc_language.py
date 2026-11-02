#!/usr/bin/env python3
"""Page-level language detection for the core documents (LANGUAGE_LEDGER audit, ADR-001 H3).

For every document in <texts>/<JUR>/DOCS.csv: detect the language of each page with >= 300 characters (lingua, high
accuracy mode), report the dominant language, the share of English pages and the full distribution, and flag documents whose
registry label disagrees with the detection (label 'en' but < 80 % English pages, or label X but dominant language != X).
Output: data/frame/doc_language_detect.csv. Detection is a diagnostic; the ledger decision is made by a human on the PDF.
"""
import csv, glob, os, re, sys, collections
from lingua import LanguageDetectorBuilder

texts, out = sys.argv[1], sys.argv[2]
det = LanguageDetectorBuilder.from_all_languages().with_preloaded_language_models().build()
rows = []
for f in sorted(glob.glob(os.path.join(texts, "*", "DOCS.csv")) + glob.glob(os.path.join(texts, "DOCS.csv"))):
    for r in csv.DictReader(open(f, encoding="utf-8")):
        p = r["file"] if os.path.exists(r["file"]) else os.path.join(os.path.dirname(f), "texts", os.path.basename(r["file"]))
        pages = re.split(r"=== DOC \d+ PAGE \d+ ===\n", open(p, encoding="utf-8", errors="replace").read())[1:]
        langs = collections.Counter()
        for t in pages:
            t = re.sub(r"\s+", " ", t).strip()
            if len(t) < 300: continue
            l = det.detect_language_of(t)
            langs[l.iso_code_639_1.name.lower() if l else "?"] += 1
        tot = sum(langs.values()) or 1; top = langs.most_common(1)[0][0] if langs else "?"; en = langs.get("en", 0) / tot
        label = r["lang"].split("/")[0]
        flag = "label_en_but_not_english" if label == "en" and en < 0.8 else ("label_disagrees" if label != "en" and top not in (label, "?") and label != "zh" else "")
        rows.append({"source_jur": r["source_jur"], "doc_id": r["doc_id"], "label": r["lang"], "dominant": top, "share_en": round(en, 2), "pages_detected": tot, "distribution": " ".join(f"{k}:{v}" for k, v in langs.most_common()), "flag": flag})
with open(out, "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
flagged = [x for x in rows if x["flag"]]
print(len(rows), "documents;", len(flagged), "flagged")
for x in flagged: print(f"  {x['source_jur']:5} {x['doc_id'][:60]:60} label={x['label']:6} dominant={x['dominant']} en={x['share_en']} ({x['distribution'][:60]})")
