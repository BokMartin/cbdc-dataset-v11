#!/usr/bin/env python3
"""Exposure registry of talk units: every paragraph that a person has read or that a development run has labelled (audit A4 of
17 Nov 2026, F06; ADR-007: "exposure registry of every displayed and model-labelled span; exclusion by canonical block").

The block is the displayed paragraph: (doc_key, page, para), because the coders and the model saw each unit with its whole
paragraph (scripts/units/context.py). A unit absorbed by a page-break join (PAGE_BREAK_JOINS_*.csv) counts as the unit it joined. A unit of a document that is no
longer in the unit set is kept with an empty `para` (it cannot be drawn again; the row records that it was shown).

Sources, in this order:
  data/units/AGREEMENT_SAMPLE_*.csv            shown to the authors (set name from the file; dates and coders from SOURCES below)
  data/units/DEV_ADJUDICATED_RELEVANCE_*.csv   shown to the authors together with a model's proposal (model-labelled too)
  data/*/runs/*/RUN_META.json with purpose development: every unit of the run is model-labelled (prompt tuning sees it)
Output data/units/EXPOSURE_REGISTRY_<date>.csv, one row per block, with no text: doc_key, page, para, block, units, sets,
shown_to, model_labelled_by, first_date. `blocks()` reads it; any later draw of a reference sample must leave these blocks out.
Which blocks the reference estimand excludes (only shown ones, or also those labelled in development runs) is for the authors
to approve (ADR-007 F06); the registry records both kinds apart so either rule can be applied.

usage: exposure_registry.py --units <units dir> --date 2026-11-23
"""
import argparse, csv, glob, json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# who saw a sample and when (from the exposure ledger); a sample not listed here is refused, so that nothing is registered silently
SOURCES = {
    "AGREEMENT_SAMPLE_dev_2026-11-13.csv": ("dev_2026-11-13", "MB DS", "", "2026-11-17"),
    "AGREEMENT_SAMPLE_facet80_2026-11-22.csv": ("facet80_2026-11-22", "MB DS", "", "2026-11-22"),
    "DEV_ADJUDICATED_RELEVANCE_MB_DS_2026-11-22.csv": ("dev_adjudication_2026-11-22", "MB DS", "gpt-6-astra (proposal shown)", "2026-11-22"),
}
COLS = ["doc_key", "page", "para", "block", "units", "sets", "shown_to", "model_labelled_by", "first_date"]


def doc_of(uid): return uid.rsplit(":p", 1)[0]


def rd(p): return list(csv.DictReader(open(p, encoding="utf-8")))


def collect(root=ROOT):
    """[(unit_id, set, shown_to, model_labelled_by, date)]"""
    out = []
    files = sorted(glob.glob(os.path.join(root, "data/units/AGREEMENT_SAMPLE_*.csv")) + glob.glob(os.path.join(root, "data/units/DEV_ADJUDICATED_RELEVANCE_*.csv")))
    for f in files:
        b = os.path.basename(f)
        if b not in SOURCES: raise SystemExit(f"{b}: no entry in SOURCES (who saw it, when); add one from the exposure ledger")
        s, who, model, date = SOURCES[b]
        out += [(r["unit_id"], s, who, model, date) for r in rd(f)]
    for mf in sorted(glob.glob(os.path.join(root, "data", "*", "runs", "*", "RUN_META.json"))):
        m = json.load(open(mf, encoding="utf-8"))
        if m.get("purpose") != "development": continue
        run = os.path.basename(os.path.dirname(mf)); cf = os.path.join(os.path.dirname(mf), "CALLS.csv")
        for r in rd(cf):
            if r["complete"] == "True":
                out += [(u, "run:" + run, "", m["model_requested"], r["started_utc"][:10]) for u in r["unit_ids"].split()]
    return out


def build(units_dir, entries, root=ROOT):
    joins = {}
    for f in sorted(glob.glob(os.path.join(root, "data/units/PAGE_BREAK_JOINS_*.csv"))):
        for r in rd(f): joins[r["absorbed"]] = r["kept"]
    where, B, missing = {}, {}, []
    for uid, s, who, model, date in entries:
        uid = joins.get(uid, uid); d = doc_of(uid)
        if d not in where:
            p = os.path.join(units_dir, d + ".units.csv")
            where[d] = {u["unit_id"]: (int(u["page"]), int(u["para"])) for u in rd(p)} if os.path.exists(p) else {}
        if not where[d]: pg, pa = int(re.search(r":p(\d+):", uid).group(1)), ""   # document no longer in the corpus: kept for the record
        elif uid not in where[d]: missing.append(uid); continue
        else: pg, pa = where[d][uid]
        k = (d, pg, pa)
        b = B.setdefault(k, {"units": set(), "sets": set(), "shown": set(), "model": set(), "date": date})
        b["units"].add(uid); b["sets"].add(s); b["shown"].update(who.split()); b["date"] = min(b["date"], date)
        if model: b["model"].add(model)
    rows = [{"doc_key": d, "page": pg, "para": pa, "block": f"{d}:p{pg}:para{pa}" if pa != "" else f"{d} (not in the corpus)", "units": " ".join(sorted(b["units"])), "sets": " ".join(sorted(b["sets"])),
             "shown_to": " ".join(sorted(b["shown"])), "model_labelled_by": "; ".join(sorted(b["model"])), "first_date": b["date"]} for (d, pg, pa), b in sorted(B.items(), key=lambda kv: (kv[0][0], kv[0][1], str(kv[0][2]).zfill(6)))]
    return rows, missing


def blocks(path=None, shown_only=False):
    """{(doc_key, page, para)} of the registry (latest file by default)."""
    path = path or sorted(glob.glob(os.path.join(ROOT, "data/units/EXPOSURE_REGISTRY_*.csv")))[-1]
    return {(r["doc_key"], int(r["page"]), int(r["para"])) for r in rd(path) if r["para"] and (not shown_only or r["shown_to"])}


def main(argv=None):
    ap = argparse.ArgumentParser(); ap.add_argument("--units", required=True); ap.add_argument("--date", required=True); a = ap.parse_args(argv)
    rows, missing = build(a.units, collect())
    if missing: raise SystemExit(f"{len(missing)} registered units are not in the unit files, e.g. {missing[:3]}")
    out = os.path.join(ROOT, "data/units", f"EXPOSURE_REGISTRY_{a.date}.csv")
    with open(out, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, COLS); w.writeheader(); w.writerows(rows)
    print(f"{len(rows)} blocks ({sum(bool(r['shown_to']) for r in rows)} shown to the authors, {sum(bool(r['model_labelled_by']) for r in rows)} model-labelled) -> {os.path.relpath(out, ROOT)}")
    return rows


if __name__ == "__main__":
    main()
