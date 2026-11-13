#!/usr/bin/env python3
"""Audit pack for a second, independent model (13 Nov 2026): prompt, brief, the repository at HEAD and a few excerpts.

Excerpts outside the repository (short, for verification only): the authors' tier workbook, the translation benchmark workbook, two
request/response pairs of the translation run, and a diagnostic sample of 300 units drawn for the auditor: hash rank with its own seed,
never a unit of the coders' agreement sample; 80 D, 40 N, 40 R, 80 not sent, 60 excluded (X).

usage: build_audit_pack.py --units <units dir> --translation <CBDC_TRANSLATION_v12 dir> --tier-workbook <xlsx> --benchmark <xlsx> --out <dir> --date 2026-11-13
"""
import argparse, csv, glob, hashlib, os, shutil, subprocess, sys, zipfile
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "scripts/units")); import select_candidates as sc  # same dictionary and exclusion rule as the pipeline
SEED = "audit-units-2026-11-13"; Q = {"D": 80, "N": 40, "R": 40, "-": 80, "X": 60}
EXAMPLES = ["EU_SI_SI_Banka-Slovenije_Zapisnik-1-seje-NSD-digitalni-evro_2024", "CN_CAND-063"]


def main():
    ap = argparse.ArgumentParser()
    for k in ("units", "translation", "tier-workbook", "benchmark", "out", "date"): ap.add_argument("--" + k, required=True)
    a = ap.parse_args(); name = f"CBDC_AUDIT_PACK_{a.date}"; P = os.path.join(a.out, name); shutil.rmtree(P, ignore_errors=True); os.makedirs(os.path.join(P, "extra/translation_examples"))
    subprocess.run(f"git -C {ROOT} archive --prefix=repo/ HEAD | tar -x -C {P}", shell=True, check=True)
    open(os.path.join(P, "repo/GIT_COMMIT.txt"), "w").write(subprocess.run(["git", "-C", ROOT, "rev-parse", "HEAD"], capture_output=True, text=True).stdout)
    open(os.path.join(P, "repo/GIT_LOG_since_2026-11-03.txt"), "w").write(subprocess.run(["git", "-C", ROOT, "log", "--since=2026-11-03", "--date=iso", "--pretty=%h %ad %s"], capture_output=True, text=True).stdout)
    shutil.copy(os.path.join(ROOT, f"docs/audits/PROMPT_AUDIT_{a.date}.md"), os.path.join(P, "00_PROMPT.md")); shutil.copy(os.path.join(ROOT, f"docs/audits/AUDIT_BRIEF_{a.date}.md"), os.path.join(P, "01_AUDIT_BRIEF.md"))
    shutil.copy(a.tier_workbook, os.path.join(P, "extra")); shutil.copy(a.benchmark, os.path.join(P, "extra"))
    man = {r["doc_key"]: r for r in csv.DictReader(open(sorted(glob.glob(os.path.join(ROOT, "data/units/UNITS_MANIFEST_*.csv")))[-1], encoding="utf-8"))}
    used = {r["unit_id"] for r in csv.DictReader(open(sorted(glob.glob(os.path.join(ROOT, "data/units/AGREEMENT_SAMPLE_*.csv")))[-1], encoding="utf-8"))}
    pool = {k: [] for k in Q}
    for key, m in man.items():
        U = list(csv.DictReader(open(os.path.join(a.units, key + ".units.csv"), encoding="utf-8")))
        st = {r["unit_id"]: r["stratum"] for r in csv.DictReader(open(os.path.join(a.units, key + ".candidates.csv"), encoding="utf-8"))}
        for u in U:
            if u["unit_id"] in used: continue
            s = st.get(u["unit_id"]) or ("X" if int(u["n_words"]) < 4 or (int(u["n_words"]) < 12 and sc.BOILER.search(u["text"])) else "-")
            pool[s].append((hashlib.sha256(f"{SEED}|{u['unit_id']}".encode()).hexdigest(), u["unit_id"], s, m["project"], m["route"], m["text_mode"], m["kind"], u["n_words"], u["text"]))
    with open(os.path.join(P, "extra/UNITS_DIAGNOSTIC_SAMPLE_300.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh); w.writerow(["unit_id", "stratum", "project", "route", "text_mode", "document_kind", "n_words", "text"])
        for s, n in Q.items():
            for r in sorted(pool[s])[:n]: w.writerow(r[1:])
    shutil.copy(os.path.join(a.translation, "SYSTEM_PROMPT_translation.md"), os.path.join(P, "extra/translation_examples"))
    for k in EXAMPLES:
        for f in glob.glob(os.path.join(a.translation, "requests", "*", k, "*chunk-01-of-*.txt")) + glob.glob(os.path.join(a.translation, "responses", "*", k, "*chunk-01-of-*")): shutil.copy(f, os.path.join(P, "extra/translation_examples"))
    z = os.path.join(a.out, name + ".zip")
    with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED) as zf:
        for d, _, fs in os.walk(P):
            for f in sorted(fs): zf.write(os.path.join(d, f), os.path.relpath(os.path.join(d, f), a.out))
    print(z, os.path.getsize(z), "bytes;", sum(len(f) for _, _, f in os.walk(P)), "files; sha256", hashlib.sha256(open(z, "rb").read()).hexdigest())


if __name__ == "__main__": main()
