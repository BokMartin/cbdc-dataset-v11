"""Non-API validity tests for the extractor (ADR-001 E17): strict parsing, strict output validation, no salvage."""
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts", "extraction"))
import extract_api as E
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
schema = json.load(open(os.path.join(ROOT, "schema/cells_v1_1.json")))

def good_rows():
    rows = []
    for c in schema["cells"]:
        rows.append({"cell": c, "value": (schema["values"][c][0] if schema["values"].get(c) else "x"), "evidence_state": "documented", "claim_status": "adopted", "derivation": "explicit"})
    return rows

def test_truncated_array_is_failure_not_salvage():
    import pytest
    with pytest.raises(ValueError): E.parse_array('[{"cell": "F1 CB_LINK_ONLINE", "value": "no"}, {"cell": "F2 PSP_LINK_ONLINE", "val')

def test_complete_fill_validates():
    by, problems = E.validate_fill(good_rows(), schema); assert not problems and len(by) == len(schema["cells"])

def test_missing_and_duplicate_cells_flagged():
    rows = good_rows()[:-1]; rows.append(dict(rows[0]))
    by, problems = E.validate_fill(rows, schema)
    assert any("missing cell" in p for p in problems) and any("duplicate" in p for p in problems)

def test_bad_enum_flagged_and_unknown_normalised():
    rows = good_rows(); rows[0]["value"] = "maybe"; rows[1]["value"] = "unknown"; rows[2]["evidence_state"] = "strong"
    by, problems = E.validate_fill(rows, schema)
    assert any("maybe" in p for p in problems) and by["F2 PSP_LINK_ONLINE"]["value"] == "n/d" and any("evidence_state" in p for p in problems)

def test_prompts_carry_contract_and_cells():
    P = E.build_prompts(schema, "CONTRACT TEXT MARKER")
    assert all("CONTRACT TEXT MARKER" in v for v in P.values()) and all("F12 LEDGER_TECHNOLOGY" in v for v in P.values())
    assert "no cap" in P["stage1"] and "silence about other routes gives n/d" in P["single"]
