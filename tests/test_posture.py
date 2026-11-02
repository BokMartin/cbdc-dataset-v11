import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))
from derive import posture_level, g_indicators

def S(t, status, verified="exact_page", basis="policy"): return {"type": t, "status": status, "quote_verified": verified, "basis": basis}

def test_ladder():
    assert posture_level([]) == "P0"
    assert posture_level([S("LAWFUL_ACCESS", "endorsed"), S("PRIVACY_AS_RISK_OR_TRADEOFF", "considered")]) == "P0"   # non-counting types
    assert posture_level([S("PRINCIPLE", "endorsed")]) == "P1"
    assert posture_level([S("PRINCIPLE", "endorsed"), S("TIERED_LOW_ID", "considered")]) == "P2"
    assert posture_level([S("CB_NO_PERSONAL_DATA", "tested")]) == "P2"
    assert posture_level([S("CB_NO_PERSONAL_DATA", "endorsed")]) == "P3"
    assert posture_level([S("CB_NO_PERSONAL_DATA", "endorsed", verified="invalid")]) == "P0"   # unlocated quote never counts
    assert posture_level([S("PSP_HOLDS_IDENTITY", "", ) | {"implementation_status": "operational"}]) == "P3"

def test_g():
    g = g_indicators([S("CB_NO_PERSONAL_DATA", "considered", basis="policy"), S("CB_NO_PERSONAL_DATA", "endorsed", basis="architectural"), S("CB_SEES_DATA", "considered"), S("PET_TECHNIQUE", "tested", verified="fuzzy_candidate")])
    assert g["G2"] == {"value": "yes", "status": "endorsed", "basis": "architectural", "n": 2}
    assert g["G3"]["value"] == "yes" and g["G3"]["status"] == "considered"
    assert g["G6"]["value"] == "not_documented"   # only an unlocated claim
    assert g["G9"]["value"] == "not_documented"
