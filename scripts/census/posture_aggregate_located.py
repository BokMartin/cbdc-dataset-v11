#!/usr/bin/env python3
"""Aggregate-only posture statistics from the SEALED survey after the mechanical citation check (audit 2 Nov item 9): the ladder
distribution and joint counts are computed over located, eligible claims (derive.posture_level / g_indicators), and only counts
leave this script. No project is named in the output.

usage: posture_aggregate_located.py --sealed <off-repo jsonl> --texts <texts root> --frame data/frame/projects.csv --out data/census/POSTURE_LADDER_aggregate.json
"""
import argparse, csv, json, os, sys, collections, hashlib, datetime as dt
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "scripts")); sys.path.insert(0, os.path.join(ROOT, "scripts", "extraction"))
import derive
from verify_quotes import norm, load_pages, check

ap = argparse.ArgumentParser(); ap.add_argument("--sealed", required=True); ap.add_argument("--texts", required=True); ap.add_argument("--frame", required=True); ap.add_argument("--out", required=True)
a = ap.parse_args()
if os.path.abspath(a.out).startswith(os.path.join(ROOT, "data", "statements")): raise SystemExit("aggregate only")
frame = {r["project"]: r for r in csv.DictReader(open(a.frame, encoding="utf-8"))}; retail = {p for p, r in frame.items() if r["retail_candidate"] == "True"}
per = collections.defaultdict(list); cache = {}; vstates = collections.Counter(); n_docs = 0
for line in open(a.sealed, encoding="utf-8"):
    r = json.loads(line)
    if r["state"] != "ok": continue
    n_docs += 1
    docs = {x["doc"]: x for x in csv.DictReader(open(os.path.join(a.texts, r["project"], "DOCS.csv"), encoding="utf-8"))}
    d = docs[str(r["doc"])]; f = d["file"] if os.path.exists(d["file"]) else os.path.join(a.texts, r["project"], "texts", os.path.basename(d["file"]))
    if f not in cache: cache[f] = load_pages(f)
    pages, _ = cache[f]
    for s in r["statements"]:
        q = norm(s.get("quote", ""))
        try: pg = int(s.get("page"))
        except Exception: pg = None
        st, ratio, found = check(q, pages, pg) if q else ("empty", 0.0, None); vstates[st] += 1
        per[r["project"]].append({"type": s.get("type"), "status": s.get("status"), "basis": s.get("basis"), "quote_verified": st, "staff_research": d.get("staff", "")})
for p in retail: per.setdefault(p, [])
ladder = collections.Counter(); g_yes = collections.Counter(); g_status = collections.Counter(); joint = collections.Counter(); arch_any = 0; arch_located = 0
for p in retail:
    S = per[p]; lvl = derive.posture_level(S); ladder[lvl] += 1; g = derive.g_indicators(S)
    for k, v in g.items():
        if v["value"] == "yes": g_yes[k] += 1; g_status[f"{k}|{v['status'] or v['implementation']}"] += 1
    joint[(g["G2"]["value"], g["G3"]["value"])] += 1
    if any(s["type"] in derive.ARCH_TYPES for s in S): arch_any += 1
    if any(s["type"] in derive.ARCH_TYPES and derive._eligible(s) for s in S): arch_located += 1
out = {"as_of": dt.datetime.now(dt.timezone.utc).isoformat(), "n_documents": n_docs, "n_retail_projects": len(retail), "citation_states_all_statements": dict(vstates),
       "ladder_located_eligible": dict(ladder), "projects_with_any_architectural_statement_raw": arch_any, "projects_with_located_eligible_architectural_statement": arch_located,
       "G_yes_located": dict(g_yes), "G_yes_by_status": dict(g_status), "joint_G2_G3_located": {f"G2={k[0]},G3={k[1]}": v for k, v in joint.items()},
       "sealed_file_sha256": hashlib.sha256(open(a.sealed, "rb").read()).hexdigest(), "note": "Counts over located (exact/spanning), non-rejected, non-staff statements; no project named. Supersedes the raw-count ladder in the design memo."}
json.dump(out, open(a.out, "w"), indent=1); print(json.dumps(out, indent=1))
