#!/usr/bin/env python3
"""Add OCR text of single scanned pages to a document that is already unitised (MB, 23 Nov 2026: pages 7, 14 and 84 of the
BOJ Annual Report 2023, CAND-132, have no text layer; page 14 reports the JAM-DEX roll-out, page 84 is a JAM-DEX poster).

The OCR text (page markers `=== PAGE n ===`; made on MB's computer with tesseract, psm 3, words not corrected) is cut by
unitise.units_of() without joining across its page markers (the pages are not adjacent). A blank line that tesseract put
before a line starting in lower case is not a paragraph break and is removed first. The new units are numbered after the
highest unit number of the document, so no existing unit id changes; rows are placed in page order. A page that already has
units is refused. The existing units files are copied unchanged to --out (a new directory) with the document's file
extended; the unit manifest of --date gets the document's new units, words and file hash and text mode `reading_order+ocr`;
data/manifest/OCR_<date>.csv gets one row for the document. Unit texts stay outside the repository.

usage: add_ocr_pages.py --text <pages.ocr.txt> --doc-key JM_CAND-132 --id CAND-132 --pdf-sha256 <sha> --pages-total 186
                        --mean-confidence 93.7,95.5,89.3 --engine "tesseract 5.4.0" --units <dir> --out <new dir> --date <date>
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
from unitise import units_of  # noqa: E402


def main(argv=None):
    ap = argparse.ArgumentParser()
    for k in ("--text", "--doc-key", "--id", "--pdf-sha256", "--pages-total", "--mean-confidence", "--engine", "--units", "--out", "--date"):
        ap.add_argument(k, required=True)
    a = ap.parse_args(argv)
    if os.path.exists(a.out):
        raise SystemExit("--out must be a new directory")
    raw = open(a.text, encoding="utf-8").read()
    clean = re.sub(r"\n[ \t]*\n(?=[a-z])", "\n", raw)
    src = os.path.join(a.units, a.doc_key + ".units.csv")
    rows = list(csv.DictReader(open(src, encoding="utf-8")))
    have = {r["page"] for r in rows}
    U, np_ = units_of(clean, join_pages=False)
    clash = sorted({u[0] for u in U} & have)
    if clash:
        raise SystemExit(f"pages {clash} already have units")
    k0 = max(int(re.search(r":s(\d+)$", r["unit_id"]).group(1)) for r in rows)
    new = [{"unit_id": f"{a.doc_key}:p{n}:s{k0 + i}", "page": n, "para": pi, "n_words": len(s.split()), "text": s, "page_end": pe}
           for i, (n, pi, _, s, pe) in enumerate(U, 1)]
    allr = sorted(rows + new, key=lambda r: (int(r["page"]), int(re.search(r":s(\d+)$", r["unit_id"]).group(1))))
    shutil.copytree(a.units, a.out)
    f = os.path.join(a.out, a.doc_key + ".units.csv")
    with open(f, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, ["unit_id", "page", "para", "n_words", "text", "page_end"])
        w.writeheader()
        w.writerows({k: r.get(k, "") for k in w.fieldnames} for r in allr)
    mf = os.path.join(ROOT, "data/units", f"UNITS_MANIFEST_{a.date}.csv")
    if not os.path.exists(mf):
        mf_in = sorted(glob.glob(os.path.join(ROOT, "data/units/UNITS_MANIFEST_*.csv")))[-1]
    else:
        mf_in = mf
    nl = "\r\n" if b"\r\n" in open(mf_in, "rb").read() else "\n"
    rd = csv.DictReader(open(mf_in, encoding="utf-8"))
    man = list(rd)
    m = next(m for m in man if m["doc_key"] == a.doc_key)
    m.update(units=str(len(allr)), words=str(sum(len(r["text"].split()) for r in allr)), units_sha256=hashlib.sha256(open(f, "rb").read()).hexdigest(),
             text_mode="reading_order+ocr")
    with open(mf, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, rd.fieldnames, lineterminator=nl)
        w.writeheader()
        w.writerows(man)
    pages = sorted({u[0] for u in U}, key=int)
    conf = [float(c) for c in a.mean_confidence.split(",")]
    row = {"id": a.id, "pdf_sha256": a.pdf_sha256, "pages": a.pages_total, "pages_ocr": len(pages), "text_mode": "reading_order+ocr",
           "mean_confidence": round(sum(conf) / len(conf), 1), "pages_below_70": sum(c < 70 for c in conf), "words": len(re.sub(r"=== PAGE [\d.]+ ===", "", raw).split()),
           "layout": "auto", "text_sha256": hashlib.sha256(raw.encode("utf-8")).hexdigest(), "dpi": 300,
           "pages_ocred": " ".join(pages), "engine": a.engine}
    rec = os.path.join(ROOT, "data/manifest", f"OCR_{a.date}.csv")
    old = list(csv.DictReader(open(rec, encoding="utf-8"))) if os.path.exists(rec) else []
    cols = list(old[0].keys()) if old else []
    cols += [c for c in row if c not in cols]
    with open(rec, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, cols)
        w.writeheader()
        w.writerows([{c: r.get(c, "") for c in cols} for r in old if r["id"] != a.id] + [{c: row.get(c, "") for c in cols}])
    print(f"{a.doc_key}: {len(new)} new units on pages {pages} (s{k0 + 1} to s{k0 + len(new)}), {len(allr)} units in all")
    return new


if __name__ == "__main__":
    main()
