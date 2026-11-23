#!/usr/bin/env python3
"""Page spans of general publications for extraction (ADR-006 B.5; ADR-013 P3, adopted by MB for both authors 23 Nov 2026:
"keep the window of CBDC pages ±1 as the initial search; follow explicit references").

A general publication is a document of kind annual_report, research_general or strategy (the kinds of the unit manifest that
are not about the CBDC as such; kind `other` holds CBDC reports too, e.g. the Icelandic Rafkróna report and the JAM-DEX wallet
privacy policy, so it is always sent whole). Its span is every page whose units mention a CBDC term (TERMS below), with one
page on either side. If the span holds 90 % or more of the characters, the document stays `whole_document`. Explicit references from a span page
to pages outside it are kept by the model in `references` (prompt v12.2 §1, "the runner resolves those references against
eligible material"); they are resolved after the extraction run, not here.

Output (no unit text): data/manifest/EXTRACTION_HEADER_EXTRA_<date>.csv with doc_key, page_span, span_pages (space-separated),
pages_with_text, span_share_chars, terms_pages; build_jobs.py --header-extra reads it and sends only the span pages.

usage: cbdc_span.py --units <units dir> --date 2026-11-23b
"""
import argparse
import collections
import csv
import glob
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
GENERAL = ("annual_report", "research_general", "strategy")
WHOLE_AT = 0.9
TERMS = re.compile(r"\b(CBDCs?|central[- ]bank digital (currenc\w+|money)|digital (euro|pound|krone|krona|rupee|rupiah|dirham|yen|shekel|tenge|"
                   r"ruble|rouble|baht|naira|ngultrum|florin|dollar|rand|won|peso|currenc\w+|cash|money)|e-?krona|e-?krone|e-?CNY|e-?HKD|e-?Rupee|"
                   r"e-?Naira|JAM-?DEX|Sand Dollar|DCash|Bakong|tokeni[sz]ed (money|cash|deposits?)|retail token)\b", re.I)


def spans(units_dir, manifest):
    out = []
    for m in manifest:
        if m["kind"] not in GENERAL:
            continue
        pages = collections.defaultdict(str)
        for u in csv.DictReader(open(os.path.join(units_dir, m["doc_key"] + ".units.csv"), encoding="utf-8")):
            pages[int(u["page"])] += " " + u["text"]
        hit = sorted(p for p, t in pages.items() if TERMS.search(t))
        span = sorted({q for p in hit for q in (p - 1, p, p + 1) if q in pages})
        share = sum(len(pages[p]) for p in span) / max(1, sum(len(t) for t in pages.values()))
        whole = share >= WHOLE_AT
        out.append({"doc_key": m["doc_key"], "page_span": "whole_document" if whole else "cbdc_span", "span_pages": "" if whole else " ".join(map(str, span)),
                    "pages_with_text": len(pages), "span_share_chars": round(share, 3), "terms_pages": len(hit)})
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(); ap.add_argument("--units", required=True); ap.add_argument("--date", required=True)
    a = ap.parse_args(argv)
    mf = sorted(glob.glob(os.path.join(ROOT, "data/units/UNITS_MANIFEST_*.csv")))[-1]
    rows = spans(a.units, list(csv.DictReader(open(mf, encoding="utf-8"))))
    p = os.path.join(ROOT, "data/manifest", f"EXTRACTION_HEADER_EXTRA_{a.date}.csv")
    with open(p, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, ["doc_key", "page_span", "span_pages", "pages_with_text", "span_share_chars", "terms_pages"]); w.writeheader(); w.writerows(rows)
    n = [r for r in rows if r["page_span"] == "cbdc_span"]
    print(f"{len(rows)} general publications, {len(n)} cut to a CBDC span; manifest {os.path.basename(mf)} -> {os.path.relpath(p, ROOT)}")
    return rows


if __name__ == "__main__":
    main()
