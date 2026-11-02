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
    return R


if __name__ == "__main__":
    R = load_registry(); core = [r for r in R if r["core_v1"] or r["core_v2"]]
    import collections; print(len(R), "documents;", len(core), "core;", "languages:", dict(collections.Counter(r["language"] for r in core)), "core without url:", sum(1 for r in core if not r["url"]))
