#!/usr/bin/env python3
"""Tier review workbook (MB, 10 Nov 2026: "rozděl dokumenty na T1 / T2 a T3 (nepoužíváme), podle zemí a let, ručně překontroluju").

Tier of a PROJECT = number of evidence documents (decision_v12 KEEP or BORDERLINE): T1 >= 8, T2 5-7, T3 <= 4 (same thresholds as the
PROJECTS sheet of the all-documents workbook). T3 projects are listed but not used for the year-by-year series. Because decision_v12 is
still a pre-fill until the authors confirm it, the workbook shows two tiers: `tier` (KEEP+BORDERLINE as they stand) and `tier if RECHECK
kept` (upper bound), and marks every project whose tier would change. The authors write the final tier in `tier (authors)`.

Sheets: README · PROJECTS (tier, counts, evidence documents per year 2018-2026, non-English evidence) · T1 · T2 · T3 · OUT_OF_FRAME
(one row per document, sorted project -> year -> decision; evidence rows first within a year) .
Inputs: the all-documents workbook (decisions), the master manifest (file in CBDC_MASTER_v12), the language detection.

usage: build_tier_workbook.py --workbook <ALL xlsx> --manifest data/manifest/MASTER_MANIFEST_2026-11-10.csv --language data/manifest/MASTER_LANGUAGE_2026-11-10.csv --out <xlsx> [--csv data/manifest/TIERS_2026-11-10.csv]
"""
import argparse, csv, collections, datetime, re
import openpyxl
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter
WRAP = Alignment(wrap_text=True, vertical="top"); BOLD = Font(bold=True); BLUE = Font(color="0563C1", underline="single")
FILL = {"KEEP": "C6EFCE", "BORDERLINE": "FFEB9C", "RECHECK": "FCE4D6", "COMPANION": "DDEBF7", "WHOLESALE": "EDEDED", "DROP": "F8CBAD"}
TFILL = {"T1": "A9D08E", "T2": "FFE699", "T3": "D9D9D9"}
ORDER = {"KEEP": 0, "BORDERLINE": 1, "RECHECK": 2, "COMPANION": 3, "WHOLESALE": 4, "DROP": 5, "": 6}
YEARS = [str(y) for y in range(2018, 2027)]


def tier(n): return "T1" if n >= 8 else "T2" if n >= 5 else "T3"


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--workbook", required=True); ap.add_argument("--manifest", required=True); ap.add_argument("--language", required=True)
    ap.add_argument("--out", required=True); ap.add_argument("--csv")
    a = ap.parse_args()
    wbi = openpyxl.load_workbook(a.workbook, read_only=True); R = list(wbi["ALL_DOCUMENTS"].iter_rows(values_only=True)); hdr = R[0]
    W = [dict(zip(hdr, r)) for r in R[1:]]
    # author decisions recorded after the workbook was built (data/manifest/AUTHOR_DECISIONS_<date>.csv) override its pre-fill
    import glob, os
    for f in sorted(glob.glob(os.path.join(os.path.dirname(os.path.abspath(a.manifest)), "AUTHOR_DECISIONS_*.csv"))):
        dec = {r["id"]: r for r in csv.DictReader(open(f, encoding="utf-8"))}
        for w in W:
            if w["id"] in dec: w["decision_v12"] = dec[w["id"]]["decision_v12"]; w["decision_source"] = "author"
    P = {r[0]: dict(zip(list(wbi["PROJECTS"].iter_rows(min_row=1, max_row=1, values_only=True))[0], r)) for r in wbi["PROJECTS"].iter_rows(min_row=2, values_only=True)}
    lang = {r["sha256"]: r for r in csv.DictReader(open(a.language, encoding="utf-8"))}
    man = collections.defaultdict(list)
    for r in csv.DictReader(open(a.manifest, encoding="utf-8")): man[r["workbook_id"]].append(r)
    docs = collections.defaultdict(list)
    for w in W:
        # the linked PDF ("__attachment-1" / "__official-download") is the document, the HTML page of the same name its landing page
        allf = man.get(w["id"], []); en_ed = [m for m in allf if m["source"] == "english_edition"]  # route-B English editions are shown, the row keeps the original as its file
        files = sorted([m for m in allf if m["source"] != "english_edition"], key=lambda m: (not re.search(r"__(attachment-\d+|official-download)\.", m["fname"]), m["fname"])); f = files[0] if files else None
        l = lang.get(f["sha256"], {}) if f else {}
        y = str(w["year"] or "").strip(); y = y if re.fullmatch(r"(19|20)\d\d", y) else "n.d."
        docs[w["project"]].append({**w, "y": y, "dec": w["decision_v12"] or "", "master": f["master_path"] if f else "", "ext": f["ext"] if f else "", "nfiles": len(files), "en_ed": en_ed[0]["master_path"] if en_ed else "",
                                   "lang": l.get("lang_class", ""), "share_en": l.get("share_en", ""), "pages": l.get("pages", ""), "lflag": l.get("flag", ""), "sha": f["sha256"] if f else ""})
    proj = {}
    for p, ds in docs.items():
        ev = [d for d in ds if d["dec"] in ("KEEP", "BORDERLINE")]; rc = [d for d in ds if d["dec"] == "RECHECK"]
        frame = (P.get(p, {}).get("in 43-frame") == "yes"); union = p == "EU"
        t = tier(len(ev)); tu = tier(len(ev) + len(rc))
        yrs = sorted(d["y"] for d in ev if d["y"] != "n.d.")
        proj[p] = {"project": p, "frame": "yes" if frame else ("union project (digital euro)" if union else "no"), "status": P.get(p, {}).get("status") or "", "n": len(ds), "ev": len(ev), "keep": sum(d["dec"] == "KEEP" for d in ev),
                   "bord": sum(d["dec"] == "BORDERLINE" for d in ev), "rc": len(rc), "tier": t, "tier_up": tu, "group": t if (frame or union) else "OUT_OF_FRAME",
                   "first": yrs[0] if yrs else "", "last": yrs[-1] if yrs else "", "byyear": collections.Counter(d["y"] for d in ev),
                   "non_en": sum(1 for d in ev if d["lang"] and d["lang"] != "en"), "no_lang": sum(1 for d in ev if not d["lang"]), "unconfirmed": sum(1 for d in ev + rc if d["decision_source"] != "author")}
    wb = Workbook(); ws = wb.active; ws.title = "README"
    cnt = collections.Counter(v["group"] for v in proj.values()); move = [p for p, v in proj.items() if v["group"] != "OUT_OF_FRAME" and v["tier"] != v["tier_up"]]
    for t in [f"TIER REVIEW, v12 (built {datetime.date.today().isoformat()}). Projects by number of evidence documents: T1 >= 8, T2 5-7, T3 <= 4 (T3 is listed but not used for the year-by-year series).",
              f"Counts now: T1 {cnt['T1']} projects, T2 {cnt['T2']}, T3 {cnt['T3']}, outside the 43-frame {cnt['OUT_OF_FRAME']}. Evidence document = decision_v12 KEEP or BORDERLINE in the all-documents workbook.",
              f"CAUTION: decision_v12 is still a PRE-FILL (your v11 verdicts + model proposals). {len(move)} projects would move up a tier if their RECHECK documents are kept: {', '.join(sorted(move))}. Column 'tier if RECHECK kept' shows the upper bound. Decide the RECHECK rows first; the tier follows.",
              "How to check: sheets T1, T2, T3 list every document of the projects in that tier, sorted project -> year -> decision (evidence rows first, green/yellow). Change 'decision (authors)' where you disagree, and write the final tier in PROJECTS column 'tier (authors)'. The digital euro (EU) is tiered as the union project; euro-area members' own documents sit under EU.",
              "Columns 'language' / 'share EN' come from page-level detection (lingua) of the file in CBDC_MASTER_v12; 'scanned_or_image' = no text layer, OCR needed. Non-English evidence documents of T1/T2 projects are listed separately in TRANSLATION_QUEUE (data/translation/).",
              "Year = year of the document as recorded in the registry / pre-screen; 'n.d.' = undated (left off the time axis). Rule of record for inclusion: docs/SOURCE_RULE_D1.md."]:
        ws.append([t])
    ws.column_dimensions["A"].width = 170
    for row in ws.iter_rows():
        for c in row: c.alignment = WRAP
    pj = wb.create_sheet("PROJECTS")
    ph = ["project", "tier", "tier if RECHECK kept", "tier (authors)", "in 43-frame", "status", "evidence docs", "KEEP", "BORDERLINE", "RECHECK", "all rows", "first year", "last year"] + YEARS + ["n.d.", "non-English evidence", "evidence w/o file or text", "unconfirmed rows (evidence+RECHECK)", "note"]
    pj.append(ph)
    go = {"T1": 0, "T2": 1, "T3": 2, "OUT_OF_FRAME": 3}
    for v in sorted(proj.values(), key=lambda v: (go[v["group"]], -v["ev"], v["project"])):
        pj.append([v["project"], v["tier"] if v["group"] != "OUT_OF_FRAME" else "out of frame", v["tier_up"] if v["group"] != "OUT_OF_FRAME" else "", "", v["frame"], v["status"], v["ev"], v["keep"], v["bord"], v["rc"], v["n"], v["first"], v["last"]]
                  + [v["byyear"].get(y, 0) or "" for y in YEARS] + [v["byyear"].get("n.d.", 0) or "", v["non_en"] or "", v["no_lang"] or "", v["unconfirmed"] or "", "moves up if RECHECK kept" if v["group"] != "OUT_OF_FRAME" and v["tier"] != v["tier_up"] else ""])
        i = pj.max_row
        if v["group"] in TFILL: pj.cell(i, 2).fill = PatternFill("solid", fgColor=TFILL[v["tier"]])
        if v["group"] != "OUT_OF_FRAME" and v["tier"] != v["tier_up"]: pj.cell(i, 3).fill = PatternFill("solid", fgColor="F4B084")
        pj.cell(i, 4).fill = PatternFill("solid", fgColor="FFF2CC")
    for c, wd in enumerate([8, 6, 10, 9, 14, 14, 9, 6, 11, 9, 7, 7, 7] + [5] * 10 + [10, 10, 12, 24], 1): pj.column_dimensions[get_column_letter(c)].width = wd
    for c in range(1, len(ph) + 1): pj.cell(1, c).font = BOLD; pj.cell(1, c).fill = PatternFill("solid", fgColor="DDDDDD"); pj.cell(1, c).alignment = WRAP
    pj.freeze_panes = "B2"; pj.auto_filter.ref = f"A1:{get_column_letter(len(ph))}{pj.max_row}"
    dh = ["project", "tier", "year", "date", "decision_v12", "decision (authors)", "decision_source", "title", "kind", "language", "share EN", "pages", "source", "MB verdict v11", "model reason", "file in CBDC_MASTER_v12", "text flag", "URL", "id", "note (authors)"]
    out_rows = []
    for g in ["T1", "T2", "T3", "OUT_OF_FRAME"]:
        d = wb.create_sheet(g); d.append(dh)
        for p in sorted(k for k, v in proj.items() if v["group"] == g):
            for x in sorted(docs[p], key=lambda x: (x["y"], ORDER.get(x["dec"], 9), str(x["title"]))):
                u = x["URL"] or ""; m = re.search(r'HYPERLINK\("([^"]+)"', str(u)); u = m.group(1) if m else u
                d.append([p, proj[p]["tier"] if g != "OUT_OF_FRAME" else "", x["y"], x["date"] or "", x["dec"], "", x["decision_source"] or "", x["title"], x["kind"] or "", x["lang"], x["share_en"], x["pages"], x["source"], x["MB verdict v11"] or "", x["model reason"] or "",
                          (x["master"] + (f" (+{x['nfiles']-1} linked)" if x["nfiles"] > 1 else "") if x["master"] else (x["downloaded"] or "")) + (" | EN edition: " + x["en_ed"] if x["en_ed"] else ""), x["lflag"], f'=HYPERLINK("{u}","open")' if u else "", x["id"], ""])
                i = d.max_row
                if x["dec"] in FILL: d.cell(i, 5).fill = PatternFill("solid", fgColor=FILL[x["dec"]])
                d.cell(i, 6).fill = PatternFill("solid", fgColor="FFF2CC")
                if x["lang"] and x["lang"] != "en": d.cell(i, 10).fill = PatternFill("solid", fgColor="F4B084")
                if u: d.cell(i, 18).font = BLUE
                out_rows.append({"project": p, "tier": proj[p]["tier"] if g != "OUT_OF_FRAME" else "out_of_frame", "tier_if_recheck_kept": proj[p]["tier_up"] if g != "OUT_OF_FRAME" else "", "year": x["y"], "id": x["id"], "decision_v12": x["dec"], "decision_source": x["decision_source"] or "",
                                 "language": x["lang"], "share_en": x["share_en"], "pages": x["pages"], "text_flag": x["lflag"], "master_path": x["master"], "sha256": x["sha"], "title": x["title"]})
        for c, wd in enumerate([7, 5, 6, 10, 12, 12, 16, 60, 14, 9, 7, 6, 9, 10, 40, 46, 16, 7, 12, 24], 1): d.column_dimensions[get_column_letter(c)].width = wd
        for c in range(1, len(dh) + 1): d.cell(1, c).font = BOLD; d.cell(1, c).fill = PatternFill("solid", fgColor="DDDDDD")
        for row in d.iter_rows(min_row=1, max_row=d.max_row):
            for c in row: c.alignment = WRAP
        d.freeze_panes = "I2"; d.auto_filter.ref = f"A1:{get_column_letter(len(dh))}{d.max_row}"
    wb.save(a.out)
    if a.csv:
        with open(a.csv, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(out_rows[0].keys())); w.writeheader(); w.writerows(out_rows)
    print(a.out, dict(cnt), "; would move up:", sorted(move))


if __name__ == "__main__": main()
