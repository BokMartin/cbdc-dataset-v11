#!/usr/bin/env python3
"""List of the documents the measurement reads (English text available) and of the evidence documents it cannot read yet, by project.

Writes data/manifest/CORPUS_DOCUMENTS_<date>.csv and CORPUS_COVERAGE_<date>.csv (repository) and, with --xlsx, a workbook for the authors.
Inputs: units manifest, candidates counts, tiers, not-unitised list, project frame. No model output, no source text.

usage: build_corpus_list.py --date 2026-11-17 [--xlsx <path>]
"""
import argparse, csv, glob, os, collections
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ROUTE = {"A": "English original", "B": "issuer's English edition", "D": "machine translation"}


def latest(pat): return sorted(glob.glob(os.path.join(ROOT, pat)))[-1]


def country(code):
    if code == "EU": return "Euro area (digital euro)"
    if code == "UK": return "United Kingdom"
    try:
        import pycountry
        c = pycountry.countries.get(alpha_2=code); return (getattr(c, "common_name", None) or c.name) if c else code
    except Exception: return code


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--date", required=True); ap.add_argument("--xlsx"); a = ap.parse_args()
    rd = lambda p: list(csv.DictReader(open(p, encoding="utf-8")))
    U = rd(latest("data/units/UNITS_MANIFEST_*.csv")); C = {r["doc_key"]: r for r in rd(latest("data/units/CANDIDATES_*.csv"))}
    T = {r["id"]: r for r in rd(latest("data/manifest/TIERS_*.csv"))}; NU = rd(latest("data/units/UNITS_NOT_UNITISED_*.csv"))
    frame = [r for r in rd(os.path.join(ROOT, "data/frame/projects.csv")) if r["analytic_frame"].strip().lower() in ("1", "true", "yes")]
    dup = collections.defaultdict(list)
    for r in U: dup[r["text_sha256"]].append(r["id"])
    docs = []
    for r in sorted(U, key=lambda r: (r["project"], r["year"], r["id"])):
        t = T.get(r["id"], {}); c = C.get(r["doc_key"], {}); same = [i for i in dup[r["text_sha256"]] if i != r["id"]]
        docs.append({"project": r["project"], "country": country(r["project"]), "tier": r["tier"], "year": r["year"], "title": t.get("title", ""), "issuer": r["issuer"],
                     "issuer_type": r["issuer_type"], "kind": r["kind"], "text_read": ROUTE.get(r["route"], r["route"]), "source_language": t.get("language", ""),
                     "pages": r["pages"], "words": r["words"], "units": r["units"], "candidates_dictionary": c.get("D", ""), "candidates_neighbour": c.get("N", ""),
                     "candidates_random_control": c.get("R", ""), "decision": t.get("decision_v12", ""), "decision_source": t.get("decision_source", ""),
                     "id": r["id"], "note": ("same text as " + ", ".join(same)) if same else ""})
    out = os.path.join(ROOT, f"data/manifest/CORPUS_DOCUMENTS_{a.date}.csv")
    with open(out, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(docs[0])); w.writeheader(); w.writerows(docs)
    ev = collections.Counter(); pubs = collections.Counter()
    for r in T.values():
        if r["decision_v12"] in ("KEEP", "BORDERLINE") and r["project"] in {f["project"] for f in frame}:
            ev[r["project"]] += 1
            if not r.get("same_publication_as"): pubs[r["project"]] += 1
    cov = []
    for f in sorted(frame, key=lambda f: f["project"]):
        p = f["project"]; d = [x for x in docs if x["project"] == p]; yrs = sorted(int(x["year"]) for x in d if x["year"].isdigit())
        rt = collections.Counter(x["text_read"] for x in d); tier = next((r["tier"] for r in T.values() if r["project"] == p and r.get("tier")), "")
        cov.append({"project": p, "country": country(p), "tier": tier, "evidence_rows": ev[p], "evidence_publications": pubs[p], "documents_read": len(d),
                    "evidence_rows_without_english_text": sum(1 for r in NU if r["project"] == p), "years": f"{yrs[0]} to {yrs[-1]}" if yrs else "",
                    "english_original": rt["English original"], "issuer_english_edition": rt["issuer's English edition"], "machine_translation": rt["machine translation"],
                    "pages": sum(int(x["pages"]) for x in d), "words": sum(int(x["words"]) for x in d),
                    "candidate_units_dictionary": sum(int(x["candidates_dictionary"] or 0) for x in d),
                    "status": "no document can be read yet" if not d else ("one document only" if len(d) == 1 else "")})
    out2 = os.path.join(ROOT, f"data/manifest/CORPUS_COVERAGE_{a.date}.csv")
    with open(out2, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(cov[0])); w.writeheader(); w.writerows(cov)
    print(out, len(docs), "documents;", out2, len(cov), "projects;", sum(1 for c in cov if not c["documents_read"]), "projects without a readable document;",
          sum(1 for x in docs if x["note"]), "rows with duplicate text")
    if a.xlsx:
        import openpyxl
        from openpyxl.styles import Font, PatternFill, Alignment
        from openpyxl.utils import get_column_letter
        wb = openpyxl.Workbook(); clean = lambda v: "".join(ch for ch in str(v) if ch >= " " or ch in "\t\n") if isinstance(v, str) else v
        def sheet(ws, rows, widths, num):
            ws.append(list(rows[0]))
            for r in rows: ws.append([int(v) if k in num and str(v).isdigit() else clean(v) for k, v in r.items()])
            for c in ws[1]: c.font = Font(bold=True, color="FFFFFF"); c.fill = PatternFill("solid", fgColor="1F3A5F"); c.alignment = Alignment(wrap_text=True, vertical="top")
            for i, k in enumerate(rows[0], 1): ws.column_dimensions[get_column_letter(i)].width = widths.get(k, 13)
            ws.freeze_panes = "C2"; ws.auto_filter.ref = ws.dimensions
        ws = wb.active; ws.title = "COVERAGE"; sheet(ws, cov, {"country": 26, "status": 28, "years": 14}, {"evidence_rows", "evidence_publications", "documents_read", "evidence_rows_without_english_text", "english_original", "issuer_english_edition", "machine_translation", "pages", "words", "candidate_units_dictionary"})
        ws = wb.create_sheet("DOCUMENTS"); sheet(ws, docs, {"country": 22, "title": 70, "issuer": 34, "text_read": 24, "id": 40, "note": 30, "kind": 16}, {"year", "pages", "words", "units", "candidates_dictionary", "candidates_neighbour", "candidates_random_control"})
        nu = [{"project": r["project"], "country": country(r["project"]), "year": T.get(r["id"], {}).get("year", ""), "title": T.get(r["id"], {}).get("title", ""), "why_not_read": r["reason"], "id": r["id"]} for r in sorted(NU, key=lambda r: (r["project"], r["id"]))]
        ws = wb.create_sheet("NOT_READ"); sheet(ws, nu, {"country": 22, "title": 70, "why_not_read": 60, "id": 40}, {"year"})
        wb.save(a.xlsx); print(a.xlsx)


if __name__ == "__main__": main()
