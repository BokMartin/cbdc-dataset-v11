#!/usr/bin/env python3
"""Download manifest of the gap-check candidates (one row per candidate URL of GAP_CHECK_PRESCREEN_2026-11-03.csv, plus one row per
PDF linked from a fetched HTML page), built from the download evidence written while fetching.

Two download rounds:
  5 and 9 Nov 2026  126 blocked / low-confidence candidates -> MANUAL_DOWNLOADS_2026-11-09.csv (kept as is, rows copied over);
                    files in Dropbox `new cbdc files/<CODE>/` and, since 9 Nov, in `Dizertace all the PDFs/CBDC_MASTER_v12/<CODE>/`.
  9 and 10 Nov 2026 the remaining 257 candidates with working links (MB: "pro jistotu chci mít všechny na Dropboxu"), fetched in the
                    Claude desktop browser pane (fetch in page context; SHA-256 computed in the page or, for 4 http-only kremlin.ru
                    pages, in the container; files moved to CBDC_MASTER_v12/<CODE>/ with hash check). Evidence in
                    data/manifest/evidence/gap_downloads_2026-11-10/: dl_plan2.json (the 257 candidates, with filenames),
                    results2.jsonl (fetch log: [i, status, size, content_type, sha256, fname, note]; last line per id is final),
                    placed_gap2.json (what was placed, with the hash of the kept file).

Columns: i (the `row` of GAP_CHECK_PRESCREEN_2026-11-03.csv, 1-based = the CAND-<i> id of the all-documents workbook; "<i>-pdf" = PDF linked
from that candidate's HTML page) · project · date ·
title · url (the candidate's URL as pre-screened; a replaced URL is in `note`) · status (in_dropbox / not_retrieved) · fname · dropbox_path
(relative to Dropbox root) · sha256 (of the kept file) · size · content_type (pdf / html / docx / rendered_html for a JS-rendered page saved
as DOM) · pages (PDF) · type_flag · note.

usage: build_manual_downloads.py --gap2 /path/to/gap2 --out data/manifest/MANUAL_DOWNLOADS_2026-11-10.csv
"""
import argparse, csv, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
EV = os.path.join(ROOT, "data/manifest/evidence/gap_downloads_2026-11-10")
EURO = {"AT", "BE", "CY", "DE", "EE", "ES", "FI", "FR", "GR", "HR", "IE", "IT", "LT", "LU", "LV", "MT", "NL", "PT", "SI", "SK"}
FIELDS = ["i", "project", "date", "title", "url", "status", "fname", "dropbox_path", "sha256", "size", "content_type", "pages", "type_flag", "note"]


def pages_of(path):
    try:
        import pypdf
        return len(pypdf.PdfReader(path).pages)
    except Exception:
        return ""


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--gap2", required=True, help="local folder holding the fetched files as <CODE>/<fname>"); ap.add_argument("--out", required=True)
    ap.add_argument("--prev", default=os.path.join(ROOT, "data/manifest/MANUAL_DOWNLOADS_2026-11-09.csv"))
    a = ap.parse_args()
    C = list(csv.DictReader(open(os.path.join(ROOT, "data/manifest/GAP_CHECK_PRESCREEN_2026-11-03.csv"), encoding="utf-8")))
    byurl = {(r["project"], r["url"]): int(r["row"]) for r in C}
    plan = {str(x["i"]): x for x in json.load(open(os.path.join(EV, "dl_plan2.json")))["plan"]}
    placed = json.load(open(os.path.join(EV, "placed_gap2.json")))
    R = {}
    for l in open(os.path.join(EV, "results2.jsonl")):
        x = json.loads(l); R[str(x[0])] = x
    rows = list(csv.DictReader(open(a.prev, encoding="utf-8")))  # round 1 (its 5 failures were retried in round 2 and are replaced below)
    for r in rows:  # round 1: re-key to the pre-screen row (the old `i` was the position in the 128-row download list) and point at the master folder
        r["i"] = str(byurl[(r["project"], r["url"])]) + ("-pdf" if "linked file" in r["title"] else "")
        if r["status"] == "in_dropbox" and r["dropbox_path"].startswith("new cbdc files"):
            r["dropbox_path"] = "Dizertace all the PDFs/CBDC_MASTER_v12/" + r["dropbox_path"].replace("\\", "/").split("/", 1)[1]
    for k, x in sorted(plan.items(), key=lambda kv: int(kv[0])):
        n = byurl[(x["project"], x["url"])]; res = R.get(k); e = placed.get(k)
        base = {"i": n, "project": x["project"], "date": x["date"], "title": x["title"], "url": x["url"]}
        if e:
            folder = "EU" if e["project"] in EURO else e["project"]; local = os.path.join(a.gap2, folder, e["fname"]); ext = e["fname"].rsplit(".", 1)[-1].lower()
            ctype = "rendered_html" if (res and res[1] == "RENDERED") else ext
            note = e.get("note", "") or ""
            if res and len(res) > 6 and res[6] and k == "163": note = (note + "; " if note else "") + res[6]
            flag = "docx" if ext == "docx" else ("rendered_page" if ctype == "rendered_html" else ("dynamic_html" if "dynamic HTML" in note else ""))
            rows.append({**base, "status": "in_dropbox", "fname": e["fname"], "dropbox_path": f"Dizertace all the PDFs/CBDC_MASTER_v12/{folder}/{e['fname']}", "sha256": e["sha256"], "size": e["size"],
                         "content_type": ctype, "pages": pages_of(local) if ext == "pdf" else "", "type_flag": flag, "note": note})
            lk = placed.get(k + "-pdf")
            if lk:  # PDF linked from the HTML page
                local2 = os.path.join(a.gap2, folder, lk["fname"]); lr = R.get(k + "-pdf", [])
                rows.append({**base, "i": f"{n}-pdf", "title": x["title"] + " (linked file)", "status": "in_dropbox", "fname": lk["fname"], "dropbox_path": f"Dizertace all the PDFs/CBDC_MASTER_v12/{folder}/{lk['fname']}",
                             "sha256": lk["sha256"], "size": lk["size"], "content_type": "pdf", "pages": pages_of(local2), "type_flag": "linked_file", "note": ("linked from " + lr[6]) if len(lr) > 6 else "PDF linked from the HTML page"})
        else:
            note = res[2] if res and res[1] == "ERR" else "not fetched"
            prev = [r for r in rows if r["i"] == str(n) and r["status"] == "not_retrieved"]
            if prev: note = "retried 9 Nov: " + note + " | 5 Nov: " + prev[0]["note"]; rows.remove(prev[0])
            rows.append({**base, "status": "not_retrieved", "fname": "", "dropbox_path": "", "sha256": "", "size": "", "content_type": "", "pages": "", "type_flag": "", "note": note})
    with open(a.out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS, extrasaction="ignore"); w.writeheader(); w.writerows(rows)
    import collections
    print(a.out, len(rows), "rows;", dict(collections.Counter(r["status"] for r in rows)), "; not retrieved:", [r["i"] for r in rows if r["status"] != "in_dropbox"])


if __name__ == "__main__": main()
