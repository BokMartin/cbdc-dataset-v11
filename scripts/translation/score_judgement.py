#!/usr/bin/env python3
"""Score the human judgement of benchmark sentence pairs (protocol in the INSTRUCTIONS sheet of the judgement workbook, fixed
11 Nov 2026 before judging). Codes: S same, W translation weaker, X translation stronger, M meaning differs otherwise, D not judgeable.
Reports, per stratum (pairs marked by the automatic check / random control of unmarked pairs) and weighted to all matched privacy
sentences (N_marked = 56, N_unmarked = 107): counts and shares among judgeable pairs with 95 % Wilson intervals. With two judges
(--second) also raw agreement and Cohen's kappa. The script checks that the sentence pairs in the workbook are the registered ones.

usage: score_judgement.py --workbook <filled xlsx> [--second <second judge's xlsx>] --key data/translation/benchmark/JUDGEMENT_KEY_2026-11-11.csv --out <json>
"""
import argparse, csv, hashlib, json, collections
import openpyxl
CODES = ["S", "W", "X", "M", "D"]; N = {"flagged": 56, "control": 107}


def wilson(k, n, z=1.96):
    if not n: return (None, None)
    p = k / n; d = 1 + z * z / n; c = (p + z * z / (2 * n)) / d; h = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5) / d
    return (round(max(0, c - h), 3), round(min(1, c + h), 3))


def read(path, key):
    ws = openpyxl.load_workbook(path)["JUDGE"]; out = {}
    for r in ws.iter_rows(min_row=2, values_only=True):
        n, code = int(r[0]), str(r[4] or "").strip().upper()
        if hashlib.sha256((r[2] + "\n" + r[3]).encode()).hexdigest() != key[n]["sha256_E_T"]: raise SystemExit(f"row {n}: sentence pair differs from the registered one")
        if code not in CODES: raise SystemExit(f"row {n}: code {code!r} missing or invalid")
        out[n] = code
    return out


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--workbook", required=True); ap.add_argument("--second"); ap.add_argument("--key", required=True); ap.add_argument("--out", required=True)
    a = ap.parse_args(); key = {int(r["n"]): r for r in csv.DictReader(open(a.key, encoding="utf-8"))}; J = read(a.workbook, key); res = {"n_rows": len(J), "strata": {}}
    for st in ("flagged", "control"):
        c = collections.Counter(J[n] for n in J if key[n]["stratum"] == st); judgeable = sum(c[k] for k in "SWXM")
        res["strata"][st] = {"rows": sum(c.values()), "not_judgeable_D": c["D"], "judgeable": judgeable,
                             **{k: {"count": c[k], "share": round(c[k] / judgeable, 3) if judgeable else None, "wilson95": wilson(c[k], judgeable)} for k in "SWXM"}}
    w = {}
    for k in "SWXM":  # weighted share over all matched privacy sentences, assuming D pairs are missing at random within a stratum
        sh = [res["strata"][st][k]["share"] for st in ("flagged", "control")]
        w[k] = round((sh[0] * N["flagged"] + sh[1] * N["control"]) / (N["flagged"] + N["control"]), 3) if None not in sh else None
    res["weighted_share_all_163_matched"] = w
    if a.second:
        K = read(a.second, key); ns = sorted(J); po = sum(J[n] == K[n] for n in ns) / len(ns)
        ca, cb = collections.Counter(J.values()), collections.Counter(K.values()); pe = sum(ca[k] * cb[k] for k in CODES) / len(ns) ** 2
        res["two_judges"] = {"raw_agreement": round(po, 3), "cohen_kappa": round((po - pe) / (1 - pe), 3) if pe < 1 else None}
    json.dump(res, open(a.out, "w"), indent=1); print(json.dumps(res, indent=1))


if __name__ == "__main__": main()
