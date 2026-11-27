#!/usr/bin/env python3
"""Recompute the preliminary results of 24 Nov 2026 from the frozen code and the run archive, and compare them with the
results files in the pack. No model call, no network. Written for audit A5 (26 Nov 2026) by the pipeline assistant.

Repaired 26 Nov 2026 after audit A5 (report docs/audits/INDEPENDENT_AUDIT_2026-11-26.md, item 29): the results files are
found by name anywhere under --results (the pack keeps them in subfolders); every comparison that fails is counted and the
script exits with status 1; a hash mismatch of the rebuilt requests is a failure; differing keys are listed; step 6 also
computes the upper reading with the publications that have own talk OR a unit without a majority; step 6b gives L and U
under the frozen ADR-012 D2 rule; step 7 asserts equality; all paths are made absolute. The pack copy of 26 Nov
(05_RECOMPUTE/) stays as it was, as the audited version.

Run it against the snapshot of main e61a562 to reproduce the results of 24 Nov; run it against a later commit to list the
keys a reducer repair changes (the script then exits 1 by design and the listed differences are the change log).

Why this exists: the scripts that built the results package of 24 Nov (index, talk, hypothesis, PET, cell history) were
written in a cloud session and never committed. This script re-derives the published numbers from committed code only
(scripts/pipeline/build_jobs.py, scripts/extraction/reduce_v122.py, scripts/derive_index.py, scripts/units/select_candidates.py)
plus the combination rules that the results package states in words. Where it matches, the numbers are reproducible; where
it does not, the report says so.

Inputs (all outside the repository, because they hold source text):
  --repo     the repository snapshot (repo/ in the core pack, main e61a562)
  --runs     the unzipped PROD_RUNS_FINAL_2026-11-24c.zip (folders runs/ and records/)
  --units    the unzipped CBDC_UNITS_v13e_2026-11-23.zip (folder with <doc_key>.units.csv and .candidates.csv)
  --results  folder with the results files of 24 Nov (results/ in the core pack)
  --work     an empty scratch folder (rebuilt requests and reduced cells are written here; they contain source quotes)

usage: python3 recompute_results.py --repo repo --runs runs_c --units units/CBDC_UNITS_v13e --results results --work work
"""
import argparse, collections, csv, glob, hashlib, json, os, re, subprocess, sys

MODELS = {"Claude": "claude", "Sol": "sol62", "DeepSeek": "deepseek"}
EX2_SHA = "5590a8da01e186ea02cf617284ed1aa2b2cb8dd0bbe35aeb9470acef73856312"  # docs/FREEZE_2026-11-23.md, amendment 1


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""): h.update(b)
    return h.hexdigest()


def find(root, name):
    """The results file of that name anywhere under root (flat folder or the pack's subfolders); exactly one."""
    hits = sorted(glob.glob(os.path.join(root, "**", name), recursive=True))
    if len(hits) != 1: raise SystemExit(f"{name}: {len(hits)} files found under {root}, need exactly one")
    return hits[0]


def main():
    ap = argparse.ArgumentParser()
    for a in ("repo", "runs", "units", "results", "work"): ap.add_argument("--" + a, required=True)
    ap.add_argument("--show", type=int, default=40, help="how many differing keys to list per step")
    a = ap.parse_args()
    for k in ("repo", "runs", "units", "results", "work"): setattr(a, k, os.path.abspath(getattr(a, k)))
    R, out, fails = a.repo, [], collections.Counter()
    say = lambda *x: (print(*x), out.append(" ".join(str(y) for y in x)))
    def fail(step, n, diffs=()):
        if n: fails[step] += n
        for d in list(diffs)[:a.show]: say("   differs:", d)
    os.makedirs(a.work, exist_ok=True)
    sys.path[:0] = [os.path.join(R, "scripts"), os.path.join(R, "scripts", "extraction"), os.path.join(R, "scripts", "units")]
    import derive_index as di, reduce_v122 as rd, select_candidates as sc

    # 1. Rebuild the production extraction requests and check them against the freeze.
    job = os.path.join(a.work, "PROD_EX2")
    meta = json.load(open(os.path.join(a.runs, "records", "PROD_EX2_claude", "RUN_META.json"), encoding="utf-8"))
    projects = sorted({i["file"].split("/")[1].split("_")[0] for i in meta["inputs"] if i["file"].startswith("units/")})
    subprocess.run([sys.executable, os.path.join(R, "scripts/pipeline/build_jobs.py"), "--stage", "extraction_single",
                    "--units", os.path.abspath(a.units), "--projects", *projects,
                    "--prompt", os.path.join(R, "pipeline/prompts/extraction_v12.2.system.md"), "--out", job,
                    "--header-extra", os.path.join(R, "data/manifest/EXTRACTION_HEADER_EXTRA_2026-11-23b.csv"),
                    "--exclude", os.path.join(R, "data/manifest/EXCLUDED_FROM_STAGES_2026-11-23.csv")],
                   check=True, cwd=R, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    s = sha(os.path.join(job, "REQUESTS.jsonl"))
    say("1. PROD_EX2 requests rebuilt:", s, "MATCHES the freeze" if s == EX2_SHA else "DIFFERS from the freeze " + EX2_SHA)
    fail("1 requests", s != EX2_SHA)

    # 2. Reduce each model's accepted responses to cells (the frozen reducer).
    manifest = os.path.join(R, "data/units/UNITS_MANIFEST_2026-11-23b.csv")
    docs = rd.docs_from_manifest(manifest, os.path.join(R, "data/manifest/EXTRACTION_HEADER_EXTRA_2026-11-23b.csv"))
    red, failed = {}, {}
    for m, k in MODELS.items():
        reqs = rd.requests_from_run(os.path.join(a.runs, "runs", f"PROD_EX2_{k}", "ATTEMPTS.jsonl"), os.path.join(job, "REQUESTS.jsonl"))
        failed[m] = sum(r["state"] == "failed" for r in reqs)
        ps = sorted({docs[r["doc_key"]]["project"] for r in reqs})
        red[m] = {p: rd.reduce_project(p, docs, reqs) for p in ps}
        json.dump(red[m], open(os.path.join(a.work, f"cells_{k}.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    say("2. requests failing the v12.2 check:", failed, "(run records: Claude 37, Sol 58, DeepSeek 4 of 376)")
    fail("2 failed requests", failed != {"Claude": 37, "Sol": 58, "DeepSeek": 4})

    # 3. Per-model cells against the workbook PRELIMINARY_RESULTS_BY_COUNTRY, sheet PO_MODELECH.
    try:
        import openpyxl
    except ImportError:
        raise SystemExit("openpyxl is needed for step 3 (pip install openpyxl)")
    if True:
        wb = openpyxl.load_workbook(find(a.results, "PRELIMINARY_RESULTS_BY_COUNTRY_2026-11-24.xlsx"), read_only=True)
        n = bad = 0; diffs, seen = [], set()
        for p, f, m, v, es, ds, im, ba, doc, pg, q in list(wb["PO_MODELECH"].iter_rows(values_only=True))[1:]:
            c = red[m][p]["cells"][f]; n += 1
            mine = (c.get("value") or "", c.get("evidence_state") or "", c.get("decision_status") or "", c.get("implementation_status") or "", c.get("document_id") or "", str(c.get("page_index") or ""))
            theirs = tuple(str(x or "") for x in (v, es, ds, im, doc, pg))
            bad += mine != theirs; seen.add((p, f, m))
            if mine != theirs: diffs.append(f"{p} {f} {m}: workbook {theirs[:4]} -> now {mine[:4]}")
        grid = {(p, f, m) for m in MODELS for p in red[m] for f in rd.MAKER_CELLS}
        if seen != grid: say(f"   key grid: {len(grid - seen)} keys missing from the workbook, {len(seen - grid)} extra"); bad += len(grid ^ seen)
        say(f"3. per-model cells (value, evidence state, statuses, document, page): {n - bad} of {n} rows identical")
        fail("3 per-model cells", bad, diffs)
        pre = list(wb["PREHLED"].iter_rows(values_only=True))[3:]
        n = bad = 0; diffs = []
        for row in pre:
            if not row[0] or row[0] not in red["Claude"]: continue
            for j, m in enumerate(MODELS):
                x = di.axis1(red[m][row[0]]["cells"]); n += 1
                s = f"{x['lower']:.2f}–{x['upper']:.2f}" if x["lower"] != x["upper"] else f"{x['lower']:.2f}–{x['upper']:.2f}"
                bad += s != row[12 + j]
                if s != row[12 + j]: diffs.append(f"{row[0]} {m}: workbook {row[12 + j]} -> now {s}")
        say(f"   per-model 7-cell intervals in sheet PREHLED: {n - bad} of {n} identical")
        fail("3 intervals", bad, diffs)

    # 4. Combination of the three models as the results package states it, then the index.
    def combine(p, f, strict):
        vs = [(red[m][p]["cells"].get(f) or {}).get("value") or "" for m in MODELS]
        nz = {v for v in vs if v}
        if strict: return vs[0] if len(set(vs)) == 1 and vs[0] else ""
        return nz.pop() if len(nz) == 1 else ""
    rows = list(csv.DictReader(open(find(a.results, "CBDC_privacy_index_PRELIMINARY_2026-11-24.csv"), encoding="utf-8")))
    bad = 0; diffs = []
    for r in rows:
        p = r["project"]
        S = {f: {"value": combine(p, f, True)} for f in di.CELLS if combine(p, f, True)}
        P = {f: {"value": combine(p, f, False)} for f in di.CELLS if combine(p, f, False)}
        x, y, z = di.axis1(S), di.axis1(P), di.axis1(P, cells_used=di.CORE4)
        mine = [round(x["lower"], 4), round(x["upper"], 4), x["determined"], round(y["lower"], 4), round(y["upper"], 4), y["determined"], round(z["lower"], 4), round(z["upper"], 4)]
        th = [float(r[k]) if "." in r[k] else int(r[k]) for k in ("strict_lower", "strict_upper", "strict_cells_determined", "prov_lower", "prov_upper", "prov_cells_determined", "prov4_lower", "prov4_upper")]
        vals = [(P.get(f) or {}).get("value", "") for f in ("F1", "F2", "F4", "F7", "F8", "F9", "F10", "F3")]
        d = mine != th or vals != [r[f + "_value"] for f in ("F1", "F2", "F4", "F7", "F8", "F9", "F10", "F3")]
        bad += d
        if d: diffs.append(f"{p}: CSV {th} {[r[f + '_value'] for f in ('F1', 'F2', 'F4', 'F7', 'F8', 'F9', 'F10', 'F3')]} -> now {mine} {vals}")
    say(f"4. index CSV (strict, provisional, 4-cell, provisional cell values): {len(rows) - bad} of {len(rows)} projects identical")
    fail("4 index", bad, diffs)
    # 4b. The frozen rule outside the core (ADR-012 D2, reduce_v122.combine_models: same value, documented, quote) for comparison.
    tiers = {r["project"]: r["tier"] for r in rows}
    cnt = collections.Counter()
    for p, t in tiers.items():
        g = "core" if t in ("T1", "T2") else "T3"
        cm = rd.combine_models({k: red[m][p]["cells"] for m, k in MODELS.items()})
        for f in rd.MAKER_CELLS:
            cnt[(g, "keys")] += 1; cnt[(g, "frozen_D2")] += cm[f]["unanimous"]; cnt[(g, "strict")] += bool(combine(p, f, True))
    say(f"4b. keys with a value, 8 cells: core {cnt[('core','frozen_D2')]} (frozen ADR-012 D2 rule) vs {cnt[('core','strict')]} ('strict') of {cnt[('core','keys')]};"
        f" T3 {cnt[('T3','frozen_D2')]} vs {cnt[('T3','strict')]} of {cnt[('T3','keys')]}")
    say("   strict = all three models give the same value (no condition on evidence state or quote);"
        " provisional = at least one model gives a value and no model gives another")

    # 5. Talk measures: eligible units, own-voice relevant units, units without a majority, publications with own talk.
    def labels(stage, k):
        lab = {}
        for l in open(os.path.join(a.runs, "runs", f"PROD_{stage}_{k}", "ATTEMPTS.jsonl"), encoding="utf-8"):
            x = json.loads(l)
            if not x.get("complete"): continue
            t = x.get("text") or ""
            if stage == "L1P":
                for line in t.splitlines():
                    if "\t" in line: u, v = line.split("\t", 1); lab[u.strip()] = v.strip()
            else:
                t = t.replace("\nEND", "").strip()
                if t.startswith("```"): t = t.strip("`").split("\n", 1)[1]
                try: o = json.loads(t)
                except Exception: continue
                lab[o["unit_id"]] = o
        return lab
    L1 = {m: labels("L1P", k) for m, k in MODELS.items()}; L2 = {m: labels("L2", k) for m, k in MODELS.items()}
    maj = lambda xs: (lambda c: c.most_common(1)[0] if c and c.most_common(1)[0][1] >= 2 else (None, 0))(collections.Counter(x for x in xs if x))
    T = collections.defaultdict(collections.Counter); pubs = collections.defaultdict(set); pubs_u = collections.defaultdict(set)
    for d in csv.DictReader(open(manifest, encoding="utf-8")):
        if d["stratum"] != "evidence": continue
        p, k = d["project"], d["doc_key"]
        cf = os.path.join(a.units, k + ".candidates.csv")
        cand = {r["unit_id"] for r in csv.DictReader(open(cf, encoding="utf-8"))} if os.path.exists(cf) else set()
        for u in csv.DictReader(open(os.path.join(a.units, k + ".units.csv"), encoding="utf-8")):
            hit = bool(sc.BROAD.search(re.sub(r"\[[^\]\n]{1,120}\]", " ", u["text"])))
            if sc.excluded(u["text"], int(u["n_words"]), hit): continue  # stratum X
            T[p]["eligible"] += 1
            if u["unit_id"] not in cand: continue  # not a candidate: counted as not relevant
            rl, _ = maj([L1[m].get(u["unit_id"]) for m in MODELS])
            if rl is None: T[p]["nomaj"] += 1; pubs_u[p].add(k); continue
            if rl != "R": continue
            vo, _ = maj([(L2[m].get(u["unit_id"]) or {}).get("voice") for m in MODELS])
            if vo == "OWN": T[p]["own"] += 1; pubs[p].add(k); pubs_u[p].add(k)
            elif vo is None: T[p]["nomaj"] += 1; pubs_u[p].add(k)
    H = list(csv.DictReader(open(find(a.results, "CBDC_privacy_talk_hypothesis_PRELIMINARY_2026-11-24.csv"), encoding="utf-8")))
    bad = sum((T[r["project"]]["eligible"], T[r["project"]]["own"], T[r["project"]]["nomaj"], len(pubs[r["project"]])) !=
              (int(r["eligible_sentences"]), int(r["own_voice_relevant"]), int(r["no_majority"]), int(r["publications_with_own_talk"])) for r in H)
    say(f"5. talk counts (eligible, own-voice relevant, no majority, publications): {len(H) - bad} of {len(H)} projects identical")
    fail("5 talk", bad)
    say("   rule used: relevance = majority (2 of 3) label among R/N/U, voice = majority among the three L2 labels; no majority on"
        " either step = 'no majority'; non-candidates = not relevant; stratum X recomputed with select_candidates.excluded()")

    # 6. Hypothesis (Registration A §3) under both readings.
    LU, LU_fixed, D2 = {}, {}, {}
    cmb = {r["project"]: rd.combine_models({k: red[m][r["project"]]["cells"] for m, k in MODELS.items()}) for r in H}
    for r in H:
        p = r["project"]; el, own, nm, pb = T[p]["eligible"], T[p]["own"], T[p]["nomaj"], len(pubs[p])
        tl, tu = pb >= 2 and own * 100 / el >= 1, pb >= 2 and (own + nm) * 100 / el >= 1
        tu_fixed = len(pubs_u[p]) >= 2 and (own + nm) * 100 / el >= 1  # upper reading with the upper publication count
        com = und = 0
        for f in ("F1", "F2", "F4", "F7"):
            c = cmb[p][f]
            if not c["unanimous"]: und += 1; continue
            cs = [(red[m][p]["cells"].get(f) or {}) for m in MODELS]
            if c["value"] == di.PROTECTIVE[f] and all(di.committed(x, f) for x in cs): com += 1
        D2[p] = [tl and com + und < 2, tu_fixed and com < 2]
        res, LU_fixed[p] = [], []
        for strict in (False, True):
            com = und = 0
            for f in ("F1", "F2", "F4", "F7"):
                v = combine(p, f, strict)
                if not v: und += 1; continue
                cs = [(red[m][p]["cells"].get(f) or {}) for m in MODELS]
                if v == di.PROTECTIVE[f] and all(di.committed(c, f) for c in cs if c.get("value") == v): com += 1
            res += [tl and com + und < 2, tu and com < 2]; LU_fixed[p].append(tu_fixed and com < 2)
        LU[p] = res
    th = {r["project"]: [r[k] == "True" for k in ("meets_both_prov_lower", "meets_both_prov_upper", "meets_both_strict_lower", "meets_both_strict_upper")] for r in H}
    core = [r["project"] for r in H if r["tier"] in ("T1", "T2")]
    fail("6 hypothesis flags", sum(LU[p] != th[p] for p in LU), [f"{p}: CSV {th[p]} -> now {LU[p]}" for p in LU if LU[p] != th[p]])
    up = [p for p in core if LU_fixed[p][0] != LU[p][1] or LU_fixed[p][1] != LU[p][3]]
    say(f"6b. frozen ADR-012 D2 rule (combine_models, three models, documented, located quote), core:"
        f" L={sum(D2[p][0] for p in core)} U={sum(D2[p][1] for p in core)} (upper reading with the upper publication count)")
    say(f"6c. upper reading with the upper publication count (own talk or a unit without a majority): provisional"
        f" U={sum(LU_fixed[p][0] for p in core)}, strict U={sum(LU_fixed[p][1] for p in core)}; core projects whose upper flag"
        f" changes: {' '.join(up) or 'none'}")
    say(f"6. hypothesis flags identical for {sum(LU[p] == th[p] for p in LU)} of {len(LU)} projects;"
        f" core: provisional L={sum(LU[p][0] for p in core)} U={sum(LU[p][1] for p in core)},"
        f" strict L={sum(LU[p][2] for p in core)} U={sum(LU[p][3] for p in core)} (holds if L>=9, fails if U<=8)")

    # 7. PET mentions.
    pet = collections.Counter()
    for r in csv.DictReader(open(find(a.results, "CBDC_PET_observations_PRELIMINARY_2026-11-24.csv"), encoding="utf-8")):
        pet[(r["model"], r["table"] if r.get("table") else "")] += 1
    mine = {m: (sum(len(v.get("pet", [])) for v in red[m].values()), sum(len(v.get("pet_wholesale_context", [])) for v in red[m].values())) for m in MODELS}
    theirs = {m: (sum(n for (mm, t), n in pet.items() if mm == m and "wholesale" not in t), sum(n for (mm, t), n in pet.items() if mm == m and "wholesale" in t)) for m in MODELS}
    say("7. PET mentions (retail, wholesale context) reducer:", mine, "| CSV:", theirs, "IDENTICAL" if mine == theirs else "DIFFERENT")
    fail("7 PET", mine != theirs)

    say("Not recomputed here: cell history and change log (cell-history-2026-11-24/), committed-PET table, figures, talk"
        " mechanism and decision shares, directional gap. Their generators were not committed.")
    say("RESULT:", "everything identical" if not fails else "DIFFERENCES in " + "; ".join(f"{k} ({v})" for k, v in sorted(fails.items())))
    with open(os.path.join(a.work, "RECOMPUTE_REPORT.txt"), "w", encoding="utf-8", newline="\n") as fh: fh.write("\n".join(out) + "\n")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
