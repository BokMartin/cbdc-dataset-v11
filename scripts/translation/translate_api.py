#!/usr/bin/env python3
"""Run the translation requests through a model API, one clean call per chunk (system prompt + one user message, no history).

Reads <pack>/TRANSLATION_REQUESTS_<date>.csv, sends pipeline/prompts/translation.system.md as system prompt and the request file as
the user message, verifies before sending that the request file still has the registered SHA-256, and writes for every chunk
<pack>/responses/<run>/<doc_key>/<request name>.response.txt (the raw output, unedited) and .meta.json (provider, model as returned,
response id, stop reason, token usage, timestamps, SHA-256 of system prompt / user message / response). A chunk whose response file
exists is skipped (resume). A response that stops for length or lacks the END marker is kept but marked failed in the meta file;
ingest_translations.py refuses it. No key is written anywhere: ANTHROPIC_API_KEY / OPENAI_API_KEY (optional OPENAI_BASE_URL) from the environment.

usage: translate_api.py --pack <dir> --date 2026-11-10 --provider openai --model <model id> --run <run name> [--priority A] [--only doc_key ...] [--max-tokens 32000] [--limit N]
"""
import argparse, csv, datetime as dt, hashlib, json, os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))


def sha(s): return hashlib.sha256(s.encode("utf-8")).hexdigest()


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--pack", required=True); ap.add_argument("--date", required=True); ap.add_argument("--provider", required=True, choices=["openai", "anthropic"])
    ap.add_argument("--model", required=True); ap.add_argument("--run", required=True); ap.add_argument("--priority", default="A"); ap.add_argument("--only", nargs="*"); ap.add_argument("--max-tokens", type=int, default=32000); ap.add_argument("--limit", type=int)
    a = ap.parse_args()
    system = open(os.path.join(ROOT, "pipeline/prompts/translation.system.md"), encoding="utf-8").read()
    prio = {q["doc_key"]: q["priority"] for q in csv.DictReader(open(os.path.join(a.pack, f"TRANSLATION_QUEUE_{a.date}.csv"), encoding="utf-8"))}
    reqs = [r for r in csv.DictReader(open(os.path.join(a.pack, f"TRANSLATION_REQUESTS_{a.date}.csv"), encoding="utf-8")) if (r["doc_key"] in a.only if a.only else prio[r["doc_key"]] in a.priority.split(","))]
    if a.provider == "anthropic":
        import anthropic; cl = anthropic.Anthropic(); sdk = f"anthropic {anthropic.__version__}"
    else:
        import openai; cl = openai.OpenAI(base_url=os.environ.get("OPENAI_BASE_URL") or None); sdk = f"openai {openai.__version__}"
    out = os.path.join(a.pack, "responses", a.run); os.makedirs(out, exist_ok=True)
    json.dump({"run": a.run, "provider": a.provider, "model_requested": a.model, "max_tokens": a.max_tokens, "sdk": sdk, "python": sys.version.split()[0], "system_sha256": sha(system),
               "system_prompt_file": "pipeline/prompts/translation.system.md", "started_utc": dt.datetime.now(dt.timezone.utc).isoformat(), "interface": "API", "requests_selected": len(reqs)},
              open(os.path.join(out, "RUN_META.json"), "w"), indent=1)
    done = 0
    for r in reqs:
        d = os.path.join(out, r["doc_key"]); os.makedirs(d, exist_ok=True); base = os.path.join(d, os.path.basename(r["request_file"])[:-4])
        if os.path.exists(base + ".response.txt"): continue
        if a.limit and done >= a.limit: break
        user = open(os.path.join(a.pack, r["request_file"]), encoding="utf-8").read()
        if sha(user) != r["user_sha256"]: raise SystemExit(f"request file changed since it was registered: {r['request_file']}")
        t0 = time.time(); ts = dt.datetime.now(dt.timezone.utc).isoformat()
        try:
            if a.provider == "anthropic":
                with cl.messages.stream(model=a.model, max_tokens=a.max_tokens, system=system, messages=[{"role": "user", "content": user}]) as st: m = st.get_final_message()
                text = "".join(b.text for b in m.content if getattr(b, "type", "") == "text")
                meta = {"response_id": m.id, "model_returned": m.model, "stop_reason": m.stop_reason, "usage": {"input_tokens": m.usage.input_tokens, "output_tokens": m.usage.output_tokens}, "temperature": "provider-controlled (not settable)"}
            else:
                m = cl.responses.create(model=a.model, instructions=system, input=user, max_output_tokens=a.max_tokens)
                text = m.output_text; meta = {"response_id": m.id, "model_returned": m.model, "stop_reason": m.status + ("/" + m.incomplete_details.reason if getattr(m, "incomplete_details", None) else ""),
                                              "usage": {"input_tokens": m.usage.input_tokens, "output_tokens": m.usage.output_tokens}, "temperature": "provider default (not sent)"}
        except Exception as e:
            print("FAILED", r["request_file"], type(e).__name__, str(e)[:200]); continue
        ok = text.rstrip().endswith("=== END OF CHUNK ===") and meta["stop_reason"] in ("end_turn", "completed", "stop")
        open(base + ".response.txt", "w", encoding="utf-8", newline="\n").write(text)
        meta.update({"doc_key": r["doc_key"], "chunk": int(r["chunk"]), "of": int(r["of"]), "provider": a.provider, "model_requested": a.model, "started_utc": ts, "seconds": round(time.time() - t0, 1),
                     "system_sha256": sha(system), "user_sha256": r["user_sha256"], "response_sha256": sha(text), "complete": ok})
        json.dump(meta, open(base + ".meta.json", "w"), indent=1); done += 1
        print("ok " if ok else "INCOMPLETE", r["request_file"], meta["usage"], meta["seconds"], "s")
    print(done, "calls made; run folder", out)


if __name__ == "__main__": main()
