#!/usr/bin/env python3
"""Mechanical citation check, v2 (ADR-001 E17 / UK12): is the FULL normalised quotation present in the cited document, on the
cited page, spanning into a neighbouring page, elsewhere in the document, or only as a fuzzy candidate?

States written to `quote_verified` (and `quote_match_ratio`):
  exact_page           full normalised quote found on the cited page
  spanning_pages       found only in the concatenation of the cited page with the next or previous page (page break inside the quote)
  elsewhere_in_doc     found in the document but not at the cited page (locator wrong) — must be corrected before release
  fuzzy_candidate      best fuzzy match ratio >= 0.90 but not exact (OCR noise, hyphenation, furniture) — requires human resolution
  invalid              nothing above; the citation does not support the claim as quoted
  empty                no quote given (allowed only when value is n/d)
  error:<...>          unreadable doc/page fields
A prefix match is never accepted (v1 accepted the first 200 characters, which let a reversed final clause pass).
Page furniture: lines that repeat on >= 50% of pages (running heads, page numbers) are removed before matching; the
removal is logged in `quote_furniture_removed` for the reader.

usage: verify_quotes.py FILL.csv <folder with DOCS.csv and texts/docNN.txt>   → writes FILL.verified.csv
"""
import csv, os, re, sys, difflib
from collections import Counter

def norm(s):
    s = (s or "").replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"').replace("–", "-").replace("—", "-").replace("­", "")
    s = re.sub(r"-\n\s*", "", s)            # hyphenation at line end
    return re.sub(r"\s+", " ", s).strip().lower()

def load_pages(path):
    txt = open(path, encoding="utf-8", errors="replace").read()
    raw = {int(m.group(1)): m.group(2) for m in re.finditer(r"=== DOC \d+ PAGE (\d+) ===\n(.*?)(?==== DOC \d+ PAGE \d+ ===|\Z)", txt, re.S)}
    # page furniture: short lines repeated on at least half of the pages
    lines = Counter()
    for t in raw.values():
        for ln in {l.strip() for l in t.split("\n") if 0 < len(l.strip()) <= 80}: lines[ln] += 1
    furniture = {l for l, c in lines.items() if len(raw) >= 4 and c >= 0.5 * len(raw)}
    pages = {p: norm("\n".join(l for l in t.split("\n") if l.strip() not in furniture)) for p, t in raw.items()}
    return pages, furniture

def check(q, pages, p):
    """Return (state, ratio)."""
    if not q: return "empty", 1.0
    if p is not None and p in pages and q in pages[p]: return "exact_page", 1.0
    if any(q in t for t in pages.values()): return "elsewhere_in_doc", 1.0   # whole quote on one page, but not the cited one
    if p is not None:  # genuinely crossing a page break next to the cited page
        for a, b in ((p, p + 1), (p - 1, p)):
            if a in pages and b in pages and q in (pages[a] + " " + pages[b]): return "spanning_pages", 1.0
    # fuzzy candidate: best window on the cited page (or any page), ratio over normalised text
    best = 0.0
    cand = [pages[p]] if (p is not None and p in pages) else list(pages.values())
    for t in cand:
        if not t: continue
        sm = difflib.SequenceMatcher(None, q, t, autojunk=False)
        m = sm.find_longest_match(0, len(q), 0, len(t))
        if m.size == 0: continue
        start = max(0, m.b - (m.a)); window = t[start:start + len(q) + 20]
        best = max(best, difflib.SequenceMatcher(None, q, window, autojunk=False).ratio())
    return ("fuzzy_candidate" if best >= 0.90 else "invalid"), round(best, 3)

def main(fill, indir):
    docs = {int(r["doc"]): r for r in csv.DictReader(open(os.path.join(indir, "DOCS.csv"), encoding="utf-8"))}
    cache = {}; rows = list(csv.DictReader(open(fill, encoding="utf-8"))); out = []
    for r in rows:
        q = norm(r.get("quote", "")); state, ratio, furn = "empty", 1.0, ""
        if q:
            try:
                d = int(float(r["doc"])); p = int(float(r["page"])) if str(r.get("page", "")).strip() not in ("", "n/d", "nan") else None
                f = docs[d]["file"]; f = f if os.path.exists(f) else os.path.join(indir, "texts", os.path.basename(f))
                if d not in cache: cache[d] = load_pages(f)
                pages, furniture = cache[d]; state, ratio = check(q, pages, p); furn = str(len(furniture))
            except Exception as e: state, ratio = ("invalid_locator" if str(r.get("doc","")).strip().lower() in ("", "n/d") else f"error:{e}"), 0.0
        elif str(r.get("value", "")).strip().lower() not in ("n/d", "unknown", ""): state = "empty_but_value_set"
        r["quote_verified"] = state; r["quote_match_ratio"] = ratio; r["quote_furniture_removed"] = furn; out.append(r)
    o = fill.replace(".csv", ".verified.csv")
    with open(o, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0].keys())); w.writeheader(); w.writerows(out)
    print(o, dict(Counter(r["quote_verified"] for r in out)))

if __name__ == "__main__": main(sys.argv[1], sys.argv[2])
