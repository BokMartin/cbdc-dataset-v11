#!/usr/bin/env python3
"""Workbook with only the rows on which the two authors differ, for a joint walk-through (17 Nov 2026).

Sheet RELEVANCE: development units where the blind relevance labels of MB and DS differ, or one of them gave no valid label.
Sheet PREKLAD: translation benchmark pairs where the two judges' codes differ.
The joint decisions made in this workbook are adjudicated labels: they are stored apart from the blind labels and never replace them.
The workbook holds source text and is not committed.

usage: build_disagreement_workbook.py --dev-mb <xlsx> --dev-ds <xlsx> --tr-mb <xlsx> --tr-ds <xlsx> --out <xlsx>
"""
import argparse, csv, glob, os
import openpyxl
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.worksheet.datavalidation import DataValidation
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
clean = lambda t: ("'" + t if isinstance(t, str) and t and t[0] in "=+-@" else t)


def grid(path, sheet): return [[c.value for c in r] for r in openpyxl.load_workbook(path)[sheet].iter_rows()]


def sheet(wb, name, cols, rows, widths, lists):
    w = wb.create_sheet(name); w.append(cols)
    for r in rows: w.append([clean(x) for x in r])
    for c in w[1]: c.font = Font(bold=True, color="FFFFFF"); c.fill = PatternFill("solid", fgColor="1F3A5F"); c.alignment = Alignment(wrap_text=True, vertical="top")
    for i, wd in enumerate(widths): w.column_dimensions[openpyxl.utils.get_column_letter(i + 1)].width = wd
    for row in w.iter_rows(min_row=2):
        for c in row: c.alignment = Alignment(wrap_text=True, vertical="top")
    for col, lst in lists.items():
        if lst:
            dv = DataValidation(type="list", formula1='"' + lst + '"', allow_blank=True); w.add_data_validation(dv); dv.add(f"{col}2:{col}{len(rows) + 1}")
        for r in range(2, len(rows) + 2): w[f"{col}{r}"].fill = PatternFill("solid", fgColor="FFF2CC")
    w.freeze_panes = "A2"; w.auto_filter.ref = w.dimensions


def main():
    ap = argparse.ArgumentParser()
    for k in ("dev-mb", "dev-ds", "tr-mb", "tr-ds", "out"): ap.add_argument("--" + k, required=True)
    a = ap.parse_args(); V = ("R", "N", "U")
    A, B = grid(a.dev_mb, "CODE"), grid(a.dev_ds, "CODE"); h = B[0]; ir = h.index("relevant")
    lab = lambda r: (str(r[ir]).strip().upper() if r[ir] else "")
    man = {r["doc_key"] for r in csv.DictReader(open(sorted(glob.glob(os.path.join(ROOT, "data/units/UNITS_MANIFEST_*.csv")))[-1], encoding="utf-8"))}
    rel = []
    rowA = {r[1]: (n, r) for n, r in enumerate(A[1:], start=2)}; assert set(rowA) == {r[1] for r in B[1:]}, "the two workbooks do not hold the same units"
    for nb, rb in enumerate(B[1:], start=2):
        n, ra = rowA[rb[1]]; n = f"MB {n} / DS {nb}"; x, y = lab(ra), lab(rb)
        if x == y and x in V: continue
        kind = "MB bez platného štítku" if x not in V else ("1 R proti N" if {x, y} == {"R", "N"} else ("2 U proti R" if {x, y} == {"U", "R"} else "3 U proti N"))
        rel.append([kind, n, rb[1], rb[2], rb[4], rb[5], rb[7], rb[8], rb[9], x or "(prázdné)", y, None, None, None, "" if rb[1].split(":p")[0] in man else "dokument už není v evidenci"])
    rel.sort(key=lambda r: (r[0], r[3], r[2]))
    TA, TB = grid(a.tr_mb, "JUDGE"), grid(a.tr_ds, "JUDGE"); tr = []
    rowT = {r[0]: r for r in TA[1:]}; assert set(rowT) == {r[0] for r in TB[1:]}
    for rb in TB[1:]:
        ra = rowT[rb[0]]; assert ra[2] == rb[2] and ra[3] == rb[3], "sentence pair differs between the two workbooks"; x, y = str(ra[4]).strip().upper(), str(rb[4]).strip().upper()
        if x != y: tr.append([f"MB {x} / DS {y}", ra[0], ra[1], ra[2], ra[3], x, y, None, None, None])
    tr.sort(key=lambda r: (r[0], r[1]))
    wb = openpyxl.Workbook(); w = wb.active; w.title = "CTI_ME"
    for t in ["Neshody MB a DS k společnému projití (17. 11. 2026)", "",
              f"List RELEVANCE: {len(rel)} vět vývojového vzorku, kde se vaše slepé štítky liší (nebo jeden chybí). Seřazeno podle typu neshody: nejdřív R proti N, pak U proti R, pak U proti N.",
              "  spolecny_stitek: na čem se shodnete (R / N / U).",
              "  proc_neshoda: A = jeden z nás se přehlédl · B = pravidlo v kódovníku je nejasné nebo chybí · C = věta není použitelná (nadpis, úlomek, tabulka) · D = bez širšího kontextu nejde rozhodnout.",
              "  pravidlo: u typu B napište jednou větou pravidlo, které by neshodu rozhodlo. Z těchto vět vznikne oprava kódovníku; to je hlavní účel.",
              "",
              f"List PREKLAD: {len(tr)} dvojic vět z překladového benchmarku, kde se vaše kódy liší (E = anglické vydání vydavatele, T = strojový překlad originálu).",
              "  spolecny_kod: S = stejný význam i síla · W = překlad slabší · X = překlad silnější · M = význam se liší jinak · D = nelze posoudit (špatně spárováno, úlomek).",
              "  proc_neshoda: A = liší se anglické vydání vydavatele, ne překlad (vydavatel text upravil) · B = skutečný posun nebo chyba překladu · C = špatně spárované věty nebo úlomek · D = jen stylistický rozdíl · E = jiné.",
              "",
              "Původní slepé štítky zůstávají uložené beze změny. Společná rozhodnutí se ukládají zvlášť jako dohodnutá, ne jako nezávislá.",
              "Vyplňujte jen žluté sloupce. Uložte pod stejným názvem."]:
        w.append([t])
    w.column_dimensions["A"].width = 160; w["A1"].font = Font(bold=True, size=13)
    for c in w["A"]: c.alignment = Alignment(wrap_text=True)
    sheet(wb, "RELEVANCE", ["typ_neshody", "radek_v_puvodnim_souboru", "unit_id", "project", "kind", "year", "page", "odstavec (věta označena »…«)", "VĚTA", "MB", "DS", "spolecny_stitek", "proc_neshoda", "pravidlo / poznámka", "upozornění"],
          rel, [16, 15, 30, 8, 13, 7, 6, 85, 55, 8, 6, 11, 11, 45, 22], {"L": "R,N,U", "M": "A,B,C,D", "N": ""})
    sheet(wb, "PREKLAD", ["typ_neshody", "#", "dokument", "E: anglické vydání vydavatele", "T: strojový překlad originálu", "MB", "DS", "spolecny_kod", "proc_neshoda", "poznámka"],
          tr, [14, 6, 26, 70, 70, 6, 6, 11, 11, 45], {"H": "S,W,X,M,D", "I": "A,B,C,D,E", "J": ""})
    wb.save(a.out)
    import collections
    print(a.out, "| relevance", len(rel), dict(collections.Counter(r[0] for r in rel)), "| preklad", len(tr), dict(collections.Counter(r[0] for r in tr)))


if __name__ == "__main__": main()
