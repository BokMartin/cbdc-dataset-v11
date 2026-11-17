# Prompt for an independent audit before the paid model runs, 17 November 2026 (paste into a second model together with the attached zip)

You are an independent methodological auditor and an experienced referee for academic journals that publish measurement-and-data papers built on large language models as annotators (target journal: *Data & Policy*, Cambridge University Press). Two economists (Prague University of Economics and Business) are building an open dataset of how central banks document the privacy of retail CBDCs. Their technical collaborator, a different LLM (Claude), designed the pipeline and wrote the documents you will read. In the next days the authors will spend several hundred US dollars and two weeks of a fixed deadline on model runs over the whole corpus with three models. **They want every flaw that would force a re-run, or that a referee would reject, found now.** Be adversarial. Do not praise. Where you are not sure, say so.

## What you receive

`CBDC_AUDIT_PACK_2026-11-17.zip`:
- `00_PROMPT.md`: this text. `01_AUDIT_BRIEF.md`: the collaborator's account, with twelve weaknesses it admits. Read it first and treat it as the defendant's statement.
- `repo/`: the repository at the commit in `repo/GIT_COMMIT.txt`, with `repo/GIT_LOG_since_2026-11-13.txt`. Start from `repo/PROJECT_BRIEF.md` and `repo/AGENTS.md`.
- `extra/CBDC_CORPUS_DOCUMENTS_2026-11-17.xlsx`: the 208 documents the models will read, coverage by project, and the evidence documents that cannot be read.
- `extra/TALK_DEV_SAMPLE_MB_relevance_only.xlsx`: the 120 development units with their context as one author saw them and his blind relevance labels.
- `extra/EXAMPLE_REQUESTS/`: the same units rendered as model requests in the two candidate forms (one unit per request; one page per request), for the relevance prompt.
- `extra/UNITS_DIAGNOSTIC_SAMPLE_300.csv`: 300 units drawn at random for you across strata, none of them in the development sample.

Not included: source documents and translations (copyright), the sealed per-project results of 2 Nov. Do not label the units of any sample for the authors and do not try to produce the dataset; your job is the procedure.

## Read in this order

1. `01_AUDIT_BRIEF.md`; `repo/PROJECT_BRIEF.md`.
2. `repo/DECISIONS/ADR-004-*.md`, `ADR-005-*.md`, `ADR-006-*.md`.
3. `repo/docs/CALIBRATION_PROTOCOL_DRAFT_2026-11-17.md`, `repo/docs/READINESS_BEFORE_CALIBRATION_2026-11-17.md`, `repo/docs/RUN_RECORD_SPEC.md`, `repo/docs/RUN_STATEMENT.md`.
4. `repo/pipeline/prompts/talk_L1_relevance.system.md`, `talk_L2_facets.system.md`, `repo/schema/talk_units_v13_DRAFT.json`, `repo/docs/TALK_CODEBOOK_cs.tsv` (Czech explanations, English values), `repo/scripts/units/` (unitise, select_candidates, context, build_requests, draw_agreement_sample, score_agreement).
5. `repo/docs/MEASUREMENT_CONTRACT_v12_DRAFT.md`, `repo/pipeline/prompts/extraction_*.system.md`, `repo/scripts/extraction/`.
6. `repo/docs/TRANSLATION_PROCEDURE.md`, `repo/data/translation/benchmark/JUDGEMENT_RESULT_MB_2026-11-17.json`, `repo/docs/audits/INDEPENDENT_AUDIT_2026-11-13.md` (the previous audit; check which of its findings are still open).

## What to examine. Answer every item; cite file paths with line numbers, CSV columns or cell coordinates.

**A. Is the collaborator's account true and complete?**
1. Recount the figures of sections 2 and 5 of the brief and of the generated block in `PROJECT_BRIEF.md` from the CSV files. Report every figure that does not reproduce.
2. Go through `READINESS_BEFORE_CALIBRATION_2026-11-17.md` row by row: is the state true? **What is missing from the list?** Name everything that must exist before the first paid calibration call and before the first paid production call and is not on it.
3. Which findings of the audit of 13 Nov are still open, and which were closed only on paper?

**B. Acceptability in an academic journal**
4. The validation design of ADR-006 A: blind human coding for relevance only (two authors, 120 units, later 400), verification of pre-filled facet labels with planted errors, complete verification of project-level statements. Would a referee of *Data & Policy*, or of a comparable journal, accept it? What is the strongest objection, and what is the cheapest addition (in author hours) that removes it? Consider: authors as the only coders; one author doing most of the work; anchoring; no independent gold standard for seven facets; the size of the samples per facet value.
5. Planted errors: is a detection rate estimated this way meaningful? How should the errors be planted (which facets, which wrong values, what share, how to keep the reviewer blind, how to analyse) so that the figure can be reported without being attacked? Give the design.
6. Which reporting standards or checklists for LLM-assisted annotation, text-as-data measurement or dataset papers should the authors follow, and which items of them does the current plan fail? **Cite only works you are certain exist; give authors, year and venue, and mark every reference you could not verify as UNVERIFIED.** The authors will check each one.
7. List the statements the paper will be able to make and those it must not make, given the design (about validity, reliability, coverage, translation, per-project results, reproducibility).

**C. Calibration of the prompts**
8. Attack `CALIBRATION_PROTOCOL_DRAFT_2026-11-17.md`. Is each rule sound: the factor tests and their decision rule, relevance blind in every round, the majority label as the pre-filled value, the cause codes, the change rule, the regression rule, the stopping rule, model-informed additions in rounds 2 and 3, the freeze? Where can the procedure overfit, leak or let the authors steer the result?
9. Sizes: are 120 + 3 × 60 units enough to calibrate eight labels, some with rare values? What sizes and what stratification would you use for the same author time (about 30 minutes per round)?
10. Disjointness of the reference sample from the calibration material: unit, paragraph, page or document? Decide and justify, given 208 documents and 44 projects.
11. One prompt for three models: how to avoid tuning it to one model? Is it defensible that the prompts were written by one of the three vendors' models? Should examples (few-shot) be used, and if so, of what origin?
12. Read the two talk prompts as an instrument. List ambiguities, contradictions with the schema or the codebook, places where the three models are likely to diverge, and output-format risks under page packing (several units per request, identifiers copied character for character). Look at the 120 development units: 24 were marked unusable by the coder. Is that a defect of unitisation, of the candidate rule or of the coder's reading of "U", and what should be done before calibration?
13. **Write the calibration protocol you would sign**, as a numbered procedure the authors can follow, with sample sizes, decision rules and what is recorded.

**D. Three models**
14. Full runs on claude-opus-5-5, gpt-6-astra and deepseek-v4-pro with a majority label: is the combination rule of section 7 of the draft defensible? Compare with the alternatives (one primary model and two robustness models; unanimity; reporting three datasets). What must be pre-registered?
15. Facets coded by all models on the union of units any model called relevant, against each model's own chain: which is right, and what does each do to the agreement figures?
16. DeepSeek: what are the risks for this corpus (China, Hong Kong and Taiwan are projects in the frame; alias repointing; data terms; context limits) and is the pre-registered check sufficient? Would an open-weight model run at a pinned revision be a better third model for a paper that claims auditability?
17. What can agreement between three LLMs show and what can it not? Give the wording you would accept in the paper.

**E. What is stored and what the paper states**
18. Check `RUN_RECORD_SPEC.md` field by field against what a referee, a replicator and a data editor need. What is missing (for example: tokenizer-independent input hashes, the exact request body, batch identifiers, provider system fingerprints, the date of each alias, parser version, random seeds of samples, licence of the outputs)? What is superfluous?
19. Source text cannot be published. Is "hashes, locators, labels, and requests rebuilt by script" enough for the reproducibility claims the authors plan? What is the strongest form of availability they can honestly offer, and what should the data-availability statement say?
20. Model retirement and aliases: what exactly should the paper state about each model, and what should be archived now that cannot be recovered later?
21. The older runs (translation, the Norway and UK pilots) lack the commit and an explicit reasoning setting. Do they have to be repeated?

**F. Design choices that could force a re-run**
22. For each cost measure of ADR-006 B (page packing, low reasoning, Batch API, cached system prompt, 20 % same-model replicate, page spans for general publications, one primary extraction mode): what is the risk to the measurement, is the proposed test adequate, and would you take the saving?
23. Order of operations: with the readiness list as it stands, what is the correct sequence up to the first production call? Identify every step where money would be spent on an input that may still change (document set, translations, unit rule, issuer metadata, contract version).
24. Coverage: non-English evidence of T3 projects was not translated, so two projects have no readable document and three have one. Is it defensible to run as is? If not: translate, or restrict project-level outputs? What does each option cost the paper?
25. The commitment layer: the contract is a draft and the extraction prompts are one version behind. Can F-cell extraction on three models responsibly run in November, calibrated only on Norway and the UK? What is the minimum that must be adopted first?

## Output

Write in English, as a report with these parts:
1. **Verdict**, two lines: calibration GO / NO-GO; production GO / NO-GO; each with the conditions.
2. **Findings**, numbered, most serious first. For each: severity (BLOCKER = would force a re-run or a rejection; MAJOR; MINOR), the item above it answers, the evidence (file and line), and the concrete fix with its cost in author hours or USD where you can estimate it.
3. Answers to items 1 to 25 in order, each at most 200 words, except item 13 (the full protocol).
4. **The list of things to store** for every run and for the deposit, as a table.
5. **Must-not-claim list** for the paper.
6. What you could not check and why.
