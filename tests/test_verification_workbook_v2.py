"""Offline tests of the two-pass verification workbooks (audit A5 finding 5, item 21). Synthetic cells only."""
import json
import os
import subprocess
import sys

import pytest
from openpyxl import load_workbook

HERE = os.path.dirname(__file__)
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "scripts", "review"))
import build_verification_workbook_v2 as v2  # noqa: E402

SECRET = "The central bank will never see the payer"


def cells(doc):
    def one(value, quote, page=5):
        return {"value": value, "document_id": doc, "page_index": page, "quote": quote, "decision_status": "endorsed",
                "implementation_status": "untested_or_unreported", "evidence_state": "documented", "basis": "architectural"}
    return {"claude": {"AU": {"cells": {"F1": one("no", SECRET), "F3": dict(one("none_stated", None), page_index="", document_id="")}},
                       "UK": {"cells": {"F7": one("no", "q uk")}}},
            "sol62": {"AU": {"cells": {"F1": one("no", SECRET, 6)}}},
            "deepseek": {"AU": {"cells": {"F1": one("yes", "other quote")}}}}


def test_keys_order_is_seeded_and_negative_search_split():
    docs = v2.documents(v2.PROJECTS)
    doc = next(d["doc_key"] for d in docs if d["project"] == "AU" and d["for_cells"] == "ano")
    r1, s1, drawn, n = v2.keys(cells(doc), docs, 7)
    r2, _, _, _ = v2.keys(cells(doc), docs, 7)
    assert [k["key"] for k in r1] == [k["key"] for k in r2] and {k["key"] for k in r1} == {"AU-F1", "UK-F7"}
    assert [k["key"] for k in s1] == ["AU-F3"]
    assert next(k for k in r1 if k["key"] == "UK-F7")["development"]
    assert len(drawn) == v2.N_EMPTY and ("AU", "F1") not in drawn


def test_pass1_hides_values_and_pass2_needs_the_lock(tmp_path, monkeypatch):
    monkeypatch.setattr(v2, "LOCK", str(tmp_path / "LOCK.csv"))
    docs = v2.documents(v2.PROJECTS)
    doc = next(d["doc_key"] for d in docs if d["project"] == "AU" and d["for_cells"] == "ano")
    read, search, drawn, _ = v2.keys(cells(doc), docs, 7)
    p1 = tmp_path / "p1.xlsx"
    v2.pass1(str(p1), "MB", "2026-11-26", read, search, drawn, docs, {})
    wb = load_workbook(p1, read_only=True)
    text = " ".join(str(c) for ws in ("PRUCHOD1", "HLEDANI") for row in wb[ws].iter_rows(values_only=True) for c in row if c)
    assert SECRET not in text and "claude" not in text.lower() and "endorsed" not in text
    assert v2.locked("MB") is None
    v2.lock_pass1("MB", str(p1))
    with pytest.raises(SystemExit):
        v2.lock_pass1("MB", str(p1))
    p2 = tmp_path / "p2.xlsx"
    v2.pass2(str(p2), "MB", "2026-11-26", read, docs, v2.read_pass1(str(p1)), v2.locked("MB")["sha256"])
    rows = list(load_workbook(p2, read_only=True)["PRUCHOD2"].iter_rows(values_only=True))
    au = [r for r in rows[1:] if r[1] == "AU-F1"]
    assert len(au) == 3 and {r[5] for r in au} == set(v2.MODEL_NAMES.values())  # one row per model, statuses not joined


def test_refuses_output_inside_the_repository(tmp_path):
    f = tmp_path / "c.json"; f.write_text(json.dumps({}))
    r = subprocess.run([sys.executable, os.path.join(ROOT, "scripts/review/build_verification_workbook_v2.py"), "--cells",
                        f"claude={f}", f"sol62={f}", f"deepseek={f}", "--out", os.path.join(ROOT, "x"), "--date", "2026-11-26"],
                       capture_output=True, text=True)
    assert r.returncode != 0 and "outside the repository" in r.stderr
