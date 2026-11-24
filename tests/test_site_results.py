"""The results page (site/results.html): test data only, until the blind core outputs are opened (ADR-016 point 4)."""
import json, os, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "site", "assets", "results.json")


def load():
    with open(DATA, encoding="utf-8") as f:
        return json.load(f)


def test_results_data_are_current():
    r = subprocess.run([sys.executable, "scripts/site/build_results_data.py", "--mock", "--check"], cwd=ROOT, capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr


def test_results_are_test_data_with_banner():
    d = load()
    assert d["label"] == "MOCK" and d["mock"] is True and d["banner"]
    assert all(p["id"].startswith("MOCK") for p in d["projects"])
    assert all(v["file"].split("/")[-1].startswith("MOCK_") for v in d["inputs"].values())


def test_no_production_run_is_an_input():
    d = load()
    assert not any("prod" in v["file"].lower() for v in d["inputs"].values())


def test_results_page_not_linked_while_test_data():
    site_js = open(os.path.join(ROOT, "site", "assets", "site.js"), encoding="utf-8").read()
    assert "results.html" not in site_js
    for f in os.listdir(os.path.join(ROOT, "site")):
        if f.endswith(".html") and f != "results.html":
            assert "results.html" not in open(os.path.join(ROOT, "site", f), encoding="utf-8").read(), f
    page = open(os.path.join(ROOT, "site", "results.html"), encoding="utf-8").read()
    assert 'name="robots" content="noindex"' in page and 'id="mock-banner"' in page


def test_hypothesis_follows_registration():
    d = load()
    h = d["hypothesis"]
    assert h["n_core"] == 16 and d["definitions"]["majority"] == 9
    assert h["L"] <= h["U"]
    assert h["verdict"] == ("holds" if h["L"] >= 9 else "fails" if h["U"] <= 8 else "inconclusive")
    assert d["definitions"]["index_cells"] == ["F1", "F2", "F4", "F7", "F8", "F9", "F10"]
    assert d["definitions"]["hypothesis_cells"] == ["F1", "F2", "F4", "F7"]
    for p in d["projects"]:
        assert (p["hypothesis"] is not None) == (p["tier"] in ("T1", "T2"))
        lo, hi = p["index"]["stated"]
        assert 0 <= lo <= hi <= 1


def test_mock_label_refuses_real_ids(tmp_path):
    sys.path.insert(0, os.path.join(ROOT, "scripts", "site"))
    import build_results_data as b
    import pytest
    inputs = dict(b.MOCK_INPUTS)
    with pytest.raises(ValueError):
        b.build("PROD", inputs)
