"""Reader of the returned disagreement workbook: only "ok" and "final : X" become a joint label; nothing is guessed (22 Nov 2026)."""
import csv, glob, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts", "review"))
import read_disagreement_workbook as rw


def row(response, proposal="N", reason="B", note=" – převzato MB. Pravidlo: Obecná věta je N. Zde konkrétní případ."):
    return {"proposal": proposal, "reason": reason, "note": note, "response": response}


def test_ok_accepts_the_proposal_and_its_rule():
    for r in ("ok", " OK", "dokument už není v evidenci - ok", "dokument už není v evidenci - OK"):
        assert rw.adjudicate(row(r)) == ("N", "agreed", "accepted_proposal", "accepted")


def test_final_overrides_and_rejects_a_contrary_rule():
    assert rw.adjudicate(row("final : R")) == ("R", "agreed", "authors_override", "rejected")
    assert rw.adjudicate(row("final: n")) == ("N", "agreed", "authors_override", "accepted")


def test_anything_else_is_not_read_as_a_label():
    for r in ("?", "MB", "DS - poznámka", "", None, "R"):
        lab, status, basis, _ = rw.adjudicate(row(r))
        assert lab == "" and status == "needs_author_check" and basis == "unclear"


def test_rule_keeps_only_the_general_sentence():
    assert rw.rule_of(" – převzato DS. Pravidlo: Obecná exekuční pravidla jsou N. Zmínka o nesouhlasu...") == "Obecná exekuční pravidla jsou N."
    assert rw.rule_of(" – převzato MB. Pouhý nadpis.") == ""


def test_committed_adjudication_matches_the_blind_files():
    p = sorted(glob.glob(os.path.join(ROOT, "data/units/DEV_ADJUDICATED_RELEVANCE_MB_DS_*.csv")))
    if not p: return
    adj = list(csv.DictReader(open(p[-1], encoding="utf-8")))
    blind = {w: {r["unit_id"]: r for r in csv.DictReader(open(sorted(glob.glob(os.path.join(ROOT, f"data/units/DEV_LABELS_{w}_*.csv")))[-1], encoding="utf-8"))} for w in ("MB", "DS")}
    for r in adj:
        u = r["unit_id"]; assert u in blind["MB"] and u in blind["DS"]
        assert r["ds_blind"] == blind["DS"][u]["relevant"]
        if blind["MB"][u]["relevant"]: assert r["mb_blind"] == blind["MB"][u]["relevant"]
        assert r["mb_blind"] != r["ds_blind"], "only disagreements are adjudicated"
        if r["status"] == "agreed": assert r["joint_label"] in ("R", "N", "U") and r["date"]
        else: assert r["status"] == "needs_author_check" and r["joint_label"] == ""
