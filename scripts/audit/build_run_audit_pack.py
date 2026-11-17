#!/usr/bin/env python3
"""Audit pack of 17 Nov 2026 (before the paid model runs): prompt, brief, the repository at HEAD and four extras outside the repository.

Extras (hold source text, so they are never committed): the corpus workbook; the development workbook with one author's blind relevance
labels; example requests for the relevance prompt in the two candidate forms (one unit / one page) for the first 12 development units;
a diagnostic sample of 300 units for the auditor (own seed, no unit of the development sample; 80 D, 40 N, 40 R, 80 not sent, 60 excluded).

usage: build_run_audit_pack.py --units <units dir> --corpus-workbook <xlsx> --dev-workbook <xlsx> --out <dir> --date 2026-11-17
"""
import argparse, csv, glob, hashlib, os, shutil, subprocess, sys, zipfile
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "scripts/units")); import select_candidates as sc, build_requests as br
SEED = "audit-units-2026-11-17"; Q = {"D": 80, "N": 40, "R": 40, "-": 80, "X": 60}


def main():
    ap = argparse.ArgumentParser()
    for k in ("units", "corpus-workbook", "dev-workbook", "out", "date"): ap.add_argument("--" + k, required=True)
    a = ap.parse_args(); name = f"CBDC_AUDIT_PACK_{a.date}"; P = os.path.join(a.out, name); shutil.rmtree(P, ignore_errors=True); os.makedirs(os.path.join(P, "extra/EXAMPLE_REQUESTS"))
    subprocess.run(f"git -C {ROOT} archive --prefix=repo/ HEAD | tar -x -C {P}", shell=True, check=True)
    open(os.path.join(P, "repo/GIT_COMMIT.txt"), "w").write(subprocess.run(["git", "-C", ROOT, "rev-parse", "HEAD"], capture_output=True, text=True).stdout)
    open(os.path.join(P, "repo/GIT_LOG_since_2026-11-13.txt"), "w").write(subprocess.run(["git", "-C", ROOT, "log", "--since=2026-11-13", "--date=iso", "--pretty=%h %ad %s"], capture_output=True, text=True).stdout)
    shutil.copy(os.path.join(ROOT, f"docs/audits/PROMPT_AUDIT_{a.date}.md"), os.path.join(P, "00_PROMPT.md")); shutil.copy(os.path.join(ROOT, f"docs/audits/AUDIT_BRIEF_{a.date}.md"), os.path.join(P, "01_AUDIT_BRIEF.md"))
    shutil.copy(a.corpus_workbook, os.path.join(P, "extra", f"CBDC_CORPUS_DOCUMENTS_{a.date}.xlsx")); shutil.copy(a.dev_workbook, os.path.join(P, "extra", "TALK_DEV_SAMPLE_MB_relevance_only.xlsx"))
    man = {r["doc_key"]: r for r in csv.DictReader(open(sorted(glob.glob(os.path.join(ROOT, "data/units/UNITS_MANIFEST_*.csv")))[-1], encoding="utf-8"))}
    dev = [r["unit_id"] for r in csv.DictReader(open(os.path.join(ROOT, "data/units/AGREEMENT_SAMPLE_dev_2026-11-13.csv"), encoding="utf-8"))]; used = set(dev)
    system = open(os.path.join(ROOT, "pipeline/prompts/talk_L1_relevance.system.md"), encoding="utf-8").read(); pool = {k: [] for k in Q}; docs = {}
    for key, m in man.items():
        U = list(csv.DictReader(open(os.path.join(a.units, key + ".units.csv"), encoding="utf-8")))
        st = {r["unit_id"]: r["stratum"] for r in csv.DictReader(open(os.path.join(a.units, key + ".candidates.csv"), encoding="utf-8"))}; docs[key] = (U, st)
        for u in U:
            if u["unit_id"] in used: continue
            s = st.get(u["unit_id"]) or ("X" if int(u["n_words"]) < 4 or (int(u["n_words"]) < 12 and sc.BOILER.search(u["text"])) else "-")
            pool[s].append((hashlib.sha256(f"{SEED}|{u['unit_id']}".encode()).hexdigest(), u["unit_id"], s, m["project"], m["route"], m["text_mode"], m["kind"], u["n_words"], u["text"]))
    with open(os.path.join(P, "extra/UNITS_DIAGNOSTIC_SAMPLE_300.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh); w.writerow(["unit_id", "stratum", "project", "route", "text_mode", "document_kind", "n_words", "text"])
        for s, n in Q.items():
            for r in sorted(pool[s])[:n]: w.writerow(r[1:])
    for n, uid in enumerate(dev[:12], 1):
        key = uid.split(":p")[0]; U, st = docs[key]; i = next(k for k, u in enumerate(U) if u["unit_id"] == uid)
        idx = [k for k, u in enumerate(U) if u["page"] == U[i]["page"] and st.get(u["unit_id"]) in ("D", "N", "R")]
        for form, user in (("single", br.single(U, i)), ("page", br.page(U, idx))):
            open(os.path.join(P, "extra/EXAMPLE_REQUESTS", f"{n:02d}_{form}.txt"), "w", encoding="utf-8").write("===== SYSTEM =====\n" + system + "\n===== USER =====\n" + user)
    open(os.path.join(P, "extra/EXAMPLE_REQUESTS/README.txt"), "w").write("Requests for the relevance prompt (talk_L1 v0.2), built by repo/scripts/units/build_requests.py (DRAFT).\nNN_single.txt: one development unit per request. NN_page.txt: all candidate units of the page that holds that unit.\nNo request has been sent to any model.\n")
    z = os.path.join(a.out, name + ".zip")
    with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED) as zf:
        for d, _, fs in os.walk(P):
            for f in sorted(fs): zf.write(os.path.join(d, f), os.path.relpath(os.path.join(d, f), a.out))
    print(z, os.path.getsize(z), "bytes;", sum(len(f) for _, _, f in os.walk(P)), "files; sha256", hashlib.sha256(open(z, "rb").read()).hexdigest())


if __name__ == "__main__": main()
