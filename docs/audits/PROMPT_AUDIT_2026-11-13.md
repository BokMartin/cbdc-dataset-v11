# Prompt for an independent audit of the procedure, 3 to 13 November 2026 (paste into a second model together with the attached zip)

You are an independent methodological auditor for an academic measurement-and-data paper (target journal: Data & Policy, Cambridge University Press). Two economists (Prague University of Economics and Business) are building an open, auditable dataset of how central banks document the privacy and identifiability architecture of retail CBDCs. Their technical collaborator, a different LLM (Claude), designed and ran most of the steps you are about to read. The authors want to know **whether the procedure contains a logical error or a process error** before they invest two days of human coding and before anything is registered. You have no stake in the result. Be adversarial, specific and brief. Where you cannot verify something from the pack, write "not verifiable from the pack" and say what would be needed; do not guess.

## What you receive

`CBDC_AUDIT_PACK_2026-11-13.zip`:
- `00_PROMPT.md`: this text.
- `01_AUDIT_BRIEF.md`: the collaborator's own account of the eleven steps S1 to S11, each claim with the file it can be recounted from, and twelve weaknesses it already admits. **Read it first. Treat it as the defendant's statement, not as evidence.**
- `repo/`: the repository at the commit named in `repo/GIT_COMMIT.txt`, with `repo/GIT_LOG_since_2026-11-03.txt`. Scripts are Python; `pytest` runs without an API key.
- `extra/TIER_REVIEW_v12_2026-11-13.xlsx`: the authors' review workbook (one row per document, 772 rows), not yet filled in.
- `extra/UNITS_DIAGNOSTIC_SAMPLE_300.csv`: 300 sentence units drawn at random for you (not part of the coders' sample), with stratum, text route and text mode.
- `extra/TRANSLATION_BENCHMARK_2026-11-11.xlsx`: the sentence pairs of the translation benchmark.
- `extra/translation_examples/`: two complete request/response pairs of the translation run with the system prompt.

Not included: source documents and translations (copyright), the sealed per-project results of the model screens of 2 Nov, the coders' workbooks. **Do not try to reconstruct per-project values of the sealed screens, and do not label the units of `data/units/AGREEMENT_SAMPLE_2026-11-13.csv`**: the authors must code them before any model does.

## Read in this order

1. `01_AUDIT_BRIEF.md`.
2. `repo/docs/PROCESS_v12.md` (the 24-step plan), `repo/docs/MEASUREMENT_CONTRACT_v12_DRAFT.md` sections 1 to 6 (construct, claim schema, status rules A and B, admissibility rule C, posture layer), `repo/EXPOSURE_LEDGER.md`.
3. `repo/docs/SOURCE_RULE_D1.md`, `repo/docs/LANGUAGE_LEDGER.md`, `repo/docs/TRANSLATION_PROCEDURE.md`.
4. `repo/docs/PRIVACY_POSTURE_LAYER_DESIGN_2026-11-02.md`, `repo/docs/PRIVACY_TALK_INSTRUMENT_PROPOSAL_2026-11-12.md`, `repo/DECISIONS/ADR-004-*.md`, `repo/docs/TALK_AGREEMENT_PROTOCOL_2026-11-13.md`, `repo/docs/TALK_CODEBOOK_cs.tsv` (Czech explanations, English values), the two `repo/pipeline/prompts/talk_*.md`, `repo/schema/talk_units_v13_DRAFT.json`.
5. The scripts under `repo/scripts/review/`, `repo/scripts/translation/`, `repo/scripts/units/`, `repo/scripts/census/talk_pilot.py`.

## What to examine

Answer every item. Cite file paths with line numbers, CSV columns or cell coordinates.

**A. Recount (is what the brief says true?)**
1. Recount from the CSV files the figures of S2, S3, S4, S5, S8, S10 and S11 of the brief. Report every figure that does not reproduce.
2. Tiers: recompute each project's tier from `data/manifest/TIERS_2026-11-10.csv` (evidence = KEEP or BORDERLINE; T1 ≥ 8, T2 5 to 7, T3 ≤ 4). Does `build_tier_workbook.py` do what its docstring says, including the override by `AUTHOR_DECISIONS_*.csv`? Can a document be counted twice (linked files, English editions)?
3. Translation hash chain: for the two pairs in `extra/translation_examples/`, recompute the SHA-256 of the system prompt, the request and the response and compare with `data/translation/TRANSLATION_REQUESTS_2026-11-10.csv` and `data/translation/runs/*/CALLS.csv`. Does `ingest_translations.py` ever alter a response? Could a truncated, reordered or partly untranslated response pass its checks? Do the two responses obey the system prompt (markers, bracketed source terms, nothing added)?
4. Unitisation and candidates: read `unitise.py` and `select_candidates.py` and look at the 300 diagnostic units. What share of the units is not a usable sentence (fragments, merged sentences, navigation text, interleaved columns)? Is stratum X removing things that should be coded, or keeping things that should not? Does the dictionary (`BROAD`) miss obvious privacy vocabulary or catch obvious noise (for example "identified" in the sense of "we identified three options", "trace", "confidential" for wholesale)? Is the 5 % control really a random sample of the remaining units, independent of content?
5. Agreement sample: does `draw_agreement_sample.py` implement the design of the protocol? Is the draw deterministic and free of model output? Check `score_agreement.py`: is Krippendorff's alpha for two coders and nominal data computed correctly, is Gwet's AC1 correct, and is the bootstrap sound? Test it on a small example of your own.
6. Pilot: are the ICC and split-half figures in `data/census/TALK_PILOT_aggregate.json` what the proposal says, and is the method in `talk_pilot.py` (arcsine transform, random-intercept model, Spearman-Brown) appropriate for shares with many zeros and unequal document lengths?
7. Run `pytest`. State which of the steps S1 to S11 have no test at all, and name the three tests you would write first.

**B. Logic of the design (is the reasoning sound?)**
8. **Construct.** The paper wants to set "privacy talk" against "privacy commitment" per project. Given the pilot (project share of variance about 0.15, median project with four evidence documents), can a project-level comparison be defended at all? Is the proposed funnel a valid replacement, and what exactly would each step's denominator be? Say where the funnel compares unlike things (sentences against cells).
9. **Selection.** Evidence documents are chosen by a rule that asks whether a document contains a statement bearing on privacy cells (source rule, condition 3), and talk is then measured as the share of privacy sentences in those documents. Is that circular? Does selecting T1/T2 by number of evidence documents bias any talk measure, and in which direction? What would a defensible denominator be?
10. **Facets against the contract.** Compare `schema/talk_units_v13_DRAFT.json` and the L2 prompt with the contract. List every inconsistency (the brief admits the status ladder; look for others: endorsement rule A, the `basis` values and the "will not use is policy, never architectural" trap, staff research, the meaning of direction GRANT for identification, the aspect ANONYMITY mapped to two cells). For each, say which side should change.
11. **Two overlapping layers.** The contract's posture layer (P0 to P3, G1 to G9, derived from model-written claims) and the unit-based instrument (ADR-004) both describe "who said what with what status". Should one replace the other? What breaks in the contract, the derivation module and the planned paper if it does?
12. **Translation as measurement.** The authors accept translation error in exchange for a single coding language. Does the benchmark (five documents, three languages, automatic sentence matching, about a third of privacy sentences unmatched) support using route-D text for (a) relevance, (b) aspect, (c) direction, (d) status and modality? What is the minimum additional evidence you would require, and is the registered human judgement of 86 pairs the right design (strata, blinding, what it can and cannot show)?
13. **Human agreement design.** Judge the sample of 400: size per facet once only relevant units count, the fixed quotas, authors as coders, training on two projects, facets scored only where both coders say relevant, thresholds 0.80 / 0.667, one revision round. Is anything here likely to produce an agreement figure a reviewer would not accept? Is the Czech codebook consistent with the English L1 and L2 prompts, so that humans and the model answer the same question?
14. **Recall.** Is a 5 % random control enough to bound the share of relevant units the dictionary misses? Compute the interval you would expect for plausible prevalences (for example 0.5 %, 1 %, 2 % relevant among about 6 100 control units classified by a model and checked by hand) and say whether the design can support the sentence "the project says little about privacy".
15. **Order of operations and exposure.** Is anything done in an order that contaminates a later step? Consider: the authors reading 400 sentences of 42 projects before the blind human reference for F-cells; decisions on documents taken after the pilot was seen; the unitisation changed after results; the agreement sample drawn before the document set is final; the issuer and voice pre-fill shown to coders as context; one model family writing the dictionary, the prompts and later the labels. For each, say whether it is harmless, must be disclosed, or must be redone.
16. **As-of date and frame.** Check dates of evidence documents against the as-of date of the contract. Is the frame of 43 projects still what the tier workbook uses, and is the treatment of the euro area (member documents under the union project) consistent across the manifest, the tiers and the units?

**C. What is missing**
17. Name the steps that must happen before registration and are in nobody's plan. Name anything in the plan that should be dropped because it cannot yield a defensible result with this corpus.
18. If you had to cut the design to what two authors can finish and defend by the end of December 2026, what would you keep?

## Output format

1. A numbered report, items 1 to 18, each with a **verdict** (sound / sound with correction / unsound / not verifiable from the pack), the evidence, and the fix.
2. A table of the twelve admitted weaknesses of the brief: for each, **agree / overstated / understated**, one line of reasons.
3. The five most serious problems you found that the brief does **not** admit, ranked, each with what it would cost to repair.
4. One paragraph: may the authors start the human coding now, yes or no, and on what condition.

Write in English. Do not restate the pack back. Do not soften findings. Do not praise.
