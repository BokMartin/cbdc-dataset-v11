#!/usr/bin/env python3
"""Agreement of two coders on the privacy-talk sample (sheet CODE of the two workbooks from draw_agreement_sample.py).

Reported per column: n, raw agreement, Krippendorff's alpha (nominal) with a bootstrap 95 % interval over units, and for `relevant`
also Gwet's AC1 (alpha is unstable when one category is rare). `relevant` is scored on all units; every facet on the units BOTH coders
marked R (the number is reported: it is the effective sample for facets). Breakdowns of `relevant` and `aspect` by candidate stratum
and by text route (A English original, B issuer's English edition, D machine translation). Thresholds are set in
docs/TALK_AGREEMENT_PROTOCOL_2026-11-13.md before coding; this script only computes.

usage: score_agreement.py --a <coder 1 xlsx> --b <coder 2 xlsx> --sample data/units/AGREEMENT_SAMPLE_2026-11-13.csv --out <json>
"""
import argparse, csv, json, random, collections
import openpyxl
COLS = {"relevant": 10, "voice": 11, "aspect": 12, "direction": 14, "basis": 15, "status": 16, "modality": 17}


def alpha(pairs):
    pairs = [(x, y) for x, y in pairs if x and y]
    if len(pairs) < 2: return None
    o = collections.Counter(); n = collections.Counter()
    for x, y in pairs: o[(x, y)] += 1; o[(y, x)] += 1; n[x] += 1; n[y] += 1
    N = 2 * len(pairs); Do = sum(v for (x, y), v in o.items() if x != y) / N
    De = sum(n[x] * n[y] for x in n for y in n if x != y) / (N * (N - 1))
    return 1.0 if De == 0 else 1 - Do / De


def ac1(pairs):
    pairs = [(x, y) for x, y in pairs if x and y]; cats = {c for p in pairs for c in p}
    if len(pairs) < 2 or len(cats) < 2: return None
    pa = sum(x == y for x, y in pairs) / len(pairs); pi = {c: sum((x == c) + (y == c) for x, y in pairs) / (2 * len(pairs)) for c in cats}
    pe = sum(p * (1 - p) for p in pi.values()) / (len(cats) - 1)
    return (pa - pe) / (1 - pe)


def stat(pairs, seed=20261113, B=2000):
    pairs = [(x, y) for x, y in pairs if x and y]; a = alpha(pairs)
    if a is None: return {"n": len(pairs)}
    rnd = random.Random(seed); bs = sorted(v for v in (alpha([pairs[rnd.randrange(len(pairs))] for _ in pairs]) for _ in range(B)) if v is not None)
    return {"n": len(pairs), "agreement": round(sum(x == y for x, y in pairs) / len(pairs), 3), "alpha": round(a, 3), "alpha_ci95": [round(bs[int(.025 * len(bs))], 3), round(bs[int(.975 * len(bs)) - 1], 3)],
            "ac1": None if ac1(pairs) is None else round(ac1(pairs), 3), "categories": dict(collections.Counter(x for p in pairs for x in p))}


def read(f):
    R = list(openpyxl.load_workbook(f, read_only=True)["CODE"].iter_rows(min_row=2, values_only=True))
    return {r[1]: {k: (str(r[c]).strip().upper() if r[c] not in (None, "") else "") for k, c in COLS.items()} for r in R if r[1]}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--a", required=True); ap.add_argument("--b", required=True); ap.add_argument("--sample", required=True); ap.add_argument("--out", required=True)
    a = ap.parse_args(); A = read(a.a); Bc = read(a.b); S = {r["unit_id"]: r for r in csv.DictReader(open(a.sample, encoding="utf-8")) if r["set"] == "main"}
    ids = [u for u in S if u in A and u in Bc]; both = [u for u in ids if A[u]["relevant"] == "R" and Bc[u]["relevant"] == "R"]
    res = {"units_in_sample": len(S), "units_coded_by_both": len([u for u in ids if A[u]["relevant"] and Bc[u]["relevant"]]), "units_both_relevant": len(both), "relevant": stat([(A[u]["relevant"], Bc[u]["relevant"]) for u in ids])}
    for k in list(COLS)[1:]: res[k] = stat([(A[u][k], Bc[u][k]) for u in both])
    for dim in ("stratum", "route"):
        res["by_" + dim] = {v: {"relevant": stat([(A[u]["relevant"], Bc[u]["relevant"]) for u in ids if S[u][dim] == v]), "aspect": stat([(A[u]["aspect"], Bc[u]["aspect"]) for u in both if S[u][dim] == v])} for v in sorted({S[u][dim] for u in ids})}
    json.dump(res, open(a.out, "w"), indent=1); print(json.dumps({k: v for k, v in res.items() if not k.startswith("by_")}, indent=1))


if __name__ == "__main__": main()
