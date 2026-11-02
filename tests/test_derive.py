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
