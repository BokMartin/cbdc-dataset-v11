"""Results on the website (ADR-019): status and provenance on every results file, short quotations only."""
import json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
A = os.path.join(ROOT, "site", "assets")
FILES = ("results.json", "cell_history.json", "pets.json", "paragraphs.json")


def load(n):
    with open(os.path.join(A, n), encoding="utf-8") as f:
        return json.load(f)


def quotes(o):
    if isinstance(o, dict):
        for k, v in o.items():
            if k in ("q", "fn") and isinstance(v, str):
                yield v
            else:
                yield from quotes(v)
    elif isinstance(o, list):
        for v in o:
            yield from quotes(v)


def test_every_results_file_has_status_and_provenance():
    for n in FILES:
        m = load(n)["meta"]
        assert m["status"] and m["inputs"] and m["sources"].get("freeze"), n


def test_quotations_are_short():
    for n in FILES:
        m = load(n)["meta"]["quote_max"]
        for q in quotes(load(n)):
            assert len(q) <= m + 2, (n, q[:60])


def test_index_definition_and_hypothesis():
    r = load("results.json")
    assert r["meta"]["cells7"] == ["F1", "F2", "F4", "F7", "F8", "F9", "F10"]
    for rule, h in r["hypothesis"].items():
        assert h["n"] == 16 and h["L"] <= h["U"]
        assert h["verdict"] == ("holds" if h["L"] >= 9 else "fails" if h["U"] <= 8 else "inconclusive")
    for p in r["projects"]:
        for k in ("prov", "strict", "prov4"):
            lo, hi = p["index"][k]
            assert 0 <= lo <= hi <= 1


def test_results_pages_show_the_status_banner():
    for page in ("results.html", "cells.html", "pets.html", "paragraphs.html", "map.html"):
        s = open(os.path.join(ROOT, "site", page), encoding="utf-8").read()
        assert 'id="prelim"' in s, page
