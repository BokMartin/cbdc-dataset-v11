"""Agreement coefficients against hand-calculated values (independent audit of 13 Nov 2026, item 5)."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts", "units"))
import score_agreement as sa

FOUR = [("R", "R"), ("R", "R"), ("N", "N"), ("R", "N")]
RNU = ["R", "N", "U"]


def test_alpha_hand_example():
    assert abs(sa.alpha(FOUR) - 0.533333) < 1e-6


def test_alpha_is_undefined_when_all_ratings_are_one_category():
    assert sa.alpha([("R", "R")] * 10) is None
    s = sa.stat([("R", "R")] * 10, RNU)
    assert s["alpha"] is None and s["agreement"] == 1.0 and s["alpha_undefined_reason"]


def test_ac1_uses_the_declared_scale_not_the_observed_one():
    assert abs(sa.ac1(FOUR, ["R", "N"]) - 0.529412) < 1e-6
    assert abs(sa.ac1(FOUR, RNU) - 0.673469) < 1e-6
    assert sa.ac1([("R", "R")] * 10, RNU) == 1.0


def test_bootstrap_does_not_score_degenerate_replicates_as_perfect():
    s = sa.stat([("R", "R")] * 30 + [("R", "N")], RNU, B=300)
    assert s["bootstrap_replicates_undefined"] > 0
    assert s["alpha_ci95_conditional_on_sample"] is None or s["alpha_ci95_conditional_on_sample"][1] < 1.0


def test_end_to_end_counts_relevance_disagreement_as_facet_disagreement():
    allowed = {"relevant": RNU, **{k: ["X", "Y"] for k in sa.COLS[1:]}}
    blank = {k: "" for k in sa.COLS[1:]}
    A = {"u1": {"relevant": "R", **{k: "X" for k in blank}}, "u2": {"relevant": "R", **{k: "X" for k in blank}}, "u3": {"relevant": "N", **blank}}
    B = {"u1": {"relevant": "R", **{k: "X" for k in blank}}, "u2": {"relevant": "N", **blank}, "u3": {"relevant": "N", **blank}}
    S = {u: {"stratum": "D", "route": "A"} for u in A}
    r = sa.score(A, B, S, allowed)
    assert r["units_both_relevant"] == 1 and r["units_relevant_for_at_least_one"] == 2
    assert r["voice_end_to_end"]["agreement"] == 0.5


def test_facet_workbook_scores_only_its_columns_and_aspect2_blank_is_none():
    """The 80-sentence workbook has no implementation or modality but has aspect2; the sample file names its stratum candidate_stratum."""
    allowed = {"relevant": RNU, "voice": ["OWN", "REPORTED"], "aspect": ["GENERAL", "ANONYMITY"], "aspect2": ["GENERAL", "ANONYMITY"]}
    def row(rel, voice="", aspect="", aspect2=""):
        return {"relevant": rel, "voice": voice, "aspect": aspect, "aspect2": aspect2}
    A = {"u1": row("R", "OWN", "GENERAL"), "u2": row("R", "OWN", "ANONYMITY", "GENERAL"), "u3": row("N")}
    B = {"u1": row("R", "OWN", "GENERAL"), "u2": row("R", "REPORTED", "GENERAL", "ANONYMITY"), "u3": row("N")}
    S = {u: {"candidate_stratum": "D", "route": "A"} for u in A}
    res = sa.score(A, B, S, allowed)
    assert res["facets_scored"] == ["voice", "aspect", "aspect2"]
    assert res["aspect2"]["counts"]["NONE"] == 2
    assert res["aspect_set"] == {"n": 2, "same_set": 2, "overlapping": 2}
    assert list(res["by_stratum"]) == ["D"]
