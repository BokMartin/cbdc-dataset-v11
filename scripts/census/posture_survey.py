#!/usr/bin/env python3
"""Sealed statement-type survey of the core corpus (development of the privacy-posture layer, 2 Nov 2026).

One request per core document: list every statement about privacy / identifiability / data access in the document, typed from
a fixed typology, with status, basis, actor, page and a short quote. Per-document output is SEALED off-repo (per-project values
would expose the project); the committed aggregate counts statement types × status × document kind and the number of
projects with at least one statement of each type, without naming projects. Example quotes for the design memo are taken
only from already-exposed projects (NO, UK) — see EXPOSURE_LEDGER.

usage: posture_survey.py --texts <folder> --frame projects.csv --model claude-opus-5-5 --sealed-out <off-repo .jsonl> \
         --aggregate-out data/census/POSTURE_SURVEY_aggregate.json [--workers 4] [--only NO,UK]
"""
import argparse, csv, hashlib, json, os, sys, collections, datetime as dt, threading
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "extraction"))
from extract_api import Client, parse_array, sha, archive  # noqa

TYPES = ["PRINCIPLE", "CB_NO_PERSONAL_DATA", "CB_SEES_DATA", "PSP_HOLDS_IDENTITY", "PSEUDONYMISATION", "TIERED_LOW_ID", "ANONYMITY_REJECTED",
         "OFFLINE_PRIVACY", "LAWFUL_ACCESS", "DATA_MINIMISATION", "USER_CONTROL_CONSENT", "NO_COMMERCIAL_USE", "PROGRAMMABILITY", "PET_TECHNIQUE",
         "LEGAL_COMMITMENT", "PRIVACY_AS_RISK_OR_TRADEOFF", "OTHER"]
SYSTEM = f"""You are an evidence auditor for a research dataset on retail CBDC privacy design. You receive ONE official document, page-delimited by
`=== DOC n PAGE p ===`. List EVERY distinct statement in it that concerns the privacy, identifiability, personal-data access or anonymity of
retail CBDC users (payer/payee). Work from the text only. Do not infer; a statement is what the document says.

Type each statement with exactly one of: {", ".join(TYPES)}.
  PRINCIPLE: privacy/data protection named as a principle, objective, requirement or design goal, without a specific mechanism.
  CB_NO_PERSONAL_DATA: the central bank (or its core system) will not / cannot see or hold personal/transaction-identity data.
  CB_SEES_DATA: the central bank will / may see or hold such data.
  PSP_HOLDS_IDENTITY: intermediaries/PSPs hold identity and/or see transactions.
  PSEUDONYMISATION: pseudonymous identifiers, tokenised identity, separation of identity from transaction data.
  TIERED_LOW_ID: wallets/tiers usable without (full) identity verification, with limits.
  ANONYMITY_REJECTED: explicit statement that full/cash-like anonymity will not be offered.
  OFFLINE_PRIVACY: privacy properties of an offline mode.
  LAWFUL_ACCESS: access by law enforcement / public authorities / AML-CFT obligations.
  DATA_MINIMISATION: collect/retain only what is necessary. USER_CONTROL_CONSENT: user control, consent, choice over data.
  NO_COMMERCIAL_USE: restriction on commercial use of data. PROGRAMMABILITY: issuer/state-imposed restrictions on use (for or against).
  PET_TECHNIQUE: named privacy technique (ZKP, blind signatures, Tourbillon-style, etc.). LEGAL_COMMITMENT: statutory/legislative privacy commitment.
  PRIVACY_AS_RISK_OR_TRADEOFF: privacy discussed as a risk, trade-off, public concern or adoption barrier. OTHER: anything else (label it).

For each statement give: "type", "status" (considered | endorsed | tested | operational | rejected | unclear — endorsed only if the
document attributes the position to the competent decision body as a decision/commitment; drafts, options, consultations, experiments are
considered/tested), "basis" (policy | architectural | cryptographic | legal | n/d), "actor" (CB | PSP | public_authority | user | n/d),
"page" (integer PDF page index from the delimiters), "quote" (verbatim, <= 40 words), "label" (<= 8 words, for OTHER or nuance).
Return ONLY a JSON array of objects (empty array if none). Do not add commentary."""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--texts", required=True); ap.add_argument("--frame", required=True); ap.add_argument("--provider", default="anthropic")
    ap.add_argument("--model", required=True); ap.add_argument("--max-tokens", type=int, default=16000); ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--sealed-out", required=True); ap.add_argument("--aggregate-out", required=True); ap.add_argument("--only", default="")
    a = ap.parse_args()
    ROOT_REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    if os.path.abspath(a.sealed_out).startswith(ROOT_REPO + os.sep): raise SystemExit("refusing: --sealed-out must be outside the repository (EXPOSURE_LEDGER)")
    frame = {r["project"]: r for r in csv.DictReader(open(a.frame, encoding="utf-8"))}
    projects = sorted(p for p in os.listdir(a.texts) if os.path.exists(os.path.join(a.texts, p, "DOCS.csv")))
    if a.only: projects = [p for p in projects if p in a.only.split(",")]
    jobs = []
    for p in projects:
        for x in csv.DictReader(open(os.path.join(a.texts, p, "DOCS.csv"), encoding="utf-8")):
            f = x["file"] if os.path.exists(x["file"]) else os.path.join(a.texts, p, "texts", os.path.basename(x["file"]))
            jobs.append((p, x, f))
    os.makedirs(os.path.dirname(a.sealed_out), exist_ok=True); reqdir = os.path.join(os.path.dirname(a.sealed_out), "posture_requests"); os.makedirs(reqdir, exist_ok=True)
    done = {}
    if os.path.exists(a.sealed_out):
        for line in open(a.sealed_out, encoding="utf-8"): r = json.loads(line); done[r["doc_id"]] = r
    cl = Client(a.provider, a.model, a.max_tokens); lock = threading.Lock()

    def run(job):
        p, x, f = job
        if x["doc_id"] in done: return
        text = open(f, encoding="utf-8", errors="replace").read()
        user = f"PROJECT {p}, DOCUMENT {x['doc']} [{x['doc_id']}], year {x['year']}, kind {x['kind']}, lang {x['lang']}\n\n{text}"
        req = archive(reqdir, f"{x['doc_id']}.user", user)
        try:
            out, meta = cl.call(SYSTEM, user); rows = parse_array(out)
            rows = [r for r in rows if isinstance(r, dict)]
            rec = {"project": p, "doc_id": x["doc_id"], "doc": x["doc"], "kind": x["kind"], "year": x["year"], "core": x["core"], "state": "ok", "statements": rows, "meta": meta, "request_sha256": req["sha256"]}
        except Exception as e: rec = {"project": p, "doc_id": x["doc_id"], "doc": x["doc"], "kind": x["kind"], "year": x["year"], "core": x["core"], "state": f"failed:{e!r}"}
        rec["utc"] = dt.datetime.now(dt.timezone.utc).isoformat()
        with lock:
            with open(a.sealed_out, "a", encoding="utf-8") as fh: fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
            done[x["doc_id"]] = rec; print(f"[posture] {p} doc {x['doc']}: {rec['state'].split(':')[0]}", flush=True)  # statement counts not logged (sealed)

    with ThreadPoolExecutor(max_workers=a.workers) as ex: list(ex.map(run, jobs))
    # aggregate: no project names
    by_type = collections.Counter(); by_type_status = collections.Counter(); by_type_kind = collections.Counter(); by_type_basis = collections.Counter()
    proj_type = collections.defaultdict(set); proj_type_status = collections.defaultdict(set); states = collections.Counter(); n_docs = 0
    for r in done.values():
        states[r["state"].split(":")[0]] += 1
        if r["state"] != "ok": continue
        n_docs += 1
        for s in r["statements"]:
            t = s.get("type", "OTHER"); t = t if t in TYPES else "OTHER"; st = s.get("status", "unclear")
            by_type[t] += 1; by_type_status[f"{t}|{st}"] += 1; by_type_kind[f"{t}|{r['kind']}"] += 1; by_type_basis[f"{t}|{s.get('basis','n/d')}"] += 1
            proj_type[t].add(r["project"]); proj_type_status[f"{t}|{st}"].add(r["project"])
    retail = {p for p, r in frame.items() if r["retail_candidate"] == "True"}
    agg = {"as_of": dt.datetime.now(dt.timezone.utc).isoformat(), "model": a.model, "system_sha256": sha(SYSTEM), "n_documents": n_docs, "states": dict(states),
           "n_projects_in_survey": len({r["project"] for r in done.values()}), "n_retail_frame": len(retail),
           "statements_by_type": dict(by_type), "statements_by_type_status": dict(by_type_status), "statements_by_type_doc_kind": dict(by_type_kind), "statements_by_type_basis": dict(by_type_basis),
           "projects_with_type": {t: len(v) for t, v in proj_type.items()}, "retail_projects_with_type": {t: len(v & retail) for t, v in proj_type.items()},
           "retail_projects_with_type_status": {k: len(v & retail) for k, v in proj_type_status.items()},
           "sealed_file_sha256": hashlib.sha256(open(a.sealed_out, "rb").read()).hexdigest(), "note": "Per-document statements sealed off-repo; aggregate names no project."}
    os.makedirs(os.path.dirname(a.aggregate_out), exist_ok=True); json.dump(agg, open(a.aggregate_out, "w"), indent=1); print(json.dumps({k: agg[k] for k in ("n_documents", "states", "statements_by_type", "retail_projects_with_type")}, indent=1))


if __name__ == "__main__": main()
