# ADR-005: independent audit of 13 Nov 2026, author decisions and dispositions

Status: decisions of MB of 13 Nov 2026 recorded; DS to confirm. Audit: `docs/audits/INDEPENDENT_AUDIT_2026-11-13.md` (prompt and brief beside it). The auditor's verdict was not to start the main human coding round with the workbooks of 13 Nov; that round has not started and its sample is withdrawn.

## 1. Author decisions (MB, 13 Nov 2026)

1. **RECHECK documents.** All 88 decided (`data/manifest/AUTHOR_DECISIONS_2026-11-13.csv`, SHA-256 of the returned workbook inside): KEEP 11, COMPANION 12, DROP 65. No RECHECK row remains. CA and JM move to T1; AE, ID and SZ to T2.
2. **The euro area is a project of its own and is analysed like a national project.** This overrides the auditor's reading (item 16) and ADR-001 F9 for the descriptive analysis: the analytic frame is 44 projects = 43 national retail candidates + the digital euro (`analytic_frame` in `data/frame/projects.csv`). Analyses that need a country-level covariate stay on the 43.
3. **Year-by-year series are kept.** The form in which they can be defended is in section 4.
4. **Which facets survive is decided on evidence**, by a development sample coded by both authors, not in advance (section 4).
5. Agreed: complete the judgement of the 86 translation pairs and add a sample of the unmatched sentences; draw a new agreement sample only after the repairs.

## 2. Repairs done on 13 Nov

| audit item | repair |
|---|---|
| 2 (duplicate editions, benchmark leak) | `data/manifest/EDITION_LINKS.csv` (4 pairs: Norges Bank memos 1/2018, 2/2019, 1/2021; BoJ pilot report). A publication is counted once in the tiers and read once, through the issuer's English edition; a translation with priority BENCH is never production text (`build_tier_workbook.py`, `unitise.py`). |
| 3 (run logs) | `data/translation/runs/*/CALLS.csv` and `RUN_META.json` were excluded by `.gitignore`; now committed. |
| 5 (scorer) | `score_agreement.py`: alpha undefined (not 1) when all ratings fall in one category, AC1 on the declared category list, undefined bootstrap replicates counted, duplicate ids and undeclared values stop the run, blanks reported, end-to-end facet score added; `tests/test_score_agreement.py` with the auditor's hand examples. |
| 16 (frame) | explicit `analytic_frame` column; counts below are for the 44-project frame. |

State after the repairs: 289 evidence rows = 285 publications in 44 projects; tiers T1 13, T2 13, T3 18; 258 documents unitised (A 198, B 18, D 42), 190 695 units, 19 526 candidates; 42 projects have text (CL and CZ have none); 27 evidence documents have no English text. 153 evidence rows are still evidence by model pre-screen only.

## 3. Repairs still to do before any coding

Shared context for humans and models (the paragraph, not adjacent units); two status axes and rule A in the talk schema, prompt and Czech codebook; fragment rule X (it removes "No identification required."); dictionary gaps (AML/CFT monitoring, retention, encryption, zero-knowledge); fail-closed translation ingest; importer of the authors' workbook decisions with a round-trip test; tests for tiers, routing, ingest, units; date precision and cutoff eligibility for the 162 rows without a full date; versioned unit ids bound to the text hash; re-translation of the three column-layout documents; translation of ID CAND-096, CAND-099 and CL CAND-057 (new evidence without English text).

## 4. Proposals awaiting the authors

**Development sample before the main sample (answers decision 4).** About 120 units, all six facets, with status coded on the contract's two axes, both authors, then scored. Facets that reach the threshold are kept; the others are merged or dropped. The model may be tuned on this sample. The main sample of 400 is drawn afterwards from the final document set and is not used for tuning, so it is a clean reference for the model.

**Yearly series (answers decision 3).** Measured on the corrected units, a T1 project has a median of 2 evidence documents per year and 46 % of its project-years rest on a single document (T2: median 1, 52 %). With a project share of variance near 0.15, a yearly *share of privacy sentences per project* is mostly the choice of document. Three forms avoid this:
- corpus-level yearly series with intervals (2021 to 2025 have 36 to 49 documents of 22 to 26 projects per year; dictionary share 4.0 to 6.2 % with document-bootstrap intervals of about ±1.5 to 3 points);
- per project, an event history instead of a share: the year in which each aspect is first stated in the issuer's own voice, first given a mechanism or legal basis, first endorsed, first operational. Each point is one located, dated statement, so it does not depend on how many documents the year has;
- per project, the documents as dated points on a timeline (no line through them), for T1 and T2.

**What replaces the dropped constructs.**
| dropped | replaced by | why it reaches the same aim |
|---|---|---|
| Talk index minus Commitment index | per aspect, a 2 × 2 table of projects: own-voice statement about the aspect (yes / no) × admissible commitment in the matching F-cell (yes / no) | "talk without commitment" becomes a count of named projects with locators, not a difference of two scales |
| ranking of projects by amount of privacy talk | highest rung reached per aspect (declaratory, policy, legal or architectural basis, endorsed, operational), with the number of documents beside it | an existence claim with a source, checkable by a reader |
| "the project is silent" | "no own-voice statement found in the searched corpus", with the number of documents searched and the upper bound from the random control | says what was measured |
| sentence-to-cell funnel | four nested shares over units (relevant / eligible, own voice / relevant, with basis / own voice, endorsed / with basis) plus a separate coverage table of F-cells per project | each ratio has one unit and one denominator |

## 5. Open questions

- ECCU (DCash) is a union project with one evidence document. By the rule of decision 2 it would also enter the frame; it is outside for now.
- Retire the posture layer P0 to P3 / G1 to G9 of the contract in favour of the unit-based instrument (audit item 11)? Not yet decided.
- CH: MB asks to check the SNB speech against the Federal Council's 2019 position; the project's status in the frame is to be re-checked.
- Two document universes (audit item 9) are not feasible by December; the proposal is to name the result "privacy statements in the selected evidence corpus" and to make no claim about an institution's communication as a whole.
