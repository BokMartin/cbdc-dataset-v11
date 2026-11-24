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

--layout blocks is for designed leaflets (the Jamaica FAQ: two-page spreads, a question column beside an answer column whose
left edge moves from question to question), where tesseract's own page segmentation reads across both columns. A page wider
than tall is cut into its two halves; each half is cut into horizontal bands at runs of blank rows, each band into a left and
a right part at its widest blank vertical gap; every part is read on its own (psm 6) and the parts follow in reading order
(top to bottom, left before right), separated by blank lines, so that a question comes before its answer.

usage: ocr_pdf.py --pdf <file.pdf> --id <document id> --out <dir> --date 2026-11-22 [--dpi 300] [--min-words 30] [--all-pages]
                  [--layout auto|blocks]
"""
import argparse
import csv
import hashlib
import json
import os
import re
import subprocess
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def text_layer(pdf, page):
    r = subprocess.run(["pdftotext", "-enc", "UTF-8", "-f", str(page), "-l", str(page), pdf, "-"], capture_output=True)
    return r.stdout.decode("utf-8", "replace")


def n_pages(pdf):
    info = subprocess.run(["pdfinfo", pdf], capture_output=True, text=True).stdout
    return int(next(l.split()[-1] for l in info.splitlines() if l.startswith("Pages:")))


# a bullet glyph that tesseract reads as a letter or a sign at the start of a line, before a capital: "e CBDC is", "¢ Transferring"
BULLET = re.compile(r"^(?:(?:e|¢e|¢«|¢|«|©|°)\s+|«)(?=[A-Z])", re.M)  # never "eNaira": a letter needs a space after it
# a capital I read as a vertical bar when it stands alone: "Can | accept", "| make"
PIPE_I = re.compile(r"(?<!\S)\|(?!\S)")


def tess(png, psm):
    """tesseract on one image: (text, word confidences)."""
    tsv = subprocess.run(["tesseract", png, "-", "-l", "eng", "--psm", str(psm), "tsv"], capture_output=True, text=True).stdout
    txt = subprocess.run(["tesseract", png, "-", "-l", "eng", "--psm", str(psm)], capture_output=True, text=True).stdout
    confs = []
    for line in tsv.splitlines()[1:]:
        f = line.split("\t")
        if len(f) == 12 and f[11].strip() and f[10] not in ("-1", ""):
            confs.append(float(f[10]))
    return txt, confs


def _runs(flags, minlen):
    """[(start, end)] of runs of True of at least minlen."""
    out, s = [], None
    for i, f in enumerate(list(flags) + [False]):
        if f and s is None:
            s = i
        elif not f and s is not None:
            if i - s >= minlen:
                out.append((s, i))
            s = None
    return out


def blocks(im, dpi, dark=160):
    """Boxes (x0, y0, x1, y1) of one page image in reading order (see --layout blocks)."""
    g = im.convert("L")
    w, h = g.size
    halves = [(0, w // 2), (w // 2, w)] if w > 1.2 * h else [(0, w)]
    px = g.load()
    boxes = []
    for x0, x1 in halves:
        step = max(1, dpi // 100)
        ink_row = [any(px[x, y] < dark for x in range(x0, x1, step)) for y in range(h)]
        blank = _runs([not r for r in ink_row], int(dpi * 0.2))
        edges = [0] + [(a + b) // 2 for a, b in blank] + [h]
        for y0, y1 in zip(edges, edges[1:]):
            if not any(ink_row[y0:y1]):
                continue
            ink_col = [any(px[x, y] < dark for y in range(y0, y1, step)) for x in range(x0, x1)]
            inked = [i for i, c in enumerate(ink_col) if c]
            lo, hi = inked[0], inked[-1]
            gaps = [(b - a, a, b) for a, b in _runs([not c for c in ink_col[lo:hi]], int(dpi * 0.13))]
            if gaps:
                _, a, b = max(gaps)
                cut = x0 + lo + (a + b) // 2
                boxes += [(x0, y0, cut, y1), (cut, y0, x1, y1)]
            else:
                boxes.append((x0, y0, x1, y1))
    return boxes


def ocr_page(pdf, page, dpi, tmp, layout="auto"):
    base = os.path.join(tmp, f"p{page}")
    subprocess.run(["pdftoppm", "-r", str(dpi), "-f", str(page), "-l", str(page), "-singlefile", "-png", pdf, base], check=True)
    dropped = []
    if layout == "auto":
        txt, confs = tess(base + ".png", 3)
    else:
        from PIL import Image, ImageOps
        im = Image.open(base + ".png")
        parts, confs = [], []
        for i, box in enumerate(blocks(im, dpi)):
            crop = os.path.join(tmp, f"p{page}_{i}.png")
            ImageOps.expand(im.crop(box), border=dpi // 10, fill="white").save(crop)
            t, c = tess(crop, 6)
            if not t.strip():
                continue
            if len(t.split()) <= 15 and (not c or sum(c) / len(c) < 75):
                dropped.append(len(t.split()))
                continue  # a logo, an emblem or a cover read as letters ("tu. f° C %"): dropped, never mixed into the text
            # one part is one block of the layout: tesseract's blank lines inside it are not paragraph breaks; a bullet starts one
            t = PIPE_I.sub("I", BULLET.sub("• ", "\n".join(l for l in t.strip().splitlines() if l.strip())))
            parts.append(re.sub(r"\n(?=• )", "\n\n", t))
            confs += c
        txt = "\n\n".join(parts) + "\n"
    return txt, (round(sum(confs) / len(confs), 1) if confs else None), dropped


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--pdf", required=True)
    ap.add_argument("--id", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--date", required=True)
    ap.add_argument("--dpi", type=int, default=300)
    ap.add_argument("--min-words", type=int, default=30)
    ap.add_argument("--all-pages", action="store_true")
    ap.add_argument("--layout", choices=["auto", "blocks"], default="auto")
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
            txt, conf, dropped = ocr_page(a.pdf, p, a.dpi, tmp, a.layout)
            parts.append((p, txt))
            pages.append({"page": p, "source": "ocr", "words": len(txt.split()), "confidence": conf,
                          "parts_dropped_words": dropped})
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
           "words": sum(x["words"] for x in pages), "layout": a.layout, "text_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(), "dpi": a.dpi}
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
