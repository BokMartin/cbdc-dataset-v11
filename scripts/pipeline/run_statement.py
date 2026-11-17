#!/usr/bin/env python3
"""Build docs/RUN_STATEMENT.md: what the paper states about every model run (model, prompt, inputs, settings), from the run records.

    python scripts/pipeline/run_statement.py            # write
    python scripts/pipeline/run_statement.py --check    # CI: the file is current and every 'run-record v1' run is complete

Runs made before the specification (docs/RUN_RECORD_SPEC.md, 17 Nov 2026) are listed with what they recorded and what they lack.
"""
import argparse, glob, json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, "docs", "RUN_STATEMENT.md")
REQUIRED = ["spec", "stage", "purpose", "provider", "interface", "model_requested", "model_returned", "parameters", "system_prompt_file",
            "system_prompt_version", "system_sha256", "user_message_format", "packing", "inputs", "git_commit", "started_utc",
            "finished_utc", "calls", "complete", "failed", "usage", "sdk", "python", "operator", "deviations"]
CALL_COLS = ["request_key", "model_returned", "stop_reason", "started_utc", "input_tokens", "output_tokens", "system_sha256",
             "user_sha256", "response_sha256", "complete"]


def rel(p): return os.path.relpath(p, ROOT).replace(os.sep, "/")


def records():
    rows, problems = [], []
    for f in sorted(glob.glob(os.path.join(ROOT, "data", "**", "RUN_META.json"), recursive=True)):
        m = json.load(open(f)); new = m.get("spec") == "run-record v1"
        if new:
            for k in REQUIRED:
                if k not in m or m[k] in ("", None): problems.append(f"{rel(f)}: field '{k}' is missing")
            calls = os.path.join(os.path.dirname(f), "CALLS.csv")
            if not os.path.exists(calls): problems.append(f"{rel(f)}: CALLS.csv is missing")
            else:
                head = open(calls, encoding="utf-8").readline().strip().split(",")
                for c in CALL_COLS:
                    if c not in head: problems.append(f"{rel(calls)}: column '{c}' is missing")
            if m.get("purpose") in ("production", "replicate", "cross_provider") and "chat" in str(m.get("interface", "")).lower():
                problems.append(f"{rel(f)}: a chat interface is not admissible for a {m['purpose']} run")
        mr = m.get("model_returned"); mr = ", ".join(mr) if isinstance(mr, list) else str(mr)
        usage = m.get("usage") or {"input_tokens": m.get("input_tokens"), "output_tokens": m.get("output_tokens")}
        params = m.get("parameters") or {"max_tokens": m.get("max_tokens"), "temperature": m.get("temperature")}
        lacks = [] if new else [k for k in ("purpose", "parameters", "inputs", "git_commit", "finished_utc", "packing") if k not in m]
        rows.append({"run": rel(os.path.dirname(f)), "stage": m.get("stage", "translation" if "/translation/" in rel(f) else "?"),
                     "purpose": m.get("purpose", "production (before spec)"), "provider": m.get("provider"), "interface": m.get("interface"),
                     "model": f"{m.get('model_requested')} → {mr}", "dates": f"{str(m.get('started_utc'))[:10]} to {str(m.get('finished_utc') or m.get('last_call_started_utc'))[:10]}",
                     "prompt": f"{m.get('system_prompt_file')} · sha256 {str(m.get('system_sha256'))[:16]}…", "params": json.dumps(params, ensure_ascii=False, sort_keys=True),
                     "inputs": "; ".join(f"{i['file']} ({str(i['sha256'])[:12]}…)" for i in m.get("inputs", [])) or m.get("scope", ""),
                     "calls": f"{m.get('complete')}/{m.get('calls')}", "tokens": f"{usage.get('input_tokens')} in / {usage.get('output_tokens')} out",
                     "commit": m.get("git_commit", "not recorded"), "lacks": ", ".join(lacks) or "nothing"})
    for f in sorted(glob.glob(os.path.join(ROOT, "data", "worked_profiles", "runs_v2_*", "MANIFEST.json"))):
        m = json.load(open(f)); calls = m.get("stage1", []) + [m[k] for k in ("single", "stage2") if isinstance(m.get(k), dict)]
        mr = sorted({c.get("model_returned") for c in calls if c.get("model_returned")}); st = sorted(c["started_utc"][:10] for c in calls if c.get("started_utc"))
        ti = sum(c.get("usage", {}).get("input_tokens", 0) for c in calls); to = sum(c.get("usage", {}).get("output_tokens", 0) for c in calls)
        rows.append({"run": rel(os.path.dirname(f)), "stage": f"extraction ({m.get('mode')}), {m.get('jur')}", "purpose": "pilot (before spec)", "provider": m.get("provider"),
                     "interface": "API, one request per call, streaming", "model": f"{m.get('model_requested')} → {', '.join(mr)}", "dates": f"{st[0]} to {st[-1]}" if st else "",
                     "prompt": "pipeline/prompts/extraction_*.system.md · sha256 " + ", ".join(f"{k} {v[:12]}…" for k, v in m.get("prompts_sha256", {}).items()),
                     "params": json.dumps({"max_tokens": m.get("max_tokens"), "temperature": m.get("temperature"), "max_doc_chars": m.get("max_doc_chars")}, ensure_ascii=False),
                     "inputs": f"{len(m.get('docs', []))} documents, text SHA-256 per document in the manifest; contract {m.get('contract_file')} ({str(m.get('contract_sha256'))[:12]}…), schema {m.get('schema_file')} ({str(m.get('schema_sha256'))[:12]}…)",
                     "calls": f"{sum(1 for c in calls if c.get('state') == 'ok')}/{len(calls)}", "tokens": f"{ti} in / {to} out",
                     "commit": "script sha256 " + str(m.get("script_sha256"))[:12] + "…", "lacks": "git_commit, reasoning setting stated explicitly, purpose"})
    return rows, problems


def render(rows):
    L = ["# Run statement: every model run behind the paper", "",
         "Generated by `scripts/pipeline/run_statement.py` from the run records; do not edit. Specification: `docs/RUN_RECORD_SPEC.md`.",
         "Model identifiers are shown as *requested → returned by the provider*. Full hashes, per-call logs and token counts are in each run folder.", ""]
    for r in rows:
        L += [f"## `{r['run']}`", "", "| | |", "|---|---|", f"| stage | {r['stage']} |", f"| purpose | {r['purpose']} |", f"| provider, interface | {r['provider']}; {r['interface']} |",
              f"| model | {r['model']} |", f"| dates of calls (UTC) | {r['dates']} |", f"| system prompt | {r['prompt']} |", f"| parameters | `{r['params']}` |",
              f"| input data | {r['inputs']} |", f"| calls complete / made | {r['calls']} |", f"| tokens | {r['tokens']} |", f"| code | {r['commit']} |",
              f"| not recorded (run predates the specification) | {r['lacks']} |", ""]
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--check", action="store_true"); a = ap.parse_args()
    rows, problems = records(); text = render(rows)
    if a.check:
        if problems: sys.exit("run records incomplete:\n  " + "\n  ".join(problems))
        if not os.path.exists(OUT) or open(OUT, encoding="utf-8").read() != text: sys.exit("docs/RUN_STATEMENT.md is not current: run scripts/pipeline/run_statement.py")
        print(f"run statement current: {len(rows)} runs")
    else:
        open(OUT, "w", encoding="utf-8").write(text); print(OUT, len(rows), "runs;", len(problems), "problems"); [print(" ", p) for p in problems]
