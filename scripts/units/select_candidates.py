#!/usr/bin/env python3
"""Candidate units for the relevance step (L1) of the privacy-talk instrument, with a built-in recall sample.

Every unit gets one stratum:
  D  dictionary hit: the unit matches the BROAD privacy dictionary (bracketed source terms and translator notes ignored)
  N  neighbour: not a hit, but the unit directly before or after a hit in the same paragraph (statements often continue across sentences)
  R  random control: none of the above, drawn by hash rank: SHA-256(seed | unit_id) below the sampling rate (default 5 %)
  -  not sent to the model
  X  excluded from candidates and from every denominator: fragments of fewer than 4 words (headings, menu items, table cells) and
     web-site boilerplate (privacy policy / privacy notice / cookies links, which would otherwise count as dictionary hits)
L1 classifies D, N and R units. Precision is measured on D and N; recall of the candidate rule is estimated from R (relevant units
the dictionary and its neighbours would have missed), so "the project says little" is a measured statement, not an assumption.
An encoder stratum (top-ranked units of the validated encoder) is to be added as E when the encoder run on these units exists.
Output outside the repository: <units dir>/<doc_key>.candidates.csv (unit_id, stratum). Repository: per-document counts only.

usage: select_candidates.py --units <units dir> --date 2026-11-12 [--rate 0.05] [--seed talk-v13-2026-11-12]
"""
import argparse, csv, glob, hashlib, os, re, collections
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
BROAD = re.compile(r"\b(privacy|anonym\w*|pseudonym\w*|personal (data|information)|data protection|confidential\w*|identif\w*|identit(y|ies)|trac(e|ed|ing|eab\w*)|surveillance|kyc|know[- ]your[- ]customer|due diligence|money[- ]laundering|data minimi[sz]\w*|consent\w*)\b", re.I)


BOILER = re.compile(r"\b(cookies?|privacy (policy|notice|statement|settings)|terms (of use|and conditions)|all rights reserved|subscribe|newsletter|follow us|site ?map)\b", re.I)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--units", required=True); ap.add_argument("--date", required=True); ap.add_argument("--rate", type=float, default=0.05); ap.add_argument("--seed", default="talk-v13-2026-11-12")
    a = ap.parse_args(); rows = []; tot = collections.Counter()
    for f in sorted(glob.glob(os.path.join(a.units, "*.units.csv"))):
        U = list(csv.DictReader(open(f, encoding="utf-8"))); key = os.path.basename(f)[:-10]
        hit = [bool(BROAD.search(re.sub(r"\[[^\]\n]{1,120}\]", " ", u["text"]))) for u in U]; st = []
        for i, u in enumerate(U):
            same = lambda j: 0 <= j < len(U) and U[j]["page"] == u["page"] and U[j]["para"] == u["para"]
            if int(u["n_words"]) < 4 or (int(u["n_words"]) < 12 and BOILER.search(u["text"])): s = "X"
            elif hit[i]: s = "D"
            elif (same(i - 1) and hit[i - 1] and int(U[i - 1]["n_words"]) >= 4) or (same(i + 1) and hit[i + 1] and int(U[i + 1]["n_words"]) >= 4): s = "N"
            elif int(hashlib.sha256(f"{a.seed}|{u['unit_id']}".encode()).hexdigest()[:8], 16) / 0xFFFFFFFF < a.rate: s = "R"
            else: s = "-"
            st.append(s)
        with open(os.path.join(a.units, key + ".candidates.csv"), "w", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh); w.writerow(["unit_id", "stratum"]); w.writerows((u["unit_id"], s) for u, s in zip(U, st) if s in "DNR")
        c = collections.Counter(st); tot.update(c); rows.append({"doc_key": key, "units": len(U), "D": c["D"], "N": c["N"], "R": c["R"], "not_sent": c["-"], "excluded_X": c["X"]})
    with open(os.path.join(ROOT, "data/units", f"CANDIDATES_{a.date}.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    print(len(rows), "documents;", dict(tot), "; to classify:", tot["D"] + tot["N"] + tot["R"])


if __name__ == "__main__": main()
