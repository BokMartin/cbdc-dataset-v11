#!/usr/bin/env python3
"""Reproducible extraction of the measurement-contract matrix from a project's core documents — v2 (ADR-001 E16/E17).

Changes from the 18 Oct version (archived in archive/run_scripts/):
  * a machine-readable cell schema (schema/cells_*.json) defines cells, allowed values and columns; outputs are validated against it
  * processing states are explicit: a document that fails (call error, unparseable or truncated output, over-long input) is
    recorded as processing_failed; synthesis is NOT run unless every document succeeded (or --allow-incomplete, which marks the run
    status 'incomplete' and every cell 'incomplete'); nothing is salvaged from truncated arrays in production (stop_reason max_tokens → failed)
  * no silent truncation of document text; an over-long document fails with reason too_long (deterministic splitting is a later, separate feature)
  * full request archive: every system and user payload is written to the run folder (requests/*.txt.gz) with its SHA-256
  * the script copies itself into the run folder; manifest records SDK versions and Python version
  * resume only with an identity key (sha256 of system prompt + contract + document text + model + max_tokens + schema); mismatch → fresh call
  * stage-one findings carry structured qualifier fields (actor, transaction_scope, limits, modality) and the registry doc_id; no row cap
  * two modes retained: single (all documents in one request) and two-stage (per-document findings → synthesis from findings)

usage: extract_api.py --jur NO --provider anthropic --model claude-opus-5-5 --mode single|two-stage|both \
         --indir <DOCS.csv + texts/> --contract docs/MEASUREMENT_CONTRACT_v1_1_2026-10-18.md --schema schema/cells_v1_1.json --outroot runs
providers: anthropic (ANTHROPIC_API_KEY), openai (OPENAI_API_KEY, optional OPENAI_BASE_URL). No key is ever written to the run folder.
"""
import argparse, csv, datetime as dt, gzip, hashlib, json, os, platform, re, shutil, sys, time

FILL_DEFAULT = {"value": "n/d", "evidence_state": "unknown", "claim_status": "", "derivation": "n.a."}


def sha(s): return hashlib.sha256(s.encode("utf-8")).hexdigest()


def build_prompts(schema, contract):
    cells = schema["cells"]; allowed = {c: v for c, v in schema["values"].items() if v}
    cell_block = "\n".join(f"- {c}: {' / '.join(allowed[c]) if c in allowed else 'free text'}" for c in cells)
    stage1 = ("You are an extraction instrument for a measurement contract on retail central bank digital currency (CBDC) design. You receive the full text of ONE "
              "official document, page-delimited by lines `=== DOC n PAGE p ===`. List every passage in THIS document that bears on any contract cell, with a verbatim quote and "
              "the page. Work only from the text; use no outside knowledge. Do not aggregate across documents or decide final values.\n\n"
              "Return ONLY a JSON array. Each element: {\"cell\": <cell label>, \"supports_value\": <value per contract>, \"claim_status\": \"option|adopted|tested|operational\", "
              "\"page\": <int>, \"quote\": <verbatim, <=60 words, source language, exact substring>, \"direction\": \"for|against|context\", "
              "\"actor\": <who: CB / operator / PSP / named authority / user / n/d>, \"transaction_scope\": <online / offline / tier / limit band / n/d>, "
              "\"limits\": <amounts, counts, time windows / n/d>, \"modality\": <unconditional / conditional: <condition> / n/d>, \"note\": <<=40 words>}\n"
              "Report every relevant passage (no cap); include passages arguing AGAINST a value as direction=against. Emit nothing for cells the document is silent on.\n\n"
              f"CELLS AND ALLOWED VALUES:\n{cell_block}\n\nTHE CONTRACT (binding definitions):\n{contract}")
    fill_cols = ", ".join(schema["fill_columns"])
    rules = ("Fill the matrix strictly under the contract: absence of a finding = value n/d, evidence_state unknown; a later decision of the competent body supersedes earlier "
             "claims on the same matter (name the superseded finding); staff research never establishes adopted/operational; 'the central bank will not use/see the data' is not "
             "'cannot link'; F2 may be inferred only if each of the contract's three premises is documented for the same participant, mode and design version; 'tested' is not 'adopted'; "
             "an offline mode without a privacy description is F4 unknown; F3 is a descriptive route (via_PSP / via_CB / via_both / none_stated / n/d), never a level of access; "
             "F7 = no requires an explicit all-routes identification requirement — silence about other routes gives n/d; F12: a platform used only in a PoC is claim_status tested; "
             "'technology-neutral' → undecided.")
    stage2 = ("You are the synthesis stage of an extraction instrument for a measurement contract on retail CBDC design. You receive (a) the list of documents of ONE jurisdiction "
              "with type, year and staff-research flag, and (b) stage-1 findings extracted from each document separately, with page, verbatim quote and qualifiers. You do NOT "
              f"receive the documents and must not use outside knowledge. {rules}\n\nReturn ONLY a JSON array with exactly one object per cell label, in the given order, with keys: "
              f"{fill_cols}. `doc` and `page` cite the ONE decisive finding (doc number, page); `doc_id` is that finding's doc_id; `quote` is copied verbatim from that finding; "
              "`justification` = 2–5 checkable sentences (why this value and not the neighbouring one; which rule decided; further findings as '(doc n p. m)'); "
              "`counter_evidence` = the strongest finding for a different value as 'doc n p. m: <quote <=25 words>' or 'none found'; `confidence` high|medium|low; "
              f"unused qualifier fields 'n/d'; `superseded` = 'doc n p. m' or ''.\n\nCELLS AND ALLOWED VALUES (in order):\n{cell_block}\n\nTHE CONTRACT (binding definitions):\n{contract}")
    single = ("You are an extraction instrument for a measurement contract on retail central bank digital currency (CBDC) design. You receive ALL core documents of ONE jurisdiction, "
              "each page-delimited by lines `=== DOC n PAGE p ===`, with a document list (doc_id, type, year, staff-research flag). Work only from the texts; no outside knowledge "
              f"of the project. {rules}\n\nReturn ONLY a JSON array with exactly one object per cell label, in the given order, with keys: {fill_cols}. `doc` and `page` cite the ONE "
              "decisive passage (doc number, page marker); `doc_id` that document's id; `quote` verbatim (<=60 words, exact substring); `justification` = 2–5 checkable sentences; "
              "`counter_evidence` = strongest passage for a different value as 'doc n p. m: <quote <=25 words>' or 'none found'; `confidence` high|medium|low; unused qualifier "
              f"fields 'n/d'; `superseded` = 'doc n p. m' or ''.\n\nCELLS AND ALLOWED VALUES (in order):\n{cell_block}\n\nTHE CONTRACT (binding definitions):\n{contract}")
    return {"stage1": stage1, "stage2": stage2, "single": single}


class Client:
    def __init__(self, provider, model, max_tokens):
        self.provider, self.model, self.max_tokens = provider, model, max_tokens
        if provider == "anthropic":
            import anthropic; self.c = anthropic.Anthropic(); self.sdk = f"anthropic {anthropic.__version__}"
        elif provider == "openai":
            import openai; self.c = openai.OpenAI(base_url=os.environ.get("OPENAI_BASE_URL") or None); self.sdk = f"openai {openai.__version__}"
        else: raise SystemExit("unknown provider")

    def call(self, system, user):
        t0 = time.time(); ts = dt.datetime.now(dt.timezone.utc).isoformat()
        if self.provider == "anthropic":
            # temperature is not accepted by the provider for current models; sampling is provider-controlled (recorded in manifest)
            with self.c.messages.stream(model=self.model, max_tokens=self.max_tokens, system=system, messages=[{"role": "user", "content": user}]) as st:
                r = st.get_final_message()
            text = "".join(b.text for b in r.content if getattr(b, "type", "") == "text")
            meta = {"response_id": r.id, "model_returned": r.model, "stop_reason": r.stop_reason, "usage": {"input_tokens": r.usage.input_tokens, "output_tokens": r.usage.output_tokens}}
        else:
            r = self.c.chat.completions.create(model=self.model, max_tokens=self.max_tokens, temperature=0, messages=[{"role": "system", "content": system}, {"role": "user", "content": user}])
            text = r.choices[0].message.content or ""
            meta = {"response_id": r.id, "model_returned": r.model, "stop_reason": r.choices[0].finish_reason, "usage": {"input_tokens": r.usage.prompt_tokens, "output_tokens": r.usage.completion_tokens}, "temperature": 0}
        meta.update({"started_utc": ts, "seconds": round(time.time() - t0, 1)})
        return text, meta


def parse_array(text):
    """Strict: the response must contain one complete JSON array. Truncated or malformed output is a failure, never salvaged."""
    m = re.search(r"\[.*\]", text, re.S)
    if not m: raise ValueError("no JSON array in response")
    arr = json.loads(m.group(0))
    if not isinstance(arr, list): raise ValueError("top-level JSON is not an array")
    return arr


def validate_fill(rows, schema):
    """Strict output validation: complete cell list, no duplicates, allowed enums. Returns (ok_rows, problems)."""
    problems = []; by = {}
    for r in rows:
        c = r.get("cell")
        if c not in schema["cells"]: problems.append(f"unknown cell {c!r}"); continue
        if c in by: problems.append(f"duplicate cell {c}"); continue
        allowed = schema["values"].get(c)
        v = str(r.get("value", "")).strip()
        if allowed and v not in allowed:
            # tolerate case/synonym variants but record them
            low = {a.lower(): a for a in allowed}
            if v.lower() in low: r["value"] = low[v.lower()]
            elif v.lower() in ("unknown", "", "none", "undetermined"): r["value"] = "n/d"
            else: problems.append(f"{c}: value {v!r} not in {allowed}")
        for fld, enum in (("evidence_state", schema["evidence_state"]), ("claim_status", schema["claim_status"]), ("derivation", schema["derivation"])):
            if str(r.get(fld, "")).strip() not in enum: problems.append(f"{c}: {fld}={r.get(fld)!r} not allowed")
        by[c] = r
    for c in schema["cells"]:
        if c not in by: problems.append(f"missing cell {c}")
    return by, problems


def archive(run, name, text):
    os.makedirs(os.path.join(run, "requests"), exist_ok=True)
    p = os.path.join(run, "requests", name + ".txt.gz")
    with gzip.open(p, "wt", encoding="utf-8") as f: f.write(text)
    return {"file": os.path.relpath(p, run), "sha256": sha(text), "chars": len(text)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--jur", required=True); ap.add_argument("--provider", default="anthropic"); ap.add_argument("--model", required=True)
    ap.add_argument("--indir", required=True); ap.add_argument("--contract", required=True); ap.add_argument("--schema", required=True)
    ap.add_argument("--outroot", default="runs"); ap.add_argument("--mode", choices=["single", "two-stage", "both"], default="single")
    ap.add_argument("--max-tokens", type=int, default=32000); ap.add_argument("--max-doc-chars", type=int, default=1_500_000, help="documents longer than this FAIL (no truncation)")
    ap.add_argument("--resume", default="", help="earlier run folder; stage-1 outputs are reused only when their identity key matches")
    ap.add_argument("--allow-incomplete", action="store_true", help="run synthesis even if a document failed; the run and every cell are marked incomplete")
    a = ap.parse_args()
    ts = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run = os.path.join(a.outroot, f"{a.jur}_{a.provider}_{a.model}_{a.mode}_{ts}"); os.makedirs(os.path.join(run, "stage1"), exist_ok=True)
    shutil.copy(__file__, os.path.join(run, "extract_api.py")); shutil.copy(a.schema, os.path.join(run, "schema.json")); shutil.copy(a.contract, os.path.join(run, "contract.md"))
    contract = open(a.contract, encoding="utf-8").read(); schema = json.load(open(a.schema, encoding="utf-8")); P = build_prompts(schema, contract)
    docs = list(csv.DictReader(open(os.path.join(a.indir, "DOCS.csv"), encoding="utf-8")))
    cl = Client(a.provider, a.model, a.max_tokens)
    manifest = {"jur": a.jur, "provider": a.provider, "model_requested": a.model, "mode": a.mode, "run_utc": ts, "status": "running",
                "temperature": ("not_settable (provider rejects temperature for current models; provider-controlled sampling)" if a.provider == "anthropic" else 0),
                "max_tokens": a.max_tokens, "max_doc_chars": a.max_doc_chars, "python": platform.python_version(), "sdk": cl.sdk,
                "contract_file": os.path.basename(a.contract), "contract_sha256": sha(contract), "schema_file": os.path.basename(a.schema), "schema_sha256": sha(open(a.schema, encoding="utf-8").read()),
                "script_sha256": sha(open(__file__, encoding="utf-8").read()), "prompts_sha256": {k: sha(v) for k, v in P.items()}, "docs": [], "stage1": [], "single": None, "stage2": None, "problems": []}
    texts = {}
    for d in docs:
        p = d["file"] if os.path.exists(d["file"]) else os.path.join(a.indir, "texts", os.path.basename(d["file"]))
        texts[d["doc"]] = open(p, encoding="utf-8", errors="replace").read()
        manifest["docs"].append({"doc": d["doc"], "doc_id": d["doc_id"], "title": d["title"], "year": d["year"], "core": d.get("core", ""), "staff": d.get("staff", ""), "kind": d.get("kind", ""),
                                 "chars": len(texts[d["doc"]]), "text_sha256": sha(texts[d["doc"]]), "too_long": len(texts[d["doc"]]) > a.max_doc_chars})
    doclist = "\n".join(f"doc {d['doc']} [{d['doc_id']}]: {d['title']} ({d['year']}; kind {d.get('kind','')}; core {d.get('core','')}; staff_research {d.get('staff','')})" for d in docs)

    def write_fill(rows_by_cell, name, run_state):
        with open(os.path.join(run, name), "w", newline="", encoding="utf-8") as f:
            cols = schema["fill_columns"] + ["processing_state"]
            w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore"); w.writeheader()
            for c in schema["cells"]:
                r = dict(FILL_DEFAULT); r.update(rows_by_cell.get(c, {})); r["cell"] = c; r["processing_state"] = run_state
                w.writerow({k: r.get(k, "") for k in cols})

    def do_call(kind, system, user, label):
        req = {"system": archive(run, f"{label}.system", system), "user": archive(run, f"{label}.user", user)}
        try: text, meta = cl.call(system, user)
        except Exception as e: return None, {"call_error": repr(e)}, req, f"processing_failed:call_error"
        resp = archive(run, f"{label}.response", text)
        if meta.get("stop_reason") in ("max_tokens", "length"): return text, meta | {"response": resp}, req, "processing_failed:truncated_output"
        try: rows = parse_array(text)
        except Exception as e: return text, meta | {"response": resp, "parse_error": repr(e)}, req, "processing_failed:unparseable"
        return rows, meta | {"response": resp}, req, "ok"

    if a.mode in ("single", "both"):
        too_long = [d["doc"] for d in manifest["docs"] if d["too_long"]]
        if too_long:
            manifest["single"] = {"state": "processing_failed:too_long", "docs": too_long}; write_fill({}, "FILL_single.csv" if a.mode == "both" else "FILL.csv", "processing_failed")
        else:
            user = f"JURISDICTION {a.jur}\n\nDOCUMENTS:\n{doclist}\n\n" + "\n\n".join(f"########## DOCUMENT {d['doc']} [{d['doc_id']}] ##########\n" + texts[d['doc']] for d in docs)
            print(f"[single] {len(user)//1000}k chars ...", end=" ", flush=True)
            rows, meta, req, state = do_call("single", P["single"], user, "single")
            by, problems = ({}, []) if state != "ok" else validate_fill(rows, schema)
            if problems: manifest["problems"] += [f"single: {x}" for x in problems]
            manifest["single"] = {"state": state, "rows": len(rows) if isinstance(rows, list) else 0, "validation_problems": problems, "request": req, **({} if meta is None else meta)}
            print(state, len(problems), "validation problems")
            write_fill(by, "FILL_single.csv" if a.mode == "both" else "FILL.csv", state if state != "ok" else ("ok" if not problems else "ok_with_validation_problems"))
        json.dump(manifest, open(os.path.join(run, "MANIFEST.json"), "w"), indent=1)
        if a.mode == "single": manifest["status"] = manifest["single"]["state"]; json.dump(manifest, open(os.path.join(run, "MANIFEST.json"), "w"), indent=1); print("run folder:", run); return

    findings = []; failed = []
    for d in docs:
        txt = texts[d["doc"]]; label = f"stage1_doc{int(d['doc']):02d}"
        user = f"DOCUMENT {d['doc']} [{d['doc_id']}] | {d['title']} | year {d['year']} | kind {d.get('kind','')} | staff_research {d.get('staff','')}\n\n" + txt
        key = sha(P["stage1"] + "|" + txt + "|" + a.model + "|" + str(a.max_tokens) + "|" + manifest["schema_sha256"])
        print(f"[stage1] doc {d['doc']} ({len(txt)//1000}k chars) ...", end=" ", flush=True)
        prev = os.path.join(a.resume, "stage1", f"doc{int(d['doc']):02d}.json") if a.resume else ""
        reused = False
        if prev and os.path.exists(prev):
            pj = json.load(open(prev, encoding="utf-8"))
            if pj.get("identity_key") == key and pj.get("state") == "ok": rows, meta, req, state = pj["rows"], pj["meta"] | {"reused_from": prev}, pj.get("request"), "ok"; reused = True
        if not reused:
            if len(txt) > a.max_doc_chars: rows, meta, req, state = None, {}, None, "processing_failed:too_long"
            else: rows, meta, req, state = do_call("stage1", P["stage1"], user, label)
        if state == "ok":
            for r in rows: r["doc"] = int(d["doc"]); r["doc_id"] = d["doc_id"]
            findings += rows
        else: failed.append({"doc": d["doc"], "doc_id": d["doc_id"], "state": state})
        json.dump({"doc": d["doc"], "doc_id": d["doc_id"], "identity_key": key, "state": state, "meta": meta, "request": req, "rows": rows if state == "ok" else []},
                  open(os.path.join(run, "stage1", f"doc{int(d['doc']):02d}.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        manifest["stage1"].append({"doc": d["doc"], "doc_id": d["doc_id"], "state": state, "rows": len(rows) if state == "ok" else 0, "reused": reused, **{k: v for k, v in (meta or {}).items() if k != "response"}})
        print(state, len(rows) if state == "ok" else 0, "rows")
    with open(os.path.join(run, "stage1_findings.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=schema["finding_columns"], extrasaction="ignore"); w.writeheader(); [w.writerow(r) for r in findings]
    if failed and not a.allow_incomplete:
        manifest["status"] = "incomplete:stage1_failures"; manifest["stage2"] = {"state": "not_run", "reason": "stage-1 failures", "failed": failed}
        write_fill({}, "FILL_two_stage.csv" if a.mode == "both" else "FILL.csv", "incomplete")
        json.dump(manifest, open(os.path.join(run, "MANIFEST.json"), "w"), indent=1); print("HALT: stage-1 failures", failed, "\nrun folder:", run); return
    user = f"JURISDICTION {a.jur}\n\nDOCUMENTS:\n{doclist}\n\nSTAGE-1 FINDINGS (JSON):\n" + json.dumps(findings, ensure_ascii=False)
    print(f"[stage2] {len(findings)} findings ...", end=" ", flush=True)
    rows, meta, req, state = do_call("stage2", P["stage2"], user, "stage2")
    by, problems = ({}, []) if state != "ok" else validate_fill(rows, schema)
    if problems: manifest["problems"] += [f"stage2: {x}" for x in problems]
    run_state = state if state != "ok" else ("incomplete" if failed else ("ok" if not problems else "ok_with_validation_problems"))
    manifest["stage2"] = {"state": state, "findings_in": len(findings), "rows": len(rows) if isinstance(rows, list) else 0, "validation_problems": problems, "failed_docs": failed, "request": req, **({} if meta is None else meta)}
    write_fill(by, "FILL_two_stage.csv" if a.mode == "both" else "FILL.csv", run_state)
    manifest["status"] = run_state; json.dump(manifest, open(os.path.join(run, "MANIFEST.json"), "w"), indent=1)
    print(state, len(problems), "validation problems", "\nrun folder:", run)


if __name__ == "__main__": main()
