#!/usr/bin/env python3
"""Join sentences cut by a page break in existing unit files (MB, 22 Nov 2026), without re-extracting any text.

Applies unitise.join_page_breaks() to every <doc_key>.units.csv of a units directory: the unit at the end of a page that
does not finish its sentence is joined with the first unit of the next page when that starts in lower case (footnotes at
the foot of the page are skipped). The joined unit keeps the identifier, page and paragraph of its first part and gets
page_end; the identifier of the second part disappears. No other identifier changes.

--dry-run (default) only reports: how many joins, in how many documents, and which joined or absorbed units are in an
earlier sample or label file of the repository (data/units/*.csv with a unit_id column). --write writes the joined
files to --out (a new directory; the input is never changed) and data/units/PAGE_BREAK_JOINS_<date>.csv with one row per
join (doc_key, kept unit_id, absorbed unit_id, page, page_end, SHA-256 of the three texts). Unit texts stay outside the
repository. --write also rewrites the unit manifest of --date (from the latest one: units, words, units_sha256 and
page_breaks_joined per document). Candidates are rebuilt afterwards by select_candidates.py on the new directory.

usage: join_page_breaks.py --units <units dir> [--write --out <new units dir> --date 2026-11-22]
"""
import argparse
import collections
import csv
import glob
import hashlib
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
from unitise import join_page_breaks  # noqa: E402


def sha(t):
    return hashlib.sha256(t.encode("utf-8")).hexdigest()


def joins_of(rows):
    """rows of a units file -> (joined rows, list of joins)."""
    tup = [(r["page"], r["para"], int(re.search(r":s(\d+)$", r["unit_id"]).group(1)), r["text"], r.get("page_end") or r["page"]) for r in rows]
    new = join_page_breaks(tup)
    by_k = {t[2]: r for t, r in zip(tup, rows)}
    kept_k = {t[2] for t in new}
    out, joins = [], []
    absorbed = [t for t in tup if t[2] not in kept_k]
    for t in new:
        r = dict(by_k[t[2]])
        if t[4] != r["page"] and t[3] != r["text"]:
            nxt = next(a for a in absorbed if a[0] == t[4] and a[2] > t[2])
            joins.append({"kept": r["unit_id"], "absorbed": by_k[nxt[2]]["unit_id"], "page": r["page"], "page_end": t[4],
                          "kept_text_sha256": sha(r["text"]), "absorbed_text_sha256": sha(by_k[nxt[2]]["text"]), "joined_text_sha256": sha(t[3])})
        r.update(text=t[3], n_words=len(t[3].split()), page_end=t[4])
        out.append(r)
    return out, joins


def repo_unit_files():
    seen = collections.defaultdict(set)
    for f in sorted(glob.glob(os.path.join(ROOT, "data/units/*.csv"))):
        try:
            rd = csv.DictReader(open(f, encoding="utf-8"))
            if "unit_id" not in (rd.fieldnames or []):
                continue
            for r in rd:
                seen[r["unit_id"]].add(os.path.basename(f))
        except UnicodeDecodeError:
            continue
    return seen


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--units", required=True)
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--out")
    ap.add_argument("--date")
    a = ap.parse_args(argv)
    if a.write and (not a.out or not a.date or os.path.abspath(a.out) == os.path.abspath(a.units)):
        raise SystemExit("--write needs --out (a new directory) and --date")
    seen = repo_unit_files()
    all_joins, units_before, units_after, docs = [], 0, 0, 0
    per_doc = {}
    for f in sorted(glob.glob(os.path.join(a.units, "*.units.csv"))):
        key = os.path.basename(f)[: -len(".units.csv")]
        rows = list(csv.DictReader(open(f, encoding="utf-8")))
        out, joins = joins_of(rows)
        units_before += len(rows)
        units_after += len(out)
        docs += bool(joins)
        all_joins += [{"doc_key": key, **j} for j in joins]
        if a.write:
            os.makedirs(a.out, exist_ok=True)
            nf = os.path.join(a.out, os.path.basename(f))
            with open(nf, "w", newline="", encoding="utf-8") as fh:
                w = csv.DictWriter(fh, ["unit_id", "page", "para", "n_words", "text", "page_end"])
                w.writeheader()
                w.writerows({k: r.get(k, "") for k in w.fieldnames} for r in out)
            per_doc[key] = {"units": len(out), "words": sum(len(r["text"].split()) for r in out), "page_breaks_joined": len(joins),
                            "units_sha256": hashlib.sha256(open(nf, "rb").read()).hexdigest()}
    touched = {}
    for j in all_joins:
        for role in ("kept", "absorbed"):
            for fn in seen.get(j[role], ()):
                touched.setdefault(fn, []).append(f"{j[role]} ({role})")
    rep = {"documents": len(glob.glob(os.path.join(a.units, "*.units.csv"))), "documents_with_joins": docs, "joins": len(all_joins),
           "units_before": units_before, "units_after": units_after, "repository_files_touched": touched}
    if a.write:
        out_csv = os.path.join(ROOT, "data/units", f"PAGE_BREAK_JOINS_{a.date}.csv")
        with open(out_csv, "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, list(all_joins[0]) if all_joins else ["doc_key"])
            w.writeheader()
            w.writerows(all_joins)
        rep["record"] = out_csv
        # the unit manifest of the same date: units, words and file hashes of the joined files
        mf = sorted(glob.glob(os.path.join(ROOT, "data/units/UNITS_MANIFEST_*.csv")))[-1]
        raw = open(mf, "rb").read()
        nl = "\r\n" if b"\r\n" in raw else "\n"
        rd = csv.DictReader(open(mf, encoding="utf-8"))
        cols = rd.fieldnames + (["page_breaks_joined"] if "page_breaks_joined" not in rd.fieldnames else [])
        man = list(rd)
        missing = [m["doc_key"] for m in man if m["doc_key"] not in per_doc]
        if missing:
            raise SystemExit(f"units files missing for {missing[:5]}")
        for m in man:
            m.update({k: str(v) for k, v in per_doc[m["doc_key"]].items()})
        out_man = os.path.join(ROOT, "data/units", f"UNITS_MANIFEST_{a.date}.csv")
        with open(out_man, "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, cols, lineterminator=nl)
            w.writeheader()
            w.writerows(man)
        rep["manifest"] = out_man
    print(json.dumps(rep, indent=1))
    return rep


if __name__ == "__main__":
    main()
