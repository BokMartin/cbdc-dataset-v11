#!/usr/bin/env python3
"""One review workbook for the v12 source decision: every registered document (with the authors' v11 verdicts) and every
gap-check candidate, with working links, link-check status, model pre-screen proposals and an empty v12 decision column.

Sheets: README · DOCUMENTS (registry + dated additions; v11 verdict carried; decision_v12 pre-filled with the v11 verdict for
KEEP/BORDERLINE, and with the D1 triage proposal for v11 DROPs) · CANDIDATES (gap check, pre-screen proposal) · PROJECTS (counts
per project for the T1/T2/T3 split) · LINKS (link-check legend). Decisions are read back by scripts/review/read_source_decisions.py.

usage: build_source_review_workbook.py --url-status <json> --out <xlsx> [--drops-prescreen data/manifest/V11_DROPS_PRESCREEN_2026-11-03.csv]
"""
import argparse, csv, json, os, sys, collections, re
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE)); sys.path.insert(0, os.path.join(ROOT, "scripts", "frame"))
from registry import load_registry
EURO = {"AT", "BE", "CY", "DE", "EE", "ES", "FI", "FR", "GR", "HR", "IE", "IT", "LT", "LU", "LV", "MT", "NL", "PT", "SI", "SK"}
WRAP = Alignment(wrap_text=True, vertical="top"); BLUE = Font(color="0563C1", underline="single"); BOLD = Font(bold=True)
FILL = {"accept": "C6EFCE", "KEEP": "C6EFCE", "BORDERLINE": "FFEB9C", "companion": "DDEBF7", "verify_first": "FCE4D6", "wholesale": "EDEDED", "reject": "F8CBAD", "DROP": "F8CBAD", "recheck": "FFEB9C"}


def link_state(u, status):
    if not u: return "no URL"
    s = status.get(u)
    if not s: return "not checked"
    code = str(s[0])
    if code == "200": return "ok"
    if code == "404": return "dead (404)"
    if code in ("403", "401", "ERR"): return "blocked for scripts (open in browser)"
    return code


def style(ws, widths, nhdr):
    for c, w in enumerate(widths, 1): ws.column_dimensions[get_column_letter(c)].width = w
    for c in range(1, nhdr + 1): ws.cell(1, c).font = BOLD; ws.cell(1, c).fill = PatternFill("solid", fgColor="DDDDDD")
    for row in ws.iter_rows():
        for c in row: c.alignment = WRAP
    ws.freeze_panes = "C2"


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--url-status", required=True); ap.add_argument("--out", required=True); ap.add_argument("--drops-prescreen", default="")
    ap.add_argument("--candidates", default=os.path.join(ROOT, "data/manifest/GAP_CHECK_PRESCREEN_2026-11-03.csv"))
    a = ap.parse_args(); status = json.load(open(a.url_status)); R = load_registry(ROOT)
    lic = {r["doc_id"]: r["licence_class"] for r in csv.DictReader(open(os.path.join(ROOT, "data/registry/DOC_LICENCES_2026-11-02.csv"), encoding="utf-8"))}
    man = {r["doc_id"]: r for r in csv.DictReader(open(os.path.join(ROOT, "data/manifest/SOURCE_MANIFEST_v12_DRAFT.csv"), encoding="utf-8"))}
    drops = {}
    if a.drops_prescreen and os.path.exists(a.drops_prescreen):
        for r in csv.DictReader(open(a.drops_prescreen, encoding="utf-8")): drops[(r["project"], r["title"][:160])] = r
    wb = Workbook(); ws = wb.active; ws.title = "README"
    for t in ["SOURCE DECISION WORKBOOK, v12 (built " + __import__("datetime").date.today().isoformat() + "). One row per document we know of. Decide in the yellow column; everything else is information.",
              "DOCUMENTS: every registered document (391 + 3 issuer English editions). Column 'MB verdict v11' is what you decided in October under the genre rubric; 'decision_v12' is pre-filled: KEEP/BORDERLINE carried over, DROP replaced by the model's D1 triage (title-level, low confidence: 'recheck' means the genre may have been the only reason). Change whatever you disagree with. Values: KEEP / BORDERLINE / DROP / WHOLESALE / COMPANION.",
              "CANDIDATES: the 378 gap-check documents not in the registry, with the model's D1 pre-screen proposal and reason. Decide in 'author_decision': accept / reject / companion / wholesale / verify_first (= fetch from browser first).",
              "Links: 'ok' opened by script; 'blocked for scripts' = the site refuses automated access but normally opens in a browser; 'dead (404)' = needs a new URL; 'no URL' = registry row without a source URL (non-core rows mostly).",
              "PROJECTS: counts per project (registered KEEP/BORDERLINE under v11; candidates proposed accept) as the basis for the T1/T2/T3 split; final tiers are computed from your decisions, not from these proposals.",
              "Rule of record: docs/SOURCE_RULE_D1.md. Official body on its own channel; retail CBDC of the project; load-bearing content (status decision, design position, legal provision, explicit privacy/identifiability statement); genre never decides; as-of 2026-10-18."]:
        ws.append([t])
    ws.column_dimensions["A"].width = 170
    for row in ws.iter_rows():
        for c in row: c.alignment = WRAP
    # DOCUMENTS
    d = wb.create_sheet("DOCUMENTS")
    hdr = ["project", "jur", "doc_id", "year", "title / filename", "kind", "scope", "source_type", "language", "route", "MB verdict v11", "pipeline verdict v11", "cat_martin", "note_martin", "core_v1/v2", "D1 triage (model, title-level)", "triage reason", "decision_v12", "decision_note", "OPEN", "link check", "licence", "sha256"]
    d.append(hdr); dv = DataValidation(type="list", formula1='"KEEP,BORDERLINE,DROP,WHOLESALE,COMPANION"', allow_blank=True); d.add_data_validation(dv)
    rows = sorted(R, key=lambda r: (("EU" if r["jur"] in EURO else r["jur"]), r["year"], r["doc_id"]))
    for i, r in enumerate(rows, 2):
        p = "EU" if r["jur"] in EURO else r["jur"]; u = r["url"] or r["source_landing_url"]; mb = r.get("core_verdict_martin", "") or ("KEEP" if r.get("route") else "")
        tri = drops.get((p, (r["title"] or r["fname"])[:160]), {}); prop = tri.get("proposal", ""); reason = tri.get("reason", "")
        triage = {"accept": "recheck → KEEP?", "companion": "COMPANION", "wholesale": "WHOLESALE", "reject": "DROP", "verify_first": "recheck"}.get(prop, "")
        dec = mb if mb in ("KEEP", "BORDERLINE") else ({"accept": "", "verify_first": "", "companion": "COMPANION", "wholesale": "WHOLESALE", "reject": "DROP"}.get(prop, ""))
        d.append([p, r["jur"], r["doc_id"], r["year"], (r["title"] or r["fname"])[:200], r["doc_kind"], r["scope"], r["source_type"], r["language"], man.get(r["doc_id"], {}).get("route", r.get("route", "")), mb, r.get("core_verdict", ""), r.get("cat_martin", ""), r.get("note_martin", ""),
                  (r["core_v1"] or r["core_v2"]), triage, reason, dec, "", f'=HYPERLINK("{u}","open")' if u else "", link_state(u, status), lic.get(r["doc_id"], ""), r["sha256"][:12]])
        if u: d.cell(i, 20).font = BLUE
        f = FILL.get(mb if mb in ("KEEP", "BORDERLINE", "DROP") else "", None)
        if f: d.cell(i, 11).fill = PatternFill("solid", fgColor=f)
        d.cell(i, 18).fill = PatternFill("solid", fgColor="FFF2CC"); dv.add(d.cell(i, 18))
        if prop == "accept": d.cell(i, 16).fill = PatternFill("solid", fgColor=FILL["recheck"])
    style(d, [6, 5, 34, 6, 50, 14, 10, 11, 8, 8, 11, 11, 11, 20, 9, 16, 44, 13, 24, 7, 22, 18, 13], len(hdr))
    # CANDIDATES
    c = wb.create_sheet("CANDIDATES")
    C = list(csv.DictReader(open(a.candidates, encoding="utf-8")))
    hdr2 = ["project", "date", "doc_type", "title", "issuer", "proposal (model, D1)", "load_bearing", "reason", "relevance", "content_note", "confidence", "already_in_registry", "author_decision", "decision_note", "OPEN", "link check", "url"]
    c.append(hdr2); dv2 = DataValidation(type="list", formula1='"accept,reject,companion,wholesale,verify_first"', allow_blank=True); c.add_data_validation(dv2)
    order = {"accept": 0, "verify_first": 1, "companion": 2, "wholesale": 3, "reject": 4}
    for i, r in enumerate(sorted(C, key=lambda r: (r["project"], order.get(r["proposal"], 9), r["date"])), 2):
        c.append([r["project"], r["date"], r["doc_type"], r["title"], r["issuer"], r["proposal"], r["load_bearing"], r["reason"], r["relevance"], r["content_note"], r["confidence"], r["already_in_registry"], r.get("author_decision", ""), r.get("decision_note", ""), f'=HYPERLINK("{r["url"]}","open")' if r["url"] else "", link_state(r["url"], status), r["url"]])
        if r["url"]: c.cell(i, 15).font = BLUE
        f = FILL.get(r["proposal"]);
        if f: c.cell(i, 6).fill = PatternFill("solid", fgColor=f)
        c.cell(i, 13).fill = PatternFill("solid", fgColor="FFF2CC"); dv2.add(c.cell(i, 13))
    style(c, [6, 10, 13, 48, 22, 13, 15, 44, 30, 40, 9, 16, 14, 24, 7, 22, 40], len(hdr2))
    # PROJECTS
    pj = wb.create_sheet("PROJECTS"); frame = {r["project"]: r for r in csv.DictReader(open(os.path.join(ROOT, "data/frame/projects.csv"), encoding="utf-8"))}
    reg = collections.Counter(); regk = collections.Counter(); cand = collections.Counter(); canda = collections.Counter(); recheck = collections.Counter()
    for r in rows:
        p = "EU" if r["jur"] in EURO else r["jur"]; reg[p] += 1
        if (r.get("core_verdict_martin") or "") in ("KEEP", "BORDERLINE") or r.get("route"): regk[p] += 1
        tri = drops.get((p, (r["title"] or r["fname"])[:160]), {})
        if tri.get("proposal") in ("accept", "verify_first"): recheck[p] += 1
    for r in C:
        cand[r["project"]] += 1
        if r["proposal"] == "accept": canda[r["project"]] += 1
    pj.append(["project", "in 43-frame", "status", "registered (all)", "registered KEEP/BORDERLINE v11", "v11 DROPs flagged for recheck", "gap candidates", "candidates proposed accept", "indicative load-bearing total", "tier (fill)", "note"])
    for p in sorted(set(list(reg) + list(cand))):
        fr = frame.get(p, {}); tot = regk[p] + canda[p]
        pj.append([p, fr.get("retail_candidate", ""), fr.get("status", ""), reg[p], regk[p], recheck[p], cand[p], canda[p], tot, "", ""])
    style(pj, [8, 10, 14, 12, 16, 16, 12, 16, 16, 9, 30], 11); pj.freeze_panes = "B2"
    wb.save(a.out); print(a.out, len(rows), "documents,", len(C), "candidates")


if __name__ == "__main__": main()
