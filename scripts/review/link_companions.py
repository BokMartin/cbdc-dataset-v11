#!/usr/bin/env python3
"""Companion documents and their links to the evidence documents of the same project and year (MB, 13 Nov 2026; ADR-005 section 9).

A COMPANION document is official and belongs to the project but is not evidence: it is not split into units and enters no talk
denominator. It is still listed and cited: for the project's status and timeline, and as the record of a legal act or decision that an
evidence document refers to. Each companion is linked to the evidence documents (KEEP / BORDERLINE) of the same project and the same
year; where the project has none in that year, to those of the nearest year, and the row says so.
`role` separates the kinds of companion: legal_text (acts, regulations, bills: the legislature or the government as law-maker, not the
maker of the CBDC speaking), status_or_news (press releases, statements, news), explainer (FAQ, web pages), speech, other.

Output: data/manifest/COMPANION_LINKS_<date>.csv (one row per companion document of the analytic frame).
usage: link_companions.py --tiers data/manifest/TIERS_<date>.csv --workbook <ALL documents xlsx> --date 2026-11-13
"""
import argparse, collections, csv, os, re
import openpyxl
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
ROLE = {"legislation": "legal_text", "regulation": "legal_text", "press_release": "status_or_news", "news": "status_or_news", "statement": "status_or_news", "faq": "explainer", "web_page": "explainer", "speech": "speech"}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--tiers", required=True); ap.add_argument("--workbook", required=True); ap.add_argument("--date", required=True); a = ap.parse_args()
    ws = openpyxl.load_workbook(a.workbook, read_only=True)["ALL_DOCUMENTS"]; R = list(ws.iter_rows(values_only=True)); h = R[0]; W = {r[h.index("id")]: dict(zip(h, r)) for r in R[1:]}
    T = [r for r in csv.DictReader(open(a.tiers, encoding="utf-8")) if r["tier"] != "out_of_frame"]
    ev = collections.defaultdict(lambda: collections.defaultdict(list))
    for r in T:
        if r["decision_v12"] in ("KEEP", "BORDERLINE") and r["year"].isdigit(): ev[r["project"]][int(r["year"])].append(r["id"])
    out = []
    for r in T:
        if r["decision_v12"] != "COMPANION": continue
        w = W.get(r["id"], {}); kind = w.get("kind") or ""; url = w.get("url") or ""; m = re.search(r'HYPERLINK\("([^"]+)"', str(url)); url = m.group(1) if m else url
        y = int(r["year"]) if r["year"].isdigit() else None; same = ev[r["project"]].get(y, []) if y else []; near = ""; link = same
        if not same and y and ev[r["project"]]:
            ny = min(ev[r["project"]], key=lambda k: (abs(k - y), k)); near = ny; link = ev[r["project"]][ny]
        out.append({"id": r["id"], "project": r["project"], "tier": r["tier"], "year": r["year"], "kind": kind, "role": ROLE.get(kind, "other"), "title": r["title"], "url": url, "decision_source": r["decision_source"],
                    "linked_evidence_ids": ";".join(link), "link_basis": "same year" if same else (f"nearest year {near}" if near != "" else "no dated evidence document in the project"), "n_linked": len(link)})
    out.sort(key=lambda o: (o["project"], o["year"], o["id"]))
    f = os.path.join(ROOT, "data/manifest", f"COMPANION_LINKS_{a.date}.csv")
    with open(f, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out[0].keys())); w.writeheader(); w.writerows(out)
    c = collections.Counter
    print(len(out), "companion documents in", len({o["project"] for o in out}), "projects;", dict(c(o["role"] for o in out)), ";", dict(c(o["link_basis"].split(" ")[0] for o in out)), "; by author", sum(o["decision_source"].startswith("author") for o in out))


if __name__ == "__main__": main()
