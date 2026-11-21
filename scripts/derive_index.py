"""Two-axis CBDC privacy index (PROPOSAL; option B chosen by MB on 21 Nov 2026, DS to confirm; see
docs/PRIVACY_INDEX_SPEC_DRAFT_2026-11-21.md and ADR-009). Run only on synthetic cells until the definition is
frozen and registered before F-cell production.

Axis 1, **stated design (any status)**: how far the design the documents describe keeps a retail payment from being
routinely attributed to an identified person, from F1, F2, F4, F7. Values are taken at any decision or implementation
status, so a considered design scores like an operated one on this axis; the status of every component is shown beside
it (axis 2) and the admissible-only version (contract §5, rule C) is computed for every project.

Primary aggregation is **lexicographic** (review of 21 Nov, item 5): F1 first, then the mean of the other components.
Embedded on [0, 1]: F1 protective -> 0.5 + 0.5 * rest; F1 not protective -> 0.5 * rest; F1 undetermined -> the
union of both. Every project with a protective F1 therefore lies above every project with a non-protective F1, and the
0.5 is the split point of the two classes, not a tuning constant. The compensatory mean and the old cap are kept as
alternative rules for the sensitivity analysis.

Missing cells are never filled. Every score is an interval [lower, upper]: lower counts an undetermined component
as not protective, upper as protective (the bound logic of contract §8.4).

Axis 2, **commitment profile**: the rung of each component (considered 1, tested 2, endorsed 3, operational 4; none 0)
and the number of components at rung 3 or above out of the 4 (fixed denominator). No mean of ranks (review item 4).

Talk labels never enter the index.
"""
import random

from derive import _status, admissible

PROTECTIVE = {"F1": "no", "F2": "no", "F4": "yes", "F7": "yes", "F8": "no", "F10": "no"}
CORE = ("F1", "F2", "F4", "F7")
REST = ("F2", "F4", "F7")
OPTIONAL = ("F8", "F10")  # sensitivity only
RULES = ("lexicographic", "mean", "cap")
CAP = 0.5
RUNG = {"considered": 1, "tested": 2, "endorsed": 3, "operational": 4}


def component(cell, fid, view="stated", exclude_route_d=False, exclude_inferred=False):
    """1 protective, 0 not protective, None undetermined. view: 'stated' (any status) or 'admissible' (rule C)."""
    if not cell:
        return None
    if view == "admissible" and not admissible(cell):
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
    if v not in ("yes", "no"):
        return None
    return 1 if v == PROTECTIVE[fid] else 0


def rung(cell):
    """Commitment rung of a cell that carries a yes/no value."""
    if not cell or str(cell.get("value", "")).strip().lower() not in ("yes", "no"):
        return 0
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


def axis1(cells, rule="lexicographic", weights=None, include=(), drop=(), **kw):
    """Interval of the stated-design score (or admissible, with view='admissible')."""
    comps = [f for f in CORE + tuple(include) if f not in drop]
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
    return {"lower": round(lo, 4), "upper": round(hi, 4), "width": round(hi - lo, 4), "components": comp, "rule": rule,
            "determined": sum(v is not None for v in comp.values()), "n_components": len(comp)}


def axis2(cells):
    """Commitment profile: rung per core component and the count at rung >= 3 out of 4."""
    profile = {f: rung(cells.get(f)) for f in CORE}
    return {"profile": profile, "decided_of_4": sum(r >= 3 for r in profile.values())}


def privacy_index(cells, **kw):
    """Both axes plus the admissible-only robustness interval."""
    kw.pop("view", None)
    return {"stated": axis1(cells, view="stated", **kw), "commitment": axis2(cells),
            "admissible": axis1(cells, view="admissible", **kw)}


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
    (mean, cap), (c) leaving out each component, (d) the admissible view, (e) adding F8 and F10."""
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
    for rule in ("mean", "cap"):
        out[f"rule_{rule}_kept"] = kept({p: axis1(c, view=view, rule=rule) for p, c in projects.items()})
    for f in CORE:
        out[f"drop_{f}_kept"] = kept({p: axis1(c, view=view, drop=(f,)) for p, c in projects.items()})
    out["admissible_view_kept"] = kept({p: axis1(c, view="admissible") for p, c in projects.items()})
    out["with_F8_F10_kept"] = kept({p: axis1(c, view=view, include=OPTIONAL) for p, c in projects.items()})
    out["no_route_D_kept"] = kept({p: axis1(c, view=view, exclude_route_d=True) for p, c in projects.items()})
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
                if rng.random() < coverage[f]:
                    protective = rng.random() < p_protective
                    v = PROTECTIVE[f] if protective else ("yes" if PROTECTIVE[f] == "no" else "no")
                    cells[f] = {"value": v, "evidence_state": "documented", "decision_status": "endorsed"}
            scores[i] = axis1(cells, view=view)
        shares.append(share_separated(scores))
    shares.sort()
    return {"mean": round(sum(shares) / len(shares), 4), "p05": round(shares[int(0.05 * len(shares))], 4),
            "p95": round(shares[int(0.95 * len(shares)) - 1], 4)}
