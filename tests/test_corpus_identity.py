"""Input identity of the current corpus (audit A4 of 17 Nov 2026, F03 and F09). Runs on the committed manifests, no source text needed."""
import collections, csv, glob, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
latest = lambda pat: sorted(glob.glob(os.path.join(ROOT, pat)))[-1]
rd = lambda p: list(csv.DictReader(open(p, encoding="utf-8")))


def test_no_two_documents_share_one_text():
    c = collections.Counter(r["text_sha256"] for r in rd(latest("data/units/UNITS_MANIFEST_*.csv")))
    assert [h for h, n in c.items() if n > 1] == []


def test_document_header_comes_from_the_issuer_ledger():
    led = {r["id"]: r for r in rd(latest("data/manifest/ISSUERS_2*.csv"))}
    bad = [r["id"] for r in rd(latest("data/units/UNITS_MANIFEST_*.csv")) if any(r[k] != led[r["id"]][k] for k in ("issuer", "issuer_type", "kind"))]
    assert bad == []


def test_candidates_and_manifest_list_the_same_documents():
    assert {r["doc_key"] for r in rd(latest("data/units/UNITS_MANIFEST_*.csv"))} == {r["doc_key"] for r in rd(latest("data/units/CANDIDATES_*.csv"))}
