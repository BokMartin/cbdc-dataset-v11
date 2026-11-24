"""Blind F-cell workbook: build from units only, lock with checks (ADR-012 D1, D2; ADR-016 §4)."""
import csv
import os
import sys

import pytest
from openpyxl import load_workbook

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts", "review"))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import build_blind_cell_workbook as B  # noqa: E402
import lock_blind_cell_workbook as L  # noqa: E402
from index_reliability import read  # noqa: E402


def _fake_units(tmp):
    d = tmp / "units"
    d.mkdir()
    for doc in B.documents():
        with open(d / (doc["doc_key"] + ".units.csv"), "w", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh)
            w.writerow(["unit_id", "page", "para", "n_words", "text", "page_end"])
            w.writerow([doc["doc_key"] + ":p1:s1", 1, 1, 6, "Offline payments protect user privacy here.", 1])
            w.writerow([doc["doc_key"] + ":p2:s2", 2, 1, 4, "Nothing relevant on this page.", 2])
    return d


def test_blind_projects_and_documents():
    docs = B.documents()
    assert B.BLIND == tuple(sorted(B.BLIND)) and len(B.BLIND) == 14
    assert not {"NO", "UK"} & {d["project"] for d in docs}
    ev = [d for d in docs if d["for_cells"] == "ano"]
    assert len(ev) == 106 and len({d["code"] for d in docs}) == len(docs)
    assert all(d["translation"] for d in ev if d["route"] == "D")


def test_guard_refuses_model_runs():
    for p in ("/mnt/project-files/prod-2026-11-23/runs/x", "/tmp/PROD_RUNS_FINAL_2026-11-24", "/tmp/a/runs"):
        with pytest.raises(SystemExit):
            B._guard(p)
    B._guard("/tmp/claude/units/CBDC_UNITS_v13e")


@pytest.fixture
def built(tmp_path, monkeypatch):
    units = _fake_units(tmp_path)
    docs = B.documents()
    rows = B.finder(docs, str(units))
    spans = {d["doc_key"] for d in docs if d["span"]}
    assert spans and {r["pages"] for r in rows if r["group"] in ("PRIV", "OFF") and r["doc_key"] not in spans} == {"1"}
    assert {r["pages"] for r in rows if r["doc_key"] in spans} == {""}  # general publications: only the CBDC span
    path = tmp_path / "BLIND_CELLS_MB_test.xlsx"
    B.workbook(str(path), "MB", "2026-11-24", docs, rows, B.SCOPE_DEFAULT)
    monkeypatch.setattr(L, "LOCK", str(tmp_path / "BLIND_CELL_LOCK.csv"))
    return path, docs


def _fill(path, override=None):
    wb = load_workbook(path)
    ws = wb["KODOVANI"]
    head = [c.value for c in ws[1]]
    col = {h: i + 1 for i, h in enumerate(head)}
    for r in range(2, ws.max_row + 1):
        ws.cell(r, col["evidence_state"], "unknown")
        ws.cell(r, col["unknown_reason"], "never_addressed")
    # one valued cell: EU F4 yes
    r = next(r for r in range(2, ws.max_row + 1) if ws.cell(r, 1).value == "EU" and ws.cell(r, 2).value == "F4")
    vals = {"value": "yes", "decision_status": "considered", "implementation_status": "untested_or_unreported",
            "evidence_state": "documented", "unknown_reason": None, "basis": "architectural", "derivation": "explicit",
            "document_id": "EU-01", "page_index": 1, "quote": "Offline payments protect user privacy here."}
    vals.update(override or {})
    for k, v in vals.items():
        ws.cell(r, col[k]).value = v
    wb.save(path)


def test_lock_writes_template_file(built, tmp_path, monkeypatch):
    path, docs = built
    _fill(path)
    out = tmp_path / "locked"
    monkeypatch.setattr(sys, "argv", ["x", "--coder", "MB", "--xlsx", str(path), "--out", str(out)])
    L.main()
    cells = read(str(out / "BLIND_CELLS_MB_locked.csv"))
    assert len(cells) == 112
    eu = cells[("EU", "F4")]
    assert eu["value"] == "yes" and eu["text_route"] == docs[[d["code"] for d in docs].index("EU-01")]["route"]
    with open(L.LOCK, newline="", encoding="utf-8") as fh:
        lock = list(csv.DictReader(fh))
    assert lock[0]["coder"] == "MB" and lock[0]["valued"] == "1"
    with pytest.raises(SystemExit, match="already locked"):
        L.main()


@pytest.mark.parametrize("override,msg", [
    ({"quote": None}, "without document or quote"),
    ({"document_id": "AU-01"}, "not a document of EU"),
    ({"basis": None}, "without basis"),
    ({"value": "maybe"}, "value 'maybe'"),
    ({"value": None, "evidence_state": None}, "neither value nor evidence_state"),
])
def test_lock_refuses(built, tmp_path, monkeypatch, override, msg):
    path, _ = built
    _fill(path, override)
    monkeypatch.setattr(sys, "argv", ["x", "--coder", "MB", "--xlsx", str(path), "--out", str(tmp_path / "o")])
    with pytest.raises((SystemExit, ValueError), match=msg):
        L.main()
    assert not os.path.exists(L.LOCK)


def test_lock_refuses_folder_in_repo(built, monkeypatch):
    path, _ = built
    _fill(path)
    monkeypatch.setattr(sys, "argv", ["x", "--coder", "MB", "--xlsx", str(path), "--out", os.path.join(ROOT, "data")])
    with pytest.raises(SystemExit, match="outside the repository"):
        L.main()
