#!/usr/bin/env python3
"""Agreement of two coders on the privacy-talk sample (sheet CODE of the two workbooks from draw_agreement_sample.py).

Reported per column: n, raw agreement, Krippendorff's alpha (nominal; undefined, not 1, when all ratings fall in one category), a
bootstrap 95 % interval that is conditional on this quota sample, Gwet's AC1 on the declared category list, counts and the confusion
table; every facet also "end to end", where a unit only one coder found relevant counts as a facet disagreement. `relevant` is scored on all units; every facet on the units BOTH coders
marked R (the number is reported: it is the effective sample for facets). Breakdowns of `relevant` and `aspect` by candidate stratum
and by text route (A English original, B issuer's English edition, D machine translation). Thresholds are set in
docs/TALK_AGREEMENT_PROTOCOL_2026-11-13.md before coding; this script only computes.

usage: score_agreement.py --a <coder 1 xlsx> --b <coder 2 xlsx> --sample data/units/AGREEMENT_SAMPLE_2026-11-13.csv --out <json>
"""
import argparse, csv, json, os, random, collections
COLS = {"relevant": 10, "voice": 11, "aspect": 12, "direction": 14, "basis": 15, "status": 16, "modality": 17}


def alpha(pairs):
    """Krippendorff's alpha, nominal, two coders, no missing values. None when undefined (fewer than 2 units, or all ratings in one
    category: expected disagreement is zero and the coefficient does not exist; audit of 13 Nov 2026, item 5)."""
    pairs = [(x, y) for x, y in pairs if x and y]
    if len(pairs) < 2: return None
    o = collections.Counter(); n = collections.Counter()
    for x, y in pairs: o[(x, y)] += 1; o[(y, x)] += 1; n[x] += 1; n[y] += 1
    N = 2 * len(pairs); Do = sum(v for (x, y), v in o.items() if x != y) / N
    De = sum(n[x] * n[y] for x in n for y in n if x != y) / (N * (N - 1))
    return None if De == 0 else 1 - Do / De


def ac1(pairs, categories):
    """Gwet's AC1 on the DECLARED category set (not the categories that happen to be observed)."""
    pairs = [(x, y) for x, y in pairs if x and y]; q = len(categories)
    if len(pairs) < 2 or q < 2: return None
    pa = sum(x == y for x, y in pairs) / len(pairs); pi = {c: sum((x == c) + (y == c) for x, y in pairs) / (2 * len(pairs)) for c in categories}
    pe = sum(p * (1 - p) for p in pi.values()) / (q - 1)
    return (pa - pe) / (1 - pe)


def stat(pairs, categories, seed=20261113, B=2000):
    """The interval is a bootstrap over the units of THIS sample (quota sample, over-sampled strata): it is conditional on the sample
    and is not a design-based interval for the corpus. Replicates in which alpha is undefined are counted, not scored as 1."""
    pairs = [(x, y) for x, y in pairs if x and y]; out = {"n": len(pairs), "categories_declared": list(categories)}
    if len(pairs) < 2: return out
    a = alpha(pairs); rnd = random.Random(seed); reps = [alpha([pairs[rnd.randrange(len(pairs))] for _ in pairs]) for _ in range(B)]; bs = sorted(v for v in reps if v is not None)
    out.update({"agreement": round(sum(x == y for x, y in pairs) / len(pairs), 3), "alpha": None if a is None else round(a, 3), "alpha_undefined_reason": "all ratings in one category" if a is None else "",
                "alpha_ci95_conditional_on_sample": [round(bs[int(.025 * len(bs))], 3), round(bs[int(.975 * len(bs)) - 1], 3)] if len(bs) > 100 else None, "bootstrap_replicates_undefined": B - len(bs),
                "ac1": None if ac1(pairs, categories) is None else round(ac1(pairs, categories), 3), "counts": dict(collections.Counter(x for p in pairs for x in p)),
                "confusion": {f"{x}|{y}": v for (x, y), v in sorted(collections.Counter(pairs).items())}})
    return out


def read(f, allowed):
    """One coder's sheet CODE. Duplicate unit ids and values outside the declared lists stop the scoring: nothing is silently dropped."""
    import openpyxl  # only needed to read the workbooks; the coefficients are tested without it
    R = list(openpyxl.load_workbook(f, read_only=True)["CODE"].iter_rows(min_row=2, values_only=True)); out = {}; bad = []
    for r in R:
        if not r[1]: continue
        if r[1] in out: bad.append(f"duplicate unit id {r[1]}")
        out[r[1]] = {k: (str(r[c]).strip().upper() if r[c] not in (None, "") else "") for k, c in COLS.items()}
        bad += [f"{r[1]}: {k}={v!r} not in the declared list" for k, v in out[r[1]].items() if v and v not in allowed[k]]
    if bad: raise SystemExit(f"{f}: {len(bad)} problems, first: " + "; ".join(bad[:5]))
    return out


def score(A, Bc, S, allowed):
    miss = sorted(set(S) - set(A)) + sorted(set(S) - set(Bc))
    if miss: raise SystemExit(f"{len(miss)} sample units are missing from a workbook, first: {miss[:3]}")
    ids = list(S); done = [u for u in ids if A[u]["relevant"] and Bc[u]["relevant"]]; both = [u for u in done if A[u]["relevant"] == "R" and Bc[u]["relevant"] == "R"]
    union = [u for u in done if "R" in (A[u]["relevant"], Bc[u]["relevant"])]
    res = {"units_in_sample": len(S), "units_coded_by_both": len(done), "units_left_blank_by_a_coder": len(ids) - len(done), "units_both_relevant": len(both), "units_relevant_for_at_least_one": len(union),
           "relevant": stat([(A[u]["relevant"], Bc[u]["relevant"]) for u in done], allowed["relevant"])}
    for k in list(COLS)[1:]:
        res[k] = stat([(A[u][k], Bc[u][k]) for u in both], allowed[k])
        res[k]["facet_blank_on_a_relevant_unit"] = sum(1 for u in both if not (A[u][k] and Bc[u][k]))
        # end to end: a unit only one coder found relevant counts as a disagreement on the facet (the other coder's label is NOT_RELEVANT)
        res[k + "_end_to_end"] = stat([(A[u][k] if A[u]["relevant"] == "R" else "NOT_RELEVANT", Bc[u][k] if Bc[u]["relevant"] == "R" else "NOT_RELEVANT") for u in union], list(allowed[k]) + ["NOT_RELEVANT"])
    for dim in ("stratum", "route"):
        res["by_" + dim] = {v: {"relevant": stat([(A[u]["relevant"], Bc[u]["relevant"]) for u in done if S[u][dim] == v], allowed["relevant"]), "aspect": stat([(A[u]["aspect"], Bc[u]["aspect"]) for u in both if S[u][dim] == v], allowed["aspect"])} for v in sorted({S[u][dim] for u in ids})}
    return res


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--a", required=True); ap.add_argument("--b", required=True); ap.add_argument("--sample", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--schema", default=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "schema/talk_units_v13_DRAFT.json"))
    a = ap.parse_args(); F = json.load(open(a.schema))["L2_facets"]; allowed = {"relevant": ["R", "N", "U"], **{k: F[k] for k in list(COLS)[1:]}}
    S = {r["unit_id"]: r for r in csv.DictReader(open(a.sample, encoding="utf-8")) if r["set"] == "main"}
    res = score(read(a.a, allowed), read(a.b, allowed), S, allowed)
    json.dump(res, open(a.out, "w"), indent=1); print(json.dumps({k: {x: y for x, y in v.items() if x != "confusion"} if isinstance(v, dict) else v for k, v in res.items() if not k.startswith("by_")}, indent=1))


if __name__ == "__main__": main()
