#!/usr/bin/env python3
"""End-to-end run of the privacy-index chain (ADR-009 draft, spec §10): blind-coder files -> reliability and merge ->
index per project -> uncertainty and sensitivity -> separation at observed coverage -> validity -> tables and the
two-axis map. Built and tested on MOCK data (scripts/index_mock.py) so that the chain is ready when the F-cells exist.

--label is required and is printed in every output: file names start with it, the report and the table carry it in
their first line, and the map carries it as a watermark. Project ids starting with MOCK force the label MOCK.

usage: index_report.py --label MOCK --a A.csv --b B.csv --known K.csv --external E.csv --measures M.csv --tiers T.csv --out DIR
"""
import argparse
import csv
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from derive_index import CORE, axis1, privacy_index, separated_pairs, share_separated, simulate_separation, uncertainty_analysis  # noqa: E402
from index_reliability import merge, read, reliability  # noqa: E402
from index_validity import check_known_cases, compare_external  # noqa: E402

F1_COLOUR = {1: "#2a7ab0", 0: "#c0392b", None: "#8a8a8a"}
F1_LABEL = {1: "F1 protective", 0: "F1 not protective", None: "F1 undetermined"}


def _csv(path):
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def run(label, a_path, b_path, known_path, external_path, measures_path, tiers_path, draws=500):
    a, b = read(a_path), read(b_path)
    if any(k[0].startswith("MOCK") for k in a) and label != "MOCK":
        raise ValueError("MOCK project ids require --label MOCK")
    rel = reliability(a, b)
    cells = merge(a, b)
    index = {p: privacy_index(c) for p, c in cells.items()}
    tiers = {r["project_id"]: r["tier"] for r in _csv(tiers_path)} if tiers_path else {}
    coverage = {f: sum(axis1(c)["components"][f] is not None for c in cells.values()) / len(cells) for f in CORE}
    res = {
        "label": label,
        "n_projects": len(cells),
        "reliability": rel,
        "coverage_after_merge": {f: round(v, 3) for f, v in coverage.items()},
        "separation_share_stated": round(share_separated({p: x["stated"] for p, x in index.items()}), 4),
        "separation_share_admissible": round(share_separated({p: x["admissible"] for p, x in index.items()}), 4),
        "simulation_at_observed_coverage": simulate_separation(coverage),
        "uncertainty_all": uncertainty_analysis(cells, draws=draws),
        "uncertainty_T1_T2": uncertainty_analysis({p: c for p, c in cells.items() if tiers.get(p) in ("T1", "T2")}, draws=draws) if tiers else None,
        "known_cases": check_known_cases(cells, _csv(known_path)) if known_path else [],
        "external": compare_external(cells, _csv(external_path), _csv(measures_path)) if external_path and measures_path else [],
    }
    return res, index, tiers


def _table_rows(index, tiers):
    rows = []
    for p in sorted(index):
        x = index[p]
        s, ad, cm = x["stated"], x["admissible"], x["commitment"]
        rows.append({"project_id": p, "tier": tiers.get(p, ""), "f1": {1: "protective", 0: "not_protective", None: "undetermined"}[s["components"]["F1"]],
                     "stated_lower": s["lower"], "stated_upper": s["upper"], "stated_width": s["width"],
                     "admissible_lower": ad["lower"], "admissible_upper": ad["upper"],
                     "rungs_F1_F2_F4_F7": "-".join(str(cm["profile"][f]) for f in CORE), "decided_of_4": cm["decided_of_4"],
                     "determined_of_4": s["determined"]})
    return rows


def svg_map(index, label, width=760, height=520):
    """Two-axis map: x = components decided (0..4), y = stated-design interval; colour = F1 class; label watermark."""
    L, R, T, B = 70, 30, 40, 60
    pw, ph = width - L - R, height - T - B
    by_x = {}
    for p in sorted(index):
        by_x.setdefault(index[p]["commitment"]["decided_of_4"], []).append(p)
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" font-family="sans-serif" font-size="11">',
           f'<rect width="{width}" height="{height}" fill="#ffffff"/>',
           f'<text x="{width / 2}" y="{height / 2}" font-size="96" fill="#d0d0d0" fill-opacity="0.45" text-anchor="middle" transform="rotate(-25 {width / 2} {height / 2})">{label} DATA</text>',
           f'<text x="{L}" y="22" font-size="13" font-weight="bold">{label}: two-axis privacy index (stated design interval by components decided)</text>']
    for k in range(5):
        x = L + pw * (k + 0.5) / 5
        out.append(f'<text x="{x}" y="{height - B + 20}" text-anchor="middle">{k}</text>')
    out.append(f'<text x="{L + pw / 2}" y="{height - 15}" text-anchor="middle">components endorsed or operational (of 4)</text>')
    for t in (0, 0.25, 0.5, 0.75, 1.0):
        y = T + ph * (1 - t)
        out.append(f'<line x1="{L}" x2="{L + pw}" y1="{y}" y2="{y}" stroke="#e6e6e6"/>')
        out.append(f'<text x="{L - 8}" y="{y + 4}" text-anchor="end">{t:.2f}</text>')
    out.append(f'<text x="18" y="{T + ph / 2}" transform="rotate(-90 18 {T + ph / 2})" text-anchor="middle">stated design (any status), interval</text>')
    for k, ps in by_x.items():
        band = pw / 5
        for i, p in enumerate(ps):
            x = L + band * k + band * (i + 1) / (len(ps) + 1)
            s = index[p]["stated"]
            col = F1_COLOUR[s["components"]["F1"]]
            y1, y2 = T + ph * (1 - s["upper"]), T + ph * (1 - s["lower"])
            out.append(f'<line x1="{x:.1f}" x2="{x:.1f}" y1="{y1:.1f}" y2="{y2:.1f}" stroke="{col}" stroke-width="2.5"><title>{p}: [{s["lower"]}, {s["upper"]}]</title></line>')
            out.append(f'<circle cx="{x:.1f}" cy="{(y1 + y2) / 2:.1f}" r="2.5" fill="{col}"/>')
    for i, (k, lab) in enumerate(F1_LABEL.items()):
        out.append(f'<rect x="{L + 10 + i * 150}" y="{T - 12}" width="10" height="10" fill="{F1_COLOUR[k]}"/><text x="{L + 25 + i * 150}" y="{T - 3}">{lab}</text>')
    out.append("</svg>")
    return "\n".join(out)


def markdown(res, rows, label):
    L = [f"# {label}: privacy index dry run", "", f"> **{label} DATA. Invented inputs; nothing here is a result.**" if label == "MOCK" else f"> Label: {label}", "",
         f"Projects: {res['n_projects']}. Separated pairs (diagnostic, spec §6): stated view {res['separation_share_stated']}, admissible view {res['separation_share_admissible']}.", "",
         "## Coding reliability (Krippendorff's alpha, nominal)", "", "| Cell | n | agreement | alpha (3 categories) | n both valued | alpha (valued) |", "|---|---|---|---|---|---|"]
    for f in CORE:
        r = res["reliability"][f]
        L.append(f"| {f} | {r['n']} | {r['agreement']} | {r['alpha_3cat']} | {r['n_both_valued']} | {r['alpha_valued']} |")
    L += ["", "## Coverage after merge and expected separation", "", "| Cell | share with a value |", "|---|---|"]
    L += [f"| {f} | {v} |" for f, v in res["coverage_after_merge"].items()]
    s = res["simulation_at_observed_coverage"]
    L += ["", f"Simulated share of separated pairs at this coverage: {s['mean']} ({s['p05']} to {s['p95']}).", "",
          "## Uncertainty and sensitivity (share of baseline separated pairs kept)", "", "| Variant | all projects | T1 and T2 |", "|---|---|---|"]
    u, t = res["uncertainty_all"], res["uncertainty_T1_T2"] or {}
    for k in u:
        if k.endswith("_kept") or k.startswith("weights") or k.startswith("baseline"):
            L.append(f"| {k} | {u[k]} | {t.get(k, '')} |")
    L += ["", "## Known cases", "", "| Case | Project | Cell | expected | observed | status |", "|---|---|---|---|---|---|"]
    L += [f"| {k['case_id']} | {k['project_id']} | {k['cell']} | {k['expected']} | {k['observed']} | {k['status']} |" for k in res["known_cases"]]
    L += ["", "## External measures (validity, not an association claim)", "", "| Measure | role | expected sign | n | rho | 95 % interval |", "|---|---|---|---|---|---|"]
    L += [f"| {e['measure']} | {e['role']} | {e['expected_sign']} | {e['n']} | {e['rho']} | {e['ci95']} |" for e in res["external"]]
    L += ["", "## Index per project", "", "| Project | Tier | F1 | stated | admissible | rungs F1-F2-F4-F7 | decided of 4 |", "|---|---|---|---|---|---|---|"]
    L += [f"| {r['project_id']} | {r['tier']} | {r['f1']} | [{r['stated_lower']}, {r['stated_upper']}] | [{r['admissible_lower']}, {r['admissible_upper']}] | {r['rungs_F1_F2_F4_F7']} | {r['decided_of_4']} |" for r in rows]
    return "\n".join(L) + "\n"


def write(out, label, res, index, tiers):
    os.makedirs(out, exist_ok=True)
    rows = _table_rows(index, tiers)
    pre = os.path.join(out, f"{label}_INDEX_")
    json.dump(res, open(pre + "RESULTS.json", "w"), indent=1)
    with open(pre + "TABLE.csv", "w", newline="", encoding="utf-8") as fh:
        fh.write(f"# {label} DATA{' - invented - not a result' if label == 'MOCK' else ''}\n")
        w = csv.DictWriter(fh, list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    open(pre + "REPORT.md", "w", encoding="utf-8").write(markdown(res, rows, label))
    open(pre + "MAP.svg", "w", encoding="utf-8").write(svg_map(index, label))
    return [pre + s for s in ("RESULTS.json", "TABLE.csv", "REPORT.md", "MAP.svg")]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--label", required=True)
    for k in ("a", "b", "out"):
        ap.add_argument(f"--{k}", required=True)
    for k in ("known", "external", "measures", "tiers"):
        ap.add_argument(f"--{k}")
    ap.add_argument("--draws", type=int, default=500)
    o = ap.parse_args()
    res, index, tiers = run(o.label, o.a, o.b, o.known, o.external, o.measures, o.tiers, o.draws)
    for f in write(o.out, o.label, res, index, tiers):
        print("written", f)


if __name__ == "__main__":
    main()
