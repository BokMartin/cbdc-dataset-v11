#!/usr/bin/env python3
"""Candidate units for the relevance step (L1) of the privacy-talk instrument, with a built-in recall sample.

Every unit gets one stratum:
  D  dictionary hit: the unit matches the BROAD privacy dictionary (bracketed source terms and translator notes ignored)
  N  neighbour: not a hit, but the unit directly before or after a hit in the same paragraph (statements often continue across sentences)
  R  random control: none of the above, drawn by hash rank: SHA-256(seed | unit_id) below the sampling rate (default 5 %)
  -  not sent to the model
  X  excluded from candidates and from every denominator: fragments of fewer than 4 words that are not dictionary hits (headings, menu
     items, table cells) and web-site boilerplate links (privacy policy / cookies) that are not sentences; see excluded()
L1 classifies D, N and R units. Precision is measured on D and N; recall of the candidate rule is estimated from R (relevant units
the dictionary and its neighbours would have missed), so "the project says little" is a measured statement, not an assumption.
An encoder stratum (top-ranked units of the validated encoder) is to be added as E when the encoder run on these units exists.
Output outside the repository: <units dir>/<doc_key>.candidates.csv (unit_id, stratum). Repository: per-document counts only.

usage: select_candidates.py --units <units dir> --date 2026-11-12 [--rate 0.05] [--seed talk-v13-2026-11-12]
"""
import argparse, csv, glob, hashlib, os, re, collections
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
BROAD = re.compile(r"\b(privacy\w*|anonym\w*|pseudonym\w*|unlinkab\w*|personal (data|information)|(user|customer|transaction|payment|payer|payee|holder)s?[’']? (data|information)|data (protection|sharing|collection|retention|access)|retention period|confidential\w*|identif\w*|identit(y|ies)|trac(e|ed|ing|eab\w*)|surveillance|monitor(ing|ed|s)? (of )?(transactions?|payments?|users?)|transaction monitoring|profiling|kyc|aml|cft|know[- ]your[- ]customer|due diligence|money[- ]laundering|data minimi[sz]\w*|consent\w*|encrypt\w*|zero[- ]knowledge|blind signatures?|(cannot|can not|not be able to|will not|does not|do not|unable to) (see|view|access|link))\b", re.I)  # v2, 13 Nov 2026: audit item 4 (AML/CFT, monitoring, retention, encryption, zero-knowledge, "cannot see"; "privacyenhancing" without hyphen)


BOILER = re.compile(r"\b(cookies?|privacy (policy|notice|statement|settings)|terms (of use|and conditions)|all rights reserved|subscribe|newsletter|follow us|site ?map)\b", re.I)


def excluded(text, n_words, hit):
    """Stratum X (v2, 13 Nov 2026, audit item 4): a fragment of fewer than 4 words is excluded only if it is not a dictionary hit
    ("No identification required." stays); web-site boilerplate only if it is at most 5 words or does not end like a sentence
    ("Our privacy policy forbids sharing customer data." stays)."""
    if n_words < 4 and not hit: return True
    return bool(BOILER.search(text)) and (n_words <= 5 or not re.search(r"[.!?][\"'”’)\]]*$", text.strip()))


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--units", required=True); ap.add_argument("--date", required=True); ap.add_argument("--rate", type=float, default=0.05); ap.add_argument("--seed", default="talk-v13-2026-11-12")  # the seed keeps its first date on purpose: a unit id keeps its control status across re-runs
    a = ap.parse_args(); rows = []; tot = collections.Counter()
    for f in sorted(glob.glob(os.path.join(a.units, "*.units.csv"))):
        U = list(csv.DictReader(open(f, encoding="utf-8"))); key = os.path.basename(f)[:-10]
        hit = [bool(BROAD.search(re.sub(r"\[[^\]\n]{1,120}\]", " ", u["text"]))) for u in U]; st = []
        for i, u in enumerate(U):
            same = lambda j: 0 <= j < len(U) and U[j]["page"] == u["page"] and U[j]["para"] == u["para"]
            if excluded(u["text"], int(u["n_words"]), hit[i]): s = "X"
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
