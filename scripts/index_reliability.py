#!/usr/bin/env python3
"""B3, coding reliability of the index cells (PROPOSAL, prepared before any data; ADR-009, spec §10).

Input: one CSV per blind coder, a copy of data/index/CODER_TEMPLATE_2026-11-22.csv (columns in FIELDS below; the
template of 21 Nov lacked the fields rule C reads and was replaced, V6 of the 22 Nov check).
Locked before either coder sees model output (contract §10).

Output: Krippendorff's alpha (nominal) per cell, on three categories (yes / no / undetermined) and on the pairs where
both coders set a value; and the merged cells for derive_index.py: agreement -> the shared value, with the lower of
the two rungs; disagreement -> value kept from neither, flagged coder_disagreement, which widens the interval.
The gate of contract §12 (alpha >= .80 on central constructs) is applied by the reader of the output, not here.

usage: index_reliability.py --a coder_MB.csv --b coder_DS.csv --out RELIABILITY.json
"""
import argparse
import csv
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "units"))
from score_agreement import alpha  # noqa: E402

sys.path.insert(0, os.path.dirname(__file__))
from derive_index import CELLS, rung  # noqa: E402

VALUES = {"yes", "no", "undetermined", "via_psp", "via_cb", "via_both", "none_stated"}  # F3 is categorical
# Coder template of 22 Nov 2026 (V6 of the 22 Nov check, ADR-012 §3): every field rule C needs travels with the cell.
FIELDS = ["project_id", "cell", "value", "decision_status", "implementation_status", "evidence_state", "basis",
          "text_route", "derivation", "conflict", "document_id", "quote", "page_index", "note"]
ENUMS = {  # contract v12 §3 to §5 and §9; blank allowed only where the value is undetermined
    "decision_status": {"", "considered", "endorsed", "rejected", "superseded", "unclear"},
    "implementation_status": {"", "untested_or_unreported", "tested", "operational", "unclear"},
    "evidence_state": {"", "documented", "partial", "unknown", "conflict", "n.a."},
    "basis": {"", "policy", "architectural", "cryptographic"},
    "text_route": {"", "A", "B", "C", "D"},
    "derivation": {"", "explicit", "inferred", "n.a."},
    "conflict": {"", "true", "false"},
}
REQUIRED_WITH_VALUE = ("evidence_state", "text_route", "derivation", "document_id", "quote")
BASIS_REQUIRED = ("F1", "F2", "F4", "F9")  # contract v12 §3: basis mandatory for these cells
ROUTE_ORDER = "ABCD"  # A strongest, D weakest (contract §9)
EVIDENCE_ORDER = ("documented", "partial", "conflict", "unknown", "n.a.", "")


def _norm(field, v):
    v = (v or "").strip()
    if field == "text_route":
        return v.upper()
    if field == "conflict":
        return {"yes": "true", "1": "true", "y": "true", "no": "false", "0": "false", "n": "false"}.get(v.lower(), v.lower())
    return v if field in ("document_id", "quote", "page_index", "note") else v.lower()


def read(path, cells=CELLS):
    """One coder file. Stops the run on anything it cannot read unambiguously, so nothing is dropped silently:
    an empty key, a cell outside the grid, a duplicate (project, cell), a value or field outside its list, a set value
    without evidence state, text route, derivation, document and quote, a set F1/F2/F4/F9 without basis, and a value
    set on evidence that says it is unknown or not applicable. Files in the old seven-column format fail here."""
    out, bad = {}, []
    with open(path, newline="", encoding="utf-8") as fh:
        rd = csv.DictReader(fh)
        missing = [f for f in FIELDS if f not in (rd.fieldnames or [])]
        if missing:
            raise ValueError(f"{path}: columns missing {missing} (coder template of 22 Nov 2026 required)")
        for i, r in enumerate(rd, start=2):
            key = (r["project_id"].strip(), r["cell"].strip().upper())
            if not key[0] or not key[1]:
                bad.append(f"row {i}: empty project_id or cell")
                continue
            if key[1] not in cells:
                bad.append(f"row {i}: cell {key[1]!r} not in the grid")
            v = (r.get("value") or "").strip().lower() or "undetermined"
            if v not in VALUES:
                bad.append(f"row {i}: value {v!r}")
            rec = {f: _norm(f, r.get(f)) for f in FIELDS}
            rec.update(project_id=key[0], cell=key[1], value=v)
            for f, allowed in ENUMS.items():
                if rec[f] not in allowed:
                    bad.append(f"row {i}: {f} {rec[f]!r}")
            if v != "undetermined":
                for f in REQUIRED_WITH_VALUE:
                    if not rec[f]:
                        bad.append(f"row {i}: value {v!r} set without {f}")
                if key[1] in BASIS_REQUIRED and not rec["basis"]:
                    bad.append(f"row {i}: value {v!r} set without basis (mandatory for {key[1]})")
                if rec["evidence_state"] in ("unknown", "n.a."):
                    bad.append(f"row {i}: value {v!r} set on evidence_state {rec['evidence_state']!r}")
            if key in out:
                bad.append(f"row {i}: duplicate {key}")
            out[key] = rec
    if bad:
        raise ValueError(f"{path}: " + "; ".join(bad))
    return out


def reliability(a, b, cells=CELLS):
    """alpha per cell. Keys present in only one file are reported, never paired with a blank (merge() keeps them as
    undetermined cells flagged missing_coder). Also listed for the authors: F1 = no set on a policy basis (contract
    v12 §6 says a policy promise never sets F1 = no; not enforced until the contract is adopted) and, among cells
    where the coders agree on the value, disagreements on the fields that rule C reads."""
    only = sorted(set(a) ^ set(b))
    res = {"keys_in_one_file_only": [list(k) for k in only]}
    for c in cells:
        pairs3 = [(a[k]["value"], b[k]["value"]) for k in a if k in b and k[1] == c]
        pairs2 = [(x, y) for x, y in pairs3 if x != "undetermined" and y != "undetermined"]
        a3, a2 = alpha(pairs3), alpha(pairs2)
        res[c] = {"n": len(pairs3), "agreement": round(sum(x == y for x, y in pairs3) / len(pairs3), 3) if pairs3 else None,
                  "alpha_3cat": None if a3 is None else round(a3, 3),
                  "n_both_valued": len(pairs2), "alpha_valued": None if a2 is None else round(a2, 3)}
    res["f1_no_on_policy_basis"] = sorted({k[0] for f in (a, b) for k, r in f.items()
                                           if k[1] == "F1" and r["value"] == "no" and r.get("basis") == "policy"})
    res["field_disagreements_on_agreed_values"] = {
        fld: sorted(f"{k[0]}:{k[1]}" for k in set(a) & set(b) if a[k]["value"] == b[k]["value"] != "undetermined"
                    and a[k].get(fld, "") != b[k].get(fld, ""))
        for fld in ("decision_status", "implementation_status", "evidence_state", "basis", "text_route", "derivation", "conflict")}
    return res


def _weaker(field, x, y):
    """The more conservative of two coders' entries for a field rule C or a sensitivity variant reads."""
    if field == "evidence_state":
        rank = {e: i for i, e in enumerate(EVIDENCE_ORDER)}  # later in the list = weaker
        return max(x, y, key=lambda e: rank.get(e, len(EVIDENCE_ORDER)))
    if field == "text_route":
        return max(x, y, key=lambda r: ROUTE_ORDER.index(r) if r in ROUTE_ORDER else 9)
    if field == "derivation":
        return "inferred" if "inferred" in (x, y) else (x or y)
    if field == "conflict":
        return "true" if "true" in (x, y) else (x or y)
    if field == "basis":
        return x if x == y else ("policy" if "policy" in (x, y) else "")  # differing non-policy bases: none
    return x if x == y else ""


def merge(a, b):
    """Cells for derive_index.py, by project. Every key of either file is kept. Both original records (with their
    quotes and documents) travel in `coded`. Agreement on the value gives the shared value, the lower of the two
    rungs, and for evidence_state, basis, text_route, derivation and conflict the more conservative entry, so that
    rule C and the route-D and inferred variants see what the coders recorded (V6; before 22 Nov the merge set
    evidence_state = documented and dropped the other fields). Disagreement gives an undetermined cell flagged
    coder_disagreement; a key in one file only gives an undetermined cell flagged missing_coder."""
    merged = {}
    for k in sorted(set(a) | set(b)):
        p, c = k
        x, y = a.get(k), b.get(k)
        if x is None or y is None:
            cell = {"value": "undetermined", "missing_coder": "true", "coded": {"a": x, "b": y}}
        elif x["value"] == y["value"] and x["value"] != "undetermined":
            lower = x if rung(x, c) <= rung(y, c) else y
            cell = {"value": x["value"], "decision_status": lower["decision_status"],
                    "implementation_status": lower["implementation_status"]}
            for f in ("evidence_state", "basis", "text_route", "derivation", "conflict"):
                cell[f] = _weaker(f, x.get(f, ""), y.get(f, ""))
            cell["coded"] = {"a": x, "b": y}
        elif x["value"] == y["value"]:
            cell = {"value": x["value"], "coded": {"a": x, "b": y}}
        else:
            cell = {"value": "undetermined", "coder_disagreement": "true", "values_coded": [x["value"], y["value"]],
                    "coded": {"a": x, "b": y}}
        merged.setdefault(p, {})[c] = cell
    return merged


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--a", required=True)
    ap.add_argument("--b", required=True)
    ap.add_argument("--out", required=True)
    o = ap.parse_args()
    a, b = read(o.a), read(o.b)
    json.dump({"reliability": reliability(a, b), "merged_cells": merge(a, b)}, open(o.out, "w"), indent=1)
    print("written", o.out)


if __name__ == "__main__":
    main()
