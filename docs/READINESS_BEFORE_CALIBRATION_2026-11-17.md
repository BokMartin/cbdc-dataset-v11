# Readiness before calibration and before the paid production runs (17 Nov 2026)

Prepared by the pipeline author from the repository state at the commit of this file; every row can be recounted from the file named. "Blocks" says what cannot start while the row is open: **C** = calibration of the talk prompts, **P** = production runs of the talk classification, **F** = F-cell extraction, **Z** = freeze and registration.

## Verdict

Calibration of the talk prompts can start once rows 2, 12, 16 to 18 and 21 are closed and the authors have answered rows 8 and 10. Production cannot start before rows 3 to 6, 13, 15 and 23. F-cell extraction additionally needs row 9, which is the largest open item: the contract and the extraction prompts are not at v12.

## A. Documents

| # | Item | State | Blocks | Who |
|---|---|---|---|---|
| 1 | Evidence set decided | done by MB (234 rows, 230 publications); DS has not confirmed | Z | DS |
| 2 | Duplicate text in the corpus | `IL_BoI_2024` and `CAND-111` have the same text hash; counted twice in units (2,187 units). Israel stays T1 with 8 publications, exactly at the threshold | C (pool), P | Claude, after MB's yes |
| 3 | **Non-English evidence of T3 projects was never translated** | translation was scoped to T1 and T2 (`docs/TRANSLATION_PROCEDURE.md`, Scope). 14 documents, 255 pages, 7 projects: CL 3, CZ 3, IS 3, UY 2, HU 1, MG 1, TR 1. **Chile and Czechia have no readable document at all**; IS, MG, UY are left with one. English-language T3 projects are read in full, so T3 coverage depends on language | P | authors decide: translate (estimate 10 to 20 USD) or state the exclusion |
| 4 | Evidence documents without a usable file | 5 without a file (IN 3, MO 1, NG 1: the eNaira Design Paper), 3 scans that need OCR (JM, MO, NG) | P for those projects | MB (manual download); authors on OCR |
| 5 | PE `CAND-250` re-translation | waiting for OpenAI credit | P | MB (credit) |
| 6 | General rule for page spans of general publications | proposed (ADR-006 B.5), not decided; one document has a span today | P, F | authors |

## B. Instrument

| # | Item | State | Blocks | Who |
|---|---|---|---|---|
| 7 | Talk codebook, schema, prompts | draft v0.3; v0.2 was audited (A3), v0.3 was not | Z | audit A4, then authors |
| 8 | Unusable units | MB marked 24 of 120 development units "U": headings, list items, table cells, and some complete sentences. Unit boundaries are fixed (identifiers); the open question is whether fragments are removed by the candidate rule or left to the models' U label | C | authors, after the audit |
| 9 | **Measurement contract and extraction prompts** | contract v12 and `schema/cells_v12_DRAFT.json` are drafts; the three extraction prompts are written for contract v1.1 | F | authors adopt; Claude updates prompts; calibration on NO and UK only |
| 10 | Combination rule for three models; facets on the union of relevant units | proposed (calibration draft, section 7) | C (round design), Z | authors |

## C. Human inputs

| # | Item | State | Blocks | Who |
|---|---|---|---|---|
| 11 | MB blind relevance, 120 units | done (`data/units/DEV_LABELS_MB_2026-11-17.csv`); two rows not filled, meaning of "U" on complete sentences open | — | MB |
| 12 | DS blind relevance, 120 units | announced for 17 Nov | C | DS |
| 13 | DS confirms ADR-004, ADR-005, ADR-006 | open | P, Z | DS |
| 14 | Translation judgement | MB judged 86 matched pairs; sub-coding of 24 "meaning differs" pairs and 30 unmatched sentences open; DS has not judged | claims that rest on machine-translated text | MB, DS |
| 15 | Issuer and voice of each document | pre-filled by a model, not confirmed by an author; **the facet prompt receives the document header (issuer, type, year) as input** | P (facets) | authors |

## D. Infrastructure

| # | Item | State | Blocks | Who |
|---|---|---|---|---|
| 16 | Runner for three providers with run record, batch where offered, idempotent, cost cap | not built | C | Claude |
| 17 | Request builder | draft (`scripts/units/build_requests.py`), single and page form | C | Claude |
| 18 | Draw of C1 to C3 | `draw_agreement_sample.py` exists; needs new seeds and exclusion of C0 | C | Claude |
| 19 | Verification workbook with pre-filled majority labels and planted errors; its scorer | not built | P (reference stage) | Claude |
| 20 | Run record specification and CI check | done (`docs/RUN_RECORD_SPEC.md`, `scripts/pipeline/run_statement.py`) | — | — |
| 21 | Accounts and credit | Anthropic: API credit of the Max plan to activate, spend limit to set; OpenAI: top-up; DeepSeek: account and key | C | MB |
| 22 | Exposure ledger | entry for the calibration rounds to be added when round 1 opens | C (formality) | Claude |
| 23 | Registration (OSF) and archive DOI (Zenodo) | not started | Z | authors |
