#!/usr/bin/env python3
"""Deterministic repair of the unit manifests after audit A4 (17 Nov 2026, F03 and F09). No text is re-extracted and no unit changes.

1. Same-text duplicates: every group of documents with one text_sha256 must be resolved by a row in data/manifest/EDITION_LINKS.csv
   (original_id = the copy that is dropped, english_id = the copy that is read). The dropped copy leaves the unit manifest and the
   candidates file, enters UNITS_NOT_UNITISED with the reason, and gets same_publication_as in the tiers file. Unresolved group = error.
2. One header source: issuer, issuer_type and kind of every document are taken from the issuer ledger (data/manifest/ISSUERS_*.csv),
   which is the file the authors review; the unit manifest no longer carries its own guess.
Writes UNITS_MANIFEST_<date>.csv, CANDIDATES_<date>.csv, UNITS_NOT_UNITISED_<date>.csv, TIERS_<date>.csv. With --units, moves the
unit files of dropped copies to <units>/_dropped_duplicates/.

usage: rebuild_unit_manifest.py --date 2026-11-17 [--units <units dir>]
"""
import argparse, collections, csv, glob, os, shutil, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def latest(pat, before=None):
    fs = sorted(f for f in glob.glob(os.path.join(ROOT, pat)) if before is None or os.path.basename(f) < before)
    return fs[-1]


def rd(p): return list(csv.DictReader(open(p, encoding="utf-8")))


def wr(p, rows, cols):
    with open(p, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols); w.writeheader(); w.writerows(rows)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--date", required=True); ap.add_argument("--units"); a = ap.parse_args()
    src = lambda stem: latest(f"{stem}_*.csv", before=os.path.basename(stem) + f"_{a.date}.csv")
    U = rd(src("data/units/UNITS_MANIFEST")); C = rd(src("data/units/CANDIDATES")); NU = rd(src("data/units/UNITS_NOT_UNITISED")); T = rd(src("data/manifest/TIERS"))
    link = {r["original_id"]: r["english_id"] for r in rd(os.path.join(ROOT, "data/manifest/EDITION_LINKS.csv"))}
    led = {r["id"]: r for r in rd(latest("data/manifest/ISSUERS_2*.csv"))}
    groups = collections.defaultdict(list)
    for r in U: groups[r["text_sha256"]].append(r["id"])
    drop = {}
    for h, ids in groups.items():
        if len(ids) < 2: continue
        keep = [i for i in ids if i not in link]
        if len(keep) != 1 or any(link[i] != keep[0] for i in ids if i in link):
            sys.exit(f"same text, not resolved in EDITION_LINKS.csv: {ids}")
        for i in ids:
            if i in link: drop[i] = keep[0]
    keys = {r["id"]: r["doc_key"] for r in U}
    U2 = [dict(r) for r in U if r["id"] not in drop]
    changed = 0
    for r in U2:
        l = led.get(r["id"])
        if not l: sys.exit(f"no issuer ledger row for {r['id']}")
        for k in ("issuer", "issuer_type", "kind"):
            if r[k] != l[k]: r[k] = l[k]; changed += 1
    C2 = [r for r in C if r["doc_key"] not in {keys[i] for i in drop}]
    NU2 = NU + [{"id": i, "project": next(r["project"] for r in U if r["id"] == i), "reason": f"same publication as {k} (identical text; read there)"} for i, k in drop.items()]
    for r in T:
        if r["id"] in drop: r["same_publication_as"] = drop[r["id"]]
    wr(os.path.join(ROOT, f"data/units/UNITS_MANIFEST_{a.date}.csv"), U2, list(U[0])); wr(os.path.join(ROOT, f"data/units/CANDIDATES_{a.date}.csv"), C2, list(C[0]))
    wr(os.path.join(ROOT, f"data/units/UNITS_NOT_UNITISED_{a.date}.csv"), NU2, list(NU[0])); wr(os.path.join(ROOT, f"data/manifest/TIERS_{a.date}.csv"), T, list(T[0]))
    if a.units:
        d = os.path.join(a.units, "_dropped_duplicates"); os.makedirs(d, exist_ok=True)
        for i in drop:
            for f in glob.glob(os.path.join(a.units, keys[i] + ".*.csv")): shutil.move(f, os.path.join(d, os.path.basename(f)))
    print(f"documents {len(U)} -> {len(U2)}; dropped {drop}; header fields aligned with the issuer ledger: {changed}; units {sum(int(r['units']) for r in U2)}; "
          f"candidates D/N/R {sum(int(r['D']) for r in C2)}/{sum(int(r['N']) for r in C2)}/{sum(int(r['R']) for r in C2)}")


if __name__ == "__main__": main()
