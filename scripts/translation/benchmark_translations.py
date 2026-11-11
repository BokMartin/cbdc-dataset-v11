#!/usr/bin/env python3
"""Translation-quality benchmark: machine translation of an original vs the issuer's own English edition of the same document.

For the route-B benchmark pairs (data/translation/ROUTE_B_PAIRS.csv, benchmark = yes) the original was translated with the same
prompt, model and run as the route-D documents. This script compares that translation (T) with the issuer's English edition (E).
The comparison is deterministic (no model), document-level, and aimed at what the measurement uses:

 1 length          words in T and E (an English edition is sometimes edited, not a literal translation; a large gap is reported)
 2 chrF            character n-gram F-score of T against E (sacrebleu, whole document as one segment): lexical closeness
 3 key terms       frequency per 10 000 words of 30 privacy / design terms in T and in E; Spearman rank correlation and the
                   terms whose frequency differs by more than a factor of 2 (with at least 5 occurrences on one side)
 4 commitment      share of sentences carrying obligation / permission / intention / possibility / negation markers in T and E
 5 numbers         share of the distinct numbers of E (2+ digits, decimals, percentages) that also occur in T, and vice versa
 6 privacy sentences  every sentence of E that contains a privacy key term is matched to its most similar sentence of T (TF-IDF
                   cosine on word 1-2-grams); reported: share matched (cosine >= 0.35), median similarity, and, among matched
                   pairs, agreement of the commitment category (obligation / permission / intention / possibility / plain) and of negation
Bracketed source terms and translator notes are removed from T before counting. Output: a CSV with one row per pair, a JSON with
the term tables, and an Excel sheet of the privacy-sentence pairs (lowest similarity and category mismatches first) for the authors
to read: both columns are English.

usage: benchmark_translations.py --pairs <json: [{doc_key, translation, english_pdf, label}]> --out-csv <csv> --out-json <json> --out-xlsx <xlsx>
"""
import argparse, csv, json, re, subprocess, statistics, collections
TERMS = {"anonym": r"\banonym\w*", "pseudonym": r"\bpseudonym\w*", "privacy": r"\bprivacy\b", "confidential": r"\bconfidential\w*", "personal data": r"\bpersonal (data|information)\b",
         "data protection": r"\bdata protection\b", "identif": r"\bidentif\w*", "identity": r"\bidentit(y|ies)\b", "verification": r"\bverif\w*", "KYC/due diligence": r"\b(kyc|know[- ]your[- ]customer|due diligence)\b",
         "AML/laundering": r"\b(aml|money[- ]laundering|terrorist financing)\b", "trace": r"\btrac(e|ed|ing|eab\w*)\b", "surveillance/monitor": r"\b(surveillance|monitor\w*)\b", "offline": r"\boff-?line\b", "limit": r"\blimit(s|ed)?\b",
         "wallet": r"\bwallets?\b", "account": r"\baccounts?\b", "token": r"\btokens?\b", "register/ledger": r"\b(ledgers?|registers?|registry)\b", "DLT/blockchain": r"\b(dlt|distributed ledger|blockchain)\b",
         "intermediar": r"\bintermediar\w*", "bank": r"\bbanks?\b", "payment service provider": r"\b(payment service providers?|psps?)\b", "legal tender": r"\blegal tender\b", "cash": r"\bcash\b",
         "smart contract/programm": r"\b(smart contracts?|programmab\w*)\b", "pilot/prototype": r"\b(pilots?|prototypes?|proof of concept)\b", "security": r"\bsecurity\b", "consent": r"\bconsent\w*", "interest": r"\binterest\b"}
PRIV = re.compile(r"\b(anonym\w*|pseudonym\w*|privacy|confidential\w*|personal (data|information)|data protection|identif\w*|identit(y|ies)|trac(e|ed|ing|eab\w*)|surveillance|kyc|due diligence|money[- ]laundering)\b", re.I)
CAT = [("obligation", r"\b(shall|must|is required to|are required to|has to|have to|obliged|obligation|mandatory)\b"), ("permission", r"\b(may|can|is allowed|are allowed|permitted|is able to|are able to)\b"),
       ("intention", r"\b(will|plans? to|intends? to|is to be|are to be|is going to)\b"), ("possibility", r"\b(could|might|would|possible|possibly|potential\w*|consider\w*|option\w*|alternative\w*|if)\b")]
NEG = re.compile(r"\b(not|no|never|cannot|neither|nor|without)\b|n't", re.I)


def clean_t(text):
    text = re.sub(r"(?m)^#.*\n", "", text); text = re.sub(r"=== PAGE [\d.]+ ===", "\n", text)
    text = re.sub(r"\[TN:[^\]]*\]", " ", text); return re.sub(r"\[[^\]\n]{1,120}\]", " ", text)


def norm(s): return re.sub(r"\s+", " ", s.replace("­", "").replace("-\n", "")).strip()


def sents(text):
    text = re.sub(r"-\n(?=[a-z])", "", text); paras = re.split(r"\n\s*\n", text); out = []
    for p in paras:
        p = norm(p)
        for s in re.split(r"(?<=[.!?;:])\s+(?=[A-Z0-9“\"(])", p):
            if len(s.split()) >= 6: out.append(s)
    return out


def cat(s):
    low = s.lower()
    for name, rx in CAT:
        if re.search(rx, low): return name
    return "plain"


def spearman(a, b):
    def rk(v):
        o = sorted(range(len(v)), key=lambda i: v[i]); r = [0.0] * len(v); i = 0
        while i < len(o):
            j = i
            while j + 1 < len(o) and v[o[j + 1]] == v[o[i]]: j += 1
            for k in range(i, j + 1): r[o[k]] = (i + j) / 2 + 1
            i = j + 1
        return r
    ra, rb = rk(a), rk(b); ma, mb = sum(ra) / len(ra), sum(rb) / len(rb)
    num = sum((x - ma) * (y - mb) for x, y in zip(ra, rb)); den = (sum((x - ma) ** 2 for x in ra) * sum((y - mb) ** 2 for y in rb)) ** 0.5
    return num / den if den else 0.0


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--pairs", required=True); ap.add_argument("--out-csv", required=True); ap.add_argument("--out-json", required=True); ap.add_argument("--out-xlsx", required=True)
    a = ap.parse_args(); pairs = json.load(open(a.pairs))
    from sacrebleu.metrics import CHRF
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    rows = []; detail = {}; review = []
    for p in pairs:
        T = clean_t(open(p["translation"], encoding="utf-8").read())
        E = subprocess.run(["pdftotext", "-enc", "UTF-8", p["english_pdf"], "-"], capture_output=True).stdout.decode("utf-8", "replace").replace("\f", "\n\n")
        Tn, En = norm(T), norm(E); wt, we = len(Tn.split()), len(En.split())
        chrf = CHRF().corpus_score([Tn], [[En]]).score
        ft = {k: len(re.findall(rx, Tn, re.I)) for k, rx in TERMS.items()}; fe = {k: len(re.findall(rx, En, re.I)) for k, rx in TERMS.items()}
        rt = [ft[k] / wt * 1e4 for k in TERMS]; re_ = [fe[k] / we * 1e4 for k in TERMS]; rho = spearman(rt, re_)
        off = [f"{k} (T {ft[k]} / E {fe[k]})" for k in TERMS if max(ft[k], fe[k]) >= 5 and (max(ft[k] / wt, fe[k] / we) > 2 * max(min(ft[k] / wt, fe[k] / we), 1e-9))]
        St, Se = sents(T), sents(E)
        prof = lambda S: {c: round(sum(1 for s in S if re.search(rx, s.lower())) / len(S), 3) for c, rx in CAT} | {"negation": round(sum(1 for s in S if NEG.search(s)) / len(S), 3)}
        pt, pe = prof(St), prof(Se)
        num = lambda s: set(re.findall(r"\d+(?:[.,]\d+)?%?", re.sub(r"(?<=\d)[  ](?=\d{3}\b)", "", s))) - {str(i) for i in range(0, 10)}
        nt, ne = {x for x in num(Tn) if len(x) >= 2}, {x for x in num(En) if len(x) >= 2}
        vec = TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True, stop_words="english").fit(St + Se); Mt = vec.transform(St)
        pe_s = [s for s in Se if PRIV.search(s)]; sims = []; agree = neg_agree = matched = 0
        if pe_s:
            C = cosine_similarity(vec.transform(pe_s), Mt)
            for i, s in enumerate(pe_s):
                j = int(C[i].argmax()); c = float(C[i, j]); sims.append(c)
                ce, ct = cat(s), cat(St[j]); ng = bool(NEG.search(s)) == bool(NEG.search(St[j]))
                if c >= 0.35: matched += 1; agree += ce == ct; neg_agree += ng
                review.append({"pair": p["label"], "similarity": round(c, 2), "category E": ce, "category T": ct, "same category": "yes" if ce == ct else "NO", "same negation": "yes" if ng else "NO",
                               "issuer English edition (E)": s[:700], "machine translation of the original (T)": St[j][:700]})
        rows.append({"pair": p["label"], "doc_key": p["doc_key"], "words_T": wt, "words_E": we, "length_ratio_T_to_E": round(wt / we, 2), "chrF": round(chrf, 1), "key_term_spearman": round(rho, 2), "key_terms_differing_x2": "; ".join(off),
                     **{f"T_{k}": v for k, v in pt.items()}, **{f"E_{k}": v for k, v in pe.items()}, "numbers_of_E_found_in_T": round(len(ne & nt) / len(ne), 2) if ne else "", "numbers_of_T_found_in_E": round(len(ne & nt) / len(nt), 2) if nt else "",
                     "privacy_sentences_E": len(pe_s), "matched_share": round(matched / len(pe_s), 2) if pe_s else "", "median_similarity": round(statistics.median(sims), 2) if sims else "",
                     "commitment_category_agreement": round(agree / matched, 2) if matched else "", "negation_agreement": round(neg_agree / matched, 2) if matched else ""})
        detail[p["label"]] = {"terms_T": ft, "terms_E": fe, "words_T": wt, "words_E": we}
    with open(a.out_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    json.dump(detail, open(a.out_json, "w"), indent=1)
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Font, PatternFill
    wb = Workbook(); ws = wb.active; ws.title = "SUMMARY"; ws.append(list(rows[0].keys()))
    for r in rows: ws.append(list(r.values()))
    for c in ws[1]: c.font = Font(bold=True); c.alignment = Alignment(wrap_text=True, vertical="top")
    ws2 = wb.create_sheet("PRIVACY_SENTENCES"); hdr = list(review[0].keys()); ws2.append(hdr)
    for r in sorted(review, key=lambda r: (r["pair"], r["same category"] == "yes" and r["same negation"] == "yes", r["similarity"])):
        ws2.append(list(r.values()))
        if r["same category"] == "NO" or r["same negation"] == "NO": ws2.cell(ws2.max_row, 5).fill = PatternFill("solid", fgColor="FCE4D6")
    for i, wd in enumerate([22, 9, 11, 11, 9, 9, 90, 90], 1): ws2.column_dimensions["ABCDEFGH"[i - 1]].width = wd
    for row in ws2.iter_rows():
        for c in row: c.alignment = Alignment(wrap_text=True, vertical="top")
    for c in ws2[1]: c.font = Font(bold=True)
    ws2.freeze_panes = "A2"; ws2.auto_filter.ref = ws2.dimensions; wb.save(a.out_xlsx)
    for r in rows: print(r["pair"], "| words", r["words_T"], r["words_E"], "| chrF", r["chrF"], "| terms rho", r["key_term_spearman"], "| nums", r["numbers_of_E_found_in_T"], "| priv sents", r["privacy_sentences_E"], "matched", r["matched_share"], "med", r["median_similarity"], "cat", r["commitment_category_agreement"], "neg", r["negation_agreement"])


if __name__ == "__main__": main()
