"""Tests of the privacy index, its uncertainty analysis and the prepared validation, on synthetic cells only."""
import csv
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
from derive_index import axis1, axis2, privacy_index, separated, simulate_separation, uncertainty_analysis  # noqa: E402
from index_reliability import merge, reliability  # noqa: E402
from index_validity import check_known_cases, compare_external, spearman  # noqa: E402

ROOT = os.path.join(os.path.dirname(__file__), "..")


def cell(value, dec="endorsed", impl=""):
    return {"value": value, "evidence_state": "documented", "decision_status": dec, "implementation_status": impl}


FULL = {"F1": cell("no"), "F2": cell("no"), "F4": cell("yes"), "F7": cell("yes")}
NONE = {"F1": cell("yes"), "F2": cell("yes"), "F4": cell("no"), "F7": cell("no")}


def test_all_missing_is_full_interval():
    r = axis1({})
    assert (r["lower"], r["upper"], r["determined"]) == (0.0, 1.0, 0)


def test_silence_is_never_zero():
    r = axis1({"F1": cell("no")})
    assert r["lower"] == 0.5 and r["upper"] == 1.0


def test_extremes():
    assert axis1(FULL)["lower"] == 1.0 and axis1(NONE)["upper"] == 0.0


def test_lexicographic_f1_class_dominates():
    weak_but_f1 = {"F1": cell("no"), "F2": cell("yes"), "F4": cell("no"), "F7": cell("no")}
    strong_but_cb_links = {"F1": cell("yes"), "F2": cell("no"), "F4": cell("yes"), "F7": cell("yes")}
    assert separated(axis1(weak_but_f1), axis1(strong_but_cb_links))
    assert axis1(strong_but_cb_links)["upper"] == 0.5


def test_cap_rule_does_not_cap_when_f1_missing():
    r = axis1({"F2": cell("no"), "F4": cell("yes"), "F7": cell("yes")}, rule="cap")
    assert r["lower"] == 0.75 and r["upper"] == 1.0


def test_stated_view_keeps_considered_admissible_drops_it():
    c = {"F1": cell("no", dec="considered")}
    r = privacy_index(c)
    assert r["stated"]["determined"] == 1 and r["admissible"]["determined"] == 0
    assert r["commitment"]["profile"]["F1"] == 1 and r["commitment"]["decided_of_4"] == 0


def test_commitment_profile_fixed_denominator():
    c = {"F1": cell("no", impl="operational"), "F2": cell("no", dec="considered", impl="tested")}
    a = axis2(c)
    assert a["profile"] == {"F1": 4, "F2": 2, "F4": 0, "F7": 0} and a["decided_of_4"] == 1


def test_route_d_inferred_and_disagreement_widen():
    c = {"F1": {**cell("no"), "text_route": "D"}, "F2": {**cell("no"), "derivation": "inferred"},
         "F4": {**cell("yes"), "coder_disagreement": "true"}}
    assert axis1(c)["determined"] == 2
    assert axis1(c, exclude_route_d=True, exclude_inferred=True)["determined"] == 0


def test_uncertainty_analysis_on_synthetic_projects():
    projects = {"P1": FULL, "P2": NONE, "P3": {}}
    u = uncertainty_analysis(projects, draws=50)
    assert u["baseline_separated_pairs"] == 1 and u["weights_kept_in_all_draws"] == 1.0
    assert u["rule_mean_kept"] == 1.0 and u["drop_F1_kept"] == 1.0


def test_simulation_more_coverage_more_separation():
    low = simulate_separation({f: 0.2 for f in ("F1", "F2", "F4", "F7")}, n_projects=20, draws=30)
    high = simulate_separation({f: 0.9 for f in ("F1", "F2", "F4", "F7")}, n_projects=20, draws=30)
    assert high["mean"] > low["mean"]


def test_reliability_and_merge():
    def row(p, c, v, dec="endorsed"):
        return {"project_id": p, "cell": c, "value": v, "decision_status": dec, "implementation_status": "", "quote": "", "page_index": ""}
    a = {("P1", "F1"): row("P1", "F1", "no"), ("P2", "F1"): row("P2", "F1", "yes"), ("P3", "F1"): row("P3", "F1", "no", "considered")}
    b = {("P1", "F1"): row("P1", "F1", "no", "considered"), ("P2", "F1"): row("P2", "F1", "no"), ("P3", "F1"): row("P3", "F1", "no")}
    rel = reliability(a, b, cells=("F1",))
    assert rel["F1"]["n"] == 3 and rel["F1"]["agreement"] == round(2 / 3, 3)
    m = merge(a, b)
    assert m["P1"]["F1"]["decision_status"] == "considered"  # lower rung of the two
    assert m["P2"]["F1"]["coder_disagreement"] == "true" and axis1(m["P2"])["determined"] == 0


def test_known_cases_and_external():
    projects = {"P1": FULL, "P2": NONE, "P3": {"F1": cell("no")}, "P4": {"F1": cell("no"), "F2": cell("no"), "F4": cell("no"), "F7": cell("no")}}
    known = [{"case_id": "K1", "project_id": "P1", "cell": "F1", "expected_value": "no"},
             {"case_id": "K2", "project_id": "P2", "cell": "F1", "expected_value": "no"},
             {"case_id": "K3", "project_id": "P3", "cell": "F2", "expected_value": "no"},
             {"case_id": "K4", "project_id": "P1", "cell": "F4", "expected_value": ""}]
    st = [r["status"] for r in check_known_cases(projects, known)]
    assert st == ["hit", "miss", "undetermined", "not_fixed"]
    ext = [{"project_id": p, "measure": "m", "value": v} for p, v in (("P1", "3"), ("P2", "1"), ("P3", "9"), ("P4", "2"))]
    res = compare_external(projects, ext, [{"measure": "m", "expected_sign": "+"}], B=200)[0]
    assert res["n"] == 3 and res["projects_excluded_wide_interval"] == ["P3"] and res["rho"] == 1.0
    assert spearman([1, 2, 3], [3, 2, 1]) == -1.0


def test_prepared_input_files_are_well_formed():
    with open(os.path.join(ROOT, "data/index/CODER_TEMPLATE_2026-11-21.csv"), newline="") as fh:
        rows = list(csv.DictReader(fh))
    assert len(rows) == 176 and {r["cell"] for r in rows} == {"F1", "F2", "F4", "F7"}
    with open(os.path.join(ROOT, "data/index/KNOWN_CASES_DRAFT_2026-11-21.csv"), newline="") as fh:
        known = list(csv.DictReader(fh))
    assert all(r["expected_value"] in ("", "yes", "no") for r in known)
    assert all(r["expected_value"] == "" for r in known if r["exposure"].startswith("NOT exposed"))


def test_mock_dry_run_end_to_end(tmp_path):
    from index_mock import write as write_mock
    from index_report import run, write as write_report
    m = write_mock(str(tmp_path / "mock"))
    res, index, tiers = run("MOCK", f"{m}/MOCK_CODER_A.csv", f"{m}/MOCK_CODER_B.csv", f"{m}/MOCK_KNOWN_CASES.csv",
                            f"{m}/MOCK_EXTERNAL.csv", f"{m}/MOCK_MEASURES.csv", f"{m}/MOCK_TIERS.csv", draws=20)
    assert res["n_projects"] == 44 and len(index) == 44
    assert [k["status"] for k in res["known_cases"]].count("miss") == 1  # the planted miss is caught
    files = write_report(str(tmp_path / "out"), "MOCK", res, index, tiers)
    assert all(os.path.basename(f).startswith("MOCK_") for f in files)
    assert open(files[1]).readline().startswith("# MOCK DATA")
    assert "MOCK DATA" in open(files[3]).read()


def test_mock_ids_require_mock_label(tmp_path):
    import pytest
    from index_mock import write as write_mock
    from index_report import run
    m = write_mock(str(tmp_path / "mock"))
    with pytest.raises(ValueError):
        run("REAL", f"{m}/MOCK_CODER_A.csv", f"{m}/MOCK_CODER_B.csv", None, None, None, None, draws=5)


def test_website_never_reads_index_mock():
    for d, _, fs in os.walk(os.path.join(ROOT, "site")):
        for f in fs:
            if f.endswith((".html", ".js", ".json", ".py")):
                assert "data/index" not in open(os.path.join(d, f), encoding="utf-8", errors="ignore").read(), f
    assert "data/index" not in open(os.path.join(ROOT, "scripts/site/build_site_data.py")).read()
