#!/usr/bin/env python3
"""Results for the website (MB, 27 Nov 2026): privacy index, cells, talk, hypothesis, PET table, cell history and the
database of relevant privacy paragraphs, written as JSON files that the pages of site/ read. A new run of results (after
the authors decide the combination rule of ADR-018 and lock the verification of ADR-017) changes only these files; the pages
stay as they are.

Inputs are files outside the repository, because the model outputs hold source text (ADR-014, REDUCER_REPAIR_2026-11-26):
  --cells DIR      cells_claude.json, cells_sol62.json, cells_deepseek.json (scripts/extraction/reduce_v122.py output)
  --pack DIR       results files: CBDC_privacy_talk_hypothesis_*.csv, CBDC_PET_observations_*.csv
  --history DIR    CBDC_cell_history_all_projects_*.csv, CBDC_change_log_*.csv
  --paragraphs F   optional: relevant own-voice units (project, doc_key, page_index, unit_id, aspect, voice, basis, decision, text)
  --status TEXT    what the results are, shown on every page (default: preliminary model output, not verified by the authors)
  --mask CODES     projects whose model values are withheld (comma list): the authors verify them blind, so no model value,
                   quotation, talk count, PET row, change or paragraph of theirs is written (MB, 27 Nov 2026, after audit A6 §13)
  --source K=V     provenance shown on the site and in the JSON (repeatable): commit, tag, pull request, date

Rules kept here, not on the pages:
  * Index: scripts/derive_index.py (mean of seven cells F1, F2, F4, F7, F8, F9, F10 as an interval; four-cell variant;
    F3 a category; ADR-012 D4). Combination of the three models, both readings until ADR-018 is decided:
    strict = all three models give the same value; provisional = at least one model gives a value and none gives another
    (the rule stated in the results package of 24 Nov and in scripts/audit/recompute_results.py, step 4).
  * Quotes: short quotations only, with the document and the page (MB, 27 Nov 2026; ADR-019). A quote is cut at QUOTE_MAX
    characters, at a sentence or word boundary, and always links to the issuer's own document.
  * Hypothesis (Registration A §3) from the same cells as the index: C_p counts protective committed cells among F1, F2,
    F4, F7 (derive_index.committed, for every model giving the combined value); lower reading counts an undetermined cell as
    committed and a unit without a majority as not relevant, upper the reverse. T_p: own-voice talk in at least two
    publications and at least 1 relevant unit per 100 eligible. No verdict is written while a core project is withheld or
    the combination rule is undecided (ADR-018): only the per-project flags of the projects shown.
  * No ordering by value is written into the data; the pages list by tier and name.

usage: build_results_site.py --cells DIR --pack DIR --history DIR [--paragraphs F] --source commit=... --source tag=...
"""
import argparse
import csv
import glob
import hashlib
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import derive_index as di  # noqa: E402

OUT = os.path.join(ROOT, "site", "assets")
MODELS = [("claude", "Claude"), ("sol62", "GPT (sol)"), ("deepseek", "DeepSeek")]
CELLS7 = list(di.CORE)
CELLS8 = list(di.CELLS)
QUOTE_MAX = 300
STATUS = "Preliminary model output, not verified by the authors"
MANIFEST = os.path.join(ROOT, "data", "units", "UNITS_MANIFEST_2026-11-23b.csv")
PET_PAPER = {"title": "Nijsse, J. and Pinto, A. (2026). Central Bank Digital Currencies: Where is the Privacy, Technology, and Anonymity? arXiv:2602.23659v2.",
             "url": "https://arxiv.org/abs/2602.23659"}


def sha(path):
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def one(folder, pattern):
    hits = sorted(glob.glob(os.path.join(folder, pattern)))
    if len(hits) != 1:
        raise SystemExit(f"{pattern}: {len(hits)} files in {folder}, need exactly one")
    return hits[0]


def rows(path):
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def short(text, limit=QUOTE_MAX):
    """A short quotation: whitespace collapsed, cut at a sentence end or a word boundary, with an ellipsis if cut."""
    t = re.sub(r"\s+", " ", str(text or "")).strip()
    if len(t) <= limit:
        return t
    cut = t[:limit - 2]  # room for " …": the result is never longer than limit
    m = max(cut.rfind(". "), cut.rfind("; "))
    if m > limit * 0.5:
        out = cut[:m + 1] + " …"
    else:
        sp = cut.rfind(" ")
        out = (cut[:sp] if sp > 0 else cut).rstrip(",;:") + " …"
    assert len(out) <= limit
    return out


def iv(x):
    return [round(x["lower"], 4), round(x["upper"], 4)]


def combine(cells_by_model, p, f, strict):
    vs = [((cells_by_model[k].get(p) or {}).get("cells", {}).get(f) or {}).get("value") or "" for k, _ in MODELS]
    nz = {v for v in vs if v}
    if strict:
        return vs[0] if len(set(vs)) == 1 and vs[0] else ""
    return next(iter(nz)) if len(nz) == 1 else ""


def agreement(vals):
    nz = [v for v in vals if v]
    if not nz:
        return "none"
    if len(set(nz)) > 1:
        return "conflict"
    return "all3" if len(nz) == 3 else "partial"


def hypothesis_flags(cells_by_model, p, talk_row, strict):
    """[lower, upper] for 'meets both' (Registration A §3), from the combined cells and the talk counts."""
    el, own, nm, pb = (int(talk_row[k]) for k in ("eligible_sentences", "own_voice_relevant", "no_majority", "publications_with_own_talk"))
    tl = pb >= 2 and el > 0 and own * 100 / el >= 1
    tu = pb >= 2 and el > 0 and (own + nm) * 100 / el >= 1
    com = und = 0
    for f in di.CORE4:
        v = combine(cells_by_model, p, f, strict)
        if not v:
            und += 1
            continue
        cs = [((cells_by_model[k].get(p) or {}).get("cells", {}).get(f) or {}) for k, _ in MODELS]
        if v == di.PROTECTIVE[f] and all(di.committed(c, f) for c in cs if c.get("value") == v):
            com += 1
    return [bool(tl and com + und < 2), bool(tu and com < 2)], com


def build(a):
    sources = dict(s.split("=", 1) for s in a.source)
    masked = sorted({x.strip() for x in (a.mask or "").split(",") if x.strip()})
    manifest = {r["doc_key"]: r for r in rows(MANIFEST)}
    docs_site = {d["id"]: d for d in json.load(open(os.path.join(OUT, "documents.json"), encoding="utf-8"))["documents"]}
    names = {p["code"]: p for p in json.load(open(os.path.join(OUT, "projects.json"), encoding="utf-8"))["projects"]}

    def doc_ref(doc_key, page=None):
        """Document reference for the site: id in documents.json, title, issuer URL, page."""
        if not doc_key:
            return None
        m = manifest.get(doc_key)
        did = m["id"] if m else doc_key
        d = docs_site.get(did) or {}
        return {"id": did, "t": d.get("t") or (m or {}).get("issuer") or did, "u": d.get("u") or "", "y": d.get("y"),
                "pg": int(page) if str(page or "").isdigit() else None}

    inputs = {}
    cells = {}
    for k, _ in MODELS:
        f = os.path.join(a.cells, f"cells_{k}.json")
        cells[k] = json.load(open(f, encoding="utf-8"))
        inputs[os.path.basename(f)] = sha(f)
    talk_f = one(a.pack, "CBDC_privacy_talk_hypothesis_*.csv")
    pet_f = one(a.pack, "CBDC_PET_observations_*.csv")
    hist_f = one(a.history, "CBDC_cell_history_all_projects_*.csv")
    log_f = one(a.history, "CBDC_change_log_*.csv")
    for f in (talk_f, pet_f, hist_f, log_f):
        inputs[os.path.basename(f)] = sha(f)
    talk = {r["project"]: r for r in rows(talk_f)}
    pet_csv = rows(pet_f)
    families = {r["code"]: r["family"] for r in pet_csv}
    mlabel = {"Claude": "claude", "Sol": "sol62", "DeepSeek": "deepseek"}
    pet_page = {}
    for r in pet_csv:  # page of each PET observation, from the results package (the reducer keeps no page for PETs)
        if str(r.get("pdf_page") or "").isdigit():
            pet_page.setdefault((r["project"], mlabel.get(r["model"], r["model"]), r["code"], r["doc_key"]), r["pdf_page"])

    projects = sorted(set().union(*[set(cells[k]) for k, _ in MODELS]))
    out = []
    pet_rows = []
    for p in projects:
        tier = talk.get(p, {}).get("tier") or (names.get(p) or {}).get("tier") or ""
        if p in masked:
            out.append({"id": p, "name": (names.get(p) or {}).get("name") or p, "tier": tier, "masked": True})
            continue
        per_model, cellinfo = {}, {}
        for k, label in MODELS:
            c = (cells[k].get(p) or {}).get("cells", {})
            per_model[k] = iv(di.axis1(c))
        S = {f: {"value": combine(cells, p, f, True)} for f in CELLS8 if combine(cells, p, f, True)}
        P = {f: {"value": combine(cells, p, f, False)} for f in CELLS8 if combine(cells, p, f, False)}
        xs, xp, x4 = di.axis1(S), di.axis1(P), di.axis1(P, cells_used=di.CORE4)
        for f in CELLS8:
            by = {}
            for k, _ in MODELS:
                c = ((cells[k].get(p) or {}).get("cells", {}).get(f) or {})
                by[k] = {"v": c.get("value") or "", "es": c.get("evidence_state") or "", "ds": c.get("decision_status") or "",
                         "is": c.get("implementation_status") or "", "ur": c.get("unknown_reason") or "",
                         "doc": doc_ref(c.get("document_id"), c.get("page_index")),
                         "q": short(c.get("quote")) if c.get("quote") else ""}
            cellinfo[f] = {"strict": (S.get(f) or {}).get("value", ""), "prov": (P.get(f) or {}).get("value", ""),
                           "agree": agreement([by[k]["v"] for k, _ in MODELS]), "models": by}
        t = talk.get(p)
        talk_out = None
        if t:
            hp, com_p = hypothesis_flags(cells, p, t, False)
            hs, com_s = hypothesis_flags(cells, p, t, True)
            talk_out = {"eligible": int(t["eligible_sentences"]), "own": int(t["own_voice_relevant"]), "nomaj": int(t["no_majority"]),
                        "per100": [float(t["per100_lower"]), float(t["per100_upper"])], "pubs": int(t["publications_with_own_talk"]),
                        "mech": float(t["mechanism_share"]) if t["mechanism_share"] else None,
                        "dec": float(t["decision_share"]) if t["decision_share"] else None,
                        "commit4": {"prov": com_p, "strict": com_s},
                        "gap": [int(t["gap_lower"]), int(t["gap_upper"])],
                        "h": {"prov": hp, "strict": hs}}
        pets = {}
        for k, label in MODELS:
            pr = cells[k].get(p) or {}
            for table, key in (("retail", "pet"), ("wholesale", "pet_wholesale_context")):
                for o in pr.get(key) or []:
                    code = o.get("code") or ""
                    pid = (table, code)
                    e = pets.setdefault(pid, {"code": code, "table": table, "family": families.get(code, "other named" if code.startswith("other:") else ""),
                                              "models": [], "obs": []})
                    if k not in e["models"]:
                        e["models"].append(k)
                    dk = o.get("document_id")
                    e["obs"].append({"m": k, "text": short(o.get("technique_text") or "", 120), "fn": short(o.get("privacy_function") or "", 200),
                                     "ds": o.get("decision_status") or "", "is": o.get("implementation_status") or "",
                                     "doc": doc_ref(dk, pet_page.get((p, k, code, dk)))})
        for e in pets.values():
            e["committed"] = any(o["ds"] == "endorsed" or o["is"] == "operational" for o in e["obs"])
            pet_rows.append(dict(e, project=p, tier=tier))
        out.append({"id": p, "name": (names.get(p) or {}).get("name") or p, "tier": tier,
                    "index": {"prov": iv(xp), "strict": iv(xs), "prov4": iv(x4), "models": per_model,
                              "det_prov": xp["determined"], "det_strict": xs["determined"]},
                    "f3": {"prov": (P.get("F3") or {}).get("value", ""), "strict": (S.get("F3") or {}).get("value", "")},
                    "cells": cellinfo, "talk": talk_out,
                    "pets": sorted({c for (tb, c) in pets if tb == "retail"})})

    core = [x for x in out if x["tier"] in ("T1", "T2")]
    shown = [x for x in core if not x.get("masked") and x.get("talk")]
    hyp = {"n": len(core), "shown": [x["id"] for x in shown], "withheld": [x["id"] for x in core if x.get("masked")],
           "verdict": None,
           "reason": "No verdict until the authors have verified the cells of the core projects and decided how the three "
                     "models are combined (ADR-018). The per-project flags of the projects shown are in each row."}

    meta = {"status": a.status or STATUS, "sources": sources, "inputs": inputs, "models": dict(MODELS),
            "cells7": CELLS7, "cells4": list(di.CORE4), "quote_max": QUOTE_MAX, "pet_paper": PET_PAPER, "masked": masked,
            "masked_note": "Withheld until the authors' verification: the model values of these projects are not published."}
    results = {"meta": meta, "hypothesis": hyp, "projects": out}

    # cell history, condensed: per project, per cell, the value of each model after each document
    hist = {}
    for r in rows(hist_f):
        if r["project"] in masked:
            hist[r["project"]] = {"tier": r["tier"], "masked": True}
            continue
        p = hist.setdefault(r["project"], {"tier": r["tier"], "docs": [], "cells": {}})
        n = int(r["after_document_no"])
        while len(p["docs"]) < n:
            p["docs"].append(None)
        if p["docs"][n - 1] is None:
            ref = doc_ref(r["doc_key"]) or {}
            p["docs"][n - 1] = {"n": n, "date": r["date"], "id": ref.get("id"), "t": ref.get("t"), "u": ref.get("u")}
        m = {"Claude": "claude", "Sol": "sol62", "DeepSeek": "deepseek"}.get(r["model"], r["model"])
        seq = p["cells"].setdefault(r["cell"], {}).setdefault(m, [])
        while len(seq) < n:
            seq.append(None)
        seq[n - 1] = [r["value"] or "", r["evidence_state"], r["decision_status"], r["implementation_status"], r["unknown_reason"]]
    changes = []
    for r in rows(log_f):
        if r["project"] in masked:
            continue
        changes.append({"id": r["log_id"], "project": r["project"], "tier": r["tier"], "cell": r["cell"], "cat": r["category"],
                        "kind": r["change_kind"], "dir": r["direction"], "models": r["models"], "n": int(r["after_document_no"] or 0),
                        "date": r["date"], "doc": doc_ref(r["doc_key"], r["page_index"]),
                        "before": [r["before_value"], r["before_decision"], r["before_implementation"]],
                        "after": [r["after_value"], r["after_decision"], r["after_implementation"]], "q": short(r["quote"])})
    history = {"meta": meta, "projects": hist, "changes": changes}

    pets = {"meta": meta, "rows": pet_rows}

    paras = {"meta": meta, "rows": [], "available": False}
    if a.paragraphs:
        inputs[os.path.basename(a.paragraphs)] = sha(a.paragraphs)
        for r in rows(a.paragraphs):
            if r["project"] in masked:
                continue
            paras["rows"].append({"p": r["project"], "doc": doc_ref(r["doc_key"], r.get("page_index")), "u": r.get("unit_id", ""),
                                  "a": r.get("aspect", ""), "v": r.get("voice", ""), "b": r.get("basis", ""), "d": r.get("decision", ""),
                                  "q": short(r.get("text", "")),
                                  "mt": (manifest.get(r["doc_key"]) or {}).get("route") == "D"})  # route D: machine translation
        paras["available"] = True
    return {"results.json": results, "cell_history.json": history, "pets.json": pets, "paragraphs.json": paras}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cells", required=True)
    ap.add_argument("--pack", required=True)
    ap.add_argument("--history", required=True)
    ap.add_argument("--paragraphs")
    ap.add_argument("--status")
    ap.add_argument("--mask", default="")
    ap.add_argument("--source", action="append", default=[])
    a = ap.parse_args()
    for name, data in build(a).items():
        with open(os.path.join(OUT, name), "w", encoding="utf-8") as fh:
            json.dump(data, fh, ensure_ascii=False, separators=(",", ":"))
            fh.write("\n")
        print("written site/assets/" + name, os.path.getsize(os.path.join(OUT, name)) // 1024, "KB")


if __name__ == "__main__":
    main()
