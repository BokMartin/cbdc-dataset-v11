#!/usr/bin/env python3
"""Read the authors' entries back from a filled tier review workbook (round trip; audit of 13 Nov 2026, items 2 and 17).

Every row whose 'decision (authors)' differs from the decision on record becomes a row of data/manifest/AUTHOR_DECISIONS_<date>.csv
(with the SHA-256 of the workbook as basis). Nothing typed is silently ignored: values outside the allowed list, ids that are not in
the manifest and duplicate ids stop the import. Entries equal to the decision on record are counted as confirmations and listed in
data/manifest/AUTHOR_CONFIRMATIONS_<date>.csv, so that "evidence by model pre-screen only" can be told from "confirmed by an author".
'issuer / voice (authors)' and 'tier (authors)' are written to AUTHOR_ISSUER_NOTES_<date>.csv / AUTHOR_TIERS_<date>.csv as typed.

Also reads the smaller workbooks built from it (RECHECK_DECISIONS, CONFIRM_EVIDENCE): any sheet with the columns `id` and
'decision (authors)' is read; `--partial` says that the workbook does not hold every document. The value OK means "reviewed, the
decision on record stands" and is written as a confirmation.

usage: read_tier_decisions.py --workbook <filled xlsx> --tiers data/manifest/TIERS_<date>.csv --by MB --date 2026-11-14 [--partial] [--confirm-all-evidence]
  --confirm-all-evidence  the author states that every evidence row left empty was reviewed and is accepted as shown
"""
import argparse, csv, hashlib, os
import openpyxl
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
ALLOWED = ("KEEP", "BORDERLINE", "COMPANION", "WHOLESALE", "DROP")


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--workbook", required=True); ap.add_argument("--tiers", required=True); ap.add_argument("--by", required=True); ap.add_argument("--date", required=True); ap.add_argument("--confirm-all-evidence", action="store_true"); ap.add_argument("--partial", action="store_true"); ap.add_argument("--suffix", default="", help="letter added to the file names when a second workbook is read on the same date")
    a = ap.parse_args(); T = {r["id"]: r for r in csv.DictReader(open(a.tiers, encoding="utf-8"))}
    sha = hashlib.sha256(open(a.workbook, "rb").read()).hexdigest(); basis = f"{os.path.basename(a.workbook)} (sha256 {sha})"
    wb = openpyxl.load_workbook(a.workbook, read_only=True); seen = set(); bad = []; dec = []; conf = []; iss = []
    blank = 0
    for sn in wb.sheetnames:
        R = list(wb[sn].iter_rows(values_only=True))
        if not R or "id" not in R[0] or "decision (authors)" not in R[0]: continue
        h = list(R[0]); g = lambda r, k: (r[h.index(k)] if k in h and h.index(k) < len(r) else None)
        for r in R[1:]:
            i = g(r, "id")
            if not i: continue
            if i in seen: bad.append(f"duplicate id {i}")
            seen.add(i)
            if i not in T: bad.append(f"id {i} is not in {os.path.basename(a.tiers)}"); continue
            d = str(g(r, "decision (authors)") or "").strip().upper(); note = str(g(r, "note (authors)") or "").strip(); iv = str(g(r, "issuer / voice (authors)") or "").strip()
            if d == "OK": conf.append({"id": i, "project": T[i]["project"], "decision_v12": T[i]["decision_v12"], "decision_source": "author", "decided_by": a.by, "date": a.date, "basis": basis, "note": note}); d = ""; note = "__done__"
            if d and d not in ALLOWED: bad.append(f"{i}: decision {d!r} not allowed"); continue
            row = {"id": i, "project": T[i]["project"], "decision_v12": d or T[i]["decision_v12"], "decision_source": "author", "decided_by": a.by, "date": a.date, "basis": basis, "note": note}
            if note == "__done__": pass
            elif d and d != T[i]["decision_v12"]: dec.append(row)
            elif d or (a.confirm_all_evidence and T[i]["decision_v12"] in ("KEEP", "BORDERLINE") and T[i]["decision_source"] != "author"): conf.append(row)
            if iv: iss.append({"id": i, "project": T[i]["project"], "issuer_voice_as_typed": iv, "by": a.by, "date": a.date, "basis": basis})
    miss = set() if a.partial else set(T) - seen
    if miss: bad.append(f"{len(miss)} documents of the manifest are missing from the workbook, e.g. {sorted(miss)[:3]}")
    if bad: raise SystemExit(f"{len(bad)} problems, nothing imported; first: " + "; ".join(bad[:6]))
    R = list(wb["PROJECTS"].iter_rows(values_only=True)) if "PROJECTS" in wb.sheetnames else [[]]; ti = list(R[0]).index("tier (authors)") if "tier (authors)" in R[0] else None
    tiers = [{"project": r[0], "tier_authors": r[ti], "by": a.by, "date": a.date, "basis": basis} for r in R[1:] if ti is not None and r[ti] not in (None, "")]
    # confirmations are effective: a confirmed row is no longer 'model pre-screen' (the tier builder reads AUTHOR_CONFIRMATIONS as author decisions that change nothing)
    tag = a.date + a.suffix
    for name, rows in ((f"AUTHOR_DECISIONS_{tag}.csv", dec), (f"AUTHOR_CONFIRMATIONS_{tag}.csv", conf), (f"AUTHOR_ISSUER_NOTES_{tag}.csv", iss), (f"AUTHOR_TIERS_{tag}.csv", tiers)):
        if rows and os.path.exists(os.path.join(ROOT, "data/manifest", name)): raise SystemExit(f"{name} exists: use --suffix")
        if rows:
            with open(os.path.join(ROOT, "data/manifest", name), "w", newline="", encoding="utf-8") as fh:
                w = csv.DictWriter(fh, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    print(f"changed decisions {len(dec)}, confirmations {len(conf)}, issuer / voice notes {len(iss)}, tiers set {len(tiers)}; workbook sha256 {sha[:12]}")


if __name__ == "__main__": main()
