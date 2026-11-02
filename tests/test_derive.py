"""The status gate: option-level or partial cells never set a commitment outcome (rule C)."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))
import derive
def c(v, ev="documented", st="adopted"): return {"value": v, "evidence_state": ev, "claim_status": st}
def test_option_no_does_not_give_y1():
    assert derive.y1({"F1": c("no", "partial", "option")}) is None
    assert derive.y1({"F1": c("no", "documented", "option")}) is None
    assert derive.y1({"F1": c("no", "partial", "adopted")}) is None
def test_symmetry():
    assert derive.y1({"F1": c("yes", "documented", "option")}) is None
    assert derive.y1({"F1": c("yes")}) == 0 and derive.y1({"F1": c("no")}) == 1
def test_type_partial_when_f4_option():
    t, poss = derive.architecture_type({"F1": c("no"), "F2": c("yes"), "F4": c("no", "partial", "option")})
    assert t == "B?" and poss == ["B0", "B1"]
def test_operational_counts():
    assert derive.y1({"F1": c("yes", "documented", "operational")}) == 0
def test_v2_fields():
    assert derive.admissible({"value": "no", "evidence_state": "documented", "decision_status": "endorsed"})
    assert not derive.admissible({"value": "no", "evidence_state": "documented", "decision_status": "considered", "implementation_status": "tested"})


def test_rule_c_full_gate():
    from derive import admissible
    base = {"value": "no", "evidence_state": "documented"}
    assert admissible(base | {"decision_status": "endorsed", "implementation_status": "untested_or_unreported"})
    assert admissible(base | {"decision_status": "unclear", "implementation_status": "operational"})
    assert not admissible(base | {"decision_status": "rejected", "implementation_status": "operational"})     # audit item 2
    assert not admissible(base | {"decision_status": "superseded", "implementation_status": "operational"})
    assert not admissible(base | {"decision_status": "endorsed", "staff_research": "Y"})
    assert not admissible(base | {"decision_status": "endorsed", "conflict": "true"})
    assert admissible(base | {"claim_status": "", "decision_status": "endorsed"})                             # blank legacy field never shadows v2
    assert admissible(base | {"claim_status": "adopted"}) and not admissible(base | {"claim_status": "tested"})
    assert admissible({"value": "via_PSP", "evidence_state": "documented", "decision_status": "endorsed"}, categorical={"via_psp", "via_cb", "via_both", "none_stated"})
    assert not admissible({"value": "via_PSP", "evidence_state": "documented", "decision_status": "endorsed"})  # yes/no cells reject categorical values
