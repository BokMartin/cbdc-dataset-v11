import csv, os, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__)); SCRIPT = os.path.join(HERE, "..", "scripts", "extraction", "compare_modes.py")
COLS = ["cell", "value", "evidence_state", "claim_status", "doc", "page", "processing_state"]


def write(path, rows):
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLS); w.writeheader(); w.writerows(rows)


def run(a, b, out, extra=()):
    r = subprocess.run([sys.executable, SCRIPT, a, b, "--labels", "s", "t", "--out", out, *extra], capture_output=True, text=True); return r.stdout + f"[exit {r.returncode}]"


def test_levels_and_invalid():
    d = tempfile.mkdtemp()
    A = [{"cell": "F1", "value": "no", "evidence_state": "partial", "claim_status": "tested", "doc": "7", "page": "10", "processing_state": "ok"},
         {"cell": "F2", "value": "yes", "evidence_state": "partial", "claim_status": "tested", "doc": "7", "page": "9", "processing_state": "ok"},
         {"cell": "F4", "value": "n/d", "evidence_state": "unknown", "claim_status": "", "doc": "", "page": "", "processing_state": "ok"}]
    B = [dict(A[0]), dict(A[1], page="11"), {"cell": "F4", "value": "yes", "evidence_state": "partial", "claim_status": "option", "doc": "4", "page": "8", "processing_state": "ok"}, {"cell": "F7", "value": "no", "evidence_state": "partial", "claim_status": "option", "doc": "2", "page": "26", "processing_state": "ok"}]
    write(f"{d}/a.csv", A); write(f"{d}/b.csv", B)
    out = run(f"{d}/a.csv", f"{d}/b.csv", f"{d}/c.csv")
    assert "VALID" in out and "INVALID" not in out
    assert "{'full': 1, 'value': 1, 'differ': 1, 'missing': 1}" in out, out
    # a failed document in one fill makes the whole comparison invalid (ADR-001 NO3 / E11)
    B[0]["processing_state"] = "processing_failed"; write(f"{d}/b.csv", B)
    out = run(f"{d}/a.csv", f"{d}/b.csv", f"{d}/c.csv")
    assert "INVALID comparison" in out and "processing_failed" in out


def test_header_only_fill_is_invalid_with_schema():
    import json
    d = tempfile.mkdtemp(); write(f"{d}/a.csv", [{"cell": "F1", "value": "no", "evidence_state": "documented", "claim_status": "adopted", "doc": "1", "page": "2", "processing_state": "ok"}]); write(f"{d}/b.csv", [])
    json.dump({"cells": ["F1", "F2"]}, open(f"{d}/schema.json", "w"))
    out = run(f"{d}/a.csv", f"{d}/b.csv", f"{d}/c.csv", ["--schema", f"{d}/schema.json"])
    assert "INVALID" in out and "missing expected cells" in out and "[exit 2]" in out
