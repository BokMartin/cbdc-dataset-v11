"""Tests of the privacy index v2 (all eight privacy cells), talk against commitments, the uncertainty analysis and the
prepared validation, on synthetic and MOCK cells only."""
import csv
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
from derive_index import CORE, CORE4, axis1, axis2, privacy_index, separated, simulate_separation, uncertainty_analysis  # noqa: E402
from index_reliability import merge, reliability  # noqa: E402
from index_validity import check_known_cases, compare_external, spearman  # noqa: E402
from talk_commitment import pair_state, project_summary, table_2x2, talk_intensity, talk_exceeds_commitment  # noqa: E402

ROOT = os.path.join(os.path.dirname(__file__), "..")


def cell(value, dec="endorsed", impl=""):
    return {"value": value, "evidence_state": "documented", "decision_status": dec, "implementation_status": impl}


FULL = {"F1": cell("no"), "F2": cell("no"), "F3": cell("via_PSP"), "F4": cell("yes"), "F7": cell("yes"), "F8": cell("no"), "F9": cell("no"), "F10": cell("no")}
NONE = {"F1": cell("yes"), "F2": cell("yes"), "F3": cell("via_CB"), "F4": cell("no"), "F7": cell("no"), "F8": cell("yes"), "F9": cell("yes"), "F10": cell("yes")}


def test_eight_cells_and_mean_by_default():
    assert len(CORE) == 8 and axis1({})["rule"] == "mean"


def test_all_missing_is_full_interval():
    r = axis1({})
    assert (r["lower"], r["upper"], r["determined"]) == (0.0, 1.0, 0)


def test_silence_is_never_zero():
    r = axis1({"F1": cell("no")})
    assert r["lower"] == 0.125 and r["upper"] == 1.0


def test_extremes_and_f3_categories():
    assert axis1(FULL)["lower"] == 1.0 and axis1(NONE)["upper"] == 0.0
    assert axis1({"F3": cell("none_stated")})["determined"] == 0  # a completed search without a route sets no score


def test_every_cell_moves_the_mean():
    base = axis1(FULL)["lower"]
    for f in CORE:
        flipped = dict(FULL)
        flipped[f] = NONE[f]
        assert axis1(flipped)["lower"] < base, f


def test_lexicographic_variant_f1_class_dominates():
    weak_but_f1 = {"F1": cell("no"), "F2": cell("yes"), "F4": cell("no"), "F7": cell("no")}
    strong_but_cb_links = {"F1": cell("yes"), "F2": cell("no"), "F4": cell("yes"), "F7": cell("yes")}
    a = axis1(weak_but_f1, rule="lexicographic", cells_used=CORE4)
    b = axis1(strong_but_cb_links, rule="lexicographic", cells_used=CORE4)
    assert separated(a, b) and b["upper"] == 0.5


def test_cap_variant_does_not_cap_when_f1_missing():
    r = axis1({"F2": cell("no"), "F4": cell("yes"), "F7": cell("yes")}, rule="cap", cells_used=CORE4)
    assert r["lower"] == 0.75 and r["upper"] == 1.0


def test_stated_view_keeps_considered_admissible_drops_it():
    r = privacy_index({"F1": cell("no", dec="considered"), "F3": cell("via_PSP")})
    assert r["stated"]["determined"] == 2 and r["admissible"]["determined"] == 1
    assert r["commitment"]["profile"]["F1"] == 1 and r["commitment"]["decided"] == 1 and r["commitment"]["n_cells"] == 8


def test_commitment_profile():
    a = axis2({"F1": cell("no", impl="operational"), "F2": cell("no", dec="considered", impl="tested")})
    assert a["profile"]["F1"] == 4 and a["profile"]["F2"] == 2 and a["decided"] == 1 and a["stated_only"] == 1


def test_route_d_inferred_and_disagreement_widen():
    c = {"F1": {**cell("no"), "text_route": "D"}, "F2": {**cell("no"), "derivation": "inferred"},
         "F4": {**cell("yes"), "coder_disagreement": "true"}}
    assert axis1(c)["determined"] == 2
    assert axis1(c, exclude_route_d=True, exclude_inferred=True)["determined"] == 0


def test_uncertainty_analysis_on_synthetic_projects():
    u = uncertainty_analysis({"P1": FULL, "P2": NONE, "P3": {}}, draws=50)
    assert u["baseline_separated_pairs"] == 1 and u["weights_kept_in_all_draws"] == 1.0
    assert u["rule_lexicographic_kept"] == 1.0 and u["drop_F1_kept"] == 1.0 and u["core4_only_kept"] == 1.0


def test_simulation_more_coverage_more_separation():
    low = simulate_separation({f: 0.2 for f in CORE}, n_projects=20, draws=30)
    high = simulate_separation({f: 0.9 for f in CORE}, n_projects=20, draws=30)
    assert high["mean"] > low["mean"]


def test_reliability_and_merge():
    def row(p, c, v, dec="endorsed"):
        return {"project_id": p, "cell": c, "value": v, "decision_status": dec, "implementation_status": "", "evidence_state": "documented",
                "basis": "architectural", "text_route": "A", "derivation": "explicit", "conflict": "", "quote": "q", "page_index": ""}
    a = {("P1", "F1"): row("P1", "F1", "no"), ("P2", "F1"): row("P2", "F1", "yes"), ("P3", "F1"): row("P3", "F1", "no", "considered"),
         ("P1", "F3"): row("P1", "F3", "via_psp")}
    b = {("P1", "F1"): row("P1", "F1", "no", "considered"), ("P2", "F1"): row("P2", "F1", "no"), ("P3", "F1"): row("P3", "F1", "no"),
         ("P1", "F3"): row("P1", "F3", "via_psp")}
    rel = reliability(a, b, cells=("F1",))
    assert rel["F1"]["n"] == 3 and rel["F1"]["agreement"] == round(2 / 3, 3)
    m = merge(a, b)
    assert m["P1"]["F1"]["decision_status"] == "considered"  # lower rung of the two
    assert m["P1"]["F3"]["value"] == "via_psp" and axis1(m["P1"])["components"]["F3"] == 1
    assert m["P2"]["F1"]["coder_disagreement"] == "true" and axis1(m["P2"])["determined"] == 0


def test_known_cases_and_external():
    projects = {"P1": FULL, "P2": NONE, "P3": {"F1": cell("no")}, "P4": {f: c for f, c in FULL.items() if f != "F10"}}
    known = [{"case_id": "K1", "project_id": "P1", "cell": "F1", "expected_value": "no"},
             {"case_id": "K2", "project_id": "P2", "cell": "F1", "expected_value": "no"},
             {"case_id": "K3", "project_id": "P3", "cell": "F2", "expected_value": "no"},
             {"case_id": "K4", "project_id": "P1", "cell": "F4", "expected_value": ""}]
    assert [r["status"] for r in check_known_cases(projects, known)] == ["hit", "miss", "undetermined", "not_fixed"]
    ext = [{"project_id": p, "measure": "m", "value": v} for p, v in (("P1", "3"), ("P2", "1"), ("P3", "9"), ("P4", "2"))]
    res = compare_external(projects, ext, [{"measure": "m", "expected_sign": "+"}], B=200)[0]
    assert res["n"] == 3 and res["projects_excluded_wide_interval"] == ["P3"]
    assert spearman([1, 2, 3], [3, 2, 1]) == -1.0


def test_talk_commitment_pairs_and_bounds():
    cells = {"F1": cell("no"), "F2": cell("no", dec="considered"), "F4": {**cell("yes", dec="considered"), "coder_disagreement": "true"}}
    assert pair_state(5, cells, "CB_ACCESS") == {"talk": True, "commitment": "admissible", "max_rung": 3, "leaning": False}
    assert pair_state(5, cells, "INTERMEDIARY_DATA")["commitment"] == "stated"
    assert pair_state(0, cells, "ANONYMITY")["commitment"] == "none"
    assert pair_state(1, cells, "OFFLINE")["commitment"] == "uncertain"
    s = project_summary({"CB_ACCESS": 3, "INTERMEDIARY_DATA": 2, "OFFLINE": 1, "ANONYMITY": 4}, cells)
    assert s["talked"] == 4 and s["committed"] == 1 and s["gap"] == [2, 3]
    t = table_2x2({"P": s})
    assert t["talk_and_committed"] == 1 and t["talk_no_commitment"] == 1 and t["talk_uncertain"] == 1


def test_talk_test_discriminates_talk_from_stated_design():
    talky = {f"P{i}": project_summary({a: 1 for a in ("CB_ACCESS", "INTERMEDIARY_DATA", "OFFLINE", "ANONYMITY", "IDENTIFICATION", "AUTHORITY_ACCESS")}, {"F1": cell("no", dec="considered")}) for i in range(12)}
    mirror = {f"P{i}": project_summary({"CB_ACCESS": 1}, {"F1": cell("no", dec="considered")}) for i in range(12)}
    assert talk_exceeds_commitment(talky, level="stated")["sign_test_p_one_sided"] < 0.01
    assert talk_exceeds_commitment(mirror, level="stated")["positive"] == 0
    assert talk_exceeds_commitment(mirror, level="admissible")["positive"] == 12  # H-TC1 cannot tell them apart
    assert talk_intensity(10, 100)["share"] == 0.1 and talk_intensity(0, 0) is None


def test_prepared_input_files_are_well_formed():
    with open(os.path.join(ROOT, "data/index/CODER_TEMPLATE_2026-11-22.csv"), newline="") as fh:
        rows = list(csv.DictReader(fh))
    assert len(rows) == 44 * 8 and {r["cell"] for r in rows} == set(CORE)
    from index_reliability import FIELDS
    assert list(rows[0]) == FIELDS and all(r[f] == "" for r in rows for f in FIELDS if f not in ("project_id", "cell"))
    with open(os.path.join(ROOT, "data/index/KNOWN_CASES_DRAFT_2026-11-21.csv"), newline="") as fh:
        known = list(csv.DictReader(fh))
    assert all(r["expected_value"] in ("", "yes", "no") for r in known)
    assert all(r["expected_value"] == "" for r in known if r["exposure"].startswith("NOT exposed"))


def test_mock_dry_run_end_to_end(tmp_path):
    from index_mock import write as write_mock
    from index_report import run, write as write_report
    m = write_mock(str(tmp_path / "mock"))
    res, index, tiers = run("MOCK", f"{m}/MOCK_CODER_A.csv", f"{m}/MOCK_CODER_B.csv", f"{m}/MOCK_KNOWN_CASES.csv",
                            f"{m}/MOCK_EXTERNAL.csv", f"{m}/MOCK_MEASURES.csv", f"{m}/MOCK_TIERS.csv", draws=20,
                            talk_path=f"{m}/MOCK_TALK_NULL.csv", intensity_path=f"{m}/MOCK_TALK_INTENSITY.csv")
    assert res["n_projects"] == 44 and len(index) == 44
    assert [k["status"] for k in res["known_cases"]].count("miss") == 1  # the planted miss is caught
    assert res["talk_commitment"]["table_2x2"]["talk_no_commitment"] == 0  # NULL: talk only where a design is stated
    files = write_report(str(tmp_path / "out"), "MOCK", res, index, tiers, "NULL")
    assert all(os.path.basename(f).startswith("MOCK_NULL_") for f in files) and len(files) == 5
    assert open(files[1]).readline().startswith("# MOCK DATA")
    assert all("MOCK DATA" in open(f).read() for f in files if f.endswith(".svg"))


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


def test_leaning_cells_bound_only_in_primary():
    lean = {"value": "no", "evidence_state": "documented", "decision_status": "leaning"}
    c = {"F1": lean, "F2": lean, "F4": cell("yes")}
    r = privacy_index(c)
    assert r["stated"]["determined"] == 1 and r["admissible"]["determined"] == 1
    assert r["stated_with_leaning"]["determined"] == 3 and r["stated_with_leaning"]["rests_on_leaning"]
    assert r["commitment"]["profile"]["F1"] == 0 and r["commitment"]["leaning"] == ["F1", "F2"]
    assert pair_state(3, c, "CB_ACCESS")["commitment"] == "none" and pair_state(3, c, "CB_ACCESS")["leaning"]
    own = dict(c, F1=cell("yes"))  # a value from the competent body's own documents replaces the leaning
    assert privacy_index(own)["stated"]["components"]["F1"] == 0


# ---------- V6 of the 22 Nov check / audit A4b finding 1: one rule-C predicate for every commitment count ----------
BAD = {"value": "no", "evidence_state": "partial", "conflict": "true", "decision_status": "unclear", "implementation_status": "operational"}


def test_v6_auditor_counterexample_is_never_a_commitment():
    from derive import admissible
    from derive_index import committed
    assert not admissible(BAD) and not committed(BAD, "F1")
    r = privacy_index({"F1": BAD})
    assert r["commitment"]["decided"] == 0 and r["commitment"]["rung3_not_admissible"] == ["F1"]
    assert r["commitment"]["profile"]["F1"] == 4  # the ladder is still shown
    assert r["stated"]["components"]["F1"] is None  # a conflicted cell states no design
    assert pair_state(3, {"F1": BAD}, "CB_ACCESS")["commitment"] == "stated"


def test_v6_partial_operational_is_stated_not_committed():
    partial = {"value": "no", "evidence_state": "partial", "decision_status": "unclear", "implementation_status": "operational"}
    r = privacy_index({"F1": partial})
    assert r["stated"]["components"]["F1"] == 1 and r["admissible"]["components"]["F1"] is None
    assert r["commitment"]["decided"] == 0
    assert pair_state(3, {"F1": partial}, "CB_ACCESS")["commitment"] == "stated"
    s = project_summary({"CB_ACCESS": 3}, {"F1": partial})
    assert s["committed"] == 0 and s["gap"] == [1, 1]


def test_v6_operational_documented_without_decision_is_admissible():
    op = {"value": "no", "evidence_state": "documented", "decision_status": "unclear", "implementation_status": "operational"}
    assert privacy_index({"F1": op})["commitment"]["decided"] == 1  # contract §5 item 3 permits it
    assert pair_state(1, {"F1": op}, "CB_ACCESS")["commitment"] == "admissible"


def _rec(p, c, v, **kw):
    r = {"project_id": p, "cell": c, "value": v, "decision_status": "endorsed", "implementation_status": "", "evidence_state": "documented",
         "basis": "architectural", "text_route": "A", "derivation": "explicit", "conflict": "", "document_id": "DOC", "quote": "q",
         "page_index": "1", "note": ""}
    r.update(kw)
    return r


def test_v6_merge_carries_fields_conservatively_and_keeps_every_key():
    a = {("P1", "F1"): _rec("P1", "F1", "no", text_route="D", derivation="inferred"), ("P1", "F2"): _rec("P1", "F2", "no"),
         ("P1", "F4"): _rec("P1", "F4", "yes", evidence_state="partial"), ("P1", "F7"): _rec("P1", "F7", "yes")}
    b = {("P1", "F1"): _rec("P1", "F1", "no"), ("P1", "F2"): _rec("P1", "F2", "no", conflict="true"),
         ("P1", "F4"): _rec("P1", "F4", "yes")}
    m = merge(a, b)["P1"]
    assert (m["F1"]["text_route"], m["F1"]["derivation"]) == ("D", "inferred")
    assert m["F2"]["conflict"] == "true" and m["F4"]["evidence_state"] == "partial"
    assert m["F7"]["missing_coder"] == "true" and m["F7"]["value"] == "undetermined"
    assert m["F1"]["coded"]["a"]["quote"] == "q" and m["F1"]["coded"]["b"]["text_route"] == "A"
    r = privacy_index(m)
    assert r["commitment"]["decided"] == 1  # only F1: F2 conflicted, F4 partial, F7 coded by one coder only
    assert axis1(m, exclude_route_d=True)["components"]["F1"] is None and axis1(m, exclude_inferred=True)["components"]["F1"] is None
    assert pair_state(2, m, "ANONYMITY")["commitment"] == "uncertain"


def _write(path, rows):
    from index_reliability import FIELDS
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, FIELDS)
        w.writeheader()
        w.writerows(rows)
    return str(path)


def test_v6_reader_refuses_incomplete_records(tmp_path):
    import pytest
    from index_reliability import read
    cases = {
        "old_format": None,
        "empty_key": [_rec("", "F1", "no")],
        "no_evidence_state": [_rec("P1", "F1", "no", evidence_state="")],
        "no_route": [_rec("P1", "F7", "yes", text_route="")],
        "no_quote": [_rec("P1", "F7", "yes", quote="")],
        "f1_without_basis": [_rec("P1", "F1", "no", basis="")],
        "value_on_unknown": [_rec("P1", "F7", "yes", evidence_state="unknown")],
        "bad_route": [_rec("P1", "F7", "yes", text_route="E")],
        "duplicate": [_rec("P1", "F7", "yes"), _rec("P1", "F7", "yes")],
        "outside_grid": [_rec("P1", "F11", "yes")],
    }
    for name, rows in cases.items():
        path = tmp_path / f"{name}.csv"
        if rows is None:
            path.write_text("project_id,cell,value,decision_status,implementation_status,quote,page_index\nP1,F1,no,endorsed,,q,1\n")
        else:
            _write(path, rows)
        with pytest.raises(ValueError):
            read(str(path))
    ok = read(_write(tmp_path / "ok.csv", [_rec("P1", "F7", "yes"), _rec("P1", "F1", "", evidence_state="", basis="", text_route="", derivation="", document_id="", quote="")]))
    assert ok[("P1", "F1")]["value"] == "undetermined"


def test_v6_through_the_report_entry_point(tmp_path):
    from index_report import run
    rows = [_rec("P1", "F1", "no", evidence_state="partial", implementation_status="operational", decision_status="unclear"),
            _rec("P1", "F2", "no", text_route="D"), _rec("P1", "F7", "yes", conflict="true"),
            _rec("P2", "F1", "no", basis="policy"), _rec("P2", "F2", "no"), _rec("P2", "F7", "yes")]
    a = _write(tmp_path / "a.csv", rows)
    b = _write(tmp_path / "b.csv", rows + [_rec("P2", "F4", "yes")])
    talk = tmp_path / "talk.csv"
    talk.write_text("project_id,aspect,own_units\nP1,CB_ACCESS,4\nP1,INTERMEDIARY_DATA,2\nP1,ANONYMITY,3\nP2,OFFLINE,1\n")
    res, index, _ = run("TEST", a, b, None, None, None, None, draws=5, talk_path=str(talk))
    assert index["P1"]["commitment"]["decided"] == 1  # F2 only; F1 partial, F7 conflicted
    assert index["P1"]["commitment"]["rung3_not_admissible"] == ["F1", "F7"]
    assert index["P2"]["commitment"]["decided"] == 3
    assert res["reliability"]["keys_in_one_file_only"] == [["P2", "F4"]]
    assert res["reliability"]["f1_no_on_policy_basis"] == ["P2"]
    pp = res["talk_commitment"]["per_project"]
    assert pp["P1"]["committed"] == 1 and pp["P1"]["gap"] == [2, 2]
    assert pp["P2"]["uncertain"] == 1 and pp["P2"]["gap"] == [0, 1]  # F4 coded by one coder only


def test_one_aspect_map_in_the_schema():
    import json
    from talk_commitment import ASPECT_CELLS, TALK_ONLY_ASPECTS, UNMAPPED_CELLS
    sch = json.load(open(os.path.join(ROOT, "schema/talk_units_v13_DRAFT.json"), encoding="utf-8"))
    m = sch["aspect_comparison_cells"]["cells"]
    assert set(m) == set(sch["L2_facets"]["aspect"])  # every codebook aspect is mapped, to cells or to none
    assert set(ASPECT_CELLS) | set(TALK_ONLY_ASPECTS) == set(m)
    assert {c for cs in ASPECT_CELLS.values() for c in cs} | set(UNMAPPED_CELLS) == set(CORE)
