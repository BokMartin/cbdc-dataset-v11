#!/usr/bin/env python3
"""Add OCR text of text in images (diagrams, charts, scanned inserts) to documents that are already unitised (MB, 23 Nov 2026:
"předpřiprav všechny dokumenty které půjdou do finální extrakce jako jamajské FAQ ... ať tenhle problém vyřešíme před finální
extrakcí"). In the development round Claude marked pages that carry only the title of a diagram as unreadable, so the whole
request failed; the text of the image is now added to such pages.

Input (made on MB's computer, tesseract, eng, words not corrected):
  --text   the OCR text, one block per page: `=== <pdf> PAGE <n> (mean confidence <c>; verdict <v>; lang <l>) ===`
  --check  the page check (pdf, page, text_layer_words, ocr_words, mean_conf, lang, flag, verdict, note): every page that was
           OCR'd, flag IMAGE_TEXT where OCR adds 25 or more words over the text layer; the verdict of a reader of the OCR text
           (ok, partial = chart or table, labels readable; garbage; not_content)
  --list   data/manifest/OCR_PAGE_LIST_<date>.csv: doc_key, route, pdf, pdf_sha256, pages (the pages that were OCR'd)
Only pages with verdict ok or partial are added. Each page is cut by unitise.units_of() without joining across pages. A unit is
dropped as noise if it has fewer than 3 words of at least 3 letters or if such words are under 40 % of its tokens (axis labels,
broken glyphs), and as a duplicate if its text (letters and digits only, lower case) is already in the text layer of the page.
The new units are numbered after the highest unit number of the document, so no existing unit id changes; their paragraph
numbers follow the highest paragraph of the page, so they form their own blocks after the text layer of the page and never join
a paragraph of the text layer (the neighbour stratum N of select_candidates.py is unchanged for existing units).

Output: --out (a new directory) is a copy of --units with the changed documents rewritten; data/units/UNITS_MANIFEST_<date>.csv
(latest manifest with units, words, units_sha256 of the changed documents and text_mode `+ocr`); data/manifest/
OCR_IMAGE_PAGES_<date>.csv, one row per OCR'd page with its verdict, what was added or dropped and the hash of its OCR text.
Unit texts stay outside the repository. Candidates are rebuilt afterwards by select_candidates.py.

usage: add_image_text.py --text _OCR_IMAGE_TEXT.txt --check _OCR_CHECK.csv --list data/manifest/OCR_PAGE_LIST_2026-11-23.csv
                         --units <dir> --out <new dir> --date 2026-11-23b --engine "tesseract 5.4.0, eng, psm 3, MB's computer"
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

HEAD = re.compile(r"^=== (.+?) PAGE (\d+) \(mean confidence ([\d.]+); verdict (\w+); lang ([\w+]+)\) ===$", re.M)
WORD = re.compile(r"^[A-Za-z][A-Za-z'’\-]{2,}[.,;:)]*$")
KEEP = ("ok", "partial")


def norm(s):
    return re.sub(r"[^a-z0-9]+", "", s.lower())


def noise(s):
    toks = s.split(); w = sum(bool(WORD.match(t)) for t in toks)
    return w < 3 or w < 0.4 * len(toks)


def blocks(raw):
    hs = list(HEAD.finditer(raw)); out = []
    for i, h in enumerate(hs):
        body = raw[h.end(): hs[i + 1].start() if i + 1 < len(hs) else len(raw)].strip("\n")
        out.append({"pdf": h.group(1), "page": h.group(2), "conf": h.group(3), "verdict": h.group(4), "lang": h.group(5), "text": body})
    return out


def sid(r):
    return int(re.search(r":s(\d+)$", r["unit_id"]).group(1))


def main(argv=None):
    ap = argparse.ArgumentParser()
    for k in ("--text", "--check", "--list", "--units", "--out", "--date", "--engine"):
        ap.add_argument(k, required=True)
    a = ap.parse_args(argv)
    if os.path.exists(a.out):
        raise SystemExit("--out must be a new directory")
    raw = open(a.text, encoding="utf-8").read()
    lst = {r["pdf"]: r for r in csv.DictReader(open(a.list, encoding="utf-8"))}
    check = {(r["pdf"], r["page"]): r for r in csv.DictReader(open(a.check, encoding="utf-8"))}
    B = blocks(raw)
    for b in B:
        if b["pdf"] not in lst or (b["pdf"], b["page"]) not in check:
            raise SystemExit(f"{b['pdf']} page {b['page']} is not in the page list or the check")
    shutil.copytree(a.units, a.out)
    rec, changed = [], {}
    for b in B:
        if b["verdict"] not in KEEP:
            continue
        key = lst[b["pdf"]]["doc_key"]
        if key not in changed:
            changed[key] = list(csv.DictReader(open(os.path.join(a.units, key + ".units.csv"), encoding="utf-8")))
        rows = changed[key]
        k0 = max(sid(r) for r in rows)
        page_rows = [r for r in rows if r["page"] == b["page"]]
        p0 = max([int(r["para"]) for r in page_rows] or [0])
        have = norm(" ".join(r["text"] for r in page_rows))
        text = re.sub(r"\n[ \t]*\n(?=[a-z])", "\n", b["text"])
        U, _ = units_of(f"=== PAGE {b['page']} ===\n" + text, join_pages=False)
        new, n_noise, n_dup = [], 0, 0
        for n, pi, _, s, pe in U:
            if noise(s): n_noise += 1; continue
            if norm(s) and norm(s) in have: n_dup += 1; continue
            new.append({"unit_id": f"{key}:p{n}:s{k0 + len(new) + 1}", "page": n, "para": str(p0 + pi), "n_words": str(len(s.split())), "text": s, "page_end": n})
        rows.extend(new)
        rec.append({"doc_key": key, "pdf": b["pdf"], "pdf_sha256": lst[b["pdf"]]["pdf_sha256"], "page": b["page"], "mean_confidence": b["conf"],
                    "verdict": b["verdict"], "lang": b["lang"], "text_layer_words": check[(b["pdf"], b["page"])]["text_layer_words"],
                    "ocr_words": check[(b["pdf"], b["page"])]["ocr_words"], "units_added": len(new), "units_dropped_noise": n_noise,
                    "units_dropped_duplicate": n_dup, "first_unit": new[0]["unit_id"] if new else "", "last_unit": new[-1]["unit_id"] if new else "",
                    "words_added": sum(int(u["n_words"]) for u in new), "ocr_text_sha256": hashlib.sha256(b["text"].encode("utf-8")).hexdigest(),
                    "engine": a.engine})
    for b in B:   # pages OCR'd and not added (garbage, not_content) are recorded too
        if b["verdict"] not in KEEP:
            rec.append({"doc_key": lst[b["pdf"]]["doc_key"], "pdf": b["pdf"], "pdf_sha256": lst[b["pdf"]]["pdf_sha256"], "page": b["page"],
                        "mean_confidence": b["conf"], "verdict": b["verdict"], "lang": b["lang"],
                        "text_layer_words": check[(b["pdf"], b["page"])]["text_layer_words"], "ocr_words": check[(b["pdf"], b["page"])]["ocr_words"],
                        "units_added": 0, "units_dropped_noise": "", "units_dropped_duplicate": "", "first_unit": "", "last_unit": "", "words_added": 0,
                        "ocr_text_sha256": hashlib.sha256(b["text"].encode("utf-8")).hexdigest(), "engine": a.engine})
    shas = {}
    for key, rows in changed.items():
        rows.sort(key=lambda r: (int(r["page"]), sid(r)))
        f = os.path.join(a.out, key + ".units.csv")
        with open(f, "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, ["unit_id", "page", "para", "n_words", "text", "page_end"])
            w.writeheader()
            w.writerows({k: r.get(k, "") for k in w.fieldnames} for r in rows)
        shas[key] = hashlib.sha256(open(f, "rb").read()).hexdigest()
    mf_in = [f for f in sorted(glob.glob(os.path.join(ROOT, "data/units/UNITS_MANIFEST_*.csv"))) if os.path.basename(f) != f"UNITS_MANIFEST_{a.date}.csv"][-1]
    nl = "\r\n" if b"\r\n" in open(mf_in, "rb").read() else "\n"
    rd = csv.DictReader(open(mf_in, encoding="utf-8")); man = list(rd)
    for m in man:
        if m["doc_key"] in changed:
            rows = changed[m["doc_key"]]
            m.update(units=str(len(rows)), words=str(sum(len(r["text"].split()) for r in rows)), units_sha256=shas[m["doc_key"]],
                     text_mode=m["text_mode"] if "ocr" in m["text_mode"] else m["text_mode"] + "+ocr")
    with open(os.path.join(ROOT, "data/units", f"UNITS_MANIFEST_{a.date}.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, rd.fieldnames, lineterminator=nl); w.writeheader(); w.writerows(man)
    rec.sort(key=lambda r: (r["doc_key"], int(r["page"])))
    with open(os.path.join(ROOT, "data/manifest", f"OCR_IMAGE_PAGES_{a.date}.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, list(rec[0])); w.writeheader(); w.writerows(rec)
    added = sum(r["units_added"] for r in rec)
    print(f"{len(changed)} documents changed, {sum(r['units_added'] > 0 for r in rec)} pages with new units, {added} units, "
          f"{sum(r['words_added'] for r in rec)} words; manifest from {os.path.basename(mf_in)}")
    return rec


if __name__ == "__main__":
    main()
