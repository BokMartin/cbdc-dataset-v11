#!/usr/bin/env python3
"""Observations of prompt v12.2 -> project cells (the claim-to-cell reducer of ADR-013 P5; contract v12 §3 to §7, ADR-012).

One model's accepted responses for one project go in; out come the eight privacy cells F1, F2, F3, F4, F7, F8, F9, F10 in the
shape that scripts/derive_index.py and scripts/derive.py read, plus the tables beside them. No model call, no network.

Order (audit A4c answer 3, "reducer order", in the part that needs no further author decision):
 1. Requests. Only a request whose response passed scripts/extraction/v122.py check() (state ok or
    ok_with_validation_problems) is used; a failed one supplies nothing (prompt §6). Search closure of the project is true
    only when every owned page of every planned request of its documents is covered by a used request; a gap is listed.
 2. Observations -> candidates, per cell. A candidate needs kind assertion (or, for F3 in an official document, a
    legal_reference), a retail or both scope, and a document layer that may establish a cell:
      official                    establishes;
      inclined_joint_retail       LEANING only, used only when no official candidate exists (ADR-012 D5; derive_index scores
                                  it only in the with_leaning variant);
      staff_research              corroborates, never establishes (contract §7.1): kept in the ledger;
      wholesale_context, scope wholesale  never a retail value (fixture 2 of A4c);
      companion_legal             F3 legal references go to the separate statutory F3 table and never to the maker's cell (P2);
      unknown layer or scope      withheld, with the reason.
 3. Evidence state of a candidate (contract §3, rule F): a decisive qualifier listed in `missing` -> partial; basis n/d for
    F1, F2, F4, F9 -> partial; a route-D observation flagged translation_uncertain -> partial with a pending source check
    (ADR-013 P4); otherwise documented. A protective value of F1, F2, F4 or F9 resting on basis policy is a pledge: it is kept
    and shown, but sets no value in either view (contract §6; ADR-013 §3).
 4. Selection: decision rejected or superseded never sets a value. The candidates of the highest status class win
    (endorsed or operational, then considered or tested, then unclear); among them the newest document wins (ADR-012 D4,
    contract §7.2). Equal class, equal date, different value -> conflict (both kept; the authors decide, §7.4). F3 routes
    of the winning class combine: via_PSP and via_CB give via_both (rule F).
 5. No value: an addressed cell without a value is unknown with reason privacy_unspecified (value unspecified),
    provisional_only (undecided) or policy_only; a cell not addressed is unknown with never_addressed when the search is
    closed, search_incomplete when it is not. F3 none_stated is computed only from a closed search with no route
    (derivation inferred, rule SEARCH_F3). F4 with an adopted exclusion of offline (details.offline_mode
    explicitly_excluded) is n.a., not a scored no (A4c answer 3: the convention is frozen before index construction).
 6. F2 inference (contract §7.3), only when no explicit F2 value exists: premises mapping, routine_record and join_key with
    the same participant, scope and design label; derivation inferred; its status is the weakest of the premises.
Not here (later steps, or author decisions): links across documents by references (P3; the reference list is kept),
supersession across differently named designs, the three-model combination outside the core (combine_models() below gives
the unanimity rule of ADR-012 D2), the PET taxonomy join.
"""
import json, re

MAKER_CELLS = ("F1", "F2", "F3", "F4", "F7", "F8", "F9", "F10")
NEEDS_BASIS = ("F1", "F2", "F4", "F9")
PROTECTIVE = {"F1": "no", "F2": "no", "F4": "yes", "F9": "no"}
F3_ROUTE = {"via_PSP": {"psp"}, "via_CB": {"cb"}, "via_both": {"psp", "cb"}}
USED = ("ok", "ok_with_validation_problems")


def _date(s):
    m = re.findall(r"\d+", str(s or "")); return tuple(int(x) for x in m[:3]) if m else (0,)


def _class(o):
    if o["decision_status"] == "endorsed" or o["implementation_status"] == "operational": return 2
    if o["decision_status"] == "considered" or o["implementation_status"] == "tested": return 1
    return 0


def _first(o):
    s = next(x for x in o["evidence"] if x["role"] == "proposition")["segments"][0]; return s


def search_state(project_docs, requests):
    """(closed, gaps): every owned page of every planned request of the project's documents is covered by a used request."""
    gaps = []
    for d in project_docs:
        planned = {p for r in requests if r["doc_key"] == d["doc_key"] for p in r["owned_pages"]}
        used = {p for r in requests if r["doc_key"] == d["doc_key"] and r["state"] in USED for p in r["owned_pages"]}
        if not planned: gaps.append(f"{d['doc_key']}: no request"); continue
        if planned - used: gaps.append(f"{d['doc_key']}: pages {sorted(planned - used)} not covered by a used request")
    return not gaps, gaps


def _evidence_state(o, doc):
    probs = []
    if o["missing"]: probs.append("missing " + ", ".join(o["missing"]))
    if o["cell"] in NEEDS_BASIS and o["basis"] == "n/d": probs.append("basis not stated")
    if doc["text_route"] == "D" and "translation_uncertain" in o["flags"]: probs.append("route D, translation_uncertain: source check pending")
    return ("partial" if probs else "documented"), probs


def _cell(c, docs, extra):
    o, d = c["obs"], docs[c["obs"]["_doc"]]; s = _first(o)
    out = {"value": c["value"], "evidence_state": c["state"], "decision_status": o["decision_status"], "implementation_status": o["implementation_status"],
           "basis": o["basis"], "layer": "official" if d["layer"] == "official" else d["layer"], "retail_or_wholesale": o["retail_or_wholesale"],
           "derivation": "explicit", "conflict": "", "superseded": "", "unknown_reason": "", "text_route": d["text_route"], "leaning": "",
           "document_id": d["doc_key"], "page_index": s["page_index"], "block_id": s["block_id"], "quote": s["quote"], "claim_ids": [o["_id"]],
           "counter_evidence": [], "problems": c["problems"], "provenance": o["_model"]}
    out.update(extra); return out


def _unknown(reason, ledger_ids=()):
    return {"value": "", "evidence_state": "unknown", "decision_status": "", "implementation_status": "", "basis": "", "layer": "", "derivation": "n.a.",
            "conflict": "", "superseded": "", "unknown_reason": reason, "claim_ids": list(ledger_ids), "counter_evidence": [], "leaning": ""}


def observations(requests, docs, drop_route_d=False):
    """Used observations with ids, deduplicated by source occurrence (document, cell, value, first located segment)."""
    seen, out = set(), []
    for r in requests:
        if r["state"] not in USED: continue
        d = docs[r["doc_key"]]
        if drop_route_d and d["text_route"] == "D": continue
        for o in r["observations"]:
            s = _first(o); key = (r["doc_key"], o["cell"], o["asserted_value"], s["page_index"], s["block_id"], s["quote"])
            if key in seen: continue
            seen.add(key); out.append(dict(o, _id=f"{r['request_id']}#{o['claim_no']}", _doc=r["doc_key"], _model=r.get("model", "")))
    return out


def reduce_project(project, docs, requests, drop_route_d=False):
    """docs: {doc_key: {doc_key, project, layer, text_route, issue_date}}; requests: [{request_id, doc_key, owned_pages, state,
    observations, model}] for one model. Returns cells, tables, search closure and the ledger of every decision taken."""
    pdocs = [d for d in docs.values() if d["project"] == project]
    closed, gaps = search_state(pdocs, [r for r in requests if docs[r["doc_key"]]["project"] == project])
    obs = [o for o in observations([r for r in requests if docs[r["doc_key"]]["project"] == project], docs, drop_route_d)]
    ledger, cand, addressed, premises, statutory, pet, descriptive, wholesale = [], {}, {}, [], [], [], [], []
    for o in obs:
        d = docs[o["_doc"]]; cell = o["cell"]; note = lambda why: ledger.append({"claim_id": o["_id"], "cell": cell, "value": o["asserted_value"], "use": why})
        if cell == "PET":
            (wholesale if (d["layer"] == "wholesale_context" or o["retail_or_wholesale"] == "wholesale") else pet).append(
                {"claim_id": o["_id"], "code": o["asserted_value"], "technique_text": o["details"].get("technique_text"), "privacy_function": o["details"].get("privacy_function"),
                 "decision_status": o["decision_status"], "implementation_status": o["implementation_status"], "scope": o["retail_or_wholesale"],
                 "design_label": o["design_label"], "layer": d["layer"], "document_id": o["_doc"]})
            note("PET profile" if pet and pet[-1]["claim_id"] == o["_id"] else "wholesale PET context"); continue
        if cell not in MAKER_CELLS:
            descriptive.append({"claim_id": o["_id"], "record": cell, "value": o["asserted_value"], "kind": o["kind"], "decision_status": o["decision_status"],
                                "layer": d["layer"], "flags": o["flags"], "document_id": o["_doc"]}); note("descriptive record"); continue
        if d["layer"] == "companion_legal":
            if cell == "F3" and o["kind"] == "legal_reference":
                statutory.append({"claim_id": o["_id"], "value": o["asserted_value"], "legal_state": o["legal_state"], "referenced_law_state": o["referenced_law_state"], "document_id": o["_doc"]})
                note("statutory F3 column (companion; never the maker's cell, ADR-013 P2)")
            else: note("companion document: not a maker cell")
            continue
        if o["kind"] == "premise":
            if d["layer"] == "official" and o["retail_or_wholesale"] in ("retail", "both"): premises.append(o); note("F2 premise")
            else: note("F2 premise outside the official retail layer: not used")
            continue
        if o["kind"] == "context": note("context only"); continue
        if o["kind"] == "legal_reference" and cell != "F3": note("legal reference: descriptive"); continue
        if o["kind"] not in ("assertion", "legal_reference"): note(f"{o['kind']}: not a cell value"); continue
        if d["layer"] in ("wholesale_context",) or o["retail_or_wholesale"] == "wholesale": note("wholesale: never a retail value"); continue
        if o["retail_or_wholesale"] == "unknown": note("scope unknown: withheld"); continue
        if d["layer"] == "staff_research": note("staff research: corroborates, never establishes"); continue
        if d["layer"] not in ("official", "inclined_joint_retail"): note(f"layer {d['layer']}: cannot establish"); continue
        if o["decision_status"] in ("rejected", "superseded"): note(f"{o['decision_status']}: history only"); continue
        v = o["asserted_value"]
        if v in ("unspecified", "undecided"): addressed.setdefault(cell, []).append((o, "privacy_unspecified" if v == "unspecified" else "provisional_only")); note("addressed, no value"); continue
        if PROTECTIVE.get(cell) == v and o["basis"] == "policy":
            addressed.setdefault(cell, []).append((o, "policy_only")); note("policy pledge: sets no value (contract §6)"); continue
        state, probs = _evidence_state(o, d)
        cand.setdefault(cell, []).append({"obs": o, "value": v, "state": state, "problems": probs, "class": _class(o),
                                         "date": max(_date(d["issue_date"]), _date(o["event_date"])), "leaning": d["layer"] == "inclined_joint_retail"})
        note("candidate" + (" (LEANING)" if d["layer"] == "inclined_joint_retail" else ""))
    cells = {}
    for f in MAKER_CELLS:
        cs = cand.get(f, []); official = [c for c in cs if not c["leaning"]]; pool = official or cs
        if f == "F2" and not pool:
            inf = infer_f2(premises, docs)
            if inf: cells[f] = inf; continue
        if not pool:
            a = addressed.get(f, [])
            if a: cells[f] = _unknown(a[-1][1], [o["_id"] for o, _ in a]); continue
            if f == "F3" and closed:
                cells[f] = dict(_unknown(""), value="none_stated", evidence_state="documented", derivation="inferred", unknown_reason="", rule="SEARCH_F3", layer="official"); continue
            cells[f] = _unknown("never_addressed" if closed else "search_incomplete"); continue
        top = max(c["class"] for c in pool); best = [c for c in pool if c["class"] == top]
        newest = max(c["date"] for c in best); win = [c for c in best if c["date"] == newest]
        others = [c["obs"]["_id"] for c in pool if c not in win]
        if f == "F3":
            routes = set().union(*(F3_ROUTE[c["value"]] for c in win))
            value = "via_both" if routes == {"psp", "cb"} else ("via_PSP" if routes == {"psp"} else "via_CB")
            cell = _cell(win[0], docs, {"value": value.lower(), "claim_ids": [c["obs"]["_id"] for c in win], "counter_evidence": others})
            if any(c["state"] == "partial" for c in win): cell["evidence_state"] = "partial"
        elif len({c["value"] for c in win}) > 1:
            cell = _cell(win[0], docs, {"value": "", "evidence_state": "conflict", "conflict": "true", "claim_ids": [c["obs"]["_id"] for c in win], "counter_evidence": others,
                                       "unknown_reason": "conflict between claims of equal standing: the authors decide (contract §7.4)"})
        else:
            w = sorted(win, key=lambda c: c["state"] != "documented")[0]
            cell = _cell(w, docs, {"claim_ids": [c["obs"]["_id"] for c in win], "counter_evidence": others})
            if f == "F4" and w["obs"]["details"].get("offline_mode") == "explicitly_excluded":
                cell.update(value="", evidence_state="n.a.", unknown_reason="offline explicitly excluded for this horizon (n.a., not a scored no)")
        if not official: cell["leaning"] = "true"
        cells[f] = cell
    return {"project": project, "cells": cells, "statutory_F3": statutory, "pet": pet, "pet_wholesale_context": wholesale, "descriptive": descriptive,
            "search_closed": closed, "gaps": gaps, "ledger": ledger}


def infer_f2(premises, docs):
    """Contract §7.3: mapping + routine_record + join_key of the same participant, scope and design label -> F2 yes (inferred)."""
    groups = {}
    for o in premises: groups.setdefault((o["reference_participant"], o["transaction_scope"], o["design_label"]), {}).setdefault(o["asserted_value"], o)
    for g in groups.values():
        if set(g) == {"mapping", "routine_record", "join_key"}:
            ps = list(g.values()); weakest = min(ps, key=_class)
            states = [_evidence_state(o, docs[o["_doc"]])[0] for o in ps]
            s = _first(weakest)
            return {"value": "yes", "evidence_state": "documented" if all(x == "documented" for x in states) else "partial",
                    "decision_status": weakest["decision_status"], "implementation_status": weakest["implementation_status"], "basis": "architectural",
                    "layer": "official", "retail_or_wholesale": weakest["retail_or_wholesale"], "derivation": "inferred", "rule": "contract §7.3 F2",
                    "premises": [o["_id"] for o in ps], "claim_ids": [o["_id"] for o in ps], "conflict": "", "superseded": "", "unknown_reason": "",
                    "text_route": docs[weakest["_doc"]]["text_route"], "leaning": "", "document_id": weakest["_doc"], "page_index": s["page_index"],
                    "block_id": s["block_id"], "quote": s["quote"], "counter_evidence": []}
    return None


def combine_models(by_model):
    """ADR-012 D2, outside the core: a cell has a value only if every model gives the same value, documented and located;
    otherwise it goes to the authors. by_model: {model: cells}."""
    out = {}
    for f in MAKER_CELLS:
        cs = [m.get(f) or {} for m in by_model.values()]
        vals = {c.get("value") for c in cs}
        ok = len(vals) == 1 and "" not in vals and None not in vals and all(c.get("evidence_state") == "documented" and c.get("quote") is not None for c in cs)
        out[f] = {"value": cs[0]["value"] if ok else "", "unanimous": ok, "to_authors": not ok, "by_model": {k: (m.get(f) or {}).get("value", "") for k, m in by_model.items()}}
    return out


def requests_from_run(attempts_path, requests_path, model=""):
    """The requests of a job with the state of their attempt, read back from a runner work folder: the completed attempt,
    else the last one that returned text (re-checked, so a response that failed the check shows as failed), else not_run."""
    import v122
    reqs = {json.loads(l)["request_key"]: json.loads(l) for l in open(requests_path, encoding="utf-8") if l.strip()}
    done, last = {}, {}
    for l in open(attempts_path, encoding="utf-8"):
        a = json.loads(l)
        if a["complete"]: done[a["request_key"]] = a
        if a.get("text"): last[a["request_key"]] = a
    out = []
    for k, r in reqs.items():
        h = v122.header_of(r["user"]); a = done.get(k) or last.get(k)
        res = v122.check(a["text"], r["user"]) if a else {"state": "not_run", "observations": [], "problems": [], "rejected": []}
        if a and not a["complete"] and res["state"] != "failed":
            res = dict(res, state="failed", problems=res["problems"] + [f"attempt not complete: {a.get('parse_error') or a.get('stop_reason')}"])
        out.append({"request_id": h["request_id"], "doc_key": h["doc_key"], "owned_pages": h["owned_pages"], "state": res["state"],
                    "observations": res["observations"] if res["state"] != "failed" else [], "problems": res["problems"], "rejected": res["rejected"],
                    "model": a["model_returned"] if a else model})
    return out


def docs_from_manifest(manifest, header_extra=None):
    """{doc_key: {doc_key, project, layer, text_route, issue_date}} from the unit manifest; the layer is the one the
    extraction header was given (scripts/pipeline/build_jobs.py: --header-extra, else official for stratum evidence)."""
    import csv
    extra = {r["doc_key"]: r for r in csv.DictReader(open(header_extra, encoding="utf-8"))} if header_extra else {}
    out = {}
    for m in csv.DictReader(open(manifest, encoding="utf-8")):
        lay = (extra.get(m["doc_key"]) or {}).get("layer") or ("official" if m.get("stratum", "evidence") == "evidence" else "unknown")
        out[m["doc_key"]] = {"doc_key": m["doc_key"], "project": m["project"], "layer": lay, "text_route": m["route"], "issue_date": m["year"]}
    return out


def main(argv=None):
    """Read a runner work folder back into project cells (one model). The output holds quotes of the sources, so write it
    OUTSIDE the repository."""
    import argparse, glob, os, sys
    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    ap = argparse.ArgumentParser()
    ap.add_argument("--job", required=True, help="job folder (REQUESTS.jsonl)"); ap.add_argument("--run-dir", required=True, help="runner work folder of one run (ATTEMPTS.jsonl)")
    ap.add_argument("--out", required=True); ap.add_argument("--header-extra"); ap.add_argument("--drop-route-d", action="store_true")
    a = ap.parse_args(argv)
    if os.path.abspath(a.out).startswith(root + os.sep): raise SystemExit("--out is inside the repository; the cells carry source quotes")
    docs = docs_from_manifest(sorted(glob.glob(os.path.join(root, "data", "units", "UNITS_MANIFEST_*.csv")))[-1], a.header_extra)
    reqs = requests_from_run(os.path.join(a.run_dir, "ATTEMPTS.jsonl"), os.path.join(a.job, "REQUESTS.jsonl"))
    projects = sorted({docs[r["doc_key"]]["project"] for r in reqs})
    # search closure counts every document of the project in the manifest: a pilot on two documents never closes it
    out = {"requests": [{k: r[k] for k in ("request_id", "state", "problems", "rejected")} | {"observations": len(r["observations"])} for r in reqs],
           "projects": {p: reduce_project(p, docs, reqs, a.drop_route_d) for p in projects}}
    json.dump(out, open(a.out, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    for p, r in out["projects"].items():
        print(p, "search closed" if r["search_closed"] else f"search open ({len(r['gaps'])} gaps)",
              " ".join(f"{f}={c.get('value') or c.get('evidence_state')}" for f, c in r["cells"].items()))
    print(sum(r["state"] == "failed" for r in reqs), "of", len(reqs), "requests failed the check ->", a.out, file=sys.stderr)


if __name__ == "__main__":
    sys_path = __import__("os").path.dirname(__import__("os").path.abspath(__file__)); __import__("sys").path.insert(0, sys_path)
    main()
