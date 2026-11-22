"""The unit manifest marks the INCLINED documents (ADR-010 draft) as their own stratum before any sample is drawn
(V5 (f) of the 22 Nov check), and the mark agrees with the corpus document list."""
import csv
import glob
import os

ROOT = os.path.join(os.path.dirname(__file__), "..")


def _latest(pat):
    return sorted(glob.glob(os.path.join(ROOT, pat)))[-1]


def test_inclined_stratum_matches_the_corpus_list():
    units = list(csv.DictReader(open(_latest("data/units/UNITS_MANIFEST_*.csv"), encoding="utf-8")))
    docs = {r["id"]: r["decision"] for r in csv.DictReader(open(_latest("data/manifest/CORPUS_DOCUMENTS_*.csv"), encoding="utf-8"))}
    assert all(u["stratum"] in ("evidence", "inclined") for u in units)
    assert {u["id"] for u in units if u["stratum"] == "inclined"} == {i for i, d in docs.items() if d == "INCLINED"}
    assert all(bool(u["inclined_group"]) == (u["stratum"] == "inclined") for u in units)
