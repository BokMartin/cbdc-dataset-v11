#!/usr/bin/env python3
"""Ingest a response obtained MANUALLY (e.g. OpenAI Playground) for a request that the pipeline archived, so that the result is
auditable like an API run: the system and user texts pasted by the human are hash-checked against the archived request, the raw
response is stored as-is, and the FILL is produced with the same parser and validator as the pipeline. The manifest records
`manual: true` and the human-supplied settings (model id, temperature, max output tokens, date, operator) verbatim.

usage: ingest_manual_response.py --source-run <archived run folder> --request single --response response.txt \
         --meta meta.json --schema schema/cells_v1_1.json --outroot <folder>
meta.json: {"provider": "openai", "model": "<model id shown by the Playground>", "temperature": 0, "max_output_tokens": 32000,
            "date_utc": "...", "operator": "MB", "interface": "OpenAI Playground", "notes": "..."}
"""
import argparse, csv, gzip, hashlib, json, os, sys, datetime as dt, shutil
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from extract_api import parse_array, validate_fill, sha

ap = argparse.ArgumentParser()
ap.add_argument("--source-run", required=True); ap.add_argument("--request", default="single"); ap.add_argument("--response", required=True)
ap.add_argument("--meta", required=True); ap.add_argument("--schema", required=True); ap.add_argument("--outroot", required=True)
ap.add_argument("--system-pasted", default=""); ap.add_argument("--user-pasted", default="")
a = ap.parse_args()
src = json.load(open(os.path.join(a.source_run, "MANIFEST.json"))); meta = json.load(open(a.meta)); schema = json.load(open(a.schema))
req = src[a.request]["request"] if a.request == "single" else None
if req is None: raise SystemExit("only the single request is supported for manual ingestion (two-stage needs one call per document)")
system = gzip.open(os.path.join(a.source_run, req["system"]["file"]), "rt", encoding="utf-8").read()
user = gzip.open(os.path.join(a.source_run, req["user"]["file"]), "rt", encoding="utf-8").read()
assert sha(system) == req["system"]["sha256"] and sha(user) == req["user"]["sha256"], "archived request does not match its manifest"
checks = {}
for label, pasted, ref in (("system", a.system_pasted, system), ("user", a.user_pasted, user)):
    if pasted:
        t = open(pasted, encoding="utf-8").read(); checks[label] = "identical" if t == ref else ("identical_modulo_trailing_newline" if t.rstrip("\n") == ref.rstrip("\n") else "DIFFERS")
text = open(a.response, encoding="utf-8").read()
run = os.path.join(a.outroot, f"{src['jur']}_{meta['provider']}_{meta['model']}_manual_{a.request}_{dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%SZ')}")
os.makedirs(os.path.join(run, "requests"), exist_ok=True)
for name, t in (("system", system), ("user", user), ("response", text)):
    with gzip.open(os.path.join(run, "requests", f"{a.request}.{name}.txt.gz"), "wt", encoding="utf-8") as f: f.write(t)
shutil.copy(a.meta, os.path.join(run, "MANUAL_META.json")); shutil.copy(a.response, os.path.join(run, "RAW_RESPONSE.txt"))
state = "ok"; problems = []; rows = []
try:
    rows = parse_array(text); by, problems = validate_fill(rows, schema); rows = list(by.values())
    if problems: state = "ok_with_validation_problems"
except Exception as e: state = f"processing_failed:{e!r}"
if rows:
    cols = schema["fill_columns"] + ["processing_state"]
    with open(os.path.join(run, f"FILL_{a.request}.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore"); w.writeheader()
        for r in rows: r["processing_state"] = state; w.writerow({c: r.get(c, "") for c in cols})
manifest = {"jur": src["jur"], "manual": True, "interface": meta.get("interface", ""), "operator": meta.get("operator", ""), "provider": meta["provider"], "model": meta["model"],
            "settings": {k: meta.get(k) for k in ("temperature", "max_output_tokens", "top_p", "reasoning", "other")}, "date_utc": meta.get("date_utc", ""), "notes": meta.get("notes", ""),
            "source_run": os.path.basename(a.source_run.rstrip("/")), "request": {"system": req["system"], "user": req["user"]}, "pasted_text_check": checks,
            "response_sha256": sha(text), "response_chars": len(text), "status": state, "validation_problems": problems, "schema_sha256": sha(open(a.schema, encoding="utf-8").read()),
            "contract_sha256": src.get("contract_sha256"), "ingested_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
            "caveat": "Manual run: the human-supplied settings cannot be verified from the response; token usage unavailable; treat as a development comparison unless the interface's own log is attached."}
json.dump(manifest, open(os.path.join(run, "MANIFEST.json"), "w"), indent=1); print(run, state, problems[:5])
