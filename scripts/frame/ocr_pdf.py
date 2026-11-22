#!/usr/bin/env python3
"""Local OCR of scanned PDF pages (MB, 22 Nov 2026: the Jamaica FAQ booklet is a scan and Jamaica is a core project).

No paid service: pdftoppm renders each page at --dpi, tesseract (eng) reads it. A page that already has a text layer of
at least --min-words words keeps that text (never mixed with OCR on the same page); --all-pages forces OCR everywhere.
Output, outside the repository (issuers' copyright): <out>/<sha256>.ocr.txt with the same page markers as the text
caches (`=== PAGE n ===`), ready for scripts/units/unitise.units_of(), and <out>/<sha256>.ocr.json with, per page, the
source (text_layer / ocr), the word count and tesseract's mean word confidence. Repository: data/manifest/OCR_<date>.csv,
one row per document (id, PDF SHA-256, pages, pages OCRed, mean confidence, pages with confidence below 70, SHA-256 of
the text). The text route of the document does not change (an English original stays route A); its text mode becomes
`ocr_tesseract` (or `reading_order+ocr` for mixed documents) so that OCR text can always be told apart.

usage: ocr_pdf.py --pdf <file.pdf> --id <document id> --out <dir> --date 2026-11-22 [--dpi 300] [--min-words 30] [--all-pages]
"""
import argparse
import csv
import hashlib
import json
import os
import subprocess
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def text_layer(pdf, page):
    r = subprocess.run(["pdftotext", "-enc", "UTF-8", "-f", str(page), "-l", str(page), pdf, "-"], capture_output=True)
    return r.stdout.decode("utf-8", "replace")


def n_pages(pdf):
    info = subprocess.run(["pdfinfo", pdf], capture_output=True, text=True).stdout
    return int(next(l.split()[-1] for l in info.splitlines() if l.startswith("Pages:")))


def ocr_page(pdf, page, dpi, tmp):
    base = os.path.join(tmp, f"p{page}")
    subprocess.run(["pdftoppm", "-r", str(dpi), "-f", str(page), "-l", str(page), "-singlefile", "-png", pdf, base], check=True)
    tsv = subprocess.run(["tesseract", base + ".png", "-", "-l", "eng", "--psm", "3", "tsv"], capture_output=True, text=True).stdout
    txt = subprocess.run(["tesseract", base + ".png", "-", "-l", "eng", "--psm", "3"], capture_output=True, text=True).stdout
    confs = []
    for line in tsv.splitlines()[1:]:
        f = line.split("\t")
        if len(f) == 12 and f[11].strip() and f[10] not in ("-1", ""):
            confs.append(float(f[10]))
    return txt, (round(sum(confs) / len(confs), 1) if confs else None)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--pdf", required=True)
    ap.add_argument("--id", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--date", required=True)
    ap.add_argument("--dpi", type=int, default=300)
    ap.add_argument("--min-words", type=int, default=30)
    ap.add_argument("--all-pages", action="store_true")
    a = ap.parse_args(argv)
    sha = hashlib.sha256(open(a.pdf, "rb").read()).hexdigest()
    os.makedirs(a.out, exist_ok=True)
    pages, parts = [], []
    with tempfile.TemporaryDirectory() as tmp:
        for p in range(1, n_pages(a.pdf) + 1):
            layer = text_layer(a.pdf, p)
            if not a.all_pages and len(layer.split()) >= a.min_words:
                parts.append((p, layer))
                pages.append({"page": p, "source": "text_layer", "words": len(layer.split()), "confidence": None})
                continue
            txt, conf = ocr_page(a.pdf, p, a.dpi, tmp)
            parts.append((p, txt))
            pages.append({"page": p, "source": "ocr", "words": len(txt.split()), "confidence": conf})
    text = "".join(f"=== PAGE {p} ===\n{t.rstrip()}\n" for p, t in parts)
    tf = os.path.join(a.out, f"{sha}.ocr.txt")
    open(tf, "w", encoding="utf-8").write(text)
    json.dump({"id": a.id, "pdf_sha256": sha, "dpi": a.dpi, "engine": subprocess.run(["tesseract", "--version"], capture_output=True, text=True).stdout.split("\n")[0],
               "pages": pages}, open(os.path.join(a.out, f"{sha}.ocr.json"), "w"), indent=1)
    ocr = [x for x in pages if x["source"] == "ocr"]
    conf = [x["confidence"] for x in ocr if x["confidence"] is not None]
    row = {"id": a.id, "pdf_sha256": sha, "pages": len(pages), "pages_ocr": len(ocr),
           "text_mode": "ocr_tesseract" if len(ocr) == len(pages) else ("reading_order+ocr" if ocr else "reading_order"),
           "mean_confidence": round(sum(conf) / len(conf), 1) if conf else "", "pages_below_70": sum(c < 70 for c in conf),
           "words": sum(x["words"] for x in pages), "text_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(), "dpi": a.dpi}
    rec = os.path.join(ROOT, "data/manifest", f"OCR_{a.date}.csv")
    rows = [r for r in (csv.DictReader(open(rec, encoding="utf-8")) if os.path.exists(rec) else []) if r["id"] != a.id] + [row]
    with open(rec, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, list(row))
        w.writeheader()
        w.writerows(rows)
    print(json.dumps(row, indent=1))
    return row


if __name__ == "__main__":
    main()
