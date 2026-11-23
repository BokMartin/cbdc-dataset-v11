#!/usr/bin/env python3
"""Add one OCR document to the units (MB, 23 Nov 2026: the Jamaica FAQ booklet, a scan in a core project).

The OCR text of scripts/frame/ocr_pdf.py (page markers `=== PAGE n ===`) is cut into units by unitise.units_of(), the same
function as every other document (sentences cut by a page break joined). The document key follows unitise.main()
(`<project>_<id>`, 70 characters). The existing units files are copied unchanged to --out (a new directory; the input is
never changed) and the new file is added; the unit manifest of --date is the latest manifest plus one row whose text_mode
is the one of the OCR record (data/manifest/OCR_<date>.csv), so OCR text is always told apart; the list of documents not
unitised of --date is the latest one without this document. Candidates are rebuilt afterwards by select_candidates.py.
Unit texts stay outside the repository.

usage: add_ocr_units.py --text <sha>.ocr.txt --id <document id> --ocr-record data/manifest/OCR_<date>.csv --units <dir>
                        --out <new dir> --date <date> --kind explainer --issuer "Bank of Jamaica"
"""
import argparse
import csv
import glob
import hashlib
import os
import re
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
from unitise import issuer_type, units_of  # noqa: E402


def latest(pattern, before):
    """The latest file of the pattern dated before --date (never the file this run writes)."""
    fs = [f for f in sorted(glob.glob(os.path.join(ROOT, "data/units", pattern))) if re.search(r"(\d{4}-\d{2}-\d{2})", f).group(1) < before]
    return fs[-1]


def write_csv(path, cols, rows, nl="\n"):
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, cols, lineterminator=nl)
        w.writeheader()
        w.writerows(rows)


def main(argv=None):
    ap = argparse.ArgumentParser()
    for k in ("--text", "--id", "--ocr-record", "--units", "--out", "--date", "--kind", "--issuer"):
        ap.add_argument(k, required=True)
    ap.add_argument("--tiers", default=os.path.join(ROOT, "data/manifest/TIERS_2026-11-17.csv"))
    a = ap.parse_args(argv)
    if os.path.abspath(a.out) == os.path.abspath(a.units) or os.path.exists(a.out):
        raise SystemExit("--out must be a new directory")
    t = next(r for r in csv.DictReader(open(a.tiers, encoding="utf-8")) if r["id"] == a.id)
    if t["decision_v12"] not in ("KEEP", "BORDERLINE"):
        raise SystemExit(f"{a.id} is {t['decision_v12']}, not an evidence document")
    rec = next(r for r in csv.DictReader(open(a.ocr_record, encoding="utf-8")) if r["id"] == a.id)
    raw = open(a.text, encoding="utf-8").read()
    if hashlib.sha256(raw.encode("utf-8")).hexdigest() != rec["text_sha256"] or rec["pdf_sha256"] != t["sha256"]:
        raise SystemExit("the OCR text or its PDF is not the one in the OCR record and the tier list")
    if t["language"] not in ("", "en"):
        raise SystemExit("only an English original is added here (route A); a translation goes through the translation queue")
    key = re.sub(r"[^A-Za-z0-9_-]+", "-", f"{t['project']}_{t['id']}")[:70]
    U, np_ = units_of(raw)
    if os.path.exists(os.path.join(a.units, key + ".units.csv")):
        raise SystemExit(f"{key} is already unitised")
    shutil.copytree(a.units, a.out)
    f = os.path.join(a.out, key + ".units.csv")
    with open(f, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["unit_id", "page", "para", "n_words", "text", "page_end"])
        for n, pi, k, s, pe in U:
            w.writerow([f"{key}:p{n}:s{k}", n, pi, len(s.split()), s, pe])
    mf = latest("UNITS_MANIFEST_*.csv", a.date)
    nl = "\r\n" if b"\r\n" in open(mf, "rb").read() else "\n"
    rd = csv.DictReader(open(mf, encoding="utf-8"))
    man = [m for m in rd if m["doc_key"] != key]
    row = {"doc_key": key, "id": t["id"], "project": t["project"], "tier": t["tier"], "year": t["year"], "kind": a.kind, "issuer": a.issuer,
           "issuer_type": issuer_type(a.issuer), "route": "A", "text_mode": rec["text_mode"], "layout_gap_share": "",
           "text_sha256": rec["text_sha256"], "pages": np_, "units": len(U), "words": sum(len(u[3].split()) for u in U),
           "units_sha256": hashlib.sha256(open(f, "rb").read()).hexdigest(), "stratum": "evidence", "inclined_group": "",
           "page_breaks_joined": sum(u[0] != u[4] for u in U)}
    out_man = os.path.join(ROOT, "data/units", f"UNITS_MANIFEST_{a.date}.csv")
    write_csv(out_man, rd.fieldnames, man + [{k: row.get(k, "") for k in rd.fieldnames}], nl)
    nu = latest("UNITS_NOT_UNITISED_*.csv", a.date)
    nl2 = "\r\n" if b"\r\n" in open(nu, "rb").read() else "\n"
    rd2 = csv.DictReader(open(nu, encoding="utf-8"))
    write_csv(os.path.join(ROOT, "data/units", f"UNITS_NOT_UNITISED_{a.date}.csv"), rd2.fieldnames, [r for r in rd2 if r["id"] != a.id], nl2)
    print(f"{key}: {len(U)} units, {row['words']} words, {np_} pages; manifest {os.path.basename(out_man)} has {len(man) + 1} documents")
    return row


if __name__ == "__main__":
    main()
