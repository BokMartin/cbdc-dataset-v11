#!/usr/bin/env python3
"""Verification workbooks, second version (26 Nov 2026), after audit A5 (docs/audits/INDEPENDENT_AUDIT_2026-11-26.md,
finding 5 and items 21, 22). The workbooks of 24 Nov (build_verification_workbook.py) stay as they are, as the record.

What changes against 24 Nov, and why:
  - Two passes. Pass 1 (PRUCHOD1) shows, for every key to verify, the question and the places to read (document code and
    page), but no value, no status, no model name and no quote. The author writes down their own value, both statuses,
    basis, the layer of the document and the supporting place, or "nedostatecna opora". Pass 1 is then locked
    (--lock-pass1: its SHA-256 goes to data/index/VERIFY_PASS1_LOCK.csv). Only then is pass 2 built for that author
    (--pass 2 refuses otherwise): one row per model and key with the model's value, statuses, basis and quote, and the
    author's pass-1 answer beside it; the author records agreement and the reason for every change. This reduces the
    anchoring on model output that astra calls structurally likely (item 21).
  - Random order. Keys are shuffled with a fixed seed (--seed, recorded in the items file), not grouped by project.
  - Negative searches. A key whose only model value is F3 none_stated has no place to read; it goes to the sheet HLEDANI
    with the drawn empty keys, as a search form (documents and pages searched, minutes, what was found).
  - Rows of the re-run of 24 Nov (the KZ supplement) are part of the cells read in, not a separate file.
  - NO and UK are added (ADR-017 names only 14 projects; audit item 22). Their rows carry the flag "vyvojovy projekt"
    because both authors saw development output for them. Their empty keys are not drawn (no rule yet; agenda ADR-018).
  - In pass 2 a missing quote is an empty cell with the reason in its own column, never a reason code in the quote
    column (item 29), and statuses are per model, not joined across models.
  - The ADR-017 draw of empty keys is unchanged: the 10 empty keys with the lowest committed rank
    (data/index/VERIFY_EMPTY_RANK_2026-11-24.csv), computed on the empty keys of the cells read in.

Input: the reducer output of each model (scripts/extraction/reduce_v122.py, the version of 26 Nov), kept outside the
repository. Repository output: data/index/VERIFY_ITEMS_<date>.csv (keys, order, places; no value, no quote) and
data/index/VERIFY_WORKBOOKS_<date>.csv (hashes). Workbooks go to --out.

usage: build_verification_workbook_v2.py --cells claude=<json> sol62=<json> deepseek=<json> --out <dir> --date 2026-11-26 --seed 20261126
       build_verification_workbook_v2.py --lock-pass1 --coder MB --xlsx <filled pass-1 workbook> --date 2026-11-26
       build_verification_workbook_v2.py --pass 2 --coder MB --xlsx <filled pass-1 workbook> --cells ... --out <dir> --date 2026-11-26 --seed 20261126
"""
import argparse
import csv
import datetime
import hashlib
import json
import os
import random
import sys

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.worksheet.datavalidation import DataValidation

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
from build_blind_cell_workbook import BLIND, CELLS, CODERS, DEVELOPMENT, PRAVIDLA, QUESTION, VALUES, documents  # noqa: E402
from build_verification_workbook import CELL_GROUPS, MODEL_NAMES, N_EMPTY, RANK, finder_pages  # noqa: E402

PROJECTS = tuple(sorted(BLIND + DEVELOPMENT))
LOCK = os.path.join(ROOT, "data", "index", "VERIFY_PASS1_LOCK.csv")
LOCK_FIELDS = ["coder", "locked_utc", "file", "sha256", "rows_answered", "rows_total"]
STATUS_D = ("endorsed", "considered", "rejected", "superseded", "unclear")
STATUS_I = ("operational", "tested", "untested_or_unreported")
BASIS = ("architectural", "cryptographic", "legal", "policy", "n/d")
LAYER = ("official_cb", "official_government", "legislation", "staff_research", "joint_research", "other")
GREY = PatternFill("solid", fgColor="DDDDDD")
YELLOW = PatternFill("solid", fgColor="FFF2CC")
WRAP = Alignment(wrap_text=True, vertical="top")


def _sha(path):
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def _norm(q):
    return " ".join((q or "").split())


def keys(cells_by_model, docs, seed):
    """(to_read, to_search, drawn, n_empty14): keys with a located model value; keys whose only value is an unlocated
    F3 none_stated; the ADR-017 draw of empty keys of the 14 projects; the number of empty keys there."""
    code = {d["doc_key"]: d["code"] for d in docs}
    read, search, empty = [], [], []
    for p in PROJECTS:
        for c in CELLS:
            got = {m: (((data.get(p) or {}).get("cells") or {}).get(c) or {}) for m, data in cells_by_model.items()}
            valued = {m: x for m, x in got.items() if x.get("value")}
            if not valued:
                if p in BLIND:
                    empty.append((p, c))
                continue
            places = sorted({(code.get(x.get("document_id"), x.get("document_id")), int(x["page_index"]))
                             for x in valued.values() if x.get("document_id") and x.get("page_index") not in (None, "")})
            k = {"key": f"{p}-{c}", "project_id": p, "cell": c, "places": places, "models": valued,
                 "development": p in DEVELOPMENT}
            (read if places else search).append(k)
    with open(os.path.join(ROOT, RANK), newline="", encoding="utf-8") as fh:
        rank = {(r["project_id"], r["cell"]): int(r["rank"]) for r in csv.DictReader(fh)}
    drawn = sorted(empty, key=lambda k: rank[k])[:N_EMPTY]
    rng = random.Random(seed)
    rng.shuffle(read)
    for i, k in enumerate(read, 1):
        k["order"] = i
    return read, search, drawn, len(empty)


NAVOD1 = [
    "Ověření buněk F, PRŮCHOD 1, autor {coder} (sešit vytvořen {date}). Vyplňujete sami, bez druhého autora (ADR-017).",
    "V tomto průchodu NEVIDÍTE, co našly modely. Vidíte jen otázku a místa, kde modely něco našly (kód dokumentu a stranu). Přečtěte to místo v kontextu (celý odstavec nebo stranu, klidně i okolí) a zapište, co z něj plyne podle vás.",
    "LIST PRUCHOD1 ({n_read} buněk, náhodné pořadí): pro každou buňku vyplňte žluté sloupce:",
    "  hodnota: hodnota buňky podle zdroje, nebo 'nedostatecna_opora', když místo nic určitého neříká.",
    "  decision_status a implementation_status: jak je věc rozhodnutá a zavedená (considered vs endorsed, tested vs operational).",
    "  basis: proč to platí (architectural, cryptographic, legal, policy, n/d).",
    "  vrstva dokumentu: kdo text vydal a s jakou pravomocí (centrální banka, vláda, zákon, výzkum zaměstnanců, společná výzkumná zpráva, jiné).",
    "  oporné místo: kód dokumentu a strana, kde to stojí (může být jiné než nabízené), a pár slov vlastními slovy.",
    "  minut: kolik času buňka zabrala.",
    "Řádky s příznakem 'vyvojovy projekt' (NO a UK): tyto projekty jste viděli ve vývojovém kole; ověřujete je stejně, výsledek se vykazuje zvlášť.",
    "LIST HLEDANI ({n_search} buněk): u těchto buněk není místo, kam se podívat (prázdné buňky vybrané náhodně podle ADR-017 a buňky, kde by odpověď plynula jen z úplného prohledání). Projděte dokumenty projektu (vyhledávač stran ve sloupci 'kde hledat'), zapište, co jste prošli, kolik minut, a co jste našli (hodnotu s místem), nebo 'nenalezeno'.",
    "Až budete hotovi, sešit uložte a pošlete. Před vrácením se s druhým autorem nedomlouvejte. Pak se sešit zamkne (jeho otisk se uloží do repozitáře) a dostanete PRŮCHOD 2 s hodnotami modelů.",
    "Pravidla buněk jsou v listu PRAVIDLA, dokumenty s cestou k PDF v listu DOKUMENTY.",
]

NAVOD2 = [
    "Ověření buněk F, PRŮCHOD 2, autor {coder} (sešit vytvořen {date}). Průchod 1 je zamčený (otisk {sha1}).",
    "Teď vidíte, co našly jednotlivé modely: jeden řádek = jeden model a jedna buňka, s hodnotou, statusy a citátem. Vedle je vaše odpověď z průchodu 1.",
    "Vyplňte žluté sloupce: nese (ano / castecne / ne: plyne hodnota modelu z citátu?), status sedí (ano / ne), konečná hodnota a statusy podle vás, a když se liší od průchodu 1, důvod změny.",
    "Změna oproti průchodu 1 je v pořádku, jen ji zdůvodněte (např. 'model ukázal místo, které jsem přehlédl').",
]


def _header(ws, cols, widths):
    for i, name in enumerate(cols, 1):
        x = ws.cell(1, i, name)
        x.font = Font(bold=True)
        x.fill = GREY
        x.alignment = WRAP
        ws.column_dimensions[x.column_letter].width = widths.get(name, 14)
    ws.freeze_panes = "A2"


def _dv(ws, cols, name, n, vals):
    if n < 1:
        return
    col = ws.cell(1, cols.index(name) + 1).column_letter
    dv = DataValidation(type="list", formula1='"' + ",".join(vals) + '"', allow_blank=True)
    ws.add_data_validation(dv)
    dv.add(f"{col}2:{col}{n + 1}")


def _fill(ws, i, vals, ncols):
    for c, v in enumerate(vals, 1):
        x = ws.cell(i, c, v)
        x.alignment = WRAP
        x.fill = GREY
    for c in range(len(vals) + 1, ncols + 1):
        ws.cell(i, c).fill = YELLOW


def _common(wb, docs):
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


P1COLS = ["poradi", "key", "project_id", "cell", "vyvojovy projekt", "otazka", "kde cist (kód: strana)",
          "hodnota", "decision_status", "implementation_status", "basis", "vrstva dokumentu", "oporne misto (kód: strana)",
          "vlastnimi slovy", "minut", "poznamka"]
SCOLS = ["key", "project_id", "cell", "proc tady", "otazka", "kde hledat (kód: strany)", "proslo (dokumenty a strany)",
         "minut", "nalezeno", "hodnota", "decision_status", "implementation_status", "oporne misto (kód: strana)",
         "vlastnimi slovy", "poznamka"]


def pass1(path, coder, date, read, search, drawn, docs, fpages):
    wb = Workbook()
    ws = wb.active
    ws.title = "NAVOD"
    ws.column_dimensions["A"].width = 150
    n_search = len(search) + len(drawn)
    for i, line in enumerate(NAVOD1, 1):
        ws.cell(i, 1, line.format(coder=coder, date=date, n_read=len(read), n_search=n_search)).alignment = WRAP
    ws.cell(1, 1).font = Font(bold=True)
    p1 = wb.create_sheet("PRUCHOD1")
    _header(p1, P1COLS, {"otazka": 40, "kde cist (kód: strana)": 26, "vlastnimi slovy": 40, "poznamka": 30,
                         "oporne misto (kód: strana)": 18})
    for i, k in enumerate(read, 2):
        _fill(p1, i, [k["order"], k["key"], k["project_id"], k["cell"], "ano" if k["development"] else "", QUESTION[k["cell"]],
                      "; ".join(f"{c}: {pg}" for c, pg in k["places"])], len(P1COLS))
    n = len(read)
    for name, vals in (("hodnota", tuple(VALUES.get("F1")) + ("via_psp", "via_cb", "via_both", "none_stated", "nedostatecna_opora")),
                       ("decision_status", STATUS_D), ("implementation_status", STATUS_I), ("basis", BASIS),
                       ("vrstva dokumentu", LAYER)):
        _dv(p1, P1COLS, name, n, vals)
    se = wb.create_sheet("HLEDANI")
    _header(se, SCOLS, {"otazka": 40, "kde hledat (kód: strany)": 50, "proc tady": 30, "proslo (dokumenty a strany)": 30,
                        "vlastnimi slovy": 40, "poznamka": 30})
    # one neutral reason for both kinds, so that the sheet does not tell which keys a model answered with none_stated
    rows = [(k["key"], k["project_id"], k["cell"]) for k in search] + [(f"{p}-{c}", p, c) for p, c in drawn]
    rows = [r + ("žádné místo ke čtení: prohledejte dokumenty projektu",) for r in sorted(rows)]
    for i, (key, p, c, why) in enumerate(rows, 2):
        where = "; ".join(s for g in CELL_GROUPS[c] for s in fpages.get((p, g), []))
        _fill(se, i, [key, p, c, why, QUESTION[c], where or ("vyhledávač stran se pro NO a UK nedělal" if p in DEVELOPMENT else "vyhledávač nic nenašel")], len(SCOLS))
    _dv(se, SCOLS, "nalezeno", len(rows), ("nalezeno", "nenalezeno"))
    _common(wb, docs)
    wb.save(path)


P2COLS = ["poradi", "key", "project_id", "cell", "vyvojovy projekt", "model", "hodnota modelu", "decision_status modelu",
          "implementation_status modelu", "evidence_state", "basis modelu", "doc_code", "page_index", "quote", "bez citatu proc",
          "vase hodnota (pruchod 1)", "vase statusy (pruchod 1)", "nese", "status sedi", "konecna hodnota", "konecny decision_status",
          "konecny implementation_status", "duvod zmeny proti pruchodu 1", "poznamka"]


def read_pass1(xlsx):
    wb = load_workbook(xlsx, read_only=True)
    rows = list(wb["PRUCHOD1"].iter_rows(values_only=True))
    head = list(rows[0])
    return {r[head.index("key")]: dict(zip(head, r)) for r in rows[1:] if r and r[head.index("key")]}


def pass2(path, coder, date, read, docs, answers, sha1):
    code = {d["doc_key"]: d["code"] for d in docs}
    wb = Workbook()
    ws = wb.active
    ws.title = "NAVOD"
    ws.column_dimensions["A"].width = 150
    for i, line in enumerate(NAVOD2, 1):
        ws.cell(i, 1, line.format(coder=coder, date=date, sha1=sha1[:16])).alignment = WRAP
    ws.cell(1, 1).font = Font(bold=True)
    p2 = wb.create_sheet("PRUCHOD2")
    _header(p2, P2COLS, {"quote": 70, "duvod zmeny proti pruchodu 1": 35, "poznamka": 30})
    i = 2
    for k in read:
        a = answers.get(k["key"]) or {}
        for m in sorted(k["models"]):
            x = k["models"][m]
            q = _norm(x.get("quote"))
            _fill(p2, i, [k["order"], k["key"], k["project_id"], k["cell"], "ano" if k["development"] else "", MODEL_NAMES[m],
                          x.get("value"), x.get("decision_status"), x.get("implementation_status"), x.get("evidence_state"),
                          x.get("basis"), code.get(x.get("document_id"), x.get("document_id")), x.get("page_index"), q or None,
                          None if q else (x.get("rule") or x.get("derivation") or "bez citátu"),
                          a.get("hodnota"), " / ".join(str(a.get(f) or "-") for f in ("decision_status", "implementation_status"))],
                  len(P2COLS))
            i += 1
    _dv(p2, P2COLS, "nese", i - 2, ("ano", "castecne", "ne"))
    _dv(p2, P2COLS, "status sedi", i - 2, ("ano", "ne"))
    _common(wb, docs)
    wb.save(path)


def locked(coder):
    if not os.path.exists(LOCK):
        return None
    with open(LOCK, newline="", encoding="utf-8") as fh:
        rows = [r for r in csv.DictReader(fh) if r["coder"] == coder]
    return rows[-1] if rows else None


def lock_pass1(coder, xlsx):
    if locked(coder):
        raise SystemExit(f"{coder}: pass 1 is already locked ({locked(coder)['sha256'][:16]})")
    ans = read_pass1(xlsx)
    done = sum(bool(r.get("hodnota")) for r in ans.values())
    row = {"coder": coder, "locked_utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
           "file": os.path.basename(xlsx), "sha256": _sha(xlsx), "rows_answered": done, "rows_total": len(ans)}
    new = not os.path.exists(LOCK)
    with open(LOCK, "a", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, LOCK_FIELDS)
        if new:
            w.writeheader()
        w.writerow(row)
    print(f"{coder}: pass 1 locked, {done} of {len(ans)} rows answered, sha256 {row['sha256'][:16]} -> {os.path.relpath(LOCK, ROOT)}")


def load_cells(pairs):
    cells = {}
    for kv in pairs:
        m, path = kv.split("=", 1)
        if m not in MODEL_NAMES:
            raise SystemExit(f"unknown model {m}")
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
        cells[m] = data.get("projects", data)
    if set(cells) != set(MODEL_NAMES):
        raise SystemExit("need the cells of all three models")
    return cells


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cells", nargs=3)
    ap.add_argument("--out")
    ap.add_argument("--date", required=True)
    ap.add_argument("--seed", type=int, default=20261126)
    ap.add_argument("--pass", dest="pass_", type=int, default=1, choices=(1, 2))
    ap.add_argument("--coder", choices=CODERS)
    ap.add_argument("--xlsx")
    ap.add_argument("--lock-pass1", action="store_true")
    a = ap.parse_args()
    if a.lock_pass1:
        if not (a.coder and a.xlsx):
            raise SystemExit("--lock-pass1 needs --coder and --xlsx")
        return lock_pass1(a.coder, a.xlsx)
    if not (a.cells and a.out):
        raise SystemExit("--cells and --out are needed")
    out = os.path.abspath(a.out)
    if out.startswith(ROOT + os.sep):
        raise SystemExit("refused: the workbooks hold source quotes and stay outside the repository")
    cells = load_cells(a.cells)
    docs = documents(PROJECTS)
    read, search, drawn, n_empty = keys(cells, docs, a.seed)
    os.makedirs(out, exist_ok=True)
    if a.pass_ == 2:
        if not (a.coder and a.xlsx):
            raise SystemExit("--pass 2 needs --coder and the filled pass-1 workbook (--xlsx)")
        lk = locked(a.coder)
        if not lk:
            raise SystemExit(f"{a.coder}: pass 1 is not locked; run --lock-pass1 first")
        if _sha(a.xlsx) != lk["sha256"]:
            raise SystemExit(f"{a.xlsx} is not the locked pass-1 workbook of {a.coder}")
        path = os.path.join(out, f"VERIFY_CELLS_{a.coder}_PASS2_{a.date}.xlsx")
        pass2(path, a.coder, a.date, read, docs, read_pass1(a.xlsx), lk["sha256"])
        print(f"{a.coder}: pass 2 -> {path}")
        return
    fpages = finder_pages(docs)
    idx = os.path.join(ROOT, "data", "index")
    with open(os.path.join(idx, f"VERIFY_ITEMS_{a.date}.csv"), "w", newline="", encoding="utf-8") as fh:
        # no value and no quote: the cell values stay out of the repository until verification is locked
        w = csv.DictWriter(fh, ["kind", "order", "key", "project_id", "cell", "development", "models", "places",
                                "inclusion_probability", "seed"])
        w.writeheader()
        for k in read:
            w.writerow({"kind": "read", "order": k["order"], "key": k["key"], "project_id": k["project_id"], "cell": k["cell"],
                        "development": int(k["development"]), "models": " ".join(sorted(k["models"])),
                        "places": "; ".join(f"{c}:{pg}" for c, pg in k["places"]), "inclusion_probability": 1, "seed": a.seed})
        for k in search:
            w.writerow({"kind": "search_negative", "key": k["key"], "project_id": k["project_id"], "cell": k["cell"],
                        "development": int(k["development"]), "models": " ".join(sorted(k["models"])), "inclusion_probability": 1})
        for p, c in drawn:
            w.writerow({"kind": "empty_key", "key": f"{p}-{c}", "project_id": p, "cell": c, "development": 0,
                        "inclusion_probability": round(N_EMPTY / n_empty, 4)})
    rec = []
    for coder in CODERS:
        path = os.path.join(out, f"VERIFY_CELLS_{coder}_PASS1_{a.date}.xlsx")
        pass1(path, coder, a.date, read, search, drawn, docs, fpages)
        rec.append((coder, os.path.basename(path), _sha(path)))
    with open(os.path.join(idx, f"VERIFY_WORKBOOKS_{a.date}.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["coder", "file", "sha256"])
        w.writerows(rec)
    dev = sum(k["development"] for k in read)
    print(f"{len(read)} keys to read ({dev} of NO and UK), {len(search)} negative-search keys, {len(drawn)} of {n_empty} empty keys"
          f" drawn; seed {a.seed} -> {out}")


if __name__ == "__main__":
    main()
