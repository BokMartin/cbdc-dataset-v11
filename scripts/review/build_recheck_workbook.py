#!/usr/bin/env python3
"""RECHECK-only decision workbook (MB, 13 Nov 2026: "a separate doc with rechecks only so it's easier to navigate").

Reads the tier review workbook and writes only the rows with decision_v12 = RECHECK, ordered by how much the decision matters:
  1 the project changes tier if enough of its RECHECK documents are kept (the number needed is shown)
  2 T1/T2 project, tier cannot change (the document would still enter the evidence set)
  3 T3 project, tier cannot change
Outside the 43-frame: separate sheet. The `id` column is the key by which the decisions are read back into
data/manifest/AUTHOR_DECISIONS_<date>.csv; nothing else in the tier workbook has to be filled in for these rows.

usage: build_recheck_workbook.py --tier-workbook <xlsx> --out <xlsx>
"""
import argparse, collections, re
import openpyxl
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.worksheet.datavalidation import DataValidation
WRAP = Alignment(wrap_text=True, vertical="top"); BOLD = Font(bold=True); BLUE = Font(color="0563C1", underline="single")
NEED = {"T3": 5, "T2": 8}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--tier-workbook", required=True); ap.add_argument("--out", required=True); a = ap.parse_args()
    wb = openpyxl.load_workbook(a.tier_workbook); P = {}
    R = list(wb["PROJECTS"].iter_rows(values_only=True))
    for r in R[1:]: P[r[0]] = dict(zip(R[0], r))
    rows = collections.defaultdict(list)
    for s in ("T1", "T2", "T3", "OUT_OF_FRAME"):
        ws = wb[s]; h = [c.value for c in ws[1]]
        for r in ws.iter_rows(min_row=2):
            d = dict(zip(h, [c.value for c in r]))
            if d["decision_v12"] != "RECHECK": continue
            m = re.search(r'HYPERLINK\("([^"]+)"', str(d["URL"] or "")); d["url"] = m.group(1) if m else ""; d["sheet"] = s; rows[s == "OUT_OF_FRAME"].append(d)
    def reach(p):
        ev, rc = p["evidence docs"], p["RECHECK"]
        return "; ".join(f"{t} if {n - ev} of {rc} kept" for t, n in (("T2", 5), ("T1", 8)) if ev < n <= ev + rc)
    def prio(d):
        p = P[d["project"]]; t, up = p["tier"], p["tier if RECHECK kept"]
        if t != up: return 1, f"now {t} ({p['evidence docs']} evidence docs); " + reach(p)
        return (2 if t in ("T1", "T2") else 3), f"{t}, tier cannot change"
    out = Workbook(); ws = out.active; ws.title = "README"
    n1 = sorted({d["project"] for d in rows[False] if prio(d)[0] == 1})
    for t in [f"RECHECK dokumenty k rozhodnutí: {len(rows[False])} v rámci 43 projektů (list RECHECK) a {len(rows[True])} mimo rámec (list OUT_OF_FRAME). Vytaženo z TIER_REVIEW_v12_2026-11-13.xlsx; stačí vyplnit tento soubor, v tier workbooku už tyto řádky vyplňovat nemusíš.",
              "Co vyplnit: sloupec 'decision (authors)' (rozbalovací seznam) a případně 'note'. KEEP = dokument je evidence; BORDERLINE = evidence s výhradou; COMPANION = doprovodný dokument k jinému (tisková zpráva k reportu apod.), sám nic nenese; WHOLESALE = týká se jen velkoobchodní CBDC; DROP = nesplňuje pravidlo (není oficiální nebo neobsahuje nic nosného).",
              "Pravidlo zařazení (docs/SOURCE_RULE_D1.md): vydal příslušný orgán na oficiálním kanálu; týká se retailové CBDC daného projektu; obsahuje aspoň jeden výrok k soukromí, identifikaci, přístupu k datům, anonymitě, offline, limitům, programovatelnosti nebo rozhodnutí o stavu projektu. Žánr nerozhoduje.",
              f"Pořadí řádků: nejdřív priorita 1 = projekty, kterým rozhodnutí změní tier ({', '.join(n1)}); sloupec 'effect on tier' říká, kolik dokumentů projektu by muselo být ponecháno. Pak priorita 2 (T1/T2 beze změny tieru) a 3 (T3 beze změny tieru). List PROJECTS shrnuje stav po projektech.",
              "Sloupec 'model reason' je důvod, proč model dokument nezařadil rovnou: je to nápověda, ne rozhodnutí. 'open' otevře zdroj na webu; 'file' je cesta ve složce CBDC_MASTER_v12 v Dropboxu. Oranžový jazyk = dokument není anglicky; pokud ho ponecháš u projektu T1/T2, půjde do překladu.",
              "U dokumentů ze staršího registru je v 'title' jen kód souboru a chybí odkaz 'open': otevři soubor podle cesty ve sloupci 'file'.", "Sloupec id neměň: podle něj se rozhodnutí načtou zpět. Hotový soubor ulož pod stejným názvem a pošli."]:
        ws.append([t])
    ws.column_dimensions["A"].width = 150
    for r in ws.iter_rows():
        for c in r: c.alignment = WRAP
    cols = ["priority", "project", "effect on tier", "year", "title", "decision (authors)", "note (authors)", "model reason", "kind", "language", "pages", "open", "file in CBDC_MASTER_v12", "issuer", "id"]
    for name, data in (("RECHECK", rows[False]), ("OUT_OF_FRAME", rows[True])):
        d_ = out.create_sheet(name); d_.append(cols)
        key = (lambda d: (prio(d)[0], d["project"], str(d["year"]), str(d["title"]))) if name == "RECHECK" else (lambda d: (d["project"], str(d["year"])))
        for d in sorted(data, key=key):
            pr = prio(d) if name == "RECHECK" else ("", "outside the 43-frame")
            d_.append([pr[0], d["project"], pr[1], d["year"], d["title"], "", "", d["model reason"], d["kind"], d["language"], d["pages"], f'=HYPERLINK("{d["url"]}","open")' if d["url"] else "", d["file in CBDC_MASTER_v12"], d.get("issuer") or "", d["id"]])
            i = d_.max_row; d_.cell(i, 6).fill = PatternFill("solid", fgColor="FFF2CC"); d_.cell(i, 7).fill = PatternFill("solid", fgColor="FFF2CC"); d_.cell(i, 12).font = BLUE
            if pr[0] == 1: d_.cell(i, 3).fill = PatternFill("solid", fgColor="F4B084")
            if d["language"] and d["language"] != "en": d_.cell(i, 10).fill = PatternFill("solid", fgColor="F4B084")
        for c, wd in enumerate([8, 8, 24, 6, 60, 16, 30, 55, 14, 9, 6, 7, 40, 28, 12], 1): d_.column_dimensions[d_.cell(1, c).column_letter].width = wd
        for c in range(1, len(cols) + 1): d_.cell(1, c).font = BOLD; d_.cell(1, c).fill = PatternFill("solid", fgColor="DDDDDD")
        for r in d_.iter_rows():
            for c in r: c.alignment = WRAP
        dv = DataValidation(type="list", formula1='"KEEP,BORDERLINE,COMPANION,WHOLESALE,DROP"', allow_blank=True); d_.add_data_validation(dv); dv.add(f"F2:F{d_.max_row}")
        d_.freeze_panes = "F2"; d_.auto_filter.ref = f"A1:O{d_.max_row}"
    pj = out.create_sheet("PROJECTS"); pj.append(["project", "tier now", "tier if all RECHECK kept", "evidence docs now", "RECHECK to decide", "what moves the tier", "non-English among RECHECK"])
    cnt = collections.Counter(d["project"] for d in rows[False]); ne = collections.Counter(d["project"] for d in rows[False] if d["language"] and d["language"] != "en")
    for p in sorted(cnt, key=lambda p: (P[p]["tier"] == P[p]["tier if RECHECK kept"], P[p]["tier"], p)):
        t = P[p]["tier"]; pj.append([p, t, P[p]["tier if RECHECK kept"], P[p]["evidence docs"], cnt[p], reach(P[p]), ne[p] or ""])
        if t != P[p]["tier if RECHECK kept"]: pj.cell(pj.max_row, 3).fill = PatternFill("solid", fgColor="F4B084")
    for c in range(1, 8): pj.cell(1, c).font = BOLD; pj.column_dimensions[pj.cell(1, c).column_letter].width = 30 if c == 6 else 18
    out.save(a.out); print(a.out, "in frame", len(rows[False]), collections.Counter(prio(d)[0] for d in rows[False]), "out of frame", len(rows[True]), "projects changing tier", n1)


if __name__ == "__main__": main()
