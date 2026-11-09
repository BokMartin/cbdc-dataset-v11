#!/usr/bin/env python3
"""ONE sheet with every document we know of (registry rows + gap-check candidates), for the authors' v12 source decision on all of
them (MB, 9 Nov 2026: "all 772 documents, we must finish collection and filtering").

Columns: id · source (registry / candidate) · project · jur · year · date · title · kind · issuer · language · in 43-frame ·
MB verdict v11 · model proposal (D1 pre-screen or DROP triage) · model reason · load_bearing · decision_v12 (PRE-FILLED, see below) ·
decision_source · decision_note · file (Dropbox path or registry filename) · sha256 · downloaded · link check · URL.

decision_v12 pre-fill (unified vocabulary KEEP / BORDERLINE / DROP / COMPANION / WHOLESALE / RECHECK):
  registry KEEP/BORDERLINE  -> as decided in v11 (decision_source = "MB v11")
  registry DROP             -> model triage mapped (accept->RECHECK, verify_first->RECHECK, companion->COMPANION, wholesale->WHOLESALE,
                               reject->DROP); decision_source = "model triage, title-level"
  candidate                 -> model pre-screen mapped (accept->KEEP, verify_first->RECHECK, companion->COMPANION, wholesale->WHOLESALE,
                               reject->DROP); decision_source = "model pre-screen"
Every pre-filled value is a proposal until the authors confirm it; `read_source_decisions.py` treats decision_source != "author" as unconfirmed.

usage: build_all_documents_workbook.py --url-status <json> --downloads data/manifest/MANUAL_DOWNLOADS_2026-11-09.csv --out <xlsx>
"""
import argparse, csv, json, os, sys, collections, datetime
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE)); sys.path.insert(0, os.path.join(ROOT, "scripts", "frame"))
from registry import load_registry
EURO = {"AT", "BE", "CY", "DE", "EE", "ES", "FI", "FR", "GR", "HR", "IE", "IT", "LT", "LU", "LV", "MT", "NL", "PT", "SI", "SK"}
WRAP = Alignment(wrap_text=True, vertical="top"); BLUE = Font(color="0563C1", underline="single"); BOLD = Font(bold=True)
FILL = {"KEEP": "C6EFCE", "BORDERLINE": "FFEB9C", "RECHECK": "FCE4D6", "COMPANION": "DDEBF7", "WHOLESALE": "EDEDED", "DROP": "F8CBAD"}
MAP_CAND = {"accept": "KEEP", "verify_first": "RECHECK", "companion": "COMPANION", "wholesale": "WHOLESALE", "reject": "DROP"}
MAP_DROP = {"accept": "RECHECK", "verify_first": "RECHECK", "companion": "COMPANION", "wholesale": "WHOLESALE", "reject": "DROP"}


def link_state(u, status):
    if not u: return "no URL"
    s = status.get(u)
    if not s: return "not checked"
    c = str(s[0])
    return {"200": "ok", "404": "dead (404)"}.get(c, "blocked for scripts (open in browser)" if c in ("403", "401", "ERR") else c)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--url-status", required=True); ap.add_argument("--downloads", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--candidates", default=os.path.join(ROOT, "data/manifest/GAP_CHECK_PRESCREEN_2026-11-03.csv"))
    ap.add_argument("--drops", default=os.path.join(ROOT, "data/manifest/V11_DROPS_PRESCREEN_2026-11-03.csv"))
    a = ap.parse_args(); status = json.load(open(a.url_status)); R = load_registry(ROOT)
    frame = {r["project"]: r for r in csv.DictReader(open(os.path.join(ROOT, "data/frame/projects.csv"), encoding="utf-8"))}
    retail = {p for p, r in frame.items() if r.get("retail_candidate") in ("True", "true", "1", "yes")}
    drops = {r["doc_id"]: r for r in csv.DictReader(open(a.drops, encoding="utf-8"))}
    dl = {}
    for r in csv.DictReader(open(a.downloads, encoding="utf-8")):
        dl.setdefault((r["project"], r["url"]), []).append(r)
    C = list(csv.DictReader(open(a.candidates, encoding="utf-8")))
    rows = []
    for r in R:
        p = "EU" if r["jur"] in EURO else r["jur"]; mb = r.get("core_verdict_martin", "") or ("KEEP" if r.get("route") else "")
        tri = drops.get(r["doc_id"], {}); prop = tri.get("proposal", ""); reason = tri.get("reason", "")
        if mb in ("KEEP", "BORDERLINE"): dec, src = mb, "MB v11"
        elif prop: dec, src = MAP_DROP.get(prop, ""), "model triage, title-level"
        else: dec, src = (mb or ""), ("MB v11" if mb else "")
        u = r["url"] or r["source_landing_url"]
        rows.append([r["doc_id"], "registry", p, r["jur"], r["year"], "", (r["title"] or r["fname"])[:220], r["doc_kind"], r.get("source", ""), r["language"], "yes" if p in retail else "no",
                     mb, prop, reason, "", dec, src, "", r["fname"], r["sha256"], "in corpus (v11 registry)" if r["sha256"] else "", link_state(u, status), u])
    for i, r in enumerate(C, 1):
        p = r["project"]; prop = r["proposal"]; dec = MAP_CAND.get(prop, ""); d = dl.get((p, r["url"]), [])
        d = [x for x in d if "linked file" not in x["title"]] or d
        if d:
            x = d[0]; downloaded = "yes, in Dropbox" if x["status"] == "in_dropbox" else "NOT retrieved: " + x["note"]; path = x["dropbox_path"]; sha = x["sha256"]
        else: downloaded = "not yet (download after decision)"; path = ""; sha = ""
        year = (r["date"] or "")[:4]
        rows.append([f"CAND-{i:03d}", "candidate", p, p, year, r["date"], r["title"][:220], r["doc_type"], r["issuer"], "", "yes" if p in retail else "no",
                     "", prop, r["reason"], r["load_bearing"], dec, "model pre-screen", "", path, sha, downloaded, link_state(r["url"], status), r["url"]])
    hdr = ["id", "source", "project", "jur", "year", "date", "title", "kind", "issuer", "language", "in 43-frame", "MB verdict v11", "model proposal", "model reason", "load_bearing",
           "decision_v12", "decision_source", "decision_note", "file", "sha256", "downloaded", "link check", "URL"]
    order = {"KEEP": 0, "BORDERLINE": 1, "RECHECK": 2, "COMPANION": 3, "WHOLESALE": 4, "DROP": 5, "": 6}
    rows.sort(key=lambda x: (x[2], order.get(x[15], 9), str(x[4]), x[6]))
    wb = Workbook(); ws = wb.active; ws.title = "README"
    for t in [f"ALL DOCUMENTS, v12 source decision (built {datetime.date.today().isoformat()}). One row per document we know of: {sum(1 for x in rows if x[1]=='registry')} registry rows + {sum(1 for x in rows if x[1]=='candidate')} gap-check candidates.",
              "Decide in the yellow column decision_v12 for EVERY row. Values: KEEP (evidence document) / BORDERLINE (keep, flag) / DROP (not evidence) / COMPANION (same content as another kept document: cover release, landing page, summary) / WHOLESALE (wholesale-only) / RECHECK (open the file first).",
              "The column is PRE-FILLED: 'decision_source' says who proposed it. 'MB v11' = your October decision (KEEP/BORDERLINE carried over). 'model triage, title-level' = your v11 DROPs re-triaged by the model from titles only (low confidence). 'model pre-screen' = the model's D1 proposal for new candidates. Overwrite whatever you disagree with; when you confirm a row, change decision_source to 'author' (or leave it: read_source_decisions.py will ask for the unconfirmed ones).",
              "Columns 'file' / 'sha256' / 'downloaded': registry documents are in the v11 corpus (Dropbox 'Dizertace all the PDFs'); 126 candidates were fetched on 5 and 9 Nov into Dropbox 'new cbdc files\\<CODE>\\'; 5 could not be retrieved (reason given); the remaining candidates are downloaded by script once accepted.",
              "Rule of record: docs/SOURCE_RULE_D1.md (official body on its own channel; retail CBDC of the project; load-bearing content; genre never decides). As-of 2026-10-18 for the registry; candidates carry their own dates (later documents are dated amendments).",
              "Sheet PROJECTS: counts per project from the pre-filled decisions (KEEP+BORDERLINE) and the indicative tier (T1 >= 8, T2 5-7, T3 <= 4). Final tiers are recomputed from your decisions."]:
        ws.append([t])
    ws.column_dimensions["A"].width = 180
    for row in ws.iter_rows():
        for c in row: c.alignment = WRAP
    d = wb.create_sheet("ALL_DOCUMENTS"); d.append(hdr)
    dv = DataValidation(type="list", formula1='"KEEP,BORDERLINE,DROP,COMPANION,WHOLESALE,RECHECK"', allow_blank=True); d.add_data_validation(dv)
    for i, x in enumerate(rows, 2):
        u = x[22]; x = list(x); x[22] = f'=HYPERLINK("{u}","open")' if u else ""
        d.append(x)
        if u: d.cell(i, 23).font = BLUE
        f = FILL.get(x[15]);
        if f: d.cell(i, 16).fill = PatternFill("solid", fgColor=f)
        else: d.cell(i, 16).fill = PatternFill("solid", fgColor="FFF2CC")
        dv.add(d.cell(i, 16))
        if x[11] in FILL: d.cell(i, 12).fill = PatternFill("solid", fgColor=FILL[x[11]])
    widths = [12, 9, 6, 5, 6, 10, 55, 14, 22, 8, 7, 11, 12, 44, 15, 13, 20, 24, 40, 14, 22, 20, 7]
    for c, w in enumerate(widths, 1): d.column_dimensions[get_column_letter(c)].width = w
    for c in range(1, len(hdr) + 1): d.cell(1, c).font = BOLD; d.cell(1, c).fill = PatternFill("solid", fgColor="DDDDDD")
    for row in d.iter_rows():
        for c in row: c.alignment = WRAP
    d.freeze_panes = "H2"; d.auto_filter.ref = f"A1:{get_column_letter(len(hdr))}{len(rows)+1}"
    # PROJECTS
    pj = wb.create_sheet("PROJECTS")
    cnt = collections.defaultdict(collections.Counter)
    for x in rows: cnt[x[2]][x[15] or "undecided"] += 1
    pj.append(["project", "in 43-frame", "status", "rows total", "KEEP", "BORDERLINE", "RECHECK", "COMPANION", "WHOLESALE", "DROP", "undecided", "evidence (KEEP+BORDERLINE)", "upper bound (+RECHECK)", "indicative tier", "tier (authors)", "note"])
    for p in sorted(cnt):
        c = cnt[p]; ev = c["KEEP"] + c["BORDERLINE"]; hi = ev + c["RECHECK"]
        tier = ("T1" if ev >= 8 else "T2" if ev >= 5 else "T3") if p in retail else "out of frame"
        pj.append([p, "yes" if p in retail else "no", frame.get(p, {}).get("status", ""), sum(c.values()), c["KEEP"], c["BORDERLINE"], c["RECHECK"], c["COMPANION"], c["WHOLESALE"], c["DROP"], c["undecided"], ev, hi, tier, "", ""])
    for c, w in enumerate([8, 10, 14, 9, 7, 11, 9, 11, 11, 7, 10, 14, 14, 12, 12, 30], 1): pj.column_dimensions[get_column_letter(c)].width = w
    for c in range(1, 17): pj.cell(1, c).font = BOLD; pj.cell(1, c).fill = PatternFill("solid", fgColor="DDDDDD")
    pj.freeze_panes = "B2"
    wb.save(a.out); print(a.out, len(rows), "rows;", dict(collections.Counter(x[15] or "undecided" for x in rows)))


if __name__ == "__main__": main()
