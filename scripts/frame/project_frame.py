#!/usr/bin/env python3
"""Recompute the project eligibility funnel from the registry and the status table (PROJECT_FRAME.md).
Run from the repository root: python3 scripts/frame/project_frame.py  → prints the funnel and writes data/frame/projects.csv"""
import csv, os, collections
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
EURO = {"AT", "BE", "BG", "HR", "CY", "EE", "FI", "FR", "DE", "GR", "IE", "IT", "LV", "LT", "LU", "MT", "NL", "PT", "SK", "SI", "ES"}
UNIONS = {"EU", "ECCU", "BCEAO"}; NOT_PROJECTS = {"BIS", "UN"}
NON_RETAIL = {"NONE", "BANNED", "NA"}  # statuses outside the retail matrix (documented in PROJECT_FRAME.md)

def main():
    R = list(csv.DictReader(open(os.path.join(ROOT, "data/registry/REGISTRY_v2_2.csv"), encoding="utf-8")))
    S = {r["jur"]: r for r in csv.DictReader(open(os.path.join(ROOT, "data/jurisdictions/JURISDICTION_STATUS_2026-10-17.csv"), encoding="utf-8"))}
    core = [r for r in R if r["core_v1"] or r["core_v2"]]
    def proj(code): return "EU" if code in EURO else code
    rows = {}
    for r in core:
        if r["jur"] in NOT_PROJECTS: continue
        p = proj(r["jur"]); d = rows.setdefault(p, {"project": p, "n_core_docs": 0, "languages": collections.Counter(), "source_codes": set()})
        d["n_core_docs"] += 1; d["languages"][r["language"]] += 1; d["source_codes"].add(r["jur"])
    out = []
    for p, d in sorted(rows.items()):
        st = S.get(p, {}).get("status", "UNRESEARCHED"); st = "UNRESEARCHED" if st.startswith("UNRESEARCHED") else st
        union = p in UNIONS; retail = st not in NON_RETAIL
        out.append({"project": p, "union": union, "status": st, "national_candidate": not union, "retail_candidate": (not union) and retail,
                    "n_core_docs": d["n_core_docs"], "languages": ";".join(f"{k}:{v}" for k, v in sorted(d["languages"].items())), "source_codes": ";".join(sorted(d["source_codes"]))})
    os.makedirs(os.path.join(ROOT, "data/frame"), exist_ok=True)
    with open(os.path.join(ROOT, "data/frame/projects.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0].keys())); w.writeheader(); w.writerows(out)
    n_all, n_nat, n_ret = len(out), sum(1 for o in out if o["national_candidate"]), sum(1 for o in out if o["retail_candidate"])
    print(f"registry rows {len(R)} | core docs {len(core)} | candidate projects {n_all} | national {n_nat} | national retail {n_ret}")
    print("status of national retail candidates:", dict(collections.Counter(o["status"] for o in out if o["retail_candidate"])))

if __name__ == "__main__": main()
