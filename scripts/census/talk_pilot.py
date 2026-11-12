#!/usr/bin/env python3
"""Deterministic pilot for the privacy-talk instrument (12 Nov 2026): what a sentence-level, dictionary-based salience measure looks
like on the evidence documents, and how reliable a project-level "talk" score built from it would be. No model, no per-project
output: the committed file holds aggregates only (keyword counts per document do not expose cell values, EXPOSURE_LEDGER 17 Oct).

Corpus: documents with decision KEEP / BORDERLINE in TIERS_<date>.csv that are English (text layer of the master file) or have an
English machine translation (route D) or an issuer English edition (route B). Unit: sentence (>= 6 words) from the text layer.
Dictionaries (case-insensitive, on sentences):
  NARROW  privacy | anonym* | pseudonym* | personal data/information | data protection | confidential*
  BROAD   NARROW + identif* | identity | trace*/traceab* | surveillance | KYC / due diligence | money laundering | data minimi* | consent
Reported: salience (share of sentences hit) per document; concentration; length confound; salience by document kind, year and text
route; modal profile of privacy sentences; split-half reliability of a project-level score (documents of a project randomly halved,
1 000 splits, Spearman-Brown corrected) for projects with >= 4 documents, for the share-based and the count-based score; agreement
between the two dictionaries; and, for the two exposed projects only (NO, UK), the rank correlation between dictionary hits and the
number of typed statements of the model survey per document.

usage: talk_pilot.py --tiers data/manifest/TIERS_2026-11-10.csv --workbook <ALL xlsx> --cache <text cache> --translations <dir> [<dir> ...] --out data/census/TALK_PILOT_aggregate.json
"""
import argparse, csv, glob, json, os, random, re, statistics as st, collections
import openpyxl
NARROW = re.compile(r"\b(privacy|anonym\w*|pseudonym\w*|personal (data|information)|data protection|confidential\w*)\b", re.I)
BROAD = re.compile(r"\b(privacy|anonym\w*|pseudonym\w*|personal (data|information)|data protection|confidential\w*|identif\w*|identit(y|ies)|trac(e|ed|ing|eab\w*)|surveillance|kyc|know[- ]your[- ]customer|due diligence|money[- ]laundering|data minimi[sz]\w*|consent\w*)\b", re.I)
FAM = {"privacy": r"\bprivacy\b", "anonymity": r"\banonym\w*", "pseudonymity": r"\bpseudonym\w*", "personal data": r"\bpersonal (data|information)\b", "data protection": r"\bdata protection\b", "confidentiality": r"\bconfidential\w*",
       "identification": r"\b(identif\w*|identit(y|ies))\b", "tracing": r"\b(trac(e|ed|ing|eab\w*)|surveillance)\b", "KYC/AML": r"\b(kyc|know[- ]your[- ]customer|due diligence|money[- ]laundering)\b", "minimisation": r"\bdata minimi[sz]\w*",
       "consent": r"\bconsent\w*", "offline": r"\boff-?line\b", "limits/tiers": r"\b(holding limits?|transaction limits?|tiered|tiers?)\b", "PETs": r"\b(zero[- ]knowledge|blind signatures?|encrypt\w*|cryptograph\w*|privacy[- ]enhancing)\b"}
MOD = [("obligation", r"\b(shall|must|required to|has to|have to|obliged|mandatory)\b"), ("intention", r"\b(will|plans? to|intends? to|is to be|are to be)\b"), ("permission", r"\b(may|can|allowed|permitted|able to)\b"),
       ("possibility", r"\b(could|might|would|possible|possibly|potential\w*|consider\w*|option\w*|alternative\w*)\b")]


def sents(text):
    text = re.sub(r"(?m)^#.*\n", "", text); text = re.sub(r"=== PAGE [\d.]+ ===", "\n\n", text); text = re.sub(r"\[[^\]\n]{1,120}\]", " ", text); text = re.sub(r"-\n\s*(?=[a-z])", "", text)
    out = []
    for p in re.split(r"\n\s*\n", text):
        p = re.sub(r"\s+", " ", p).strip()
        for s in re.split(r"(?<=[.!?;:])\s+(?=[A-Z0-9“\"(])", p):
            if len(s.split()) >= 6: out.append(s)
    return out


def spearman(a, b):
    def rk(v):
        o = sorted(range(len(v)), key=lambda i: v[i]); r = [0.0] * len(v); i = 0
        while i < len(o):
            j = i
            while j + 1 < len(o) and v[o[j + 1]] == v[o[i]]: j += 1
            for k in range(i, j + 1): r[o[k]] = (i + j) / 2 + 1
            i = j + 1
        return r
    if len(a) < 3: return None
    ra, rb = rk(a), rk(b); ma, mb = sum(ra) / len(ra), sum(rb) / len(rb)
    den = (sum((x - ma) ** 2 for x in ra) * sum((y - mb) ** 2 for y in rb)) ** 0.5
    return round(sum((x - ma) * (y - mb) for x, y in zip(ra, rb)) / den, 3) if den else None


def q(v): v = sorted(v); n = len(v); return {"n": n, "min": round(v[0], 4), "q1": round(v[n // 4], 4), "median": round(st.median(v), 4), "q3": round(v[(3 * n) // 4], 4), "max": round(v[-1], 4)} if v else {"n": 0}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--tiers", required=True); ap.add_argument("--workbook", required=True); ap.add_argument("--cache", required=True); ap.add_argument("--translations", nargs="+", required=True)
    ap.add_argument("--editions", default="data/translation/ENGLISH_EDITIONS_2026-11-10.csv"); ap.add_argument("--statements", default="data/statements"); ap.add_argument("--out", required=True)
    a = ap.parse_args()
    ws = openpyxl.load_workbook(a.workbook, read_only=True)["ALL_DOCUMENTS"]; R = list(ws.iter_rows(values_only=True)); h = R[0]; kind = {r[h.index("id")]: (r[h.index("kind")] or "n/d") for r in R[1:]}
    tr = {}
    for d in a.translations:
        for f in glob.glob(os.path.join(d, "*.en.txt")): tr[os.path.basename(f)[:-7]] = f
    ed = {e["parallel_of"]: e for e in csv.DictReader(open(a.editions, encoding="utf-8")) if e["sha256"]}
    docs = []; skipped = collections.Counter()
    for r in csv.DictReader(open(a.tiers, encoding="utf-8")):
        if r["decision_v12"] not in ("KEEP", "BORDERLINE") or r["tier"] == "out_of_frame": continue
        key = re.sub(r"[^A-Za-z0-9_-]+", "-", f"{r['project']}_{r['id']}")[:70]; path = route = None
        if r["language"] == "en" and r["sha256"] and os.path.exists(os.path.join(a.cache, r["sha256"] + ".txt")): path, route = os.path.join(a.cache, r["sha256"] + ".txt"), "A_english_original"
        elif r["id"] in ed and os.path.exists(os.path.join(a.cache, ed[r["id"]]["sha256"] + ".txt")): path, route = os.path.join(a.cache, ed[r["id"]]["sha256"] + ".txt"), "B_issuer_english_edition"
        elif key in tr: path, route = tr[key], "D_machine_translation"
        if not path: skipped[r["language"] or r["text_flag"] or "no file"] += 1; continue
        S = sents(open(path, encoding="utf-8").read())
        if len(S) < 5: skipped["too little text"] += 1; continue
        nn = [s for s in S if NARROW.search(s)]; nb = sum(1 for s in S if BROAD.search(s)); mod = collections.Counter()
        for s in nn:
            for name, rx in MOD:
                if re.search(rx, s.lower()): mod[name] += 1; break
            else: mod["plain"] += 1
        T = " ".join(S); fam = {k for k, rx in FAM.items() if re.search(rx, T, re.I)}
        docs.append({"fam": fam, "id": r["id"], "project": r["project"], "tier": r["tier"], "year": r["year"], "kind": kind.get(r["id"], "n/d"), "route": route, "n": len(S), "narrow": len(nn), "broad": nb, "mod": mod})
    D = docs; out = {"as_of": "2026-11-12", "corpus": {"documents": len(D), "projects": len({d["project"] for d in D}), "sentences": sum(d["n"] for d in D), "by_route": dict(collections.Counter(d["route"] for d in D)),
                     "evidence_documents_without_usable_english_text": dict(skipped)}, "dictionaries": {"narrow": NARROW.pattern, "broad": BROAD.pattern}}
    sal = lambda d, k="narrow": d[k] / d["n"]
    tot = sum(d["narrow"] for d in D); top = sorted(D, key=lambda d: -d["narrow"])
    out["document_level"] = {"salience_narrow": q([sal(d) for d in D]), "salience_broad": q([sal(d, "broad") for d in D]), "documents_with_zero_narrow_hits": sum(1 for d in D if not d["narrow"]),
                             "privacy_sentences_total_narrow": tot, "share_of_all_privacy_sentences_in_top_10pct_documents": round(sum(d["narrow"] for d in top[:max(1, len(D) // 10)]) / tot, 3),
                             "spearman_count_vs_length": spearman([d["narrow"] for d in D], [d["n"] for d in D]), "spearman_share_vs_length": spearman([sal(d) for d in D], [d["n"] for d in D]),
                             "spearman_narrow_vs_broad_share": spearman([sal(d) for d in D], [sal(d, "broad") for d in D])}
    grp = lambda f: {k: {"documents": len(v), "sentences": sum(d["n"] for d in v), "pooled_salience_narrow": round(sum(d["narrow"] for d in v) / sum(d["n"] for d in v), 4), "median_doc_salience": round(st.median(sal(d) for d in v), 4)}
                     for k, v in sorted(collections.defaultdict(list, {k: [d for d in D if f(d) == k] for k in {f(d) for d in D}}).items()) if len(v) >= 5}
    out["by_kind"] = grp(lambda d: d["kind"]); out["by_year"] = grp(lambda d: d["year"]); out["by_route"] = grp(lambda d: d["route"]); out["by_tier"] = grp(lambda d: d["tier"])
    M = collections.Counter()
    for d in D: M.update(d["mod"])
    out["modal_profile_of_privacy_sentences"] = {k: round(v / sum(M.values()), 3) for k, v in M.most_common()}
    P = collections.defaultdict(list)
    for d in D: P[d["project"]].append(d)
    kp = collections.defaultdict(lambda: [0, 0])
    for d in D: kp[d["kind"]][0] += d["narrow"]; kp[d["kind"]][1] += d["n"]
    exp = lambda d: d["n"] * kp[d["kind"]][0] / kp[d["kind"]][1]
    big = {p: v for p, v in P.items() if len(v) >= 4}; rnd = random.Random(20261112); res = {"share": [], "count": [], "share_broad": [], "share_standardised_by_document_kind": [], "breadth_term_families": [], "mean_of_document_shares": []}
    for _ in range(1000):
        xa = {k: [] for k in res}; xb = {k: [] for k in res}
        for p, v in big.items():
            v = v[:]; rnd.shuffle(v); A, B = v[: len(v) // 2], v[len(v) // 2:]
            for k, f in (("share", lambda X: sum(d["narrow"] for d in X) / sum(d["n"] for d in X)), ("count", lambda X: sum(d["narrow"] for d in X)), ("share_broad", lambda X: sum(d["broad"] for d in X) / sum(d["n"] for d in X)),
                         ("share_standardised_by_document_kind", lambda X: sum(d["narrow"] for d in X) / max(sum(exp(d) for d in X), 1e-9)), ("breadth_term_families", lambda X: len(set().union(*[d["fam"] for d in X]))),
                         ("mean_of_document_shares", lambda X: sum(d["narrow"] / d["n"] for d in X) / len(X))):
                xa[k].append(f(A)); xb[k].append(f(B))
        for k in res:
            r = spearman(xa[k], xb[k]); res[k].append(2 * r / (1 + r) if r is not None and r > -1 else 0)
    out["project_level"] = {"projects": len(P), "projects_with_4plus_documents": len(big), "documents_per_project": q([len(v) for v in P.values()]),
                            "pooled_salience_narrow_across_projects": q([sum(d["narrow"] for d in v) / sum(d["n"] for d in v) for v in P.values()]),
                            "split_half_reliability_spearman_brown": {k: {"median": round(st.median(v), 2), "p05": round(sorted(v)[50], 2), "p95": round(sorted(v)[950], 2)} for k, v in res.items()},
                            "spearman_project_share_vs_number_of_documents": spearman([sum(d["narrow"] for d in v) / sum(d["n"] for d in v) for v in P.values()], [len(v) for v in P.values()]),
                            "spearman_project_count_vs_number_of_documents": spearman([sum(d["narrow"] for d in v) for v in P.values()], [len(v) for v in P.values()])}
    sv = collections.Counter()
    for f in glob.glob(os.path.join(a.statements, "*_statements.csv")):
        for r in csv.DictReader(open(f, encoding="utf-8")): sv[r["doc_id"]] += 1
    out["project_level"]["breadth_term_families_across_projects"] = q([len(set().union(*[d["fam"] for d in v])) for v in P.values()])
    out["project_level"]["spearman_breadth_vs_number_of_documents"] = spearman([len(set().union(*[d["fam"] for d in v])) for v in P.values()], [len(v) for v in P.values()])
    out["project_level"]["spearman_breadth_vs_share"] = spearman([len(set().union(*[d["fam"] for d in v])) for v in P.values()], [sum(d["narrow"] for d in v) / sum(d["n"] for d in v) for v in P.values()])
    big8 = {p: v for p, v in P.items() if len(v) >= 8}; r8 = []
    for _ in range(1000):
        xa, xb = [], []
        for p, v in big8.items():
            v = v[:]; rnd.shuffle(v); A, B = v[: len(v) // 2], v[len(v) // 2:]; xa.append(sum(d["narrow"] for d in A) / sum(d["n"] for d in A)); xb.append(sum(d["narrow"] for d in B) / sum(d["n"] for d in B))
        r = spearman(xa, xb); r8.append(2 * r / (1 + r) if r is not None and r > -1 else 0)
    out["project_level"]["split_half_share_projects_with_8plus_documents"] = {"projects": len(big8), "median": round(st.median(r8), 2), "p05": round(sorted(r8)[50], 2), "p95": round(sorted(r8)[950], 2)}
    pairs = [(d["narrow"], d["broad"], sv[d["id"]]) for d in D if d["id"] in sv]
    out["convergence_share_based"] = spearman([d["narrow"] / d["n"] for d in D if d["id"] in sv], [sv[d["id"]] / d["n"] for d in D if d["id"] in sv])
    out["convergence_with_model_survey_exposed_projects_only"] = {"documents": len(pairs), "spearman_narrow_hits_vs_survey_statements": spearman([p[0] for p in pairs], [p[2] for p in pairs]), "spearman_broad_hits_vs_survey_statements": spearman([p[1] for p in pairs], [p[2] for p in pairs])}
    try:  # variance decomposition: how much of document salience belongs to the project once document kind (and year) is held fixed
        import math, pandas as pd, statsmodels.formula.api as smf, warnings; warnings.simplefilter("ignore")
        big_k = {k for k, v in collections.Counter(d["kind"] for d in D).items() if v >= 5}
        df = pd.DataFrame([{"y": math.asin(math.sqrt(d["narrow"] / d["n"])), "project": d["project"], "kind": d["kind"] if d["kind"] in big_k else "other", "year": d["year"] if d["year"].isdigit() else "nd", "logn": math.log(d["n"])} for d in D])
        icc = {}
        for name, f in (("no_controls", "y ~ 1"), ("document_kind", "y ~ C(kind)"), ("kind_and_length", "y ~ C(kind) + logn"), ("kind_length_year", "y ~ C(kind) + logn + C(year)")):
            m = smf.mixedlm(f, df, groups=df["project"]).fit(reml=True); vp = float(m.cov_re.iloc[0, 0]); icc[name] = {"project_variance_share_ICC": round(vp / (vp + m.scale), 3), "residual_sd": round(m.scale ** 0.5, 4)}
        ols0 = smf.ols("y ~ 1", df).fit(); olsk = smf.ols("y ~ C(kind)", df).fit(); olsp = smf.ols("y ~ C(project)", df).fit()
        out["variance_decomposition_document_salience"] = {"transform": "arcsine square root of the narrow share", "mixed_model_random_intercept_project": icc, "R2_document_kind_alone": round(olsk.rsquared, 3), "R2_project_dummies_alone": round(olsp.rsquared, 3), "adjR2_project_dummies_alone": round(olsp.rsquared_adj, 3)}
        print(json.dumps(out["variance_decomposition_document_salience"], indent=1))
    except Exception as e:
        out["variance_decomposition_document_salience"] = {"error": str(e)}; print("variance decomposition failed:", e)
    json.dump(out, open(a.out, "w"), indent=1); print(json.dumps(out["project_level"], indent=1)); print(out["convergence_with_model_survey_exposed_projects_only"], out["convergence_share_based"])


if __name__ == "__main__": main()
