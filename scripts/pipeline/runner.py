#!/usr/bin/env python3
"""Run a job of model requests on one provider and leave a run record v1 behind (docs/RUN_RECORD_SPEC.md).

Three providers, one prompt, identical user messages (calibration protocol, models of MB of 17 Nov 2026):
  anthropic  claude-opus-5-5   Message Batches (50 % off) or Messages; the system prompt is a cached block
  openai     gpt-6-astra       Batch API on /v1/responses (50 % off) or Responses; prompt_cache_key per run
  deepseek   deepseek-v4-pro   Chat Completions, parallel calls; the provider caches repeated prefixes on its own (no batch API)

Money (MB, 23 Nov 2026: "optimalizuj performance a dollar cost ... není zaplý autoreload"):
  - `plan` estimates tokens and cost from the job and pipeline/PRICES.json, and makes no call.
  - `run` refuses to start without --max-usd. Before each submission it adds the cost already measured, the estimate of the
    batches still in flight and the estimate of the next chunk; a chunk that would pass the cap is cut, and when nothing fits
    the run stops (exit 4). Estimates are conservative (3 characters per token, no cache discount, measured output x 1.25).
  - Exhausted credit (HTTP 402, billing_error, insufficient_quota, "credit balance is too low", "Insufficient Balance") stops
    the run cleanly (exit 3): every response already paid for is on disk, batches in flight stay recorded, and running the
    same command again after a top-up collects them and sends only what has no completed attempt. Nothing paid is sent twice.

Records: every attempt is appended to <work>/<run>/ATTEMPTS.jsonl as soon as it is known (with the response text, which may hold
source text: the work folder lives outside the repository). `record` writes the run folder data/<stage>/runs/<run>/ with
RUN_META.json, SYSTEM_PROMPT.md, CALLS.csv and, for talk stages, RESPONSES.jsonl, and runs the validator of run_statement.py.
A response that does not pass the strict parser is a failed attempt, never a label. Failed attempts stay in the record; a retry
is a new attempt row. Keys come from the environment only (ANTHROPIC_API_KEY, OPENAI_API_KEY, DEEPSEEK_API_KEY); none is written.

usage:
  runner.py plan   --job <job dir> --provider anthropic --model claude-opus-5-5 [--batch] [--expect-output 400]
  runner.py run    --job <job dir> --work <dir> --provider ... --model ... --purpose development --max-usd 20
                   [--batch] [--wait] [--chunk 2000] [--concurrency 8] [--max-tokens 8000] [--effort low] [--max-attempts 2]
                   [--retry-unparsed] [--operator MB]
  runner.py record --work <dir> --run <run name> [--out data/<stage>/runs/<run>]
A job dir holds REQUESTS.jsonl ({request_key, unit_ids, user, user_sha256} per line), JOB_META.json and SYSTEM_PROMPT.md, written
by scripts/pipeline/build_jobs.py.
"""
import argparse, csv, datetime as dt, hashlib, json, os, platform, subprocess, sys, threading, time
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(ROOT, "scripts", "talk"))
import run_statement as rs  # noqa: E402

EXIT_CREDIT, EXIT_CAP, EXIT_FATAL = 3, 4, 5
CHARS_PER_TOKEN = 3.0          # conservative: more tokens than the o200k or Claude tokenizer give on English prose
PRICES = json.load(open(os.path.join(ROOT, "pipeline", "PRICES.json"), encoding="utf-8"))
ATTEMPT_COLS = rs.CALL_COLS + ["cache_write_tokens", "error_kind", "cost_usd"]


def sha(s): return hashlib.sha256(s.encode("utf-8")).hexdigest()
def now(): return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
def cid(key): return "k" + sha(key)[:40]     # custom ids: Anthropic allows [A-Za-z0-9_-]{1,64}


class CreditExhausted(Exception):
    pass


def classify(exc):
    """'credit' | 'rate' | 'transient' | 'fatal' for an exception or an error object of a provider."""
    status = getattr(exc, "status_code", None) or getattr(exc, "status", None)
    text = (str(getattr(exc, "body", "") or "") + " " + str(getattr(exc, "code", "") or "") + " " + str(getattr(exc, "type", "") or "") + " " + str(exc)).lower()
    if status == 402 or any(s in text for s in ("billing_error", "insufficient_quota", "credit balance is too low", "insufficient balance", "billing_hard_limit")):
        return "credit"
    if status == 429 or "rate_limit" in text: return "rate"
    name = type(exc).__name__
    if status in (408, 409, 500, 502, 503, 504, 529) or name in ("APITimeoutError", "APIConnectionError", "TimeoutError", "ConnectionError") \
            or any(s in text for s in ("overloaded", "api_error", "server_error", "timeout", "expired", "canceled", "cancelled")):
        return "transient"
    return "fatal"


# ---------------------------------------------------------------------------------------------------------------- parsers
def parser_for(stage):
    """parse(text, req) -> note ('' or a remark kept in parse_error) or raises ParseError. req is the job request."""
    import parse_output as po
    if stage == "talk_L1": return lambda text, req: (po.parse_l1(text, req["unit_ids"]), "")[1]
    if stage == "talk_L2": return lambda text, req: (po.parse_l2(text, req["unit_ids"]), "")[1]
    sys.path.insert(0, os.path.join(ROOT, "scripts", "extraction")); import v122
    def extraction(text, req):   # prompt v12.2 (ADR-013): envelope and coverage checked against the request that was sent
        r = v122.check(text, req["user"])
        if r["state"] == "failed": raise po.ParseError("; ".join(r["problems"])[:300])
        return f"{len(r['rejected'])} observations rejected by field or quote checks" if r["rejected"] else ""
    return extraction


# ---------------------------------------------------------------------------------------------------------------- backends
def _usage_openai_dict(u):
    u = u or {}
    return {"input_tokens": u.get("input_tokens", u.get("prompt_tokens", 0)) or 0,
            "cached_input_tokens": (u.get("input_tokens_details") or {}).get("cached_tokens", u.get("prompt_cache_hit_tokens", 0)) or 0,
            "cache_write_tokens": 0,
            "output_tokens": u.get("output_tokens", u.get("completion_tokens", 0)) or 0,
            "reasoning_tokens": ((u.get("output_tokens_details") or u.get("completion_tokens_details") or {}).get("reasoning_tokens")) or 0}


def result_from_responses_body(b):
    """OpenAI Responses object (dict) -> result."""
    text = "".join(c.get("text", "") for it in b.get("output", []) if it.get("type") == "message" for c in it.get("content", []) if c.get("type") == "output_text")
    inc = (b.get("incomplete_details") or {}).get("reason")
    return dict(response_id=b.get("id", ""), model_returned=b.get("model", ""), stop_reason=b.get("status", "") + ("/" + inc if inc else ""),
                text=text, ok_stop=b.get("status") == "completed", **_usage_openai_dict(b.get("usage")))


class AnthropicBackend:
    provider = "anthropic"

    def __init__(self, model, max_tokens, effort=None, batch=False, client=None):
        self.model, self.max_tokens, self.effort, self.batch = model, max_tokens, effort, batch
        self.interface = "anthropic.message_batches" if batch else "anthropic.messages"
        self.ttl = "1h" if batch else None   # batch items run spread over up to an hour: the longer cache lifetime pays off
        if client is None:
            import anthropic; client = anthropic.Anthropic(); self.sdk = f"anthropic {anthropic.__version__}"
        else: self.sdk = "fake"
        self.c = client

    def params(self, system, user):
        cc = {"type": "ephemeral", **({"ttl": self.ttl} if self.ttl else {})}
        p = {"model": self.model, "max_tokens": self.max_tokens, "system": [{"type": "text", "text": system, "cache_control": cc}],
             "messages": [{"role": "user", "content": user}]}
        if self.effort: p["output_config"] = {"effort": self.effort}
        return p

    def sent_parameters(self):
        return {"max_tokens": self.max_tokens, "output_config.effort": self.effort or "provider default (not sent)",
                "thinking": "provider default (not sent; adaptive on this model)", "system": "one text block with cache_control " + (self.ttl or "5m"),
                "temperature": "provider default (not sent; not settable on this model)", "tools": "none", "stream": "true" if not self.batch else "not applicable (batch)"}

    def _result(self, m):
        m = m if isinstance(m, dict) else m.model_dump()
        u = m.get("usage") or {}; read = u.get("cache_read_input_tokens") or 0; write = u.get("cache_creation_input_tokens") or 0
        text = "".join(b.get("text", "") for b in m.get("content", []) if b.get("type") == "text")
        return dict(response_id=m.get("id", ""), model_returned=m.get("model", ""), stop_reason=m.get("stop_reason") or "", text=text,
                    ok_stop=m.get("stop_reason") == "end_turn", input_tokens=(u.get("input_tokens") or 0) + read + write, cached_input_tokens=read,
                    cache_write_tokens=write, output_tokens=u.get("output_tokens") or 0, reasoning_tokens="")

    def call(self, system, user):
        with self.c.messages.stream(**self.params(system, user)) as st: return self._result(st.get_final_message())

    def submit(self, system, reqs):
        return self.c.messages.batches.create(requests=[{"custom_id": cid(r["request_key"]), "params": self.params(system, r["user"])} for r in reqs]).id

    def ended(self, bid): return self.c.messages.batches.retrieve(bid).processing_status == "ended"

    def results(self, bid):
        for r in self.c.messages.batches.results(bid):
            r = r if isinstance(r, dict) else r.model_dump()
            res = r["result"]; t = res["type"]
            if t == "succeeded": yield r["custom_id"], self._result(res["message"]), None
            elif t == "errored":
                e = (res.get("error") or {}).get("error") or res.get("error") or {}
                yield r["custom_id"], None, (classify(type("E", (Exception,), {})(json.dumps(e))), json.dumps(e)[:300])
            else: yield r["custom_id"], None, ("transient", t)


class OpenAIBackend:
    provider = "openai"

    def __init__(self, model, max_tokens, effort=None, batch=False, cache_key="", client=None):
        self.model, self.max_tokens, self.effort, self.batch, self.cache_key = model, max_tokens, effort, batch, cache_key
        self.interface = "openai.batch" if batch else "openai.responses"
        if client is None:
            import openai; client = openai.OpenAI(); self.sdk = f"openai {openai.__version__}"
        else: self.sdk = "fake"
        self.c = client

    def params(self, system, user):
        # the system prompt goes as a developer message, not as `instructions`: gpt-6.2 models do not cache `instructions`
        # (measured 23 Nov 2026: 0 cached tokens with `instructions`, 1,144 of 1,379 with a developer message; gpt-6-astra caches both)
        p = {"model": self.model, "input": [{"role": "developer", "content": system}, {"role": "user", "content": user}],
             "max_output_tokens": self.max_tokens, "store": False}
        if self.cache_key: p["prompt_cache_key"] = self.cache_key
        if self.effort: p["reasoning"] = {"effort": self.effort}
        return p

    def sent_parameters(self):
        return {"max_output_tokens": self.max_tokens, "reasoning.effort": self.effort or "provider default (not sent)", "store": False,
                "prompt_cache_key": self.cache_key or "not sent", "temperature": "provider default (not sent)", "tools": "none",
                "system_prompt": "developer message (input[0])", "endpoint": "/v1/responses" + (" through /v1/batches, completion_window 24h" if self.batch else "")}

    def call(self, system, user):
        return result_from_responses_body(self.c.responses.create(**self.params(system, user)).model_dump())

    def submit(self, system, reqs):
        lines = "".join(json.dumps({"custom_id": cid(r["request_key"]), "method": "POST", "url": "/v1/responses", "body": self.params(system, r["user"])}) + "\n" for r in reqs)
        f = self.c.files.create(file=("requests.jsonl", lines.encode("utf-8")), purpose="batch")
        return self.c.batches.create(input_file_id=f.id, endpoint="/v1/responses", completion_window="24h").id

    def ended(self, bid):
        b = self.c.batches.retrieve(bid)
        if b.status == "failed":
            errs = " ".join(str(getattr(e, "code", "")) + " " + str(getattr(e, "message", "")) for e in (getattr(getattr(b, "errors", None), "data", None) or []))
            if classify(Exception(errs)) == "credit": raise CreditExhausted(f"batch {bid} failed: {errs[:200]}")
        return b.status in ("completed", "failed", "expired", "cancelled")

    def results(self, bid):
        b = self.c.batches.retrieve(bid)
        for fid in (b.output_file_id, b.error_file_id):
            if not fid: continue
            for line in self.c.files.content(fid).text.splitlines():
                if not line.strip(): continue
                o = json.loads(line); resp = o.get("response") or {}
                if resp.get("status_code") == 200: yield o["custom_id"], result_from_responses_body(resp["body"]), None
                else:
                    e = (resp.get("body") or {}).get("error") or o.get("error") or {}
                    err = type("E", (Exception,), {})(json.dumps(e)); err.status_code = resp.get("status_code")
                    yield o["custom_id"], None, (classify(err), json.dumps(e)[:300])


class DeepSeekBackend:
    provider, interface, batch = "deepseek", "deepseek.chat_completions", False

    def __init__(self, model, max_tokens, effort=None, thinking=None, client=None):
        self.model, self.max_tokens, self.effort, self.thinking = model, max_tokens, effort, thinking
        if client is None:
            import openai; client = openai.OpenAI(api_key=os.environ["DEEPSEEK_API_KEY"], base_url="https://api.deepseek.com"); self.sdk = f"openai {openai.__version__}"
        else: self.sdk = "fake"
        self.c = client

    def params(self, system, user):
        p = {"model": self.model, "max_tokens": self.max_tokens, "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}]}
        if self.effort: p["reasoning_effort"] = self.effort
        if self.thinking: p["extra_body"] = {"thinking": {"type": self.thinking}}
        return p

    def sent_parameters(self):
        return {"max_tokens": self.max_tokens, "reasoning_effort": self.effort or "provider default (not sent)", "thinking": self.thinking or "provider default (not sent)",
                "temperature": "provider default (not sent)", "tools": "none", "stream": False, "base_url": "https://api.deepseek.com"}

    def call(self, system, user):
        d = self.c.chat.completions.create(**self.params(system, user)).model_dump(); ch = d["choices"][0]
        return dict(response_id=d.get("id", ""), model_returned=d.get("model", ""), stop_reason=ch.get("finish_reason") or "", text=(ch.get("message") or {}).get("content") or "",
                    ok_stop=ch.get("finish_reason") == "stop", **_usage_openai_dict(d.get("usage")))


def make_backend(a, client=None):
    if a.provider == "anthropic": return AnthropicBackend(a.model, a.max_tokens, a.effort, a.batch, client=client)
    if a.provider == "openai": return OpenAIBackend(a.model, a.max_tokens, a.effort, a.batch, cache_key=getattr(a, "cache_key", ""), client=client)
    if a.batch: raise SystemExit("deepseek has no batch interface; run without --batch")
    return DeepSeekBackend(a.model, a.max_tokens, a.effort, getattr(a, "thinking", None), client=client)


# ---------------------------------------------------------------------------------------------------------------- money
def price(model):
    if model not in PRICES: raise SystemExit(f"no price for {model} in pipeline/PRICES.json: the cost cap cannot work without one")
    return PRICES[model]


def cost(model, batch, input_tokens, cached, write, output, ttl=None):
    p = price(model); f = p["batch_discount"] if batch else 1.0
    wprice = p.get("cache_write_1h" if ttl == "1h" else "cache_write_5m", p["input"])
    fresh = max(0, input_tokens - cached - write)
    return f * (fresh * p["input"] + cached * p["cached_input"] + write * wprice + output * p["output"]) / 1e6


def estimate(model, batch, system, reqs, out_per_request):
    tin = sum((len(system) + len(r["user"])) / CHARS_PER_TOKEN for r in reqs); tout = out_per_request * len(reqs)
    return tin, tout, cost(model, batch, int(tin), 0, 0, int(tout))


# ---------------------------------------------------------------------------------------------------------------- job and state
def load_job(job):
    reqs = [json.loads(l) for l in open(os.path.join(job, "REQUESTS.jsonl"), encoding="utf-8") if l.strip()]
    for r in reqs:
        if sha(r["user"]) != r["user_sha256"]: raise SystemExit(f"request {r['request_key']} differs from its recorded hash")
    if len({r["request_key"] for r in reqs}) != len(reqs): raise SystemExit("a request key appears twice in the job")
    meta = json.load(open(os.path.join(job, "JOB_META.json"), encoding="utf-8"))
    system = open(os.path.join(job, "SYSTEM_PROMPT.md"), "rb").read().decode("utf-8")
    return reqs, meta, system


class Run:
    def __init__(self, work, name):
        self.dir = os.path.join(work, name); os.makedirs(self.dir, exist_ok=True)
        self.sf, self.af = os.path.join(self.dir, "STATE.json"), os.path.join(self.dir, "ATTEMPTS.jsonl")
        self.state = json.load(open(self.sf, encoding="utf-8")) if os.path.exists(self.sf) else {"batches": {}, "events": []}
        self.attempts = [json.loads(l) for l in open(self.af, encoding="utf-8")] if os.path.exists(self.af) else []
        self.lock = threading.Lock()

    def save(self):
        tmp = self.sf + ".tmp"; json.dump(self.state, open(tmp, "w", encoding="utf-8"), indent=1); os.replace(tmp, self.sf)

    def event(self, text):
        self.state["events"].append(f"{now()} {text}"); self.save(); print(text, flush=True)

    def add(self, row):
        with self.lock:
            row["attempt"] = 1 + sum(1 for a in self.attempts if a["request_key"] == row["request_key"])
            self.attempts.append(row)
            with open(self.af, "a", encoding="utf-8") as fh: fh.write(json.dumps(row, ensure_ascii=False) + "\n"); fh.flush(); os.fsync(fh.fileno())

    def by_key(self):
        d = {}
        for a in self.attempts: d.setdefault(a["request_key"], []).append(a)
        return d

    def inflight(self):
        return {k for b in self.state["batches"].values() if not b["collected"] for k in b["keys"]}

    def todo(self, reqs, max_attempts, retry_unparsed):
        bk, fly, out = self.by_key(), self.inflight(), []
        for r in reqs:
            at = bk.get(r["request_key"], [])
            if any(a["complete"] for a in at) or r["request_key"] in fly: continue
            counted = [a for a in at if a["error_kind"] != "credit"]   # an attempt refused for credit was not served
            if len(counted) >= max_attempts: continue
            if counted and not at[-1]["error_kind"] in ("credit", "rate", "transient") and not (retry_unparsed and at[-1]["error_kind"] in ("unparsed", "stop")): continue
            out.append(r)
        return out

    def spent(self): return sum(a["cost_usd"] for a in self.attempts)


# ---------------------------------------------------------------------------------------------------------------- execution
def row_for(req, system_sha, res, err, parse, model, batch, ttl, started):
    row = {c: "" for c in ATTEMPT_COLS}
    row.update(request_key=req["request_key"], unit_ids=" ".join(req["unit_ids"]), started_utc=started, system_sha256=system_sha, user_sha256=req["user_sha256"],
               complete=False, parsed_ok=False, error_kind="", cost_usd=0.0, text=None)
    if err:
        row.update(error_kind=err[0], parse_error=f"call failed ({err[0]}): {err[1][:200]}"); return row
    for k in ("response_id", "model_returned", "stop_reason", "input_tokens", "cached_input_tokens", "cache_write_tokens", "output_tokens", "reasoning_tokens"): row[k] = res[k]
    row["text"] = res["text"]; row["response_sha256"] = sha(res["text"])
    row["cost_usd"] = round(cost(model, batch, res["input_tokens"], res["cached_input_tokens"], res["cache_write_tokens"] or 0, res["output_tokens"], ttl), 6)
    try:
        note = parse(res["text"], req); row["parsed_ok"] = True; row["parse_error"] = note
    except Exception as e:
        row.update(error_kind="unparsed", parse_error=str(e)[:300])
    if row["parsed_ok"] and not res["ok_stop"]: row.update(error_kind="stop", parse_error=f"stop reason {res['stop_reason']}")
    row["complete"] = row["parsed_ok"] and res["ok_stop"]
    return row


def budget_cut(run, a, system, todo, out_est, inflight_est):
    room = a.max_usd - run.spent() - inflight_est; take = []
    for r in todo:
        c = estimate(a.model, a.batch, system, [r], out_est)[2]
        if c > room: break
        take.append(r); room -= c
    return take


def out_estimate(run, a):
    done = [a2["output_tokens"] for a2 in run.attempts if a2["complete"]]
    return 1.25 * (sum(done) / len(done)) if len(done) >= 5 else a.expect_output


def run_sync(run, be, a, system, reqs, parse):
    ssha = sha(system); stop = threading.Event()
    def one(r):
        if stop.is_set(): return
        t = now()
        try: res, err = be.call(system, r["user"]), None
        except Exception as e:
            res, err = None, (classify(e), f"{type(e).__name__}: {e}")
            if err[0] == "credit": stop.set()
            if err[0] == "rate": time.sleep(min(60, 5 * (1 + len(run.by_key().get(r["request_key"], [])))))
        run.add(row_for(r, ssha, res, err, parse, a.model, False, None, t))
    while not stop.is_set():
        todo = run.todo(reqs, a.max_attempts, a.retry_unparsed)
        if not todo: break
        take = budget_cut(run, a, system, todo[: a.chunk], out_estimate(run, a), 0)
        if not take: run.event(f"cost cap reached: {run.spent():.2f} USD measured of {a.max_usd} allowed; {len(todo)} requests not sent"); return EXIT_CAP
        with ThreadPoolExecutor(max_workers=a.concurrency) as ex: list(ex.map(one, take))
        fatal = [x for x in run.attempts[-len(take):] if x["error_kind"] == "fatal"]
        if fatal and len(fatal) == len(take): run.event(f"every call of the last chunk failed with a non-retryable error: {fatal[0]['parse_error']}"); return EXIT_FATAL
    if stop.is_set():
        run.event(f"credit exhausted at {run.spent():.2f} USD measured; top up and run the same command again (completed requests are not sent again)"); return EXIT_CREDIT
    return 0


def collect(run, be, a, system, reqs, parse):
    by_cid = {cid(r["request_key"]): r for r in reqs}; ssha = sha(system); credit = False
    for bid, b in run.state["batches"].items():
        if b["collected"]: continue
        try:
            if not be.ended(bid): continue
        except CreditExhausted as e:
            run.event(str(e)); b["collected"] = True; run.save(); credit = True; continue
        got = set()
        for c, res, err in be.results(bid):
            r = by_cid.get(c)
            if r is None or r["request_key"] not in b["keys"]: continue
            got.add(r["request_key"]); credit |= bool(err and err[0] == "credit")
            run.add(row_for(r, ssha, res, err, parse, a.model, True, getattr(be, "ttl", None), b["submitted_utc"]))
        for k in set(b["keys"]) - got:   # in the batch but without any result line: not served
            run.add(row_for(next(r for r in reqs if r["request_key"] == k), ssha, None, ("transient", "no result line in the batch output"), parse, a.model, True, None, b["submitted_utc"]))
        b["collected"] = True; b["collected_utc"] = now(); run.save(); print(f"batch {bid}: {len(got)} results collected", flush=True)
    return credit


def run_batch(run, be, a, system, reqs, parse):
    while True:
        if collect(run, be, a, system, reqs, parse):
            run.event(f"credit exhausted at {run.spent():.2f} USD measured; top up and run the same command again"); return EXIT_CREDIT
        fly = run.inflight(); oe = out_estimate(run, a)
        fly_est = estimate(a.model, True, system, [r for r in reqs if r["request_key"] in fly], oe)[2]
        todo = run.todo(reqs, a.max_attempts, a.retry_unparsed)
        if todo:
            take = budget_cut(run, a, system, todo[: a.chunk], oe, fly_est)
            if not take and not fly:
                run.event(f"cost cap reached: {run.spent():.2f} USD measured of {a.max_usd} allowed; {len(todo)} requests not sent"); return EXIT_CAP
            if take:
                try: bid = be.submit(system, take)
                except Exception as e:
                    k = classify(e); run.event(f"batch submission refused ({k}): {str(e)[:200]}")
                    return EXIT_CREDIT if k == "credit" else EXIT_FATAL
                run.state["batches"][bid] = {"keys": [r["request_key"] for r in take], "submitted_utc": now(), "collected": False}; run.save()
                print(f"batch {bid} submitted: {len(take)} requests", flush=True); continue
        if not run.inflight(): return 0
        if not a.wait: print(f"{len(run.inflight())} requests in flight; run the same command again to collect them", flush=True); return 0
        time.sleep(a.poll)


def git_commit(allow_dirty):
    head = subprocess.run(["git", "-C", ROOT, "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    dirty = subprocess.run(["git", "-C", ROOT, "status", "--porcelain"], capture_output=True, text=True).stdout.strip()
    if dirty and not allow_dirty: raise SystemExit("the working tree is not clean; commit first (the run record names the commit)")
    return head, bool(dirty)


# expected output tokens per request (for the estimate) and the output limit sent, per stage, when not given: a v12.2
# response carries every observation with its 30 fields and segments, and reasoning counts toward the limit
STAGE_DEFAULTS = {"talk_L1": (400, 8000), "talk_L2": (800, 8000), "extraction_single": (16000, 64000)}


def stage_defaults(a, jm):
    eo, mt = STAGE_DEFAULTS.get(jm["stage"], (400, 8000))
    if a.expect_output is None: a.expect_output = eo
    if a.max_tokens is None: a.max_tokens = mt


def cmd_run(a, client=None):
    reqs, jm, system = load_job(a.job); stage_defaults(a, jm)
    if a.max_usd is None: raise SystemExit("--max-usd is required: no paid run without a cap")
    price(a.model)
    a.cache_key = f"{jm['stage']}-{sha(system)[:16]}"
    be = make_backend(a, client); name = a.run or f"{a.provider}_{a.model}_{be.interface.split('.')[1]}_{dt.date.today():%Y%m%d}"
    run = Run(a.work, name); commit, dirty = git_commit(a.allow_dirty) if client is None else ("0" * 40, False)
    st = run.state; fixed = {"job_sha256": sha(open(os.path.join(a.job, "REQUESTS.jsonl"), encoding="utf-8").read()), "system_sha256": sha(system),
                             "provider": a.provider, "model": a.model, "interface": be.interface, "parameters": be.sent_parameters()}
    for k, v in fixed.items():
        if k in st and st[k] != v: raise SystemExit(f"run {name} was started with another {k}; use a new --run name")
    if "started_utc" not in st:
        st.update(fixed, run=name, stage=jm["stage"], purpose=a.purpose, job=os.path.abspath(a.job), job_meta=jm, git_commit=commit, dirty=dirty,
                  started_utc=now(), sdk=be.sdk, python=platform.python_version(), operator=a.operator, max_usd=a.max_usd, ttl=getattr(be, "ttl", None))
        open(os.path.join(run.dir, "SYSTEM_PROMPT.md"), "wb").write(system.encode("utf-8")); run.save()
    st["max_usd"] = a.max_usd; run.save()
    parse = parser_for(jm["stage"])
    code = (run_batch if a.batch else run_sync)(run, be, a, system, reqs, parse)
    bk = run.by_key(); done = sum(1 for k in bk if any(x["complete"] for x in bk[k]))
    print(f"{name}: {done} of {len(reqs)} requests complete, {len(run.attempts)} attempts, {run.spent():.2f} USD measured (list prices)", flush=True)
    return code


def cmd_plan(a):
    reqs, jm, system = load_job(a.job); stage_defaults(a, jm)
    tin, tout, c = estimate(a.model, a.batch, system, reqs, a.expect_output)
    p = price(a.model)
    cached = sum(len(r["user"]) for r in reqs) / CHARS_PER_TOKEN + len(reqs) * (len(system) / CHARS_PER_TOKEN) * 0.05 + len(system) / CHARS_PER_TOKEN
    lo = cost(a.model, a.batch, int(tin), int(tin - cached), 0, int(tout * 0.5))
    out = {"stage": jm["stage"], "requests": len(reqs), "input_tokens_est": int(tin), "output_tokens_est": int(tout), "model": a.model, "batch": a.batch,
           "usd_cap_estimate": round(c, 2), "usd_likely_low": round(lo, 2), "price_verified": p.get("verified", False)}
    print(json.dumps(out, indent=1)); return out


# ---------------------------------------------------------------------------------------------------------------- record
def cmd_record(a):
    run = Run(a.work, a.run); st = run.state
    if not st.get("started_utc"): raise SystemExit("no such run")
    stage = st["stage"]; out = a.out or os.path.join(ROOT, "data", stage.split("_")[0] if stage.startswith("talk") else stage.split("_")[0], "runs", a.run)
    os.makedirs(out, exist_ok=True)
    open(os.path.join(out, "SYSTEM_PROMPT.md"), "wb").write(open(os.path.join(run.dir, "SYSTEM_PROMPT.md"), "rb").read())
    with open(os.path.join(out, "CALLS.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, rs.CALL_COLS, extrasaction="ignore"); w.writeheader()
        for x in run.attempts: w.writerow({**x, "complete": str(bool(x["complete"])), "parsed_ok": str(bool(x["parsed_ok"])), "attempt": str(x["attempt"])})
    if stage.startswith("talk_"):
        with open(os.path.join(out, "RESPONSES.jsonl"), "w", encoding="utf-8") as fh:
            for x in run.attempts:
                if x["text"] is not None: fh.write(json.dumps({"request_key": x["request_key"], "attempt": x["attempt"], "text": x["text"]}, ensure_ascii=False) + "\n")
    bk = run.by_key(); done = [x for x in run.attempts if x["complete"]]; jm = st["job_meta"]
    unsent = [k for k in jm.get("request_keys", []) if k not in bk]
    dev = list(st["events"]) + ([f"{len(unsent)} requests of the job were never sent"] if unsent else []) + (["working tree was not clean at the start"] if st.get("dirty") else [])
    dev += [f"cost at list prices from measured usage: {run.spent():.2f} USD (cap {st['max_usd']} USD)"]
    meta = {"spec": "run-record v1", "stage": stage, "purpose": st["purpose"], "provider": st["provider"], "interface": st["interface"],
            "model_requested": st["model"], "model_returned": sorted({x["model_returned"] for x in done}) or [""], "parameters": st["parameters"],
            "system_prompt_file": jm["system_prompt_file"], "system_prompt_version": jm["system_prompt_version"], "system_sha256": st["system_sha256"],
            "user_message_format": jm["user_message_format"], "packing": jm["packing"], "inputs": jm["inputs"], "git_commit": st["git_commit"],
            "started_utc": st["started_utc"], "finished_utc": max((x["started_utc"] for x in run.attempts), default=st["started_utc"]),
            "calls": len(bk), "complete": len({x["request_key"] for x in done}), "failed": len(bk) - len({x["request_key"] for x in done}),
            "retried": sum(1 for v in bk.values() if len(v) > 1), "batches": {k: {"requests": len(v["keys"]), "submitted_utc": v["submitted_utc"]} for k, v in st["batches"].items()},
            "usage": {k: sum(int(x[k] or 0) for x in run.attempts) for k in ("input_tokens", "cached_input_tokens", "cache_write_tokens", "output_tokens", "reasoning_tokens")},
            "usage_note": "input_tokens include cached and cache-write tokens on every provider" + ("; Anthropic does not report reasoning tokens apart from output" if st["provider"] == "anthropic" else ""),
            "sdk": st["sdk"], "python": st["python"], "operator": st["operator"] + " (key from the environment, not stored)", "deviations": "; ".join(dev) or "none"}
    json.dump(meta, open(os.path.join(out, "RUN_META.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    P = rs.validate_run(out, a.root or ROOT); print("\n".join(P) if P else f"{out}: run record v1 valid"); return P


def main(argv=None, client=None):
    ap = argparse.ArgumentParser(); sub = ap.add_subparsers(dest="cmd", required=True)
    for n in ("plan", "run"):
        p = sub.add_parser(n); p.add_argument("--job", required=True); p.add_argument("--provider", required=True, choices=["anthropic", "openai", "deepseek"])
        p.add_argument("--model", required=True); p.add_argument("--batch", action="store_true"); p.add_argument("--expect-output", type=int)
        p.add_argument("--max-tokens", type=int); p.add_argument("--effort"); p.add_argument("--thinking", choices=["enabled", "disabled"])
    r = sub.choices["run"]
    r.add_argument("--work", required=True); r.add_argument("--run"); r.add_argument("--purpose", required=True, choices=sorted(rs.PURPOSES)); r.add_argument("--max-usd", type=float)
    r.add_argument("--wait", action="store_true"); r.add_argument("--poll", type=int, default=60); r.add_argument("--chunk", type=int, default=2000)
    r.add_argument("--concurrency", type=int, default=8); r.add_argument("--max-attempts", type=int, default=2); r.add_argument("--retry-unparsed", action="store_true")
    r.add_argument("--operator", default="MB"); r.add_argument("--allow-dirty", action="store_true")
    c = sub.add_parser("record"); c.add_argument("--work", required=True); c.add_argument("--run", required=True); c.add_argument("--out"); c.add_argument("--root")
    a = ap.parse_args(argv)
    if a.cmd == "plan": return cmd_plan(a)
    if a.cmd == "run": return cmd_run(a, client)
    return cmd_record(a)


if __name__ == "__main__":
    res = main(); sys.exit(res if isinstance(res, int) else 0)
