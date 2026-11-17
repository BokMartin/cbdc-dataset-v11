# Calibration of the talk prompts and of the run design: DRAFT for audit (17 Nov 2026)

Status: proposal of the pipeline author (Claude). **Nothing in this document has been run and no author has adopted it.** It is written to be attacked by the audit of 17 Nov (`docs/audits/PROMPT_AUDIT_2026-11-17.md`). Decisions it builds on: ADR-004, ADR-005, ADR-006.

## 1. What is calibrated, what is fixed

- **Calibrated:** the wording of the two system prompts (`pipeline/prompts/talk_L1_relevance.system.md` v0.2, `talk_L2_facets.system.md` v0.3) together with the Czech codebook (they change in the same commit or not at all); the form of the request (one unit, or all candidate units of a page: `scripts/units/build_requests.py`); the reasoning setting; the robustness of the output format.
- **Fixed during calibration:** the units and their identifiers, the candidate rule, the context rule (`scripts/units/context.py`), the list of models, the list of facets (a facet may be dropped, none may be added), the document set.
- **Models (MB, 17 Nov):** `claude-opus-5-5` (Anthropic), `gpt-6-astra` (OpenAI), `deepseek-v4-pro` (DeepSeek). One prompt and identical user messages for all three; no provider-specific wording. All calls through the provider API with a run record of purpose `development` (`docs/RUN_RECORD_SPEC.md`).

## 2. Material

| set | units | use | may a model see it before the authors code |
|---|---|---|---|
| C0 | the 120 development units of 13 Nov (`AGREEMENT_SAMPLE_dev_2026-11-13.csv`); MB coded relevance blind on 17 Nov, DS to do the same | factor tests (section 3), regression after every prompt change | relevance: no (done for MB); facets: yes |
| C1, C2, C3 | three new samples of 60 units, same strata as C0 (dictionary hit 45, neighbour 8, random control 7), seeds committed before the draw, disjoint from C0 and from each other | one calibration round each | relevance: no; facets: yes |
| reference | 400 units, drawn only after the freeze, from units that share no paragraph with C0 to C3 | the reported validation; never used for any change | no |

Open choice put to the auditor: disjointness of the reference sample at the level of the unit and paragraph (proposed), the page, or the document (cleanest, but with 208 documents and 82 already touched by C0 it would bias the reference sample towards documents not used in calibration).

## 3. Factor tests on C0, before round 1 (one factor at a time, current prompts, all three models)

1. **Baseline twice**: one unit per request, provider default reasoning. The agreement between the two runs is the test-retest agreement of each model and the yardstick for the next two tests.
2. **Packing**: the full pages that hold the C0 units, page-packed, against the baseline.
3. **Reasoning**: lowest setting the provider offers against the baseline.

Rule: a cheaper variant is adopted only if (a) its agreement with the baseline is not below the test-retest agreement of the baseline (point estimate inside the bootstrap interval of the latter) and (b) its agreement with the authors' blind relevance labels is not lower than the baseline's. Otherwise the baseline form is used in production, whatever it costs. The result of each test is recorded in ADR-006 before round 1.

## 4. One round (C1, then C2, then C3)

1. An author codes **relevance blind** for the round's units (one column; this is the part the authors accepted to do by hand).
2. The three models label the units with the current prompt version (relevance; facets for every unit that at least one model calls relevant).
3. The author's workbook shows, per unit, the paragraph with the unit marked and, for each facet, **one pre-filled label: the majority of the three models**, with a mark where the models disagreed. The author records, per facet, correct or wrong, the right value if wrong, and one cause: C = codebook ambiguous, P = prompt unclear or silent, M = model slip against a clear rule, S = the unit is not a usable sentence, T = translation.
4. Error table per facet, cause and model.
5. **Change rule.** The prompt and codebook change only for causes C and P, and only when the same confusion occurs in at least two units of the round or is a systematic confusion between two values. One change = one diff, with its reason and the unit identifiers that motivated it, in `pipeline/prompts/CHANGELOG.md`. No sentence from the corpus is copied into a prompt; examples in prompts are invented.
6. **Regression.** After a change all earlier sets (C0 up to the current round) are re-run on all three models. The change is kept only if no model's agreement with the author-corrected labels falls on any facet and the targeted confusion decreases.
7. **Stop.** After C3, or earlier if a round produces no change. A fourth round needs a written reason. Rounds 2 and 3 may add up to 20 units chosen where the models disagreed or where a rare value (ENDORSED, OPERATIONAL, CRYPTOGRAPHIC) was output; model-informed sampling is allowed in development and never in the reference sample.

## 5. What a round reports (appendix of the paper, as development, not validation)

Per model: relevance precision, recall and Krippendorff's alpha against the author's blind labels; share of pre-filled facet labels the author accepted (an anchored figure, labelled as such); pairwise and three-way agreement between the models; parse failures; tokens and cost.

## 6. Freeze

Frozen and registered (ADR, OSF) before the reference sample is drawn: the two prompt files (SHA-256), codebook, schema, request form, reasoning setting, model identifiers, the combination rule (section 7), the replicate design. A defect found after the freeze leads to a new version and a full re-run; both are reported.

## 7. Combination of the three models (proposed, to be fixed at the freeze)

- Each model labels relevance for all candidate units. **All three models code the facets for the union** of units that at least one model called relevant, so that facet agreement is measured on the same units.
- Dataset label per unit and facet = the value given by at least two of three models; otherwise `NO_MAJORITY`. A unit is relevant if at least two models say so.
- `NO_MAJORITY` units are counted and reported; those that would decide a project-level statement (an event-history milestone, a cell of the talk × commitment table) are adjudicated by an author against the source sentence.
- The paper reports every result for the majority label and for each model separately, with pairwise and three-way agreement, overall and by project, by text route (original, issuer edition, machine translation) and for CN, HK and TW against the rest (pre-registered check of the non-Western model on politically sensitive projects).
- Agreement between models is reported as robustness to the choice of model, not as validity. Validity rests on the authors' blind relevance labels, the verification sample with planted errors and the complete verification of project-level statements (ADR-006 A).

## 8. F-cell extraction is calibrated separately

Only Norway and the UK are exposed to the authors (EXPOSURE_LEDGER); they are the only projects on which the extraction prompts may be tuned. Before that the measurement contract v12 and `schema/cells_v12_DRAFT.json` must be adopted and the three extraction prompts (still written for contract v1.1) brought to v12. Then: Norway and the UK on the three models, comparison with the existing development profiles, freeze, production on all projects.

## 9. Known weaknesses of this draft

1. Facet verification is anchored on a pre-filled label and done mostly by one author.
2. C0 is used many times (factor tests, every regression); the prompts may fit it. It is therefore never reported as validation.
3. Rounds of 60 units contain few units with rare values; the planted-error sample and the project-level census carry that burden.
4. The three models share training data; their majority can be jointly wrong.
5. A pre-filled majority label hides which model erred from the author, by design; the error table by model is computed afterwards.
6. Estimated cost of the whole calibration: under 40 USD at list prices (an estimate, not a measurement).
