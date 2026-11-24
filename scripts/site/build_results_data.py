#!/usr/bin/env python3
"""The results page of the website: data for site/results.html (MB, 24 Nov 2026: prepare the page in advance on the
test data, so that when the outputs are opened only the numbers change).

What the page shows follows Registration A (docs/REGISTRATION_A_DRAFT_2026-11-23.md) and ADR-012 D1, D3, D4:
  * the stated-design privacy index: the mean of seven cells F1, F2, F4, F7, F8, F9, F10, as an interval
    (scripts/derive_index.py, nothing imputed); beside it, outside the mean, the four-cell index (F1, F2, F4, F7),
    F3 as a category, the PET profile (codes of Nijsse and Pinto 2026, a profile, not a scale) and axis 2 (cells that
    pass committed() out of seven);
  * talk beside the index, never in it: volume of own-voice relevant talk per 100 eligible units, the share of
    relevant sentences that state a mechanism or a decision, and the directional gap (aspects talked about without a
    commitment, scripts/talk_commitment.py);
  * the hypothesis "much talk, few commitments" on the 16 core projects with its lower and upper readings (L, U):
    holds if L >= 9, fails if U <= 8, inconclusive otherwise; no sign test;
  * by tier: T1 and T2 are the core, T3 is exploratory ("often unfinished CBDC research").
Projects are listed by tier and code. There is no league table and no ordering by value (index spec §6).

Inputs (one set per run, all read from files; this script computes nothing that the index code does not):
  --a, --b            blind coder files (index_reliability.read format)
  --tiers             project_id,tier
  --talk              project_id,aspect,own_units           (own-voice relevant units per talk aspect)
  --intensity         project_id,candidate_units,own_relevant_units   (eligible units of stratum X; own-voice R)
  --extra             project_id,own_voice_publications,no_majority_units,mechanism_units,decision_units,pet_codes
                      (pet_codes separated by '|'; mechanism = basis other than NONE, decision = ENDORSED)

Test data: with --label MOCK every project id must start with MOCK, every input is the MOCK set of data/index/mock/
plus data/site/mock/MOCK_SITE_EXTRA.csv (written by --make-mock-extra, a fixed seed), and the page carries a banner on
every view. A real run needs --label with the run name and project ids without MOCK; it is written only after the
blind core outputs are opened under ADR-016 point 4. Model outputs of the blind core are never an input here before then.

usage:
  build_results_data.py --mock            # the test-data page (default inputs), writes site/assets/results.json
  build_results_data.py --mock --check    # fail if site/assets/results.json is not what the inputs give
  build_results_data.py --make-mock-extra # rewrite data/site/mock/MOCK_SITE_EXTRA.csv
"""
import argparse
import csv
import hashlib
import json
import os
import random
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from derive_index import CORE, CORE4, PROTECTIVE, committed, component, privacy_index  # noqa: E402
from index_reliability import merge, read  # noqa: E402
from talk_commitment import ASPECT_CELLS, TALK_ONLY_ASPECTS, project_summary, talk_intensity  # noqa: E402

sys.path.insert(0, os.path.join(ROOT, "scripts", "extraction"))
from v122 import PET_CODES  # noqa: E402

OUT = os.path.join(ROOT, "site", "assets", "results.json")
MOCK_DIR = os.path.join(ROOT, "data", "index", "mock")
MOCK_EXTRA = os.path.join(ROOT, "data", "site", "mock", "MOCK_SITE_EXTRA.csv")
MOCK_INPUTS = {"a": os.path.join(MOCK_DIR, "MOCK_CODER_A.csv"), "b": os.path.join(MOCK_DIR, "MOCK_CODER_B.csv"),
               "tiers": os.path.join(MOCK_DIR, "MOCK_TIERS.csv"), "talk": os.path.join(MOCK_DIR, "MOCK_TALK_H.csv"),
               "intensity": os.path.join(MOCK_DIR, "MOCK_TALK_INTENSITY.csv"), "extra": MOCK_EXTRA}
BANNER = "MOCK DATA - invented - not a result"
CORE_TIERS = ("T1", "T2")
H_CELLS = CORE4  # the four protective commitments of the hypothesis (D3): F1, F2, F4, F7
MAJORITY = 9  # of the 16 core projects
EXTRA_FIELDS = ["project_id", "own_voice_publications", "no_majority_units", "mechanism_units", "decision_units", "pet_codes", "note"]


def _csv(path):
    with open(path, newline="", encoding="utf-8") as fh:
        return [r for r in csv.DictReader(line for line in fh if not line.startswith("#"))]


def _sha(path):
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def make_mock_extra(seed=20261124):
    """Invented talk facets and PET codes for MOCK01 to MOCK44: the inputs the MOCK set of 21 Nov does not have."""
    rng = random.Random(seed)
    intensity = {r["project_id"]: r for r in _csv(MOCK_INPUTS["intensity"])}
    codes = sorted(PET_CODES)
    rows = []
    for p in sorted(intensity):
        rel = int(intensity[p]["own_relevant_units"])
        mech = rng.randint(0, rel)
        dec = rng.randint(0, mech)
        pets = sorted(rng.sample(codes, rng.choice([0, 0, 1, 2, 3, 4])))
        rows.append({"project_id": p, "own_voice_publications": rng.choice([1, 2, 2, 3, 4, 5, 6, 8]),
                     "no_majority_units": rng.randint(0, max(1, rel // 6)), "mechanism_units": mech, "decision_units": dec,
                     "pet_codes": "|".join(pets), "note": BANNER})
    os.makedirs(os.path.dirname(MOCK_EXTRA), exist_ok=True)
    with open(MOCK_EXTRA, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=EXTRA_FIELDS, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    return MOCK_EXTRA


def _iv(x):
    return [x["lower"], x["upper"]]


def _per100(units, eligible):
    return round(100.0 * units / eligible, 2) if eligible else None


def hypothesis_reading(cells, extra, intensity):
    """Registration A §3. Lower reading: an undetermined cell counts as committed, a unit without a majority label as
    not relevant. Upper reading: the reverse. Returns T_p, C_p and 'meets both' at each reading."""
    committed_n = sum(committed(cells.get(f), f) and str(cells[f].get("value", "")).strip().lower() == PROTECTIVE[f]
                      for f in H_CELLS if cells.get(f))
    undetermined_n = sum(component(cells.get(f), f) is None and not committed(cells.get(f), f) for f in H_CELLS)
    eligible = int(intensity["candidate_units"])
    own = int(intensity["own_relevant_units"])
    nomaj = int(extra["no_majority_units"] or 0)
    pubs = int(extra["own_voice_publications"] or 0)
    out = {}
    for reading, n_commit, n_rel in (("lower", committed_n + undetermined_n, own), ("upper", committed_n, own + nomaj)):
        much = pubs >= 2 and eligible > 0 and 100.0 * n_rel / eligible >= 1.0
        few = n_commit < 2
        out[reading] = {"much_talk": much, "few_commitments": few, "meets_both": much and few,
                        "commitments_counted": n_commit, "relevant_per_100": _per100(n_rel, eligible)}
    return out


def verdict(L, U):
    if L >= MAJORITY:
        return "holds"
    if U <= MAJORITY - 1:
        return "fails"
    return "inconclusive"


def build(label, inputs):
    a, b = read(inputs["a"]), read(inputs["b"])
    cells = merge(a, b)
    tiers = {r["project_id"]: r["tier"] for r in _csv(inputs["tiers"])}
    talk = {}
    for r in _csv(inputs["talk"]):
        talk.setdefault(r["project_id"], {})[r["aspect"]] = int(r["own_units"] or 0)
    intensity = {r["project_id"]: r for r in _csv(inputs["intensity"])}
    extra = {r["project_id"]: r for r in _csv(inputs["extra"])}
    ids = sorted(cells)
    mock = label == "MOCK"
    if mock != all(p.startswith("MOCK") for p in ids) or (not mock and any(p.startswith("MOCK") for p in ids)):
        raise ValueError("MOCK project ids go with --label MOCK and only with it")
    missing = [p for p in ids if p not in tiers or p not in intensity or p not in extra]
    if missing:
        raise ValueError("projects without tier, intensity or extra row: " + ", ".join(missing))
    projects = []
    for p in ids:
        c = cells[p]
        ix = privacy_index(c)
        s = project_summary(talk.get(p, {}), c)
        it = intensity[p]
        ex = extra[p]
        own = int(it["own_relevant_units"])
        eligible = int(it["candidate_units"])
        ti = talk_intensity(own, eligible)
        pets = [x for x in (ex.get("pet_codes") or "").split("|") if x]
        bad = [x for x in pets if x not in PET_CODES and not x.startswith("other:")]
        if bad:
            raise ValueError(f"{p}: PET codes not in the list: {bad}")
        mech, dec = int(ex["mechanism_units"] or 0), int(ex["decision_units"] or 0)
        projects.append({
            "id": p, "tier": tiers[p], "core": tiers[p] in CORE_TIERS,
            "index": {"stated": _iv(ix["stated"]), "admissible": _iv(ix["admissible"]), "core4": _iv(ix["core4_stated"]),
                      "determined": ix["stated"]["determined"], "of": ix["stated"]["n_components"],
                      "components": ix["stated"]["components"]},
            "f3": ix["F3"]["value"] or "undetermined",
            "pet": pets,
            "axis2": {"committed": ix["commitment"]["decided"], "of": ix["commitment"]["n_cells"],
                      "rungs": ix["commitment"]["profile"]},
            "talk": {"eligible_units": eligible, "own_relevant_units": own,
                     "per_100": _per100(own, eligible),
                     "per_100_ci95": [round(100 * x, 2) for x in ti["ci95"]] if ti else None,
                     "own_voice_publications": int(ex["own_voice_publications"] or 0),
                     "mechanism_share": round(mech / own, 4) if own else None,
                     "decision_share": round(dec / own, 4) if own else None,
                     "aspects_talked": s["talked"], "aspects": s["aspects"],
                     "gap": s["gap"], "committed_aspects": s["committed"],
                     "talk_only_aspects": [k for k, v in s["talk_only_aspects"].items() if v]},
            "hypothesis": hypothesis_reading(c, ex, it) if tiers[p] in CORE_TIERS else None,
        })
    core = [x for x in projects if x["core"]]
    L = sum(x["hypothesis"]["lower"]["meets_both"] for x in core)
    U = sum(x["hypothesis"]["upper"]["meets_both"] for x in core)
    by_tier = {}
    for t in sorted(set(tiers[p] for p in ids)):
        rows = [x for x in projects if x["tier"] == t]
        by_tier[t] = {"n": len(rows),
                      "stated_lower_mean": round(sum(x["index"]["stated"][0] for x in rows) / len(rows), 4),
                      "stated_upper_mean": round(sum(x["index"]["stated"][1] for x in rows) / len(rows), 4),
                      "committed_mean": round(sum(x["axis2"]["committed"] for x in rows) / len(rows), 2),
                      "with_pet": sum(bool(x["pet"]) for x in rows)}
    pet_counts = {}
    for x in projects:
        for code in x["pet"]:
            pet_counts[code] = pet_counts.get(code, 0) + 1
    return {
        "label": label,
        "mock": mock,
        "banner": BANNER if mock else "",
        "inputs": {k: {"file": os.path.relpath(v, ROOT), "sha256": _sha(v)} for k, v in sorted(inputs.items())},
        "definitions": {"index_cells": list(CORE), "core4_cells": list(CORE4), "hypothesis_cells": list(H_CELLS),
                        "aspects_with_cell": {k: list(v) for k, v in ASPECT_CELLS.items()},
                        "aspects_without_cell": list(TALK_ONLY_ASPECTS), "majority": MAJORITY,
                        "core_tiers": list(CORE_TIERS)},
        "hypothesis": {"n_core": len(core), "L": L, "U": U, "verdict": verdict(L, U)},
        "by_tier": by_tier,
        "pet_counts": dict(sorted(pet_counts.items(), key=lambda kv: (-kv[1], kv[0]))),
        "projects": projects,
    }


def dump(data):
    return json.dumps(data, ensure_ascii=False, separators=(",", ":"), sort_keys=True) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mock", action="store_true", help="the test-data page from the MOCK inputs")
    ap.add_argument("--label")
    for k in MOCK_INPUTS:
        ap.add_argument(f"--{k}")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--make-mock-extra", action="store_true")
    o = ap.parse_args()
    if o.make_mock_extra:
        print("written", os.path.relpath(make_mock_extra(), ROOT))
        return 0
    if o.mock:
        label, inputs = "MOCK", dict(MOCK_INPUTS)
    else:
        if not o.label or any(getattr(o, k) is None for k in MOCK_INPUTS):
            ap.error("give --mock, or --label and every input file")
        label, inputs = o.label, {k: os.path.abspath(getattr(o, k)) for k in MOCK_INPUTS}
    text = dump(build(label, inputs))
    if o.check:
        cur = open(OUT, encoding="utf-8").read() if os.path.exists(OUT) else ""
        if cur != text:
            print("site/assets/results.json is not current: run scripts/site/build_results_data.py --mock")
            return 1
        print("results data current (label %s)" % label)
        return 0
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write(text)
    print("written site/assets/results.json (label %s, %d projects)" % (label, len(json.loads(text)["projects"])))
    return 0


if __name__ == "__main__":
    sys.exit(main())
