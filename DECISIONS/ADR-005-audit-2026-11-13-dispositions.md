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

## 6. Decisions of MB, 13 Nov 2026, 14:42

1. **Year-by-year output per project is the event history** (first own-voice statement, first with a mechanism or legal basis, first endorsed, first operational, per aspect), with the corpus-level yearly series beside it. A yearly share per project is not reported.
2. **Narrowing accepted**; which facets stay is decided by the development sample (`docs/TALK_AGREEMENT_PROTOCOL_v2_2026-11-13.md`).
3. **ECCU stays outside the frame.** The frame is 44 projects: 43 national retail candidates and the digital euro. The euro area is included as the one union project with a retail CBDC under preparation and a large evidence base; this is an author choice and is stated as such.
4. **The posture layer P0 to P3 / G1 to G9 is retired** in favour of the unit-based instrument. To do: contract section 6b, `scripts/derive.py` (`posture_level`), its tests, the site; the outputs of 2 Nov stay archived as development artefacts.
5. Translation of the new non-English evidence with the same model and prompt (run `openai_gpt-6-astra_api_20261113`).

## 7. Done on 13 Nov after these decisions

- Talk schema v0.3, L1 prompt v0.2, L2 prompt v0.3, Czech codebook v0.3: decision and implementation as two axes, rule A in both languages, `stance` (PROTECTS / EXPOSES) instead of `direction`, basis must belong to the coded statement, REJECTED removed, flags as three fields, the aspect-to-cell map reduced to comparison pairs that never set a cell, the funnel replaced by nested shares, the 2 × 2 table, the highest rung and the event history.
- One context rule for coders and model (`scripts/units/context.py`).
- Candidate rule v2: short dictionary hits are no longer excluded, boilerplate only when it is not a sentence, dictionary extended (AML/CFT, monitoring, retention, encryption, zero-knowledge, "cannot see").
- Translation text mode: a PDF with column gaps on at least 15 % of its long lines is translated from reading-order text; `data/translation/PAGE_SPANS.csv` limits a general publication to the pages that name the CBDC (first use: Indonesian Law 4/2023, 9 of 819 pages).
- ID CAND-099 (Blueprint 2030) has an issuer English edition on bi.go.id: route B, not machine-translated; the file is still to be downloaded and its page count compared.
- CL CAND-057 is a T3 document and stays untranslated like the other non-English T3 evidence (translation scope is T1/T2).
- Translation run `openai_gpt-6-astra_api_20261113`: 11 calls, all complete (ID CAND-096; TW CAND-345 and CAND-350 re-translated from reading-order text and replacing their first translations). PE CAND-250 was not re-translated: the API account ran out of credit; its first translation (from layout text, column gaps on 45 % of long lines) stays in use and is flagged.
- Development sample drawn: 120 units, 38 projects, 82 documents (`data/units/AGREEMENT_SAMPLE_dev_2026-11-13.csv`); workbooks for MB and DS outside the repository.
- Units after all changes of the day: 259 documents (A 198, B 18, D 43), 190 890 units; candidates D 8 528, N 6 484, R 6 244 (21 256); X 49 452.

## 8. Confirmation of the 153 pre-screened evidence documents (MB, 13 Nov 2026, 17:12)

MB reviewed all 153 documents that were evidence by the model pre-screen only (`CONFIRM_EVIDENCE_v12_2026-11-13.xlsx`, read by `scripts/review/read_tier_decisions.py`; SHA-256 of the returned workbook in the files): 104 confirmed (`data/manifest/AUTHOR_CONFIRMATIONS_2026-11-13b.csv`), 49 changed (`AUTHOR_DECISIONS_2026-11-13b.csv`: COMPANION 45, DROP 3, BORDERLINE 1). No evidence document rests on a model proposal any more: of 241 evidence rows (237 publications), 121 carry the authors' v11 verdict and 120 an author decision or confirmation of 11 to 13 Nov.

Effect: tiers are now T1 8 (EU, IL, JM, JP, KZ, SE, TW, UK), T2 9 (AU, BS, CA, HK, ID, IN, NO, NZ, RU), T3 27. Fourteen projects moved down one tier. Thirteen T3 projects have exactly four evidence documents and three T2 projects exactly seven, one short of the next tier: the tier of 16 of 44 projects depends on a single document.

Units after these decisions: 212 documents (A 166, B 15, D 31), 176 858 units, 20 323 candidates (D 8 184, N 6 273, R 5 866). ID CAND-099 is read through Bank Indonesia's English edition (52 pages, SHA-256 f4d9b022…f71a186, fetched 13 Nov). Nine of the 120 development-sample units belong to documents that are no longer evidence; they stay in the development sample, which tests the codebook and not the corpus.

Flagged for the authors (pipeline author's note, not a decision): among the 45 documents moved to COMPANION are seven legal texts (RU federal laws 339-FZ, 340-FZ, 105-FZ, 248-FZ; KZ Law on payments and NBK Resolution 42; AE Decree-Law 54/2023) and several status decisions (NO Dec 2025 recommendation, UK statements). Legal texts are the only source of basis LEGAL / decision ENDORSED for the two live projects RU and KZ, and of the lawful-access cell F3. Whether COMPANION documents may still be cited for project status and for F-cells, while being left out of the talk measurement, is not written down anywhere and needs a rule.
