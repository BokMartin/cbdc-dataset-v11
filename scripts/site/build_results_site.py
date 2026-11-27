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
  --source K=V     provenance shown on the site and in the JSON (repeatable): commit, tag, pull request, date

Rules kept here, not on the pages:
  * Index: scripts/derive_index.py (mean of seven cells F1, F2, F4, F7, F8, F9, F10 as an interval; four-cell variant;
    F3 a category; ADR-012 D4). Combination of the three models, both readings until ADR-018 is decided:
    strict = all three models give the same value; provisional = at least one model gives a value and none gives another
    (the rule stated in the results package of 24 Nov and in scripts/audit/recompute_results.py, step 4).
  * Quotes: short quotations only, with the document and the page (MB, 27 Nov 2026; ADR-019). A quote is cut at QUOTE_MAX
    characters, at a sentence or word boundary, and always links to the issuer's own document.
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
    cut = t[:limit]
    m = max(cut.rfind(". "), cut.rfind("; "))
    if m > limit * 0.5:
        return cut[:m + 1] + " …"
    return cut[:cut.rfind(" ")].rstrip(",;:") + " …"


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


def build(a):
    sources = dict(s.split("=", 1) for s in a.source)
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
    families = {r["code"]: r["family"] for r in rows(pet_f)}

    projects = sorted(set().union(*[set(cells[k]) for k, _ in MODELS]))
    out = []
    pet_rows = []
    for p in projects:
        tier = talk.get(p, {}).get("tier") or (names.get(p) or {}).get("tier") or ""
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
            talk_out = {"eligible": int(t["eligible_sentences"]), "own": int(t["own_voice_relevant"]), "nomaj": int(t["no_majority"]),
                        "per100": [float(t["per100_lower"]), float(t["per100_upper"])], "pubs": int(t["publications_with_own_talk"]),
                        "mech": float(t["mechanism_share"]) if t["mechanism_share"] else None,
                        "dec": float(t["decision_share"]) if t["decision_share"] else None,
                        "commit4": int(t["protective_commitments_F1_F2_F4_F7"] or 0),
                        "gap": [int(t["gap_lower"]), int(t["gap_upper"])],
                        "h": {"prov": [t["meets_both_prov_lower"] == "True", t["meets_both_prov_upper"] == "True"],
                              "strict": [t["meets_both_strict_lower"] == "True", t["meets_both_strict_upper"] == "True"]}}
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
                    e["obs"].append({"m": k, "text": o.get("technique_text") or "", "fn": short(o.get("privacy_function") or "", 200),
                                     "ds": o.get("decision_status") or "", "is": o.get("implementation_status") or "",
                                     "doc": doc_ref(o.get("document_id"))})
        for e in pets.values():
            e["committed"] = any(o["ds"] == "endorsed" or o["is"] == "operational" for o in e["obs"])
            pet_rows.append(dict(e, project=p, tier=tier))
        out.append({"id": p, "name": (names.get(p) or {}).get("name") or p, "tier": tier,
                    "index": {"prov": iv(xp), "strict": iv(xs), "prov4": iv(x4), "models": per_model,
                              "det_prov": xp["determined"], "det_strict": xs["determined"]},
                    "f3": {"prov": (P.get("F3") or {}).get("value", ""), "strict": (S.get("F3") or {}).get("value", "")},
                    "cells": cellinfo, "talk": talk_out,
                    "pets": sorted({c for (tb, c) in pets if tb == "retail"})})

    core = [x for x in out if x["tier"] in ("T1", "T2") and x["talk"]]
    hyp = {}
    for rule in ("prov", "strict"):
        L = sum(x["talk"]["h"][rule][0] for x in core)
        U = sum(x["talk"]["h"][rule][1] for x in core)
        hyp[rule] = {"L": L, "U": U, "n": len(core), "verdict": "holds" if L >= 9 else "fails" if U <= 8 else "inconclusive"}

    meta = {"status": a.status or STATUS, "sources": sources, "inputs": inputs, "models": dict(MODELS),
            "cells7": CELLS7, "cells4": list(di.CORE4), "quote_max": QUOTE_MAX, "pet_paper": PET_PAPER}
    results = {"meta": meta, "hypothesis": hyp, "projects": out}

    # cell history, condensed: per project, per cell, the value of each model after each document
    hist = {}
    for r in rows(hist_f):
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
            paras["rows"].append({"p": r["project"], "doc": doc_ref(r["doc_key"], r.get("page_index")), "u": r.get("unit_id", ""),
                                  "a": r.get("aspect", ""), "v": r.get("voice", ""), "b": r.get("basis", ""), "d": r.get("decision", ""),
                                  "q": short(r.get("text", ""))})
        paras["available"] = True
    return {"results.json": results, "cell_history.json": history, "pets.json": pets, "paragraphs.json": paras}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cells", required=True)
    ap.add_argument("--pack", required=True)
    ap.add_argument("--history", required=True)
    ap.add_argument("--paragraphs")
    ap.add_argument("--status")
    ap.add_argument("--source", action="append", default=[])
    a = ap.parse_args()
    for name, data in build(a).items():
        with open(os.path.join(OUT, name), "w", encoding="utf-8") as fh:
            json.dump(data, fh, ensure_ascii=False, separators=(",", ":"))
            fh.write("\n")
        print("written site/assets/" + name, os.path.getsize(os.path.join(OUT, name)) // 1024, "KB")


if __name__ == "__main__":
    main()
