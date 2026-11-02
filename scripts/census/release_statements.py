#!/usr/bin/env python3
"""Release the statement survey of EXPOSED projects only (EXPOSURE_LEDGER) from the sealed file into the repository, with the
mechanical citation check applied, for the website's "documented statements" panel.

usage: release_statements.py --sealed <off-repo .jsonl> --texts <texts root> --projects NO,UK --out data/statements
Writes <out>/<JUR>_statements.csv with columns: project, doc, doc_id, year, kind, type, status, basis, actor, page, quote, label,
quote_verified, quote_match_ratio. Refuses any project not listed in --projects (the list must match the ledger).
"""
import argparse, csv, json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "extraction"))
from verify_quotes import norm, load_pages, check

ap = argparse.ArgumentParser(); ap.add_argument("--sealed", required=True); ap.add_argument("--texts", required=True); ap.add_argument("--projects", required=True); ap.add_argument("--out", required=True)
a = ap.parse_args(); allowed = set(a.projects.split(",")); os.makedirs(a.out, exist_ok=True)
rows = {p: [] for p in allowed}; cache = {}
for line in open(a.sealed, encoding="utf-8"):
    r = json.loads(line)
    if r["project"] not in allowed or r["state"] != "ok": continue
    docs = {x["doc"]: x for x in csv.DictReader(open(os.path.join(a.texts, r["project"], "DOCS.csv"), encoding="utf-8"))}
    d = docs[str(r["doc"])]; f = d["file"] if os.path.exists(d["file"]) else os.path.join(a.texts, r["project"], "texts", os.path.basename(d["file"]))
    if f not in cache: cache[f] = load_pages(f)
    pages, _ = cache[f]
    for s in r["statements"]:
        q = norm(s.get("quote", ""))
        try: pg = int(s.get("page"))
        except Exception: pg = None
        st, ratio = check(q, pages, pg) if q else ("empty", 0.0)
        rows[r["project"]].append({"project": r["project"], "doc": r["doc"], "doc_id": r["doc_id"], "year": r["year"], "kind": r["kind"], "type": s.get("type", ""), "status": s.get("status", ""),
                                   "basis": s.get("basis", ""), "actor": s.get("actor", ""), "page": pg if pg is not None else "", "quote": s.get("quote", ""), "label": s.get("label", ""),
                                   "quote_verified": st, "quote_match_ratio": ratio})
for p, L in rows.items():
    o = os.path.join(a.out, f"{p}_statements.csv")
    with open(o, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(L[0].keys())); w.writeheader(); w.writerows(L)
    from collections import Counter; print(o, len(L), dict(Counter(x["quote_verified"] for x in L)))
