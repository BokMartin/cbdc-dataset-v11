#!/usr/bin/env python3
"""Build site/assets/data.json for the v11 website (mock-up of the finished product).

REAL inputs
  data/registry/REGISTRY_v2_2.csv                    document registry (391 documents, 92 registry codes)
  data/jurisdictions/JURISDICTION_STATUS_2026-10-17.csv  official project status with sources
  docs/MEASUREMENT_CONTRACT_v1_1_2026-10-18.md       feature definitions (parsed from §4)
  data/worked_profiles/<JUR>_api_single_v1_1.csv     development fills (the only real cell values so far)
MOCK
  Every other cell value, trajectory and decisive page is generated here with a fixed seed. Values are drawn
  from realistic distributions but are NOT tied to what is publicly known about any project (no LLM prior),
  so they cannot anchor later coding. Each mock cell carries provenance = "MOCK". Decisive documents cited
  by mock cells are real registry rows (title, year, URL) but the page and the (empty) quote are placeholders.

Unit of analysis follows the contract: euro area, ECCU and WAEMU are one project each; national euro-area
documents are attached to the euro-area project. BIS and UN rows are not projects.

usage: python3 scripts/site/build_site_data.py        (from the repository root; needs pycountry)
"""
import csv, json, os, random, re
import pycountry
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
AS_OF = "2026-10-18"
rng = random.Random(1101)
def read_csv(p): return list(csv.DictReader(open(os.path.join(ROOT, p), encoding="utf-8")))

# ---------- contract: feature definitions ----------
contract = open(os.path.join(ROOT, "docs/MEASUREMENT_CONTRACT_v1_1_2026-10-18.md"), encoding="utf-8").read()
features = []
for line in contract.split("\n"):
    m = re.match(r"\| \*\*(F\d+) ([A-Z_]+)\*\*[^|]*\| (.*?) \| (.*?) \| (.*?) \| (.*?) \|$", line)
    if m: features.append({"id": m.group(1), "name": m.group(2), "question": m.group(3), "values": m.group(4), "qualifiers": m.group(5), "traps": m.group(6)})
CELLS = ["F1", "F2", "F3", "F4", "F7", "F8", "F9", "F10", "F12"]
OBJ = ["payment_modernisation", "financial_inclusion", "monetary_sovereignty_transmission", "cash_substitute_resilience", "aml_cft_tax_enforcement", "innovation_competitiveness"]
VALS = {"F1": ["yes", "no"], "F2": ["yes", "no"], "F3": ["via_PSP", "via_CB", "via_both", "none_stated"], "F4": ["yes", "no"], "F7": ["yes", "no"],
        "F8": ["yes", "no"], "F9": ["yes", "no"], "F10": ["yes", "no"], "F12": ["conventional_centralised", "permissioned_DLT", "hybrid", "undecided"]}
# marginal probabilities for a determined value (mock, deliberately not tied to real projects)
P = {"F1": {"yes": .35, "no": .65}, "F2": {"yes": .85, "no": .15}, "F3": {"via_PSP": .55, "via_CB": .15, "via_both": .1, "none_stated": .2},
     "F4": {"yes": .3, "no": .7}, "F7": {"yes": .4, "no": .6}, "F8": {"yes": .9, "no": .1}, "F9": {"yes": .75, "no": .25}, "F10": {"yes": .15, "no": .85},
     "F12": {"conventional_centralised": .35, "permissioned_DLT": .35, "hybrid": .15, "undecided": .15}}
P_OBJ = {"payment_modernisation": .8, "financial_inclusion": .5, "monetary_sovereignty_transmission": .45, "cash_substitute_resilience": .6, "aml_cft_tax_enforcement": .15, "innovation_competitiveness": .55}
def draw(d): r = rng.random(); acc = 0
def draw(d):
    r = rng.random(); acc = 0
    for k, p in d.items():
        acc += p
        if r <= acc: return k
    return list(d)[-1]

# ---------- jurisdictions → projects ----------
EURO = ["AT", "BE", "BG", "HR", "CY", "EE", "FI", "FR", "DE", "GR", "IE", "IT", "LV", "LT", "LU", "MT", "NL", "PT", "SK", "SI", "ES"]
ECCU = ["AG", "DM", "GD", "KN", "LC", "VC"]
WAEMU = ["BJ", "BF", "CI", "GW", "ML", "NE", "SN", "TG"]
UNION = {"EU": ("Euro area (Eurosystem)", EURO), "ECCU": ("Eastern Caribbean Currency Union (ECCB)", ECCU), "BCEAO": ("West African Economic and Monetary Union (BCEAO)", WAEMU)}
NOT_PROJECTS = {"BIS", "UN"}
NAMES = {"UK": "United Kingdom", "HK": "Hong Kong SAR", "MO": "Macao SAR", "TW": "Taiwan", "RU": "Russia", "US": "United States", "BO": "Bolivia", "SZ": "Eswatini", "TR": "Türkiye", "XK": "Kosovo", "VE": "Venezuela", "IR": "Iran", "KR": "Korea", "CZ": "Czechia"}
def numeric(a2):
    if a2 == "XK": return "383"
    c = pycountry.countries.get(alpha_2=("GB" if a2 == "UK" else a2)); return str(int(c.numeric)) if c else None
def name(a2):
    if a2 in NAMES: return NAMES[a2]
    c = pycountry.countries.get(alpha_2=a2); return getattr(c, "common_name", None) or (c.name if c else a2)

registry = read_csv("data/registry/REGISTRY_v2_2.csv")
status = {r["jur"]: r for r in read_csv("data/jurisdictions/JURISDICTION_STATUS_2026-10-17.csv")}
projects = {}
def proj(code):
    if code in UNION: nm, members = UNION[code]; ids = [numeric(c) for c in members]
    else: nm, members, ids = name(code), [code], [numeric(code)]
    return projects.setdefault(code, {"code": code, "name": nm, "members": members, "map_ids": [i for i in ids if i], "docs": []})
for r in registry:
    code = r["jur"]
    if code in NOT_PROJECTS: continue
    if code in EURO: code = "EU"
    p = proj(code)
    p["docs"].append({"doc_id": r["doc_id"], "year": int(r["year"]) if r["year"].isdigit() else None, "title": r["title"][:160] or r["fname"], "url": r["url"],
                      "layer": "core_v1" if r["core_v1"] else ("core_v2" if r["core_v2"] else "registry"), "verdict": r["core_v1"] or r["core_v2"] or "",
                      "staff_research": r["staff_research"] in ("Y", "yes", "True", "true"), "source_jur": r["jur"]})
for code, p in projects.items():
    p["docs"].sort(key=lambda d: (d["year"] or 0, d["doc_id"]))
    p["years"] = sorted({d["year"] for d in p["docs"] if d["year"] and d["year"] >= 2014})
    s = status.get(code, {})
    st = s.get("status", "EXPLORATION")
    if st.startswith("UNRESEARCHED"): st = "EXPLORATION"; p["status_mock"] = True
    p["status"] = st; p["status_date"] = s.get("status_date", ""); p["project_name"] = s.get("project_name", ""); p["pause_kind"] = s.get("pause_kind", "")
    p["status_source"] = s.get("source_url", "")
    p["retail"] = st not in ("NONE", "NA", "BANNED") and not (code in ("BO", "BR"))
    p["n_core"] = sum(1 for d in p["docs"] if d["layer"] != "registry")

# ---------- real development fills ----------
def load_fill(path, label, p):
    rows = {r["cell"]: r for r in csv.DictReader(open(path, encoding="utf-8"))}
    cells = {}
    docs_by_no = {}
    for key, cell in [("F1", "F1 CB_LINK_ONLINE"), ("F2", "F2 PSP_LINK_ONLINE"), ("F3", "F3 LAWFUL_ACCESS_ROUTE"), ("F4", "F4 PRIVATE_OFFLINE_AVAILABLE"), ("F7", "F7 LOW_ID_ROUTE"),
                      ("F8", "F8 ONBOARDING_ID"), ("F9", "F9 TARGETED_REIDENTIFICATION"), ("F10", "F10 PROGRAMMABLE_RESTRICTIONS"), ("F12", "F12 LEDGER_TECHNOLOGY")]:
        r = rows.get(cell)
        if not r: continue
        v = r["value"].replace("via_psp", "via_PSP").replace("permissioned_dlt", "permissioned_DLT").replace("unknown", "n/d")
        cells[key] = {"value": v, "evidence_state": r["evidence_state"], "claim_status": r["claim_status"], "derivation": r.get("derivation", ""),
                      "doc_no": r.get("doc", ""), "page": r.get("page", ""), "quote": r.get("quote", ""), "justification": r.get("justification", ""),
                      "counter_evidence": r.get("counter_evidence", ""), "quote_verified": r.get("quote_verified", ""), "provenance": label}
    flags = {o: rows.get(f"F11 {o}", {}).get("value", "n/d").lower() in ("yes", "1", "true") for o in OBJ}
    cells["F11"] = {"flags": flags, "primary_status": rows.get("F11 primary_status", {}).get("value", "n/d"), "primary_objectives": rows.get("F11 primary_objectives", {}).get("value", ""),
                    "evidence_state": rows.get("F11 primary_status", {}).get("evidence_state", ""), "claim_status": rows.get("F11 primary_status", {}).get("claim_status", ""),
                    "doc_no": rows.get("F11 primary_status", {}).get("doc", ""), "page": rows.get("F11 primary_status", {}).get("page", ""), "quote": rows.get("F11 primary_status", {}).get("quote", ""), "provenance": label}
    return cells

def typ(c):
    f1, f2, f4 = c["F1"]["value"], c["F2"]["value"], c["F4"]["value"]
    on = "A" if f1 == "yes" else ("B" if (f1 == "no" and f2 == "yes") else ("C" if (f1 == "no" and f2 == "no") else ("B/C" if f1 == "no" else "?")))
    off = "0" if f4 == "no" else ("1" if f4 == "yes" else "?")
    return "?" if on == "?" else on + off
def primary(f11):
    ps = f11.get("primary_status", "n/d")
    if ps == "one_primary":
        po = f11.get("primary_objectives", "") or ""
        for o in OBJ:
            if o in po: return o
        on = [o for o in OBJ if f11["flags"].get(o)]
        return on[0] if on else "n/d"
    return ps if ps in ("several_joint", "unranked", "conflict") else "n/d"

# ---------- mock generation with trajectories ----------
STATUS_CS = {"LIVE": "operational", "PILOT": "tested", "PREPARATION": "adopted", "EXPLORATION": "option", "PAUSED": "option", "DISCONTINUED": "option"}
def mock_project(p):
    years = p["years"] or [2024]
    cur = {f: "n/d" for f in CELLS}; cs = {f: "option" for f in CELLS}
    flags = {o: False for o in OBJ}
    snaps = []; final_cs = STATUS_CS.get(p["status"], "option")
    det_target = {"LIVE": .98, "PILOT": .97, "PREPARATION": .95, "EXPLORATION": .85, "PAUSED": .85, "DISCONTINUED": .8}.get(p["status"], .8)
    if len(years) == 1: det_target = min(det_target, .75)
    for i, y in enumerate(years):
        last = i == len(years) - 1
        changes = []
        for f in CELLS:
            if cur[f] == "n/d":
                p_det = det_target if last else (0.35 + 0.5 * i / max(1, len(years) - 1))
                if rng.random() < p_det: cur[f] = draw(P[f]); cs[f] = "option"; changes.append(f"{f} first documented: {cur[f]}")
            else:
                if rng.random() < 0.08:
                    old = cur[f]; cur[f] = draw(P[f])
                    if cur[f] != old: changes.append(f"{f} {old} → {cur[f]}")
                if cs[f] == "option" and rng.random() < 0.35: cs[f] = "tested" if p["status"] in ("PILOT", "LIVE") or rng.random() < .5 else "adopted"; changes.append(f"{f} {cs[f]}")
        if last:
            for f in CELLS:
                if cur[f] != "n/d" and final_cs in ("operational", "adopted", "tested"): cs[f] = final_cs if rng.random() < .8 else cs[f]
        for o in OBJ:
            if not flags[o] and rng.random() < (P_OBJ[o] * (0.5 if i == 0 else 0.35)): flags[o] = True; changes.append(f"objective declared: {o}")
        if last and not any(flags.values()): flags["payment_modernisation"] = True
        ps = draw({"one_primary": .4, "several_joint": .3, "unranked": .25, "n/d": .05}) if i == 0 else snaps[-1]["f11"]["primary_status"]
        if i > 0 and rng.random() < .15: ps = draw({"one_primary": .5, "several_joint": .3, "unranked": .2})
        on = [o for o in OBJ if flags[o]]
        po = rng.choice(on) if (ps == "one_primary" and on) else ""
        if i > 0 and ps == "one_primary" and snaps[-1]["f11"]["primary_objectives"] in on and rng.random() < .8: po = snaps[-1]["f11"]["primary_objectives"]
        f11 = {"flags": dict(flags), "primary_status": ps, "primary_objectives": po}
        c = {f: {"value": cur[f]} for f in CELLS}
        snaps.append({"year": y, "cells": dict(cur), "claim_status": dict(cs), "f11": f11, "type": typ(c), "primary": primary(f11), "changes": changes})
    # decisive documents: for each cell, the most recent document (≤ last year) — mock page
    docs_sorted = [d for d in p["docs"] if d["year"]]
    def decisive(y):
        cand = [d for d in docs_sorted if d["year"] <= y] or docs_sorted
        return rng.choice(cand[-3:]) if cand else None
    cells = {}
    last = snaps[-1]
    for f in CELLS:
        d = decisive(last["year"])
        cells[f] = {"value": last["cells"][f], "evidence_state": ("unknown" if last["cells"][f] == "n/d" else draw({"documented": .75, "partial": .2, "conflict": .05})),
                    "claim_status": "" if last["cells"][f] == "n/d" else last["claim_status"][f], "derivation": "explicit" if rng.random() < .9 else "inferred",
                    "doc_id": d["doc_id"] if d else "", "doc_title": d["title"] if d else "", "doc_year": d["year"] if d else "", "doc_url": d["url"] if d else "",
                    "page": rng.randint(3, 60) if (d and last["cells"][f] != "n/d") else "", "quote": "", "provenance": "MOCK"}
    d = decisive(last["year"])
    cells["F11"] = {**last["f11"], "evidence_state": "documented", "claim_status": last["claim_status"]["F1"] or "option", "doc_id": d["doc_id"] if d else "", "doc_title": d["title"] if d else "",
                    "doc_year": d["year"] if d else "", "doc_url": d["url"] if d else "", "page": rng.randint(2, 20), "quote": "", "provenance": "MOCK"}
    return cells, snaps

KEY2CELL = {"F1 CB_LINK_ONLINE": "F1", "F2 PSP_LINK_ONLINE": "F2", "F3 LAWFUL_ACCESS_ROUTE": "F3", "F4 PRIVATE_OFFLINE_AVAILABLE": "F4", "F7 LOW_ID_ROUTE": "F7",
            "F8 ONBOARDING_ID": "F8", "F9 TARGETED_REIDENTIFICATION": "F9", "F10 PROGRAMMABLE_RESTRICTIONS": "F10", "F12 LEDGER_TECHNOLOGY": "F12"}
NORM = {"1": "yes", "0": "no", "true": "yes", "false": "no", "via_psp": "via_PSP", "via_cb": "via_CB", "permissioned_dlt": "permissioned_DLT", "permissionless_dlt": "permissionless_DLT", "unknown": "n/d", "undetermined": "n/d"}
def real_history(p, cells, hist_path):
    """Development profiles: trajectory derived from the pipeline's history.json (stage-1 findings per document and year):
    for each document year, the last 'for' finding per cell up to that year; the final year carries the synthesis values."""
    H = json.load(open(hist_path, encoding="utf-8")) if hist_path and os.path.exists(hist_path) else {}
    years = p["years"]; snaps = []; last_year = years[-1]
    for i, y in enumerate(years):
        last = i == len(years) - 1
        c = {}; cs = {}; changes = []
        for key, f in KEY2CELL.items():
            if last: c[f] = cells[f]["value"]; cs[f] = cells[f]["claim_status"]; continue
            found = [h for h in H.get(key, []) if h["year"] and int(h["year"]) <= y]
            if found:
                v = str(found[-1]["value"]).strip(); v = NORM.get(v.lower(), v); c[f] = v; cs[f] = found[-1].get("claim_status", "")
                if found[-1]["year"] == y and (not snaps or snaps[-1]["cells"].get(f) != v): changes.append(f"{f}: {v} ({cs[f]})")
            else: c[f] = "n/d"; cs[f] = ""
        flags = {}
        for o in OBJ:
            found = [h for h in H.get(f"F11 {o}", []) if h["year"] and int(h["year"]) <= y]
            flags[o] = cells["F11"]["flags"][o] if last else (str(found[-1]["value"]).lower() in ("yes", "1", "true") if found else False)
        f11 = {"flags": flags, "primary_status": cells["F11"]["primary_status"] if last else ("n/d" if not any(flags.values()) else "unranked"), "primary_objectives": cells["F11"]["primary_objectives"] if last else ""}
        snaps.append({"year": y, "cells": c, "claim_status": cs, "f11": f11, "type": typ({f: {"value": c[f]} for f in CELLS}), "primary": primary(f11),
                      "changes": changes if not last else ["synthesis values (contract v1.1 run)"]})
    return snaps

dev_dir = os.path.join(ROOT, "data/worked_profiles")
for code, p in projects.items():
    dev = os.path.join(dev_dir, f"{code}_api_single_v1_1.csv")
    if os.path.exists(dev):
        p["cells"] = load_fill(dev, "development:api_single:claude-opus-5-5:contract_v1.1", p); p["mock"] = False
        core_docs = [d for d in p["docs"] if d["layer"] != "registry"]
        for f, c in p["cells"].items():  # map doc numbers (DOCS.csv order = core docs by year) to registry rows
            try: d = core_docs[int(float(c.get("doc_no", ""))) - 1]; c.update({"doc_id": d["doc_id"], "doc_title": d["title"], "doc_year": d["year"], "doc_url": d["url"]})
            except Exception: pass
        p["history"] = real_history(p, p["cells"], os.path.join(dev_dir, f"{code}_history_two_stage_v1_1.json"))
    elif p["retail"]:
        p["cells"], p["history"] = mock_project(p); p["mock"] = True
    else:
        p["cells"] = None; p["history"] = []; p["mock"] = True
    if p["cells"]:
        p["type"] = typ(p["cells"]); p["primary"] = primary(p["cells"]["F11"])
        p["y1"] = 1 if p["cells"]["F1"]["value"] == "no" else (0 if p["cells"]["F1"]["value"] == "yes" else None)
        p["y3"] = 1 if p["cells"]["F7"]["value"] == "yes" else (0 if p["cells"]["F7"]["value"] == "no" else None)
    else: p["type"] = "n.a."; p["primary"] = "n.a."; p["y1"] = None; p["y3"] = None

# ---------- aggregate time series (for the chart under the map) ----------
YEARS = list(range(2016, 2027))
def as_of(p, y):
    s = None
    for h in p["history"]:
        if h["year"] <= y: s = h
    return s
series = {"type": {}, "primary": {}}
for y in YEARS:
    ct, cp = {}, {}
    for p in projects.values():
        s = as_of(p, y)
        if not s: continue
        ct[s["type"]] = ct.get(s["type"], 0) + 1; cp[s["primary"]] = cp.get(s["primary"], 0) + 1
    series["type"][y] = ct; series["primary"][y] = cp

out = {"as_of": AS_OF, "contract": "MEASUREMENT_CONTRACT_v1_1_2026-10-18", "mock": True,
       "mock_note": "Illustrative mock-up of the finished dataset: all cell values, trajectories and decisive pages are seeded placeholders (not tied to any real project) except the development profiles.",
       "features": features, "objectives": OBJ, "types": ["A0", "A1", "B0", "B1", "C0", "C1"], "years": YEARS, "series": series,
       "projects": sorted(projects.values(), key=lambda p: p["name"])}
os.makedirs(os.path.join(ROOT, "site/assets"), exist_ok=True)
json.dump(out, open(os.path.join(ROOT, "site/assets/data.json"), "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
n = len(projects); retail = sum(1 for p in projects.values() if p["retail"]); dev = sum(1 for p in projects.values() if not p["mock"])
print(f"data.json: {n} projects ({retail} retail), {sum(len(p['docs']) for p in projects.values())} documents, {len(features)} features; development: {dev}; types now:",
      {k: sum(1 for p in projects.values() if p['type'] == k) for k in ["A0", "A1", "B0", "B1", "C0", "C1"]})
