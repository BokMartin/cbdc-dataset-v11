#!/usr/bin/env python3
"""Page-delimited text from a PDF, in the format every pipeline stage expects:

    ### DOC <n> | <doc_id> | <title> | year <y> | core: <verdict> | staff_research: <flag> | kind: <kind> | lang: <lang>
    (blank)
    === DOC <n> PAGE 1 ===
    <pdftotext -layout output of page 1>
    === DOC <n> PAGE 2 ===
    ...

Page p is the PDF page index (1-based), never the printed label. Pages with no text layer are OCR'd with tesseract when
--ocr is given (language code per --ocr-lang). The SHA-256 of the PDF is printed so the registry row can be verified.

usage: pdf_to_pages.py --pdf file.pdf --doc 1 --doc-id ID --title T --year 2018 --core KEEP --kind other --lang en --out texts/NO/texts/doc01.txt [--ocr --ocr-lang eng]
"""
import argparse, hashlib, os, subprocess, sys, tempfile


def n_pages(pdf):
    out = subprocess.run(["pdfinfo", pdf], capture_output=True, text=True).stdout
    for line in out.splitlines():
        if line.startswith("Pages:"): return int(line.split()[1])
    raise RuntimeError("pdfinfo failed")


def page_text(pdf, p):
    return subprocess.run(["pdftotext", "-layout", "-f", str(p), "-l", str(p), pdf, "-"], capture_output=True, text=True).stdout


def ocr_page(pdf, p, lang):
    with tempfile.TemporaryDirectory() as d:
        subprocess.run(["pdftoppm", "-r", "300", "-f", str(p), "-l", str(p), "-png", pdf, os.path.join(d, "pg")], check=True)
        png = [f for f in os.listdir(d) if f.endswith(".png")][0]
        return subprocess.run(["tesseract", os.path.join(d, png), "-", "-l", lang], capture_output=True, text=True).stdout


def main():
    ap = argparse.ArgumentParser()
    for k in ("pdf", "doc", "doc_id", "title", "year", "out"): ap.add_argument("--" + k.replace("_", "-"), required=True)
    ap.add_argument("--core", default=""); ap.add_argument("--staff", default=""); ap.add_argument("--kind", default=""); ap.add_argument("--lang", default="")
    ap.add_argument("--ocr", action="store_true"); ap.add_argument("--ocr-lang", default="eng")
    a = ap.parse_args(); N = n_pages(a.pdf); parts = [f"### DOC {a.doc} | {a.doc_id} | {a.title} | year {a.year} | core: {a.core} | staff_research: {a.staff} | kind: {a.kind} | lang: {a.lang}\n\n"]
    ocr_pages = 0
    for p in range(1, N + 1):
        t = page_text(a.pdf, p)
        if a.ocr and len(t.strip()) < 20: t = ocr_page(a.pdf, p, a.ocr_lang); ocr_pages += 1
        parts.append(f"=== DOC {a.doc} PAGE {p} ===\n{t}\n")
    os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True); open(a.out, "w", encoding="utf-8").write("".join(parts))
    sha = hashlib.sha256(open(a.pdf, "rb").read()).hexdigest(); chars = sum(len(x) for x in parts)
    print(f"{a.out}: {N} pages, {chars} chars, ocr_pages={ocr_pages}, pdf_sha256={sha}")


if __name__ == "__main__": main()
