# Independent audit of the CBDC measurement pipeline

13 November 2026 · Pack commit `4d4f1423163fd3cede0512cf15905720b0e97a3d`

**Decision: do not start the main human coding round with the current workbooks.** Repair the frame and edition routing, align the instruments, freeze the coding context, and correct the agreement scorer first. Source review and training preparation can proceed. The existing pilot supports caution about project rankings; it does not validate the proposed funnel.

Paths below are relative to `repo/`, except `extra/`. CSV row references include the header as row 1. I audited the supplied snapshot, rebuilt the all-document and tier workbooks in a separate working copy, ran the tests, checked the two translation examples, and inspected all 300 diagnostic texts. I did not label the agreement sample or reconstruct sealed project results. Source PDFs, complete translations, and the complete unit-text population are absent: manifest reconciliation is distinguished from source verification throughout.

## 1. Recount of S2, S3, S4, S5, S8, S10 and S11

**Verdict: sound with correction.** Most reported arithmetic reproduces; its interpretation as a 43-national-project corpus does not.

| Step | Independent recount | Correction or limitation |
|---|---|---|
| S2 | Master: 777 files = 394 registry + 369 candidate + 14 English editions. Registry hash status: 392 identical, 2 different. Manual-download ledger: 382 rows, 369 obtained, 13 not retrieved. | The manual ledger includes 378 candidates and four attachments; rows are not all independent documents. These are recorded hash statuses, not independent rehashes of the absent source files. |
| S3 | 772 rows: KEEP 250, BORDERLINE 35, RECHECK 88, COMPANION 222, DROP 152, WHOLESALE 25. Decision sources: model pre-screen 366, MB v11 128, title triage 266, author 12. | 285 evidence rows overall; 278 in the tiered national-plus-EU set; **263 in the national frame**. Tiers 11/12/21 include EU; national tiers are **10/12/21**. The 17 potential upward moves reproduce. |
| S4 | 777 language records, 495 English. Route-B search: 72 = 19 full + 7 partial + 2 unofficial + 44 none. | English-edition ledger contains 15 entries, 14 held and one unavailable. “14 fetched” is correct. |
| S5 | Queue: 63 = 44 translate + 14 route B + 5 benchmark. First translation manifest: 43 documents, 174 chunks; second: 4 documents, 14 chunks. | These reproduce **registered chunks**, not independently verified API-call totals: the advertised `runs/*/CALLS.csv` files are absent. The first manifest includes five benchmark translations. |
| S8 | 250 unitised documents, 185,295 units; D 7,037, N 5,792, R 6,123, X 48,233, not sent 118,110. D+N+R = 18,952. Non-X denominator = 137,062. Another 28 tiered documents lack usable English text. | The 250 include **15 EU documents**: national unitised documents = 235, covering 41 national projects; CL and CZ have no unitised document. The candidate sample is Bernoulli hashing, not an exact-size 5% draw. |
| S10 | 278 issuer rows: central bank 253, government 17, legislature 8; institutional voice 197, other voice classes 81. | **122 proposed rows and 156 remaining rows**, not 121/157. Moreover, 118 of 250 unit-manifest `issuer_type` values differ from the newer issuer ledger. |
| S11 | Main 400: D/N/R 260/80/60; A/B/D 292/30/78; T1/T2/T3 201/140/59; 42 projects, 151 documents. Training 30 from NO/UK: D/N/R 20/5/5. | Counts reproduce, including 20 EU main-sample units. Both coder orders are permutations of 1–400. No training/main ID overlap; no diagnostic/agreement ID overlap. These checks use IDs and metadata, not agreement labels. |

Evidence: `data/manifest/MASTER_MANIFEST_2026-11-10.csv` (`source`, `hash_check`); `MANUAL_DOWNLOADS_2026-11-10.csv` (`status`); `TIERS_2026-11-10.csv` (`project`, `decision_v12`, `decision_source`, `tier`); `MASTER_LANGUAGE_2026-11-10.csv` (`lang_class`); `data/translation/ROUTE_B_PAIRS.csv`, `ENGLISH_EDITIONS_2026-11-10.csv`, `TRANSLATION_QUEUE_2026-11-10.csv`, `TRANSLATION_MANIFEST_*.csv`; `data/units/CANDIDATES_2026-11-13.csv` (all count columns), `UNITS_MANIFEST_2026-11-13.csv`, `AGREEMENT_SAMPLE_2026-11-13.csv` (`set`, `stratum`, `route`, `tier`, `project`, coder orders); `data/manifest/ISSUERS_PROPOSED_2026-11-13.csv`, `ISSUERS_2026-11-13.csv` (`issuer_type`, `voice_class`).

**Fix:** publish separate file/document/edition/project denominators, rebuild all downstream artifacts from one explicitly national manifest, and replace the stale brief counts.

## 2. Tiers, author overrides and duplicate documents

**Verdict: sound with correction.** The implemented arithmetic and twelve author overrides reproduce. The observational units are not consistently deduplicated.

Independent evidence counts, before deduplication:

| Tier | Projects and evidence counts |
|---|---|
| T1 | AU 8; **EU 15**; IL 10; JP 12; KZ 10; NO 13; NZ 9; RU 13; SE 11; TW 9; UK 22 |
| T2 | BS 6; CA 7; CN 7; HK 7; IN 6; JM 7; MO 6; MU 7; NG 6; PE 7; TH 6; TR 6 |
| T3 | AE 4; AW 2; BT 3; CH 4; CL 2; CZ 3; GH 4; HU 4; ID 4; IS 4; KE 2; MG 2; NA 3; NP 4; PW 3; RW 3; SG 3; SZ 4; UA 3; UY 3; ZA 4 |

All 29 other codes are marked outside the tiered set. Potential upward moves are AE, BS, CA, CH, CL, CN, CZ, ID, IN, JM, MG, NA, NP, RW, SZ, TH, UA. Rebuilding `build_all_documents_workbook.py` followed by `build_tier_workbook.py` produced a tier CSV identical in every row and field to the supplied CSV. In the latter script, lines 43–48 apply sorted author-decision files; lines 55–59 prefer linked downloads over landing pages and retain newly attached English editions within their original row. This part works.

However, older registry English editions remain independent evidence rows. The following original/English pairs are both counted: `JP_BoJ_Pilot_JP` / `JP_BoJ_Pilot_EN`; `NO_Norway_nbmemo-1-2018` / `NO_NBPapers_1_2018_en`; `NO_Norway_nb_memo_2_19_dsp` / `NO_NBPapers_2_2019_en`; `NO_Norway_norges-bank-memo-1-2021` / `NO_NBPapers_1_2021_en`. Their source-language texts also enter route D through **benchmark translations**, despite available issuer English. Their unit-manifest text hashes match those benchmark translation hashes. The English versions separately enter route A. There is no same-SHA duplicate among the evidence files; that does not detect translation-equivalent documents.

Removing those four duplicate originals alone changes JP 12→11, NO 13→10, unitised documents 250→246, and route D 46→42; it does not change their tiers. These are isolated corrections, before excluding EU or resolving other evidence decisions.

**Fix:** add a canonical publication ID and edition relationships, count publications once, make BENCH records ineligible for production, and route every canonical publication through the preferred English edition regardless of acquisition batch. Explicitly pin author-decision inputs; add an importer and validation for the completed review workbook so edits in “decision (authors)” cannot remain merely decorative.

## 3. Translation hash chain and ingest

**Verdict: not verifiable from the pack** for the claimed complete chain; the two supplied byte-level examples pass the available comparisons.

The system prompt hash is `5c054f82c7d9991d2b505de0ee2a54adc40aee03657537073013ba062b670716` in the repository, example prompt, response metadata and manifests.

| Example | Request SHA-256 | Response SHA-256 |
|---|---|---|
| `CN_CAND-063.chunk-01-of-01` | `c6f559e9230144f6690e6b476854ded442f2f946c68a1b0191844c0a92143b54` | `930b413702668e7a9ee6c57e184525ede46925e5840db5b079f658c7f2dc8f89` |
| `EU_SI_SI_Banka-Slovenije_Zapisnik-1-seje-NSD-digitalni-evro_2024.chunk-01-of-01` | `f8c3c50cad7e8353d55bac8ce872d13ddc0f5079ba3c2d3f63e9f9e190773737` | `6ed9ed05de129a94e33100ac9d47a3fe98b5152bb1398214af68c3163cd69040` |

Requests match `TRANSLATION_REQUESTS_2026-11-10.csv`; responses match example metadata and translation-manifest response hashes. Headers repeat the registered source hash, page markers preserve CN page 1 and Slovenian pages 1–3, and both end with END. The original source bytes are absent, so repeating a source hash does not independently verify that source. No `CALLS.csv` is supplied anywhere. The pack's git-archive approach and ignored `runs/` directories explain the omission; the omission still prevents the requested check.

The raw response is not rewritten by ingest. The assembled translation **is** transformed: text-mode newline handling, stripped lines, removed transport headers/terminators and pagewise reassembly. This is acceptable only as a separately hashed derivative. `scripts/translation/ingest_translations.py:27–35,41–75` has weaker checks than the claimed chain: prompt mismatch warns; language detection is optional; response bytes are not checked against the response-metadata hash; absent completion metadata defaults permissively; entirely missing documents can escape the processing loop; page order is checked but within-page omissions/reordering are not. Length thresholds are too coarse to establish completeness. Partly untranslated text can pass through short pages, the sampled first 4,000 characters or tolerated non-English pages. A truncated body with intact markers and END can pass.

Both examples preserve the expected transport structure and contain no evident extra explanatory preamble. They do **not** demonstrate perfect instruction compliance: the Slovenian output uses “offline” without the required first-occurrence bracketed source term. Hashes and marker checks do not establish semantic faithfulness, especially modality. A qualified bilingual review is still required to verify “nothing added or lost.”

**Fix:** archive CALLS plus immutable run metadata; fail closed on hash/prompt/completion mismatch and missing expected chunks/documents; separate raw-byte and assembled-text hashes; pin source extraction mode. In `translate_api.py:32–38`, prevent overwriting run metadata while silently reusing old response files. Add per-page completeness diagnostics and human semantic checks rather than treating character ratios as validation.

## 4. Unitisation, dictionary and random controls

**Verdict: unsound** as an already validated sentence denominator; the random-control mechanism itself is serviceable.

I classified only structural usability in the permitted diagnostic sample. “Unusable as one standalone sentence” means an obvious heading/list/table fragment, truncated clause, merged sentences, navigation or interleaved columns. Minor numbering artifacts were tolerated. This is one auditor's descriptive inspection, not a blinded reliability result or a set of substantive privacy labels.

| Diagnostic stratum | Inspected | Structurally unusable | Share |
|---|---:|---:|---:|
| D | 80 | 23 | 28.8% |
| N | 40 | 8 | 20.0% |
| R | 40 | 14 | 35.0% |
| Not sent | 80 | 28 | 35.0% |
| X | 60 | 60 | 100.0% |
| Non-X sample | 240 | 73 | 30.4% |

The total 133/300 = 44.3% is **not a corpus estimate**, because the diagnostic strata were sampled disproportionately. Unusable does not necessarily mean uncodable with source context; it means the advertised single-sentence unit is not what is supplied. Reproducible flagged CSV rows in `extra/UNITS_DIAGNOSTIC_SAMPLE_300.csv`:

- D: 4, 6, 8, 9, 13, 15, 18, 27, 29, 30, 31, 39, 42, 45, 46, 51, 60, 63, 68, 70, 72, 75, 77.
- N: 85, 89, 90, 103, 104, 111, 112, 113.
- R: 127, 128, 132, 133, 135, 140, 143, 147, 148, 151, 152, 155, 156, 158.
- Not sent: 165, 167, 168, 170, 174, 176, 179, 183, 185, 187, 192, 193, 195, 196, 198, 201, 209, 212, 215, 221, 225, 226, 227, 228, 229, 235, 238, 239.
- X: 242–301.

Examples include interleaving at row 45, contents material at row 77 and navigation at row 229. No demonstrated substantive false exclusion can be established from the sampled X fragments without their context. Nevertheless, the **rule** demonstrably excludes valid statements: “No identification required.” has fewer than four words; “Our privacy policy forbids sharing customer data.” matches the short boilerplate filter. Both deserve substantive assessment.

`select_candidates.py:20,23,31–37` catches “We identified three options” and wholesale confidentiality, but misses standalone AML/CFT monitoring, retention, encryption, zero-knowledge proofs and “The bank cannot see payments.” Neighbours and R can recover some misses; they cannot recover X, which has zero inclusion probability. “Privacyenhancing” in diagnostic row 209 illustrates extraction-dependent matching problems.

The hash threshold is deterministic pseudorandom Bernoulli sampling with approximately 5% inclusion, conditional on eligibility and fixed IDs. It is content-independent in that conditional sense, not an exact hash-ranked sample of prescribed size. IDs contain document/page/sequence, not the source hash (`unitise.py` unit-ID construction); re-extraction can change text under the same ID and redraw the population. The candidate default seed remains dated 12 November, even when output is dated 13 November; not a statistical error, but it must be recorded.

**Fix:** freeze source extraction and version IDs; retain paragraph/source locators; audit X separately; repair boilerplate and table handling; distinguish unusable/processing-failed units from irrelevant substantive prose. Recompute denominators after repairs. Check subprocess extraction failures rather than accepting empty outputs (`unitise.py:55–57`).

## 5. Agreement draw and scorer

**Verdict: unsound** as a production scorer; the supplied draw matches its declared quotas.

`draw_agreement_sample.py:25–27,39–79` implements deterministic hash ordering, route/stratum quotas, tier splits for A, project round robin and the document/stratum cap. It does not use unit-level model labels. Upstream document admission and issuer metadata are nevertheless model-assisted. It does not stratify by genre, despite broader design aspirations. Full regeneration requires the absent unit files; metadata checks reproduce the counts, exclusions and coder permutations.

Synthetic two-coder example: pairs `(R,R), (R,R), (N,N), (R,N)` give raw agreement 0.75 and nominal alpha **0.533333**, correctly computed by `score_agreement.py:17–24`. Two defects matter:

| Probe | Current output | Required interpretation |
|---|---:|---|
| Every rating is R | alpha 1.0 | Alpha is undefined: expected disagreement is zero. Report raw agreement 1 and the degenerate marginal distribution. |
| Four-pair example, AC1 | 0.529412 | Correct for a declared two-category scale; **0.673469** for the actual fixed R/N/U scale. Categories must be prespecified, not inferred from observed ratings. |
| Every rating is R, AC1 | null | With the declared nontrivial category scale, AC1 is 1. |

`score_agreement.py:35–40` correctly resamples paired ratings, but its iid-unit bootstrap ignores the quota and document/project sampling structure; degenerate resamples are incorrectly assigned alpha 1. These intervals are not design-aware population intervals. `:43–55` silently overwrites duplicate IDs, intersects incomplete sheets and filters blanks. It does not validate unit hashes or allowed values. Optional `aspect2` and flags are not scored.

**Fix:** define the scale and estimand; validate complete unique IDs, text hashes and allowed labels; report missingness explicitly; return undefined alpha in degenerate cases, including bootstrap replicates. Use a declared stratified/cluster-aware sensitivity analysis for generalisation, or label the interval as conditional on this challenge sample. Assert quota fulfilment and pin the unit manifest instead of automatically choosing the latest filename. Keep an untouched model-evaluation set if the human sample will tune prompts.

## 6. Pilot statistics and interpretation

**Verdict: sound with correction** as an exploratory warning, not a validated project-level reliability estimate.

`data/census/TALK_PILOT_aggregate.json` reproduces the proposal's corrected section 9: 125,178 sentences, 3,251 narrow hits (2.597%), 39 zero-hit documents; document-kind R² 0.185; ICC 0.156 unadjusted, 0.132 with kind, 0.131 with kind/length, 0.133 with kind/length/year. Share split-half median is 0.46, 5th–95th split quantiles 0.08–0.71; count median 0.78. Among 11 projects with at least eight documents, share median is 0.74, quantiles 0.45–0.89. Project count/document-count correlation is 0.675; **share/document-count correlation is 0.28**, so “shares do not” is too categorical. The older section 2 figures are superseded. The JSON `as_of` still says 12 November despite the corrected run.

A complete statistical rerun is **not verifiable from the pack**: source texts and per-document analytic inputs are omitted. The pilot uses a different sentence-length filter from candidate selection; 125,178 is not the production denominator 137,062.

The unweighted arcsine-square-root Gaussian mixed model does not remove unequal sampling variance from very different document lengths; zero mass and heterogeneous genres remain. Adding length as a predictor does not solve unequal residual precision. `talk_pilot.py` also suppresses fitting warnings without exporting convergence diagnostics. The Spearman–Brown correction is applied to **Spearman rank** correlations of unequal document halves; interpret it as a heuristic rank-stability diagnostic, not classical parallel-test reliability. Its split quantiles are not confidence intervals. Genre adjustment changes the estimand and may remove real communication choices.

**Fix:** retain this as a documented development diagnostic; rerun on the repaired corpus with explicit denominators and convergence outputs. If an inferential model is retained, compare binomial/beta-binomial count models and document/genre sensitivity. Avoid presenting an ICC of transformed dictionary shares as validation of semantic institutional positions.

## 7. Tests

**Verdict: sound with correction.** Executed in a separate Windows working copy with Python 3.12.8:

`python -m pytest audit_repo/tests -q -p no:cacheprovider` → **24 passed in 1.42 seconds**.

The six files test earlier comparison, derivation, extraction validation, posture, prompt export and quotation verification. **None of S1–S11 has direct end-to-end or dedicated regression coverage** for the new workflow: search/pre-screen, download/master reconciliation, tiers/overrides, language/edition routing, translation ingestion, benchmark matching, pilot, units/candidates, reading-order correction, issuers, agreement draw/scorer. Existing posture/derivation tests cover related older logic, not this instrument's integration.

First three additions:

1. A tiny full corpus fixture with a national project, EU, original/English pair, BENCH translation, landing page/attachment and author override; assert one canonical document, correct frame, correct preferred text, and review-workbook round trip.
2. Translation ingestion fixtures with missing entire documents, missing/reordered chunks, changed bytes, stale prompt metadata and incomplete text; assert rejection and immutable raw hashes.
3. Agreement fixtures checking the hand-calculated example above, constant marginals, fixed categories, missing/duplicate IDs and hash mismatch; then a deterministic quota/context fixture.

These test failure modes found here, not merely implementation details.

## 8. Construct, project comparisons and the funnel

**Verdict: unsound** as a project trait ranking or the proposed conversion funnel; defensible as bounded corpus description after revision.

At ICC 0.15, the parallel-document heuristic `kρ/[1+(k−1)ρ]` gives reliability 0.414 for four documents, 0.585 for eight, 0.679 for twelve and 0.802 for twenty-three. These are illustrative assumptions, not estimated reliabilities for each project. Four heterogeneous documents do not support a stable ranking of an institution's underlying privacy emphasis. They can support an explicitly conditional description of the collected corpus, with coverage and measurement uncertainty. Low ICC does not make exact description of that finite corpus mathematically invalid.

The proposed funnel in `schema/talk_units_v13_DRAFT.json`, `derived.funnel`, is not nested: relevant non-dictionary units occur in N and R; endorsed policy claims need not name a legal/architectural/cryptographic mechanism; sentences map many-to-many to F-cells. “Admissible F-commitments” cannot be the last attrition stage of a sentence funnel.

**Fix:** define U = eligible substantive units in the fixed document universe, L = estimated relevant units, O = relevant own-position units, M = own-position units with a specified legal/design basis, and E = M units satisfying the chosen commitment rule. Report L/U, O/L, M/O and E/M, with weighted counts and undefined zero denominators. Also report all endorsed own statements independently of M; do not hide policy commitments through an intermediate filter. Dictionary hits are a retrieval diagnostic, not a substantive funnel stage. Report F-cell coverage in a separate table with its own project-by-feature denominator and explicit unknown/conflict/inapplicable states. A broad aspect label cannot establish an F-cell.

## 9. Selection and denominators

**Verdict: unsound** for estimating general institutional privacy salience from the current evidence-selected corpus.

`docs/SOURCE_RULE_D1.md`, condition 3, selects documents for bearing on privacy cells. Measuring privacy share within that selected set is outcome-related selection. It is not circular as a conditional statement—“among documents admitted for this purpose”—but cannot establish how much the institution discusses privacy across its retail-CBDC communications. T1/T2 thresholds additionally condition on publication, collection and language coverage. Counts are predictably volume-sensitive; the direction of bias in **shares** is not identified. Adding technical privacy reports can raise them; adding long general reports can lower them.

There is a second denominator problem beyond genre: whole annual reports and proceedings bring unrelated prose into the denominator. The pilot JSON `by_kind.annual_report` contains 15,765 sentences across eight documents, versus 3,105 in six `annual_report_chapter` records. These are different content boundaries, not merely different styles. Without the complete sources, the exact unrelated share is not verifiable.

**Fix:** maintain two universes: an authority/content-selected evidential set for commitments, and a uniformly searched official retail-CBDC communication set for talk, admitted independently of privacy content. Prespecify CBDC section boundaries for general publications without using privacy terms to choose them. If the broader universe is infeasible, rename the result “privacy-statement composition in the selected evidence corpus,” drop institution-wide silence claims, and show source/genre/route coverage. Do not silently pool central-bank, government and legislative voices.

## 10. Facets versus the measurement contract

**Verdict: unsound.** The incompatibilities below prevent deriving contractual commitments from the draft facet labels.

Evidence: contract `docs/MEASUREMENT_CONTRACT_v12_DRAFT.md:35–53,57–82,90–100,106–131`; L2 prompt `pipeline/prompts/talk_L2_facets.system.md:4–30`; schema keys `L2_facets`, `crosswalk_from_survey_types_2026-11-02`, `derived`, `aspect_to_F_cells`; Czech codebook rows identified by facet/value.

| Inconsistency | Required change |
|---|---|
| Single status ladder cannot represent endorsed-and-tested, unclear-but-operational, or superseded claims. | Change talk schema/prompt/codebook to separate decision and implementation axes, or explicitly prohibit deriving commitments from talk status. Preserve supersession and uncertainty. |
| Czech ENDORSED is an institution's decision/requirement; English requires the competent body. Both omit a clear common rule for commitments conditional only on issuance. | Apply contract rule A consistently; record competence and endorsement source. A firm verb is insufficient. |
| Czech OPERATIONAL includes effective regulations; English means a live system. | Keep legal effectiveness in `legal_state`; do not infer operational CBDC implementation. |
| REJECTED includes “will not be done,” which can be an endorsed negative design choice. | Distinguish rejection of a proposition/design from a negative asserted value. “No anonymity” may be an endorsed position. |
| REPORTED always gets NOT_APPLICABLE, although an official report may explicitly document another competent body's endorsement. | Separate reported voice from evidence of an authority's decision; preserve source and competence for subsequent claims. |
| OWN is the publisher's voice, including staff-authored views; issuer type alone does not establish institutional authority. | Add verified document-layer/author-role handling; staff research cannot establish commitments. English L2's staff trap helps but does not replace this metadata rule. |
| Talk basis adds NONE and LEGAL to policy/architectural/cryptographic; a single “strongest” basis can replace rather than complement a legal rule. | Keep declaratory evidence and legal state separate; allow justified multiple bases, attached to the exact proposition. Amend the contract only if broad descriptive talk fields are explicitly separate. |
| “Strongest basis in the paragraph” can transfer an unrelated cryptographic mechanism onto a policy promise. | Require entailment for the coded clause. Retain the contract's “will not use” trap; paragraph proximity is not support. |
| CB_ACCESS merges central bank and any core operator, identity, balances and transactions. | Preserve actor attribution and data object; independent operators and balance reporting cannot set F1. |
| Ordinary/exceptional access, payer/payee, online/offline, release horizon, synchronisation and design version are missing. | Add these in linked atomic claims before any F derivation; do not pretend sentence facets contain them. |
| ANONYMITY maps to F1 and F4 jointly. | Delete automatic mapping. General anonymity, central-bank online linkability and offline privacy are distinct. |
| IDENTIFICATION ambiguously points to F7/F8; KYC may be mistaken for transaction linkage or absence of all low-ID routes. | Preserve F8's descriptive role; enforce explicit all-route evidence for F7=no and separate premises for F2. |
| GRANT conflates giving an actor data access with requiring user identification; anonymity rejection says no particular actor has routine linkage. | Define direction relative to a specified access/identity proposition, or rename it as a broad privacy stance and prohibit cell inference. |
| PET_TECHNIQUE crosswalk automatically sets CRYPTOGRAPHIC. | Merely naming or considering a PET does not establish a property backed by cryptography. Require mechanism and status evidence. |
| F9 has no explicit aspect crosswalk; PROGRAMMABILITY is categorically called irrelevant. | Keep exceptional reidentification in atomic claims; allow privacy-relevant programming statements through L1 while excluding unrelated functionality. Resolve whether F9/F10 remain in scope. |
| GENERAL collapses principles and concerns; DATA_PROTECTION collapses minimisation and legal commitments; OTHER is presumed mostly reported/irrelevant. | Treat the 17→10 mapping as lossy, not invertible; retain required claim subtype tags if G indicators survive. |
| `two_statements` keeps only the main clause; `aspect2` has no independent direction/basis/status. | Split propositions for commitment work. A flagged sentence cannot faithfully encode two opposing access claims. |
| Human form lacks model `modal_term`; optional flags are a single dropdown while model flags are an array. Schema is a configuration document, not a validating JSON Schema. | Align input/output contracts and implement a strict parser, allowed-value validation, multiplicity and completeness checks. |

The contractual authority, symmetry and qualifier rules should remain authoritative for commitments. Broad talk categories may remain simpler only if they are explicitly descriptive and never substituted for contractual claims.

## 11. Overlapping posture layers

**Verdict: sound with correction.** Use one descriptive talk representation, with a separate contractual claim layer.

The old P ladder is particularly unsuitable as a silence measure: contract lines 108–112 assign P0 even when lawful access or privacy risks are discussed. G2/G3 also concern broader personal-data statements than F1. Replacing P/G with the sentence instrument is not a cosmetic rename: statement counts, locators, subtype information and the basis/status semantics change. A 17-to-10 crosswalk cannot recover every old G indicator.

**Fix:** amend contract §6b, ADR-004, the proposal, prompts, exports, site and `scripts/derive.py` together. Prefer sentence-level descriptive talk plus linked atomic F claims; drop P0–P3 from the main paper. Retain selected G-style presence indicators only if each is explicitly derivable and source-located under the new schema. Archive the earlier outputs and tests as development artifacts; add tests for the replacement rather than relabelling the old outputs. No talk-derived label should bypass rule C.

## 12. Translation as measurement

**Verdict: unsound** as validation of route-D status/modality; insufficient evidence for general route-D relevance, aspect or direction accuracy.

The benchmark workbook `extra/TRANSLATION_BENCHMARK_2026-11-11.xlsx`, `PRIVACY_SENTENCES`, contains 247 source-side privacy sentences: 163 matched, **84 unmatched**. The judgement key has 56 flagged and 30 control pairs. Similarity, term ranks and number preservation are diagnostics; they are not error rates for the intended labels. Five documents in three languages cannot establish transportability across the translation queue. Automatically matched pairs condition on successful matching and omit the failures most likely to matter. English issuer editions are useful comparators, but may themselves abridge or rewrite the original; neither difference automatically proves translation error.

| Facet | What the present evidence supports |
|---|---|
| Relevance | Preliminary lexical preservation only; no adequate estimate of omissions or false relevance. |
| Aspect | Some topical stability, not actor/mode/object fidelity across languages. |
| Direction | Negation matching is not sufficient: scope, participant and obligation can reverse the substantive reading. |
| Status/modality | Explicitly weak: 50–94% modal-category agreement is not a validation gate. Mechanical verb categories also conflate senses of “may” and “will.” |

**Fix:** finish the 86-pair judgement before using it as evidence, with the stratum hidden and a rubric covering actor, object, negation scope, conditions and commitment strength. Preserve sampling probabilities; all-flagged plus 30 controls is a diagnostic enrichment design, not an unweighted accuracy sample. It cannot assess the 84 unmatched sentences: add a random sample of those, source-page alignment and omitted material. Eight supplied excerpts reach the 700-character cap; inspect complete spans when judging meaning. Use bilingual source checks for consequential claims and a probability sample spanning the additional languages/layout modes. Re-extract/retranslate affected column layouts. A second model alone is not a gold standard. Route B should replace the four production BENCH leaks immediately (item 2).

## 13. Human agreement design and bilingual codebook

**Verdict: sound with correction** as instrument development; not yet a defensible population validation.

Four hundred is not intrinsically too small, but effective facet size is the number both call R, not 400. At the proposed minimum 120, ten aspects average only twelve cases each before route/status subdivisions; rare labels can be absent. Fixed quotas and round robin are reasonable for coverage, but pooled alpha describes this enriched mix. Report per-category support, confusion matrices, disagreement rates and the actual relevant intersection. Do not infer corpus prevalence from the sample.

Scoring only mutually relevant units hides relevance-induced facet errors. Keep that conditional score, but add an end-to-end joint-label evaluation or a union-relevant adjudication analysis. Authors are legitimate developers, not independent external validators; their agreement is **not mathematically an upper bound** on outside-coder agreement (protocol line 43). Training on NO/UK needs supplementation with non-scored difficult cases covering authority, law, translation, conflicting clauses and negative commitments. Prevent main units or their displayed context from inadvertently duplicating training material.

The 0.80/0.667 cutoffs are conventions, not self-validating release gates. Specify handling of wide intervals, undefined coefficients, rare categories and top-ups before coding; the top-up needs a fixed size and stopping rule. The fresh 150 after one revision is reasonable if genuinely untouched; publish both rounds. Human-human agreement does not establish model accuracy, and prompt tuning on all 400 eliminates a clean model holdout.

The Czech and English instructions differ materially on authority and operational laws (item 10). More subtly, `draw_agreement_sample.py:66,112` shows only adjacent units, truncated to 600 characters, potentially across paragraphs/pages, whereas L1/L2 promise paragraph context. Humans and models would therefore answer with different information. The workbook has no `modal_term` field and does not explicitly display route in its column list.

**Fix:** harmonise Czech/English examples and decision rules, give identical bounded context to humans and models, correct the scorer, and freeze the evaluation design before opening CODE. Retaining subsequently excluded documents is acceptable for a labelled development/challenge set (protocol line 20), not a claim that the sample validates the final population unchanged.

## 14. Recall and “says little”

**Verdict: sound with correction.** About 6,100 genuinely checked random units can constrain corpus-level residual prevalence usefully. It cannot alone establish project-level silence.

For illustration, Wilson 95% intervals at n=6,100 are below; 0.5% uses the expected count 30.5 as an approximation. These assume correct human-assessed labels and simple random/Bernoulli sampling from the retained residual population. They are not intervals incorporating model error.

| True residual prevalence | Expected relevant controls | Approximate 95% interval | Relevant units in the current 124,233-unit residual pool |
|---|---:|---|---|
| 0.5% | 30.5 | 0.351–0.711% | 621; interval 437–883 |
| 1.0% | 61 | 0.779–1.282% | 1,242; interval 968–1,593 |
| 2.0% | 122 | 1.678–2.383% | 2,485; interval 2,084–2,960 |

The pool is R + not_sent, from `CANDIDATES_2026-11-13.csv`; it excludes X. If T is the verified relevant total in D+N, retrieval recall is `T / (T + 124233*p)`. A lower bound substitutes the upper prevalence bound; without T, a numeric recall figure cannot be supplied. Weight R units by inverse inclusion probability (approximately 20), D/N by 1. Distinguish dictionary-only recall from dictionary-plus-neighbour recall.

Human checking must cover model-negative controls, not merely confirmed positives. Otherwise model misses are counted as retrieval success. X has zero probability and requires a separate audit. Global intervals do not transport to each project: with only 50 controls and no hits, a one-sided 95% upper prevalence bound is still about 5.8%. Even globally, zero of 6,100 implies an upper bound about 0.049%, not literal absence. Source-search omissions, unavailable texts, translation and unitisation remain outside these intervals.

**Fix:** report “few relevant statements in the searched, eligible corpus,” with project coverage and an upper bound where estimable. Do not infer institutional indifference or silence from a low dictionary count. Finite-population/design-based inference can be used for the fixed corpus; broader generalisation needs additional assumptions.

## 15. Order, exposure and contamination

**Verdict: sound with correction.** Most events require disclosure and versioning, not a claim that all blinding is destroyed.

| Event | Disposition |
|---|---|
| Authors read 400 source units before later F-reference coding | Disclose source exposure at project/document/span level. It does not reveal sealed model answers, so model-output blinding can survive. It removes source-naivety; if that is required, reserve reference projects before talk coding or reverse the order. |
| Document decisions after seeing pilot aggregates | Disclose; apply a rule blind to project talk estimates, log reasons and freeze. If decisions depend on results, treat the analysis as exploratory and add sensitivity to the prior set. |
| Reading-order correction after results | Appropriate engineering repair, but version and rerun every dependent artifact. A/B were corrected; D still inherits the old extraction. |
| Agreement drawn before final evidence set | Retain only as development evidence, or redraw against the frozen final target. In the current case frame, routing and context repairs justify regenerating before coding. |
| Issuer/voice context | Verify issuer before use. The generator actually shows issuer/joint issuer, kind and year—not a `voice_class` label. Do not claim a voice-label prefill is displayed. Such metadata can still influence OWN/authority decisions. |
| One model family develops dictionary/prompts and later labels | Disclose correlated error risk; human source-based holdouts and failure-focused validation matter more than nominally independent model branding. |

Evidence: `EXPOSURE_LEDGER.md`; contract lines 176–178; agreement protocol lines 20–28; workbook generator lines 84–85,111–112. **Fix:** update the exposure ledger before the reference draw; separate development, human-reference locking, prompt tuning and final model evaluation. Do not open or infer the sealed project results early.

## 16. As-of date and national frame

**Verdict: unsound** on frame consistency; the date check is incomplete.

Contract lines 15–21 specify 43 national projects, unions outside that analytic frame, and 18 October 2026. The tier builder intentionally puts EU in a tier (`build_tier_workbook.py:64–70`), while unitisation accepts any tier other than out-of-frame (`unitise.py:95–100`). Thus EU's 15 documents enter the 250 documents and 20 units enter the human main sample. Treating member documents as one EU project is internally sensible; including that project in national denominators is not. The 42 unitised projects mean **41 national + EU**, not 42 of 43 national projects.

Workbook evidence rows total 285, not the brief's stale 281. In `extra/TIER_REVIEW_v12_2026-11-13.xlsx`, tier sheets columns C/D/E/S are year/date/decision/ID: 128 date cells are blank, five contain a year, 29 contain year-month, and 123 contain a full date. Therefore **162 lack a full day**, not 128. All 123 full dates precede the cutoff. Thirteen incomplete-date records have year 2026; four have January–June month dates, already sufficient to precede October. Nine have blank date cells; several titles supply an earlier month/day. Examples: T1 D14 blank but H14 says 3 September; T1 D192/H192 April; T1 D240/H240 and D241/H241 March; T1 D291/H291 needs a more precise SE publication date. T1 rows 302,333,334 and T3 row 141 also need metadata reconciliation.

November collection alone is not a violation. Earlier-year records or an unambiguously pre-cutoff month need no invented day. Mutable websites and amended legislation need the version existing at cutoff, not merely an old original publication date. Full source-version checking is **not verifiable from the pack**.

**Fix:** explicit `analysis_frame=national` filtering with EU as a separately labelled supplement; regenerate national counts and samples. Record date precision and a cutoff-eligibility decision, and archive the relevant version of mutable sources.

## 17. Missing pre-registration work and work to drop

**Verdict: unsound** to register the current procedure as a frozen production design.

The general plan anticipates many validations, but does not operationalise the following defects exposed by the actual artifacts:

1. Canonical publication/edition identity, a BENCH exclusion invariant and a national/union frame invariant across every output.
2. A tested round trip from author-reviewed workbook fields into the production manifest, with rejected/stale/duplicate decisions surfaced rather than silently ignored.
3. One declared text/context contract for humans and models; hash-bound source, translation, unit and paragraph versions.
4. A denominator rule for sections of general publications, a separate X audit and explicit processing-loss accounting.
5. Fixed AC1 category sets, undefined-alpha handling, missing-label validation, and an end-to-end facet score accounting for relevance disagreements.
6. Explicit separation of legal state, competence, claim status and implementation, plus a formal decision on retiring the P/G instrument.
7. An untouched model-evaluation component after human-driven revisions; declared top-up/stopping rules and rare-category handling.
8. A replay bundle containing run logs and all non-copyright analytical inputs needed to reproduce published aggregates; a manifest is not the underlying input.

Also complete the already-planned author approvals, evidence review, translation judgement, citation checking and failure gates; these are unfinished tasks, not newly discovered omissions. For the official Chinese English edition distributed through BIS, explicitly document whether an authenticated issuer edition hosted by a third party satisfies the “own official channel” rule; do not silently change that rule case by case.

**Drop:** year-by-year project indices, a subtraction of talk and commitment indices, the sentence-to-cell conversion funnel, P0 as “silent,” and project trait rankings justified solely by the current ICC/split-half pilot. Drop any claim of general translation accuracy based on matched benchmark pairs alone. The corpus can support an auditable cross-section with histories and unknowns; it does not support a fabricated panel or an absence claim from failed retrieval.

## 18. A defensible December 2026 scope

**Verdict: sound with correction.** Keep a measurement-and-data paper with a constrained descriptive contribution.

- **By late November:** repair canonical IDs/frame/routes, resolve source decisions and cutoff eligibility, align the codebook, validate scorer/context, then freeze and register the revised protocol with its development history.
- **Late November–early December:** independent human coding and adjudication under the repaired protocol; complete targeted translation/source checks, retaining processing failures and uncertainty rather than forcing labels.
- **December production:** contractual F1/F2/F3/F4/F7/F8 claims with source locators, authority, two status axes, basis and qualifiers; a smaller validated talk table limited to relevance, voice and reliable aspects. Keep direction/status only if their validation gates pass. Resolve or omit F9/F10 rather than allowing them to expand the project indefinitely.
- **By end December:** release manifest, decisions, code, checks, raw coder outputs, adjudications and reproducible aggregates; publish coverage/missingness tables and a few predeclared qualitative contrasts. EU remains a separate supplement. Omit the covariate illustration if admissible cases remain too few to support it.

Prioritise source-located claims and honest coverage over full-corpus six-facet classification. If independent bilingual assessment cannot be obtained in time, route-D status claims remain unvalidated and should be withheld from strong commitment comparisons or explicitly flagged for restricted use. The scope must shrink rather than converting an unavailable validation into an assumption.

## The twelve admitted weaknesses

| # | Assessment | Reason |
|---|---|---|
| 1. Provisional evidence set | **Understated** | Beyond provisional decisions, the set includes an out-of-frame union and duplicate language editions. |
| 2. Volume-based tiers | **Agree** | Publication/search/language volume conditions inclusion; share-bias direction is not generally known. |
| 3. Translation | **Understated** | Benchmark-only texts leak into production, run logs are absent, and matching excludes difficult sentences; a second model would not resolve validity. |
| 4. Regex unitisation | **Understated** | 73/240 retained diagnostic units fail the single-sentence structural criterion; X can exclude substantive statements. |
| 5. Five-percent recall control | **Overstated** | The numerical sample can bound global residual prevalence usefully; the larger problems are zero-probability X, unchecked model negatives and project-specific precision. |
| 6. Facet/contract alignment | **Understated** | Competence, legal effectiveness, actor/data scope, negative commitments and the non-nested funnel fail beyond the acknowledged status ladder. |
| 7. Agreement sample | **Understated** | False perfect alpha, data-dependent AC1 categories, silent missingness and unequal human/model context are additional concrete defects. |
| 8. Exposure | **Overstated** | Source exposure must be logged, but it does not itself expose sealed model outputs or make model-output-blind reference coding impossible. |
| 9. Low project signal | **Agree** | It undermines latent project rankings; it does not prohibit a clearly conditional finite-corpus description. |
| 10. Process/testing | **Understated** | All 24 legacy tests pass, but none protects the new workflow; stale metadata and incomplete replay inputs remain. |
| 11. As-of dates | **Understated** | The denominator is stale and 162 lack a full date; nevertheless earlier years/months often already establish cutoff eligibility. |
| 12. Literature anchors | **Agree** | The pack does not contain a completed citation audit. Check actual sources and their applicability, not just bibliographic existence. |

## Five serious concrete problems not admitted in the brief

Repair estimates are indicative analyst effort, excluding waiting for bilingual reviewers or rerunning large jobs. They overlap and should not be added mechanically.

| Rank | Problem | Repair and approximate cost |
|---|---|---|
| 1 | **EU contaminates the national analytic set and human sample.** | Explicit frame invariant, rebuild all derived counts/sample, add regression fixture: half to one day. |
| 2 | **Four benchmark translations and their English editions both enter evidence.** | Canonical edition linkage, production BENCH exclusion, preferred-text routing, full duplicate audit and rebuild: one to two days. |
| 3 | **The proposed funnel is not nested and changes unit from sentences to F-cells.** | Rewrite estimands/denominators, separate retrieval from substantive stages and F coverage, update contract/schema/paper: half to one day plus author decisions. |
| 4 | **The scorer can certify degenerate data as perfect alpha and changes AC1's scale with the sample.** | Correct coefficients/validation/bootstrap semantics and add synthetic fixtures: half to one day. |
| 5 | **Humans and models receive different context for the same purported instrument.** | Freeze a shared context renderer, repair bilingual authority/legal-state rules, regenerate forms and test round trip: one to two days before coding; substantially more if coding has already begun. |

## May human coding start now?

**No for the main 400-unit round.** First fix the frame and edition routing, freeze the reviewed evidence/text versions, reconcile authority/status/basis rules, give humans and models identical context, and repair and test the scorer. Then regenerate the workbooks and record the revised sampling/exposure plan before either author opens CODE. Source review and preparation of non-scored training cases can start immediately. The authors need not wait for every later production analysis, but they must not spend two days coding an instrument whose categories and displayed evidence are about to change.

## Verification notes and methodological references

The audit ran the supplied suite, independently rebuilt tiers, joined metadata, checked file bytes for the two provided translations, tested coefficient and candidate-selection examples, and manually reviewed only the permitted diagnostic texts. No source corpus or complete translation corpus was supplied, so source completeness, full semantic fidelity, the complete pilot rerun and full sample regeneration remain unverified. No source or pipeline changes were made to the supplied pack.

For the statistical corrections, primary references checked during this audit were Krippendorff's [Computing Krippendorff's Alpha-Reliability](https://www.asc.upenn.edu/sites/default/files/2021-03/Computing%20Krippendorff%27s%20Alpha-Reliability.pdf), the author's [irrCAC documentation](https://cran.r-project.org/web/packages/irrCAC/refman/irrCAC.html) on supplying the complete category set, and Warton and Hui's [The arcsine is asinine](https://doi.org/10.1890/10-0340.1). These support the coefficient/transform cautions; they do not substitute for validation on this corpus. This is not a completed audit of every literature anchor in the proposal.
