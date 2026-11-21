"""Exploratory commitment-based privacy index (PROPOSAL, not adopted; see docs/PRIVACY_INDEX_PROPOSAL_2026-11-21.md, ADR-008 draft).

Built only from F-cells of the commitment layer (contract v12). Talk labels never enter it. Missing cells are never filled:
the index is an interval [lower, upper], where lower treats every undetermined component as not protective and upper
as protective (the same bound logic as contract §8.4 for Y1). A determined, non-protective F1 caps the index (gate),
because no other component offsets routine attribution of payments to persons by the central bank.

Run only on synthetic cells until the definition is frozen and registered before F-cell production.
"""
import random

from derive import admissible

# cell id -> the value that protects the reference user's privacy
PROTECTIVE = {"F1": "no", "F2": "no", "F4": "yes", "F7": "yes", "F8": "no", "F10": "no"}
# dimensions of the primary definition: A state/central bank, B intermediaries, C identity at entry, D offline
DIMENSIONS = {"A": ["F1"], "B": ["F2"], "C": ["F7"], "D": ["F4"]}
OPTIONAL = {"F8": "C", "F10": "E"}  # sensitivity only: F8 joins C, F10 forms its own dimension E
DEFAULT_CAP = 0.5


def _component(cell, fid, strict, exclude_route_d, exclude_inferred):
    """1 protective, 0 not protective, None undetermined."""
    if not cell:
        return None
    if strict and not admissible(cell):
        return None
    if exclude_route_d and str(cell.get("text_route", "")).strip().upper() == "D":
        return None
    if exclude_inferred and str(cell.get("derivation", "")).strip().lower() == "inferred":
        return None
    v = str(cell.get("value", "")).strip().lower()
    if v not in ("yes", "no"):
        return None
    return 1 if v == PROTECTIVE[fid] else 0


def dimensions_for(include=()):
    dims = {k: list(v) for k, v in DIMENSIONS.items()}
    for fid in include:
        dims.setdefault(OPTIONAL[fid], []).append(fid)
    return dims


def _score(comp, dims, weights, cap, fill):
    vals = {f: (fill if v is None else v) for f, v in comp.items()}
    total = sum(weights[d] for d in dims)
    s = sum(weights[d] * sum(vals[f] for f in fs) / len(fs) for d, fs in dims.items()) / total
    if cap is not None and vals.get("F1") == 0:
        s = min(s, cap)
    return s


def privacy_index(cells, strict=True, include=(), cap=DEFAULT_CAP, weights=None, exclude_route_d=False, exclude_inferred=False, drop=()):
    """Return dict with lower, upper, width, determined, n_components, components. `drop` removes components (leave-one-out)."""
    dims = dimensions_for(include)
    dims = {d: [f for f in fs if f not in drop] for d, fs in dims.items()}
    dims = {d: fs for d, fs in dims.items() if fs}
    weights = weights or {d: 1.0 for d in dims}
    comp = {f: _component(cells.get(f), f, strict, exclude_route_d, exclude_inferred) for fs in dims.values() for f in fs}
    lo, hi = _score(comp, dims, weights, cap, 0), _score(comp, dims, weights, cap, 1)
    return {"lower": round(lo, 4), "upper": round(hi, 4), "width": round(hi - lo, 4),
            "determined": sum(v is not None for v in comp.values()), "n_components": len(comp), "components": comp}


def ranked_above(a, b):
    """a is ranked above b only if their intervals do not overlap."""
    return a["lower"] > b["upper"]


def ordered_pairs(results):
    """Set of (p, q) with p ranked above q."""
    return {(p, q) for p, a in results.items() for q, b in results.items() if p != q and ranked_above(a, b)}


def weight_sensitivity(projects, draws=1000, seed=20261121, **kw):
    """Dirichlet(1) weights over the dimensions; returns the share of baseline ordered pairs kept in every draw and on average."""
    rng = random.Random(seed)
    base = ordered_pairs({p: privacy_index(c, **kw) for p, c in projects.items()})
    if not base:
        return {"baseline_pairs": 0, "kept_all_draws": None, "mean_kept": None}
    dims = list(dimensions_for(kw.get("include", ())))
    kept_counts = {pair: 0 for pair in base}
    for _ in range(draws):
        g = [rng.gammavariate(1.0, 1.0) for _ in dims]
        w = {d: x / sum(g) for d, x in zip(dims, g)}
        cur = ordered_pairs({p: privacy_index(c, weights=w, **kw) for p, c in projects.items()})
        for pair in base:
            kept_counts[pair] += pair in cur
    return {"baseline_pairs": len(base), "kept_all_draws": sum(v == draws for v in kept_counts.values()) / len(base),
            "mean_kept": sum(kept_counts.values()) / (len(base) * draws)}


SENSITIVITY_VARIANTS = {
    "primary": {},
    "status_attached": {"strict": False},
    "with_F8_F10": {"include": ("F8", "F10")},
    "no_route_D": {"exclude_route_d": True},
    "no_inferred": {"exclude_inferred": True},
    "no_gate": {"cap": None},
}


def sensitivity_table(projects):
    out = {name: {p: privacy_index(c, **kw) for p, c in projects.items()} for name, kw in SENSITIVITY_VARIANTS.items()}
    for f in ("F1", "F2", "F4", "F7"):
        out[f"drop_{f}"] = {p: privacy_index(c, drop=(f,)) for p, c in projects.items()}
    return out
