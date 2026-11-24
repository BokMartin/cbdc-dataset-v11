#!/usr/bin/env python3
"""Verification workbooks for the 14 blind core projects (ADR-017, MB 24 Nov 2026).

Input: the reducer output of each of the three models (`scripts/extraction/reduce_v122.py --out`, one JSON per model, kept
OUTSIDE the repository because it carries source quotes). For every project-cell key of the 14 projects and the eight cells
F1, F2, F3, F4, F7, F8, F9, F10:
  - a key where at least one model gives a value is a verification item; every distinct (value, document, page, quote) of
    the models is one row, with the models that gave it and their status;
  - of the keys where no model gives a value, the 10 with the lowest rank in data/index/VERIFY_EMPTY_RANK_2026-11-24.csv are
    the empty-key check (ADR-017 point 2), with the page-finder pages of the cell (data/index/BLIND_CELL_FINDER_2026-11-24.csv)
    as a starting point; their inclusion probability is 10 / number of empty keys.
One workbook per author (MB, DS), identical except for the name; the authors fill them alone.

Repository output: data/index/VERIFY_ITEMS_<date>.csv (keys, row ids, models, document, page; no value, no quote) and the workbook
hashes. The workbooks go to --out.

usage: build_verification_workbook.py --cells claude=<json> sol62=<json> deepseek=<json> --out <dir> --date 2026-11-24
"""
import argparse
import csv
import hashlib
import json
import os
import sys

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.worksheet.datavalidation import DataValidation

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
from build_blind_cell_workbook import BLIND, CELLS, CODERS, QUESTION, PRAVIDLA, VALUES, FINDER, documents  # noqa: E402

RANK = "data/index/VERIFY_EMPTY_RANK_2026-11-24.csv"
FINDER_FILE = "data/index/BLIND_CELL_FINDER_2026-11-24.csv"
N_EMPTY = 10
CELL_GROUPS = {"F1": ("PRIV",), "F2": ("PRIV",), "F3": ("LAW",), "F4": ("OFF",), "F7": ("IDENT",), "F8": ("IDENT",),
               "F9": ("PRIV", "LAW"), "F10": ("PROG",)}
MODEL_NAMES = {"claude": "claude-opus-5-5", "sol62": "gpt-6.2-sol", "deepseek": "deepseek-v4-pro"}
GREY = PatternFill("solid", fgColor="DDDDDD")
YELLOW = PatternFill("solid", fgColor="FFF2CC")
WRAP = Alignment(wrap_text=True, vertical="top")
assert FINDER


def _sha(path):
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def _norm(q):
    return " ".join((q or "").split())


def items(cells_by_model, docs):
    """Rows to verify and the drawn empty keys."""
    code = {d["id"]: d["code"] for d in docs}
    code.update({d["doc_key"]: d["code"] for d in docs})
    rows, empty = [], []
    for p in BLIND:
        for c in CELLS:
            got = {}
            for m, data in cells_by_model.items():
                x = ((data.get(p) or {}).get("cells") or {}).get(c) or {}
                if not x.get("value"):
                    continue
                k = (x["value"], x.get("document_id", ""), x.get("page_index", ""), _norm(x.get("quote")))
                got.setdefault(k, []).append((m, x))
            if not got:
                empty.append((p, c))
                continue
            for j, (k, ms) in enumerate(sorted(got.items(), key=lambda kv: (-len(kv[1]), kv[0])), 1):
                v, doc, page, quote = k
                x = ms[0][1]
                rows.append({
                    "row_id": f"{p}-{c}-{j}", "project_id": p, "cell": c, "value": v,
                    "models": " ".join(m for m, _ in ms), "n_models": len(ms),
                    "all_values": " / ".join(sorted({((cells_by_model[m].get(p) or {}).get("cells") or {}).get(c, {}).get("value") or "-" for m in cells_by_model})),
                    "decision_status": " / ".join(sorted({y.get("decision_status", "") or "-" for _, y in ms})),
                    "implementation_status": " / ".join(sorted({y.get("implementation_status", "") or "-" for _, y in ms})),
                    "evidence_state": " / ".join(sorted({y.get("evidence_state", "") or "-" for _, y in ms})),
                    "basis": " / ".join(sorted({y.get("basis", "") or "-" for _, y in ms})),
                    "derivation": x.get("derivation", ""), "rule": x.get("rule", ""),
                    "document_id": doc, "doc_code": code.get(doc, doc), "page_index": page, "quote": quote,
                })
    with open(os.path.join(ROOT, RANK), newline="", encoding="utf-8") as fh:
        rank = {(r["project_id"], r["cell"]): int(r["rank"]) for r in csv.DictReader(fh)}
    drawn = sorted(empty, key=lambda k: rank[k])[:N_EMPTY]
    return rows, drawn, len(empty)


def finder_pages(docs):
    with open(os.path.join(ROOT, FINDER_FILE), newline="", encoding="utf-8") as fh:
        f = [r for r in csv.DictReader(fh)]
    out = {}
    for d in docs:
        if d["for_cells"] != "ano":
            continue
        for r in f:
            if r["doc_key"] == d["doc_key"] and r["pages"]:
                out.setdefault((d["project"], r["group"]), []).append(f"{d['code']}: {r['pages']}")
    return out


NAVOD = [
    "Ověření buněk F, autor {coder} (sešit vytvořen {date}). Vyplňujete sami, bez druhého autora (ADR-017).",
    "CO: tři modely našly ve 14 projektech jádra hodnoty buněk s citátem. Ověřujete, zda citát závěr nese a zda sedí status. Nečtete celé dokumenty.",
    "LIST OVERIT ({n_rows} řádků): jeden řádek = jedna hodnota s citátem (stejný citát od více modelů je sloučený, ve sloupci 'modely'). Otevřete PDF na uvedené straně (cesta v listu DOKUMENTY), přečtěte citát v kontextu odstavce a vyplňte žluté sloupce.",
    "  nese = ano / castecne / ne: plyne hodnota buňky z citátu (pro běžného plátce v běžné online peněžence, v tomto projektu)?",
    "  status = ano / ne: sedí decision_status a implementation_status (considered vs endorsed, tested vs operational)? Pokud ne, napište správný do 'spravny status'.",
    "  spravna hodnota: jen když 'nese' = ne nebo castecne a ze stejného místa plyne jiná hodnota (nebo unknown).",
    "  Řádky bez citátu (F3 none_stated z prohledání): model nenašel žádnou cestu přístupu orgánů. Pokud o nějaké víte z dokumentů projektu, napište 'ne' a kde; jinak 'ano'.",
    "LIST PRAZDNE ({n_empty} buněk): u těchto náhodně vybraných buněk žádný model hodnotu nenašel. Projděte strany z vyhledávače (sloupec 'kde hledat'). Když najdete hodnotu, zapište ji s kódem dokumentu, stranou a citátem; jinak 'nenalezeno'. Stačí rozumná snaha, zapište minuty.",
    "Pravidla buněk jsou v listu PRAVIDLA (stejná jako dřív). Hodnoty ostatních modelů ke stejné buňce vidíte ve sloupci 'hodnoty modelů'.",
    "Nedomlouvejte se s druhým autorem, dokud oba sešity nevrátíte. Neshody pak projdete společně nad zdrojem.",
]


def _header(ws, cols, widths):
    for i, name in enumerate(cols, 1):
        x = ws.cell(1, i, name)
        x.font = Font(bold=True)
        x.fill = GREY
        x.alignment = WRAP
        ws.column_dimensions[x.column_letter].width = widths.get(name, 13)
    ws.freeze_panes = "A2"


def _dv(ws, col, n, vals):
    dv = DataValidation(type="list", formula1='"' + ",".join(vals) + '"', allow_blank=True)
    ws.add_data_validation(dv)
    dv.add(f"{col}2:{col}{n + 1}")


VCOLS = ["row_id", "project_id", "cell", "otazka", "value", "hodnoty modelu", "modely", "decision_status",
         "implementation_status", "evidence_state", "basis", "doc_code", "page_index", "quote",
         "nese", "status", "spravna hodnota", "spravny status", "poznamka"]
ECOLS = ["key", "project_id", "cell", "otazka", "kde hledat (kód: strany)", "nalezeno", "value", "decision_status",
         "implementation_status", "doc_code", "page_index", "quote", "minut", "poznamka"]


def workbook(path, coder, date, rows, drawn, docs, fpages):
    wb = Workbook()
    ws = wb.active
    ws.title = "NAVOD"
    ws.column_dimensions["A"].width = 150
    for i, line in enumerate(NAVOD, 1):
        ws.cell(i, 1, line.format(coder=coder, date=date, n_rows=len(rows), n_empty=len(drawn))).alignment = WRAP
    ws.cell(1, 1).font = Font(bold=True)

    ov = wb.create_sheet("OVERIT")
    _header(ov, VCOLS, {"otazka": 35, "quote": 70, "poznamka": 30, "hodnoty modelu": 16, "modely": 18})
    for i, r in enumerate(rows, 2):
        vals = [r["row_id"], r["project_id"], r["cell"], QUESTION[r["cell"]], r["value"], r["all_values"],
                " ".join(MODEL_NAMES[m] for m in r["models"].split()), r["decision_status"], r["implementation_status"],
                r["evidence_state"], r["basis"], r["doc_code"], r["page_index"],
                r["quote"] or "(bez citátu: " + (r["rule"] or "odvozeno") + ")"]
        for c, v in enumerate(vals, 1):
            x = ov.cell(i, c, v)
            x.alignment = WRAP
            x.fill = GREY
        for c in range(len(vals) + 1, len(VCOLS) + 1):
            ov.cell(i, c).fill = YELLOW
    n = len(rows)
    _dv(ov, "O", n, ("ano", "castecne", "ne"))
    _dv(ov, "P", n, ("ano", "ne"))

    pe = wb.create_sheet("PRAZDNE")
    _header(pe, ECOLS, {"otazka": 35, "kde hledat (kód: strany)": 50, "quote": 60, "poznamka": 30})
    for i, (p, c) in enumerate(drawn, 2):
        where = "; ".join(s for g in CELL_GROUPS[c] for s in fpages.get((p, g), []))
        for k, v in enumerate([f"{p}-{c}", p, c, QUESTION[c], where or "vyhledávač nic nenašel"], 1):
            x = pe.cell(i, k, v)
            x.alignment = WRAP
            x.fill = GREY
        for k in range(6, len(ECOLS) + 1):
            pe.cell(i, k).fill = YELLOW
    _dv(pe, "F", len(drawn), ("nalezeno", "nenalezeno"))

    pr = wb.create_sheet("PRAVIDLA")
    _header(pr, ["oddíl", "buňka / pole", "pravidlo"], {"oddíl": 10, "buňka / pole": 26, "pravidlo": 140})
    for i, row in enumerate(PRAVIDLA, 2):
        for c, v in enumerate(row, 1):
            pr.cell(i, c, v).alignment = WRAP

    dc = wb.create_sheet("DOKUMENTY")
    cols = ["kód", "projekt", "pro buňky", "rok", "název", "druh", "cesta textu", "PDF v Dropboxu (Dizertace all the PDFs)",
            "anglický překlad (cesta D)", "document id"]
    _header(dc, cols, {"název": 60, "PDF v Dropboxu (Dizertace all the PDFs)": 60, "anglický překlad (cesta D)": 45, "document id": 30})
    for i, d in enumerate(docs, 2):
        for c, v in enumerate([d["code"], d["project"], d["for_cells"], d["year"], d["title"], d["kind"], d["route"], d["pdf"],
                               d["translation"], d["id"]], 1):
            dc.cell(i, c, v).alignment = WRAP
    wb.save(path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cells", nargs=3, required=True, help="claude=<json> sol62=<json> deepseek=<json>")
    ap.add_argument("--out", required=True)
    ap.add_argument("--date", required=True)
    a = ap.parse_args()
    out = os.path.abspath(a.out)
    if out.startswith(ROOT + os.sep):
        raise SystemExit("refused: the workbooks hold source quotes and stay outside the repository")
    cells = {}
    for kv in a.cells:
        m, path = kv.split("=", 1)
        if m not in MODEL_NAMES:
            raise SystemExit(f"unknown model {m}")
        with open(path, encoding="utf-8") as fh:
            cells[m] = json.load(fh)["projects"]
    docs = documents()
    rows, drawn, n_empty = items(cells, docs)
    fpages = finder_pages(docs)
    os.makedirs(out, exist_ok=True)
    idx = os.path.join(ROOT, "data", "index")
    with open(os.path.join(idx, f"VERIFY_ITEMS_{a.date}.csv"), "w", newline="", encoding="utf-8") as fh:
        # no value and no quote: the cell values of the 14 projects stay out of the repository until verification is locked
        w = csv.DictWriter(fh, ["kind", "row_id", "project_id", "cell", "models", "doc_code", "page_index",
                                "inclusion_probability"])
        w.writeheader()
        for r in rows:
            w.writerow({"kind": "item", **{k: r[k] for k in ("row_id", "project_id", "cell", "models", "doc_code", "page_index")},
                        "inclusion_probability": 1})
        for p, c in drawn:
            w.writerow({"kind": "empty_key", "row_id": f"{p}-{c}", "project_id": p, "cell": c,
                        "inclusion_probability": round(N_EMPTY / n_empty, 4)})
    rec = []
    for coder in CODERS:
        path = os.path.join(out, f"VERIFY_CELLS_{coder}_{a.date}.xlsx")
        workbook(path, coder, a.date, rows, drawn, docs, fpages)
        rec.append((coder, os.path.basename(path), _sha(path)))
    with open(os.path.join(idx, f"VERIFY_WORKBOOKS_{a.date}.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["coder", "file", "sha256"])
        w.writerows(rec)
    keys = len({(r["project_id"], r["cell"]) for r in rows})
    print(f"{keys} keys with a value, {len(rows)} rows to verify; {n_empty} empty keys, {len(drawn)} drawn; -> {out}")


if __name__ == "__main__":
    main()
