# ADR-001 — Dispositions of the consolidated external consultation of 28 October 2026

Status: **proposed** (drafted 2 Nov 2026 by Claude for the authors; each row becomes *accepted* / *modified* / *rejected* only with the initials and date of an author in the last column). Context: `CBDC_v11_COMPLETE_CONSULTATION_2026-10-28.md` (external LLM consultant, Parts I–V), responding to the consultation pack of 27 Oct 2026. Rows cite the consultation's own identifiers (rules A–F; NO1–NO16, UK1–UK12; repair table; Part II–V items).

Legend for *Recommendation*: **accept** = implement as stated; **modify** = implement with the stated change; **defer** = not before the first production release; **reject** = not implemented, reason given. *Phase* = where it lands in the plan (0 bookkeeping · 1 instrument v2 · 2 development cases · 3 freeze/registration · 4 human reference · 5 production/audit · 6 analysis/writing).

## A. Framing, venue, hypotheses

| # | Item | Recommendation | Phase | Rationale / note | Decided (initials, date) |
|---|---|---|---|---|---|
| A1 | Keep "measurement and data paper with limited illustration" framing | accept | — | Consultant and authors agree | |
| A2 | Target venue: Data & Policy (Cambridge) instead of Economic Modelling | accept | 6 | Authors' decision 30 Oct 2026; Turobov & Coyle (2026, D&P 8:e47) is the nearest precedent; self-imposed target 31 Dec 2026, no external deadline | MB 30.10. |
| A3 | Replace "Institutional Determinants" in the title | **modify**: keep the title for now, revisit at writing stage | 6 | Author's standing decision (30 Oct); consultant's objection recorded and will be re-examined once results exist | MB 30.10. |
| A4 | Demote H1 (informal economy) to descriptive; H2 (liberal democracy) the only classified illustration | accept | 3 | Mechanism of H1 targets state/PSP access (dropped Y₂), not CB separation (Y₁) | MB 30.10. |
| A5 | Do not strengthen the illustration with controls, extra outcomes or weak-evidence countries | accept | 3–6 | | |
| A6 | Central question reframed: "who is documented as able to link a retail payment to a person, under what status, with what uncertainty" | accept | 6 | | |
| A7 | Preferred empirical application: audited cross-project account + table of commitments that disappear under strict evidence rules | accept | 6 | Replaces any rhetoric-vs-commitment correlation | |

## B. Measurement contract — governing rules A–F

| # | Item | Recommendation | Phase | Rationale / note | Decided |
|---|---|---|---|---|---|
| B-A | Rule A: endorsement replaces "conditional statement = commitment"; draft/preliminary design ≠ endorsement; record endorsing authority separately | accept | 1 | Decides Norway rough draft (option) and UK consultation response (claim-level) | |
| B-B | Rule B: replace status ladder with `decision_status` (considered/endorsed/rejected/superseded/unclear) × `implementation_status` (untested_or_unreported/tested/operational/unclear) + design/experiment id; export crosswalk to old labels | accept | 1 | | |
| B-C | Rule C: primary commitment matrix admits only yes/no · documented · endorsed-or-operational · all qualifiers · no unresolved conflict; symmetric for 0 and 1 | accept | 1 | Closes the Y₁ asymmetry (contract v1.1 line 85) | |
| B-D | Rule D: F1 actor = CB and agents whose routine access is attributable to it; independent operators recorded separately; reference participant = payer in ordinary online wallet; basis of evidence policy/architectural/cryptographic recorded | accept | 1 | | |
| B-E | Rule E: delete F7 inference from silence (contract v1.1 §6.6a); F7 = no requires explicit all-routes identification requirement | accept | 1 | Our own regression of 18 Oct; legacy sensitivity only as labelled diagnostic | |
| B-F | Rule F: define evidence states; add `processing_failed` outside the substantive scale; `derivation = n.a.` when no value; F3 via_PSP + via_CB → via_both, not conflict; `none_stated` = completed search found no route | accept | 1 | | |

## C. The 28 development problems

| # | Item | Recommendation | Phase | Decided |
|---|---|---|---|---|
| NO1 | Provisional single draft is still provisional (rule A) | accept | 1 | |
| NO2 | Store issuer, decision authority, endorsement source, competence separately; accept official report's explicit account with locator | accept | 1 | |
| NO3 | Project status: `activity` × `issuance_intent` × `last_stage` × `legal_constraint` instead of lifecycle labels | accept | 1 | Replaces our open question "declined, still exploring" | |
| NO4 | Routine inferential access defined under rule D; analytic linkability recorded separately from identity key | accept + limit | 1 | |
| NO5 | F2 premises must share participant, mode, design version; tested premise cannot establish endorsed production architecture | accept | 1 | |
| NO6 | Balance/interest reporting tagged separately, never transaction-data access | accept | 1 | |
| NO7 | F3 quotes incorporation-by-reference; route only when holder/path identified; no legal reconstruction from model knowledge | accept | 1 | |
| NO8 | Code roles not organisations; CB supervisory request → F3 with role | accept | 1 | |
| NO9 | Reason codes for unknown (never addressed / provisional only / privacy unspecified); omission from a later list ≠ rejection | accept | 1 | |
| NO10 | F7 eligibility by focal user; counterparty verification does not disqualify | accept | 1 | |
| NO11 | F9 restricted to documented exceptional process with actor, information state, condition; leaks → risk note | accept | 1 | |
| NO12 | F10: exclude issuance/redemption/holding limits/AML controls; court seizure separate; **or drop F10** | **defer decision**: keep F10 in v2 draft with the exclusions; drop if development cases show it consumes time | 1–2 | |
| NO13 | Objectives: `endorsed/considered/explicitly_rejected/not_documented/unresolved` at atomic level; split sovereignty from transmission | accept | 1 | |
| NO14 | Rank original objective statements, not assessment questions; later rejection supersedes, omission does not | accept | 1 | |
| NO15 | Claim-level retail/wholesale and test-case identifiers | accept | 1 | |
| NO16 | Locators: PDF page index, printed label, span, offsets; inferred cells carry premise citations | accept | 1 | |
| UK1 | Regenerate task/schema from frozen specification; archive old tasks with version | accept | 1 | |
| UK2 | Rule D; alias→PSP ≠ alias→transaction→person; alias privacy issue recorded separately | accept + limit | 1 | |
| UK3 | Status attaches to the claim, not the document; no mechanical doc_kind → status | accept | 1 | |
| UK4 | No adopted F2 from adopted identity holdings + option/test transaction visibility | accept | 1 | |
| UK5 | Record route without treating "likely limited to" as exhaustive; separate underlying-law status from proposed CBDC rule | accept | 1 | |
| UK6 | Named authority or `authority_unspecified`; no channel-level outcomes | accept | 1 | |
| UK7 | F4 about a specified release horizon; deferred online settlement ≠ private offline; option-only launch rule → unknown | accept | 1 | |
| UK8 | Participant-built Lab wallets = tested capability in the experiment, with sponsor attribution | accept | 1 | |
| UK9 | F9 requires an actual exceptional linkage mechanism; **or omit F9** | **defer decision** as NO12 | 1–2 | |
| UK10 | F10 excludes holding limits and AML onboarding restrictions | accept (if F10 kept) | 1 | |
| UK11 | Preserve ranked original objective statements with stable ids → thematic tags; "two jointly primary motives", not four flags | accept | 1 | |
| UK12 | Multi-page quotation spans with documented furniture removal; full normalised match; ±1 page is diagnostic only | accept | 1 | |

## D. Other contract changes

| # | Item | Recommendation | Phase | Note | Decided |
|---|---|---|---|---|---|
| D1 | Replace genre exclusions in CORE_RUBRIC (press releases, FAQs) with an authority/content rule applied uniformly; small F11 source layer for objectives-only material | **modify**: adopt the rule for the production source manifest; do not re-open core_v1 freeze retroactively — record as dated amendment | 1–3 | Jamaica exception already shows the inconsistency | |
| D2 | Freeze one actual source manifest (core_v1 + core_v2 + uniform gap check); never describe as "109-document study" with different sets per project | accept | 3 | | |
| D3 | F12: component + selection status; "hybrid" = defined combination in the core ledger | accept | 1 | | |
| D4 | History = claim history, not design panel; cut the aggregate time series from this paper; release dated claims | accept | 6 | Website slider stays labelled experimental | |
| D5 | F11 = 8 atomic tags with 6-group display crosswalk; rejection/endorsement stored atomically | accept | 1 | | |

## E. LLM-as-instrument methodology

| # | Item | Recommendation | Phase | Note | Decided |
|---|---|---|---|---|---|
| E1 | Name the instrument "human-adjudicated, LLM-assisted measurement pipeline"; report raw A, raw B, agreement, adjudicated dataset separately | accept | 5–6 | | |
| E2 | Reporting: GUIDE-LLM primary checklist; Abdurahman et al. primer; TRIPOD-LLM adapted supplementary | accept | 6 | | |
| E3 | Blind full-profile reference: 16 projects (12 as emergency reduction, labelled limited validation); probability sampling within declared English-accessible domain, metadata strata, inclusion probabilities retained | **open**: 12 vs 16 to be decided by authors on measured capacity (Friday 6 Nov consultation) | 3–4 | Claude's recommendation: 12 full profiles + E5 | |
| E4 | Challenge set (synthetic/development) for rare values, status changes, exceptional access; never pooled with the probability sample | accept | 3–5 | | |
| E5 | Independently code F1 (+F7 if Y₃ kept) with qualifiers for **every** analytic project before model exposure; development cases flagged as exposed | accept | 4 | Protects the regression outcomes directly | |
| E6 | Both authors lock independent workbooks and the adjudicated reference before model results are opened; blank reference workbook (not the review workbook) | accept | 4 | | |
| E7 | Hide predictor values and expected directions during reference coding; country anonymity not claimed | accept | 4 | | |
| E8 | Frozen pipeline run once on blind projects; retries only for transport failures under fixed policy | accept | 5 | | |
| E9 | Decision gates (α ≥ .80 central constructs; ≥ 95 % joint correctness F1/F2/F4/F7 as screening gate; no unsupported adopted primary outcome; type ≥ 90 % exact; citations 100 % located + entailment-checked; stability runs on 6 fixed projects) frozen before scoring; denominators and intervals reported | accept as proposed values; freeze at Phase 3 | 3 | Project-specific operational rules, not journal thresholds | |
| E10 | Outer audit: sample source pages/sections, 15–20 DROP documents, OCR/coverage loss reported | accept | 5 | | |
| E11 | Single vs two-stage comparison invalid (missing docs NO 2, 4; UK 4); rerun with complete identical coverage before choosing | accept | 2 | Status summary line 28 withdrawn (see EXPOSURE_LEDGER) | |
| E12 | Provisional routing: complete-source single request when within token budget for both providers; fixed section extraction + synthesis with source spans for larger corpora; validate both | accept | 2–3 | | |
| E13 | Two providers; primary frozen on development performance; second exposes disagreements; adjudication of all disagreements, failures, primary-outcome cells, sample of agreements | accept | 5 | Second API key supplied by MB when needed | |
| E14 | Workload amendment: one author source-checks every retained claim, the other all inferential cells + blind sample; documented as amendment of contract line 104 | accept | 4–5 | | |
| E15 | Contamination battery 40–60 cases (evidence deletion, masking/substitution, minimal semantic edits, irrelevant evidence, order/duplication, lesser-known sources), pre-registered | accept | 3 (design) / 5 (run) | | |
| E16 | Reproducibility: archive full request payloads, ids, settings/unavailable fields, retries, SDK versions, lockfile; exact replay from archived outputs without API, separate from fresh-rerun stability envelope | accept | 1 | | |
| E17 | Mandatory code repairs (9): full-span quote check; processing_failed/incomplete states with halt; no silent truncation/salvage in production; strict output validation; resume only with identity key; structured stage-one qualifiers; one tested derivation module with status gate; joins by doc_id; parameterised review builder | accept | 1 | | |
| E18 | F12 vs trackers = concurrent coding check, not privacy validation; archive exact tracker versions; add second criterion: operational wallet/onboarding rules for live/pilot schemes | accept | 5 | | |
| E19 | Failure policy with tolerances and actions registered | accept | 3 | | |
| E20 | Do not bolt the old DSL correction onto Firth contrasts | accept | 6 | | |

## F. Pre-registration

| # | Item | Recommendation | Phase | Decided |
|---|---|---|---|---|
| F1 | Replace "no F-cell value seen" with dated prior-exposure disclosure | accept | 0 (ledger) / 3 | |
| F2 | Estimand: current-documentation cross-section at 18 Oct 2026; eligible national retail projects with admissible F1 and observed X; unadjusted model-based association among measurable projects | accept | 3 | |
| F3 | One covariate rule: common observation year ≤ 2025 from archived release, named before registration | accept | 3 | |
| F4 | q25/q75 from the eligible covariate frame before excluding unknown Y; fixed across analyses; quantile algorithm named | accept | 3 | |
| F5 | Interval for the nonlinear contrast itself (profiled or pre-specified simulation), convergence checks | accept | 3 | |
| F6 | Decision table: H2 Δ ≥ +δ supported if L > +δ; strong magnitude excluded if U < +δ; else indeterminate; two-sided 95 % (97.5 % if two hypotheses) | accept | 3 | |
| F7 | Simulate the decision rule at n = 20/30/40/45 before registration | accept | 3 | |
| F8 | Elicit δ (structured session, independent written answers, signed minutes); if no defensible smallest magnitude → register estimation with intervals | accept | 3 | |
| F9 | Keep union exclusion; omit union-inclusive sensitivity; explicit missingness bounds | accept | 3 | |
| F10 | Drop CBI unless clear descriptive purpose | accept | 3 | |

## G. Completion plan, scope, cuts

| # | Item | Recommendation | Note | Decided |
|---|---|---|---|---|
| G1 | SUERF 4 Dec not pursued; Economic Modelling 31 Dec replaced by Data & Policy target | accept | authors 30 Oct | MB 30.10. |
| G2 | Cuts: aggregate historical panel, encoder retraining/model competitions, methods spin-off, legal-access reconstruction, extra regressions, decorative website work | accept | | |
| G3 | Seven development cases: NO, UK, euro area, Canada, Chile, Hungary, one LIVE | accept | | |
| G4 | Minimum viable paper as defined by the consultant | accept | | |

## H. Language (Part V)

| # | Item | Recommendation | Phase | Decided |
|---|---|---|---|---|
| H1 | Evidence-language ledger beside the contract; routes A (English original) / B (issuer English version) / C (independently checked translation) / D (machine-only, provisional) | accept | 1–2 | |
| H2 | Primary human-verified outcomes from A/B/C only; D flagged, not promoted | accept | 4 | |
| H3 | Audit the 12 non-English core documents (incl. suspect `zh` label on JP_BoJ_Pilot_JP, `ru/uk`) for authentic official English counterparts | accept | 1 | |
| H4 | Authentic parallel-text test where pairs exist; no universal minimum number | accept | 4–5 | |
| H5 | Report English-accessibility selection; no "globally validated multilingual" claim | accept | 6 | |

## Items rejected or not applicable

None rejected outright. Two decisions deferred to the authors (E3 blind-set size; NO12/UK9 F9/F10 retention) and one modified (A3 title).
