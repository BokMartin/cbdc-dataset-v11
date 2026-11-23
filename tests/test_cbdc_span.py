import csv
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts", "extraction"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts", "pipeline"))
import cbdc_span  # noqa: E402
import build_jobs  # noqa: E402


def _units(d, key, pages):
    with open(os.path.join(d, key + ".units.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh); w.writerow(["unit_id", "page", "para", "n_words", "text", "page_end"])
        for i, (p, t) in enumerate(pages, 1): w.writerow([f"{key}:p{p}:s{i}", p, 1, len(t.split()), t, p])


def test_span_of_general_publication(tmp_path):
    body = [(p, "Inflation remained within the target range this year.") for p in range(1, 11)]
    body[4] = (5, "The Bank continued its work on a central bank digital currency pilot.")
    _units(tmp_path, "A", body); _units(tmp_path, "B", body)
    man = [{"doc_key": "A", "kind": "annual_report"}, {"doc_key": "B", "kind": "other"}]
    rows = cbdc_span.spans(str(tmp_path), man)
    assert rows == [{"doc_key": "A", "page_span": "cbdc_span", "span_pages": "4 5 6", "pages_with_text": 10, "span_share_chars": rows[0]["span_share_chars"], "terms_pages": 1}]
    m = {"doc_key": "A", "pages": "10", "project": "X", "issuer": "i", "issuer_type": "central_bank", "year": "2025", "kind": "annual_report",
         "route": "A", "text_mode": "reading_order"}
    units = build_jobs.load_units(os.path.join(tmp_path, "A.units.csv"))
    reqs = build_jobs.extraction_requests(units, m, 60000, rows[0])
    assert len(reqs) == 1 and "page_span: cbdc_span" in reqs[0][2] and "page_indices: [4, 5, 6]" in reqs[0][2]
    whole = build_jobs.extraction_requests(units, m, 60000, {})
    assert "page_indices: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]" in whole[0][2]
