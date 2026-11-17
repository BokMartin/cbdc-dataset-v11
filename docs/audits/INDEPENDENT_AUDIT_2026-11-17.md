# Independent audit before the paid CBDC model runs

17 November 2026 · Supplied snapshot `7e6e4c597fc07a16000aa771db125aebbaad14dc`

## 1. Verdict

**Calibration NO-GO now.** Proceed with a bounded development pilot only after repairing input identity, resolving the coding rules and metadata, protecting the reference material, and testing the runner, parser and provenance checks under the replacement protocol below.

**Production NO-GO now.** Freeze the corpus, translation restrictions, instrument and analysis rules; obtain independent validation of retained claims; implement replay and failure gates. F-cell production additionally requires a coherent adopted v12 contract, regenerated prompts, qualified claim extraction and contrasting development cases.

This is an audit of the supplied snapshot, not the live repository. No paid calls were made, no sample units were assigned new substantive labels, no sealed results were opened, and the supplied package was not edited. Findings distinguish executable failures, manifest arithmetic and methodological judgments. Neither this report nor a checklist can guarantee journal acceptance. All repair costs below are planning estimates, not measured quotations; author and engineering hours are distinguished and overlapping estimates must not be added mechanically.

Paths are relative to `repo/` unless prefixed `extra/` or `01_`. Line numbers refer to this snapshot. CSV references identify columns or keys; workbook references use sheet and cell coordinates. The answers to questions 1–25 are in section 3; detailed evidence tables follow them so that each answer except question 13 remains within the requested 200-word limit.

## 2. Findings, most serious first

### F01. BLOCKER: verification is being asked to establish validity that it does not measure

**Items:** 4, 5, 7, 9, 17, 25. **Evidence:** ADR-006 A.2–A.3, lines 9–14; calibration draft lines 33–41, 49–53; contract lines 162–176.

Agreement with pre-filled majority labels is an anchored acceptance rate. Detecting artificial errors does not identify sensitivity to naturally occurring errors, much less accuracy on seven facets. Checking every selected project quotation cannot establish that an earlier statement was not missed, or that a negative table cell is correct. The proposed safeguards therefore do not close the validity gap. This is a blocker for the proposed strong facet/project claims, not an assertion that journals prohibit model-coded descriptive datasets.

**Fix:** add a small, genuinely blank, independently double-coded facet reference after freeze; retain raw coder judgments and adjudication. For the cheapest defensible reduced paper, independently assess voice/aspect on 80–120 relevant units and keep the remaining facets explicitly exploratory. For seven-facet claims, use the 120-relevant-unit reference and targeted supplement in question 13. Source-first checking must include model negatives and earlier documents. **Cost:** approximately 4–8 combined author hours for a restricted core check; 8–16 for seven facets and adjudication, potentially more for difficult sources. An external reviewer helps independence but is not a substitute for this design.

### F02. BLOCKER: F-cell extraction is not a v12 instrument, even if a v12 file is supplied

**Items:** 12, 18, 21–23, 25. **Evidence:** `scripts/extraction/extract_api.py:28–59,100–120,166–228`; `pipeline/prompts/extraction_single.system.md:3–27`; `extraction_stage1.system.md:3–28`; `extraction_stage2_synthesis.system.md:3–27`; `schema/cells_v12_DRAFT.json:5–26`; contract lines 35–51, 157–176.

The exported prompts embed v1.1; more importantly, the generator itself still requires `claim_status=option|adopted|tested|operational` in stage one. Supplying the draft v12 schema does not remove this. Final fills retain one decisive quote instead of a complete linked atomic-claim record. The v12 schema defines **21 output rows**, not twelve homogeneous cells: F5/F6 are reserved, F11 and F12 expand. The comparison script still compares `claim_status`, not the two new status axes (`compare_modes.py:19,51–53`). Its apparent full agreement can ignore a material v12 status difference. Stage-one outputs receive no substantive schema validation before synthesis.

**Fix:** adopt one contract, replace hard-coded old instructions, validate atomic findings and derivations, attach all necessary premises/endorsement sources, and update comparison/export/replay together. Resolve F9/F10 and the language rule. Test contrasting live/provisional, staff/institutional, negative, conditional, companion-backed and translated cases. **Cost:** 2–4 author hours for decisions, roughly 16–32 engineering hours plus development review and measured API cost.

### F03. BLOCKER: the corpus and displayed coding inputs are not yet frozen or internally consistent

**Items:** 1–3, 8, 10, 12, 23. **Evidence:** unit manifest, `text_sha256`, keys `IL_IL_BoI_2024` and `IL_CAND-111`; candidate CSV count columns; `extra/TALK_DEV_SAMPLE_MB_relevance_only.xlsx`, `CODE!B42,J42,K42`; sample CSV `unit_text_sha256`; `unitise.py:107,119–125`.

Two Israel records each contain the same 2,187-unit text, with different random-control selections. The registered development unit at `CODE!B42` has a non-empty text hash, but `J42` is empty. This is not merely an unanswered label. Fourteen development units come from documents no longer in the current 208-document unit manifest. That is acceptable for explicitly historical development, but not for unqualified validation of the current pool. IDs do not include an immutable text/unitisation version.

**Fix:** choose a canonical publication, version and regenerate affected units/candidates; carry over labels only after exact input reconciliation. Recover the original displayed text for row 42 and obtain a fresh blind response. Keep excluded C0 documents as marked challenge material. Record raw and display-normalised text hashes. **Cost:** 1–2 author hours and 4–8 engineering hours; no production calls should precede it.

### F04. BLOCKER: the claimed fail-closed translation ingest still fails open

**Items:** 2, 3, 18, 21, 23. **Evidence:** `scripts/translation/ingest_translations.py:26,33,42,52–57,98–100`; `unitise.py:90–102,110–117`; `TRANSLATION_PROCEDURE.md:38`.

A synthetic response with correct markers but **no per-call metadata and no run system hash** was accepted with `status=ok`, even with `--expect TEST`. Hash comparisons run only when hashes exist; a missing metadata file skips completion and identity checks. Missing whole documents are enforced only if optional `--expect` is supplied. Duplicate response basenames overwrite earlier entries in `found`. Unitisation reads translations found on disk rather than requiring a successful, matching manifest entry and checking its translation hash. These are executable admission gaps, not demonstrated corruption of the existing translations.

**Fix:** require metadata, expected document/chunk inventories and every identity hash; reject duplicate response identities; validate raw bytes separately from normalised text; consume only explicitly pinned successful translation records. Add negative fixtures. **Cost:** approximately 4–8 engineering hours and a source-archive verification pass; repeat only inputs that fail validation or semantic review.

### F05. BLOCKER: the run-record check can certify a fictitious run

**Items:** 2, 18–20, 23. **Evidence:** `scripts/pipeline/run_statement.py:13–17,23–48`; `RUN_RECORD_SPEC.md:15–44`.

A fixture with placeholder hashes, 999 supposedly completed calls, a header-only `CALLS.csv`, no responses and an empty input list produced **zero checker problems**. The checker validates presence of selected metadata keys and column headings, not artifacts or reconciliation. Omitting `spec` bypasses new-spec validation, regardless of run date. `retried`, `parsed_ok`, response/batch IDs, packed IDs and several other specified fields are not enforced. Checking whether the interface string contains “chat” would also reject a legitimate API called “Chat Completions API” while accepting an uninformative “API”.

**Fix:** use typed schemas, an explicit legacy allowlist and endpoint/interface enums; verify hashes, inventories, call/attempt counts, exact output IDs, parsing and final response selection. Separate logical requests from attempts. **Cost:** 4–8 engineering hours plus integration tests. The current green check is not evidence of complete provenance.

### F06. BLOCKER: the reference separation rule is not implemented and ignores packed-page exposure

**Items:** 2, 8, 10, 13, 23. **Evidence:** calibration draft lines 16–19, 24, 37; `draw_agreement_sample.py:24–25,61–65,70–82`; `build_requests.py:33–44`.

The drawer excludes only exact development unit IDs, not paragraphs, pages, aliases or the C1–C3 exposure planned by the draft. Full-page factor tests label additional units beyond C0. Existing sample metadata has no explicit paragraph field. A unit on a calibration page can therefore enter the nominally independent reference, including as a duplicate edition under another ID.

**Fix:** register every displayed and model-labelled context span; exclude canonical page blocks for a design that may use page packing. Bind blocks to the text version and duplicate-publication map. Declare evaluation conditional on the remaining pages, with coverage of excluded pages reported. **Cost:** 3–6 engineering hours and about 1 author hour to approve the estimand.

### F07. BLOCKER for adopting the savings: the factor-test rule does not establish non-inferiority

**Items:** 8, 9, 13, 22. **Evidence:** calibration draft lines 21–27, 35–37; ADR-006 B.1–B.2.

“Not below baseline test-retest” and “inside its bootstrap interval” are different rules. Neither measures the paired change in error against an independent reference. A cheap variant can agree with a wrong baseline; small samples can make a harmful difference inconclusive. Packing and reasoning are tested separately but their proposed combination is not. The regression rule selects among noisy outcomes by requiring improvement/no loss in every model/facet.

**Fix:** predeclare tolerances, paired clustered uncertainty, critical-error rules and an inconclusive outcome; test the combined selected settings. Default to the baseline when the saving is not supported, or explicitly narrow the claim instead of calling equivalence established. **Cost:** 2–4 design/scoring hours; API cost must be measured. A 120-unit experiment cannot establish rare-value equivalence.

### F08. BLOCKER for unrestricted translated claims: language coverage and translation restrictions conflict

**Items:** 1, 3, 7, 21, 23–25. **Evidence:** readiness rows 3–5,14; contract line 157; `TRANSLATION_PROCEDURE.md:36–48`; benchmark JSON; corpus coverage columns.

Fourteen untranslated documents in seven T3 projects remain outside the readable pool; Chile and Czechia have none. The contract excludes route-D cells from the primary human-verified matrix, whereas newer prose proposes narrower status/modality restrictions and English-only processing. These must not be silently reconciled by the runner. The weighted benchmark score assumes unjudgeable pairs are missing at random within strata. It is not a 31% source-translation error rate.

**Fix:** translate the missing eligible evidence or explicitly restrict the population and project claims; validate consequential translated evidence against source language or an authentic independent edition. Finish unmatched-pair review and show unjudgeability as its own outcome. **Cost:** the package's $10–20 translation estimate is unverified; add roughly 2–4 author hours for benchmark follow-up, with bilingual review separately budgeted.

### F09. MAJOR: publisher metadata and institutional voice remain conflated

**Items:** 2, 7, 12, 23, 25. **Evidence:** `unitise.py:34–40,123–125`; issuer ledger `issuer_type,voice_class`; unit manifest `issuer_type`; L2 lines 4,18,25–27; schema lines 21,192–202.

There are **117 issuer-type disagreements** between current unit-manifest rows and matching issuer-ledger rows; 113 unit-manifest rows say `not_recorded`. `BS_CAND-030` is labelled legislature by the heuristic because its issuer string includes “Official Gazette”. A staff author's position is not necessarily the institutional position merely because a central bank publishes it. OWN-based event histories need an explicit authority filter, not just the F-cell prohibition on staff evidence.

**Fix:** one reviewed header source, shared by humans/models/analysis; separate speaker, publisher and decision authority; define institutional eligibility for talk-derived milestones. Treat the two legislation-coded manifest rows as review flags, not proven source-rule violations. **Cost:** 2–5 author hours for focused metadata review and 2–4 engineering hours.

### F10. MAJOR: project absence, “first”, and highest-rung claims exceed what the candidate pipeline observes

**Items:** 4, 7, 14, 17, 23–25. **Evidence:** ADR-006 A.3 line 13; schema lines 184–200; candidate CSV; `select_candidates.py:9–12,26–45`.

There are 110,366 unsent non-X units and 43,627 X units. A positive quotation can establish an observed statement; it cannot establish absence or the earliest true statement. Random controls estimate residual prevalence only with adequate validated labels and explicit weights. X has zero inclusion probability. Legal/architectural basis, endorsement and operation are distinct attributes, not necessarily stages of one progression. Majority-by-facet can create a joint profile no model supplied; aspect2 has no separate stance/status.

**Fix:** say “earliest located in the searched corpus”; audit earlier source material and model negatives for consequential claims; keep unknown separate from no finding; report a status/basis vector rather than an assumed ladder. Preserve raw model tuples and flag incoherent consensus tuples. **Cost:** 2–4 design hours; source checks depend on the number of retained project claims.

### F11. MAJOR: “U” mixes instrument usability with coder uncertainty

**Items:** 2, 8, 9, 12. **Evidence:** L1 lines 5,14; codebook lines 5–7; workbook `CODE!J9,K9,J25,K25,J41,K41,J91,K91,J99,K99`; `unitise.py:61–80`; `select_candidates.py:26–31`.

The returned U labels include headings and grammatically complete prose as well as damaged fragments. Structural examples are detailed below without re-labelling the units. The filter also still excludes the invented complete sentence “Privacy policy prohibits disclosure.” Its substantive applicability would need context, but this proves that the rule is not simply “exclude non-sentences”. Splitting on colons/semicolons and treating blank-line blocks as paragraphs creates table/list units and page-boundary context loss.

**Fix:** clarify content-unclear versus difficult-to-classify; add a separate diagnostic uncertainty field; re-instruct both coders without supplying this auditor's labels. Validate unitisation and excluded-X material before freezing denominators. **Cost:** 1–2 author hours and 4–8 engineering hours for targeted repairs and fixtures, not a promise to perfect PDF reading order.

### F12. MAJOR: request packing changes both context and dependency

**Items:** 8, 10, 12, 15, 22. **Evidence:** `context.py:12–24`; `build_requests.py:21–44`; supplied request pairs.

The page renderer unions windows. In an eight-sentence synthetic paragraph, a single request for u1 contains 1,492 characters while a two-target page request contains 2,980; u1 now sees a sentence absent from its single-unit view. It also sees other paragraphs. This is an instrument change, not only a transport saving. The L2 preamble asserts an earlier stage judged each unit relevant even when the model's own L1 rejected a unit admitted by another model.

**Fix:** make the coding view match the selected model input, record target/context membership and packing order, and explicitly instruct L2 how to handle union-admitted units without assuming relevance. Score request-level dependence. **Cost:** 2–4 engineering hours plus the factor test.

### F13. MAJOR: the data-availability promise conflicts with the journal's current policy

**Items:** 6, 18–20. **Evidence:** `RUN_RECORD_SPEC.md:41–44,54–57`; verified Data & Policy research-transparency policy [R6].

The specification promises source/extraction material “available on request”, while the journal expressly rejects a bare on-request availability statement. A legal restriction can be explained and reviewed, but it needs concrete access conditions. Hashes do not let readers reconstruct unavailable source bytes. The claim of API-free replay from committed extraction outputs is not fulfilled merely by publishing hashes of withheld outputs.

**Fix:** deposit all lawful analytical outputs and replay dependencies, obtain stable source/archive references and a rights/access manifest, and specify restricted access where needed. Do not assume every official document has identical redistribution restrictions or that all short derived metadata must be withheld. **Cost:** 3–6 author/editorial hours plus engineering packaging; permission delays are unknown.

### F14. MAJOR: companion linking and cutoff eligibility are still unverified evidence relationships

**Items:** 1–3, 7, 18, 23, 25. **Evidence:** `COMPANION_LINKS_2026-11-13.csv`, `link_basis,url,decision_source`; source rule lines 12,33,40–47; contract lines 19,37,57.

Only 194 of 283 companions are linked by the same year; 87 use a nearest year and two have no dated evidence link. All 283 URL cells in this manifest are empty. The links are navigational, not proof that a particular law endorses a particular proposition. Most companions, including potential status material, lack an author review. Current corpus exports expose year but not the cutoff/version eligibility needed for the contract's 18 October 2026 cutoff.

**Fix:** retain bibliographic joins to actual URLs, verify claim-specific endorsement links and dates, audit a prespecified sample of excluded/companion material for missed eligible claims, and adopt one cutoff with precision-aware eligibility. **Cost:** 2–4 author hours for rule/metadata decisions, then source-dependent review.

### F15. MAJOR: sampling and scoring do not yet support population or rare-value validation

**Items:** 5, 8–10, 17, 22. **Evidence:** `draw_agreement_sample.py:24–26,41–53,61–82`; `score_agreement.py:14,38–47,66–79`.

The current round-robin quota sample is a coverage design, not a supplied probability-weighted corpus validation sample. The bootstrap explicitly conditions on its sample and still resamples units rather than request/document clusters. Optional second aspects and flags are not scored. Rare values receive unknown effective sample sizes. The declared 20% repeat lacks an exact sampling unit and a rule for replaying the same packed contexts.

**Fix:** distinguish challenge and probability components; retain inclusion probabilities; evaluate each value's support, false positives and false negatives; score secondary aspects/flags if used. Repeat complete original request bodies and report both conditional L2 stability and end-to-end stability. **Cost:** 3–6 engineering/design hours plus the human reference workload in F01.

### F16. MAJOR: absence of changes is not a stopping rule for a calibrated instrument

**Items:** 8, 9, 11, 13. **Evidence:** calibration draft lines 31–37,61–65.

A round can produce no changes because it contains no difficult positive examples, because a reviewer accepts an anchor, or because one severe failure occurs only once. Requiring two examples before repairing a clear defect is inappropriate; requiring every round to end in a change, as ADR-006 A.2 suggests, is equally inappropriate. Repeated C0 scoring provides regression evidence, not fresh validation.

**Fix:** time-box rounds, separate rule defects from performance optimisation, allow a single proven critical defect to trigger correction, use a fresh final development check, and reduce scope when planned gates remain unmet. **Cost:** about 1 author hour to adopt the replacement rules.

### F17. MAJOR: provider diversity and identity are not established by brand names

**Items:** 11, 14, 16–20, 22. **Evidence:** calibration draft lines 9,52–53; ADR-006 lines 17,23–34; current DeepSeek documentation [R7–R9].

The preregistered CN/HK/TW agreement contrast conflates topic, genre, route and model error. Two other models do not supply ground truth. Current DeepSeek documentation maps v4-pro to a dated version; the documented repointing on the pricing page concerns legacy Flash names. That does not verify the brief's implied v4-pro October repointing. Provider defaults, endpoint semantics, context/output limits, retention terms and pricing must be checked for the exact API account and model.

**Fix:** archive model/endpoint documentation, run small capability probes, monitor fixed sentinel requests for drift, count refusals separately, and compare blind-reference errors within matched strata. Treat the precise v4-pro repointing claim as UNVERIFIED. **Cost:** 2–4 technical hours and small measured probe cost.

### F18. MINOR arithmetic/documentation; MAJOR budgeting uncertainty

**Items:** 1–3, 18, 22–23. **Evidence:** `01_AUDIT_BRIEF.md` sections 2,5; `PROJECT_BRIEF.md:52–67,89–94`; ADR-006 line 34; `update_brief.py:19–23,31,42–55`.

The main counts reproduce, but “283 linked to evidence of the same year” is false. The generated 30% and prose 31% M figures come from rounding a stored 0.305. The briefing date excludes newer human inputs; the status table still says MB coding is pending. The cost bounds add correctly, but no reproducible cost ledger supports the provider token assumptions, 2–4× counterfactual or full-run estimate. Twelve request pairs are supplied, not 120 pairs. Passing 29 tests does not test the new talk runner, which does not exist.

**Fix:** distinguish recorded totals from verified unique publications, remove stale prose, format benchmark percentages to one decimal place, and create a per-stage/provider usage and price ledger with measured calibration usage and explicit exclusions. **Cost:** 1–2 engineering hours for prose/count fixes, plus cost instrumentation already required for the runner.

## 3. Answers to the 25 questions

### 1. Recount of the brief and generated block

The recorded totals reproduce: 44 frame projects; 777 master-file rows; 772 document-decision rows; 234 in-frame evidence rows and 230 publications after the four registered edition links; tiers 8/8/28; 208 readable documents in 42 projects, routes A/B/D 163/15/30; 174,052 units; candidates 8,088/6,231/5,740, total 20,059. MB relevance is 58 R, 36 N, 24 U, two invalid/blank entries. Translation logs contain 199 successful registered calls and 43 unique non-BENCH translated documents across three runs.

These are manifest counts, not proof of source completeness. One unlinked duplicate reduces actual unique readable texts/publications by one. Companions total 283, 64 author-reviewed, but only 194 have same-year links. The benchmark is 30.5% M on the stored rounded calculation, displayed inconsistently as 30% and 31%. The budget adds to $320–455; a 30% reserve yields $416–591.50. Provider-level costs and the claimed 2–4× saving cannot be reconstructed from the supplied CSVs. See Table A for all generated rows and Table B for readiness.

### 2. Readiness, row by row, and missing prerequisites

Table B reviews all 23 rows. Most admissions of unfinished work are accurate; row 20 overstates provenance enforcement and row 11 understates the blank input cell. The opening verdict incorrectly allows metadata, translation and scope decisions affecting calibration inputs to remain unresolved.

Before the first paid calibration call add: immutable input/display hashes; duplicate and stale-sample handling; raw workbook integrity; shared header/context rules; R/N/U clarification; strict output/parser tests; exact request/attempt identity; complete expected inventories; tested run-record validation; protected reference page blocks; a rule for union-admitted L2 units; preregistered factor tolerances and failure states; verified provider parameters and a cost cap. Only inputs actually used in the bounded pilot need be ready, but later changes require a documented calibration recheck.

Before production add: source/cutoff and page-span freeze; language-use policy; probability-aware reference sampling; independent facet evidence or restricted claims; X/model-negative/omitted-page audits; consensus coherence; claim-specific companion checks; repeated-request design; output derivation and API-free replay; rights/access documentation; and release gates. A runner or workbook alone does not implement these methodological decisions.

### 3. Which 13 November findings remain open?

Table C maps all 18 earlier items. Real repairs include fixed-category AC1, undefined-alpha handling, detection of duplicate/invalid coder entries, the shared single-unit context renderer, expanded candidate dictionary, four explicit edition links, and the descriptive 44-project frame authorised by MB. The EU change is an author-approved change of scope, not an unresolved requirement to exclude it.

Partly closed: translation identity checks, unit quality, benchmark protection, issuer metadata, source-workbook import, bilingual alignment and denominator definitions. Still open: independent facet validity, rare-value evidence, translation transportability, cutoff/version eligibility, source-retrieval recall, X audit and a full replay deposit.

Closed only on paper or overstated: “fail-closed” ingestion accepts missing metadata; the run-record checker accepts nonexistent outputs; the sampling code lacks promised context separation; generated prose calls all companion links same-year; v12 prompt adoption is not accomplished by changing the contract path. The retired posture layer is labelled retired, but legacy code/tests are not evidence that replacement talk outputs work. All 29 supplied tests pass; this does not close these gaps.

### 4. Would the validation design be acceptable?

Potentially as a transparently bounded model-annotation dataset, but I would not accept its present claim that all seven facets and project summaries are validated. The strongest objection is circular validation: the same authors develop the taxonomy, inspect majority suggestions and then use their acceptance as evidence of accuracy. Artificial-error detection and checking selected positive quotations leave shared model errors and omissions unmeasured.

Authors may legitimately be domain coders. One author doing most verification is not automatically disqualifying. The problem is absence of an independent response channel for the key constructs and absence of value-specific sample support.

The cheapest repair is blank double-coding of 80–120 relevant units for voice/aspect, with pre-adjudication labels retained, combined with restricting the other facets to exploratory model outputs. Approximately 4–8 combined author hours is a planning allowance. For strong seven-facet claims use the fuller protocol below; do not pretend the same small set validates every rare value. An external domain reader on a subset is useful but does not make sparse evidence adequate.

### 5. A defensible planted-error design

Treat planted errors as an attention/error-detection experiment, not an accuracy correction. First establish source-supported target labels independently; a third model's output is not sufficient to certify an error. Use a coordinator who is not the reviewer. Commit the seed and encrypted/hashed allocation before review, reveal the key afterward, and keep natural model outputs unchanged in a separate file.

On 120 relevant verification units, plant approximately 10–15% of seven facet cells, about 84–126 cells, with no more than one planted facet per unit where feasible. Balance facets and include realistic confusions: provisional/endorsed, tested/operational, policy/architecture, speaker attribution, actor/aspect, modality and stance. Include both inflation and attenuation, plausible difficult errors and untouched controls. Avoid internally impossible combinations that advertise the manipulation; log unavoidable interactions.

Report attempts, correct detections, correct repairs, erroneous changes to untouched labels and abstentions by facet/error type, with unit-clustered uncertainty. Do not pool easy and consequential errors without weights. Detection on roughly 12–18 planted cells per facet is imprecise. No inverse-detection adjustment or bound on natural residual error is justified without a validated transportability model.

### 6. Reporting standards and checklist gaps

Use **Feuerriegel et al. (2026), Nature Human Behaviour, GUIDE-LLM** [R1], and **Gebru et al. (2021), Communications of the ACM, Datasheets for Datasets** [R2]. Apply **Grimmer and Stewart (2013), Political Analysis** [R3] as methodological guidance, not a compliance checklist. **Abdurahman et al. (2024), PNAS Nexus** [R4] supports task-specific caution. **Gallifant et al. (2025), Nature Medicine, TRIPOD-LLM** [R5] is a supplementary reporting analogy, not a CBDC-specific standard or journal requirement. These references were verified; full details/links appear below.

GUIDE-LLM gaps include exact operational versions/defaults (B.1–B.3), actual deployed prompts/instructions (C.1–C.2), independent validation and post-processing (E.1–E.2), and a functioning shareable runner (F.1). Disclose prompt-development assistance and provider relationships where applicable. Dataset documentation must cover selection, inaccessible documents, languages, transformations, intended/prohibited uses, maintenance and access restrictions.

Data & Policy requires a data-availability statement and does not accept a bare “available on request” promise [R6]. Completing a checklist reports limitations; it does not cure them.

### 7. Permitted and impermissible claims

Permitted after executing the stated checks: this is a versioned dataset of located statements in a specified, author-selected evidence corpus; relevance has measured agreement against blind human coding; other released labels have the particular validation or verification reported; model comparisons measure sensitivity to these model configurations; observed project statements have documented sources.

Not permitted: population-wide institutional privacy emphasis, comprehensive coverage of all official communications, validated seven-facet accuracy from anchored acceptance, source-language translation accuracy from English-to-English comparison, unbiased model consensus, absence of a commitment from missing evidence, or exact repeatability of hosted model generation.

Dates must mean the earliest located statement within the searched and eligible corpus, not the historical first statement. Named project tables require unknown/unavailable/conflict states and searches for missed positives. A source-checked positive claim is stronger than an unsupported negative.

“Reproducible” must specify whether it means numerical replay from released outputs, reconstruction with separately acquired sources, or a new stochastic model run. The dataset is descriptive of documentation, not a direct measurement of implemented privacy or legal enforceability.

### 8. Attack on the calibration draft

The fixed-document/unit/context principle is reasonable only after actual reconciliation. The factor rule is not a valid equivalence test; add paired non-inferiority tolerances and test interactions. Relevance should remain blind in every round, but preserve individual judgments before discussion and distinguish one-author development from two-author validation.

A hidden-vendor majority prefill reduces vendor cues but increases majority anchoring. Disagreement highlighting directs attention; randomise a no-highlight/blank subset. Cause codes need overlapping categories plus metadata, scope, context, parser and coder uncertainty. They are diagnoses, not mutually exclusive truth labels.

The two-occurrence change rule blocks repair of a single severe logic error. The “no model worsens on any facet” regression rule is noisy multiple selection and rewards overfitting. Keep regression for known defects; evaluate predictive loss with a prespecified tolerance on fresh material.

Stopping on no change can stop after an easy round. Model-informed additions are legitimate development but must remain separately tagged and included in the exposure map. Freeze is necessary; after a defect, invalidate affected outputs and validation rather than automatically rerunning unrelated stages. Never relabel a used reference as untouched.

### 9. Sample size and the 30-minute constraint

The relevant denominator is not 300 total units but the number of independently assessed instances of each value. C0 contains 58 author-R units; ten aspects and rare ENDORSED/OPERATIONAL/CRYPTOGRAPHIC values cannot be validated by nominal totals. At 1% prevalence a 60-unit simple random draw has about a 55% chance of containing no instances. Development enrichment helps discover defects, not estimate prevalence.

For roughly the same round time, use 40 fresh relevance units per round, allocated D/N/R 24/8/8 and balanced across routes, document genres and institutional/staff voice. Deep-review 20 of them for facets: ten chosen by source/metadata rules fixed before predictions and ten separately tagged challenge cases, with model-informed selection allowed only in later rounds. Rotate rare-value and rule coverage across rounds.

Time the first ten cases. Twenty seven-facet reviews plus blind relevance may exceed 30 minutes; reduce deep-review breadth or drop facets rather than force superficial agreement. Calibration rounds remain development. A separate reference and rare-value supplement are additional work, not free validation supplied by these rounds.

### 10. Appropriate disjointness

Use **canonical page-level blocks**, enlarged to include every actual displayed context span, because page packing is being considered. Unit-only separation permits a neighbour or repeated copy to leak; paragraph-only separation fails when full pages have already been labelled or shown during factor tests. Map duplicate publications and exact repeated text before splitting.

Document-disjoint evaluation is cleaner for a claim of generalisation to new documents, but is not necessary for estimating performance on untouched pages of this fixed corpus. It would exclude all 82 C0 documents and could distort coverage. Report the evaluation as conditional on unexposed page blocks, show excluded coverage, and do not claim document-generalisation. A secondary held-out-document check is useful if feasible.

Reserve the reference blocks before further development exposure; draw labels after freeze. Hashes of exclusions and page lists must be committed before selection. If revised unitisation changes page identities, re-establish separation before any calls. F-cell blind project reference requires its own project-level exposure rule; this talk split does not replace it.

### 11. One prompt across three models

One semantic prompt is defensible. Freeze a shared text definition and output schema, allow documented API-specific transport parameters, and evaluate all three models in every development round. “Low reasoning” is not necessarily the same computational intervention across providers. Report exact supported settings and omitted defaults.

Claude writing the prompts is a disclosed development dependency, not automatic invalidity. The relevant risks are correlated mistakes and optimisation toward one model. Mask vendor identity during review, inspect each model's errors and preserve every change's rationale. Do not select the winning model, prompt or consensus rule on the final reference.

Few-shot examples are optional. Prefer a small, balanced set of invented, author-approved minimal contrasts covering the difficult rules, with expected labels justified by the codebook. If real development examples are used, exclude their canonical context blocks and near-duplicates from evaluation and disclose their origin. Do not use sealed project outputs or unreviewed model-generated answers as authoritative examples. Compare zero-shot/few-shot during development only and retain one frozen choice.

### 12. Prompt ambiguities, output risks and unusable units

Key defects: the union L2 preamble assumes relevance; OWN conflates publisher/institution; the reported-competent-decision exception exists in English but not explicitly in Czech; “law in force” is overbroad without applicability to the coded proposition; multi-basis priority is unspecified; aspect2 inherits no separate stance/status; main-clause selection is ambiguous; modality lacks an uncertainty value; `anonymity_rejected` differs between general anonymity and cash-like anonymity; schema's PROGRAMMABILITY crosswalk is categorical while L1 is conditional.

Packing creates cross-target context and order dependence. Require exact unique IDs, correct cardinality, validated booleans/enums, no extra output, proper END handling, and explicit refusal/truncation/error states. The current schema is descriptive configuration, not a validating JSON Schema.

The 24 U responses mix structural defects and coder interpretation. Headings occur at J9/J27/J44; complete sentences at J25/J41/J91/J99; J67 is a substantive list-shaped passage. This is a structural description, not new relevance coding. J42 is blank despite its registered hash. Resolve the author’s interpretation, restore input integrity and recheck rules before calibration; do not automatically remove all U units.

### 13. Calibration protocol I would sign

The following is a proposed replacement, requiring author adoption. It permits bounded development before the entire production corpus is ready, but prohibits claiming a freeze that has not happened. Numerical tolerances are explicit proposed operating choices, not universal journal standards.

1. **Adopt the intended claims and reduce scope first.** State the finite corpus, cutoff, source rule, institutional voice, route-D restrictions and exact outputs. Choose whether seven facets will be independently assessed. If the authors refuse any blank facet coding, retain a model-coded exploratory facet layer and remove claims of independently validated facets. Commit the decision, including DS's position. Separate talk milestones from contractual commitments.

2. **Create one input identity manifest.** Assign canonical publication/edition IDs. Resolve the Israel duplicate. Record source bytes, extracted text, translated text, unitisation version, unit file, raw unit text, displayed context and header hashes. Maintain a mapping for surviving historical IDs rather than silently changing their meaning. Pin the exact manifests instead of selecting “latest”. No calibration input may be changed under its existing identity.

3. **Reconcile C0 before anyone sees model labels.** Preserve the returned MB workbook byte-for-byte. Recover `CODE!J42` from the registered input, determine what MB saw, and obtain a fresh blind response. Resolve invalid `T` at K71 without silently treating it as N/U. The I58 context mismatch is explained by an Excel safety apostrophe: removing that display escape reproduces the registered hash. Implement the inverse/display-hash rule explicitly. Keep the 14 units outside the current corpus as marked development/challenge observations. DS codes the reconciled material independently; lock both original submissions before discussion.

4. **Clarify the coding manual using invented examples.** Explain that U concerns unreadable/indeterminate content, not merely hesitation, table form or difficult relevance. Add separate uncertainty/reason notes. Resolve the English/Czech reported-authority exception, institutional versus staff voice, overlapping bases, main versus second proposition, modality and flags. Record a short training exercise outside the reference. Preserve pre-clarification C0 labels separately; do not call revised judgments originally blind to discussion.

5. **Audit the preprocessing boundary.** Inspect a metadata-stratified set of at least 60 X items and 60 retained units from outside the reference for extraction loss and context adequacy, without using model relevance predictions to choose them. Add table/list, cross-page, footnote, HTML navigation, short meaningful sentence and multi-column fixtures. Record source checks separately from deterministic text checks. If source recovery changes units, regenerate and version all affected inputs before continuing. The provided diagnostic sample is development material once inspected.

6. **Reserve exposure blocks now.** Track all C0 pages, all factor-test pages, displayed context, duplicates and later C1–C3 pages. Reserve disjoint canonical page blocks covering each route and major genre/tier for the final reference. Log source exposure separately from model-output exposure. No author sees reference model outputs until independent labels are locked. No frozen F-reference project may be exposed to F-cell model values during talk review without explicitly changing its eligibility.

7. **Test the infrastructure offline.** Implement the three-provider runner, strict L1/L2 parser and typed run records. Include missing/duplicate/invented/reordered IDs, invalid enums/types, extra text, absent END, truncation, refusal, empty response, timeout, retry, batch partial completion and resume mismatch. Verify that a malformed request cannot silently become an ordinary N or unknown substantive label. Require hashes and expected inventories. Demonstrate numerical replay on a synthetic miniature dataset. Record secret-free request bodies and complete provider response envelopes in the private archive.

8. **Approve the bounded calibration budget.** Use only provider APIs and authorised accounts; no paid call is made merely by adopting this report. Verify endpoint/model availability, reasoning controls, system-role semantics, token/output limits and prices. Run a few explicitly developmental capability calls under a small cap, then revise the estimate from observed usage. Use a fixed maximum spend and stop on identity drift, incomplete coverage or cost-cap breach. Archive dated documentation and settings. Treat these calls as development exposures.

9. **Run C0 factor tests for every model.** Baseline: identical single-unit requests twice with explicitly recorded default reasoning. Compare packing alone and lower reasoning alone with the baseline, then test the combined proposed cheap setting. Use the same target units for scored comparisons; every additional packed-page target enters the exposure registry. If packing is selected, humans must see the corresponding information view for subsequent reference coding, or the analysis must explicitly separate input-view differences from model errors. Test L2 on a fixed candidate set, independent of each variant's relevance predictions, so an easier subset cannot create apparent savings.

10. **Use a prespecified factor decision rule.** For relevance, compare paired error and recall against locked human adjudication; bootstrap paired outcomes by page/document, preserving strata. Proposed non-inferiority margins: at most three percentage points worse in recall and three points worse in total R/N/U error. Require the one-sided 95% upper bound on loss to be below the chosen margin for each retained model; report unsupported cases as inconclusive, not equivalent. Add a critical-error gate: no unexplained newly unsupported ENDORSED/OPERATIONAL judgment in the reviewed challenge cases, and no unrecovered identifier/coverage failures. Facet agreement against another model run is only a stability diagnostic; independent development checks are needed for accuracy. With C0 alone these gates will often be inconclusive. Keep baseline settings rather than increasing the sample indefinitely to obtain a favourable result. An author may adopt a different design tradeoff only by recording that equivalence was not established.

11. **Conduct at most three fresh development rounds.** Use 40 units per round, D/N/R 24/8/8, with fixed metadata route/genre/voice coverage and document caps. Commit sampling seeds and exclusions before drawing. An author codes all relevance labels blind; deep-review 20 units for all retained facets. Ten are selected by predeclared source/metadata rules before seeing predictions; ten are challenge units, which may be model-informed in rounds two/three. Preserve the distinction. If the authors retain 60-unit rounds, reserve enough time for actual reading; do not claim 420 facet decisions plus reading are reliably completed in 30 minutes.

12. **Reduce anchoring and document corrections.** In development only, randomly assign a small subset to blank first-pass facet coding before showing the prefill. For the remainder, show a vendor-masked prefill; randomise whether disagreement highlighting is shown or report it as an intervention. Save all three raw predictions, the exact displayed suggestion, whether it was highlighted, human acceptance/correction/abstention, source consulted and elapsed time. Causes may be multi-label: rule, prompt, model slip, unitisation/context, translation, metadata, parser or coder uncertainty. Never use planted errors in the raw dataset or pretend their corrected labels are natural model outputs.

13. **Apply a constrained change rule.** Repair a single demonstrated severe logic, provenance or parser defect immediately. For ambiguous semantic revisions require an author rationale and a minimal contrast; repeated examples strengthen the case but are not mandatory. No change solely to make a vendor win. Every change has a versioned diff, motivating IDs, expected effect and affected stages. Change Czech codebook, English prompt and validating schema together. Add no corpus sentence to a prompt without registering its exposure.

14. **Regress deterministically; assess accuracy separately.** Rerun fixed prior development inputs under the revised settings for every model. Preserve known-defect fixtures and check the target confusion. Compare paired changes with the predeclared tolerance; do not require every noisy point estimate to improve. Investigate systematic harm to one model or class. Do not repeatedly sample fresh model answers until a preferred response appears. Freeze the selected attempt/retry policy in advance.

15. **Stop by scope and evidence, not by fatigue.** Stop after three rounds plus one fresh 40-unit development confirmation set, or earlier only if required rule coverage, parser gates and a fresh confirmation all pass. The confirmation set is subsequently development, never the reference. If a retained facet still has unresolved critical ambiguity, drop/merge it or postpone its strong claims. Record failures and abandoned versions. A fourth round requires an explicit scope/budget amendment and new untouched material, not repeated use of the final reference.

16. **Freeze before final evaluation.** Register corpus/text hashes, cutoff/precision, page spans, all prompts/examples, header/context renderer, validating schemas, models/endpoints/parameters, consensus and abstention rules, handling of U/failures, rare-value policy, sampling seeds/probabilities, replicate design, analysis estimands/weights, release tolerances and correction policy. Specify whether aspect2 participates in project claims and how conflicting two-proposition units are handled. Define statistical missingness separately from substantive absence. Archive the code and dependency lock.

17. **Draw and lock the 400-unit relevance reference.** Use a probability design within the untouched page-block population, not an undocumented round-robin convenience draw. A practical allocation is D/N/R 240/80/80, with declared route quotas and known selection probabilities; document caps require an actual two-stage design, not weights guessed afterward. Both authors code relevance independently. Preserve labels before adjudication; report counts, confusion, R precision/recall, alpha/AC1, missing/U rates, stratum-specific and weighted results, and clustered intervals. The evaluation population excludes exposed blocks; disclose its coverage. Do not use this sample to change prompts. If a proposed release gate fails, report the failure and develop a new version with a fresh reference or narrow the release.

18. **Add independent facet evidence.** Select up to 120 human-adjudicated relevant reference units for blank coding of all retained facets by both authors, before showing any facet outputs. If the 400 contain fewer, use one predeclared top-up of up to 200 untouched units, screened blind for relevance; report its selection and nonattainment rather than sampling until a desired score appears. For rare consequential values, add a fixed challenge supplement of at most 60 source-selected units, separately reported. Aim for at least 20 independently adjudicated instances and enough model-positive cases to examine both false negatives and false positives for a claimed value; this is an evidence floor, not proof of precision. Values below it receive no general accuracy claim. Record independent labels, adjudication, support counts, confusion and joint/end-to-end errors. If the authors choose only voice/aspect validation, mark every other facet accordingly.

19. **Run the verification experiment separately.** Apply question 5's planted-error procedure to a distinct verification presentation. A coordinator certifies the intended wrong values and keeps the key hidden. Report error detection/repair and unnecessary edits by facet/type. Reviewers may consent to an undisclosed seeded quality check; the particular locations must remain hidden. Keep the natural-output validation sample separate from manipulation performance. Do not treat the detection figure as a bound on dataset accuracy.

20. **Execute the frozen three-model design.** L1 runs on the complete candidate inventory. L2 runs on the fixed union admitted by any model, with an explicit instruction that relevance is not assumed and a recorded way to flag inapplicability. Save each model's native L1→L2 result, the union analysis and the consensus. Require two valid votes for a majority; a failure is not a vote for N, and a three-way R/N/U split is unresolved. Check facet-wise consensus for impossible combinations. Adjudications are a separate, versioned layer, not silently substituted raw model output.

21. **Repeat requests, not isolated rows.** Draw the registered stratified 20% repeat at original request level, retain all units/context/order in those requests and record realised unit coverage. Repeat both stages as specified. Report conditional L2 stability on identical inputs and end-to-end stability separately; the latter includes L1 gating. Interleave vendors and runs in time where feasible, archive returned identity/fingerprint, and monitor a fixed sentinel set. If an alias changes, split versions and apply the registered drift response rather than pooling them.

22. **Apply source and release gates.** Validate model-negative random controls and a separate X sample; estimate retrieval residual prevalence with weights and model-error limitations. Check every reported positive project claim against the source, and investigate earlier/negative evidence for “first” or no-finding claims. For commitments require complete qualifiers, competent authority, located and entailed evidence, conflict/supersession checks, language eligibility and no processing failure. Predeclared relevance performance targets must be tied to intended claims; a reasonable proposed target is a one-sided 95% lower bound of 0.90 for R recall on the reference, with class-support caveats. If not met, do not issue corpus-wide absence/recall claims. Keep estimates even when a gate fails.

23. **Calibrate F extraction separately before F production.** Adopt and implement v12 first. Use NO/UK plus at least three contrasting cases selected by metadata, such as a live system, staff-heavy corpus and translated/companion-backed case. Opening these is an author-approved development exposure and removes them from the blind project reference. Use a 40–60-case atomic-claim challenge battery from the adopted contract. Lock the remaining project-level human reference before opening their model fills, or explicitly replace the older ambitious F-reference protocol with a narrower signed design. The November deadline is not a reason to waive these steps.

24. **Publish a replayable, layered deposit.** Release machine outputs, human labels, seed allocations after unblinding, adjudications, final derivations, unit locators/hashes, coverage, failed calls and executable analysis. Keep restricted text/request archives under a specified access mechanism. Run the released replay from a clean environment and compare every reported number. Record which stages must rerun after each type of change; an analysis-only bug need not trigger new API calls when the necessary raw outputs survive.

### 14. Majority versus alternatives

Majority is a defensible prespecified aggregation rule, not a validity guarantee. It reduces idiosyncratic errors only under favourable error dependence and comparable model competence. With R/N/U, three different votes must remain unresolved; processing failures and refusals need separate treatment. Facet-wise majorities can produce an incoherent tuple, so preserve votes and validate combinations.

A primary model plus two robustness models is easier to interpret but makes primary selection consequential. Unanimity sacrifices coverage and recall, and common mistakes still survive. Three separate datasets preserve disagreement but shift the combination burden to users. I would release all raw model layers and a clearly defined majority layer, with human adjudications separate, rather than three opaque final products.

Preregister models/versions, equal or unequal vote weights, tie/U/missing handling, union L2 eligibility, coherence rules, model-exclusion criteria, adjudication triggers, sensitivity analyses and whether aggregate tables use native chains or consensus. Do not choose the rule after seeing attractive project results. For F-cells, voting on values does not replace rule-C admissibility or coherent supporting claims.

### 15. Union relevance versus each model's own chain

Use both, for different questions. L2 on the union gives all models the same target set and supports a conditional facet comparison. Native chains measure the functioning end-to-end instrument, including each model's missed relevance. Agreement only on the intersection of model-R units discards difficult cases and can inflate apparent performance.

The union is itself model-selected and excludes units all three miss. It therefore cannot estimate full-corpus facet validity. Include human-relevant/model-negative reference cases in an explicit end-to-end evaluation; retain their original omission rather than retroactively pretending they entered the model dataset.

Modify the L2 preamble: a union-admitted unit was not necessarily judged relevant by that model, and may not be relevant at all. Provide an explicit inapplicable/relevance-review channel and retain it separately from substantive facet values. Report the number reaching each stage, pairwise/three-way agreement on the fixed union, native-chain errors, and human-reference errors. Do not compare models on different L2 denominators without stating that difference.

### 16. DeepSeek risks and adequacy of its check

The CN/HK/TW versus rest agreement comparison is insufficient: it cannot distinguish political sensitivity from language, genre, translation, topic or shared errors. Prespecify refusal/omission rates, label distributions and errors against blind human reference within matched strata; report small subgroup support rather than a confident bias test.

Current official documentation lists `deepseek-v4-pro` mapped to `DeepSeek-V4-Pro-0813`, a 1M context and a stated 384K maximum output [R7]. These are advertised limits, not evidence that every account/endpoint accepts the intended request. The same page documents legacy **Flash** alias redirection, not the claimed October v4-pro change; that claim is UNVERIFIED. Archive the actual mapping before calls.

Review the API-specific terms and exact endpoint settings [R8–R9]; do not infer zero retention from a stateless conversation API. A pinned open-weight revision improves preservation of model identity and permits local execution, but also needs weights/tokenizer/chat-template/quantisation/runtime hashes and resources. It is not automatically less biased or bit-reproducible. Prefer it if auditability gains justify the operational burden; it need not replace a functioning API model solely because of national origin.

### 17. What three-model agreement can show

Acceptable wording:

“Using identical registered text inputs and coding definitions, the three specified model configurations produced the reported levels of agreement. This quantifies sensitivity to those model configurations on the stated eligible units. It does not establish correctness, independence of errors, representativeness of the sources, translation fidelity or equivalence to human interpretation. Accuracy and error analyses are reported separately against the locked human reference, with limited support for rare values.”

Report raw agreement, marginal distributions, confusion and per-value counts beside alpha/AC1; include U, abstentions and processing failures explicitly. State whether a statistic is conditional on union relevance, mutually relevant units or the complete chain. Cluster by document/request where applicable.

A majority of three correlated models can confidently agree on the same mistaken rule or translation. Agreement is therefore neither a gold standard nor an empirical upper/lower bound on validity. A lack of disagreement in a rare subgroup may simply reflect small sample size or degenerate label distributions.

### 18. Run-record specification, missing and superfluous fields

Table D checks the specified fields and adds the deposit requirements. Keep the existing fields, but enforce their types, contents and artifact relationships. Add immutable run/attempt IDs, parent-stage identity, actual secret-free request bodies, endpoint/API version, batch/custom IDs, response envelopes, fingerprints where supplied, parser/normalisation/derivation versions, complete output/target inventories, seeds/inclusion probabilities, alias mapping dates, refusal/error classification, prices and rights/access terms.

Tokenizer-independent hashes are already partly contemplated by `user_sha256` and input SHA-256. The missing distinction is exact bytes versus normalised UTF-8 text versus canonical request JSON; define each, store the actual payload and verify reconstruction. A model tokenizer version is an additional cost/context record, not a substitute.

No required scientific field is obviously superfluous. Avoid credentials, unnecessary personal account identifiers and huge duplicated public text archives. Store model-returned identifiers once per call plus a run summary; a single run-level string is insufficient if aliases drift. Preserve provider-reported reasoning summaries/tokens if returned and permitted; do not claim access to hidden internal reasoning. The checker currently does not enforce this specification.

### 19. Reproducibility without publishing source text

Hashes, locators, labels and rebuilding scripts support verification of identity and potentially replay of released analyses. They do not guarantee reconstruction of unavailable or mutable source documents. The strongest honest offer is: exact numerical replay from the released nonrestricted analytical inputs; conditional reconstruction of requests for readers who lawfully acquire matching source versions; separately reported stochastic API reruns.

Proposed availability text, to complete with actual identifiers:

“Version [v] of the labels, metadata, human judgments, adjudications and analysis code is deposited at [DOI]. These materials reproduce the reported tables without new model calls. Source documents and text-bearing requests are listed in a rights and access manifest with issuer URLs, retrieval dates, version hashes and locators. Materials that cannot lawfully be redistributed are excluded from the public deposit; their restrictions and any permitted controlled-access procedure are specified there. Request reconstruction requires the listed source versions and may be impossible where they are no longer obtainable. Hosted-model reruns are not guaranteed to reproduce the original responses.”

Do not leave placeholders in the submitted paper or promise unrestricted on-request access; Data & Policy's policy requires a concrete explanation [R6].

### 20. Retirement and aliases

For each model state provider, requested ID, returned ID, documented underlying version, endpoint/API version, access dates, settings and omitted defaults, request form, SDK/runtime, inference window, refusals/retries, and whether the provider guarantees a fixed snapshot. A dated identifier is not evidence that the authors possess the weights.

Archive now: the exact secret-free payloads and response envelopes; relevant response headers/fingerprints if supplied; prompt/schema/contract bytes; source and transformed-text versions; parser and SDK dependencies; pricing, limits, alias mapping and applicable terms as dated snapshots; batch result files and all failed attempts. Provider dashboards and mutable documentation may disappear or change.

State explicitly that preserved outputs permit analysis replay but hosted generation may become unavailable. For open weights additionally preserve revision/weight hashes, tokenizer and chat template, quantisation, inference engine and hardware/numerical settings. Even then, exact generation may depend on nondeterministic kernels. No invented snapshot suffix should be substituted for an API-accepted identifier.

### 21. Must older translation and NO/UK runs be repeated?

Not merely because a commit or reasoning setting was not recorded. Preserve their known hashes and outputs, reconstruct only settings supported by contemporaneous evidence, and mark the rest unknown. Do not backfill a guessed commit or current default as a historical fact.

NO/UK pilot fills are development artifacts; they need not be repeated to validate historical bookkeeping. They **must** be rerun under the adopted v12 instrument before they become current instrument results, because schema, claims and status semantics change materially.

Existing translations can be retained as fixed input versions if their identity/completeness is verified and their permitted use is explicitly adopted. Re-extract/retranslate PE CAND-250 and any other demonstrated text-order/completeness failures. Missing provenance may restrict their claims without requiring blanket retranslation. Applying a prospective record standard retroactively must include a documented legacy policy; currently the specification simultaneously prohibits noncompliant result inputs and lists pre-spec translation production. Resolve that contradiction before publication.

### 22. Cost measures: risk, test and decision

| Measure | Assessment and decision |
|---|---|
| Page packing | Changes context, target interactions and output risk. Current test inadequate. Accept only after paired combined-setting tests and context-consistent validation. |
| Low reasoning | Can change semantic errors and refusals; provider settings are not comparable by name. Test both L1 and L2 and retain baseline where inconclusive. |
| Batch API | Primarily operational, but model/version/time and partial failures can differ. Accept with identical payload/settings, identity checks and complete reconciliation. |
| Cached system prompt | Accept exact-prefix caching; no shortening or changed instructions. Record cache behaviour and charges. |
| 20% same-model repeat | Useful stability sample, not independent validation. Replay original packed requests, stratify, include failures and report rare-value support. |
| CBDC page spans | Selection can miss pronouns, annexes, tables and distant definitions. Do not accept the current single-document demonstration as general validation. Audit omitted pages and apply uniform boundaries. |
| One primary extraction mode | Accept after complete-coverage contrasting-case tests; mode disagreement is not itself truth. Restricting the second mode to T1/T2 leaves T3 mode robustness unassessed. |

Estimate savings from measured usage and archived prices after freezing inputs.

### 23. Correct sequence to the first production call

First adopt scope, source cutoff, language restrictions and claim definitions. Resolve duplicates, missing texts/OCR decisions, PE retranslation, general-publication spans and issuer/voice metadata. Regenerate and hash units/candidates; reconcile C0 and reserve reference exposure blocks. Repair/test the runner, parser, ingest and provenance; then run bounded calibration, with human judgments locked first. Complete benchmark follow-up and input sensitivity checks before the final freeze.

Adopt and register the frozen instrument, consensus, validation and replicate designs. Draw the reference and lock independent labels before opening model outputs. Run a controlled evaluation and apply release/failure gates; only then proceed to the full production schedule. A preregistered blinded full run can technically precede evaluation scoring, but risks wasting the entire run and does not earn a GO verdict here.

Premature spending points: translating a document later excluded; coding units before page-span or retranslation changes; facet calls before issuer correction; page-packed calibration before context decisions; F extraction before contract/schema adoption; and full runs before performance/coverage gates. Record dependencies so purely analytical corrections do not force needless API repeats.

### 24. Untranslated T3 evidence

Running the current readable subset is defensible only for explicitly restricted observed-corpus statements with visible missingness. It cannot support a 44-project comparative claim interpreted as equivalent coverage. Chile/Czechia must be “no readable evidence”, not no talk/no commitment. Iceland, Madagascar and Uruguay each have one readable document because of these exclusions; Macao also has one, for other availability reasons.

I prefer translating the 14 eligible documents, 255 pages, in seven projects before freezing talk coverage. The supplied $10–20 estimate is not independently substantiated. Translation does not itself validate commitment status or remove the need for source-language checks on consequential claims.

If time prevents it, retain all projects in the coverage register, restrict substantive comparisons to the declared readable domain, and suppress or qualify negative/milestone conclusions for inadequately covered projects. Do not drop inconvenient projects after inspecting their labels. Translation costs some processing/review time; restriction costs breadth, balance and the interpretation of cross-project comparisons. Neither option repairs unknown source-search omissions.

### 25. Can November F extraction responsibly proceed after only NO/UK calibration?

Not as the proposed validated three-model commitment dataset. NO/UK are exposed, repeatedly reviewed and poor sole tests of live systems, translated evidence, companion-backed law and other institutional structures. The old contract itself calls for contrasting development cases and independent project reference (lines 161–176).

Minimum before F production: adopt v12 and resolve open features/language policy; remove obsolete embedded rules; implement two-axis atomic findings, authority/endorsement links, qualifier completeness, conflicts/supersession and deterministic admissibility; update comparison and output validation; demonstrate full-source coverage under the selected mode; calibrate at least three contrasting additional cases and a 40–60-case rule battery; and lock a feasible independent source-based project reference before exposure.

The proposed majority must combine valid supported claims, not simply vote on unsupported yes/no cells. Retain all supporting/counter-evidence and adjudicate critical conflicts. If that cannot fit November, reduce to F1/F2/F3/F4/F7/F8 or postpone the commitment layer. Running exploratory extractions is possible, but they must remain development and must not be presented as frozen production merely to meet 30 November.

## 4. Detailed evidence tables

### Table A. Independent recount and corrections

| Claim | Recount | Evidence and qualification |
|---|---|---|
| Frame 44 = 43 national + EU | Reproduces | `data/frame/projects.csv`, `analytic_frame`; 48 total rows, 44 true. |
| 777 files, 772 document rows | Reproduces as records | Master manifest row count; tier CSV row count. Source files were not supplied for rehashing. |
| 234 evidence rows, all author-decided | 120 `MB v11`, 98 `author (confirmed)`, 16 `author` | Tier CSV, in-frame KEEP/BORDERLINE, `decision_source`. This establishes recorded provenance, not independent source review. |
| 230 publications | Reproduces the registered linkage count | Tier CSV `same_publication_as` removes four linked editions. Israel's additional same-text pair remains unlinked. After correcting it, 229 publications and 207 readable texts are expected if nothing else changes. |
| Tiers 8/8/28 | Recomputed from unique registered evidence publications | T1 EU/IL/JM/JP/KZ/SE/TW/UK; T2 AU/BS/CA/HK/IN/NO/NZ/RU. Israel remains T1 at eight after deduplication. |
| 283 companions, 64 reviewed | Reproduces | Companion CSV `decision_source`: author 64; model pre-screen 141; title-level triage 78. |
| All companions same-year linked | Does not reproduce | `link_basis`: same year 194; nearest year 87; no dated evidence 2. All URL cells are empty in this file; URLs may be recoverable by joins elsewhere. |
| 208 documents, 42 projects, A/B/D 163/15/30 | Reproduces | Unit manifest and corpus documents CSV; 8,688 recorded pages. CL/CZ unreadable; IS/MG/MO/UY one document each. |
| 22 without English text | Reproduces after excluding four already-read edition counterparts | Not-unitised CSV has 26 rows: four linked editions, 14 untranslated, five no file, three scanned. |
| Three translation runs, 199 calls, 43 documents | Reproduces with distinct denominators | CALLS counts 174+14+11; 43 unique non-BENCH document keys; three-run manifests contain two retranslations and five BENCH documents. Only 30 translated documents remain in current measurement. |
| Translation token totals | 1,094,761 input; 638,945 output | Sum `input_tokens,output_tokens` of the three CALLS CSVs; these are recorded usage, not invoices. |
| 174,052 units | Reproduces | Unit and candidate manifest sums. The two Israel copies contribute 4,374 units; one redundant copy contributes 2,187. Deduplicated total would be 171,865, before other changes. |
| 20,059 candidates | 8,088 D + 6,231 N + 5,740 R | Candidate CSV. Non-X denominator 130,425; residual R + unsent 116,106; unsent 110,366; X 43,627. |
| Deduplicate Israel candidate effect | Remove either 489 or 498 candidates depending on retained identity | `IL_IL_BoI_2024`: 239 D,185 N,65 R; `IL_CAND-111`:239 D,185 N,74 R. IDs affect the hash sample; choose canonical routing before recomputing. |
| C0 120 | 90 D/15 N/15 R; routes 84 A/11 B/25 D; 38 projects,82 documents | Development sample CSV. Fourteen units are outside the current unit-manifest document set, rather than the earlier nine reported at an intermediate state in ADR-005. |
| MB labels | R58/N36/U24/blank-or-invalid2 | DEV_LABELS CSV and workbook K column. `K71=T`; J42 is also blank. No DS labels supplied. |
| No model unit labels | No such run/output found in supplied records | This is evidence of absence from the package, not proof no outside run exists. Twelve single/page example pairs are supplied, each marked unsent. |
| 86 translation pairs judged | 68 judgeable;18 D; S35/W4/X5/M24 | Benchmark JSON. Weighted stored shares S.586/W.051/X.059/M.305 reproduce its computation using rounded within-stratum shares. |
| Weighted to all 163 matched | Conditional/MAR interpretation required | `score_judgement.py:51–59` excludes D within each stratum. Keeping D as an outcome gives weighted S46.7%,W4.0%,X4.6%,M24.2%,D20.5%. These are English-rendering comparisons, not original-language accuracy. |
| Unmatched supplement | 0/30 completed | Benchmark JSON. The full unmatched population is 84; do not confuse it with the 30-row supplement. |
| 29 tests | 29 passed in 2.96 seconds | Python 3.12 runtime, pytest 8.4.2; separate working copy, no cache provider. |
| Generated checks | Both pass | `update_brief.py --check`; `run_statement.py --check`, six records. Passing does not establish semantic truth of generated wording. |
| $320–455 plus reserve | Addition reproduces; $416–591.50 after 30% | ADR-006 cost components. No calculation table/usage model supports the prediction or 2–4× comparison. |

### Table B. Readiness checklist, every row

“Verified” below means confirmed from the supplied files, not from unavailable accounts or source documents. C = calibration; P = production; F = commitment extraction.

| Row | Assessment | Correction to the gate |
|---:|---|---|
| 1 Evidence set | Recorded MB provenance reproduces; DS confirmation not present | Freeze author approvals, canonical IDs, scope and cutoff; do not equate all rows decided with complete source validity. |
| 2 Israel duplicate | Verified same text hash,2,187 units per copy | C/P: resolve and rebuild identities/counts/control sample. Do not describe 2,187 as the total across both copies. |
| 3 T3 language gap | Verified 14 documents/255 pages/7 projects; CL/CZ none | P; also C for any affected text used in calibration. Translate or adopt restricted population before freeze. |
| 4 Missing files/scans | Manifest supports 5/3 and listed projects | P for affected claims; record explicit missing/OCR outcomes. Recovering a file may change calibration distribution. |
| 5 PE retranslation | Pending in supplied records | C if PE text enters calibration, otherwise P for dependent output; do not tune on known defective text then quietly substitute it. |
| 6 Page spans | Rule unadopted; one translation-span example | C as well as P/F where it changes units/context; test excluded-page recall and version source coverage. |
| 7 Instrument v0.3 | Draft status confirmed; L1 actually v0.2 | C semantic-rule decisions needed, then final freeze. Distinguish component versions. |
| 8 Unusable units | 24 U reproduce, interpretation unresolved | C: clarify U and audit structure; cannot declare all 24 extraction failures. |
| 9 F contract/prompts | Correctly open, but broader than prompt-file edit | F: generator, schema, claims, validators, comparison, derivation and reference all must align. |
| 10 Combination/union | Proposed, no implementation | C round design and P freeze: ties,U,failures,coherence,adjudication and native-chain analysis. |
| 11 MB labels | 118 valid entries; one blank unit text, one invalid label | C: reconcile actual displayed inputs and blanks; preserve raw submissions. |
| 12 DS relevance | No returned artifact | C factor claims relying on two-author reference; no claim that an announced date means completion. |
| 13 DS ADR approval | No confirmation in supplied snapshot | P/Z under authors' governance; do not infer agreement from silence. |
| 14 Translation judgment | JSON supports 86 entries,18 unjudgeable,unmatched missing | C/P depending on affected input and claim. Correct conditional denominator; source-language evidence still absent. |
| 15 Issuer/voice | Unconfirmed; competing metadata disagree in117/208 rows | C for L2/header evaluation, not merely P. Pin one reviewed source. |
| 16 Three-provider runner | Not supplied as a functioning talk runner | C: offline failure/resume/parser/provenance/cost tests, then bounded capability probes. |
| 17 Request builder | Exists, explicitly draft | C: single/page context equivalence is not guaranteed; test escaping,bounds,IDs,order,header. |
| 18 C1–C3 draw | Existing drawer has only dev/main presets | C: new designs plus canonical context exclusions and exposure registry, not only new seeds. |
| 19 Verification/scorer | Not supplied as implemented | P reference: independently validated planted truths, blinded allocation, clean controls and separate raw outputs. |
| 20 Run record/CI | Documents exist; enforcement inadequate | C/P: actual artifact/hash/inventory validation. Synthetic fictitious run passes current check. |
| 21 Accounts/credit | Not verifiable from pack | C operational prerequisite; verify current account entitlements and limits, never assume a subscription funds API use. |
| 22 Exposure ledger | Historical entries exist; actual17Nov coding not logged there | C before new exposure; register full pages/contexts, not only target IDs. |
| 23 OSF/Zenodo | No completed registration/archive supplied | Before frozen confirmatory evaluation/production; development can precede it if honestly recorded. |

Additional gates absent as explicit checklist rows: output/schema validator; cutoff/date-precision ledger; source/text/ID immutability; workbook input-hash checks; benchmark failure policy; omitted-page/X/model-negative audit; probability weights and uncertainty; facet-specific support; consensus coherence; evidence for absence/earliest claims; F-reference feasibility; run drift and request retry policy; API-free replay; rights/access and maintenance policy. F03–F17 and question 13 specify the concrete actions.

### Table C. Disposition of all 18 previous-audit topics

| Prior item | Current disposition | Evidence/remaining action |
|---:|---|---|
| 1 Recount | Updated totals reproduce; wording defects remain | Table A; generated checks do not test interpretation. |
| 2 Tiers/editions/author overrides | Four links and author import implemented; duplicate audit incomplete | EDITION_LINKS; `build_tier_workbook.py:43–52,79–89`; Israel duplicate; round-trip fixtures still absent from suite. |
| 3 Translation chain | Logs now present; fail-closed claim not achieved | Missing metadata fixture passes; expected inventory optional; source bytes absent. |
| 4 Units/dictionary | Reading-order and dictionary changes real; structural validity unresolved | `unitise.py:51–80`; short hit survives; boilerplate sentence still excluded; IDs unversioned. |
| 5 Scorer/draw | Coefficient fixes tested; design/identity gaps remain | Alpha undefined and fixed AC1 reproduced; sample only excludes IDs; no hash verification, aspect2/flag scoring. |
| 6 Pilot statistics | Remain development diagnostics | No new raw corpus rerun verified; no justification to reuse old reliability as final-instrument validation. |
| 7 Tests | Increased24→29, all pass | Five new coefficient/end-to-end tests; no integrated new talk-runner, ingest, canonical-routing or workbook identity suite. |
| 8 Construct/funnel | Non-nested F funnel removed in schema | `schema...:184–200`; “highest rung” still conflates orthogonal attributes; ADR-004 historical prose is obsolete. |
| 9 Selection/denominators | Narrow selected-corpus interpretation adopted in principle | Source rule still content-selects; general-publication spans not frozen; no claim of institution-wide coverage. |
| 10 Facets/contract | Two status axes/stance and nonautomatic F map improved | English/Czech reported-decision exception, institutional authority, multiple propositions/bases and v12 extraction remain unresolved. |
| 11 Posture overlap | Retirement explicit in contract line104 | Legacy outputs/code retained as development; replacement replay not implemented. |
| 12 Translation validity | Human matched-pair results added | No source-language validation, unmatched completion or transportability evidence; restrictions inconsistent across documents. |
| 13 Human design/context | Shared single-unit renderer implemented; validation design weakened | ADR-006 supersedes full blind facets; packed pages alter view; U interpretation and blank J42 unresolved. |
| 14 Recall/silence | Not operationally closed | Random R exists, but X and model-negative source audit absent; project negatives/first dates not proven. |
| 15 Exposure/order | Dev/reference distinction preserved in prose | Full-page and duplicate exposure exclusion not implemented; newer exposure entries absent. |
| 16 Frame/date | Frame issue superseded by explicit author decision |44-project descriptive scope coherent; cutoff/source-version eligibility still not established. |
| 17 Registration/replay | Several specifications added, not frozen/implemented | F04–F07,F13,F15; missing actual deposit and validation gates. |
| 18 Feasible scope | No final scope cut adopted | Deadline remains inconsistent with unfinished independent validation/F implementation; use conditional scope reductions, not hidden waivers. |

### Table D. What to store for every run and in the deposit

Public means release where lawful; text-bearing requests/source outputs may require restricted access. No entry authorises publishing credentials or copyrighted source text without rights.

| Existing field or required addition | Per-run record/validation | Deposit treatment and assessment |
|---|---|---|
| `spec` | Versioned typed schema; explicit legacy run allowlist | Public; cannot be bypassed by omitting the field. |
| `stage` | Enumerated stage and pipeline version | Public; include adjudication/derivation stages separately. |
| `purpose` | Development/production/replicate/cross-provider plus parent-run relation | Public; never promote development accuracy to reference performance. |
| `provider,interface` | Endpoint, API version, region/service tier if relevant; API versus interactive product enum | Public nonsecret metadata; do not substring-ban “chat”. |
| `model_requested,model_returned` | Exact IDs per call and run summary | Public; attach documented alias mapping/version and its retrieval date. |
| `parameters` | Actual secret-free request parameters, defaults omitted, unsupported settings | Public; include reasoning, sampling, max output, structured response, tools/history/cache. |
| Prompt file/version/hash | Exact system/developer instructions and examples | Public when lawful; verify hash against archived bytes, not a mutable pathname. |
| `user_message_format,script_sha256` | Renderer source/version, header source, escaping/normalisation | Public code plus fixtures; include every transitive transformation dependency. |
| `packing` | Exact request-unit membership, order, context windows, split limits | Public metadata; record realised counts, not just the word “page”. |
| `inputs` | Canonical publication/edition, source/text/translation/unit/context/header hashes and row inventories | Public hashes/locators and legal source links; private exact source versions where required. |
| `git_commit` | Clean tree assertion and archived source/dependency lock; dirty patch if exceptional | Public reproducible source archive/DOI. Never infer old commits without evidence. |
| `started_utc,finished_utc` | Run, logical request and attempt timestamps | Public; permits drift/time comparisons. |
| `calls,complete,failed,retried` | Reconcile logical requests versus attempts, final chosen responses and failures | Public; retries append rather than overwrite. Define counts unambiguously. |
| `usage` | Provider input/output/cache/reasoning usage, including unavailable values | Public; distinguish included reasoning charges to avoid double counting. |
| `sdk,python` | SDK, interpreter, dependencies, OS; relevant extractor/OCR/tool versions | Public environment lock; deterministic preprocessing must be reproducible. |
| `operator` | Responsible person/role and approved account alias | Public or restricted as appropriate; no API key or unnecessary personal account identifier. |
| `deviations` | Typed incident plus narrative, affected inputs and corrective action | Public scientific deviations; redact secrets. |
| `request_key,unit_ids` | Immutable logical ID tied to complete request content | Public identity/membership; exact request body private if source-bearing. |
| `response_id,batch_id,custom_id` | All relevant IDs, submission/status/result inventories | Public where safe; retain batch files before provider expiry. |
| `stop_reason,complete,parsed_ok` | Provider completion, parser result and semantic gate separate | Public; refusal/truncation/schema failure must not become substantive absence. |
| Call time/seconds/token fields | Record per attempt and reconcile with usage summaries | Public; useful for operational audit, not substantive confidence. |
| `system_sha256,user_sha256,response_sha256` | Define exact-byte and normalised-text hashing separately; verify artifacts | Public; include canonical request-body hash independent of tokenizer. |
| Raw request body **addition** | Preserve actual secret-free JSON/body and role sequence, not only reconstructability | Restricted if necessary; public template plus hashes and reconstruction tests. |
| Response envelope/fingerprint **addition** | Raw provider response, returned IDs, fingerprint/headers if supplied | Public label-only outputs; restrict source-bearing portions. Unknown fingerprint explicitly missing. |
| Parser/schema/version **addition** | Exact parser, enum and cross-field rules, normalisation, rejected outputs | Public; preserve raw outputs alongside corrected/parsed versions. |
| Attempt/resume key **addition** | Include model, all parameters, full header/body, context/order, system/schema and parent outputs | Public key inputs/hashes; prevents stale reuse after metadata changes. |
| Samples/seeds/probabilities **addition** | Population hash, exclusions, random generator, seeds, inclusion probabilities and clustering | Public after unblinding; include selected IDs and realised coverage. |
| Human data **addition** | Original independent submissions, display hashes, timestamps, correction reasons, adjudications | Public labels/provenance where lawful; keep identity masking/permissions as appropriate. |
| Planted-error experiment **addition** | Natural output, displayed mutation, target truth, random key and reviewer outcomes | Release allocation after review; never overwrite original outputs. |
| Claims/derivation **addition** | Atomic claim IDs, complete premise/endorsement links, qualifiers, conflicts, supersession and eligibility | Public nonrestricted structured claims and reproducible final transformations; text access separately specified. |
| Prices/budget **addition** | Dated price table, currency, cache/batch assumptions, observed stage costs | Public cost ledger; distinguish estimate from invoice/usage. |
| Rights/access/licence **addition** | Source and output permissions, provider terms snapshot, redistribution/access decision | Public rights manifest and dataset/code licences; do not infer output rights from API-schema licence. |
| Drift/retirement **addition** | Model documentation snapshot, sentinel requests/results, version-change incidents | Public metadata/results; preserve raw bytes while available. |
| Release replay **addition** | Final outputs, dependency graph, scripts, checksums and expected tables | Public DOI deposit; clean-environment replay must run without API access for claimed reproducible numbers. |
| Maintenance **addition** | Version policy, corrections/contact process, retention/access steward | Public datasheet; avoid an unsupported promise of perpetual API availability. |

## 5. Must-not-claim list for the paper

1. “All seven facets were independently validated” when only relevance was blind-coded.
2. “Human verified” without stating who, which records, whether labels were pre-filled and what was actually checked.
3. “Planted-error detection bounds natural label accuracy” without a validated model linking the two error distributions.
4. “Three independent models” when only providers differ; shared training, prompts, inputs and translations create common error paths.
5. “Consensus is ground truth” or “inter-model agreement demonstrates validity”.
6. “31% of translations are wrong.” The benchmark compares two English renderings, excludes unmatched cases and conditions on judgeability within strata.
7. “The translations preserve commitment strength across languages” based on five documents in three languages or modal-token matching.
8. “44 projects were measured equally.” Forty-two currently have readable evidence, and coverage differs by language and source availability.
9. “No privacy statement/commitment exists” from a negative retrieval result, missing source or unsuccessful model call.
10. “First stated in year X” without the qualifier that X is the earliest located eligible statement in the searched corpus.
11. “Highest rung” as a validated latent progression from policy through law/design to operation. These properties may coexist and are not necessarily ordered.
12. “Whole-corpus recall” from model-coded random controls alone, or from a design that gives X units zero inclusion probability.
13. “The project protects privacy” when the evidence establishes only a published statement or provisional design.
14. “No state access” from F1 central-bank linkability or from a general anonymity label.
15. “An endorsed design” from a firm verb, published staff paper, generic effective law or majority vote without competent-authority evidence.
16. “A representative accuracy estimate” from the unweighted project-balanced development/challenge sample.
17. “No meaningful degradation under packing/low reasoning” because a difference is nonsignificant or inside a baseline interval.
18. “Exact reproducibility” of hosted generation; numerical output replay and fresh model reruns are separate claims.
19. “Fully open/replayable dataset” when essential analytical outputs are withheld or only hashes are provided.
20. “Available on request” as the entire Data Availability Statement for this journal.
21. “All pipeline checks pass, therefore inputs and outputs are valid.” The executed negative fixtures contradict that implication.
22. “Production completed by November” as evidence that an unadopted or changing instrument was frozen.

## 6. Verification performed, limitations and references

### Executed checks

- Independently summed the frame, tier/evidence, corpus, candidates, translation logs and human-label records. Recomputed tier categories after the registered edition links and checked same-text duplicate groups.
- Joined current unit and issuer ledgers, compared development membership with the current corpus, and checked development/diagnostic ID overlap (zero).
- Inspected the returned 120-row development workbook and its text/context hashes without producing replacement relevance/facet labels. Of 120 unit-text cells, J42 fails the registered hash because it is blank. Context I58 matches after removing the documented formula-escape apostrophe; it is not evidence of source corruption.
- Inspected the corpus workbook's three sheets: COVERAGE 45 rows, DOCUMENTS 209, NOT_READ 27, including headers. Its 26 NOT_READ records include four edition counterparts already read elsewhere, so “not read” is not a 26-publication missingness count.
- Checked diagnostic metadata: D80/N40/R40/unsent80/X60. Performed structural scans and inspected short retained fragments; did not create a new substantive label set or estimate a corpus structural-error rate from these oversampled strata.
- Enumerated the twelve single/page request pairs and inspected a paired example and the request builder; no calls were made. The pack does not contain 120 paired examples, despite the broader description in the prompt.
- Ran all 29 supplied tests in a separate working copy: **29 passed**. Both generated-document checks pass. Did not run production, source download, site deployment or account actions.
- Executed independent synthetic probes: undefined alpha/fixed AC1 behave as repaired; packed context can expand; a complete short boilerplate-matching sentence is excluded; v12-generated stage one retains legacy status instructions; the array parser accepts surrounding prose; a fictitious run passes record validation; translation ingest accepts missing run hash/per-call metadata.

### What could not be checked, and why

**Absent source bytes:** the original PDFs/HTML, full translations and full per-document unit files were intentionally excluded. I could not rehash originals, verify all reading-order/OCR extraction, regenerate the whole corpus, establish semantic translation fidelity, or validate actual source eligibility and coverage. Manifest equality does not substitute for these checks.

**No final model outputs or DS reference:** no accuracy, model agreement, true planted-error performance or production cost can be measured yet. No statement in this report fabricates such results.

**Incomplete historical artifacts:** raw benchmark judgment workbook, all translation request/response bodies, failed provider calls and live account settings are not supplied. The benchmark arithmetic was checked from the supplied result and scoring code, not independently rejudged. The third-run record has 11 successful calls; the documented failed PE credit attempt is not in those 11 rows, so “199 calls” should be understood as registered successful call records, not necessarily every attempted request.

**No live repository/CI verification:** `GIT_COMMIT.txt` identifies the audited snapshot; I did not pull or push a repository. The archive is the requested evidence, and modifying origin/main would defeat the independent snapshot audit. Local tests are not proof that the remote workflow is green.

**Provider identity and costs:** current official DeepSeek documentation was checked, but the exact account/model capabilities must still be tested. I did not verify the historical October v4-pro repointing, the claimed subscription/API-credit entitlement, or the full Anthropic/OpenAI price assumptions. These remain UNVERIFIED, not accepted budget facts.

**No legal clearance or journal guarantee:** source copyright and permissible access vary. The report identifies the need for a rights/access decision and the journal's stated policy; it does not determine redistribution rights for each source. Acceptance depends on the final claims, executed validation and editorial review.

### Verified methodological references and official policies

The bibliographic identities below were checked against publisher, author/institutional or official project sources on 17 November 2026. Recommendations applying them to this CBDC design are this audit's judgments. None is asserted to impose a universal numeric sample-size threshold.

**R1.** Feuerriegel, Stefan; Barrie, Christopher; Crockett, M. J.; Globig, Laura K.; McLoughlin, Killian L.; Mirea, Dan-Mircea; Spirling, Arthur; Yang, Diyi; et al. (2026). *A reporting checklist for large language models in behavioural science*. **Nature Human Behaviour 10**, 1182–1186. [Publisher/DOI](https://doi.org/10.1038/s41562-026-02492-7); [GUIDE-LLM checklist](https://llm-checklist.com/checklist/). The checklist explicitly covers model/configuration, prompts, human validation, processing and code disclosure.

**R2.** Gebru, Timnit; Morgenstern, Jamie; Vecchione, Briana; Vaughan, Jennifer Wortman; Wallach, Hanna; Daumé III, Hal; Crawford, Kate (2021). *Datasheets for Datasets*. **Communications of the ACM 64(12)**, 86–92. [DOI](https://doi.org/10.1145/3458723); [author institutional publication record](https://www.microsoft.com/en-us/research/project/datasheets-for-datasets/publications/). Use for dataset motivation, composition, collection, recommended use and maintenance documentation.

**R3.** Grimmer, Justin; Stewart, Brandon M. (2013). *Text as Data: The Promise and Pitfalls of Automatic Content Analysis Methods for Political Texts*. **Political Analysis 21(3)**, 267–297. [DOI](https://doi.org/10.1093/pan/mps028); [author's publication record](https://bstewart.scholar.princeton.edu/publications/text-data-promise-and-pitfalls-automatic-content-analysis-methods-political). Methodological rationale for task-specific validation of automated text analysis.

**R4.** Abdurahman, Suhaib; Atari, Mohammad; Karimi-Malekabadi, Farzan; Xue, Mona J.; Trager, Jackson; Park, Peter S.; Golazizian, Preni; Omrani, Ali; Dehghani, Morteza (2024). *Perils and opportunities in using large language models in psychological research*. **PNAS Nexus 3(7)**, pgae245. [DOI](https://doi.org/10.1093/pnasnexus/pgae245); [full article](https://pmc.ncbi.nlm.nih.gov/articles/PMC11249969/). Relevant caution about opaque models, bias and task-specific evidence; not a CBDC annotation standard.

**R5.** Gallifant, Jack; Afshar, Majid; Ameen, Saleem; et al. (2025). *The TRIPOD-LLM reporting guideline for studies using large language models*. **Nature Medicine 31**, 60–69. [DOI](https://doi.org/10.1038/s41591-024-03425-5); [official guideline article](https://www.tripod-statement.org/wp-content/uploads/2025/01/TRIPOD-LLM-Article.pdf). Adapt relevant annotation/model-reporting elements; do not claim clinical checklist compliance establishes social-science validity.

**R6.** Cambridge University Press, **Data & Policy**, current [Research transparency policy](https://www.cambridge.org/core/journals/data-and-policy/information/journal-policies/research-transparency) and [Preparing your materials](https://www.cambridge.org/core/journals/data-and-policy/information/author-instructions/preparing-your-materials). A data-availability statement is required; restrictions must be explained, a bare on-request statement is unacceptable, and persistent archives are expected where possible. These are journal policies, not research articles.

**R7.** DeepSeek, [Models & Pricing](https://api-docs.deepseek.com/quick_start/pricing/), accessed 17 November 2026. Official current alias/version, context/output and price information. The page supports a Flash alias-redirection statement; it does not establish the brief's particular v4-pro October allegation.

**R8.** DeepSeek, [Responses API](https://api-docs.deepseek.com/api/create-response/), accessed 17 November 2026. The documented endpoint is stateless at the conversation level and has model-specific role semantics. Stateless conversation behaviour alone does not establish a general data-retention guarantee.

**R9.** DeepSeek, [Open Platform Terms of Service](https://cdn.deepseek.com/policies/en-US/deepseek-open-platform-terms-of-service.html), released 22 April 2026/effective 29 April 2026, accessed 17 November 2026. The API-specific terms describe input responsibility and conditional input/output rights. Archive the terms that actually govern the authors' account and obtain any necessary institutional rights review.

### Practical release decision

The immediate task is not a full-corpus model run. It is a bounded repair-and-calibration cycle with an independently protected reference. If author time is fixed, retain fewer claims: independently assessed relevance/voice/aspect, explicit coverage and located statements first; postpone unsupported facets or the full commitment layer. The deadline should determine scope, not the strength of the evidence claimed.
