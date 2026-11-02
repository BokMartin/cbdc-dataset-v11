#!/usr/bin/env python3
"""Consolidate the per-project gap-check outputs (model-assisted search under SOURCE_RULE_D1) into one table and a coverage summary.

usage: consolidate_gap_check.py <folder with <CODE>_candidates.csv and <CODE>_coverage.txt> data/manifest/GAP_CHECK_2026-11-02.csv
The candidates are PROPOSALS: nothing enters the registry until an author confirms eligibility (column `author_decision`, empty).
"""
import csv, glob, os, sys, json, collections, datetime as dt

src, out = sys.argv[1], sys.argv[2]
COLS = ["project", "title", "date", "issuer", "doc_type", "url", "language", "relevance", "content_note", "confidence", "already_in_registry"]
rows = []; cov = {}
for f in sorted(glob.glob(os.path.join(src, "*_candidates.csv"))):
    code = os.path.basename(f).split("_")[0]
    try:
        for r in csv.DictReader(open(f, encoding="utf-8")):
            if not any(r.values()): continue
            rows.append({c: (r.get(c) or "").strip() for c in COLS} | {"project": code, "author_decision": "", "decision_note": ""})
    except Exception as e: print("unreadable", f, e)
for f in sorted(glob.glob(os.path.join(src, "*_coverage.txt"))):
    code = os.path.basename(f).split("_")[0]; cov[code] = open(f, encoding="utf-8").read().strip()
seen = set(); dedup = []
for r in rows:
    k = (r["project"], r["url"].rstrip("/").lower() or r["title"].lower())
    if k in seen: continue
    seen.add(k); dedup.append(r)
dedup.sort(key=lambda r: (r["project"], r["date"]))
with open(out, "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=COLS + ["author_decision", "decision_note"]); w.writeheader(); w.writerows(dedup)
by = collections.Counter(r["project"] for r in dedup); newc = collections.Counter(r["project"] for r in dedup if r["already_in_registry"].lower().startswith("no"))
judg = {}
for c, t in cov.items():
    tl = t.lower(); judg[c] = "major gaps" if "major gap" in tl else ("minor gaps" if "minor gap" in tl else ("complete" if "complete" in tl else "unclear"))
summary = {"generated_utc": dt.datetime.now(dt.timezone.utc).isoformat(), "projects_with_output": sorted(set(list(by) + list(cov))), "n_candidates": len(dedup), "n_new_candidates": sum(newc.values()),
           "candidates_by_project": dict(by), "new_by_project": dict(newc), "coverage_judgement": judg, "by_doc_type": dict(collections.Counter(r["doc_type"] for r in dedup)),
           "by_confidence": dict(collections.Counter(r["confidence"] for r in dedup)), "note": "model-assisted search; author confirmation pending for every row"}
json.dump({"summary": summary, "coverage_notes": cov}, open(out.replace(".csv", ".json"), "w"), indent=1, ensure_ascii=False)
print(json.dumps(summary, indent=1))
