"""Two-axis CBDC privacy index (PROPOSAL; option B chosen by MB on 21 Nov 2026, DS to confirm; see
docs/PRIVACY_INDEX_SPEC_DRAFT_2026-11-21.md and ADR-009). Run only on synthetic cells until the definition is
frozen and registered before F-cell production.

Axis 1, **stated design (any status)**: how far the design the documents describe keeps a retail payment from being
routinely attributed to an identified person, from the cells in CORE (version 1: F1, F2, F4, F7; version 2, below:
eight cells). Values are taken at any decision or implementation
status, so a considered design scores like an operated one on this axis; the status of every component is shown beside
it (axis 2) and the admissible-only version (contract §5, rule C) is computed for every project.

v2 (MB, 21 Nov 21:31: an index that rests on F1 alone is useless; all F-cells must matter): eight privacy cells
F1, F2, F3, F4, F7, F8, F9, F10, scored by SCORE, primary aggregation the compensatory MEAN. The lexicographic rule
below (review of 21 Nov, item 5) and the cap are kept only as sensitivity variants.
Lexicographic variant: F1 first, then the mean of the other components.
Embedded on [0, 1]: F1 protective -> 0.5 + 0.5 * rest; F1 not protective -> 0.5 * rest; F1 undetermined -> the
union of both. Every project with a protective F1 therefore lies above every project with a non-protective F1, and the
0.5 is the split point of the two classes, not a tuning constant. The compensatory mean and the old cap are kept as
alternative rules for the sensitivity analysis.

Missing cells are never filled. Every score is an interval [lower, upper]: lower counts an undetermined component
as not protective, upper as protective (the bound logic of contract §8.4).

Axis 2, **commitment profile**: the rung of each component (considered 1, tested 2, endorsed 3, operational 4; none 0)
and the number of components at rung 3 or above out of the cells in CORE (8 in version 2, 4 in version 1; fixed
denominator). No mean of ranks (review item 4).

Talk labels never enter the index.
"""
import random

from derive import _status, admissible

# Score of each cell value for the reference user's privacy (v2 after MB, 21 Nov 21:31: "all F relevant").
# F3 and F9 have a direction the authors must confirm (AMBIGUOUS); a sensitivity variant drops them.
SCORE = {
    "F1": {"no": 1, "yes": 0},                         # CB cannot link online payments to a person
    "F2": {"no": 1, "yes": 0},                         # PSP cannot link
    "F3": {"via_psp": 1, "via_cb": 0, "via_both": 0},  # lawful access only through intermediaries, as for bank accounts
    "F4": {"yes": 1, "no": 0},                         # private offline mode
    "F7": {"yes": 1, "no": 0},                         # low-identity route
    "F8": {"no": 1, "yes": 0},                         # ordinary wallet without verified identity
    "F9": {"no": 1, "yes": 0},                         # no exceptional re-identification process
    "F10": {"no": 1, "yes": 0},                        # no programmable restrictions on use
}
PROTECTIVE = {f: next(v for v, x in m.items() if x == 1) for f, m in SCORE.items()}
CORE = ("F1", "F2", "F3", "F4", "F7", "F8", "F9", "F10")
CORE4 = ("F1", "F2", "F4", "F7")  # v1 definition, kept as a sensitivity variant
AMBIGUOUS = ("F3", "F9")
OPTIONAL = ()
RULES = ("mean", "lexicographic", "cap")
CAP = 0.5
RUNG = {"considered": 1, "tested": 2, "endorsed": 3, "operational": 4}


def is_leaning(cell):
    """Cell status LEANING (ADR-010 draft, PR 3): a value taken from an INCLINED document, set only when no document of
    the competent body gives one. Never a commitment."""
    return bool(cell) and (str(cell.get("decision_status", "")).strip().lower() == "leaning"
                           or str(cell.get("leaning", "")).strip().lower() in ("true", "1", "yes"))


def component(cell, fid, view="stated", exclude_route_d=False, exclude_inferred=False, include_leaning=False):
    """1 protective, 0 not protective, None undetermined. view: 'stated' (any status) or 'admissible' (rule C).
    A LEANING cell is undetermined in the primary index (it only bounds the interval); include_leaning=True scores it
    at its value (sensitivity variant, never in the admissible view)."""
    if not cell:
        return None
    if is_leaning(cell) and (not include_leaning or view == "admissible"):
        return None
    if view == "admissible" and not admissible(cell, categorical=set(SCORE[fid]) if fid == "F3" else None):
        return None
    if exclude_route_d and str(cell.get("text_route", "")).strip().upper() == "D":
        return None
    if exclude_inferred and str(cell.get("derivation", "")).strip().lower() == "inferred":
        return None
    if str(cell.get("coder_disagreement", "")).strip().lower() in ("true", "1", "yes"):
        return None  # an unresolved disagreement between the blind coders widens the interval
    dec, _ = _status(cell)
    if dec in ("rejected", "superseded"):
        return None
    v = str(cell.get("value", "")).strip().lower()
    return SCORE[fid].get(v)


def rung(cell, fid=None):
    """Commitment rung of a cell that carries a scored value (yes/no, or the F3 categories)."""
    valid = set(SCORE[fid]) if fid in SCORE else {"yes", "no"}
    if not cell or str(cell.get("value", "")).strip().lower() not in valid:
        return 0
    if is_leaning(cell):
        return 0  # below every status of the competent body's own documents
    dec, impl = _status(cell)
    if dec in ("rejected", "superseded"):
        return 0
    if impl == "operational":
        return 4
    if dec == "endorsed":
        return 3
    if impl == "tested":
        return 2
    return 1 if dec == "considered" else 0


def _wmean(vals, weights, fill):
    total = sum(weights[f] for f in vals)
    return sum(weights[f] * (fill if v is None else v) for f, v in vals.items()) / total


def axis1(cells, rule="mean", weights=None, include=(), drop=(), cells_used=CORE, **kw):
    """Interval of the stated-design score (or admissible, with view='admissible')."""
    comps = [f for f in tuple(cells_used) + tuple(include) if f not in drop]
    comp = {f: component(cells.get(f), f, **kw) for f in comps}
    w = {f: 1.0 for f in comps}
    if weights:
        w.update({f: weights[f] for f in comps if f in weights})
    rest = {f: v for f, v in comp.items() if f != "F1"}
    f1 = comp.get("F1")
    if rule == "lexicographic" and "F1" in comp and rest:
        r_lo, r_hi = _wmean(rest, w, 0), _wmean(rest, w, 1)
        if f1 == 1:
            lo, hi = 0.5 + 0.5 * r_lo, 0.5 + 0.5 * r_hi
        elif f1 == 0:
            lo, hi = 0.5 * r_lo, 0.5 * r_hi
        else:
            lo, hi = 0.5 * r_lo, 0.5 + 0.5 * r_hi
    else:
        lo, hi = _wmean(comp, w, 0), _wmean(comp, w, 1)
        if rule == "cap" and f1 == 0:  # only a DETERMINED non-protective F1 caps (fixes the bug found in review)
            lo, hi = min(lo, CAP), min(hi, CAP)
    leaning = [f for f in comps if is_leaning(cells.get(f)) and comp[f] is not None]
    determined = sum(v is not None for v in comp.values())
    return {"lower": round(lo, 4), "upper": round(hi, 4), "width": round(hi - lo, 4), "components": comp, "rule": rule,
            "determined": determined, "n_components": len(comp), "leaning_scored": leaning,
            "rests_on_leaning": bool(leaning) and len(leaning) * 2 >= determined}


def axis2(cells, cells_used=CORE):
    """Commitment profile: rung per cell and the count at rung >= 3 (endorsed or operational) out of all cells."""
    profile = {f: rung(cells.get(f), f) for f in cells_used}
    return {"profile": profile, "decided": sum(r >= 3 for r in profile.values()), "n_cells": len(profile),
            "stated_only": sum(1 <= r <= 2 for r in profile.values()),
            "leaning": [f for f in cells_used if is_leaning(cells.get(f))]}


def privacy_index(cells, **kw):
    """Both axes plus the admissible-only robustness interval."""
    kw.pop("view", None)
    return {"stated": axis1(cells, view="stated", **kw), "commitment": axis2(cells),
            "admissible": axis1(cells, view="admissible", **kw),
            "stated_with_leaning": axis1(cells, view="stated", include_leaning=True, **kw)}


# ---------- separation of projects (diagnostic until DS confirms ordering, review item 8) ----------
def separated(a, b):
    """a lies above b: non-overlapping intervals, or, under the lexicographic rule, a protective F1 against a
    non-protective one (the two classes meet at 0.5, so the tie at the split point is resolved by the class)."""
    if a.get("rule") == b.get("rule") == "lexicographic":
        fa, fb = a["components"].get("F1"), b["components"].get("F1")
        if fa == 1 and fb == 0:
            return True
        if fa == 0 and fb == 1:
            return False
    return a["lower"] > b["upper"]


def separated_pairs(scores):
    return {(p, q) for p, a in scores.items() for q, b in scores.items() if p != q and separated(a, b)}


def share_separated(scores):
    n = len(scores)
    return len(separated_pairs(scores)) / (n * (n - 1) / 2) if n > 1 else 0.0


# ---------- B1: uncertainty and sensitivity analysis (runs now on synthetic data) ----------
def _dirichlet(rng, keys):
    g = [rng.gammavariate(1.0, 1.0) for _ in keys]
    return {k: x / sum(g) for k, x in zip(keys, g)}


def uncertainty_analysis(projects, draws=500, seed=20261121, view="stated"):
    """Share of the baseline separated pairs that survive (a) Dirichlet(1) weight draws, (b) the alternative rules
    (lexicographic, cap), (c) leaving out each cell, (d) the admissible view, (e) without the ambiguous F3 and F9,
    (f) the four cells of v1 only, (g) without route-D or inferred cells."""
    base_scores = {p: axis1(c, view=view) for p, c in projects.items()}
    base = separated_pairs(base_scores)
    out = {"n_projects": len(projects), "baseline_separated_pairs": len(base), "baseline_share": round(share_separated(base_scores), 4)}

    def kept(variant_scores):
        cur = separated_pairs(variant_scores)
        return None if not base else round(len(base & cur) / len(base), 4)

    rng = random.Random(seed)
    counts = {pair: 0 for pair in base}
    for _ in range(draws):
        w = _dirichlet(rng, CORE)
        cur = separated_pairs({p: axis1(c, view=view, weights=w) for p, c in projects.items()})
        for pair in base:
            counts[pair] += pair in cur
    out["weights_kept_in_all_draws"] = None if not base else round(sum(v == draws for v in counts.values()) / len(base), 4)
    out["weights_mean_kept"] = None if not base else round(sum(counts.values()) / (len(base) * draws), 4)
    for rule in ("lexicographic", "cap"):
        out[f"rule_{rule}_kept"] = kept({p: axis1(c, view=view, rule=rule) for p, c in projects.items()})
    for f in CORE:
        out[f"drop_{f}_kept"] = kept({p: axis1(c, view=view, drop=(f,)) for p, c in projects.items()})
    out["admissible_view_kept"] = kept({p: axis1(c, view="admissible") for p, c in projects.items()})
    out["without_F3_F9_kept"] = kept({p: axis1(c, view=view, drop=AMBIGUOUS) for p, c in projects.items()})
    out["core4_only_kept"] = kept({p: axis1(c, view=view, cells_used=CORE4) for p, c in projects.items()})
    out["no_route_D_kept"] = kept({p: axis1(c, view=view, exclude_route_d=True) for p, c in projects.items()})
    out["with_leaning_kept"] = kept({p: axis1(c, view=view, include_leaning=True) for p, c in projects.items()})
    out["no_inferred_kept"] = kept({p: axis1(c, view=view, exclude_inferred=True) for p, c in projects.items()})
    return out


# ---------- review item 3: how many pairs can be separated at a given coverage (before the freeze) ----------
def simulate_separation(coverage, p_protective=0.5, n_projects=44, draws=200, seed=20261121, view="stated"):
    """coverage: probability that each core cell carries a value (dict per cell). Synthetic projects; the result is a
    design argument, not a measurement. Returns mean and 5th/95th percentile of the share of separated pairs."""
    rng = random.Random(seed)
    shares = []
    for _ in range(draws):
        scores = {}
        for i in range(n_projects):
            cells = {}
            for f in CORE:
                if rng.random() < coverage.get(f, 0):
                    protective = rng.random() < p_protective
                    v = PROTECTIVE[f] if protective else next(x for x, sc in SCORE[f].items() if sc == 0)
                    cells[f] = {"value": v, "evidence_state": "documented", "decision_status": "endorsed"}
            scores[i] = axis1(cells, view=view)
        shares.append(share_separated(scores))
    shares.sort()
    return {"mean": round(sum(shares) / len(shares), 4), "p05": round(shares[int(0.05 * len(shares))], 4),
            "p95": round(shares[int(0.95 * len(shares)) - 1], 4)}
