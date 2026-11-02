#!/usr/bin/env python3
"""Reproducible two-stage extraction of the measurement-contract matrix from a jurisdiction's core documents.

Stage 1 (per document): the model reads ONE document and returns every passage that bears on any contract cell
         (cell, supported value, claim_status, page, verbatim quote, note). No cross-document reasoning.
Stage 2 (synthesis): the model receives only the stage-1 findings of all documents (not the documents) plus the
         document list, and fills the matrix applying the contract's supersession and derivation rules.
Everything is logged: model id, parameters, prompt SHA-256, raw request/response JSON, timestamps, token usage.
A run is a folder `runs/<JUR>_<provider>_<model>_<UTC timestamp>/` and can be re-run bit-for-bit in intent
(temperature 0; outputs may still differ across provider-side model updates — the model id and date are the record).

usage: extract_api.py --jur NO --provider anthropic --model claude-opus-5-5 --indir llm_fill/NO --contract MEASUREMENT_CONTRACT_v1_2026-10-18.md [--cells cells.txt] [--max-doc-chars 400000]
providers: anthropic (ANTHROPIC_API_KEY), openai (OPENAI_API_KEY; also any OpenAI-compatible endpoint via OPENAI_BASE_URL).
No key is ever written to the run folder.
"""
import argparse, csv, datetime as dt, hashlib, json, os, re, sys, time

CELLS = ["F1 CB_LINK_ONLINE", "F2 PSP_LINK_ONLINE", "F3.LE", "F3.FIU", "F3.TAX", "F3.OTHER", "F3 aggregate",
         "F4 PRIVATE_OFFLINE_AVAILABLE", "F7 LOW_ID_ROUTE", "F8 ONBOARDING_ID", "F9 TARGETED_REIDENTIFICATION",
         "F10 PROGRAMMABLE_RESTRICTIONS", "F11 payment_modernisation", "F11 financial_inclusion",
         "F11 monetary_sovereignty_transmission", "F11 cash_substitute_resilience", "F11 aml_cft_tax_enforcement",
         "F11 innovation_competitiveness", "F11 primary_status", "F11 primary_objectives"]
FILL_COLS = ["cell", "value", "evidence_state", "claim_status", "derivation", "doc", "page", "quote", "actor",
             "transaction_scope", "limits", "modality", "legal_state", "superseded", "justification",
             "counter_evidence", "confidence"]

STAGE1_SYSTEM = """You are an extraction instrument for a measurement contract on retail central bank digital currency (CBDC) design. You will receive the full text of ONE official document, page-delimited by lines `=== DOC n PAGE p ===`. Your task is to list every passage in THIS document that bears on any of the contract cells below, with a verbatim quote and the page. Work only from the text provided; use no outside knowledge of the project. Do not aggregate across documents, do not decide final values — only report what this document supports.

Return ONLY a JSON array (no prose). Each element:
{"cell": <one of the cell labels>, "supports_value": <value this passage supports, per contract>, "claim_status": "option|adopted|tested|operational", "page": <int>, "quote": <verbatim, <=60 words, source language>, "direction": "for|against|context", "note": <<=30 words: why this passage bears on the cell; name the actor, scope, limits, modality if the text gives them>}
Include passages that argue AGAINST a value as "direction":"against". If the document says nothing on a cell, do not emit a row for it. Emit at most 8 rows per cell. Quotes must be exact substrings of the text (normalise only whitespace).

CELL LABELS: """ + "; ".join(CELLS) + "\n\nTHE CONTRACT (binding definitions):\n"

STAGE2_SYSTEM = """You are the synthesis stage of an extraction instrument for a measurement contract on retail CBDC design. You receive (a) the list of documents of ONE jurisdiction with their type, year and staff-research flag, and (b) stage-1 findings: passages extracted from each document separately, with page and verbatim quote. You do NOT receive the documents themselves and must not use outside knowledge. Fill the matrix strictly under the contract: absence of a finding = value n/d, evidence_state unknown; a later decision of the competent body supersedes earlier claims on the same matter (name the superseded finding); staff research never establishes adopted/operational; "the central bank will not use/see the data" is not "cannot link"; F2 may be inferred only if findings establish each of the contract's three premises; "tested" is not "adopted"; an offline mode without a privacy description is F4 unknown; F3 aggregate TARGETED_ONLY requires a general norm covering all channels, otherwise partial.

Return ONLY a JSON array with exactly one object per cell label, in the given order, with keys:
""" + ", ".join(FILL_COLS) + """
`doc` and `page` cite the ONE decisive finding (doc number, page); `quote` is copied verbatim from that finding; `justification` = 2–5 sentences a reviewer can check (why this value and not the neighbouring one; which rule decided; further findings as "(doc n p. m)"); `counter_evidence` = the strongest finding for a different value as "doc n p. m: <quote <=25 words>" or "none found"; `confidence` high|medium|low. Unused qualifier fields = "n/d"; `superseded` = "doc n p. m" or "".

CELL LABELS (in order): """ + "; ".join(CELLS) + "\n\nTHE CONTRACT (binding definitions):\n"


def sha(s): return hashlib.sha256(s.encode("utf-8")).hexdigest()


class Client:
    def __init__(self, provider, model, temperature=0.0, max_tokens=16000):
        self.provider, self.model, self.temperature, self.max_tokens = provider, model, temperature, max_tokens
        if provider == "anthropic":
            import anthropic; self.c = anthropic.Anthropic()
        elif provider == "openai":
            import openai; self.c = openai.OpenAI(base_url=os.environ.get("OPENAI_BASE_URL") or None)
        else: raise SystemExit("unknown provider")

    def call(self, system, user):
        t0 = time.time()
        if self.provider == "anthropic":
            # Anthropic API: `temperature` is deprecated/rejected for current models; sampling is provider-controlled.
            # The record of reproducibility is therefore model id + prompt hash + raw response, not a temperature value.
            r = self.c.messages.create(model=self.model, max_tokens=self.max_tokens,
                                       system=system, messages=[{"role": "user", "content": user}])
            text = "".join(b.text for b in r.content if getattr(b, "type", "") == "text")
            meta = {"response_id": r.id, "model_returned": r.model, "stop_reason": r.stop_reason,
                    "usage": {"input_tokens": r.usage.input_tokens, "output_tokens": r.usage.output_tokens}}
        else:
            r = self.c.chat.completions.create(model=self.model, temperature=self.temperature, max_tokens=self.max_tokens,
                                               messages=[{"role": "system", "content": system}, {"role": "user", "content": user}])
            text = r.choices[0].message.content
            meta = {"response_id": r.id, "model_returned": r.model, "stop_reason": r.choices[0].finish_reason,
                    "usage": {"input_tokens": r.usage.prompt_tokens, "output_tokens": r.usage.completion_tokens}}
        meta["seconds"] = round(time.time() - t0, 1)
        return text, meta


def parse_json(text):
    m = re.search(r"\[.*\]", text, re.S)
    if not m: raise ValueError("no JSON array in response")
    return json.loads(m.group(0))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--jur", required=True); ap.add_argument("--provider", default="anthropic")
    ap.add_argument("--model", required=True); ap.add_argument("--indir", required=True); ap.add_argument("--contract", required=True)
    ap.add_argument("--outroot", default="runs"); ap.add_argument("--max-doc-chars", type=int, default=400000)
    ap.add_argument("--temperature", type=float, default=0.0); ap.add_argument("--stage1-only", action="store_true")
    a = ap.parse_args()
    ts = dt.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    run = os.path.join(a.outroot, f"{a.jur}_{a.provider}_{a.model}_{ts}"); os.makedirs(os.path.join(run, "stage1"), exist_ok=True)
    contract = open(a.contract, encoding="utf-8").read()
    docs = list(csv.DictReader(open(os.path.join(a.indir, "DOCS.csv"), encoding="utf-8")))
    cl = Client(a.provider, a.model, a.temperature)
    temp_rec = "not_settable (provider rejects temperature for this model)" if a.provider == "anthropic" else a.temperature
    manifest = {"jur": a.jur, "provider": a.provider, "model": a.model, "temperature": temp_rec, "run_utc": ts,
                "contract_sha256": sha(contract), "contract_file": os.path.basename(a.contract),
                "stage1_system_sha256": sha(STAGE1_SYSTEM + contract), "stage2_system_sha256": sha(STAGE2_SYSTEM + contract),
                "cells": CELLS, "docs": [], "stage1": [], "stage2": None, "script_sha256": sha(open(__file__, encoding="utf-8").read())}
    findings = []
    for d in docs:
        p = os.path.join(a.indir, os.path.basename(os.path.dirname(d["file"])), os.path.basename(d["file"])) if not os.path.exists(d["file"]) else d["file"]
        txt = open(p, encoding="utf-8", errors="replace").read()
        manifest["docs"].append({"doc": d["doc"], "doc_id": d["doc_id"], "title": d["title"], "year": d["year"], "core": d["core"],
                                 "staff": d["staff"], "kind": d["kind"], "chars": len(txt), "text_sha256": sha(txt), "truncated": len(txt) > a.max_doc_chars})
        user = f"DOCUMENT {d['doc']} | {d['doc_id']} | {d['title']} | year {d['year']} | kind {d['kind']} | staff_research {d['staff']}\n\n" + txt[:a.max_doc_chars]
        print(f"[stage1] doc {d['doc']} ({len(txt)//1000}k chars) ...", end=" ", flush=True)
        try:
            text, meta = cl.call(STAGE1_SYSTEM + contract, user)
            rows = parse_json(text); err = ""
        except Exception as e:
            text, meta, rows, err = str(e), {}, [], repr(e)
        for r in rows: r["doc"] = int(d["doc"])
        findings += rows
        json.dump({"doc": d["doc"], "user_sha256": sha(user), "meta": meta, "error": err, "raw": text, "rows": rows},
                  open(os.path.join(run, "stage1", f"doc{int(d['doc']):02d}.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        manifest["stage1"].append({"doc": d["doc"], "rows": len(rows), "error": err, **meta}); print(len(rows), "rows", err)
    with open(os.path.join(run, "stage1_findings.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["doc", "cell", "supports_value", "claim_status", "page", "quote", "direction", "note"], extrasaction="ignore")
        w.writeheader(); [w.writerow(r) for r in findings]
    json.dump(manifest, open(os.path.join(run, "MANIFEST.json"), "w"), indent=1)
    if a.stage1_only: print("stage1 only; run folder:", run); return
    doclist = "\n".join(f"doc {d['doc']}: {d['title']} ({d['year']}; kind {d['kind']}; core {d['core']}; staff_research {d['staff']})" for d in docs)
    user = f"JURISDICTION {a.jur}\n\nDOCUMENTS:\n{doclist}\n\nSTAGE-1 FINDINGS (JSON):\n" + json.dumps(findings, ensure_ascii=False)
    print(f"[stage2] {len(findings)} findings ...", end=" ", flush=True)
    text, meta = cl.call(STAGE2_SYSTEM + contract, user)
    try: rows = parse_json(text); err = ""
    except Exception as e: rows, err = [], repr(e)
    json.dump({"user_sha256": sha(user), "meta": meta, "error": err, "raw": text}, open(os.path.join(run, "stage2.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    manifest["stage2"] = {"findings_in": len(findings), "rows": len(rows), "error": err, **meta}
    with open(os.path.join(run, "FILL.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FILL_COLS, extrasaction="ignore"); w.writeheader()
        for c in CELLS:
            r = next((x for x in rows if x.get("cell") == c), {"cell": c, "value": "n/d", "evidence_state": "unknown"})
            w.writerow({k: r.get(k, "") for k in FILL_COLS})
    json.dump(manifest, open(os.path.join(run, "MANIFEST.json"), "w"), indent=1)
    print(len(rows), "rows", err, "\nrun folder:", run)


if __name__ == "__main__": main()
