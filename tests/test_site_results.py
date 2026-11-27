"""Results on the website (ADR-019): status and provenance on every results file, short quotations only, and no model
value of the projects the authors are verifying (MB, 27 Nov 2026, after audit A6 §13)."""
import json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
A = os.path.join(ROOT, "site", "assets")
FILES = ("results.json", "cell_history.json", "pets.json", "paragraphs.json")
# Withheld until the authors' verification ends; a change here needs MB's decision.
UNDER_VERIFICATION = {"AU", "BS", "CA", "EU", "HK", "IL", "IN", "JM", "JP", "KZ", "NZ", "RU", "SE", "TW"}


def load(n):
    with open(os.path.join(A, n), encoding="utf-8") as f:
        return json.load(f)


def quotes(o):
    if isinstance(o, dict):
        for k, v in o.items():
            if k in ("q", "fn", "text") and isinstance(v, str):
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
            assert len(q) <= m, (n, q[:60])


def test_index_definition_and_hypothesis():
    r = load("results.json")
    assert r["meta"]["cells7"] == ["F1", "F2", "F4", "F7", "F8", "F9", "F10"]
    h = r["hypothesis"]
    assert h["n"] == 16
    if h["withheld"]:
        assert h["verdict"] is None and "prov" not in h and "strict" not in h
    for p in r["projects"]:
        if p.get("masked"):
            continue
        for lo, hi in (p["talk"]["h"].values() if p.get("talk") else ()):
            assert hi or not lo  # meeting both at the lower reading implies the upper
        for k in ("prov", "strict", "prov4"):
            lo, hi = p["index"][k]
            assert 0 <= lo <= hi <= 1


def test_results_pages_show_the_status_banner():
    for page in ("results.html", "cells.html", "pets.html", "paragraphs.html", "map.html"):
        s = open(os.path.join(ROOT, "site", page), encoding="utf-8").read()
        assert 'id="prelim"' in s, page


def test_projects_under_verification_are_withheld():
    r = load("results.json")
    assert set(r["meta"]["masked"]) == UNDER_VERIFICATION
    for p in r["projects"]:
        if p["id"] in UNDER_VERIFICATION:
            assert set(p) == {"id", "name", "tier", "masked"}, p["id"]
    assert set(r["hypothesis"]["withheld"]) <= UNDER_VERIFICATION and not set(r["hypothesis"]["shown"]) & UNDER_VERIFICATION
    h = load("cell_history.json")
    assert all(set(h["projects"][c]) == {"tier", "masked"} for c in UNDER_VERIFICATION if c in h["projects"])
    assert not {c["project"] for c in h["changes"]} & UNDER_VERIFICATION
    assert not {x["project"] for x in load("pets.json")["rows"]} & UNDER_VERIFICATION
    assert not {x["p"] for x in load("paragraphs.json")["rows"]} & UNDER_VERIFICATION


def test_pet_mentions_have_a_page():
    obs = [o for x in load("pets.json")["rows"] for o in x["obs"]]
    assert obs and all(o["doc"] and o["doc"]["pg"] for o in obs if o["doc"] and o["doc"]["u"].lower().split("?")[0].endswith(".pdf"))
