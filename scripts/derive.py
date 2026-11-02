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
