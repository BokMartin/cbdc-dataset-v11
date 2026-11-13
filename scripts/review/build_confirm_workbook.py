#!/usr/bin/env python3
"""Confirmation workbook for evidence documents that rest on the model pre-screen only (MB, 13 Nov 2026: "a separate file, easier to
fill in, with links").

One row per document with decision_v12 KEEP / BORDERLINE and decision_source 'model pre-screen', in the analytic frame, ordered
tier -> project -> year. The author answers in 'decision (authors)':
  OK         reviewed, the proposal stands
  KEEP / BORDERLINE / COMPANION / WHOLESALE / DROP   the author's own decision
An empty cell means NOT REVIEWED (it is not read as agreement). 'effect on tier' says how many evidence documents the project has and
how many would have to go before its tier changes. Sheet ISSUER_CHECK lists the other evidence documents whose proposed issuer or
voice is flagged. Read back with read_tier_decisions.py --partial (the `id` column is the key).

usage: build_confirm_workbook.py --tier-workbook <TIER_REVIEW xlsx> --out <xlsx>
"""
import argparse, collections, re
import openpyxl
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.worksheet.datavalidation import DataValidation
WRAP = Alignment(wrap_text=True, vertical="top"); BOLD = Font(bold=True); BLUE = Font(color="0563C1", underline="single"); YEL = PatternFill("solid", fgColor="FFF2CC"); ORA = PatternFill("solid", fgColor="F4B084")


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--tier-workbook", required=True); ap.add_argument("--out", required=True); a = ap.parse_args()
    wb = openpyxl.load_workbook(a.tier_workbook); rows = []; ev = collections.Counter()
    for s in ("T1", "T2", "T3"):
        ws = wb[s]; h = [c.value for c in ws[1]]
        for r in ws.iter_rows(min_row=2):
            d = dict(zip(h, [c.value for c in r])); m = re.search(r'HYPERLINK\("([^"]+)"', str(d["URL"] or "")); d["url"] = m.group(1) if m else ""; d["sheet"] = s; rows.append(d)
    T = list(openpyxl.load_workbook(a.tier_workbook, read_only=True)["PROJECTS"].iter_rows(values_only=True)); P = {r[0]: dict(zip(T[0], r)) for r in T[1:]}
    def effect(p):
        n = P[p]["evidence docs"]; t = P[p]["tier"]
        if t == "T1": return f"T1, {n} evidence docs; T2 if {n - 7} dropped"
        if t == "T2": return f"T2, {n} evidence docs; T3 if {n - 4} dropped"
        return f"T3, {n} evidence docs"
    todo = [d for d in rows if d["decision_v12"] in ("KEEP", "BORDERLINE") and d["decision_source"] == "model pre-screen"]
    out = Workbook(); ws = out.active; ws.title = "README"
    pc = collections.Counter(d["project"] for d in todo)
    for t in [f"Potvrzení dokumentů evidence, které zatím stojí jen na návrhu modelu: {len(todo)} dokumentů ve {len(pc)} projektech (list CONFIRM). Vytaženo z TIER_REVIEW_v12_2026-11-13c.xlsx; vyplň tento soubor, v tier workbooku tyto řádky vyplňovat nemusíš.",
              "CO TO JE: tyto dokumenty našla rešerše 2. až 3. 11. a model je navrhl zařadit jako evidenci (KEEP) nebo evidenci s výhradou (BORDERLINE). Nikdo z autorů je zatím nepotvrdil. Do měření vstupují už teď, proto je potřeba, aby je autor viděl.",
              "CO VYPLNIT ve sloupci 'decision (authors)': OK = podíval jsem se, návrh platí. Jinak vlastní rozhodnutí: KEEP = evidence; BORDERLINE = evidence s výhradou; COMPANION = doprovodný dokument (tisková zpráva k reportu, rozcestník), sám nic nenese; WHOLESALE = jen velkoobchodní CBDC; DROP = není oficiální nebo neobsahuje nic nosného. PRÁZDNÁ BUŇKA = neprošel jsem (nebere se jako souhlas).",
              "PRAVIDLO ZAŘAZENÍ: dokument vydal příslušný orgán (centrální banka, ministerstvo, vláda, zákonodárce) na oficiálním kanálu; týká se retailové CBDC daného projektu; obsahuje aspoň jeden výrok k soukromí, identifikaci, přístupu k datům, anonymitě, offline platbám, limitům, programovatelnosti, nebo rozhodnutí o stavu projektu. Žánr nerozhoduje: projev guvernéra na webu banky může být evidence.",
              "JAK NA TO RYCHLE: sloupec 'why proposed' říká, co model v dokumentu našel a proč ho navrhl. 'open' otevře zdroj na webu; 'file' je cesta ve složce CBDC_MASTER_v12 v Dropboxu. Většinou stačí ověřit, že dokument existuje, je oficiální a opravdu se týká retailové CBDC; nemusíš ho číst celý. Odhad: 1 až 2 minuty na dokument.",
              "SLOUPEC 'effect on tier': kolik dokumentů evidence projekt má a kolik by jich muselo vypadnout, aby se změnil tier. U projektů těsně nad hranicí (oranžově) na rozhodnutí záleží nejvíc.",
              "VYDAVATEL: sloupce 'issuer' a 'voice' jsou návrh (kdo dokument vydal a zda mluví instituce sama, guvernér v projevu, zaměstnanci, zákon...). Pokud je to špatně, napiš správně do 'issuer / voice (authors)'. Oranžová poznámka v 'issuer check' znamená, že si tím nejsem jistý. List ISSUER_CHECK obsahuje ostatní dokumenty evidence s takovou poznámkou (ty už jsi dříve schválil, jde jen o vydavatele).",
              "Oranžový jazyk = dokument není anglicky. Sloupec 'English text' říká, z jakého textu se čte (originál, anglické vydání vydavatele, strojový překlad), nebo že anglický text zatím chybí.",
              "Sloupec id neměň. Hotový soubor ulož a pošli; načte se skriptem scripts/review/read_tier_decisions.py."]:
        ws.append([t])
    ws.column_dimensions["A"].width = 150
    for r in ws.iter_rows():
        for c in r: c.alignment = WRAP
    cols = ["project", "effect on tier", "year", "title", "proposed", "decision (authors)", "note (authors)", "why proposed", "kind", "language", "pages", "open", "file in CBDC_MASTER_v12", "issuer", "voice", "issuer check", "issuer / voice (authors)", "English text", "id"]
    def sheet(name, data, with_decision=True):
        d_ = out.create_sheet(name); d_.append(cols)
        for d in data:
            p = d["project"]; n = P[p]["evidence docs"]; tight = (P[p]["tier"] == "T1" and n - 7 <= 2) or (P[p]["tier"] == "T2" and n - 4 <= 2)
            d_.append([p, effect(p), d["year"], d["title"], d["decision_v12"], "", "", d["model reason"], d["kind"], d["language"], d["pages"], f'=HYPERLINK("{d["url"]}","open")' if d["url"] else "", d["file in CBDC_MASTER_v12"],
                       d.get("issuer") or "", d.get("voice of document") or "", d.get("issuer check") or "", "", d.get("English text for extraction") or "", d["id"]])
            i = d_.max_row; d_.cell(i, 12).font = BLUE; d_.cell(i, 17).fill = YEL
            if with_decision: d_.cell(i, 6).fill = YEL; d_.cell(i, 7).fill = YEL
            if tight: d_.cell(i, 2).fill = ORA
            if d["language"] and d["language"] != "en": d_.cell(i, 10).fill = ORA
            if d.get("issuer check"): d_.cell(i, 16).fill = ORA
            if str(d.get("English text for extraction") or "").startswith("NO"): d_.cell(i, 18).fill = PatternFill("solid", fgColor="F8CBAD")
        for c, wd in enumerate([7, 22, 6, 55, 11, 14, 28, 55, 14, 8, 6, 7, 36, 26, 16, 30, 24, 20, 11], 1): d_.column_dimensions[d_.cell(1, c).column_letter].width = wd
        for c in range(1, len(cols) + 1): d_.cell(1, c).font = BOLD; d_.cell(1, c).fill = PatternFill("solid", fgColor="DDDDDD")
        for r in d_.iter_rows():
            for c in r: c.alignment = WRAP
        if with_decision:
            dv = DataValidation(type="list", formula1='"OK,KEEP,BORDERLINE,COMPANION,WHOLESALE,DROP"', allow_blank=True); d_.add_data_validation(dv); dv.add(f"F2:F{d_.max_row}")
        d_.freeze_panes = "F2"; d_.auto_filter.ref = f"A1:S{d_.max_row}"
    order = {"T1": 0, "T2": 1, "T3": 2}
    sheet("CONFIRM", sorted(todo, key=lambda d: (order[d["sheet"]], d["project"], str(d["year"]), str(d["title"]))))
    ids = {d["id"] for d in todo}
    sheet("ISSUER_CHECK", sorted([d for d in rows if d["decision_v12"] in ("KEEP", "BORDERLINE") and d["id"] not in ids and d.get("issuer check")], key=lambda d: (d["project"], str(d["year"]))), with_decision=False)
    pj = out.create_sheet("PROJECTS"); pj.append(["project", "tier", "evidence docs", "of these to confirm here", "confirmed earlier (MB)", "what changes the tier"])
    for p in sorted(pc, key=lambda p: (order[P[p]["tier"]], p)): pj.append([p, P[p]["tier"], P[p]["evidence docs"], pc[p], P[p]["evidence docs"] - pc[p], effect(p).split("; ", 1)[-1] if ";" in effect(p) else ""])
    for c in range(1, 7): pj.cell(1, c).font = BOLD; pj.column_dimensions[pj.cell(1, c).column_letter].width = 24
    out.save(a.out)
    print(a.out, "to confirm", len(todo), dict(collections.Counter(d["sheet"] for d in todo)), dict(collections.Counter(d["decision_v12"] for d in todo)), "no link", sum(not d["url"] for d in todo), "non-English", sum(1 for d in todo if d["language"] and d["language"] != "en"), "issuer-check-only rows", out["ISSUER_CHECK"].max_row - 1)


if __name__ == "__main__": main()
