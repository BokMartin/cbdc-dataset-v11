#!/usr/bin/env python3
"""Manifest of the authors' MASTER document folder (Dropbox `Dizertace all the PDFs/CBDC_MASTER_v12/<CODE>/<file>`, EU members
under `EU`), built 9 Nov 2026 when every document we hold (v11 registry corpus + the 3 Norges Bank English editions + the 123
gap-check files fetched on 5 and 9 Nov) was consolidated into one folder (MB: "všech 700+ do 1 složky").

Inputs: the placement list written while copying (`MASTER_ITEMS_<date>.json`: id, source, project, fname, sha256, size,
registry_sha256, flag, v11_verdict) and the ALL-documents decision workbook (decision_v12 pre-fill and its source), joined on
registry doc_id or on SHA-256 (linked attachments on the parent candidate's filename stem).

Output columns: master_path · project · source · id · workbook_id · year · title · fname · ext · size · sha256 · registry_sha256 ·
hash_check · v11_verdict · decision_v12 (pre-fill, see build_all_documents_workbook.py) · decision_source · note.

usage: build_master_manifest.py --items data/manifest/MASTER_ITEMS_2026-11-10.json --workbook <ALL xlsx> --out data/manifest/MASTER_MANIFEST_2026-11-10.csv
(10 Nov 2026: the folder was completed with the remaining 246 gap-check files; candidate ids are CAND-<pre-screen row> = workbook ids.)
"""
import argparse, csv, json, os, collections
import openpyxl
EURO = {"AT", "BE", "CY", "DE", "EE", "ES", "FI", "FR", "GR", "HR", "IE", "IT", "LT", "LU", "LV", "MT", "NL", "PT", "SI", "SK"}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--items", required=True); ap.add_argument("--workbook", required=True); ap.add_argument("--out", required=True)
    a = ap.parse_args(); items = json.load(open(a.items))
    ws = openpyxl.load_workbook(a.workbook, read_only=True)["ALL_DOCUMENTS"]; rows = list(ws.iter_rows(values_only=True)); hdr = rows[0]
    W = [dict(zip(hdr, r)) for r in rows[1:]]; byid = {r["id"]: r for r in W}; bysha = {r["sha256"]: r for r in W if r["sha256"]}
    byfile = {os.path.basename((r["file"] or "").replace("\\", "/")): r for r in W if r["file"]}
    out = []
    for it in items:
        w = byid.get(it["id"]) or bysha.get(it["sha256"]) or byfile.get(it["fname"]); note = it.get("flag", "")
        if w is None and it.get("parallel_of"):  # issuer's English edition of a document already in the workbook (route B)
            w = byid.get(it["parallel_of"]); note = (note + "; " if note else "") + "issuer English edition of " + it["parallel_of"]
        if w is None and "__" in it["fname"]:  # linked attachment of an HTML candidate: parent has the same stem before the last "__"
            stem = it["fname"].rsplit("__", 1)[0]
            for k, r in byfile.items():
                if k.rsplit(".", 1)[0] == stem: w = r; note = (note + "; " if note else "") + "linked file of " + k; break
        folder = "EU" if it["project"] in EURO else it["project"]
        hc = "" if not it.get("registry_sha256") else ("identical" if it["registry_sha256"] == it["sha256"] else "DIFFERS")
        out.append({"master_path": f"CBDC_MASTER_v12/{folder}/{it['fname']}", "project": it["project"], "source": it["source"], "id": it["id"], "workbook_id": w["id"] if w else "",
                    "year": it.get("year", ""), "title": (w["title"] if w and w["title"] != w["id"] else it.get("title", "")) if (w and w["title"] != w["id"]) or it.get("title", "") != it["id"] else os.path.splitext(it["fname"])[0], "fname": it["fname"], "ext": os.path.splitext(it["fname"])[1].lstrip(".").lower(),
                    "size": it["size"], "sha256": it["sha256"], "registry_sha256": it.get("registry_sha256", ""), "hash_check": hc, "v11_verdict": it.get("v11_verdict", ""),
                    "decision_v12": (w["decision_v12"] if w else ""), "decision_source": (w["decision_source"] if w else ""), "note": note})
    out.sort(key=lambda r: r["master_path"])
    with open(a.out, "w", newline="", encoding="utf-8") as f:
        wr = csv.DictWriter(f, fieldnames=list(out[0].keys())); wr.writeheader(); wr.writerows(out)
    c = collections.Counter(r["decision_v12"] or "undecided" for r in out)
    print(a.out, len(out), "files;", sum(r["size"] for r in out) // 1_000_000, "MB;", dict(c), "; unmatched:", sum(1 for r in out if not r["workbook_id"]))


if __name__ == "__main__": main()
