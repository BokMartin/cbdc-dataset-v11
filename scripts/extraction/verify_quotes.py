#!/usr/bin/env python3
"""Mechanical citation check for a FILL.csv (or stage1_findings.csv): is the quote an exact (whitespace-normalised,
case-insensitive) substring of the cited document page (±1 page)? Adds columns quote_verified (exact_page / adjacent_page /
elsewhere_in_doc / NOT_FOUND / empty) and writes <file>.verified.csv. Exit code 0 always; the column is the result."""
import csv, os, re, sys

def norm(s): return re.sub(r"\s+", " ", (s or "")).strip().lower().replace("’", "'").replace("“", '"').replace("”", '"').replace("–", "-").replace("—", "-")

def load_pages(path):
    txt = open(path, encoding="utf-8", errors="replace").read()
    pages = {}
    for m in re.finditer(r"=== DOC \d+ PAGE (\d+) ===\n(.*?)(?==== DOC \d+ PAGE \d+ ===|\Z)", txt, re.S):
        pages[int(m.group(1))] = norm(m.group(2))
    return pages

def main(fill, indir):
    docs = {int(r["doc"]): r for r in csv.DictReader(open(os.path.join(indir, "DOCS.csv"), encoding="utf-8"))}
    cache = {}
    rows = list(csv.DictReader(open(fill, encoding="utf-8")))
    out = []
    for r in rows:
        q = norm(r.get("quote", "")); res = "empty"
        if q:
            try:
                d = int(float(r["doc"])); p = int(float(r["page"])) if r.get("page") not in ("", None) else None
                f = docs[d]["file"]; f = f if os.path.exists(f) else os.path.join(indir, "texts", os.path.basename(f))
                pages = cache.setdefault(d, load_pages(f))
                core = q[:200]
                if p is not None and p in pages and core in pages[p]: res = "exact_page"
                elif p is not None and any(core in pages.get(x, "") for x in (p-1, p+1)): res = "adjacent_page"
                elif any(core in t for t in pages.values()): res = "elsewhere_in_doc"
                else:
                    # tolerate OCR/hyphenation: try first 12 words
                    w = " ".join(q.split()[:12])
                    res = "elsewhere_in_doc(prefix)" if any(w in t for t in pages.values()) else "NOT_FOUND"
            except Exception as e: res = f"error:{e}"
        r["quote_verified"] = res; out.append(r)
    o = fill.replace(".csv", ".verified.csv")
    with open(o, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0].keys())); w.writeheader(); w.writerows(out)
    from collections import Counter
    print(o, dict(Counter(r["quote_verified"] for r in out)))

if __name__ == "__main__": main(sys.argv[1], sys.argv[2])
