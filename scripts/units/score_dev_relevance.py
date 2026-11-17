#!/usr/bin/env python3
"""Agreement of the two authors' blind relevance labels on the development sample, from the committed label files (no workbook, no text).

Reports raw agreement, Krippendorff's alpha with a bootstrap interval, Gwet's AC1 and the confusion table: for all units both coded,
for the units whose document is still in the current corpus, per stratum, and with every pair that holds a "U" removed.
The development sample is not the reported validation; these figures say how well the codebook works for humans before it is repaired.

usage: score_dev_relevance.py --a data/units/DEV_LABELS_MB_<date>.csv --b data/units/DEV_LABELS_DS_<date>.csv --out <json>
"""
import argparse, collections, csv, glob, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import score_agreement as sa
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))); C = ["R", "N", "U"]


def block(P, cats):
    if not P: return {"n": 0}
    s = sa.stat(P, cats, B=2000); c = collections.Counter(P)
    return {"n": len(P), "agreement": round(s["agreement"], 3), "alpha": None if s["alpha"] is None else round(s["alpha"], 3), "alpha_ci95_conditional_on_sample": s.get("alpha_ci95_conditional_on_sample"),
            "ac1": round(sa.ac1(P, cats), 3), "confusion_rows_a_cols_b": {x: {y: c[(x, y)] for y in cats} for x in cats}}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--a", required=True); ap.add_argument("--b", required=True); ap.add_argument("--out", required=True); a = ap.parse_args()
    rd = lambda p: {r["unit_id"]: r for r in csv.DictReader(open(p, encoding="utf-8"))}
    A, B = rd(a.a), rd(a.b); assert set(A) == set(B), "the two files do not hold the same units"
    man = {r["doc_key"] for r in csv.DictReader(open(sorted(glob.glob(os.path.join(ROOT, "data/units/UNITS_MANIFEST_*.csv")))[-1], encoding="utf-8"))}
    ids = [u for u in A if A[u]["relevant"] in C and B[u]["relevant"] in C]; pair = lambda us: [(A[u]["relevant"], B[u]["relevant"]) for u in us]
    noU = lambda us: [p for p in pair(us) if "U" not in p]
    out = {"coder_a": next(iter(A.values()))["coder"], "coder_b": next(iter(B.values()))["coder"], "units_in_sample": len(A), "both_coded": len(ids),
           "not_coded_by_a": sorted(u for u in A if A[u]["relevant"] not in C), "not_coded_by_b": sorted(u for u in B if B[u]["relevant"] not in C),
           "all": block(pair(ids), C), "all_without_U_pairs": block(noU(ids), ["R", "N"]),
           "current_corpus_only": block(pair([u for u in ids if u.split(":p")[0] in man]), C),
           "by_stratum": {s: block(pair([u for u in ids if A[u]["stratum"] == s]), C) for s in ("D", "N", "R")},
           "U_labels": {"a": sum(A[u]["relevant"] == "U" for u in ids), "b": sum(B[u]["relevant"] == "U" for u in ids), "both": sum(A[u]["relevant"] == "U" == B[u]["relevant"] for u in ids)},
           "threshold_of_protocol_v2": 0.667, "status": "development sample; not a reported validation"}
    json.dump(out, open(a.out, "w"), indent=1); print(json.dumps({k: out[k] for k in ("both_coded", "U_labels")}), out["all"]["agreement"], out["all"]["alpha"], out["all_without_U_pairs"]["alpha"])


if __name__ == "__main__": main()
