"""The run-record check must verify artifacts: a fictitious run fails, a consistent miniature run passes (audit A4 of 17 Nov 2026, F05)."""
import csv, hashlib, json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts", "pipeline"))
import run_statement as rs

H = lambda t: hashlib.sha256(t.encode("utf-8")).hexdigest()


def make(tmp, **over):
    root = str(tmp); folder = os.path.join(root, "data", "talk", "runs", "x_20261201"); os.makedirs(folder)
    system = "SYSTEM PROMPT TEXT"; open(os.path.join(folder, "SYSTEM_PROMPT.md"), "w").write(system)
    os.makedirs(os.path.join(root, "data", "units")); inp = os.path.join(root, "data", "units", "IN.csv"); open(inp, "w").write("unit_id\nu1\nu2\n")
    resp = {"u1": "u1\tR\nEND", "u2": "u2\tN\nEND"}
    rows = [{"request_key": k, "attempt": "1", "unit_ids": k, "response_id": "resp_" + k, "model_returned": "model-x-1", "stop_reason": "end", "started_utc": "2026-12-01T10:00:00Z",
             "input_tokens": "10", "cached_input_tokens": "0", "output_tokens": "5", "reasoning_tokens": "0", "system_sha256": H(system), "user_sha256": H("user " + k),
             "response_sha256": H(t), "complete": "True", "parsed_ok": "True", "parse_error": ""} for k, t in resp.items()]
    with open(os.path.join(folder, "CALLS.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=rs.CALL_COLS); w.writeheader(); w.writerows(rows)
    with open(os.path.join(folder, "RESPONSES.jsonl"), "w") as fh:
        for k, t in resp.items(): fh.write(json.dumps({"request_key": k, "attempt": 1, "text": t}) + "\n")
    meta = {"spec": "run-record v1", "stage": "talk_L1", "purpose": "development", "provider": "x", "interface": "openai.responses", "model_requested": "model-x",
            "model_returned": ["model-x-1"], "parameters": {"max_output_tokens": 100, "reasoning": "provider default (not sent)"}, "system_prompt_file": "pipeline/prompts/talk_L1_relevance.system.md",
            "system_prompt_version": "v0.2", "system_sha256": H(system), "user_message_format": "scripts/units/build_requests.py single()", "packing": "one unit per request",
            "inputs": [{"file": "data/units/IN.csv", "sha256": rs.sha_file(inp), "rows": 2}], "git_commit": "a" * 40, "started_utc": "2026-12-01T10:00:00Z", "finished_utc": "2026-12-01T10:01:00Z",
            "calls": 2, "complete": 2, "failed": 0, "usage": {"input_tokens": 20, "output_tokens": 10}, "sdk": "x 1.0", "python": "3.12", "operator": "test", "deviations": "none"}
    meta.update(over); json.dump(meta, open(os.path.join(folder, "RUN_META.json"), "w")); return folder, root


def test_consistent_run_passes(tmp_path):
    folder, root = make(tmp_path); assert rs.validate_run(folder, root) == []


def test_fictitious_run_fails(tmp_path):
    folder, root = make(tmp_path, calls=999, complete=999)
    assert any("999" in p for p in rs.validate_run(folder, root))


def test_header_only_calls_and_no_responses_fail(tmp_path):
    folder, root = make(tmp_path)
    open(os.path.join(folder, "CALLS.csv"), "w").write(",".join(rs.CALL_COLS) + "\n"); os.remove(os.path.join(folder, "RESPONSES.jsonl"))
    P = rs.validate_run(folder, root); assert any("logical requests" in p for p in P) and any("RESPONSES.jsonl" in p for p in P)


def test_changed_prompt_input_or_response_fails(tmp_path):
    folder, root = make(tmp_path); open(os.path.join(folder, "SYSTEM_PROMPT.md"), "a").write(" changed")
    assert any("SYSTEM_PROMPT.md" in p for p in rs.validate_run(folder, root))
    folder, root = make(tmp_path / "b"); open(os.path.join(root, "data", "units", "IN.csv"), "a").write("u3\n")
    assert any("differs from the recorded SHA-256" in p for p in rs.validate_run(folder, root))
    folder, root = make(tmp_path / "c"); open(os.path.join(folder, "RESPONSES.jsonl"), "w").write(json.dumps({"request_key": "u1", "attempt": 1, "text": "u1\tN\nEND"}) + "\n")
    assert any("RESPONSES.jsonl" in p for p in rs.validate_run(folder, root))


def test_chat_products_and_unknown_interfaces_are_rejected(tmp_path):
    folder, root = make(tmp_path, interface="API"); assert any("interface" in p for p in rs.validate_run(folder, root))
    folder, root = make(tmp_path / "b", interface="openai.chat_completions"); assert rs.validate_run(folder, root) == []


def test_run_without_spec_is_not_silently_legacy():
    assert "data/translation/runs/openai_gpt-6-astra_api_20261110" in rs.LEGACY and len(rs.LEGACY) == 3
