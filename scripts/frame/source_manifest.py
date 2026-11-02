#!/usr/bin/env python3
"""Production source manifest (ADR-001 D2): ONE table of every document that may serve as evidence, replacing "core_v1 + core_v2
+ ad-hoc additions". Built from the frozen registry + dated amendments (registry.py), the dated additions (route-B English
editions), the reuse-terms tables and the language ledger routes. Nothing is edited by hand: re-run to regenerate.

Columns: doc_id, project (analytic project code; euro-area members → EU), jur, year, title, doc_kind, verdict (KEEP/BORDERLINE),
staff_research, language, route (A English original · B issuer English edition · C checked translation · D machine/provisional ·
B_available = issuer English edition exists but is not yet ingested), parallel_of, url, url_amended, sha256, licence_class,
in_frame_43, provenance_note, amended.
Output: data/manifest/SOURCE_MANIFEST_DRAFT.csv + SOURCE_MANIFEST_DRAFT.json (counts). Frozen at Phase 3 as SOURCE_MANIFEST_v1.
"""
import csv, json, os, sys, collections, datetime as dt
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE)); sys.path.insert(0, HERE)
from registry import load_registry

EURO = {"AT", "BE", "CY", "DE", "EE", "ES", "FI", "FR", "GR", "HR", "IE", "IT", "LT", "LU", "LV", "MT", "NL", "PT", "SI", "SK"}
B_AVAILABLE = {"RU_Russia_concept_08042021": "Bank of Russia English edition 'Digital Ruble Concept' (LANGUAGE_LEDGER #4)"}
PAIR_OF = {"JP_BoJ_Pilot_JP": "JP_BoJ_Pilot_EN"}  # original-language pair of an English core document already in the corpus
NOTE_FIELDS = ("notes",)


def main():
    R = load_registry(ROOT); frame = {r["project"]: r for r in csv.DictReader(open(os.path.join(ROOT, "data/frame/projects.csv"), encoding="utf-8"))}
    lic = {r["doc_id"]: r for r in csv.DictReader(open(os.path.join(ROOT, "data/registry/DOC_LICENCES_2026-11-02.csv"), encoding="utf-8"))}
    lic_inst = {r["jur"]: r for r in csv.DictReader(open(os.path.join(ROOT, "data/registry/LICENCES_BY_INSTITUTION_2026-11-02.csv"), encoding="utf-8"))}
    adds = list(csv.DictReader(open(os.path.join(ROOT, "data/registry/REGISTRY_ADDITIONS_2026-11-02.csv"), encoding="utf-8")))
    rows = []
    for r in R:
        if not (r["core_v1"] or r["core_v2"]): continue
        p = "EU" if r["jur"] in EURO else r["jur"]; lang = r["language"]
        route = "A" if lang == "en" else ("B_available" if r["doc_id"] in B_AVAILABLE else "D")
        if any(a["parallel_of"] == r["doc_id"] for a in adds) or r["doc_id"] in PAIR_OF: route = "B_pair_original"
        rows.append({"doc_id": r["doc_id"], "project": p, "jur": r["jur"], "year": r["year"], "title": r["title"] or r["fname"], "doc_kind": r["doc_kind"], "verdict": r["core_v1"] or r["core_v2"],
                     "staff_research": r["staff_research"], "language": lang, "route": route, "parallel_of": PAIR_OF.get(r["doc_id"], ""), "url": r["url"], "url_amended": r.get("url_amended", ""), "sha256": r["sha256"],
                     "licence_class": lic.get(r["doc_id"], {}).get("licence_class", lic_inst.get(r["jur"], {}).get("licence_class", "")), "in_frame_43": frame.get(p, {}).get("retail_candidate", "False"),
                     "provenance_note": (r.get("notes", "") if r.get("amended", "") and "notes@" in r.get("amended", "") else "") + (B_AVAILABLE.get(r["doc_id"], "")), "amended": r.get("amended", "")})
    for a in adds:
        rows.append({"doc_id": a["doc_id"], "project": a["jur"], "jur": a["jur"], "year": a["year"], "title": a["title"], "doc_kind": "", "verdict": "KEEP" if "2018" not in a["doc_id"] else "BORDERLINE",
                     "staff_research": "", "language": a["language"], "route": a["route"], "parallel_of": a["parallel_of"], "url": a["url"], "url_amended": "addition", "sha256": a["sha256"],
                     "licence_class": lic_inst.get(a["jur"], {}).get("licence_class", ""), "in_frame_43": frame.get(a["jur"], {}).get("retail_candidate", "False"), "provenance_note": a["basis"], "amended": f"added@{a['date']};"})
    rows.sort(key=lambda x: (x["project"], x["year"], x["doc_id"]))
    os.makedirs(os.path.join(ROOT, "data/manifest"), exist_ok=True)
    with open(os.path.join(ROOT, "data/manifest/SOURCE_MANIFEST_DRAFT.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    c = lambda k: dict(collections.Counter(x[k] for x in rows))
    evid = [x for x in rows if x["route"] != "B_pair_original"]
    summary = {"generated_utc": dt.datetime.now(dt.timezone.utc).isoformat(), "n_rows": len(rows), "n_evidence_documents": len(evid), "n_projects": len({x["project"] for x in rows}),
               "by_route": c("route"), "by_language": c("language"), "by_verdict": c("verdict"), "by_licence": c("licence_class"), "in_frame_43": sum(1 for x in evid if x["in_frame_43"] == "True"),
               "non_english_in_frame_43": sorted(f"{x['project']}:{x['doc_id']}" for x in evid if x["in_frame_43"] == "True" and x["route"] in ("D", "B_available")),
               "missing_url": [x["doc_id"] for x in rows if not x["url"]], "missing_sha256": [x["doc_id"] for x in rows if not x["sha256"]],
               "gap_check": "pending: uniform authority/content rule (ADR D1) to be applied per project before freeze", "status": "DRAFT; frozen at Phase 3 as SOURCE_MANIFEST_v1"}
    json.dump(summary, open(os.path.join(ROOT, "data/manifest/SOURCE_MANIFEST_DRAFT.json"), "w"), indent=1); print(json.dumps(summary, indent=1))


if __name__ == "__main__": main()
