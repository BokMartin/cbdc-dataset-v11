#!/usr/bin/env python3
"""MOCK inputs for a dry run of the privacy-index chain (MB, 21 Nov 2026: "zatím to udělej na mockup datech").

Writes invented data for 44 invented projects MOCK01 to MOCK44 (no real project code, no real value) into
data/index/mock/: two blind-coder files, known cases, external measures. Every file name starts with MOCK_ and every
file says MOCK in its first row or field. These are not results and must never be read as results.

usage: index_mock.py [--out data/index/mock] [--seed 20261121]
"""
import argparse
import csv
import os
import random

CORE = ("F1", "F2", "F4", "F7")
PROTECTIVE = {"F1": "no", "F2": "no", "F4": "yes", "F7": "yes"}
STATUS = [("considered", "untested_or_unreported", 0.5), ("considered", "tested", 0.2),
          ("endorsed", "untested_or_unreported", 0.2), ("endorsed", "operational", 0.1)]
COVERAGE = {"F1": 0.77, "F2": 0.5, "F4": 0.5, "F7": 0.5}  # F1 from the sealed census aggregate; the rest assumed
TIERS = ["T1"] * 8 + ["T2"] * 8 + ["T3"] * 28
FIELDS = ["project_id", "cell", "value", "decision_status", "implementation_status", "quote", "page_index"]
BANNER = "MOCK DATA - invented - not a result"


def _status(rng):
    x, acc = rng.random(), 0.0
    for dec, impl, p in STATUS:
        acc += p
        if x < acc:
            return dec, impl
    return STATUS[-1][:2]


def generate(seed=20261121, disagreement=0.1):
    rng = random.Random(seed)
    projects = [f"MOCK{i:02d}" for i in range(1, 45)]
    a, b = [], []
    for p in projects:
        lean = rng.random()  # a project-level tendency, so that the cells are not independent
        for c in CORE:
            if rng.random() < COVERAGE[c]:
                protective = rng.random() < 0.25 + 0.5 * lean
                v = PROTECTIVE[c] if protective else ("yes" if PROTECTIVE[c] == "no" else "no")
                dec, impl = _status(rng)
            else:
                v, dec, impl = "undetermined", "", ""
            row = {"project_id": p, "cell": c, "value": v, "decision_status": dec, "implementation_status": impl,
                   "quote": BANNER, "page_index": ""}
            a.append(row)
            r2 = dict(row)
            if rng.random() < disagreement:
                r2["value"] = rng.choice([x for x in ("yes", "no", "undetermined") if x != v])
            b.append(r2)
    tiers = dict(zip(projects, rng.sample(TIERS, len(TIERS))))
    return projects, tiers, a, b


def write(out, seed=20261121):
    os.makedirs(out, exist_ok=True)
    projects, tiers, a, b = generate(seed)
    for name, rows in (("MOCK_CODER_A.csv", a), ("MOCK_CODER_B.csv", b)):
        with open(os.path.join(out, name), "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, FIELDS)
            w.writeheader()
            w.writerows(rows)
    rng = random.Random(seed + 1)
    valued = [r for r in a if r["value"] != "undetermined"]
    picks = rng.sample(valued, 6)
    with open(os.path.join(out, "MOCK_KNOWN_CASES.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["case_id", "project_id", "cell", "expected_value", "expected_min_rung", "note"])
        for i, r in enumerate(picks, 1):
            exp = r["value"] if i != 6 else ("yes" if r["value"] == "no" else "no")  # one planted miss
            w.writerow([f"MK{i:02d}", r["project_id"], r["cell"], exp, "", BANNER + (" (planted miss)" if i == 6 else "")])
    with open(os.path.join(out, "MOCK_EXTERNAL.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["project_id", "measure", "value", "note"])
        prot = {p: sum(1 for r in a if r["project_id"] == p and r["value"] == PROTECTIVE[r["cell"]]) for p in projects}
        for p in projects:
            w.writerow([p, "mock_convergent", round(prot[p] + rng.gauss(0, 1), 3), BANNER])
            w.writerow([p, "mock_discriminant", round(rng.gauss(0, 1), 3), BANNER])
    with open(os.path.join(out, "MOCK_MEASURES.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["measure", "role", "expected_sign", "source", "vintage", "note"])
        w.writerow(["mock_convergent", "convergent", "+", "invented", "", BANNER])
        w.writerow(["mock_discriminant", "discriminant", "0", "invented", "", BANNER])
    with open(os.path.join(out, "MOCK_TIERS.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["project_id", "tier", "note"])
        for p in projects:
            w.writerow([p, tiers[p], BANNER])
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(os.path.dirname(__file__), "..", "data", "index", "mock"))
    ap.add_argument("--seed", type=int, default=20261121)
    o = ap.parse_args()
    print("written", write(o.out, o.seed))
