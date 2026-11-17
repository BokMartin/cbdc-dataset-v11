#!/usr/bin/env python3
"""Build docs/RUN_STATEMENT.md: what the paper states about every model run (model, prompt, inputs, settings), from the run records.

    python scripts/pipeline/run_statement.py            # write
    python scripts/pipeline/run_statement.py --check    # CI: the file is current and every 'run-record v1' run is complete

Runs made before the specification (docs/RUN_RECORD_SPEC.md, 17 Nov 2026) are listed with what they recorded and what they lack.
"""
import argparse, csv, glob, hashlib, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, "docs", "RUN_STATEMENT.md")
REQUIRED = ["spec", "stage", "purpose", "provider", "interface", "model_requested", "model_returned", "parameters", "system_prompt_file",
            "system_prompt_version", "system_sha256", "user_message_format", "packing", "inputs", "git_commit", "started_utc",
            "finished_utc", "calls", "complete", "failed", "usage", "sdk", "python", "operator", "deviations"]


LEGACY = {"data/translation/runs/openai_gpt-6-astra_api_20261110", "data/translation/runs/openai_gpt-6-astra_api_20261111",
          "data/translation/runs/openai_gpt-6-astra_api_20261113"}   # runs made before the specification; nothing may be added here
STAGES = {"talk_L1", "talk_L2", "translation", "extraction_single", "extraction_stage1", "extraction_stage2"}
PURPOSES = {"development", "production", "replicate", "cross_provider"}
INTERFACES = {"anthropic.messages", "anthropic.message_batches", "openai.responses", "openai.batch", "openai.chat_completions",
              "deepseek.chat_completions", "deepseek.responses"}
CALL_COLS = ["request_key", "attempt", "unit_ids", "response_id", "model_returned", "stop_reason", "started_utc", "input_tokens", "cached_input_tokens",
             "output_tokens", "reasoning_tokens", "system_sha256", "user_sha256", "response_sha256", "complete", "parsed_ok", "parse_error"]
HEX = re.compile(r"^[0-9a-f]{64}$")


def rel(p): return os.path.relpath(p, ROOT).replace(os.sep, "/")


def sha_file(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def validate_run(folder, root=ROOT):
    """Problems of one 'run-record v1' folder. Checks artifacts, not only that fields exist (audit A4 of 17 Nov 2026, F05)."""
    P = []; m = json.load(open(os.path.join(folder, "RUN_META.json"))); name = os.path.relpath(folder, root).replace(os.sep, "/")
    for k in REQUIRED:
        if k not in m or m[k] in ("", None, [], {}): P.append(f"field '{k}' is missing or empty")
    if P: return [f"{name}: {x}" for x in P]
    if m["stage"] not in STAGES: P.append(f"stage '{m['stage']}' is not one of {sorted(STAGES)}")
    if m["purpose"] not in PURPOSES: P.append(f"purpose '{m['purpose']}' is not one of {sorted(PURPOSES)}")
    if m["interface"] not in INTERFACES: P.append(f"interface '{m['interface']}' is not a provider API endpoint of the list in run_statement.py")
    if not isinstance(m["parameters"], dict): P.append("parameters is not an object")
    if not HEX.match(str(m["system_sha256"])): P.append("system_sha256 is not a SHA-256")
    sp = os.path.join(folder, "SYSTEM_PROMPT.md")
    if not os.path.exists(sp): P.append("SYSTEM_PROMPT.md (the exact system prompt of the run) is missing")
    elif sha_file(sp) != m["system_sha256"]: P.append("SYSTEM_PROMPT.md does not have the recorded system_sha256")
    if not re.match(r"^[0-9a-f]{40}$", str(m["git_commit"])): P.append("git_commit is not a full commit hash")
    for i in m["inputs"] if isinstance(m["inputs"], list) else []:
        f = os.path.join(root, str(i.get("file", "")))
        if not HEX.match(str(i.get("sha256", ""))): P.append(f"input {i.get('file')}: no SHA-256")
        elif i.get("in_repository", True) and not os.path.exists(f): P.append(f"input {i.get('file')}: file not in the repository")
        elif i.get("in_repository", True) and sha_file(f) != i["sha256"]: P.append(f"input {i.get('file')}: file differs from the recorded SHA-256")
    cf = os.path.join(folder, "CALLS.csv")
    if not os.path.exists(cf): return [f"{name}: {x}" for x in P + ["CALLS.csv is missing"]]
    rows = list(csv.DictReader(open(cf, encoding="utf-8"))); head = list(rows[0]) if rows else open(cf, encoding="utf-8").readline().strip().split(",")
    miss = [c for c in CALL_COLS if c not in head]
    if miss: return [f"{name}: {x}" for x in P + ["CALLS.csv lacks columns: " + ", ".join(miss)]]
    done = [r for r in rows if r["complete"] == "True"]; keys = {r["request_key"] for r in rows}; okkeys = [r["request_key"] for r in done]
    if len(keys) != m["calls"]: P.append(f"calls = {m['calls']} but CALLS.csv holds {len(keys)} logical requests")
    if len(set(okkeys)) != m["complete"]: P.append(f"complete = {m['complete']} but CALLS.csv holds {len(set(okkeys))} completed requests")
    if len(okkeys) != len(set(okkeys)): P.append("a request has two completed attempts; the final response is not unique")
    if len(keys) - len(set(okkeys)) != m["failed"]: P.append(f"failed = {m['failed']} does not match CALLS.csv")
    for r in rows:
        if not (HEX.match(r["system_sha256"]) and HEX.match(r["user_sha256"])): P.append(f"{r['request_key']}: request hashes missing"); break
        if r["system_sha256"] != m["system_sha256"]: P.append(f"{r['request_key']}: another system prompt than the run's"); break
    for r in done:
        if not HEX.match(r["response_sha256"]) or not r["model_returned"] or not r["response_id"]: P.append(f"{r['request_key']}: completed call without response hash, response id or returned model"); break
    mr = set(m["model_returned"] if isinstance(m["model_returned"], list) else [m["model_returned"]])
    if {r["model_returned"] for r in done} - mr: P.append("CALLS.csv holds a returned model identifier that RUN_META does not list")
    u = m["usage"] if isinstance(m["usage"], dict) else {}
    for k in ("input_tokens", "output_tokens"):
        if u.get(k) != sum(int(r[k] or 0) for r in rows): P.append(f"usage.{k} is not the sum of CALLS.csv")
    if m["stage"].startswith("talk_"):
        rf = os.path.join(folder, "RESPONSES.jsonl")
        if not os.path.exists(rf): P.append("RESPONSES.jsonl is missing (classification responses are committed in full)")
        else:
            R = {}
            for l in open(rf, encoding="utf-8"):
                o = json.loads(l); R[(o["request_key"], str(o["attempt"]))] = hashlib.sha256(o["text"].encode("utf-8")).hexdigest()
            for r in done:
                if R.get((r["request_key"], r["attempt"])) != r["response_sha256"]: P.append(f"{r['request_key']}: response text missing from RESPONSES.jsonl or different from its recorded hash"); break
    return [f"{name}: {x}" for x in P]


def records():
    rows, problems = [], []
    for f in sorted(glob.glob(os.path.join(ROOT, "data", "**", "RUN_META.json"), recursive=True)):
        m = json.load(open(f)); new = m.get("spec") == "run-record v1"
        if new: problems += validate_run(os.path.dirname(f))
        elif rel(os.path.dirname(f)) not in LEGACY: problems.append(f"{rel(f)}: no 'spec: run-record v1' and not on the list of runs made before the specification")
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
