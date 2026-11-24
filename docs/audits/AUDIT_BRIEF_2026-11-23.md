# Audit brief, 23 November 2026 (A4c): the F-cell extraction prompt v12.1, before the authors adopt it

Written by the pipeline assistant (Claude, Anthropic), which also wrote the prompt under audit. **Treat this as the defendant's statement.**

## 1. Why this audit, and why now

MB read the prompt on 23 Nov and found it in order, but wants a second model's review before the authors adopt it ("prompt za mě vypadal v pořádku ale chtěl bych feedback od druhého LLM", 23 Nov 2026). Nothing has been run with it. No runner for it exists yet. The first use will be one development round on Norway and the UK (ADR-012 D1), then production on three models from three providers. A defect found now costs an edit. The same defect found after production costs a re-run of every project, and possibly a new blind coding round.

## 2. What the prompt is for (details in `repo/docs/MEASUREMENT_CONTRACT_v12_DRAFT.md` and `repo/DECISIONS/ADR-012-*.md`)

- The F-cells (F1 to F4, F7 to F12, plus a new PET profile) describe the stated privacy design of each retail CBDC project. They feed the stated-design privacy index: the mean of seven cells F1, F2, F4, F7, F8, F9, F10, with F3 categorical beside it and a four-cell variant. They also feed the commitment profile (axis 2) and the registered hypothesis "much talk, few commitments" (ADR-012 D3).
- In the 16 core projects (tiers T1 and T2), **both authors code every cell from the sources before any model output is opened**. The models are a comparison there. Outside the core, a value stands only if all three models agree with a located quote and a source check confirms it (ADR-012 D1, D2).
- **The model does not decide cell values.** It lists claims, one document per request. A script is meant to derive the cells from those claims: rule C admissibility, supersession ("the newest claim of the highest status wins"), conflict, evidence state and unknown reasons. **This script does not exist yet.** `repo/scripts/derive.py` and `derive_index.py` work on cells, not on claims.
- The prompt applies these earlier decisions:
  - no text truncation; split only at page markers (ADR-001 E17, v11 lessons);
  - reading-order text, because the layout text interleaved columns (13 Nov);
  - the PDF page index as the only locator, with quotes allowed across a page break (ADR-002);
  - general publications sent only as the CBDC pages plus one page on either side, with laws and codes treated as companion documents (MB, 22 Nov 2026 16:07);
  - PET codes and layers taken from Nijsse and Pinto (2026), Table 1, Figure 8, Section 5 and Table 2 (ADR-012; MB supplied the PDF on 22 Nov).

## 3. The v11 lessons the prompt claims to handle

| v11 problem (where recorded) | What the prompt does |
|---|---|
| Documents silently cut at 400,000 characters; a truncated model output "salvaged" (`repo/archive/run_scripts/README.md`, ADR-001 E17) | No cut; long documents split at page markers with a one-page overlap. The model returns a `coverage` object; a mismatch or `complete: false` fails the request, and nothing is salvaged |
| Layout text interleaved two columns (`repo/docs/PRIVACY_TALK_INSTRUMENT_PROPOSAL_2026-11-12.md` §9) | Header field `text_layer`; the model lists garbled pages as `unreadable_pages` |
| Fractional or printed page numbers as locators; quotes across a page break lost (ADR-002 item 3) | `page_index` from the marker only; `printed_label` separate; `spans_pages` |
| Model decided cell values directly; not checkable (v11 prompt `repo/pipeline/prompts/extraction_single.system.md`) | Claims only; derivation by script |
| Scans without a text layer | OCR done on 23 Nov for the Jamaica FAQ booklet and three image-only pages of the Bank of Japan annual report 2023 (`repo/docs/OCR_2026-11-23.md`, `repo/data/manifest/OCR_2026-11-23.csv`); other scans (MO, NG) are listed as not unitised (`repo/data/units/UNITS_NOT_UNITISED_2026-11-23.csv`); `text_layer: ocr` in the header |

## 4. What the assistant itself thinks may be wrong (find more)

1. **The derivation is unspecified.** The prompt's output has never been mapped field by field onto `repo/schema/cells_v12_DRAFT.json`. Some cell fields have no source in a claim, for example `evidence_state: partial` when a decisive qualifier is missing, `conflict`, or `unknown_reason: search_incomplete`. The PET cell is not in that schema.
2. **One document per request loses cross-document links.** A design note may be `considered` while a later press release records the Board's decision on it. Each claim is then extracted in isolation, and nothing links the two. Supersession and endorsement-by-reference depend on matching claims across documents (`design_or_experiment_id`, free text). The prompt gives no stable key for that.
3. **The status depends on the header.** `decision_authority` is given in the header. The issuer and voice records it comes from are a model pre-fill that the authors have not all confirmed (`repo/docs/READINESS_BEFORE_CALIBRATION_2026-11-17.md` item 15).
4. **The coverage object is self-reported.** A model can write the right page numbers without having read the pages. Only counts are compared mechanically. Quote location (`repo/scripts/extraction/verify_quotes.py`) catches invented quotes, not missed claims.
5. **Basis.** The policy/architectural line in the synthetic test (page 2, "will hold no information that links") is a judgement call. A wrong `architectural` turns a promise into F1 = no in the index.
6. **The conditional commitment rule** ("if issued, the digital X will ...", which counts as endorsed) can be over-applied to a whole paragraph after one sentence names a Board decision.
7. **F7 and anonymity.** The rule that a rejection of full anonymity is never F7 = no is stated twice (§5.5, §5.12). But F7 = no needs "verified identity on every route", and this is easy to over-read from onboarding text (F8).
8. **PET list.**
   - Includes `standard_encryption`, `digital_signatures`, `two_tier_model` and `multi_factor_authentication`. They are in Nijsse and Pinto's tables but are baseline features, so they may flood the profile.
   - Excludes nothing by status, so tested wholesale experiments will appear as well.
   - The layer column is a reference for the script; the model is not asked to output it.
9. **Retail scope is inconsistent.** §3 says a claim is about the retail CBDC, but `retail_or_wholesale` allows `wholesale`, and PET observations from wholesale experiments are supposed to be kept as context (ADR-012 D5). Which wholesale claims to report is not stated.
10. **Layers.** The contract's background legal layer (F3 only) became `companion_legal` in the header. The contract text was not changed to match.
11. **Known editing slip.** §3 refers to `PRIVACY_PRINCIPLE` as "§5.10"; it is §5.13.
12. **Translation (route D).** Quotes are exact substrings of the machine translation. An error in the shared translation propagates to all three models identically (audit A4b, finding 6). The flag `translation_uncertain` has no rule for when to use it.
13. **Length.** Long reports (100 to 300 pages) with many claims may exceed a provider's output limit. The prompt asks the model to return `complete: false` rather than shorten. The split rule for output length is not written.
14. **Three providers.** The prompt has not been tried on any of them. JSON adherence, `also_at` lists and 60-word quote limits may behave differently.
15. **F11 and F12.** F11 claims use `stated` / `explicitly_rejected` plus the status axes, while the schema has five values per tag. The mapping is implicit. F12 asks for the platform name in `justification`, not in a field.

## 5. Also offered for review (Part B, lower priority)

Codebook v0.4 (`repo/docs/TALK_CODEBOOK_cs.tsv`, Czech) and the relevance prompt v0.3 (`repo/pipeline/prompts/talk_L1_relevance.system.md`) are proposals from the joint adjudication of 22 Nov (ADR-011 §5) that the authors have not formally confirmed. On 23 Nov the authors coded 80 sentences blind with codebook v0.4. Relevance alpha was 0.921 on 79 units, and every facet passed protocol v2 §4 on the 29 units both called relevant (`repo/docs/FACET80_AGREEMENT_2026-11-23.md`). The facet prompt `talk_L2_facets.system.md` is being revised in another thread at this moment, so it is **not** offered for review.

## 6. Money and time at stake

The review is free: MB runs it in a chat product. A development round on NO and UK with three models costs a few USD; production on 44 projects costs more, and is the step a wrong prompt would waste.

## 7. Conflict of interest to declare

The reviewer's vendor is the same as that of the model that made the project's machine translations (route D) and pre-filled the 19 Nov disagreement workbook. A model of that vendor will also be one of the three extraction models. The PET vocabulary comes from a paper both authors read, including its Table 2 (`repo/EXPOSURE_LEDGER.md`).
