#!/usr/bin/env python3
"""Model-only endorsement census (Phase 1; EXPOSURE_LEDGER 'planned entries').

Question, for every candidate project: does the core corpus contain an explicit statement by the authority competent to set the
requirement that ENDORSES a requirement about whether the issuing central bank (or an operator whose access is attributable to
it) can routinely link an ordinary retail online payment to an identified person (cell F1)? One API request per project with all
its core documents. Output per project is SEALED (written outside the repository; only its SHA-256 and the aggregate counts are
committed), so that the authors see no per-project value before the blind draw.

Categories: endorsed_no (authority endorses that the CB cannot/does not have routine linkage) · endorsed_yes · proposal_only
(statement exists but only as consultation/draft/option) · tested_only · operational_undocumented (live system, no statement) ·
none (no statement found) · unclear. Also records the decision authority, the document type carrying the strongest statement,
and the project's documented issuance decision state.

usage: endorsement_census.py --texts <folder with <JUR>/DOCS.csv+texts> --frame data/frame/projects.csv --contract <md> --model claude-opus-5-5 \
         --sealed-out <path outside repo> --aggregate-out data/census/ENDORSEMENT_CENSUS_aggregate.json
"""
import argparse, csv, hashlib, json, os, sys, collections, datetime as dt
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "extraction"))
from extract_api import Client, parse_array, sha, archive  # noqa

SYSTEM = """You are an evidence auditor for a measurement contract on retail CBDC design. You receive ALL core documents of ONE project, page-delimited
by `=== DOC n PAGE p ===`, with a document list. Answer ONE question from the texts only, with no outside knowledge of the project:

Is there an explicit statement, by the authority competent to set the requirement, that ENDORSES a design requirement about whether the issuing central
bank (or an operator whose routine access is attributable to it) can routinely link an ordinary retail ONLINE payment to an identified natural person?

Endorsement means the competent body (central bank governing body, ministry, legislature, union authority) adopts or commits to the requirement —
including a commitment conditional only on a future issuance decision. A consultation paper, design note, draft, "rough draft", working assumption,
option under study, recommendation or experiment report is NOT endorsement, even if official. A live, operating system counts as operational
evidence if the arrangement is described. "The central bank will not USE/ACCESS the data" is a policy promise; "cannot link / holds no identity
key / sees only pseudonymous data" is an architectural statement — record which basis the statement has.

Return ONLY one JSON array with one object:
[{"category": "endorsed_no|endorsed_yes|proposal_only|tested_only|operational_undocumented|none|unclear",
  "basis": "architectural|policy|cryptographic|n/d", "decision_authority": "<body named in the text or n/d>",
  "strongest_doc": <doc number>, "strongest_doc_id": "<doc_id>", "page": <int>, "quote": "<verbatim <=60 words>",
  "strongest_doc_kind": "<law|decision|final_report|consultation|design_note|experiment_report|annual_report|speech|other>",
  "issuance_decision_state": "issued|decided_to_issue|not_decided|decided_not_now|discontinued|n/d",
  "justification": "<2-4 sentences>", "confidence": "high|medium|low"}]
THE CONTRACT (for the definition of F1 and the status vocabulary):
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--texts", required=True); ap.add_argument("--frame", required=True); ap.add_argument("--contract", required=True)
    ap.add_argument("--provider", default="anthropic"); ap.add_argument("--model", required=True); ap.add_argument("--max-tokens", type=int, default=4000)
    ap.add_argument("--sealed-out", required=True); ap.add_argument("--aggregate-out", required=True); ap.add_argument("--only", default="")
    ap.add_argument("--include-unions", action="store_true")
    a = ap.parse_args()
    contract = open(a.contract, encoding="utf-8").read(); system = SYSTEM + contract
    frame = [r for r in csv.DictReader(open(a.frame, encoding="utf-8"))]
    targets = [r["project"] for r in frame if r["retail_candidate"] == "True" or (a.include_unions and r["union"] == "True")]
    if a.only: targets = [t for t in targets if t in a.only.split(",")]
    cl = Client(a.provider, a.model, a.max_tokens)
    os.makedirs(os.path.dirname(a.sealed_out), exist_ok=True); reqdir = os.path.join(os.path.dirname(a.sealed_out), "census_requests"); os.makedirs(reqdir, exist_ok=True)
    done = {}
    if os.path.exists(a.sealed_out):
        for line in open(a.sealed_out, encoding="utf-8"): r = json.loads(line); done[r["project"]] = r
    for p in targets:
        if p in done: continue
        d = os.path.join(a.texts, p)
        if not os.path.exists(os.path.join(d, "DOCS.csv")): rec = {"project": p, "state": "no_texts"}
        else:
            docs = list(csv.DictReader(open(os.path.join(d, "DOCS.csv"), encoding="utf-8")))
            doclist = "\n".join(f"doc {x['doc']} [{x['doc_id']}]: {x['title']} ({x['year']}; kind {x['kind']}; core {x['core']}; staff_research {x['staff']}; lang {x['lang']})" for x in docs)
            user = f"PROJECT {p}\n\nDOCUMENTS:\n{doclist}\n\n" + "\n\n".join(f"########## DOCUMENT {x['doc']} [{x['doc_id']}] ##########\n" + open(x['file'] if os.path.exists(x['file']) else os.path.join(d, 'texts', os.path.basename(x['file'])), encoding='utf-8', errors='replace').read() for x in docs)
            print(f"[census] {p}: {len(docs)} docs, {len(user)//1000}k chars ...", end=" ", flush=True)
            req = archive(reqdir, f"{p}.user", user)
            try:
                text, meta = cl.call(system, user); rows = parse_array(text); rec = {"project": p, "state": "ok", "result": rows[0] if rows else {}, "meta": meta, "n_docs": len(docs), "chars": len(user), "request_sha256": req["sha256"]}
            except Exception as e: rec = {"project": p, "state": f"failed:{e!r}", "n_docs": len(docs), "chars": len(user)}
            print(rec["state"], rec.get("result", {}).get("category", ""))
        rec["utc"] = dt.datetime.now(dt.timezone.utc).isoformat()
        with open(a.sealed_out, "a", encoding="utf-8") as f: f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        done[p] = rec
    # aggregate only: no per-project values leave the sealed file
    cat = collections.Counter(); kind = collections.Counter(); basis = collections.Counter(); state = collections.Counter(); dec = collections.Counter()
    for p, r in done.items():
        state[r["state"].split(":")[0]] += 1
        if r["state"] == "ok":
            res = r.get("result", {}); cat[res.get("category", "?")] += 1; kind[res.get("strongest_doc_kind", "?")] += 1; basis[res.get("basis", "?")] += 1; dec[res.get("issuance_decision_state", "?")] += 1
    agg = {"as_of": dt.datetime.now(dt.timezone.utc).isoformat(), "model": a.model, "provider": a.provider, "system_sha256": sha(system), "contract_sha256": sha(contract),
           "n_projects": len(done), "states": dict(state), "category": dict(cat), "basis": dict(basis), "strongest_doc_kind": dict(kind), "issuance_decision_state": dict(dec),
           "sealed_file_sha256": hashlib.sha256(open(a.sealed_out, "rb").read()).hexdigest(), "note": "Per-project results are sealed (outside the repository) until after the blind draw; see EXPOSURE_LEDGER.md."}
    os.makedirs(os.path.dirname(a.aggregate_out), exist_ok=True); json.dump(agg, open(a.aggregate_out, "w"), indent=1); print(json.dumps(agg, indent=1))


if __name__ == "__main__": main()
