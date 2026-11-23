# ADR-013: audit A4c of the F-cell extraction prompt v12.1 (23 Nov 2026): record, verification and proposed dispositions

Status: **P1 to P4 and B1 adopted as recommended** (MB, 23 Nov 2026 15:21 UTC: "s pěti rozhodnutími souhlasíme s tebou", written for both authors; DS to confirm in his own words if he wishes). P5, P6 and B2 needed no decision. Before that the file was a record and proposal. The repairs in §3 need no decision, because they implement rules already adopted (contract v12, ADR-012); they are made in a separate change. No prompt is changed by this file.

MB read prompt v12.1 on 23 Nov and asked for a second model's review before adopting it ("prompt za mě vypadal v pořádku ale chtěl bych feedback od druhého LLM"). The pipeline assistant wrote the prompt, the brief and the audit prompt (beside the report in `docs/audits/`).

| Item | File | SHA-256 |
|---|---|---|
| Report, stored unchanged | [`docs/audits/INDEPENDENT_AUDIT_2026-11-23.md`](../docs/audits/INDEPENDENT_AUDIT_2026-11-23.md) | `ec67ba8bda8d40408889257f9b2c311e800ee74d3dc56753a9bba37704040c0c` |
| Prompt under audit (v12.1) | [`docs/audits/EXTRACTION_PROMPT_v12.1_audited_2026-11-23.md`](../docs/audits/EXTRACTION_PROMPT_v12.1_audited_2026-11-23.md) | `93f1bf479d50a7d09951b0a250c37542e577fb8ca4e3feb9f17cf21396b7514b` |
| Audit prompt, brief, synthetic test document | `docs/audits/PROMPT_AUDIT_2026-11-23.md`, `AUDIT_BRIEF_2026-11-23.md`, `TEST_DOCUMENT_synthetic_2026-11-23.md` | `5ef9bf34…`, `abfd4c31…`, `972b0639…` |
| Pack | `CBDC_PROMPT_AUDIT_PACK_2026-11-23.zip` (outside the repository) | `d13a890e3a2ab1ff54fe5741430a26b0ad438491c35e94589c5ba17cc4009bd3` |

The pack was built from `b60f444` (main after PR 17); the auditor confirmed all six payload hashes and the commit. The auditor was run by MB in a chat product. It identifies itself as "OpenAI Codex, based on GPT-6". It declares a vendor-level interest: the same vendor made the route-D translations, pre-filled the 19 Nov disagreement workbook, and supplies one of the three extraction models. It read the full Nijsse and Pinto paper on arXiv.

**Verdict of the auditor:**
- development round on NO and UK with v12.1: **NO-GO**;
- production: **NO-GO**.

It reports 13 findings: 5 blockers, 7 major, 1 minor. It proposes twelve replacement blocks (A1 to A12) and a complete prompt v12.2 (report, appendix). It gives three offline acceptance fixtures (answer 12). Its answer on Part B is conditional adoption of codebook v0.4 and relevance prompt v0.3, with wording fixes.

## 1. What the pipeline assistant checked

| Claim | Checked how | Result |
|---|---|---|
| Finding 1: the index code still scores F3 and averages eight cells, against ADR-012 D4 (seven cells, F3 categorical) | `scripts/derive_index.py` lines 12, 34–48: `CORE = (F1, F2, F3, F4, F7, F8, F9, F10)`, `SCORE["F3"]` gives via_psp 1, via_cb 0 | **confirmed**. ADR-012 D4 was written into the contract and the spec (PR 15), but not into the code. Also, the F3 set has no `none_stated` |
| Finding 3: the v11 parser reads a JSON array, not the v12 object | `scripts/extraction/extract_api.py` lines 88–94 (`parse_array`) | **confirmed**. This is the v11 runner; the v12 runner is not built (HANDOFF §5 item 1) |
| Finding 3: the quote checker expects other page markers | `scripts/extraction/verify_quotes.py` line 31 parses `=== DOC n PAGE p ===`; prompt v12.1 sends `=== PAGE p ===` | **confirmed**: with the v12.1 format it would find zero pages |
| Answer 3: `admissible()` accepts a cell whose basis is `policy` (F1 = no), and a cell from a joint retail layer | `scripts/derive.py` lines 23–37: no check of `basis` or of the source layer, only `staff_research` | **confirmed** by reading the code. This contradicts contract §6 F1 ("policy promise never sets F1 = no") and ADR-012 D5 |
| Finding 13: two broken section references | prompt v12.1 §3 ("§5.10" for PRIVACY_PRINCIPLE) and §5.5 ("§5.11" for anonymity) | **confirmed**. The brief named only the first |
| Answer 8: a route-D rule from 17 Nov is still in force in the translation procedure | `docs/TRANSLATION_PROCEDURE.md` line 48, point (5): "no result of the paper may rest on route-D text alone for decision status or modality" | **confirmed**. It conflicts with ADR-012 D6 (route D in the main result); nobody superseded it |
| Answer 8: Peru, two readings | `docs/LANGUAGE_LEDGER.md` line 62 ("flagged wherever used") against the prompt summary ("flag and leave out") | **confirmed**. MB's words of 22 Nov 16:08 support "flag and leave out" for a non-core project |
| Answer 13: protocol v2 still shows the old 260/80/60 reference allocation | `docs/TALK_AGREEMENT_PROTOCOL_v2_2026-11-13.md` lines 5–15 | **confirmed**; the script and the contract carry 140/50/210 (ADR-012 D18, PR 15) |
| Answer 13: counts of the 80 sentences | auditor recounted from the two label files | agrees with `docs/FACET80_AGREEMENT_2026-11-23.md` |
| Answer 2: PET layers (BBS+ and MPC at C/E in Table 1, E and C in Figure 8; mixing C, privacy pools E) | `docs/audits/05_NIJSSE_PINTO_excerpt.md` and the PDF | **confirmed**; the v12.1 table merged them |
| Executed probes (index moves 1.000 → 0.875 when only F3 changes; A4b's V6 example now fails `committed()`) | not re-run; consistent with the code read above | plausible, not re-executed |
| Proposed v12.2 hash `3b9ef746…` and "replacements replayed" | not checked | open |

## 2. Row by row

"Auditor" is the report's proposal. "Assistant" is the pipeline assistant's proposal. The author decision column is filled only by MB and DS.

| # | Subject | Auditor | Assistant | Author decision |
|---|---|---|---|---|
| P1 | Basis of the prompt | Replace v12.1 by v12.2. Observations instead of claims: typed `kind`, evidence segments with block ids, `missing` qualifiers, `references` for cross-document links, `details` per cell, stricter output envelope | agree: v12.2 keeps the structure, the cells, the page rules, the PET list and MB's rules of 22 Nov, and it closes findings 2 to 6 and 8 to 11. Its one substantive change against an author decision is P2. **Authors decide** || MB, 23 Nov 2026 15:21 UTC, for both authors: "s pěti rozhodnutími souhlasíme s tebou" → **adopted as recommended** |
| P2 | Laws and other companion documents | A companion records legal references only. It can supply a detail to a linked maker claim, but it **cannot originate** a maker cell, including F3. The statutory position is shown separately ("maker-documented positions") | MB on 22 Nov 16:07: from laws the model takes "only lawful access (F3), legal state and who decided". The contract §2 has had a background legal layer "F3 only" since v11. The auditor's version narrows both. Recommended: the auditor's version, with the statutory F3 route reported in its own column. Then F3 still shows what the law says, but never as the maker's design. **Authors decide** || MB, 23 Nov 2026 15:21 UTC, for both authors: "s pěti rozhodnutími souhlasíme s tebou" → **adopted as recommended** |
| P3 | General publications (`cbdc_span`) | Keep the window of CBDC pages ±1 as the initial search. Follow explicit references to articles, definitions and annexes, and report a bounded search where a reference stays unresolved | agree. This is done by the runner, at no model cost, and keeps MB's rule. **Authors decide** (it adds to MB's rule) || MB, 23 Nov 2026 15:21 UTC, for both authors: "s pěti rozhodnutími souhlasíme s tebou" → **adopted as recommended** |
| P4 | Route D and the 17 Nov restriction | Either keep the restriction for D-only decisive status (endorsed against considered), or supersede it explicitly | ADR-012 D6 keeps route D in the main result (MB rejected the narrower version on 22 Nov). Recommended: supersede the 17 Nov restriction explicitly. A claim flagged `translation_uncertain` gets a targeted source check before it can count as a commitment; unflagged route-D claims count as they are, and the variant without route D is reported beside them. **Authors decide** || MB, 23 Nov 2026 15:21 UTC, for both authors: "s pěti rozhodnutími souhlasíme s tebou" → **adopted as recommended** |
| P5 | Development round on NO and UK | NO-GO until: a typed claim schema and mapping to cells; a runner with offline fixtures; a minimal claim-to-cell reducer that passes the three acceptance fixtures; the PET table in the schema | agree. This is a sequence of work for the pipeline author, not an author choice. The round costs a few USD, but its output cannot be read without the reducer | |
| P6 | Production | NO-GO even with v12.2, until the end-to-end path is shown and the core reference is locked | agree (consistent with ADR-012 D1, D2) | |
| B1 | Codebook v0.4 and relevance prompt v0.3 | Conditional adoption for the reference sample. One heading tie-break for both texts (table of contents or outline → N; isolated heading or fragment → U). Rule: "decide from the marked unit and the supplied paragraph alone". Russia and Thailand labels kept as recorded exceptions. Replace "upper bound" in the 80-sentence report by "performance for other coders is unknown" | agree. The wording changes are small but they are rule changes, so both authors must confirm them before the reference sample is drawn. **Authors decide** || MB, 23 Nov 2026 15:21 UTC, for both authors: "s pěti rozhodnutími souhlasíme s tebou" → **adopted as recommended** |
| B2 | What the paper says about the 80 sentences | Report the conditional and end-to-end alphas side by side, the rare categories never used, and that the authors are the coders | agree | |

## 3. Repairs that need no author decision (implement rules already adopted)

1. `scripts/derive_index.py`:
   - the primary number is the mean of seven cells, as ADR-012 D4 says;
   - F3 is categorical, outside the mean, with `none_stated` in its value set;
   - the four-cell variant sits beside it;
   - the auditor's first acceptance fixture becomes a test: F3 changes, and both intervals stay the same;
   - mock outputs are regenerated.
2. `scripts/derive.py` `admissible()`:
   - a cell from a non-official layer is never admissible, so LEANING stays only in the `with_leaning` variant (ADR-012 D5);
   - a protective value of F1, F2, F4 or F9 resting on `basis = policy` is not admissible (contract §6);
   - each rule gets a negative test.
3. Text alignments:
   - protocol v2 §1 gets the 140/50/210 allocation;
   - `docs/FACET80_AGREEMENT_2026-11-23.md` drops "upper bound";
   - the Peru entry in `docs/LANGUAGE_LEDGER.md` reads "flagged and left out of extraction (non-core, MB 22 Nov)".
4. The v12 runner, when it is built, parses the object envelope and uses the page format of the prompt. `verify_quotes.py` reads both formats. Both are tested on the auditor's fixtures. This is part of HANDOFF §5 item 1.

## 4. Consequences

Added after the decision of 23 Nov:
- MB, same message: development rounds are run outside the API, by hand in a chat product as with this audit; no low reasoning-effort setting; the three models are not changed. The NO/UK development round therefore needs no paid API call, but it still waits for the reducer and fixtures (P5), because its output must be read by the same code as production.


- No development round and no paid call until P1 to P4 are decided and the repairs of §3 and the reducer exist.
- If P1 is adopted, prompt v12.2 enters `pipeline/prompts/` with the author decisions on P2 to P4 written in. The v12.1 text stays in `docs/audits/` as the audited version.
- The ledger row for this audit is in `EXPOSURE_LEDGER.md`; the register row in `docs/audits/README.md` §4.
