"""Exposure registry (A4 F06): blocks are paragraphs, joins are followed, dropped documents are kept, unknown samples are refused."""
import csv, json, os, sys
import pytest
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts", "units"))
import exposure_registry as er


def w(p, rows):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", newline="") as fh:
        x = csv.DictWriter(fh, list(rows[0])); x.writeheader(); x.writerows(rows)


def test_blocks_from_samples_runs_and_joins(tmp_path, monkeypatch):
    root, units = str(tmp_path), str(tmp_path / "units")
    w(os.path.join(units, "D.units.csv"), [{"unit_id": f"D:p{p}:s{s}", "page": p, "para": a} for p, s, a in [(1, 1, 1), (1, 2, 1), (2, 3, 1), (2, 4, 2)]])
    w(os.path.join(root, "data/units/AGREEMENT_SAMPLE_dev_2026-11-13.csv"), [{"unit_id": "D:p1:s2"}, {"unit_id": "GONE:p5:s9"}])
    w(os.path.join(root, "data/units/PAGE_BREAK_JOINS_2026-11-22.csv"), [{"kept": "D:p2:s4", "absorbed": "D:p3:s5"}])
    run = os.path.join(root, "data/talk/runs/r"); w(os.path.join(run, "CALLS.csv"), [{"unit_ids": "D:p3:s5", "complete": "True", "started_utc": "2026-12-01T00:00:00Z"}])
    json.dump({"purpose": "development", "model_requested": "m"}, open(os.path.join(run, "RUN_META.json"), "w"))
    monkeypatch.setattr(er, "SOURCES", {"AGREEMENT_SAMPLE_dev_2026-11-13.csv": ("dev", "MB DS", "", "2026-11-17")})
    rows, missing = er.build(units, er.collect(root), root)
    assert missing == []
    got = {(r["doc_key"], r["page"], r["para"]): r for r in rows}
    assert got[("D", 1, 1)]["shown_to"] == "DS MB" and got[("D", 2, 2)]["model_labelled_by"] == "m" and got[("GONE", 5, "")]
    p = os.path.join(root, "reg.csv"); w(p, rows)
    assert er.blocks(p) == {("D", 1, 1), ("D", 2, 2)} and er.blocks(p, shown_only=True) == {("D", 1, 1)}


def test_a_sample_without_a_ledger_entry_is_refused(tmp_path, monkeypatch):
    w(os.path.join(str(tmp_path), "data/units/AGREEMENT_SAMPLE_new_2026-12-01.csv"), [{"unit_id": "D:p1:s1"}])
    monkeypatch.setattr(er, "SOURCES", {})
    with pytest.raises(SystemExit): er.collect(str(tmp_path))
