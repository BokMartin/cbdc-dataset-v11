"""Tests of the exploratory privacy index on synthetic cells only (no project data)."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
from derive_index import two_axis_index, privacy_index, ranked_above, sensitivity_table, weight_sensitivity  # noqa: E402

E = {"evidence_state": "documented", "decision_status": "endorsed"}


def cell(value, **kw):
    return {"value": value, **E, **kw}


def test_all_missing_is_full_interval():
    r = privacy_index({})
    assert (r["lower"], r["upper"], r["determined"]) == (0.0, 1.0, 0)


def test_silence_is_never_zero():
    r = privacy_index({"F1": cell("no")})
    assert r["lower"] == 0.25 and r["upper"] == 1.0


def test_fully_protective_and_fully_not():
    full = {"F1": cell("no"), "F2": cell("no"), "F4": cell("yes"), "F7": cell("yes")}
    none = {"F1": cell("yes"), "F2": cell("yes"), "F4": cell("no"), "F7": cell("no")}
    assert privacy_index(full)["lower"] == 1.0 and privacy_index(none)["upper"] == 0.0


def test_gate_caps_when_cb_links():
    r = privacy_index({"F1": cell("yes"), "F2": cell("no"), "F4": cell("yes"), "F7": cell("yes")})
    assert r["upper"] == 0.5
    assert privacy_index({"F1": cell("yes"), "F2": cell("no"), "F4": cell("yes"), "F7": cell("yes")}, cap=None)["upper"] == 0.75


def test_strict_drops_considered_cells_status_view_keeps_them():
    c = {"F1": {"value": "no", "evidence_state": "documented", "decision_status": "considered"}}
    assert privacy_index(c)["determined"] == 0
    assert privacy_index(c, strict=False)["determined"] == 1


def test_route_d_and_inferred_exclusion():
    c = {"F1": cell("no", text_route="D"), "F2": cell("no", derivation="inferred")}
    assert privacy_index(c)["determined"] == 2
    assert privacy_index(c, exclude_route_d=True, exclude_inferred=True)["determined"] == 0


def test_ranking_only_without_overlap():
    a = privacy_index({"F1": cell("no"), "F2": cell("no"), "F4": cell("yes"), "F7": cell("yes")})
    b = privacy_index({"F1": cell("yes")})
    c = privacy_index({})
    assert ranked_above(a, b) and not ranked_above(a, c) and not ranked_above(c, b)


def test_sensitivity_runs_on_synthetic_projects():
    projects = {"P1": {"F1": cell("no"), "F2": cell("no"), "F4": cell("yes"), "F7": cell("yes")},
                "P2": {"F1": cell("yes"), "F2": cell("yes"), "F4": cell("no"), "F7": cell("no")},
                "P3": {}}
    t = sensitivity_table(projects)
    assert set(t["primary"]) == {"P1", "P2", "P3"} and "drop_F1" in t
    w = weight_sensitivity(projects, draws=50)
    assert w["baseline_pairs"] == 1 and w["kept_all_draws"] == 1.0


def test_two_axis_status_never_enters_design_axis():
    considered = {f: {"value": v, "evidence_state": "documented", "decision_status": "considered"} for f, v in (("F1", "no"), ("F2", "no"), ("F4", "yes"), ("F7", "yes"))}
    operational = {f: {"value": v, "evidence_state": "documented", "decision_status": "endorsed", "implementation_status": "operational"} for f, v in (("F1", "no"), ("F2", "no"), ("F4", "yes"), ("F7", "yes"))}
    a, b = two_axis_index(considered), two_axis_index(operational)
    assert a["design"]["lower"] == b["design"]["lower"] == 1.0
    assert a["commitment"] == 0.25 and b["commitment"] == 1.0
    assert a["strict"]["determined"] == 0 and b["strict"]["determined"] == 4 and b["admissible"] == 4


def test_two_axis_no_values():
    r = two_axis_index({})
    assert r["commitment"] is None and r["design"]["upper"] == 1.0
