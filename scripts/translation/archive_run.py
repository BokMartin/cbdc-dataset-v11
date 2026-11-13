#!/usr/bin/env python3
"""Archive the call log of a translation run in the repository: data/translation/runs/<run>/CALLS.csv and RUN_META.json.

Built only from the per-chunk .meta.json files written by translate_api.py at the time of each call (no response text, no key).
The first two runs were archived by hand in the same format; this script makes the step reproducible (audit of 13 Nov 2026, item 3).

usage: archive_run.py --pack <dir> --run <run name> --scope "<what was translated and why>"
"""
import argparse, csv, glob, json, os
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--pack", required=True); ap.add_argument("--run", required=True); ap.add_argument("--scope", required=True); a = ap.parse_args()
    src = os.path.join(a.pack, "responses", a.run); rm = json.load(open(os.path.join(src, "RUN_META.json"))); rows = []
    for f in sorted(glob.glob(os.path.join(src, "*", "*.meta.json"))):
        m = json.load(open(f))
        rows.append({"doc_key": m["doc_key"], "chunk": m["chunk"], "of": m["of"], "response_file": os.path.basename(f)[:-10] + ".response.txt", "response_id": m["response_id"], "model_returned": m["model_returned"], "stop_reason": m["stop_reason"],
                     "started_utc": m["started_utc"], "seconds": m["seconds"], "input_tokens": m["usage"]["input_tokens"], "output_tokens": m["usage"]["output_tokens"], "system_sha256": m["system_sha256"], "user_sha256": m["user_sha256"],
                     "response_sha256": m["response_sha256"], "complete": m["complete"]})
    dst = os.path.join(ROOT, "data/translation/runs", a.run); os.makedirs(dst, exist_ok=True)
    with open(os.path.join(dst, "CALLS.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    rm.update({"model_returned": sorted({r["model_returned"] for r in rows}), "interface": "API (Responses API, one call per chunk, no history, no tools)", "temperature": "provider default (not sent)",
               "last_call_started_utc": max(r["started_utc"] for r in rows), "calls": len(rows), "complete": sum(bool(r["complete"]) for r in rows), "input_tokens": sum(r["input_tokens"] for r in rows),
               "output_tokens": sum(r["output_tokens"] for r in rows), "scope": a.scope, "one_request_per_conversation": "yes", "operator": "MB (run by Claude in the project container; key supplied by MB, not stored)"})
    json.dump(rm, open(os.path.join(dst, "RUN_META.json"), "w"), indent=1); print(dst, len(rows), "calls,", rm["complete"], "complete,", rm["input_tokens"], "in /", rm["output_tokens"], "out tokens")


if __name__ == "__main__": main()
