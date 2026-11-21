#!/usr/bin/env python3
"""B3, coding reliability of the index cells (PROPOSAL, prepared before any data; ADR-009, spec §10).

Input: one CSV per blind coder (format in docs/PRIVACY_INDEX_SPEC_DRAFT_2026-11-21.md §10.3), columns
project_id, cell, value (yes / no / undetermined), decision_status, implementation_status, quote, page_index.
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
from derive_index import CORE, rung  # noqa: E402

VALUES = {"yes", "no", "undetermined", "via_psp", "via_cb", "via_both", "none_stated"}  # F3 is categorical
FIELDS = ["project_id", "cell", "value", "decision_status", "implementation_status", "quote", "page_index"]


def read(path):
    """Duplicate (project, cell) rows and values outside the declared set stop the run: nothing is dropped silently."""
    out, bad = {}, []
    with open(path, newline="", encoding="utf-8") as fh:
        for i, r in enumerate(csv.DictReader(fh), start=2):
            key = (r["project_id"].strip(), r["cell"].strip().upper())
            v = (r.get("value") or "").strip().lower() or "undetermined"
            if v not in VALUES:
                bad.append(f"row {i}: value {v!r}")
            if key in out:
                bad.append(f"row {i}: duplicate {key}")
            out[key] = {**{k: (r.get(k) or "").strip() for k in FIELDS}, "value": v}
    if bad:
        raise ValueError(f"{path}: " + "; ".join(bad))
    return out


def reliability(a, b, cells=CORE):
    """alpha per cell. Keys present in only one file are reported, never paired with a blank."""
    only = sorted(set(a) ^ set(b))
    res = {"keys_in_one_file_only": [list(k) for k in only]}
    for c in cells:
        pairs3 = [(a[k]["value"], b[k]["value"]) for k in a if k in b and k[1] == c]
        pairs2 = [(x, y) for x, y in pairs3 if x != "undetermined" and y != "undetermined"]
        a3, a2 = alpha(pairs3), alpha(pairs2)
        res[c] = {"n": len(pairs3), "agreement": round(sum(x == y for x, y in pairs3) / len(pairs3), 3) if pairs3 else None,
                  "alpha_3cat": None if a3 is None else round(a3, 3),
                  "n_both_valued": len(pairs2), "alpha_valued": None if a2 is None else round(a2, 3)}
    return res


def merge(a, b):
    """Cells for derive_index.py, by project."""
    merged = {}
    for k in sorted(set(a) & set(b)):
        p, c = k
        x, y = a[k], b[k]
        if x["value"] == y["value"] and x["value"] != "undetermined":
            lower = x if rung(x, c) <= rung(y, c) else y
            cell = {"value": x["value"], "evidence_state": "documented", "decision_status": lower["decision_status"],
                    "implementation_status": lower["implementation_status"]}
        elif x["value"] == y["value"]:
            cell = {"value": x["value"]}
        else:
            cell = {"value": "undetermined", "coder_disagreement": "true", "values_coded": [x["value"], y["value"]]}
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
