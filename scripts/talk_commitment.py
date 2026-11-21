"""Privacy talk against commitments, by aspect (PROPOSAL after MB, 21 Nov 2026 21:31; spec §12, ADR-009).

MB's expectation, to be registered as a hypothesis before any data exist (not a finding): projects talk about privacy
much more than they commit to it in their documents.

The two layers stay separately measured (ADR-004 §4, ADR-005): talk comes from the talk instrument (own-voice relevant
units per aspect), commitments from the F-cells (rule C). They meet only on the same unit, the (project, aspect) pair,
on the six aspects that have a matching F-cell. Per pair the outcome is a cell of the 2 x 2 table of ADR-005 (talk yes
or no x admissible commitment yes or no), extended by the middle step "design stated, not decided" (rung 1 or 2).
Per project the gap is a COUNT of aspects talked about without an admissible commitment, over the same six aspects: a
count of 2 x 2 cells, not the difference of two scales. Talk intensity (share of relevant own-voice units) is reported
beside it, descriptively, and never enters the gap.

An unresolved disagreement of the blind coders on a mapped cell leaves the commitment of that pair uncertain; every
project-level quantity is then given as bounds (uncertain counted as committed: smallest gap; as not committed: largest).
"""
import math
import random

from derive_index import is_leaning, rung

ASPECT_CELLS = {  # talk aspect (codebook v0.3) -> F-cells that can carry a commitment on it
    "CB_ACCESS": ("F1",),
    "INTERMEDIARY_DATA": ("F2",),
    "AUTHORITY_ACCESS": ("F3", "F9"),
    "OFFLINE": ("F4",),
    "ANONYMITY": ("F7",),
    "IDENTIFICATION": ("F7", "F8"),
}
TALK_ONLY_ASPECTS = ("DATA_PROTECTION", "USER_CONTROL", "PETS", "GENERAL")  # no F-cell: talk reported, no gap
UNMAPPED_CELLS = ("F10",)  # programmable restrictions: no talk aspect; in the design index only


def _disputed(cell):
    return str((cell or {}).get("coder_disagreement", "")).strip().lower() in ("true", "1", "yes")


def pair_state(talk_units, cells, aspect):
    """talk: own-voice relevant units on the aspect (int); cells: the project's F-cells.
    Returns talk (bool), commitment ('admissible' / 'stated' / 'none' / 'uncertain') and the highest rung."""
    mapped = ASPECT_CELLS[aspect]
    rungs = [rung(cells.get(f), f) for f in mapped]
    if any(_disputed(cells.get(f)) for f in mapped) and max(rungs) < 3:
        commitment = "uncertain"
    elif max(rungs) >= 3:
        commitment = "admissible"
    elif max(rungs) >= 1:
        commitment = "stated"
    else:
        commitment = "none"
    return {"talk": (talk_units or 0) > 0, "commitment": commitment, "max_rung": max(rungs),
            "leaning": any(is_leaning(cells.get(f)) for f in mapped)}  # LEANING never counts as stated or committed


def project_summary(talk, cells):
    """talk: {aspect: own-voice units}. Counts over the six mapped aspects, with bounds for uncertain pairs."""
    states = {a: pair_state(talk.get(a, 0), cells, a) for a in ASPECT_CELLS}
    n = len(states)
    talked = sum(s["talk"] for s in states.values())
    committed = sum(s["commitment"] == "admissible" for s in states.values())
    stated = sum(s["commitment"] in ("admissible", "stated") for s in states.values())
    uncertain = sum(s["commitment"] == "uncertain" for s in states.values())
    gap_lo = sum(s["talk"] and s["commitment"] not in ("admissible", "uncertain") for s in states.values())
    gap_hi = gap_lo + sum(s["talk"] and s["commitment"] == "uncertain" for s in states.values())
    return {"aspects": n, "talked": talked, "design_stated": stated, "committed": committed, "uncertain": uncertain,
            "gap": [gap_lo, gap_hi],
            "talk_share": round(talked / n, 4), "commit_share": [round(committed / n, 4), round((committed + uncertain) / n, 4)],
            "stated_share": [round(stated / n, 4), round((stated + uncertain) / n, 4)],
            "talk_only_aspects": {a: talk.get(a, 0) > 0 for a in TALK_ONLY_ASPECTS},
            "pairs": states}


def table_2x2(summaries):
    """Corpus 2 x 2 over all (project, aspect) pairs, plus the 'design stated, not decided' middle row."""
    t = {"talk_and_committed": 0, "talk_stated_not_decided": 0, "talk_no_commitment": 0, "talk_uncertain": 0,
         "silent_committed": 0, "silent_stated": 0, "silent_none": 0, "silent_uncertain": 0}
    for s in summaries.values():
        for st in s["pairs"].values():
            pre = "talk" if st["talk"] else "silent"
            key = {"admissible": "and_committed" if st["talk"] else "committed", "stated": "stated_not_decided" if st["talk"] else "stated",
                   "none": "no_commitment" if st["talk"] else "none", "uncertain": "uncertain"}[st["commitment"]]
            t[f"{pre}_{key}"] += 1
    return t


def _binom_upper_tail(k, n):
    """P(X >= k) for X ~ Bin(n, 0.5), exact."""
    return sum(math.comb(n, i) for i in range(k, n + 1)) / 2 ** n if n else None


def talk_exceeds_commitment(summaries, bound="lower", level="admissible", B=2000, seed=20261121):
    """Pre-specified tests (proposal). level 'admissible' (H-TC1): d = talk_share - share of aspects with an admissible
    commitment. level 'stated' (H-TC2, the discriminating one): d = talk_share - share of aspects whose design the
    documents state at any status. Uses the bound least favourable to the hypothesis ('lower': uncertain pairs counted
    as committed or stated). One-sided sign test over projects with d != 0, and the mean of d with a project bootstrap
    95 % interval. The MOCK dry run showed that H-TC1 comes out positive even when talk only mirrors stated designs,
    because decided commitments are rare: only H-TC2 can tell "talk without substance" from "talk about designs not yet
    decided"."""
    key = "commit_share" if level == "admissible" else "stated_share"
    d = [s["talk_share"] - (s[key][1] if bound == "lower" else s[key][0]) for s in summaries.values()]
    pos, neg = sum(x > 0 for x in d), sum(x < 0 for x in d)
    rng = random.Random(seed)
    means = sorted(sum(d[rng.randrange(len(d))] for _ in d) / len(d) for _ in range(B)) if d else []
    return {"n_projects": len(d), "positive": pos, "negative": neg, "zero": len(d) - pos - neg,
            "sign_test_p_one_sided": None if pos + neg == 0 else round(_binom_upper_tail(pos, pos + neg), 6),
            "mean_d": round(sum(d) / len(d), 4) if d else None,
            "mean_d_ci95": [round(means[int(0.025 * B)], 4), round(means[int(0.975 * B) - 1], 4)] if means else None,
            "bound": bound, "level": level}


def talk_intensity(own_relevant, candidates, z=1.96):
    """Share of own-voice relevant units among candidate units, Wilson interval. Descriptive only; never in the gap."""
    if not candidates:
        return None
    p = own_relevant / candidates
    den = 1 + z * z / candidates
    c = (p + z * z / (2 * candidates)) / den
    h = z * math.sqrt(p * (1 - p) / candidates + z * z / (4 * candidates ** 2)) / den
    return {"share": round(p, 4), "ci95": [round(max(0, c - h), 4), round(min(1, c + h), 4)], "n": candidates}
