# Audit brief, 17 November 2026: before the paid model runs

Written by the pipeline author (Claude). **This is the defendant's statement, not evidence.** Every claim names the file it can be checked against.

## 1. What the paper is

A measurement-and-data article for *Data & Policy*: an open, auditable dataset of how the bodies that design retail CBDCs (mostly central banks) talk about user privacy and what they commit to, for 44 projects (43 national retail projects and the digital euro). Two layers: (i) **privacy talk**, sentence units of official documents labelled for relevance and seven facets (ADR-004, `schema/talk_units_v13_DRAFT.json`); (ii) **commitments**, twelve feature cells per project extracted under a measurement contract with verbatim located quotes (`docs/MEASUREMENT_CONTRACT_v12_DRAFT.md`). Outputs: a talk × commitment table by aspect, an event history per project, a yearly series for the corpus. No causal claims. Overview: `PROJECT_BRIEF.md`.

## 2. What exists (recount from the files)

- Corpus: 234 evidence rows = 230 publications decided by an author; 208 documents with English text (163 English originals, 15 issuer English editions, 30 machine translations by gpt-6-astra), 42 of 44 projects: `data/manifest/CORPUS_DOCUMENTS_2026-11-17.csv`, `CORPUS_COVERAGE_2026-11-17.csv`.
- Units: 174,052 sentence units; 20,059 candidates for classification (dictionary hit 8,088, neighbour 6,231, random control 5,740): `data/units/`.
- Human input so far: MB coded relevance blind for 120 development units (R 58, N 36, U 24, 2 empty): `data/units/DEV_LABELS_MB_2026-11-17.csv`. MB judged 86 translation pairs: `data/translation/benchmark/JUDGEMENT_RESULT_MB_2026-11-17.json`. DS: nothing returned yet.
- Model runs so far: three translation runs and development extractions for Norway and the UK: `docs/RUN_STATEMENT.md`. **No unit has been labelled by a model.**

## 3. What the authors decided since the audit of 13 Nov (ADR-005, ADR-006)

1. The euro area is a project of its own (frame of 44). ECCU is out.
2. Legal texts of parliaments and governments are companion documents: cited for state and timeline, never a source of talk units.
3. **The authors will not code the seven facets blind.** MB did relevance blind and declined the rest (effort out of proportion; the data of the paper are the model's labels). Validation is by verification of pre-filled labels, with four safeguards: relevance stays blind and independent; planted errors measure the detection rate of the verification; every project-level statement of the paper is checked against its source sentence; the other facets are described as model-coded and verified (ADR-006 A).
4. **All candidate units and all F-cells are run in full on three models**: claude-opus-5-5, gpt-6-astra, deepseek-v4-pro (chosen as an inexpensive non-Western model). The paper reports agreement and each model's results.
5. Target: all model runs done by 30 November.

## 4. What is proposed and not decided

- Calibration procedure: `docs/CALIBRATION_PROTOCOL_DRAFT_2026-11-17.md` (factor tests, three rounds of 60 units, change rule, regression, freeze, majority of three, facets on the union of relevant units).
- Run design to save cost (ADR-006 B): page-packed requests, low reasoning setting, Batch API, replicate with the same model on a 20 % subsample, page spans for general publications, one primary extraction mode.
- What every run stores: `docs/RUN_RECORD_SPEC.md`; what the paper states: generated `docs/RUN_STATEMENT.md`.
- Readiness list: `docs/READINESS_BEFORE_CALIBRATION_2026-11-17.md`.

## 5. Money at stake (estimates at list prices of 17 Nov, not measurements)

Three models, full scope, with the cost measures: 320 to 455 USD, up to about 600 USD with a 30 % reserve for re-runs; without the measures two to four times that. The largest share is gpt-6-astra. A design error found after the production runs costs a full re-run and, with the deadline, probably a cut in scope.

## 6. Weaknesses the author already admits

1. Facet validity rests on anchored verification by, in practice, one author; inter-coder agreement exists for relevance only (and only once DS has coded).
2. Translation: 31 % of matched benchmark sentence pairs were judged "meaning differs" by MB (weighted), not yet broken down; the benchmark covers five documents and three languages.
3. Coverage depends on language in T3: non-English T3 evidence was never translated; Chile and Czechia have no readable document (readiness row 3).
4. One duplicate text in the corpus (readiness row 2); five evidence documents without a file, three scans.
5. The contract for the commitment layer is a draft and the extraction prompts are one version behind (readiness row 9).
6. The issuer and type of each document, which the facet prompt receives as input, were pre-filled by a model and not confirmed by an author.
7. 20 % of the development units were marked unusable by MB; the unit rule was audited in version 1 only.
8. Model identifiers are aliases chosen by the providers (`claude-opus-5-5`, `gpt-6-astra`, `deepseek-v4-pro`); DeepSeek repointed an alias in October 2026 according to secondary sources; a bit-identical re-run is not possible with any of them.
9. Source texts, translations and unit texts cannot be published (issuers' copyright); the repository holds hashes, locators and labels. A reader can verify, but cannot re-run, without collecting the documents again from the listed URLs.
10. The pipeline author is itself one of the three models' vendors' products (Claude wrote the prompts that claude-opus-5-5 will run); the prompts were never tuned on another model's output.
11. The cost estimates rest on token counts of one tokenizer and an assumed factor for the others; reasoning tokens of the classification have not been measured.
12. The steps changed after commit `4d4f142` (audit A3) have not been audited: document decisions and companion rule, translation run 3 with the reading-order rule, unitisation version 2, schema and prompts v0.3, ADR-006.
