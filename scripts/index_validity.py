#!/usr/bin/env python3
"""B2, validity checks of the privacy index (PROPOSAL, prepared before any data; ADR-009, spec §10).

1. Known cases: cells whose value the authors fix in advance from an official document
   (data/index/KNOWN_CASES_DRAFT_2026-11-21.csv). The index must reproduce them; a miss is reported, never tuned away.
2. Convergent and discriminant comparison with external measures (data/index/EXTERNAL_MEASURES_DRAFT_2026-11-21.csv):
   Spearman rho between the midpoint of the stated-design interval and each measure, only for projects whose
   interval is at most `max_width` wide, with the expected sign written before the data exist. This is a validity
   check of the instrument, reported as such; it is not an association claim and uses no causal language.

usage: index_validity.py --cells MERGED.json --known KNOWN.csv --external EXTERNAL.csv --measures MEASURES.csv --out VALIDITY.json
"""
import argparse
import csv
import json
import os
import random
import sys

sys.path.insert(0, os.path.dirname(__file__))
from derive_index import axis1, rung  # noqa: E402


def check_known_cases(projects, known):
    """known: rows with project_id, cell, expected_value, expected_min_rung (optional). Rows without an expected value
    are listed as 'not_fixed' (the authors have not filled them)."""
    out = []
    for k in known:
        exp = (k.get("expected_value") or "").strip().lower()
        cell = projects.get(k["project_id"], {}).get(k["cell"])
        got = (cell or {}).get("value", "undetermined")
        if not exp:
            status = "not_fixed"
        elif got not in ("yes", "no"):
            status = "undetermined"
        elif got != exp:
            status = "miss"
        else:
            mr = (k.get("expected_min_rung") or "").strip()
            status = "hit" if not mr or rung(cell) >= int(mr) else "hit_value_low_rung"
        out.append({"case_id": k.get("case_id"), "project_id": k["project_id"], "cell": k["cell"], "expected": exp,
                    "observed": got, "status": status})
    return out


def _ranks(xs):
    order = sorted(range(len(xs)), key=lambda i: xs[i])
    r = [0.0] * len(xs)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and xs[order[j + 1]] == xs[order[i]]:
            j += 1
        for k in range(i, j + 1):
            r[order[k]] = (i + j) / 2 + 1
        i = j + 1
    return r


def spearman(x, y):
    if len(x) < 3:
        return None
    rx, ry = _ranks(x), _ranks(y)
    mx, my = sum(rx) / len(rx), sum(ry) / len(ry)
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    den = (sum((a - mx) ** 2 for a in rx) * sum((b - my) ** 2 for b in ry)) ** 0.5
    return None if den == 0 else num / den


def compare_external(projects, external, measures, max_width=0.25, seed=20261121, B=2000):
    """external: rows project_id, measure, value. measures: rows measure, expected_sign (+, -, 0), role, source, vintage."""
    scores = {p: axis1(c) for p, c in projects.items()}
    out = []
    for m in measures:
        vals = {r["project_id"]: float(r["value"]) for r in external if r["measure"] == m["measure"] and r["value"] not in ("", None)}
        common = [p for p in vals if p in scores and scores[p]["width"] <= max_width]
        x = [(scores[p]["lower"] + scores[p]["upper"]) / 2 for p in common]
        y = [vals[p] for p in common]
        rho = spearman(x, y)
        ci = None
        if rho is not None:
            rng = random.Random(seed)
            reps = []
            for _ in range(B):
                idx = [rng.randrange(len(common)) for _ in common]
                r = spearman([x[i] for i in idx], [y[i] for i in idx])
                if r is not None:
                    reps.append(r)
            reps.sort()
            if len(reps) > 100:
                ci = [round(reps[int(0.025 * len(reps))], 3), round(reps[int(0.975 * len(reps)) - 1], 3)]
        out.append({"measure": m["measure"], "role": m.get("role"), "expected_sign": m.get("expected_sign"),
                    "n": len(common), "rho": None if rho is None else round(rho, 3), "ci95": ci,
                    "projects_excluded_wide_interval": sorted(p for p in vals if p in scores and scores[p]["width"] > max_width)})
    return out


def _csv(path):
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cells", required=True, help="merged_cells from index_reliability.py")
    ap.add_argument("--known", required=True)
    ap.add_argument("--external")
    ap.add_argument("--measures")
    ap.add_argument("--out", required=True)
    o = ap.parse_args()
    projects = json.load(open(o.cells)).get("merged_cells")
    res = {"known_cases": check_known_cases(projects, _csv(o.known))}
    if o.external and o.measures:
        res["external"] = compare_external(projects, _csv(o.external), _csv(o.measures))
    json.dump(res, open(o.out, "w"), indent=1)
    print("written", o.out)


if __name__ == "__main__":
    main()
