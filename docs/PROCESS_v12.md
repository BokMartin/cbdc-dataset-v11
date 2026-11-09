# The v12 process, step by step (for the consultation of 6 November 2026)

## What the reader wants to know

**Reader question 1 (the frame).** In what state are retail CBDC projects, and why do their issuers say they want them, according to their own documents? Path: source manifest → status decisions found by the gap check → F11 declared objectives with quotes → claim history. Output: status table of 43 projects with the deciding document; objectives table (eight atomic tags with status, one quote per tag); change map. Difference from trackers: every entry is a located, status-attached claim from the issuer; silence is reported as silence.

**Reader question 2 (the core).** When a central bank says its digital currency will respect privacy, has it actually committed to a design in which it cannot see who pays whom, and how many have? Path: the same manifest → extraction of F1–F12 and every privacy statement → citation check → human reference and audit → commitment matrix (rule C) and posture layer through one derivation module. Output: talk (P0–P3, G1–G9 with status), commitments (F1, type A0–C1), and the commitments that disappear under strict rules, side by side; co-occurrence of "will not see" and "will see" statements within projects, dated. Difference: talk and commitment measured by the same instrument on the same documents, never mixed; the gap is the finding, with a document and page behind every cell.

One line per step. Status as of 3 Nov 2026 in brackets.

1. **Fix the question and the unit.** Who is documented as able to link a retail CBDC payment to a person, under what status, with what uncertainty. Unit = one CBDC project under one decision authority. [done]
2. **Collect CBDC documents.** Official central-bank and government publications on CBDC, all jurisdictions. Registry of 391 documents, 85 jurisdictions, each with URL and SHA-256. [done, frozen 18 Oct]
3. **Separate official from non-official.** Keep only documents published by the competent body on its own channel (central bank, ministry, legislature, union authority). BIS, IMF, consultancies, media, trackers are never evidence. [rule D1 written]
4. **Separate load-bearing from peripheral.** Keep only documents that decide or state something: a status decision, a design position, a legal provision, an explicit statement on privacy, identifiability, data access, anonymity, offline, tiers, programmability or ledger. Genre does not decide. [rule D1 written; v11 genre rubric retired]
5. **Run one uniform gap check per project.** Search every project's official channels for documents that pass steps 3 and 4 and are not yet registered. Record what was searched, what was found, what could not be opened. [done for all 43 projects: 378 candidates, 354 new]
6. **Authors decide on every candidate.** Accept, reject, companion or wholesale, with a one-line reason; a model pre-screen only speeds this up. Accepted documents are downloaded, hashed and added as dated rows. [pre-screen done; author decision in progress]
7. **Freeze the source manifest.** One table of all evidence documents: project, year, kind, language, route, URL, SHA-256, reuse terms, one as-of date (18 Oct 2026). Everything later is a dated amendment. [draft; freeze after step 6]
8. **Convert documents to page-indexed text.** `pdftotext` per page, OCR where there is no text layer, one marker per PDF page; the page index is the locator everywhere. [done for the v11 core; to repeat for additions]
9. **Audit document language.** Page-level detection, registry label corrections, evidence-language ledger with routes A (English original), B (issuer English edition), C (checked translation), D (machine, provisional). [done: 106 English / 19 non-English; Norway re-run on route B]
10. **Fix the project frame.** 48 projects → 46 national → 43 retail candidates; unions, wholesale-only and statutory-ban cases excluded with reasons. [done]
11. **Write the measurement contract.** Cells F1–F12 as questions answered only from the project's documents, with values, decisive qualifiers and traps; claim schema; two status axes (decision × implementation); the admissibility rule for commitments; the posture layer (P0–P3, G1–G9); derivation rules; outcomes. [v12 draft; adopt after step 7]
12. **Encode the contract as a schema.** Allowed values per cell, enums, fill columns, JSON output format; every model output is validated against it. [v1.1 in use; v12 draft]
13. **Build the extraction pipeline.** Prompts rendered from contract + schema and exported with hashes; two modes (all documents in one request; per-document findings then synthesis); two providers via API; every request and response archived; model id, settings and hashes in a manifest. [built; prompts exported]
14. **Check every citation mechanically.** Each quote must be found verbatim on the cited page; states exact / spanning / elsewhere / fuzzy / invalid; found page recorded. [built, tested]
15. **Compare modes and providers.** Cell-by-cell comparison with coverage checks; a comparison with a failed or missing document is invalid by construction. [built; NO and UK compared]
16. **Run development cases and revise definitions.** Norway, United Kingdom, then euro area, Canada, Chile, Hungary, one live project. Authors review every cell in a workbook against the cited page; disagreements are classified as model error or definition problem; the contract is revised. At most five prompt versions, each dated. [NO, UK done; others next]
17. **Run sealed model-only screens.** One-question endorsement census and a typed statement survey over the whole corpus; per-project results sealed off-repository; authors see aggregates only; exposure recorded in a ledger and enforced by an allowlist in code. [done; to re-run after step 7]
18. **Freeze and register.** Manifest, contract, prompts, routing rule, decision gates and failure policy frozen; repository tagged; Zenodo DOI; OSF registration with exposure disclosure, language denominators and, if a classified estimate remains, the smallest effect of interest elicited from the authors and the supervisor. [gate]
19. **Build the human reference.** Both authors code a probability sample of 12–16 projects blind, from the PDFs, in workbooks without model columns; workbooks locked before any model output is opened; adjudication logged. In addition, F1 is source-checked for every analytic project before model exposure. [after the freeze]
20. **Run production extraction.** Frozen pipeline over all projects, both providers, once; retries only for transport failures; all disagreements, failures and primary-outcome cells adjudicated by the authors. [after step 19]
21. **Audit the instrument.** One scored run on the blind set (agreement α, AC1; feature, type and outcome error); challenge battery of synthetic edits; outer audit of excluded documents and OCR loss; stability envelope on six fixed projects. [after step 20]
22. **Derive the layers.** Commitment matrix through the admissibility gate; architecture type and outcomes; posture ladder and indicators from located claims; linguistic emphasis; claim history per cell. All by one tested derivation module. [module built]
23. **Analyse and report.** Cross-project tables, the table of commitments that disappear under strict rules, missingness bounds, descriptive cross-tabulations; any institutional association exploratory and labelled. Reporting per GUIDE-LLM and TRIPOD-LLM. [after step 22]
24. **Release and let others check.** Dataset CC BY, code MIT, website with document and page links on every value, every number replayable from archived outputs without API access; independent re-audit by a second model before submission; then peer review. [ongoing: audit of 2 Nov applied]

## Techniques we use for validation, auditability and openness

- **Mechanical citation check** on every quote (full-span match on the cited page, furniture removed, found page recorded).
- **Schema validation** of every model output; parse failures are recorded as failures, never repaired.
- **Request and response archive** with SHA-256 of prompts, contract, schema and script; model id and settings in every manifest; prompts exported as versioned files and tested for drift.
- **Two providers, two modes**, compared cell by cell with coverage checks; routing rule registered before scoring.
- **Sealed model-only screens**: per-project results off-repository, only aggregates and hashes committed; exposure ledger; release allowlist enforced in code.
- **Blind human reference** (no model columns, locked before exposure), inter-coder agreement (α, AC1), adjudication logged; source-first F1 for all projects.
- **Admissibility gate in code** (documented, endorsed or operational, not rejected, not staff research, no conflict), symmetric for yes and no; tested.
- **Pre-registration** (OSF) with decision gates, failure policy, exposure disclosure and language denominators; smallest effect of interest only if a classified estimate remains.
- **Dated amendments, never silent edits**: registry corrections, additions, URL and licence tables as dated rows applied by a loader.
- **Language audit**: page-level detection, routes A–D, issuer English editions, parallel-text test.
- **Reuse-terms audit** per issuer and document before any corpus deposit.
- **Decision records** (ADR-001 consultation, ADR-002 audit) with author initials; a Czech progress note and this process list kept current.
- **Independent review by a second model** from an audit pack (no sealed data), findings applied the same day and recorded.
- **Tests and CI** (24 tests: gates, citation check, comparator validity, prompt drift, secrets scan); one-command re-run of the machine stages from any provider.
- **Open release**: CC BY data, MIT code, GitHub Pages site with document links at the cited page, Zenodo DOI, full git history as the audit trail.
