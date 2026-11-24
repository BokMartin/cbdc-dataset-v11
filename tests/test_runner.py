"""The runner with fake provider clients, no network and no cost: truncated output, refusal, timeout, unparsable output, exhausted
credit (sync and batch), the cost cap, resume without sending a paid request twice, and a valid run record at the end."""
import contextlib, hashlib, json, os, sys, types
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts", "pipeline"))
import runner  # noqa: E402

H = lambda t: hashlib.sha256(t.encode("utf-8")).hexdigest()
SYSTEM = "SYSTEM PROMPT\n"


def job(tmp, keys):
    d = os.path.join(str(tmp), "job"); os.makedirs(d)
    open(os.path.join(d, "SYSTEM_PROMPT.md"), "w").write(SYSTEM)
    with open(os.path.join(d, "REQUESTS.jsonl"), "w") as fh:
        for k in keys:
            u = f"UNIT {k}\n»text {k}«\n\nCODE\n{k}\n"; fh.write(json.dumps({"request_key": k, "unit_ids": [k], "user": u, "user_sha256": H(u)}) + "\n")
    json.dump({"stage": "talk_L1", "system_prompt_file": "pipeline/prompts/talk_L1_relevance.system.md", "system_prompt_version": "test", "user_message_format": "test",
               "packing": "one unit per request", "inputs": [{"file": "units/x.csv", "sha256": "a" * 64, "rows": 1, "in_repository": False}], "request_keys": keys},
              open(os.path.join(d, "JOB_META.json"), "w"))
    return d


def key_of(user): return user.split("\n")[0].split()[1]


class Err(Exception):
    def __init__(self, msg, status): super().__init__(msg); self.status_code = status


def answer(k, mode):
    """(text, stop_reason) for a behaviour."""
    return {"ok": (f"{k}\tR\nEND", "end_turn"), "trunc": (f"{k}\t", "max_tokens"), "refuse": ("", "refusal"), "garbage": ("I think it is relevant.", "end_turn")}[mode]


class FakeAnthropic:
    """messages.stream / messages.batches with the shapes runner.py reads."""
    def __init__(self, plan, end_after=0):
        self.plan, self.sent, self.end_after, self.batches = plan, [], end_after, {}
        fake = self
        class Batches:
            def create(self, requests):
                r = fake.plan.get("_submit")
                if r: raise r
                bid = f"msgbatch_{len(fake.batches)}"; fake.batches[bid] = {"reqs": requests, "polls": 0}; fake.sent += [key_of(x["params"]["messages"][0]["content"]) for x in requests]
                return types.SimpleNamespace(id=bid)
            def retrieve(self, bid):
                b = fake.batches[bid]; b["polls"] += 1
                return types.SimpleNamespace(processing_status="ended" if b["polls"] > fake.end_after else "in_progress")
            def results(self, bid):
                for x in fake.batches[bid]["reqs"]:
                    k = key_of(x["params"]["messages"][0]["content"]); mode = fake.mode(k)
                    if mode == "credit": yield {"custom_id": x["custom_id"], "result": {"type": "errored", "error": {"type": "error", "error": {"type": "billing_error", "message": "credit"}}}}
                    elif mode == "expired": yield {"custom_id": x["custom_id"], "result": {"type": "expired"}}
                    else: yield {"custom_id": x["custom_id"], "result": {"type": "succeeded", "message": fake.msg(k, mode)}}
        class Messages:
            batches = Batches()
            @contextlib.contextmanager
            def stream(self, **p):
                k = key_of(p["messages"][0]["content"]); fake.sent.append(k); mode = fake.mode(k)
                if mode == "timeout": raise Err("timed out", 408)
                if mode == "credit": raise Err("Your credit balance is too low to access the Anthropic API.", 400)
                yield types.SimpleNamespace(get_final_message=lambda: fake.msg(k, mode))
        self.messages = Messages()

    def mode(self, k):
        m = self.plan.get(k, "ok")
        if isinstance(m, list): m = m.pop(0) if len(m) > 1 else m[0]
        return m

    def msg(self, k, mode):
        t, s = answer(k, mode)
        return {"id": "msg_" + k, "model": "claude-opus-5-5", "stop_reason": s, "content": [{"type": "text", "text": t}],
                "usage": {"input_tokens": 50, "cache_read_input_tokens": 900, "cache_creation_input_tokens": 0, "output_tokens": 8}}


class FakeDeepSeek:
    def __init__(self, credit_after=None):
        self.sent, self.credit_after = [], credit_after; fake = self
        class Completions:
            def create(self, **p):
                k = key_of(p["messages"][1]["content"])
                if fake.credit_after is not None and len(fake.sent) >= fake.credit_after: raise Err('{"error":{"message":"Insufficient Balance"}}', 402)
                fake.sent.append(k)
                d = {"id": "ds_" + k, "model": "deepseek-v4-pro", "choices": [{"finish_reason": "stop", "message": {"content": f"{k}\tN\nEND"}}],
                     "usage": {"prompt_tokens": 1000, "prompt_cache_hit_tokens": 900, "completion_tokens": 20, "completion_tokens_details": {"reasoning_tokens": 12}}}
                return types.SimpleNamespace(model_dump=lambda: d)
        self.chat = types.SimpleNamespace(completions=Completions())


class FakeOpenAI:
    def __init__(self, quota_keys=()):
        self.files_store, self.batches_store, self.quota_keys = {}, {}, set(quota_keys); fake = self
        class Files:
            def create(self, file, purpose):
                fid = f"file_{len(fake.files_store)}"; fake.files_store[fid] = file[1].decode(); return types.SimpleNamespace(id=fid)
            def content(self, fid): return types.SimpleNamespace(text=fake.files_store[fid])
        class Batches:
            def create(self, input_file_id, endpoint, completion_window):
                out, err = [], []
                for line in fake.files_store[input_file_id].splitlines():
                    o = json.loads(line); k = key_of(o["body"]["input"][-1]["content"]); assert o["body"]["input"][0]["role"] == "developer" and "instructions" not in o["body"]
                    if k in fake.quota_keys: err.append(json.dumps({"custom_id": o["custom_id"], "response": {"status_code": 429, "body": {"error": {"code": "insufficient_quota", "message": "quota"}}}}))
                    else:
                        body = {"id": "resp_" + k, "model": "gpt-6-astra-2026", "status": "completed", "output": [{"type": "message", "content": [{"type": "output_text", "text": f"{k}\tU\nEND"}]}],
                                "usage": {"input_tokens": 1000, "input_tokens_details": {"cached_tokens": 800}, "output_tokens": 30, "output_tokens_details": {"reasoning_tokens": 20}}}
                        out.append(json.dumps({"custom_id": o["custom_id"], "response": {"status_code": 200, "body": body}}))
                bid = f"batch_{len(fake.batches_store)}"; fake.files_store[bid + "_out"] = "\n".join(out); fake.files_store[bid + "_err"] = "\n".join(err)
                fake.batches_store[bid] = types.SimpleNamespace(status="completed", output_file_id=bid + "_out", error_file_id=bid + "_err" if err else None, errors=None)
                return types.SimpleNamespace(id=bid)
            def retrieve(self, bid): return fake.batches_store[bid]
        self.files, self.batches = Files(), Batches()


def run(d, tmp, client, provider="anthropic", model="claude-opus-5-5", extra=()):
    return runner.main(["run", "--job", d, "--work", os.path.join(str(tmp), "work"), "--run", "r1", "--provider", provider, "--model", model,
                        "--purpose", "development", "--max-usd", "5", "--max-attempts", "2"] + list(extra), client=client)


def record(tmp):
    out = os.path.join(str(tmp), "data", "talk", "runs", "r1")
    return runner.main(["record", "--work", os.path.join(str(tmp), "work"), "--run", "r1", "--out", out, "--root", str(tmp)]), out


def rows(tmp): return [json.loads(l) for l in open(os.path.join(str(tmp), "work", "r1", "ATTEMPTS.jsonl"))]


def test_sync_failures_are_recorded_and_only_transient_ones_retried(tmp_path):
    d = job(tmp_path, ["u1", "u2", "u3", "u4", "u5"])
    fake = FakeAnthropic({"u2": "trunc", "u3": "refuse", "u4": ["timeout", "ok"], "u5": "garbage"})
    assert run(d, tmp_path, fake) == 0
    R = rows(tmp_path); by = {}
    for r in R: by.setdefault(r["request_key"], []).append(r)
    assert by["u1"][0]["complete"] and len(by["u1"]) == 1
    assert by["u2"][0]["error_kind"] == "unparsed" and len(by["u2"]) == 1          # cut off: no END line, never a label, not resent
    assert by["u3"][0]["error_kind"] == "unparsed" and not by["u3"][0]["complete"]   # refusal: empty text
    assert [r["error_kind"] for r in by["u4"]] == ["transient", ""] and by["u4"][1]["complete"]
    assert by["u5"][0]["parse_error"].startswith("no END line")
    assert by["u1"][0]["cached_input_tokens"] == 900 and by["u1"][0]["input_tokens"] == 950
    P, out = record(tmp_path); assert P == []
    meta = json.load(open(os.path.join(out, "RUN_META.json")))
    assert meta["calls"] == 5 and meta["complete"] == 2 and meta["failed"] == 3 and meta["retried"] == 1 and meta["interface"] == "anthropic.messages"


def test_credit_exhaustion_stops_and_resume_sends_only_what_is_missing(tmp_path):
    d = job(tmp_path, [f"u{i}" for i in range(10)])
    fake = FakeDeepSeek(credit_after=4)
    assert run(d, tmp_path, fake, "deepseek", "deepseek-v4-pro", ["--concurrency", "1"]) == runner.EXIT_CREDIT
    first = list(fake.sent); assert len(first) == 4
    fake.credit_after = None
    assert run(d, tmp_path, fake, "deepseek", "deepseek-v4-pro", ["--concurrency", "1"]) == 0
    assert sorted(fake.sent) == sorted(f"u{i}" for i in range(10))            # every request served exactly once
    done = [r["request_key"] for r in rows(tmp_path) if r["complete"]]; assert sorted(done) == sorted(set(done)) and len(done) == 10
    P, out = record(tmp_path); assert P == []
    assert "credit exhausted" in json.load(open(os.path.join(out, "RUN_META.json")))["deviations"]


def test_batch_in_flight_is_collected_not_resubmitted(tmp_path):
    d = job(tmp_path, ["u1", "u2", "u3"])
    fake = FakeAnthropic({"u3": ["expired", "ok"]}, end_after=1)
    assert run(d, tmp_path, fake, extra=["--batch"]) == 0                       # submitted, still processing, no --wait
    assert fake.sent == ["u1", "u2", "u3"]
    assert run(d, tmp_path, fake, extra=["--batch", "--wait", "--poll", "0"]) == 0
    assert fake.sent.count("u1") == 1 and fake.sent.count("u3") == 2           # only the expired item went out again
    P, out = record(tmp_path); assert P == []
    m = json.load(open(os.path.join(out, "RUN_META.json"))); assert m["interface"] == "anthropic.message_batches" and m["complete"] == 3 and len(m["batches"]) == 2


def test_batch_credit_errors_stop_the_run(tmp_path):
    d = job(tmp_path, ["u1", "u2"])
    fake = FakeAnthropic({"u2": "credit"})
    assert run(d, tmp_path, fake, extra=["--batch", "--wait", "--poll", "0"]) == runner.EXIT_CREDIT
    fake.plan["u2"] = "ok"; fake.plan["_submit"] = Err("Your credit balance is too low", 400)
    assert run(d, tmp_path, fake, extra=["--batch", "--wait", "--poll", "0"]) == runner.EXIT_CREDIT   # still no credit: nothing sent
    del fake.plan["_submit"]
    assert run(d, tmp_path, fake, extra=["--batch", "--wait", "--poll", "0"]) == 0
    assert fake.sent.count("u1") == 1 and fake.sent.count("u2") == 2


def test_openai_batch_results_and_quota_errors(tmp_path):
    d = job(tmp_path, ["u1", "u2"])
    fake = FakeOpenAI(quota_keys={"u2"})
    assert run(d, tmp_path, fake, "openai", "gpt-6-astra", ["--batch", "--wait", "--poll", "0"]) == runner.EXIT_CREDIT
    R = {r["request_key"]: r for r in rows(tmp_path)}
    assert R["u1"]["complete"] and R["u1"]["reasoning_tokens"] == 20 and R["u2"]["error_kind"] == "credit"
    fake.quota_keys = set()
    assert run(d, tmp_path, fake, "openai", "gpt-6-astra", ["--batch", "--wait", "--poll", "0"]) == 0
    P, out = record(tmp_path); assert P == []


def test_cost_cap_stops_before_any_call_and_cap_is_required(tmp_path):
    d = job(tmp_path, ["u1", "u2"])
    fake = FakeAnthropic({})
    code = runner.main(["run", "--job", d, "--work", os.path.join(str(tmp_path), "work"), "--run", "r1", "--provider", "anthropic", "--model", "claude-opus-5-5",
                        "--purpose", "development", "--max-usd", "0.00001"], client=fake)
    assert code == runner.EXIT_CAP and fake.sent == []
    with pytest.raises(SystemExit):
        runner.main(["run", "--job", d, "--work", os.path.join(str(tmp_path), "w2"), "--provider", "anthropic", "--model", "claude-opus-5-5", "--purpose", "development"], client=fake)


def test_credit_is_told_apart_from_rate_and_server_errors():
    assert runner.classify(Err("billing_error", 402)) == "credit"
    assert runner.classify(Err('{"code": "insufficient_quota"}', 429)) == "credit"
    assert runner.classify(Err("rate limited", 429)) == "rate"
    assert runner.classify(Err("overloaded", 529)) == "transient"
    assert runner.classify(Err("invalid model", 404)) == "fatal"


def test_changed_job_or_prompt_cannot_continue_an_old_run(tmp_path):
    d = job(tmp_path, ["u1"]); assert run(d, tmp_path, FakeAnthropic({})) == 0
    open(os.path.join(d, "SYSTEM_PROMPT.md"), "a").write("changed")
    with pytest.raises(SystemExit): run(d, tmp_path, FakeAnthropic({}))
