#!/usr/bin/env python3
"""Apply decided fixes to the issuer ledger and to the unit manifest of the same date (MB, 23 Nov 2026: the machine check
scripts/review/check_issuers.py replaces the manual review of issuer, issuer type and kind; only its conflicts go to the authors).

Reads the latest ledger before --date and the fixes file (id, field, old, new, reason, decided); refuses a fix whose `old` value
is not the current one. Writes data/manifest/ISSUERS_<date>.csv (the fixed rows get issuer_source = machine_check_<date>, and the
`check` note that the fix answers is cleared) and rewrites issuer, issuer_type and kind in data/units/UNITS_MANIFEST_<date>.csv.

usage: apply_issuer_fixes.py --fixes data/manifest/ISSUER_FIXES_2026-11-23.csv --date 2026-11-23
"""
import argparse, csv, glob, io, os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FIELDS = {"issuer", "issuer_type", "kind"}


def latest(pattern, before):
    c = [p for p in sorted(glob.glob(os.path.join(ROOT, pattern))) if os.path.basename(p).split("_")[-1][:10] < before]
    return c[-1]


def read(p):
    raw = open(p, encoding="utf-8", newline="").read()
    return list(csv.DictReader(io.StringIO(raw))), ("\r\n" if "\r\n" in raw else "\n")


def write(p, rows, nl):
    with open(p, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, list(rows[0]), lineterminator=nl); w.writeheader(); w.writerows(rows)


def apply(ledger, manifest, fixes, date):
    led = {r["id"]: r for r in ledger}
    for f in fixes:
        if f["field"] not in FIELDS: raise SystemExit(f"field not fixable here: {f['field']}")
        r = led.get(f["id"])
        if r is None: raise SystemExit(f"id not in the ledger: {f['id']}")
        if r[f["field"]] != f["old"]: raise SystemExit(f"{f['id']} {f['field']}: ledger holds {r[f['field']]!r}, fix expects {f['old']!r}")
        r[f["field"]] = f["new"]; r["issuer_source"] = f"machine_check_{date}"
        if r["check"] == "issuer is not a central bank" and r["issuer_type"] == "central_bank": r["check"] = ""
    for m in manifest:
        if m["id"] in led:
            for k in FIELDS: m[k] = led[m["id"]][k]
    return ledger, manifest


def main(argv=None):
    ap = argparse.ArgumentParser(); ap.add_argument("--fixes", required=True); ap.add_argument("--date", required=True); a = ap.parse_args(argv)
    lp = latest("data/manifest/ISSUERS_2*.csv", a.date); ledger, lnl = read(lp)
    mp = os.path.join(ROOT, "data/units", f"UNITS_MANIFEST_{a.date}.csv"); manifest, mnl = read(mp)
    fixes = list(csv.DictReader(open(a.fixes, encoding="utf-8")))
    ledger, manifest = apply(ledger, manifest, fixes, a.date)
    write(os.path.join(ROOT, "data/manifest", f"ISSUERS_{a.date}.csv"), ledger, lnl); write(mp, manifest, mnl)
    print(f"{len(fixes)} fixes from {os.path.basename(a.fixes)} applied to {os.path.basename(lp)} -> ISSUERS_{a.date}.csv and {os.path.basename(mp)}")


if __name__ == "__main__":
    main()
