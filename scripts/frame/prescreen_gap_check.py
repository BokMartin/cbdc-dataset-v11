#!/usr/bin/env python3
"""Model pre-screen of gap-check candidates under SOURCE_RULE_D1, to speed up the AUTHOR decision (which remains the decision of
record). For every candidate row the model proposes one of: accept (official channel, competent body, retail CBDC of the project,
load-bearing content: a decision, a design position, a legal provision or an explicit privacy/identifiability statement),
companion (same content as a registered document: cover press release, landing page, summary), wholesale, reject (not the
competent body, no load-bearing content, out of scope, after the as-of date) or verify_first (cannot be judged from the row:
low confidence, unopened PDF). One request per project; the prompt is archived with its hash; output is a CSV the authors
edit in the `author_decision` column.

usage: prescreen_gap_check.py --candidates data/manifest/GAP_CHECK_2026-11-02.csv --rule docs/SOURCE_RULE_D1.md --registry-dir <folder with <CODE>_registry.csv> \
         --model claude-opus-5-5 --out data/manifest/GAP_CHECK_PRESCREEN_2026-11-03.csv
"""
import argparse, csv, json, os, sys, collections, datetime as dt
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE)); sys.path.insert(0, os.path.join(ROOT, "scripts", "extraction"))
from extract_api import Client, parse_array, sha, archive

SYSTEM = """You pre-screen candidate source documents for an academic dataset of OFFICIAL retail-CBDC documents. The authors want only official and
load-bearing documents: published by the competent body on its official channel, about the project's RETAIL CBDC, and carrying content that
decides or states something (a status decision, a design position, a legal provision, an explicit statement on privacy, identifiability,
data access, anonymity, offline, tiered wallets, programmability or ledger technology). Apply the rule text given below strictly. Be
conservative: when a row only mentions CBDC in passing, or is a speech without a concrete statement, or an annual-report section that
repeats a registered document, propose reject or companion, not accept.

For each candidate row return a JSON object: {"row": <row number as given>, "proposal": "accept|companion|wholesale|reject|verify_first",
"reason": "<= 25 words, naming the rule criterion (authority / scope / content / date / duplicate) that decides", "load_bearing": "status_decision|design_position|legal_provision|privacy_statement|none"}.
Return ONLY a JSON array with one object per row, in the given order.

THE RULE:
"""


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--candidates", required=True); ap.add_argument("--rule", required=True); ap.add_argument("--registry-dir", required=True)
    ap.add_argument("--provider", default="anthropic"); ap.add_argument("--model", required=True); ap.add_argument("--out", required=True); ap.add_argument("--only", default="")
    a = ap.parse_args(); rule = open(a.rule, encoding="utf-8").read().split("## Gap-check result")[0]; system = SYSTEM + rule
    rows = list(csv.DictReader(open(a.candidates, encoding="utf-8")))
    for i, r in enumerate(rows, 1): r["row"] = str(i)
    by = collections.defaultdict(list)
    for r in rows: by[r["project"]].append(r)
    cl = Client(a.provider, a.model, 16000); outdir = os.path.dirname(os.path.abspath(a.out)); reqdir = os.path.join(outdir, "prescreen_requests"); os.makedirs(reqdir, exist_ok=True)
    results = {}; meta = {"model": a.model, "provider": a.provider, "system_sha256": sha(system), "started_utc": dt.datetime.now(dt.timezone.utc).isoformat(), "projects": {}}
    for p, L in sorted(by.items()):
        if a.only and p not in a.only.split(","): continue
        regf = os.path.join(a.registry_dir, f"{p}_registry.csv"); reg = open(regf, encoding="utf-8").read() if os.path.exists(regf) else "(none)"
        user = f"PROJECT {p}\n\nDOCUMENTS ALREADY IN THE REGISTRY (title/filename, year, kind, core verdict):\n{reg}\n\nCANDIDATE ROWS:\n" + "\n".join(
            f"row {r['row']}: date={r['date']} | type={r['doc_type']} | issuer={r['issuer']} | title={r['title']} | relevance={r['relevance']} | note={r['content_note']} | confidence={r['confidence']} | already_in_registry={r['already_in_registry']} | url={r['url']}" for r in L)
        req = archive(reqdir, f"{p}.user", user)
        try:
            text, m = cl.call(system, user); arr = parse_array(text)
            for o in arr: results[str(o.get("row"))] = o
            meta["projects"][p] = {"n": len(L), "state": "ok", "response_id": m.get("response_id"), "request_sha256": req["sha256"]}
            print(f"[prescreen] {p}: {len(L)} rows ok", flush=True)
        except Exception as e:
            meta["projects"][p] = {"n": len(L), "state": f"failed:{e!r}"}; print(f"[prescreen] {p}: failed {e!r}", flush=True)
    cols = ["row", "project", "date", "doc_type", "title", "issuer", "proposal", "load_bearing", "reason", "relevance", "content_note", "confidence", "already_in_registry", "url", "author_decision", "decision_note"]
    with open(a.out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore"); w.writeheader()
        for r in rows:
            o = results.get(r["row"], {}); w.writerow({**r, "proposal": o.get("proposal", "NOT_SCREENED"), "load_bearing": o.get("load_bearing", ""), "reason": o.get("reason", ""), "author_decision": "", "decision_note": ""})
    meta["counts"] = dict(collections.Counter(results[k].get("proposal", "?") for k in results)); meta["finished_utc"] = dt.datetime.now(dt.timezone.utc).isoformat()
    json.dump(meta, open(a.out.replace(".csv", ".json"), "w"), indent=1); print(json.dumps(meta["counts"], indent=1))


if __name__ == "__main__": main()
