#!/usr/bin/env python3
"""Lock one returned blind F-cell workbook (ADR-012 D1, D2; ADR-016 §4).

Reads the sheet KODOVANI of a workbook made by build_blind_cell_workbook.py and filled by one author, checks it, writes
the coder file in the format of the coder template of 22 Nov 2026 (read by scripts/index_reliability.py) and the sheets
PET and CTENI as CSV to a folder OUTSIDE the repository (quotes are source text), and appends one row to
data/index/BLIND_CELL_LOCK.csv with the SHA-256 of the returned workbook and of the coder file. That row, pushed to
GitHub, is the time stamp of the lock: model outputs of the 14 blind projects may be opened only after both coders have a
row there (and the reference sample is coded, ADR-016 §4). A coder is locked once; the script refuses a second lock.

Checks (all problems are listed at once, nothing is dropped silently): the 112 keys (14 projects x 8 cells) are present
exactly once and nothing else; every row has either a value or an evidence state; an unknown state has a reason; a
value has a document of that project, a whole-number page and a quote; text_route is filled from the document when
blank and must match it when given; then index_reliability.read() applies the template rules (enums, basis for F1, F2,
F4, F9, no value on unknown or n.a. evidence).

usage: lock_blind_cell_workbook.py --coder MB --xlsx BLIND_CELLS_MB_2026-11-24_filled.xlsx --out <dir outside the repo>
"""
import argparse
import csv
import datetime
import hashlib
import os
import sys

from openpyxl import load_workbook

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
from build_blind_cell_workbook import BLIND, CELLS, CODERS, EXTRA, VALUES, documents  # noqa: E402
from index_reliability import FIELDS, read  # noqa: E402

LOCK = os.path.join(ROOT, "data", "index", "BLIND_CELL_LOCK.csv")
LOCK_FIELDS = ["coder", "locked_utc", "returned_file", "returned_sha256", "coder_csv_sha256", "rows", "valued",
               "undetermined", "pet_rows", "reading_rows"]


def _sha(path):
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def _s(v):
    if v is None:
        return ""
    if isinstance(v, float) and v.is_integer():
        v = int(v)
    return str(v).strip()


def _sheet(wb, name):
    ws = wb[name]
    rows = list(ws.iter_rows(values_only=True))
    head = [_s(h) for h in rows[0]]
    return [dict(zip(head, map(_s, r))) for r in rows[1:] if any(_s(x) for x in r)]


def check(rows, docs):
    """Coder records and the list of problems."""
    by_code = {d["code"]: d for d in docs}
    by_id = {d["id"]: d for d in docs}
    grid = {(p, c) for p in BLIND for c in CELLS}
    seen, bad, out = set(), [], []
    for i, r in enumerate(rows, 2):
        key = (r.get("project_id", ""), r.get("cell", "").upper())
        if key not in grid:
            bad.append(f"row {i}: {key} is not one of the 112 keys")
            continue
        if key in seen:
            bad.append(f"row {i}: {key} twice")
        seen.add(key)
        rec = {f: r.get(f, "") for f in FIELDS + EXTRA}
        rec["cell"] = key[1]
        v, ev = rec["value"].lower(), rec["evidence_state"].lower()
        if v and v not in VALUES[key[1]]:
            bad.append(f"row {i} {key}: value {v!r} (allowed {', '.join(VALUES[key[1]])})")
        if not v and not ev:
            bad.append(f"row {i} {key}: neither value nor evidence_state (an empty row is not an answer)")
        if ev == "unknown" and not rec["unknown_reason"]:
            bad.append(f"row {i} {key}: evidence_state unknown without unknown_reason")
        d = None
        if rec["document_id"]:
            d = by_code.get(rec["document_id"].upper()) or by_id.get(rec["document_id"])
            if d is None or d["project"] != key[0]:
                bad.append(f"row {i} {key}: document {rec['document_id']!r} is not a document of {key[0]}")
                d = None
            elif d["for_cells"] != "ano":
                bad.append(f"row {i} {key}: document {d['code']} is wholesale (INCLINED), not for F-cells")
            else:
                rec["document_id"] = d["id"]
        if v:
            if not rec["document_id"] or not rec["quote"]:
                bad.append(f"row {i} {key}: value without document or quote")
            if not rec["page_index"].isdigit():
                bad.append(f"row {i} {key}: page_index {rec['page_index']!r} is not a page number")
        if d is not None:
            if not rec["text_route"]:
                rec["text_route"] = d["route"]
            elif rec["text_route"].upper() != d["route"]:
                bad.append(f"row {i} {key}: text_route {rec['text_route']} but document {d['code']} is route {d['route']}")
        out.append(rec)
    for k in sorted(grid - seen):
        bad.append(f"missing key {k}")
    return out, bad


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--coder", required=True, choices=CODERS)
    ap.add_argument("--xlsx", required=True)
    ap.add_argument("--out", required=True, help="folder outside the repository")
    a = ap.parse_args()
    out = os.path.abspath(a.out)
    if out == ROOT or out.startswith(ROOT + os.sep):
        raise SystemExit("refused: the coder files hold quotes of source text and stay outside the repository")
    if os.path.exists(LOCK):
        with open(LOCK, newline="", encoding="utf-8") as fh:
            if any(r["coder"] == a.coder for r in csv.DictReader(fh)):
                raise SystemExit(f"refused: {a.coder} is already locked in {os.path.relpath(LOCK, ROOT)}")
    wb = load_workbook(a.xlsx, read_only=True, data_only=True)
    recs, bad = check(_sheet(wb, "KODOVANI"), documents())
    if bad:
        raise SystemExit(f"{a.xlsx}: {len(bad)} problem(s), nothing locked:\n  " + "\n  ".join(bad))
    os.makedirs(out, exist_ok=True)
    stem = f"BLIND_CELLS_{a.coder}_locked"
    coder_csv = os.path.join(out, stem + ".csv")
    with open(coder_csv, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, FIELDS + EXTRA)
        w.writeheader()
        w.writerows(recs)
    read(coder_csv)  # the template rules of index_reliability; raises on any violation
    extra = {}
    for sheet in ("PET", "CTENI"):
        rows = _sheet(wb, sheet)
        extra[sheet] = len(rows)
        with open(os.path.join(out, f"{stem}_{sheet}.csv"), "w", newline="", encoding="utf-8") as fh:
            if rows:
                w = csv.DictWriter(fh, list(rows[0]))
                w.writeheader()
                w.writerows(rows)
    new = not os.path.exists(LOCK)
    with open(LOCK, "a", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, LOCK_FIELDS)
        if new:
            w.writeheader()
        w.writerow({"coder": a.coder, "locked_utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "returned_file": os.path.basename(a.xlsx), "returned_sha256": _sha(a.xlsx),
                    "coder_csv_sha256": _sha(coder_csv), "rows": len(recs),
                    "valued": sum(bool(r["value"]) for r in recs), "undetermined": sum(not r["value"] for r in recs),
                    "pet_rows": extra["PET"], "reading_rows": extra["CTENI"]})
    print(f"{a.coder} locked: {len(recs)} rows, coder file {coder_csv}")


if __name__ == "__main__":
    main()
