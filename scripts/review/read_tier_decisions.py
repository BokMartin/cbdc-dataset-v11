#!/usr/bin/env python3
"""Read the authors' entries back from a filled tier review workbook (round trip; audit of 13 Nov 2026, items 2 and 17).

Every row whose 'decision (authors)' differs from the decision on record becomes a row of data/manifest/AUTHOR_DECISIONS_<date>.csv
(with the SHA-256 of the workbook as basis). Nothing typed is silently ignored: values outside the allowed list, ids that are not in
the manifest and duplicate ids stop the import. Entries equal to the decision on record are counted as confirmations and listed in
data/manifest/AUTHOR_CONFIRMATIONS_<date>.csv, so that "evidence by model pre-screen only" can be told from "confirmed by an author".
'issuer / voice (authors)' and 'tier (authors)' are written to AUTHOR_ISSUER_NOTES_<date>.csv / AUTHOR_TIERS_<date>.csv as typed.

usage: read_tier_decisions.py --workbook <filled xlsx> --tiers data/manifest/TIERS_<date>.csv --by MB --date 2026-11-14 [--confirm-all-evidence]
  --confirm-all-evidence  the author states that every evidence row left empty was reviewed and is accepted as shown
"""
import argparse, csv, hashlib, os
import openpyxl
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
ALLOWED = ("KEEP", "BORDERLINE", "COMPANION", "WHOLESALE", "DROP")


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--workbook", required=True); ap.add_argument("--tiers", required=True); ap.add_argument("--by", required=True); ap.add_argument("--date", required=True); ap.add_argument("--confirm-all-evidence", action="store_true")
    a = ap.parse_args(); T = {r["id"]: r for r in csv.DictReader(open(a.tiers, encoding="utf-8"))}
    sha = hashlib.sha256(open(a.workbook, "rb").read()).hexdigest(); basis = f"{os.path.basename(a.workbook)} (sha256 {sha})"
    wb = openpyxl.load_workbook(a.workbook, read_only=True); seen = set(); bad = []; dec = []; conf = []; iss = []
    for sn in ("T1", "T2", "T3", "OUT_OF_FRAME"):
        R = list(wb[sn].iter_rows(values_only=True)); h = list(R[0]); g = lambda r, k: (r[h.index(k)] if k in h and h.index(k) < len(r) else None)
        for r in R[1:]:
            i = g(r, "id")
            if not i: continue
            if i in seen: bad.append(f"duplicate id {i}")
            seen.add(i)
            if i not in T: bad.append(f"id {i} is not in {os.path.basename(a.tiers)}"); continue
            d = str(g(r, "decision (authors)") or "").strip().upper(); note = str(g(r, "note (authors)") or "").strip(); iv = str(g(r, "issuer / voice (authors)") or "").strip()
            if d and d not in ALLOWED: bad.append(f"{i}: decision {d!r} not allowed"); continue
            row = {"id": i, "project": T[i]["project"], "decision_v12": d or T[i]["decision_v12"], "decision_source": "author", "decided_by": a.by, "date": a.date, "basis": basis, "note": note}
            if d and d != T[i]["decision_v12"]: dec.append(row)
            elif d or (a.confirm_all_evidence and T[i]["decision_v12"] in ("KEEP", "BORDERLINE") and T[i]["decision_source"] != "author"): conf.append(row)
            if iv: iss.append({"id": i, "project": T[i]["project"], "issuer_voice_as_typed": iv, "by": a.by, "date": a.date, "basis": basis})
    miss = set(T) - seen
    if miss: bad.append(f"{len(miss)} documents of the manifest are missing from the workbook, e.g. {sorted(miss)[:3]}")
    if bad: raise SystemExit(f"{len(bad)} problems, nothing imported; first: " + "; ".join(bad[:6]))
    R = list(wb["PROJECTS"].iter_rows(values_only=True)); ti = list(R[0]).index("tier (authors)"); tiers = [{"project": r[0], "tier_authors": r[ti], "by": a.by, "date": a.date, "basis": basis} for r in R[1:] if r[ti] not in (None, "")]
    for name, rows in ((f"AUTHOR_DECISIONS_{a.date}.csv", dec), (f"AUTHOR_CONFIRMATIONS_{a.date}.csv", conf), (f"AUTHOR_ISSUER_NOTES_{a.date}.csv", iss), (f"AUTHOR_TIERS_{a.date}.csv", tiers)):
        if rows:
            with open(os.path.join(ROOT, "data/manifest", name), "w", newline="", encoding="utf-8") as fh:
                w = csv.DictWriter(fh, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    print(f"changed decisions {len(dec)}, confirmations {len(conf)}, issuer / voice notes {len(iss)}, tiers set {len(tiers)}; workbook sha256 {sha[:12]}")


if __name__ == "__main__": main()
