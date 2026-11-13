#!/usr/bin/env python3
"""Supplement to the human judgement of the translation benchmark: the privacy sentences the automatic matcher could NOT pair.

The judgement registered on 11 Nov 2026 covers matched pairs only (163 of 247 privacy sentences of the issuers' English editions).
The independent audit of 13 Nov (item 12) pointed out that the 84 unmatched sentences are the ones most likely to hide a loss.
This script draws a simple random sample of them (default 30, seed 20261113) and shows, for each, the three most similar sentences of
the machine translation (same TF-IDF matcher as benchmark_translations.py). The judge says which candidate, if any, renders the
sentence, and codes that candidate with the same codes as the main judgement.
Reported (fixed before judging): share of sampled sentences with a rendering among the three candidates, with a 95 % Wilson interval,
and S / W / X / M among those; rows with no rendering are listed and are NOT counted as omissions: three candidates cannot show that
a sentence is absent from the translation (the English edition may also contain text the original does not have). Combined with the
main judgement by stratum weights (matched 163, unmatched 84) only as a lower bound on the share rendered with the same meaning.
The sheet is added to the judge's workbook; the key (document, similarities, SHA-256 of the sentence) goes to the repository.

usage: build_unmatched_sample.py --pairs <pairs json> --workbook <judgement xlsx to extend> --out <xlsx> --date 2026-11-13 [--n 30]
"""
import argparse, csv, hashlib, json, os, random, subprocess, sys
import openpyxl
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.worksheet.datavalidation import DataValidation
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE)); sys.path.insert(0, HERE)
import benchmark_translations as bt
WRAP = Alignment(wrap_text=True, vertical="top")


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--pairs", required=True); ap.add_argument("--workbook", required=True); ap.add_argument("--out", required=True); ap.add_argument("--date", required=True)
    ap.add_argument("--n", type=int, default=30); ap.add_argument("--seed", type=int, default=20261113); a = ap.parse_args()
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    un = []; tot = 0
    for p in json.load(open(a.pairs)):
        T = bt.clean_t(open(p["translation"], encoding="utf-8").read())
        E = subprocess.run(["pdftotext", "-enc", "UTF-8", p["english_pdf"], "-"], capture_output=True).stdout.decode("utf-8", "replace").replace("\f", "\n\n")
        St, Se = bt.sents(T), bt.sents(E); vec = TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True, stop_words="english").fit(St + Se); Mt = vec.transform(St)
        pe = [s for s in Se if bt.PRIV.search(s)]; tot += len(pe); C = cosine_similarity(vec.transform(pe), Mt)
        for i, s in enumerate(pe):
            top = sorted(range(len(St)), key=lambda j: -C[i, j])[:3]
            # same boundary as the registered judgement sample of 11 Nov, which was drawn on similarities rounded to two decimals (163 matched, 84 unmatched; one pair at 0.3476 counts as matched there)
            if round(float(C[i, top[0]]), 2) < 0.35: un.append({"pair": p["label"], "E": s, "cands": [(St[j], round(float(C[i, j]), 2)) for j in top]})
    rnd = random.Random(a.seed); un.sort(key=lambda u: (u["pair"], u["E"])); sample = rnd.sample(un, min(a.n, len(un))); rnd.shuffle(sample)
    wb = openpyxl.load_workbook(a.workbook); ins = wb["INSTRUCTIONS"]
    for t in ["", f"ADDED {a.date}: sheet UNMATCHED (after the independent audit). The automatic matcher found no partner for {len(un)} of the {tot} privacy sentences of the English editions; sheet JUDGE cannot say anything about them. UNMATCHED shows a random sample of {len(sample)} of these sentences (E), each with the three most similar sentences of the machine translation (T1, T2, T3).",
              "What to do on UNMATCHED. In 'which candidate' choose 1, 2 or 3 if that candidate renders the E sentence (same content, possibly split or worded differently), or 0 if none of the three does. If you chose 1, 2 or 3, code that candidate against E with the same codes as on sheet JUDGE (S, W, X, M). If you chose 0, leave the code empty.",
              "A 0 does not mean the translation omitted the sentence: you see only three candidates, and the English edition can contain text the original does not have. Zeros are reported as 'no rendering among three candidates', not as omissions."]:
        ins.append([t]); ins.cell(ins.max_row, 1).alignment = WRAP
    ws = wb.create_sheet("UNMATCHED"); cols = ["#", "document", "issuer English edition (E)", "T1", "T2", "T3", "which candidate (1 / 2 / 3 / 0 = none)", "CODE (S / W / X / M)", "note (optional)"]; ws.append(cols); key = []
    for n, u in enumerate(sample, 1):
        ws.append([n, u["pair"], u["E"]] + [c[0] for c in u["cands"]] + ["", "", ""])
        for c in (7, 8): ws.cell(n + 1, c).fill = PatternFill("solid", fgColor="FFF2CC")
        key.append({"n": n, "pair": u["pair"], "similarity_1": u["cands"][0][1], "similarity_2": u["cands"][1][1], "similarity_3": u["cands"][2][1], "sha256_E": hashlib.sha256(u["E"].encode("utf-8")).hexdigest()})
    for c, wd in enumerate([4, 20, 55, 45, 45, 45, 14, 12, 30], 1): ws.column_dimensions[ws.cell(1, c).column_letter].width = wd
    for c in range(1, len(cols) + 1): ws.cell(1, c).font = Font(bold=True); ws.cell(1, c).fill = PatternFill("solid", fgColor="DDDDDD")
    for r in ws.iter_rows():
        for c in r: c.alignment = WRAP
    for col, vals in (("G", "1,2,3,0"), ("H", "S,W,X,M")):
        dv = DataValidation(type="list", formula1=f'"{vals}"', allow_blank=True); ws.add_data_validation(dv); dv.add(f"{col}2:{col}{len(sample) + 1}")
    ws.freeze_panes = "D2"; wb.save(a.out)
    with open(os.path.join(ROOT, "data/translation/benchmark", f"JUDGEMENT_KEY_UNMATCHED_{a.date}.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(key[0].keys())); w.writeheader(); w.writerows(key)
    import collections
    print("privacy sentences", tot, "unmatched", len(un), "sampled", len(sample), dict(collections.Counter(u["pair"] for u in sample)))


if __name__ == "__main__": main()
