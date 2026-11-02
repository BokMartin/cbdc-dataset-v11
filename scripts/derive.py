"""Single derivation module for architecture type and outcomes (ADR-001 E17, consultation rule C).

Used by the analysis, the exports and the website. A cell enters the *commitment* derivation only if it is admissible:
value in {yes, no}, evidence_state == documented, status endorsed/adopted or operational, no conflict. Everything else is
undetermined for commitment purposes. A separate *permissive* derivation (values only, any status) is available for the
labelled option/test view and for the diagnostic table of "commitments that disappear under strict rules"; it is never
used for Y or for the primary type.

Status vocabulary: contract v1.1 uses claim_status ∈ {option, adopted, tested, operational}; contract v2 will use
decision_status × implementation_status. ADMISSIBLE_STATUS covers both via the crosswalk below.
"""
ADMISSIBLE_STATUS = {"adopted", "operational", "endorsed"}  # v1.1 labels + v2 decision_status 'endorsed'
YESNO = {"yes", "no"}


def admissible(cell):
    """True if a cell may set a commitment value (rule C)."""
    if not cell: return False
    v = str(cell.get("value", "")).strip().lower()
    ev = str(cell.get("evidence_state", "")).strip().lower()
    st = str(cell.get("claim_status", cell.get("decision_status", ""))).strip().lower()
    impl = str(cell.get("implementation_status", "")).strip().lower()
    return v in YESNO and ev == "documented" and (st in ADMISSIBLE_STATUS or impl == "operational")


def _val(cell, strict):
    if not cell: return None
    if strict and not admissible(cell): return None
    v = str(cell.get("value", "")).strip().lower()
    return v if v in YESNO else None


def architecture_type(cells, strict=True):
    """Return (type_string, possible_set). strict=True → commitment type; strict=False → permissive (values only)."""
    f1, f2, f4 = _val(cells.get("F1"), strict), _val(cells.get("F2"), strict), _val(cells.get("F4"), strict)
    online = {"yes": {"A"}, "no": None}.get(f1) if f1 else {"A", "B", "C"}
    if f1 == "no": online = {"B"} if f2 == "yes" else ({"C"} if f2 == "no" else {"B", "C"})
    offline = {"yes": {"1"}, "no": {"0"}}.get(f4) if f4 else {"0", "1"}
    possible = sorted(o + f for o in online for f in offline)
    label = possible[0] if len(possible) == 1 else ("?" if len(possible) == 6 else "/".join(sorted(online)) + ("?" if len(offline) == 2 else next(iter(offline))))
    return label, possible


def y1(cells, strict=True):
    v = _val(cells.get("F1"), strict); return None if v is None else (1 if v == "no" else 0)


def y3(cells, strict=True):
    v = _val(cells.get("F7"), strict); return None if v is None else (1 if v == "yes" else 0)


def summary(cells):
    """Both views side by side, for exports and the website panel."""
    t_strict, p_strict = architecture_type(cells, True); t_perm, p_perm = architecture_type(cells, False)
    return {"type_commitment": t_strict, "possible_commitment": p_strict, "type_permissive": t_perm, "possible_permissive": p_perm,
            "y1_commitment": y1(cells, True), "y1_permissive": y1(cells, False), "y3_commitment": y3(cells, True), "y3_permissive": y3(cells, False),
            "admissible_cells": sorted(k for k, c in cells.items() if k != "F11" and admissible(c))}


if __name__ == "__main__":
    # self-test: Norway-like case — F1 no/partial/option must NOT give Y1 = 1 under strict derivation
    no = {"F1": {"value": "no", "evidence_state": "partial", "claim_status": "option"}, "F2": {"value": "yes", "evidence_state": "partial", "claim_status": "option"}, "F4": {"value": "n/d", "evidence_state": "unknown", "claim_status": ""}, "F7": {"value": "n/d"}}
    s = summary(no); assert s["y1_commitment"] is None and s["y1_permissive"] == 1 and s["type_commitment"] == "?" and s["type_permissive"] == "B?", s
    uk = {"F1": {"value": "no", "evidence_state": "documented", "claim_status": "adopted"}, "F2": {"value": "yes", "evidence_state": "documented", "claim_status": "adopted"}, "F4": {"value": "no", "evidence_state": "partial", "claim_status": "option"}, "F7": {"value": "no", "evidence_state": "documented", "claim_status": "adopted"}}
    s = summary(uk); assert s["y1_commitment"] == 1 and s["type_commitment"] == "B?" and s["type_permissive"] == "B0" and s["y3_commitment"] == 0, s
    print("derive.py self-test ok:", s)


# ---------- privacy-posture layer (contract v2 §6b) ----------
ARCH_TYPES = {"CB_NO_PERSONAL_DATA", "CB_SEES_DATA", "PSP_HOLDS_IDENTITY", "PSEUDONYMISATION", "TIERED_LOW_ID", "OFFLINE_PRIVACY", "ANONYMITY_REJECTED", "PET_TECHNIQUE"}
PRINCIPLE_TYPES = {"PRINCIPLE", "LEGAL_COMMITMENT", "DATA_MINIMISATION", "USER_CONTROL_CONSENT", "NO_COMMERCIAL_USE"}
LOCATED = {"exact_page", "spanning_pages"}
G_INDICATORS = {"G1": "PRINCIPLE", "G2": "CB_NO_PERSONAL_DATA", "G3": "CB_SEES_DATA", "G4": "TIERED_LOW_ID", "G5": "ANONYMITY_REJECTED", "G6": "PET_TECHNIQUE", "G7": "DATA_MINIMISATION", "G8": "LEGAL_COMMITMENT", "G9": "PRIVACY_AS_RISK_OR_TRADEOFF"}
STATUS_RANK = {"endorsed": 4, "operational": 4, "tested": 2, "considered": 1, "unclear": 0, "rejected": 0, "": 0}


def _committed(s):
    st = str(s.get("decision_status", s.get("status", ""))).lower(); impl = str(s.get("implementation_status", "")).lower()
    return st in ("endorsed", "operational") or impl == "operational"


def _located(s): return str(s.get("quote_verified", s.get("verified", ""))).lower() in LOCATED


def posture_level(statements):
    """P3 / P2 / P1 / P0 from located statement claims (contract v2 §6b.2). Unlocated claims never count."""
    S = [s for s in statements if _located(s)]
    arch = [s for s in S if s.get("type") in ARCH_TYPES]
    if any(_committed(s) for s in arch): return "P3"
    if arch: return "P2"
    if any(s.get("type") in PRINCIPLE_TYPES for s in S): return "P1"
    return "P0"


def g_indicators(statements):
    """G1–G9: yes / not_documented with highest status and basis of the strongest supporting located claim (§6b.3)."""
    out = {}
    for g, t in G_INDICATORS.items():
        sup = [s for s in statements if s.get("type") == t and _located(s)]
        if not sup: out[g] = {"value": "not_documented", "status": "", "basis": "", "n": 0}; continue
        best = max(sup, key=lambda s: STATUS_RANK.get(str(s.get("decision_status", s.get("status", ""))).lower(), 0))
        out[g] = {"value": "yes", "status": str(best.get("decision_status", best.get("status", ""))).lower(), "basis": best.get("basis", ""), "n": len(sup)}
    return out


def posture_summary(statements):
    return {"posture_level": posture_level(statements), "g": g_indicators(statements), "n_located": sum(1 for s in statements if _located(s)), "n_statements": len(statements)}
