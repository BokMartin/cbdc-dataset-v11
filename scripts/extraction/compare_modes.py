#!/usr/bin/env python3
"""Mechanical comparison of two fills of the same jurisdiction (e.g. single vs two-stage, or two models/vendors).

For each cell the comparison tuple is (value, evidence_state, claim_status, doc, page). Agreement levels:
  full      identical tuple
  value     same value, different evidence/status/locator
  differ    different value
  missing   cell present in only one fill
Prints the per-cell table and a summary; writes <out>.csv. Exit code 0 always (this is a report, not a gate).
Both fills must have processing_state 'ok' or 'ok_with_validation_problems' on every row; otherwise the comparison is
reported as INVALID (ADR-001 NO3: a comparison that silently omits failed documents is not a comparison).

usage: compare_modes.py A.csv B.csv [--labels single two_stage] [--out comparison.csv]
"""
import argparse, csv, collections

KEY = ("value", "evidence_state", "claim_status", "doc", "page")


def load(p):
    rows = list(csv.DictReader(open(p, encoding="utf-8")))
    bad = sorted({r.get("processing_state", "") for r in rows} - {"ok", "ok_with_validation_problems"})
    return {r["cell"]: r for r in rows}, bad


def norm(v): return str(v or "").strip().lower()


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("a"); ap.add_argument("b"); ap.add_argument("--labels", nargs=2, default=["A", "B"]); ap.add_argument("--out", default="")
    a = ap.parse_args(); A, badA = load(a.a); B, badB = load(a.b); la, lb = a.labels
    valid = not badA and not badB
    out = []; counts = collections.Counter()
    for cell in sorted(set(A) | set(B)):
        ra, rb = A.get(cell), B.get(cell)
        if not ra or not rb: level = "missing"
        else:
            ta = tuple(norm(ra.get(k)) for k in KEY); tb = tuple(norm(rb.get(k)) for k in KEY)
            level = "full" if ta == tb else ("value" if ta[0] == tb[0] else "differ")
        counts[level] += 1
        out.append({"cell": cell, "agreement": level, **{f"{la}_{k}": (ra or {}).get(k, "") for k in KEY}, **{f"{lb}_{k}": (rb or {}).get(k, "") for k in KEY}})
        print(f"{cell:40} {level:8} {la}={(ra or {}).get('value','-')!s:>18} [{(ra or {}).get('evidence_state','')}/{(ra or {}).get('claim_status','')}/d{(ra or {}).get('doc','')}p{(ra or {}).get('page','')}]  {lb}={(rb or {}).get('value','-')!s:>18} [{(rb or {}).get('evidence_state','')}/{(rb or {}).get('claim_status','')}/d{(rb or {}).get('doc','')}p{(rb or {}).get('page','')}]")
    print("\nVALID" if valid else f"\nINVALID comparison: processing states {la}={badA} {lb}={badB}", dict(counts))
    if a.out:
        with open(a.out, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(out[0].keys())); w.writeheader(); w.writerows(out)
            f.write(f"# valid={valid}; {dict(counts)}\n")


if __name__ == "__main__": main()
