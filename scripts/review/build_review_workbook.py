#!/usr/bin/env python3
"""Review and reference workbooks (ADR-001 E17 "parameterised review builder", E6 "blank reference workbook").

Two modes:
  review     development verification: one row per cell, model fills side by side, agreement flag, verdict columns, clickable
             PDF page links (Dropbox path from --pdf-root), DEFINITIONS sheet from the contract. Development material only.
  reference  BLANK blind reference workbook for a human coder: one row per cell, contract definitions, NO model columns, no
             "agree_<model>" verdict; the coder fills value / evidence_state / statuses / locator / quote / qualifiers from the
             PDFs. Used for the blind set and for the source-first F1(/F7) coding of every analytic project (E5).

usage:
  build_review_workbook.py review    --jur NO --name Norway --docs llm_fill/NO/DOCS.csv --registry REGISTRY.csv --contract C.md \
      --schema schema/cells_v1_1.json --fill opus=FILL_a.csv [--fill gpt=FILL_b.csv] --pdf-root "C:/.../dizertace v 11/" --out OUT.xlsx
  build_review_workbook.py reference --jur CL --name Chile  --docs texts/CL/DOCS.csv --registry REGISTRY.csv --contract C.md \
      --schema schema/cells_v12_DRAFT.json --coder MB --pdf-root ... --out CL_reference_MB.xlsx [--cells "F1 CB_LINK_ONLINE,F7 LOW_ID_ROUTE"]
No path is hard-coded; every input is an argument.
"""
import argparse, json, os, re
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter
from urllib.parse import quote

WRAP = Alignment(wrap_text=True, vertical="top"); BLUE = Font(color="0563C1", underline="single")


def load_defs(contract_text):
    defs = {}
    for line in contract_text.split("\n"):
        mm = re.match(r"\| \*\*(F\d+)[^|]*\| (.*?) \| (.*?) \| (.*?) \|(?: (.*?) \|)?$", line)
        if mm: defs[mm.group(1)] = tuple(x or "" for x in mm.groups()[1:])
    m = re.search(r"(## 7\. Derivation rules.*?)(?=\n## 8\.)", contract_text, re.S) or re.search(r"(## 6\. Aggregation and derivation rules.*?)(?=\n## 8\.)", contract_text, re.S)
    return defs, (m.group(1).strip() if m else "")


def defn(cell, defs):
    d = defs.get(cell.split(" ")[0].split(".")[0])
    if not d: return ""
    q, v, a, b = (list(d) + ["", ""])[:4]
    if cell.startswith("F11 ") and "primary" not in cell: q = f"Does the institution state '{cell[4:]}' as an objective (with a quote)? Not documented ≠ absence of motive."
    if cell == "F11 primary_status": q = "Did the institution explicitly rank one objective as main?"
    if cell == "F11 primary_objectives": q = "Which objective(s) are ranked as main — only when the ranking is documented (ranked original statements)."
    if cell.startswith("F12 "): q = f"[{cell[4:]}] " + q
    return f"{q}\nVALUES: {v}\nQUALIFIERS/TRAPS: {a}\n{b}".strip()


def make_href(registry, pdf_root):
    R = pd.read_csv(registry, dtype=str, keep_default_na=False).set_index("doc_id")
    def href(doc_id):
        if doc_id not in R.index or not pdf_root: return ""
        r = R.loc[doc_id]; layer = "core_v1" if r.get("core_v1", "") else "core_v2"; core = r.get("core_v1", "") or r.get("core_v2", "")
        return "file:///" + quote(pdf_root + f"{layer}/{core}/{r.year}/{r.fname}", safe="/:")
    return href


def style(ws, widths, header_cols):
    for c, w in enumerate(widths, 1): ws.column_dimensions[get_column_letter(c)].width = w
    for c in range(1, header_cols + 1): ws.cell(1, c).font = Font(bold=True); ws.cell(1, c).fill = PatternFill("solid", fgColor="DDDDDD")
    for row in ws.iter_rows():
        for c in row: c.alignment = WRAP


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("mode", choices=["review", "reference"])
    for k in ("jur", "name", "docs", "registry", "contract", "schema", "out"): ap.add_argument("--" + k, required=True)
    ap.add_argument("--fill", action="append", default=[]); ap.add_argument("--pdf-root", default=""); ap.add_argument("--coder", default="")
    ap.add_argument("--cells", default=""); ap.add_argument("--notes", action="append", default=[])
    a = ap.parse_args()
    schema = json.load(open(a.schema)); con = open(a.contract, encoding="utf-8").read(); defs, rules = load_defs(con)
    docs = pd.read_csv(a.docs, dtype=str, keep_default_na=False); href = make_href(a.registry, a.pdf_root)
    cells = a.cells.split(",") if a.cells else list(schema["cells"])
    def page_href(doc_no, page):
        try: r = docs[docs.doc.astype(int) == int(float(doc_no))].iloc[0]
        except Exception: return ""
        try: pg = int(float(page))
        except Exception: pg = None
        u = href(r.doc_id); return (u + (f"#page={pg}" if pg else "")) if u else ""
    wb = Workbook(); ws = wb.active; ws.title = "README"
    status_cols = ["decision_status", "implementation_status"] if "decision_status" in schema else ["claim_status"]
    if a.mode == "review":
        fills = {}
        for f in a.fill:
            k, p = f.split("=", 1); F = pd.read_csv(p, dtype=str, keep_default_na=False)
            if "quote_verified" not in F.columns: F["quote_verified"] = ""
            fills[k] = F
        for t in [f"LLM-FILLED PROFILE — {a.name} ({a.jur}) — human verification (DEVELOPMENT coding; instrument {schema.get('instrument')}).",
                  f"Models: {', '.join(fills)}. Open the cited page (links), check quote and justification, fill YOUR_VERDICT (agree_<model> / own value) and NOTE; write CONTRACT: ... when the definition is the problem.",
                  "Page cells open the PDF at the cited PDF page index (#page=), where the viewer supports it. Jurisdictions reviewed this way are development cases and are excluded from the blind set (EXPOSURE_LEDGER)."]: ws.append([t])
    else:
        for t in [f"BLIND REFERENCE CODING — {a.name} ({a.jur}) — coder {a.coder or '____'} — instrument {schema.get('instrument')}.",
                  "Code every cell from the PDFs only. Do not open any model output for this project. Fill value, evidence_state, statuses, basis, document #, PDF page, verbatim quote, qualifiers, derivation (explicit/inferred + premises), note. Absence of mention = unknown with a reason code; a 'no' needs the same evidence as a 'yes'.",
                  "Lock this workbook (save as final, record the SHA-256 in the exposure ledger) BEFORE comparing with the other coder or any model. Adjudication happens in a separate file.",
                  "Page links in DOCS open the PDF. The keyword finder, if supplied, lists page references only, never values."]: ws.append([t])
    ws.column_dimensions["A"].width = 160
    for row in ws.iter_rows():
        for c in row: c.alignment = WRAP
    d = wb.create_sheet("DOCS"); d.append(["#", "year", "core", "kind", "lang", "title", "OPEN", "doc_id"])
    for i, r in enumerate(docs.itertuples(), 1):
        u = href(r.doc_id); d.append([int(r.doc), r.year, getattr(r, "core", ""), getattr(r, "kind", ""), getattr(r, "lang", ""), r.title, f'=HYPERLINK("{u}","open")' if u else "", r.doc_id])
        if u: d.cell(i + 1, 7).font = BLUE
    style(d, [4, 6, 11, 14, 6, 80, 8, 40], 8)
    m = wb.create_sheet("CODING" if a.mode == "reference" else "REVIEW")
    if a.mode == "review":
        per = ["value", "evidence_state"] + status_cols + ["derivation", "doc", "page" if "page" in next(iter(fills.values())).columns else "page_index", "quote", "quote_verified", "justification", "counter_evidence", "confidence"]
        hdr = ["cell", "DEFINITION", "MODELS AGREE?"] + [f"{k}: {f}" for k in fills for f in per] + ["YOUR_VERDICT (agree_<model> / value)", "YOUR evidence_state", "YOUR status", "NOTE"]
        m.append(hdr)
        for F in fills.values():
            for c in F.cell:
                if c not in cells: cells.append(c)
        for ci, cell in enumerate(cells, 2):
            row = [cell]; vals = []
            for k, F in fills.items():
                r = F[F.cell == cell]; r = r.iloc[0] if len(r) else pd.Series({f: "" for f in per})
                vals.append(tuple(str(r.get(f, "")).strip().lower() for f in ["value", "evidence_state"] + status_cols)); row += [r.get(f, "") for f in per]
            agree = "yes" if len(set(vals)) == 1 else ("value only" if len(set(v[0] for v in vals)) == 1 else "NO")
            row.insert(1, agree); row.insert(1, defn(cell, defs)); row += ["", "", "", ""]; m.append(row)
            if agree != "yes": m.cell(ci, 3).fill = PatternFill("solid", fgColor="FFC7CE" if agree == "NO" else "FFEB9C")
            for ki in range(len(fills)):
                col = 4 + ki * len(per) + per.index("doc") + 1; doc_no = m.cell(ci, col - 1).value; pg = m.cell(ci, col).value
                u = page_href(doc_no, pg) if str(doc_no).strip() not in ("", "n/d", "nan") else ""
                if u: m.cell(ci, col).value = f'=HYPERLINK("{u}","p.{pg}")'; m.cell(ci, col).font = BLUE
        style(m, [30, 55, 10] + [12, 12] + [11] * len(status_cols) + [10, 5, 7, 55, 11, 60, 45, 9] * 1 + [12] * (len(per) * (len(fills) - 1)) + [22, 14, 12, 50], len(hdr)); m.freeze_panes = "D2"
    else:
        hdr = ["cell", "DEFINITION", "value", "evidence_state"] + status_cols + ["basis", "derivation (explicit / inferred: premises)", "doc #", "PDF page", "quote (verbatim)", "actor", "transaction_scope", "limits", "modality", "unknown_reason", "note"]
        m.append(hdr)
        for cell in cells: m.append([cell, defn(cell, defs)] + [""] * (len(hdr) - 2))
        style(m, [30, 60, 12, 13] + [14] * len(status_cols) + [12, 28, 6, 8, 60, 14, 16, 14, 16, 16, 40], len(hdr)); m.freeze_panes = "C2"
    v = wb.create_sheet("VALUES"); v.append(["cell", "allowed values"])
    for c in cells: v.append([c, ", ".join(schema["values"].get(c) or ["free text"])])
    for k in ("evidence_state", "decision_status", "implementation_status", "claim_status", "basis", "derivation", "unknown_reason"):
        if k in schema: v.append([k, ", ".join(x for x in schema[k] if x)])
    style(v, [34, 90], 2)
    dd = wb.create_sheet("DEFINITIONS"); dd.append(["feature", "question", "values", "qualifiers / traps", ""])
    for f, t in defs.items(): dd.append([f] + list(t)[:4])
    dd.append([]); dd.append(["DERIVATION RULES"])
    for line in rules.split("\n"):
        if line.strip(): dd.append([line])
    style(dd, [28, 70, 30, 70, 30], 5)
    for n in a.notes:
        k, p = n.split("=", 1)
        if os.path.exists(p):
            s = wb.create_sheet(f"NOTES_{k}"[:31]); s.column_dimensions["A"].width = 160
            for line in open(p, encoding="utf-8"): s.append([line.rstrip("\n")])
    wb.save(a.out); print(a.out, len(cells), "cells", a.mode)


if __name__ == "__main__": main()
