"""Registry loader: the frozen REGISTRY_v2_2.csv plus dated amendments applied in order (data/registry/REGISTRY_AMENDMENT_*.csv and
SOURCE_URL_AMENDMENT_*.csv). The frozen file is never edited; every change is a row with old value, new value, basis and date.
"""
import csv, glob, os
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def load_registry(root=ROOT, apply_amendments=True):
    R = list(csv.DictReader(open(os.path.join(root, "data/registry/REGISTRY_v2_2.csv"), encoding="utf-8")))
    if not apply_amendments: return R
    by = {r["doc_id"]: r for r in R}; applied = []
    for f in sorted(glob.glob(os.path.join(root, "data/registry/REGISTRY_AMENDMENT_*.csv"))):
        for a in csv.DictReader(open(f, encoding="utf-8")):
            r = by.get(a["doc_id"])
            if r is None: continue
            r[a["field"]] = a["new"]; r.setdefault("amended", ""); r["amended"] += f"{a['field']}@{a['date']};"; applied.append((a["doc_id"], a["field"]))
    for f in sorted(glob.glob(os.path.join(root, "data/registry/SOURCE_URL_AMENDMENT_*.csv"))):
        for a in csv.DictReader(open(f, encoding="utf-8")):
            r = by.get(a["doc_id"])
            if r is not None and not r.get("url") and a["url_kind"] != "not_found": r["url"] = a["url"]; r["url_amended"] = a["confidence"]; applied.append((a["doc_id"], "url"))
    # dated additions (e.g. issuer English editions): full registry rows derived from the addition file
    for f in sorted(glob.glob(os.path.join(root, "data/registry/REGISTRY_ADDITIONS_*.csv"))):
        for a in csv.DictReader(open(f, encoding="utf-8")):
            if a["doc_id"] in by: continue
            row = {k: "" for k in R[0].keys()}
            row.update({"doc_id": a["doc_id"], "jur": a["jur"], "fname": a["fname"], "year": a["year"], "title": a["title"], "url": a["url"], "language": a["language"], "sha256": a["sha256"],
                        "core_v1": "KEEP" if "2018" not in a["doc_id"] else "BORDERLINE", "doc_kind": "progress_report" if "2018" not in a["doc_id"] else "other", "notes": a["basis"],
                        "amended": f"added@{a['date']};", "route": a["route"], "parallel_of": a["parallel_of"]})
            R.append(row); by[a["doc_id"]] = row
    return R


if __name__ == "__main__":
    R = load_registry(); core = [r for r in R if r["core_v1"] or r["core_v2"]]
    import collections; print(len(R), "documents;", len(core), "core;", "languages:", dict(collections.Counter(r["language"] for r in core)), "core without url:", sum(1 for r in core if not r["url"]))
