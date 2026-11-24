#!/usr/bin/env python3
"""Reader for the returned translation disagreement workbook (NESHODY_PREKLAD_MB_DS_<date>.xlsx, sheet PREKLAD).

MB and DS went through the 35 benchmark pairs on which their blind codes differ and wrote a joint code into column K
(finalni_kod_MB_DS); columns H to J hold an AI proposal of 19 Nov that served only as background. The script checks every
sentence pair against the registered key (SHA-256 of E and T) and writes one row per pair without any text. A blank or invalid
column K is left as needs_author_check. The blind judgements are not changed.

usage: read_translation_disagreement.py --workbook <xlsx> --key data/translation/benchmark/JUDGEMENT_KEY_2026-11-11.csv --out <csv> --date <YYYY-MM-DD>
"""
import argparse, collections, csv, hashlib
CODES = ("S", "W", "X", "M", "D")
COLS = ["n", "pair", "stratum", "mb_blind", "ds_blind", "ai_proposal", "joint_code", "reason", "status", "adjudicated_by", "date", "workbook_sha256"]


def code(x):
    c = str(x or "").strip().upper()
    return c if c in CODES else ""


def main():
    import openpyxl
    ap = argparse.ArgumentParser()
    for k in ("workbook", "key", "out", "date"): ap.add_argument("--" + k, required=True)
    a = ap.parse_args(); sha = hashlib.sha256(open(a.workbook, "rb").read()).hexdigest()
    key = {int(r["n"]): r for r in csv.DictReader(open(a.key, encoding="utf-8"))}
    ws = openpyxl.load_workbook(a.workbook)["PREKLAD"]; rows = list(ws.iter_rows(values_only=True)); h = rows[0]
    assert h[1] == "#" and h[5] == "MB" and h[6] == "DS" and h[10] == "finalni_kod_MB_DS", "unexpected layout of sheet PREKLAD"
    out = []
    for r in rows[1:]:
        if r[1] is None: continue
        n = int(r[1]); E, T = (r[3] or ""), (r[4] or "")
        E, T = (E[1:] if E.startswith("'") else E), (T[1:] if T.startswith("'") else T)
        assert hashlib.sha256((E + "\n" + T).encode()).hexdigest() == key[n]["sha256_E_T"], f"pair {n} differs from the registered one"
        mb, ds, j = code(r[5]), code(r[6]), code(r[10])
        assert mb and ds and mb != ds, f"pair {n} is not a disagreement"
        out.append({"n": n, "pair": key[n]["pair"], "stratum": key[n]["stratum"], "mb_blind": mb, "ds_blind": ds, "ai_proposal": code(r[7]),
                    "joint_code": j, "reason": str(r[11] or "").strip().upper(), "status": "agreed" if j else "needs_author_check",
                    "adjudicated_by": "MB+DS jointly" if j else "", "date": a.date if j else "", "workbook_sha256": sha})
    out.sort(key=lambda d: d["n"])
    with open(a.out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLS); w.writeheader(); w.writerows(out)
    print(a.out, len(out), dict(collections.Counter(d["status"] for d in out)), dict(collections.Counter(d["joint_code"] for d in out)))


if __name__ == "__main__": main()
