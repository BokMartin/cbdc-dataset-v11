#!/usr/bin/env python3
"""One-command re-run of the machine part of the procedure from the repository (pipeline/README.md).

Stages (each is an existing script; nothing here is new logic):
  frame      scripts/frame/project_frame.py            registry -> data/frame/projects.csv
  texts      (input) page-delimited texts per project  <texts>/<JUR>/DOCS.csv + texts/docNN.txt (made from the PDFs with pdftotext; see README)
  census     scripts/census/endorsement_census.py      sealed per-project endorsement census (aggregate committed)
  survey     scripts/census/posture_survey.py          sealed statement-type survey (aggregate committed)
  extract    scripts/extraction/extract_api.py         per project, --mode single|two-stage|both
  verify     scripts/extraction/verify_quotes.py       citation check of every fill
  compare    scripts/extraction/compare_modes.py       single vs two-stage (when both)
  prompts    scripts/pipeline/export_prompts.py        rendered prompts + hashes
  site       scripts/site/build_site_data.py           website data (development profiles + released statements only)
Human stages (reference coding, adjudication, blind draw, release of sealed results) are NOT run here; see README.

usage: run_all.py --provider anthropic --model claude-opus-5-5 --texts /path/texts --sealed-dir /path/outside/repo \
         --contract archive/v11/docs/MEASUREMENT_CONTRACT_v1_1_2026-10-18.md --schema schema/cells_v1_1.json \
         [--projects NO,UK] [--mode both] [--stages frame,prompts,census,survey,extract,verify,compare,site] [--dry-run]
Provider API key from the environment (ANTHROPIC_API_KEY / OPENAI_API_KEY). Every API stage writes its own manifest and request archive.
"""
import argparse, csv, glob, os, subprocess, sys, datetime as dt
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def sh(cmd, dry):
    print("$", " ".join(cmd), flush=True)
    if not dry: subprocess.run(cmd, check=True, cwd=ROOT)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--provider", default="anthropic"); ap.add_argument("--model", required=True); ap.add_argument("--texts", required=True); ap.add_argument("--sealed-dir", required=True)
    ap.add_argument("--contract", required=True); ap.add_argument("--schema", required=True); ap.add_argument("--projects", default=""); ap.add_argument("--mode", default="both")
    ap.add_argument("--stages", default="frame,prompts,census,survey,extract,verify,compare,site"); ap.add_argument("--outroot", default=os.path.join(ROOT, "runs")); ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(); st = set(a.stages.split(",")); py = sys.executable; d = a.dry_run
    frame = os.path.join(ROOT, "data/frame/projects.csv")
    if "frame" in st: sh([py, "scripts/frame/project_frame.py"], d)
    if "prompts" in st: sh([py, "scripts/pipeline/export_prompts.py", "--contract", a.contract, "--schema", a.schema], d)
    if "census" in st: sh([py, "scripts/census/endorsement_census.py", "--texts", a.texts, "--frame", frame, "--contract", a.contract, "--provider", a.provider, "--model", a.model,
                          "--sealed-out", os.path.join(a.sealed_dir, "ENDORSEMENT_CENSUS_sealed.jsonl"), "--aggregate-out", "data/census/ENDORSEMENT_CENSUS_aggregate.json"] + (["--only", a.projects] if a.projects else []), d)
    if "survey" in st: sh([py, "scripts/census/posture_survey.py", "--texts", a.texts, "--frame", frame, "--provider", a.provider, "--model", a.model, "--max-tokens", "40000",
                          "--sealed-out", os.path.join(a.sealed_dir, "POSTURE_SURVEY_sealed.jsonl"), "--aggregate-out", "data/census/POSTURE_SURVEY_aggregate.json"] + (["--only", a.projects] if a.projects else []), d)
    projects = a.projects.split(",") if a.projects else [r["project"] for r in csv.DictReader(open(frame, encoding="utf-8")) if r["retail_candidate"] == "True"]
    runs = {}
    for p in projects:
        indir = os.path.join(a.texts, p)
        if "extract" in st:
            sh([py, "scripts/extraction/extract_api.py", "--jur", p, "--provider", a.provider, "--model", a.model, "--mode", a.mode, "--indir", indir, "--contract", a.contract, "--schema", a.schema, "--outroot", a.outroot], d)
        cands = sorted(glob.glob(os.path.join(a.outroot, f"{p}_{a.provider}_*"))); run = cands[-1] if cands else None; runs[p] = run
        if run and "verify" in st:
            for f in glob.glob(os.path.join(run, "FILL_*.csv")):
                if not f.endswith(".verified.csv"): sh([py, "scripts/extraction/verify_quotes.py", f, indir], d)
        if run and "compare" in st and os.path.exists(os.path.join(run, "FILL_single.verified.csv")) and os.path.exists(os.path.join(run, "FILL_two_stage.verified.csv")):
            sh([py, "scripts/extraction/compare_modes.py", os.path.join(run, "FILL_single.verified.csv"), os.path.join(run, "FILL_two_stage.verified.csv"), "--labels", "single", "two_stage", "--out", os.path.join(run, "COMPARISON_single_vs_two_stage.csv")], d)
    if "site" in st: sh([py, "scripts/site/build_site_data.py"], d)
    print("done", dt.datetime.now(dt.timezone.utc).isoformat(), {p: (os.path.basename(r) if r else None) for p, r in runs.items()})

if __name__ == "__main__": main()
