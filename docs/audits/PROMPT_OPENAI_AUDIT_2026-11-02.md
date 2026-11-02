# Prompt for an independent audit (paste into ChatGPT / OpenAI model with the attached zip)

You are an independent methodological and technical auditor for an academic measurement-and-data paper (target journal: Data & Policy, Cambridge). The authors (two economists, Prague University of Economics and Business) are building an open, auditable dataset of how central banks document the privacy and identifiability architecture of retail CBDCs. Their technical collaborator (an LLM, Claude) did one day of work on 2 November 2026 and the authors want **every claim from that day verified by a second, independent model before it is used**. You have no stake in the result. Be adversarial, specific and brief. Where you cannot verify something, say "not verifiable from the pack" rather than guessing.

## What you receive

`cbdc-dataset-v11_audit_pack_2026-11-02.zip` contains:
- `repo/`: the full repository as committed (12 commits on 2 Nov, listed in `repo/GIT_LOG_2026-11-02.txt`): scripts (Python), tests, documents, data exports, website source.
- `TEXTS_INDEX.csv`: the index of the 132 page-delimited document texts used as inputs (the texts themselves are not included: copyright; the registry carries URL and SHA-256 of every PDF).
- This prompt.

Not included, by design: the sealed per-project results of two model-only surveys (the "endorsement census" and the "posture survey"). Only their aggregates and the SHA-256 of the sealed files are in `repo/data/census/`. **Do not try to reconstruct per-project values** (the authors must not see them before a blind draw; see `repo/EXPOSURE_LEDGER.md`).

## Read first, in this order

1. `repo/README.md`, `repo/PROGRESS_cs.md` (Czech; a one-page status), `repo/DECISIONS/ADR-001-consultation-2026-10-28-dispositions.md` (what an earlier consultant recommended and what the authors decided).
2. `repo/docs/MEASUREMENT_CONTRACT_v1_1_2026-10-18.md` (the instrument in force) and `repo/docs/MEASUREMENT_CONTRACT_v2_DRAFT_2026-11-02.md` (the draft that today's work feeds).
3. `repo/docs/CONSULTATION_BRIEF_2026-11-06_cs.md` (Czech; the authors' decision sheet for Friday). Everything in it must be traceable to files in the pack.

## What to verify (answer each item; cite file paths and line numbers or cell coordinates)

**A. Code and tests**
1. Run `pytest` in `repo/` (Python 3.11+, pandas, openpyxl needed; no API key needed). Report the result. If you cannot execute code, read `repo/tests/*.py` and state for each test whether the asserted behaviour matches the code it tests.
2. `repo/scripts/derive.py`: does `admissible()` implement rule C of contract v2 §5 exactly (value yes/no, evidence_state documented, status endorsed/adopted or operational)? Is it symmetric for yes and no? Does `posture_level()` match contract v2 §6b.2 (including: unlocated quotes never count; LAWFUL_ACCESS/PROGRAMMABILITY/RISK/OTHER never count)?
3. `repo/scripts/extraction/verify_quotes.py`: can a prefix-only match still pass? Can a quote on the wrong page be reported as `exact_page`? Is the state order (exact_page → elsewhere_in_doc → spanning_pages) sound?
4. `repo/scripts/extraction/compare_modes.py`: can a comparison with a failed document be reported as VALID?
5. `repo/scripts/census/endorsement_census.py` and `posture_survey.py`: does any per-project value reach a committed file? Check `data/census/*.json` for anything that identifies a project.
6. `repo/pipeline/PROMPTS.json` + `prompts/*.md`: do the SHA-256 values match the hashes recorded in `repo/data/worked_profiles/runs_v2_NO/MANIFEST.json` (`single.request.system.sha256`), `runs_v2_UK/MANIFEST.json`, and `data/census/ENDORSEMENT_CENSUS_aggregate.json` (`system_sha256`)? Recompute at least one hash yourself.

**B. Data claims made today (each must be reproducible from the pack)**
7. Project frame: `data/frame/projects.csv` gives 48 projects / 46 national / 43 retail candidates. Count them. Are the exclusions (unions; BO, BR, US) documented in `PROJECT_FRAME.md` with reasons?
8. Endorsement census aggregate (`data/census/ENDORSEMENT_CENSUS_aggregate.json`): 43 projects, categories endorsed_no 3 / endorsed_yes 2 / operational_undocumented 3 / proposal_only 16 / tested_only 9 / none 10. Do the counts sum to 43? Is the conclusion in the brief ("Y₁ determinable for ~5–8 projects; orientation rule ≥ 20 not met") a correct reading of these numbers under rule C?
9. Posture survey aggregate (`data/census/POSTURE_SURVEY_aggregate.json`): 125 documents, 2,628 statements. Do the per-type counts in `docs/PRIVACY_POSTURE_LAYER_DESIGN_2026-11-02.md` §1 match the JSON? Do the "retail projects with ≥ 1" numbers match `retail_projects_with_type`?
10. Norway single vs two-stage (`data/worked_profiles/runs_v2_NO/COMPARISON_single_vs_two_stage.csv`): 4 full / 7 value / 6 differ, both FILLs with all rows `ok` or `ok_with_validation_problems`, citations 17/17 `exact_page` in both `.verified.csv`. Recount from the CSVs.
11. UK (`runs_v2_UK/`): 3 / 12 / 2; single 11 exact + 5 `elsewhere_in_doc` + 1 `invalid_locator`, two-stage 17/17. Check the five mislocated quotes: is the claimed constant offset (doc 3: +4; doc 4: +2) consistent with the `page` values in the CSV?
12. Norway route B (`runs_v2_NO_en/`): EN vs NB single 3 / 11 / 3; the claim that F1 "flips between no and n/d across four runs, always partial, never admissible". Verify from the four FILL files (runs_v2_NO single and two_stage; runs_v2_NO_en single and two_stage).
13. Language detection (`data/frame/doc_language_detect.csv`): 9 flagged labels, listed in `docs/LANGUAGE_LEDGER.md`. Are the nine rows flagged in the CSV the same nine named in the ledger? After the amendment (`data/registry/REGISTRY_AMENDMENT_2026-11-02.csv`, applied by `scripts/frame/registry.py`), is the count "105 English / 20 non-English core documents" correct? (Recompute from REGISTRY_v2_2.csv + the amendment.)
14. Source URLs (`data/registry/SOURCE_URL_AMENDMENT_2026-11-02.csv`): 73 rows, 72 with a URL, 60 marked hash-identical. Spot-check **five** URLs of your choice by opening them: does the page exist and match the document (title, year)? Report which five.
15. Reuse terms (`data/registry/LICENCES_BY_INSTITUTION_2026-11-02.csv`, `DOC_LICENCES_2026-11-02.csv`): class counts 59 / 42 / 14 / 10. Spot-check **three** institutions' terms pages (open the `terms_url`) including the Bank of England classification as all-rights-reserved and HM Treasury as OGL.
16. Website data (`site/assets/data.json`, `scripts/site/build_site_data.py`): are the Norway and UK profiles labelled as development/not validated? Do their `statements` carry `verified` states and `doc_url` from the registry? Is any project other than NO and UK carrying real statements (it must not)?

**C. Methodology (judgement, with reasons)**
17. Contract v2 §6b posture layer: is the P0–P3 ladder well defined and mutually exclusive? Is there any way a G-indicator could be read as a commitment? Is "sensitivity without loosening the definition" achieved, or is this the v1 problem (conditional statement = commitment) returning under another name?
18. The brief's framing for Friday: given the census aggregate, is the recommendation (measurement-and-data paper as the core; H2 at most exploratory on the status-attached view) the right reading, or is there a defensible alternative the authors should hear?
19. Exposure: does anything in the pack or in today's work expose per-project values of unexposed projects to the authors? Check the website build, the aggregates, the design memo's example quotes (must be NO/UK only), and the commit messages.
20. Single vs two-stage: is the pack's reading ("values agree; status labels and locators differ; single mode mislocates pages in very long requests") supported by both NO and UK, and what routing rule would you register (ADR E12)?
21. Language: given that 11 of the core documents in the 43-frame are non-English (7 projects) and only Norway has an issuer English edition, is the authors' "English-accessible domain" framing honest, and what should the registration say about CL, RU, TW, CZ, CN, UA?

## Output format

A numbered report, item by item (1–21), each with: **verdict** (confirmed / confirmed with correction / not confirmed / not verifiable from the pack), the evidence (file, line or cell), and, where relevant, the fix. Then a ranked list of the five most serious problems you found, and a one-paragraph overall judgement. Write in English. Do not pad; do not restate the pack's own text back; do not soften findings.
