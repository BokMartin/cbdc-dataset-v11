#!/usr/bin/env python3
"""Blind facet sample of 80 sentences (D8 of ADR-012; MB 22 Nov 2026: "raději 80 vět").

Both authors code the same 80 units, each alone and before any model has labelled a unit: relevance afresh, and for the
units they call relevant voice, aspect (optional second aspect), basis, decision and stance (ADR-012 D8 as accepted by MB
at 14:21 and 14:27; basis added by MB at 16:07, as the auditor proposed, because D3 counts sentences with a mechanism). The result is a development diagnosis of the facets, not the reference measurement: the reference
sample of 400 (D18) is drawn later and never contains a unit of this set or of the development sample.

Population: candidate units of stratum D (dictionary hit) in documents of stratum `evidence` of the latest unit
manifest (INCLINED documents are out), minus every unit whose paragraph was shown to the coders in an earlier
agreement sample (the 120 development units of 13 Nov were shown with their paragraphs, so the whole paragraph is
exposed; A4 F06). --projects narrows it (for example NO,UK). Dictionary hits are used because the facets are coded only on
relevant units and about half of the development hits were relevant to both coders; a fresh mix with neighbours and
random controls would leave too few relevant units out of 80.

Draw: stratified simple random sample by text route (A English original, B issuer's English edition, D machine
translation), allocation proportional to the size of each route in the population (largest remainder), units in the
order of SHA-256(seed | unit_id) within a route. The inclusion probability n_h / N_h of every unit is stored, so the
set can be weighted back to the population of dictionary hits (D18). No caps and no rotation: these would make the
probabilities unknown (audit A4b, finding on 21a).

What the coder sees: the unit, its paragraph (scripts/units/context.py, the string the model will receive), issuer,
kind, year and text route. Never a model label, never the other coder's label, never a label from an earlier round.

Outputs: outside the repository (unit text is the issuers' copyright) one workbook per coder, rows in a different
order for each; in the repository data/units/AGREEMENT_SAMPLE_facet80_<date>.csv with unit ids, route, inclusion
probability, the SHA-256 of the unit text, of its context and of the document's unit file, and the row order per
coder.

usage: draw_facet_sample.py --units <units dir> --issuers data/manifest/ISSUERS_2026-11-13.csv --out <dir> --date 2026-11-22
       [--n 80] [--projects NO,UK] [--manifest data/units/UNITS_MANIFEST_<date>.csv] [--samples-dir data/units]
"""
import argparse
import collections
import csv
import glob
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
import context  # noqa: E402

SEED = "talk-v13-facet80-2026-11-22"
ROUTE = {"A": "English original", "B": "issuer's English edition", "D": "MACHINE TRANSLATION"}
COLS = ["n", "unit_id", "project", "issuer (document)", "kind", "year", "text is", "page", "paragraph (unit marked »…«)",
        "UNIT TO CODE", "relevant", "voice", "aspect", "aspect2", "basis", "decision", "stance", "note"]
FACETS = ("voice", "aspect", "aspect2", "basis", "decision", "stance")
WRAP = Alignment(wrap_text=True, vertical="top")
BOLD = Font(bold=True)


def hx(*p):
    return hashlib.sha256("|".join(p).encode()).hexdigest()


def clean(t):
    import re
    t = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", " ", t or "")
    return ("'" + t) if t and t[0] in "=+-@" else t


def allocate(sizes, n):
    """Proportional allocation with the largest remainder; ties broken by route letter."""
    total = sum(sizes.values())
    if total < n:
        raise SystemExit(f"population {total} smaller than the sample {n}")
    raw = {k: n * v / total for k, v in sizes.items()}
    out = {k: int(x) for k, x in raw.items()}
    for k in sorted(raw, key=lambda k: (-(raw[k] - out[k]), k))[: n - sum(out.values())]:
        out[k] += 1
    return out


def exposed_units(samples_dir):
    """Every unit of an earlier agreement sample (development, facet, reference) is out."""
    seen = set()
    for f in glob.glob(os.path.join(samples_dir, "AGREEMENT_SAMPLE_*.csv")):
        seen |= {r["unit_id"] for r in csv.DictReader(open(f, encoding="utf-8"))}
    return seen


def population(units_dir, manifest, projects, exclude):
    pool, text = [], {}
    for m in manifest:
        if m.get("stratum", "evidence") != "evidence" or (projects and m["project"] not in projects):
            continue
        U = list(csv.DictReader(open(os.path.join(units_dir, m["doc_key"] + ".units.csv"), encoding="utf-8")))
        st = {r["unit_id"]: r["stratum"] for r in csv.DictReader(open(os.path.join(units_dir, m["doc_key"] + ".candidates.csv"), encoding="utf-8"))}
        shown = {(u["page"], u["para"]) for u in U if u["unit_id"] in exclude}  # paragraphs a coder has already read
        for i, u in enumerate(U):
            if st.get(u["unit_id"]) == "D" and (u["page"], u["para"]) not in shown:
                text[u["unit_id"]] = (context.render(U, i), u["text"], u["page"])
                pool.append({"unit_id": u["unit_id"], "doc_key": m["doc_key"], "id": m["id"], "project": m["project"], "tier": m["tier"],
                             "route": m["route"], "kind": m["kind"], "year": m["year"], "units_sha256": m["units_sha256"]})
    return pool, text


def draw(pool, n):
    by = collections.defaultdict(list)
    for u in pool:
        by[u["route"]].append(u)
    alloc = allocate({r: len(v) for r, v in by.items()}, n)
    sample = []
    for r, units in sorted(by.items()):
        chosen = sorted(units, key=lambda u: hx(SEED, u["unit_id"]))[: alloc[r]]
        for u in chosen:
            u["inclusion_probability"] = round(alloc[r] / len(units), 8)
            u["route_population"] = len(units)
        sample += chosen
    return sample


README = [
    "Slepé kódování 80 vět, kodér {coder} (vylosováno {date}, seed {seed}). Na listu CODE je {n} vět. Kóduje každý SÁM, bez porady a bez pomoci jazykového modelu; o jednotlivých větách se nebavte, dokud oba neodevzdáte.",
    "PROČ: ověřujeme, zda se dva lidé shodnou na údajích voice, aspect, basis, decision a stance (rozhodnutí MB 22. 11. 2026, ADR-012 D8; basis doplněn na přání MB), a zároveň znovu na relevanci. Výsledek se zveřejní takový, jaký bude. Když shoda nevyjde, projdete věty spolu a dohodnete konečné štítky; nesplněný práh ale zůstane nesplněný a údaj se v článku označí jako exploratorní.",
    "CO SE KÓDUJE: jen věta ve žlutém sloupci UNIT TO CODE. Sloupec 'paragraph' je odstavec, v němž věta stojí (věta je v něm označena »takto«); slouží k pochopení zájmen, odkazů a toho, kdo mluví. Je prázdný, pokud věta stojí sama (nadpis, buňka tabulky). Stejný odstavec dostane i model.",
    "Sloupec 'relevant': R = věta sama něco říká o soukromí, identifikovatelnosti nebo přístupu k datům uživatelů retailové CBDC; N = neříká; U = nečitelná nebo useknutá (U jen výjimečně, viz CODEBOOK). Pokud N nebo U, ostatní sloupce nechte prázdné.",
    "Pokud R: vyplňte voice, aspect, basis, decision a stance (rozbalovací seznamy). aspect2 jen tehdy, když věta mluví o dvou aspektech. Ostatní údaje z dřívějšího sešitu (implementation, modality, příznaky) se tentokrát nekódují. Do 'note' pište pochybnosti.",
    "Sloupec 'text is' říká, zda čtete anglický originál, anglické vydání vydavatele, nebo STROJOVÝ PŘEKLAD. Věty jsou slovníkové zásahy (obsahují slovo z oblasti soukromí), proto bude většina relevantní, ale ne všechny.",
    "Pravidla jsou na listu CODEBOOK: verze 0.4 z 22. 11. 2026 po společném projití neshod (ADR-011); dokud ji oba autoři nepotvrdí, je to návrh. Kódujte podle ní.",
    "Pořadí řádků je pro každého kodéra jiné (náhodné). Neřaďte list: kódujte v daném pořadí. Odhad času 2 až 3,5 hodiny. Soubor uložte pod stejným názvem a pošlete zpět; nic jiného v něm neměňte.",
]


def workbook(path, coder, date, sample, text, iss, schema, codebook):
    wb = Workbook()
    ws = wb.active
    ws.title = "READ_ME"
    for t in README:
        ws.append([t.format(coder=coder, date=date, seed=SEED, n=len(sample))])
    ws.column_dimensions["A"].width = 160
    for r in ws.iter_rows():
        for c in r:
            c.alignment = WRAP
    cb = wb.create_sheet("CODEBOOK")
    for line in codebook:
        cb.append(line)
    for i, wd in enumerate([18, 26, 120], 1):
        cb.column_dimensions[chr(64 + i)].width = wd
    for r in cb.iter_rows():
        for c in r:
            c.alignment = WRAP
        if r[0].value and len(r) > 1 and not r[1].value:
            r[0].font = BOLD
    d = wb.create_sheet("CODE")
    d.append(COLS)
    order = sorted(sample, key=lambda u: hx(SEED, coder, u["unit_id"]))
    for n, u in enumerate(order, 1):
        ctx, t, pg = text[u["unit_id"]]
        i_ = iss.get(u["id"], {})
        issuer = (i_.get("issuer") or "") + (" + " + i_["joint_with"] if i_.get("joint_with") else "")
        d.append([n, u["unit_id"], u["project"], issuer, u["kind"], u["year"], ROUTE[u["route"]], pg, clean(ctx), clean(t)] + [""] * (len(COLS) - 10))
        d.cell(n + 1, 10).fill = PatternFill("solid", fgColor="FFF2CC")
        u["order_" + coder] = n
    lists = {"relevant": ["R", "N", "U"], "voice": schema["voice"], "aspect": schema["aspect"], "aspect2": schema["aspect"],
             "basis": schema["basis"], "decision": schema["decision"], "stance": schema["stance"]}
    for c, wd in enumerate([5, 14, 7, 22, 12, 6, 14, 5, 60, 60, 9, 11, 18, 18, 15, 15, 12, 30], 1):
        d.column_dimensions[d.cell(1, c).column_letter].width = wd
    for c in range(1, len(COLS) + 1):
        d.cell(1, c).font = BOLD
        d.cell(1, c).fill = PatternFill("solid", fgColor="DDDDDD")
    for r in d.iter_rows():
        for c in r:
            c.alignment = WRAP
    for name, vals in lists.items():
        dv = DataValidation(type="list", formula1='"' + ",".join(vals) + '"', allow_blank=True)
        d.add_data_validation(dv)
        L = d.cell(1, COLS.index(name) + 1).column_letter
        dv.add(f"{L}2:{L}{len(sample) + 1}")
    d.freeze_panes = "K2"
    wb.save(path)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--units", required=True)
    ap.add_argument("--issuers", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--date", required=True)
    ap.add_argument("--n", type=int, default=80)
    ap.add_argument("--projects", default="")
    ap.add_argument("--manifest", default=None)
    ap.add_argument("--samples-dir", default=os.path.join(ROOT, "data/units"))
    ap.add_argument("--schema", default=os.path.join(ROOT, "schema/talk_units_v13_DRAFT.json"))
    ap.add_argument("--codebook", default=os.path.join(ROOT, "docs/TALK_CODEBOOK_cs.tsv"))
    a = ap.parse_args(argv)
    mf = a.manifest or sorted(glob.glob(os.path.join(ROOT, "data/units/UNITS_MANIFEST_*.csv")))[-1]
    manifest = list(csv.DictReader(open(mf, encoding="utf-8")))
    if "stratum" not in manifest[0]:
        raise SystemExit(f"{mf} has no stratum column: INCLINED documents would enter the population")
    iss = {r["id"]: r for r in csv.DictReader(open(a.issuers, encoding="utf-8"))}
    projects = {p.strip() for p in a.projects.split(",") if p.strip()}
    pool, text = population(a.units, manifest, projects, exposed_units(a.samples_dir))
    sample = draw(pool, a.n)
    schema = json.load(open(a.schema, encoding="utf-8"))["L2_facets"]
    codebook = [l.rstrip("\n").split("\t") for l in open(a.codebook, encoding="utf-8") if l.strip()]
    os.makedirs(a.out, exist_ok=True)
    files = []
    for coder in ("MB", "DS"):
        files.append(os.path.join(a.out, f"TALK_FACET80_{coder}_{a.date}.xlsx"))
        workbook(files[-1], coder, a.date, sample, text, iss, schema, codebook)
    rows = [{"unit_id": u["unit_id"], "set": "facet80", "candidate_stratum": "D", "project": u["project"], "tier": u["tier"],
             "route": u["route"], "kind": u["kind"], "route_population": u["route_population"],
             "inclusion_probability": u["inclusion_probability"],
             "unit_text_sha256": hashlib.sha256(text[u["unit_id"]][1].encode("utf-8")).hexdigest(),
             "context_sha256": hashlib.sha256(text[u["unit_id"]][0].encode("utf-8")).hexdigest(),
             "units_file_sha256": u["units_sha256"], "order_MB": u["order_MB"], "order_DS": u["order_DS"]}
            for u in sorted(sample, key=lambda u: u["unit_id"])]
    out_csv = os.path.join(a.samples_dir, f"AGREEMENT_SAMPLE_facet80_{a.date}.csv")
    with open(out_csv, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    c = collections.Counter
    summary = {"n": len(sample), "population": len(pool), "routes": dict(c(u["route"] for u in sample)),
               "tiers": dict(c(u["tier"] for u in sample)), "projects": len({u["project"] for u in sample}),
               "documents": len({u["doc_key"] for u in sample}), "with_context": sum(bool(text[u["unit_id"]][0]) for u in sample),
               "manifest": os.path.basename(mf), "record": out_csv, "workbooks": files}
    print(json.dumps(summary, indent=1))
    return summary


if __name__ == "__main__":
    main()
