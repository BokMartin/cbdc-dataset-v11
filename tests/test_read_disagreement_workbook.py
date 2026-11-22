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
        if r["basis"] == "authors_clarification": assert r["clarification_source"] and r["authors_response"].lower() != "ok"
        if r["status"] == "agreed": assert r["joint_label"] in ("R", "N", "U") and r["date"]
        else: assert r["status"] == "needs_author_check" and r["joint_label"] == ""


def test_committed_translation_adjudication_is_complete_and_text_free():
    p = sorted(glob.glob(os.path.join(ROOT, "data/translation/benchmark/JUDGEMENT_ADJUDICATED_MB_DS_*.csv")))
    if not p: return
    key = {r["n"]: r for r in csv.DictReader(open(os.path.join(ROOT, "data/translation/benchmark/JUDGEMENT_KEY_2026-11-11.csv"), encoding="utf-8"))}
    rows = list(csv.DictReader(open(p[-1], encoding="utf-8")))
    assert len({r["n"] for r in rows}) == len(rows)
    for r in rows:
        assert r["n"] in key and r["pair"] == key[r["n"]]["pair"] and r["mb_blind"] != r["ds_blind"]
        assert (r["status"] == "agreed") == (r["joint_code"] in ("S", "W", "X", "M", "D"))
        assert set(r) == {"n", "pair", "stratum", "mb_blind", "ds_blind", "ai_proposal", "joint_code", "reason", "status", "adjudicated_by", "date", "workbook_sha256"}
