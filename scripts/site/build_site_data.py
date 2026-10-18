#!/usr/bin/env python3
"""Build site/assets/data.json for the v11 website.

Real inputs:  data/registry/REGISTRY_v2_2.csv (document registry, core_v1/core_v2 flags),
              data/jurisdictions/JURISDICTION_STATUS_2026-10-17.csv (official project status),
              docs/MEASUREMENT_CONTRACT_v1_1_2026-10-18.md (feature definitions, parsed from §4),
              data/worked_profiles/*.csv (development fills — the only real cell values so far).
Mock input:   every other cell value is generated here with a fixed seed and written with provenance = "MOCK".
              The site shows a MOCK banner until data/features/matrix.csv exists with provenance != MOCK.

usage: python3 scripts/site/build_site_data.py   (run from the repository root)
"""
import csv, json, os, random, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
AS_OF = "2026-10-18"
rng = random.Random(11)

def read_csv(p): return list(csv.DictReader(open(os.path.join(ROOT, p), encoding="utf-8")))

# ---------- contract: features ----------
contract = open(os.path.join(ROOT, "docs/MEASUREMENT_CONTRACT_v1_1_2026-10-18.md"), encoding="utf-8").read()
features = []
for line in contract.split("\n"):
    m = re.match(r"\| \*\*(F\d+) ([A-Z_]+)\*\*[^|]*\| (.*?) \| (.*?) \| (.*?) \| (.*?) \|$", line)
    if m: features.append({"id": m.group(1), "name": m.group(2), "question": m.group(3), "values": m.group(4), "qualifiers": m.group(5), "traps": m.group(6)})
CELLS = ["F1", "F2", "F3", "F4", "F7", "F8", "F9", "F10", "F11", "F12"]  # F5/F6 reserved

# ---------- jurisdictions ----------
registry = read_csv("data/registry/REGISTRY_v2_2.csv")
core = [r for r in registry if r["core_v1"] or r["core_v2"]]
status = {r["jur"]: r for r in read_csv("data/jurisdictions/JURISDICTION_STATUS_2026-10-17.csv")}
import pycountry
NAMES = {"UK": "United Kingdom", "EU": "Euro area (Eurosystem)", "ECCU": "Eastern Caribbean Currency Union", "HK": "Hong Kong SAR", "MO": "Macao SAR",
         "TW": "Taiwan", "RU": "Russia", "US": "United States", "KR": "Korea", "IR": "Iran", "BO": "Bolivia", "SZ": "Eswatini", "TR": "Türkiye"}
EURO = ["AT", "BE", "HR", "CY", "EE", "FI", "FR", "DE", "GR", "IE", "IT", "LV", "LT", "LU", "MT", "NL", "PT", "SK", "SI", "ES"]
ECCU = ["AG", "DM", "GD", "KN", "LC", "VC"]  # plus Anguilla, Montserrat (not in topojson at this scale)
def numeric(a2):
    c = pycountry.countries.get(alpha_2=("GB" if a2 == "UK" else a2))
    return str(int(c.numeric)) if c else None
def name(a2):
    if a2 in NAMES: return NAMES[a2]
    c = pycountry.countries.get(alpha_2=a2); return c.common_name if c and hasattr(c, "common_name") else (c.name if c else a2)

jurs = {}
for r in core:
    j = jurs.setdefault(r["jur"], {"code": r["jur"], "name": name(r["jur"]), "docs": [], "member_ids": None})
    j["docs"].append({"doc_id": r["doc_id"], "year": int(r["year"]) if r["year"].isdigit() else None, "title": r["title"][:140],
                      "layer": "core_v1" if r["core_v1"] else "core_v2", "verdict": r["core_v1"] or r["core_v2"],
                      "staff_research": r["staff_research"] in ("Y", "yes", "True", "true"), "url": r["url"]})
for code, j in jurs.items():
    j["docs"].sort(key=lambda d: (d["year"] or 0, d["doc_id"]))
    j["years"] = sorted({d["year"] for d in j["docs"] if d["year"]})
    s = status.get(code, {})
    j["status"] = s.get("status", "UNRESEARCHED"); j["status_date"] = s.get("status_date", ""); j["project_name"] = s.get("project_name", "")
    j["pause_kind"] = s.get("pause_kind", "")
    if code == "EU": j["member_ids"] = [numeric(c) for c in EURO]
    elif code == "ECCU": j["member_ids"] = [numeric(c) for c in ECCU]
    else: j["map_id"] = numeric(code)

# ---------- cell values: real development fills, else mock ----------
VALS = {"F1": ["yes", "no"], "F2": ["yes", "no"], "F3": ["via_PSP", "via_CB", "via_both", "none_stated"], "F4": ["yes", "no"],
        "F7": ["yes", "no"], "F8": ["yes", "no"], "F9": ["yes", "no"], "F10": ["yes", "no"],
        "F12": ["conventional_centralised", "permissioned_DLT", "hybrid", "undecided"]}
OBJ = ["payment_modernisation", "financial_inclusion", "monetary_sovereignty_transmission", "cash_substitute_resilience", "aml_cft_tax_enforcement", "innovation_competitiveness"]
STATUS_BY_PROJECT = {"LIVE": "operational", "PILOT": "tested", "PREPARATION": "adopted", "EXPLORATION": "option", "PAUSED": "option", "DISCONTINUED": "option", "BANNED": "n.a.", "NONE": "n.a."}

def mock_cells(j):
    """Deterministic placeholder values; distribution loosely shaped by project status so the mock map is not uniform. Never read as findings."""
    cells = {}
    weight_unknown = {"LIVE": 0.1, "PILOT": 0.2, "PREPARATION": 0.25, "EXPLORATION": 0.45}.get(j["status"], 0.6)
    cs = STATUS_BY_PROJECT.get(j["status"], "option")
    for f in CELLS:
        if f == "F11":
            flags = {o: (rng.random() < {"payment_modernisation": .8, "financial_inclusion": .5, "monetary_sovereignty_transmission": .45,
                                         "cash_substitute_resilience": .6, "aml_cft_tax_enforcement": .15, "innovation_competitiveness": .55}[o]) for o in OBJ}
            cells["F11"] = {"value": flags, "primary_status": rng.choice(["one_primary", "several_joint", "unranked", "n/d"]), "evidence_state": "documented", "claim_status": cs, "provenance": "MOCK"}
            continue
        if rng.random() < weight_unknown: cells[f] = {"value": "n/d", "evidence_state": "unknown", "claim_status": "", "provenance": "MOCK"}
        else:
            v = rng.choice(VALS[f]); cells[f] = {"value": v, "evidence_state": rng.choice(["documented", "documented", "partial"]), "claim_status": cs, "provenance": "MOCK"}
    return cells

def load_fill(path, label):
    rows = {r["cell"]: r for r in csv.DictReader(open(path, encoding="utf-8"))}
    cells = {}
    def one(key, cell):
        r = rows.get(cell)
        if r: cells[key] = {"value": r["value"].replace("via_psp", "via_PSP").replace("permissioned_dlt", "permissioned_DLT"), "evidence_state": r["evidence_state"], "claim_status": r["claim_status"],
                            "doc": r.get("doc", ""), "page": r.get("page", ""), "quote": r.get("quote", ""), "justification": r.get("justification", ""), "provenance": label}
    for key, cell in [("F1", "F1 CB_LINK_ONLINE"), ("F2", "F2 PSP_LINK_ONLINE"), ("F3", "F3 LAWFUL_ACCESS_ROUTE"), ("F4", "F4 PRIVATE_OFFLINE_AVAILABLE"), ("F7", "F7 LOW_ID_ROUTE"),
                      ("F8", "F8 ONBOARDING_ID"), ("F9", "F9 TARGETED_REIDENTIFICATION"), ("F10", "F10 PROGRAMMABLE_RESTRICTIONS"), ("F12", "F12 LEDGER_TECHNOLOGY")]: one(key, cell)
    flags = {o: rows.get(f"F11 {o}", {}).get("value", "n/d").lower() in ("yes", "1", "true") for o in OBJ}
    cells["F11"] = {"value": flags, "primary_status": rows.get("F11 primary_status", {}).get("value", "n/d"), "primary_objectives": rows.get("F11 primary_objectives", {}).get("value", ""),
                    "evidence_state": rows.get("F11 primary_status", {}).get("evidence_state", ""), "claim_status": rows.get("F11 primary_status", {}).get("claim_status", ""), "provenance": label}
    return cells

def typ(cells):
    f1, f2, f4 = cells["F1"]["value"], cells["F2"]["value"], cells["F4"]["value"]
    on = "A" if f1 == "yes" else ("B" if f1 == "no" and f2 == "yes" else ("C" if f1 == "no" and f2 == "no" else ("B/C?" if f1 == "no" else "?")))
    off = "0" if f4 == "no" else ("1" if f4 == "yes" else "?")
    return on + off

dev_dir = os.path.join(ROOT, "data/worked_profiles")
for code, j in jurs.items():
    dev = os.path.join(dev_dir, f"{code}_api_single_v1_1.csv")
    if os.path.exists(dev): j["cells"] = load_fill(dev, "development:api_single:claude-opus-5-5:contract_v1.1"); j["mock"] = False
    else: j["cells"] = mock_cells(j); j["mock"] = True
    j["type"] = typ(j["cells"])
    j["y1"] = 1 if j["cells"]["F1"]["value"] == "no" else (0 if j["cells"]["F1"]["value"] == "yes" else None)
    j["y3"] = 1 if j["cells"]["F7"]["value"] == "yes" else (0 if j["cells"]["F7"]["value"] == "no" else None)
    # mock history: one snapshot per document year; the LAST snapshot equals the current cells. Real history comes from the pipeline's history.json.
    hist = []; cur = {f: j["cells"][f]["value"] for f in CELLS if f != "F11"}
    years = j["years"] or [2024]
    for i, y in enumerate(years):
        if i == len(years) - 1: snap = dict(cur)
        else:
            snap = dict(cur)
            for f in ("F1", "F4", "F10", "F12"):  # earlier years: more undecided, occasional change
                if rng.random() < 0.5: snap[f] = "n/d"
                elif rng.random() < 0.25 and f in VALS: snap[f] = rng.choice(VALS[f])
        hist.append({"year": y, "type": typ({k: {"value": v} for k, v in snap.items()} | {"F2": {"value": snap.get("F2", "n/d")}}), "cells": snap,
                     "claim_status": "option" if i < len(years) - 1 else j["cells"]["F1"]["claim_status"], "provenance": "MOCK" if j["mock"] else "development:derived_from_fill_years"})
    j["history"] = hist

out = {"as_of": AS_OF, "contract": "MEASUREMENT_CONTRACT_v1_1_2026-10-18", "mock": True,
       "mock_note": "All cell values except the development profiles (NO, UK) are placeholders generated by scripts/site/build_site_data.py. They illustrate the target product and are not findings.",
       "features": features, "objectives": OBJ, "types": ["A0", "A1", "B0", "B1", "C0", "C1"],
       "jurisdictions": sorted(jurs.values(), key=lambda j: j["name"])}
os.makedirs(os.path.join(ROOT, "site/assets"), exist_ok=True)
json.dump(out, open(os.path.join(ROOT, "site/assets/data.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=0)
n_dev = sum(1 for j in jurs.values() if not j["mock"])
print(f"data.json: {len(jurs)} jurisdictions, {len(core)} core documents, {len(features)} features; development fills: {n_dev}, mock: {len(jurs)-n_dev}")
