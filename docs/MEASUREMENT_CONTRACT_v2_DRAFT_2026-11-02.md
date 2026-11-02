# MEASUREMENT CONTRACT v2 — CBDC privacy dataset / paper v11 (DRAFT)

Status: **draft for the authors' consultation of 6 November 2026**, prepared 2 November 2026 by Claude from contract v1.1 (18 Oct) and ADR-001 (dispositions of the external consultation of 28 Oct). Nothing here is adopted until an author initials the corresponding ADR row. Items marked **[OPEN]** need an author decision on 6 Nov. Authors: Martin Bok, Dominik Stroukal. Technical collaborator: Claude. Target: Data & Policy (measurement and data paper, limited illustration).

Reading guide: §1–§2 scope; §3 the claim schema; §4 status model (rules A–B); §5 admissibility (rule C); §6 cells; §7 derivation; §8 outcomes; §9 evidence language; §10 human protocol; §11 machine protocol; §12 validation and gates; §13 exposure; §14 change log and crosswalk to v1.1.

---

## 1. Construct, unit, estimand

**Construct.** Publicly documented institutional positions on the privacy and identifiability architecture of a retail CBDC, measured as *claims* with a status, not as a design panel. The primary matrix reports **endorsed or operational** positions only (§5); everything else is reported with its status attached, never as a commitment.

**Unit.** Project under one decision authority (unchanged). Monetary unions are one project each; member-state documents are sources, not observations. Union projects are outside the national analytic frame (ADR F9).

**Analytic frame** (`PROJECT_FRAME.md`, `data/frame/projects.csv`, 2 Nov 2026): 48 projects → 46 national → **43 retail-candidate national projects**. The frame is fixed before any production run; the three exclusions (BO, BR, US) and seven `UNRESEARCHED` statuses are recorded with reasons.

**Estimand (ADR F2).** Cross-section of current documentation as of the as-of date (**2026-10-18**, unchanged); eligible = national retail projects with an admissible F1 cell (§5) and observed covariate; the illustration estimates an unadjusted model-based association among measurable projects. Missingness bounds are reported (§8.4).

**Time.** Current state at the as-of date with a *claim history* (§7.6). No aggregate panel is built from it (ADR D4).

## 2. Scope of evidence

`core_v1` (109 documents, frozen 18 Oct) + `core_v2` (UK, 18 documents) → one **production source manifest** frozen at Phase 3 with a uniform gap check (ADR D2). Genre exclusions in the core rubric are replaced by an authority/content rule applied uniformly; the earlier freeze is not re-opened retroactively, the manifest records the amendment with a date (ADR D1). Layers unchanged: official (default) · `staff_research` (corroborates, never establishes) · wholesale-only (flagged, out of the retail analysis) · background legal layer (F3 only).

**Document-level language** is recorded in the evidence-language ledger (§9), not in the claim.

## 3. Atomic claim schema

One paragraph yields zero or more claims. Fields (⊕ = new in v2, Δ = changed):

| field | content |
|---|---|
| `project_id`, `document_id` | from registry / manifest |
| `locator` ⊕ | `page_index` (PDF 1-based) · `printed_label` (as printed, if any) · `span` (verbatim, may cross a page break) · `char_offsets` in the page-delimited text; the mechanical check (§11.4) uses `span` + `page_index` (NO16, UK12) |
| `issuer` ⊕ / `decision_authority` ⊕ / `endorsement_source` ⊕ / `competence` ⊕ | who published; which body is competent to decide the matter; which text records the endorsement (may be the official report's explicit account, with its locator); whether the issuer *is* the competent body (NO2) |
| `feature_id` | F1 … F12 (F5/F6 reserved; F9/F10 **[OPEN]**, see §6) |
| `asserted_value` | per feature (§6) |
| `decision_status` Δ | `considered` · `endorsed` · `rejected` · `superseded` · `unclear` (rule B) |
| `implementation_status` Δ | `untested_or_unreported` · `tested` · `operational` · `unclear` (rule B) |
| `design_or_experiment_id` ⊕ | which design version / pilot / test case / wallet the claim is about (NO5, NO15, UK8); `retail_or_wholesale` ⊕ at claim level (NO15) |
| `basis` ⊕ | `policy` ("will not use/see") · `architectural` (holds no key / sees only pseudonymous data) · `cryptographic` (rule D); mandatory for F1, F2, F4, F9 |
| `actor` | **role**, not organisation (NO8): `CB` · `CB_agent` (routine access attributable to the CB) · `independent_operator` · `PSP` · `public_authority:<role>` · `user`; payer/payee where the source distinguishes |
| `reference_participant` ⊕ | default `payer_ordinary_online_wallet` (rule D); state deviations |
| `transaction_scope`, `limits`, `modality`, `legal_state` | as v1.1 (qualifiers mandatory where the cell says so) |
| `derivation` | `explicit` · `inferred` (premises as claim ids + rule number) · `n.a.` (when no value is set; rule F) |
| `unknown_reason` ⊕ | `never_addressed` · `provisional_only` · `privacy_unspecified` · `search_incomplete` (NO9) |
| `superseded_by` | claim id |
| `provenance` | `human:MB` · `human:DS` · `model:<model id>` · `model+human` |
| `processing_state` ⊕ | `ok` · `ok_with_validation_problems` · `processing_failed` · `incomplete` — outside the substantive scale (rule F) |

Rule unchanged: every qualifier needed to derive the cell value is recorded, inherited, or `n/d`; a decisive missing qualifier caps the evidence state at `partial`.

## 4. Status model (rules A and B)

**4.1 Endorsement (rule A).** A claim is `endorsed` only when the **competent decision authority** adopts or commits to the position: a decision, a published design decision explicitly attributed to the governing body, legislation, or a commitment *conditional only on a future issuance decision*. The following are `considered`, however official or detailed: consultation papers, "rough drafts", working assumptions, design notes presented as provisional, options under study, recommendations, and experiment reports (NO1). The endorsing body and the text that records the endorsement are stored separately from the issuer (NO2); a document's genre never sets the status mechanically — status attaches to the claim (UK3).

**4.2 Two axes (rule B).** `decision_status` × `implementation_status` replace the v1.1 ladder option/adopted/tested/operational. Crosswalk for exports and the legacy diagnostic:

| v1.1 | v2 |
|---|---|
| option | considered × untested_or_unreported |
| tested | considered × tested (or endorsed × tested when the tested design was later endorsed — two claims) |
| adopted | endorsed × untested_or_unreported |
| operational | endorsed × operational (or unclear × operational where the operating arrangement is documented but no endorsing decision is cited — see §5) |

**4.3 Project status (NO3).** Replaces lifecycle labels in the analysis: `activity` (active / paused / ended) × `issuance_intent` (decided_to_issue / not_decided / decided_not_now / rejected) × `last_stage` (research / PoC / pilot / live) × `legal_constraint` (none / enabling_law_pending / prohibited). The registry's LIVE/PILOT/… labels remain descriptive display labels on the website only.

## 5. Admissibility and the primary matrix (rule C)

A cell enters the **primary commitment matrix** (and hence Y, the type and the illustration) only if **all** hold:

1. value ∈ {yes, no} (or the feature's categorical set);
2. `evidence_state = documented` (all decisive qualifiers present);
3. supporting claim is `endorsed` (any implementation status) **or** `operational` with the arrangement described in an official-layer document (unclear decision status allowed only for operational systems, flagged `operational_undocumented_decision`);
4. no unresolved `conflict`;
5. the claim is not `superseded` or `rejected`.

The rule is **symmetric**: a "no" needs the same evidence as a "yes" (closes the v1.1 Y₁ asymmetry). Everything else is reported in the **status-attached view** (considered/tested values with their status) and in the **table of commitments that disappear under strict rules** (ADR A7). Implementation: `scripts/derive.py` (`admissible()`), tested; the website shows both views, labelled.

**Evidence states (rule F):** `documented` · `partial` · `unknown` (+ `unknown_reason`) · `conflict` · `n.a.` (feature not applicable, e.g. offline for a project that endorsed "no offline") · and outside the scale `processing_failed`. `none_stated` (F3) means a completed search found no route; it is a value, not an unknown.

## 6. Feature definitions (cells)

Unchanged from v1.1 unless stated. Each cell = value · evidence_state · decision_status · implementation_status · basis · derivation · provenance · locator.

| ID | question (v2 wording) | values | v2 changes and traps |
|---|---|---|---|
| **F1 CB_LINK_ONLINE** | Can the issuing central bank, **or an agent whose routine access is attributable to it**, in the ordinary online mode, routinely attribute a retail payment by the reference participant (payer, ordinary wallet) to an identified natural person? | yes / no | Rule D. Independent operators (not attributable) recorded as separate claims, never merged into F1. Record `basis`: policy promise ("will not use") never sets F1 = no; architectural or cryptographic basis required. *Routine inferential access* (analytic linkability of pseudonymous data) is recorded in a separate note field `analytic_linkability`, never as F1 = yes (NO4). Balance/interest reporting to the CB is tagged `balance_reporting`, never transaction-data access (NO6). Alias → PSP mapping ≠ alias → transaction → person (UK2). |
| **F2 PSP_LINK_ONLINE** | Can the payer's PSP routinely attribute an online payment to a person? | yes / no | Inference (§7.3) only from premises that share participant, mode and design version; a *tested* premise cannot establish an *endorsed* production value (NO5, UK4). |
| **F3 LAWFUL_ACCESS_ROUTE** | Does the institution document a route by which a public authority can obtain person-attributable transaction data, and through whom? | via_PSP / via_CB / via_both / none_stated / n/d | Descriptive only (unchanged). via_PSP + via_CB from different claims → `via_both`, not conflict (rule F). Incorporation by reference ("same rules as for bank accounts") is quoted; a route is set only when the data holder and the path are identified (NO7); no legal reconstruction from model knowledge. Public-authority *role* recorded, or `authority_unspecified` (NO8, UK6). "Likely limited to" is not exhaustive (UK5). Underlying-law status kept separate from proposed CBDC rule (`legal_state`). No channel-level outcome. |
| **F4 PRIVATE_OFFLINE_AVAILABLE** | For a **specified release horizon**, is an offline mode endorsed in which individual transfer details are not routinely transmitted to or linked with a person by the CB/PSP, including at synchronisation? | yes / no | Deferred online settlement ≠ private offline; an option-only launch rule → unknown (UK7). Tested offline capability = considered × tested. |
| **F5 / F6** | reserved | | unchanged |
| **F7 LOW_ID_ROUTE** | Is there an endorsed retail mode in which an eligible **focal user** can hold/pay up to a stated limit without verified personal identity? | yes / no | **§6.6a of v1.1 deleted (rule E):** F7 = no requires an explicit requirement that *all* routes/tiers verify identity; silence → unknown (`never_addressed`). Counterparty verification does not disqualify (NO10). The v1.1 inferred zero is kept only as a labelled legacy diagnostic. |
| **F8 ONBOARDING_ID** | Does opening the ordinary wallet require verified identity? | yes / no | Descriptive; not a premise for F2 or F7. |
| **F9 TARGETED_REIDENTIFICATION** **[OPEN]** | Is a documented exceptional process recorded by which an online payment can be attributed to a person afterwards — with actor, information state and condition? | yes / no | Requires an actual exceptional linkage *mechanism*; privacy leaks and general risks go to a risk note (NO11, UK9). **Decision 6 Nov:** keep with this restriction, or omit. |
| **F10 PROGRAMMABLE_RESTRICTIONS** **[OPEN]** | Does the endorsed design allow issuer/state-imposed restrictions on use (purpose, expiry, blocking)? | yes / no | Excludes issuance/redemption rules, holding limits, AML onboarding controls and court seizure (NO12, UK10). **Decision 6 Nov:** keep in v2 and drop if development cases show it consumes time, or omit now. |
| **F11 OBJECTIVES** Δ | Which objectives does the institution state, and did it rank one as main? | 8 atomic tags, each `endorsed` / `considered` / `explicitly_rejected` / `not_documented` / `unresolved` (NO13); `primary_status` as v1.1; `primary_objectives` from **ranked original statements with stable ids** (UK11, NO14) | Tags: `payment_modernisation` · `financial_inclusion` · `monetary_sovereignty` · `monetary_policy_transmission` (split, NO13) · `cash_substitute` · `payment_resilience` (split) · `aml_cft_tax_enforcement` · `innovation_competitiveness`. Display crosswalk to the six v1.1 groups in `schema/f11_crosswalk.json` (ADR D5). Later rejection supersedes; omission from a later list ≠ rejection (NO14). |
| **F12 LEDGER_TECHNOLOGY** Δ | Which ledger technology, by **component**, and with what selection status? | per component (`core_ledger`, `offline_component`, `settlement_layer`): conventional_centralised / permissioned_DLT / permissionless_DLT / hybrid / undecided / n/d; `selection_status` = tested / shortlisted / selected / operational; `platform` free text | "hybrid" = a *defined* combination within the core ledger, not "DLT in one pilot, centralised in another" (ADR D3). Concurrent coding check against archived tracker versions (BIS, Atlantic Council) is a check of the extraction, not of privacy validity (E18). |

## 7. Derivation rules

1. **Primary values** come only from admissible claims (§5). Status-attached values are reported with their status; staff-research corroborates, never establishes.
2. **Supersession:** later decision of the competent body on the same matter wins; a general speech never overrides a specific rule; superseded claims stored with `superseded_by`. Omission of an item from a later list is not supersession (NO9, NO14).
3. **Inference** only as a necessary conclusion from documented premises recorded as claim ids with the rule number; premises must share participant, mode and design version (NO5). F2 inference: (i) identifier→person mapping at the PSP, (ii) PSP routinely sees the transaction record, (iii) same mode, same participant, same design version. Every inferred cell is flagged; the report shows which types change when inferred cells are removed.
4. **Conflict** between admissible claims of equal standing → `conflict`; both stored; adjudication by the authors with a written reason; never by a model.
5. **Missing decisive qualifier** → `partial`. Absence of mention → `unknown` with reason code.
6. **Claim history** = dated sequence of (year, document, value, decision_status, implementation_status) per cell, derived from claims, never hand-coded; reported as a change map only for projects with ≥ 3 dated documents; released as dated claims, not as a panel (ADR D4).
7. **Type** (A0 … C1) from admissible F1/F2/F4 only; partial assignment where an input is missing; nominal, never ordered (unchanged). The permissive (status-attached) type is shown beside it, labelled.

## 8. Outcomes and illustration

- **Y₁** = 1 ⇔ admissible F1 = no; 0 ⇔ admissible F1 = yes; else undetermined. Orientation rule unchanged (≥ 20 determinable, minority ≥ 6) — tested against the sealed endorsement census (§13) before registration.
- **Y₂** dropped (v1.1). **Y₃** = 1 ⇔ admissible F7 = yes; 0 ⇔ admissible F7 = no (explicit only); kept only if determinable projects ≥ 20 **[OPEN: depends on F7 census count]**.
- **H1** descriptive only; **H2** (liberal democracy) the single classified illustration (ADR A4). Decision table (ADR F6): Δ ≥ +δ supported if L > +δ; strong magnitude excluded if U < +δ; otherwise indeterminate; two-sided 95 %. **δ elicited** in a structured session with independent written answers before registration (ADR F8; working value 0.20 is *not* adopted). Covariate from one archived release, common year ≤ 2025; quartiles from the eligible frame before excluding unknown Y (ADR F3–F4). Interval for the nonlinear contrast itself with convergence checks; decision rule simulated at n = 20/30/40/45 (ADR F5, F7). No controls, no extra outcomes, no union-inclusive sensitivity, no CBI covariate (ADR A5, F9, F10).
- **8.4 Missingness:** eligible-but-undetermined projects are counted and bounds reported (all-undetermined-as-0 / as-1).
- Naming unchanged: no "state control", no causal verbs; "is associated with", "co-occurs with".

## 9. Evidence language (ADR H1–H5)

An **evidence-language ledger** (`docs/LANGUAGE_LEDGER.md`) lists every non-English core document with its route: **A** English original · **B** issuer's own English version (the English text is the evidence; the original is retained for the parallel-text test) · **C** independently checked human translation (translator and checker named) · **D** machine translation only, *provisional*. Primary human-verified outcomes use A/B/C only; D cells are flagged and never promoted to the primary matrix. Where authentic pairs exist (route B), a parallel-text test compares extraction from the original and the English version. The paper reports the English-accessibility selection; no multilingual validity is claimed.

## 10. Human protocol

- **Development cases** (exposed, flagged in `EXPOSURE_LEDGER.md`): NO, UK, euro area, Canada, Chile, Hungary, one LIVE project (ADR G3). Filled first by the pipeline (both providers), verified by the authors in the review workbook; verdicts are development material.
- **Reference coding** (blind): both authors code independently from the PDFs in a **blank reference workbook** (no model columns, no `agree_<model>`), lock their workbooks, then adjudicate; the adjudicated reference is locked before any model output for those projects is opened (E6). Predictor values and expected directions hidden during coding (E7).
- **Scope of the reference** **[OPEN, ADR E3]:** 16 full profiles (12 as emergency reduction, labelled limited validation), probability sample within the English-accessible domain with metadata strata and retained inclusion probabilities; **plus** F1 (and F7 if Y₃ kept) with qualifiers for **every** analytic project before model exposure (E5). Workload split: one author source-checks every retained claim, the other all inferential cells and the blind sample (E14).
- Keyword finder in the workbook lists page references only.

## 11. Machine protocol

- **Pipeline** `scripts/extraction/extract_api.py` v2: request = this contract (§3–§7) + schema `schema/cells_v2.json`; modes `single` (all documents, one request) and `two-stage` (per-document findings → synthesis); strict output validation; `processing_failed` / `incomplete` states with halt of synthesis; no truncation, no salvage; resume only by identity key; full request/response archive, model id, SDK and Python versions, prompt and script hashes, retries (E16, E17). Provider sampling settings that cannot be set are recorded as such.
- **Routing (E12):** complete-source single request when within the token budget of **both** providers; otherwise fixed section extraction + synthesis with source spans; both validated on development cases. The mode is fixed before the freeze on a *valid* comparison with identical, complete coverage (E11).
- **Two providers** (E13): primary fixed on development performance; the second exposes disagreements; all disagreements, failures and primary-outcome cells adjudicated, plus a sample of agreements.
- **11.4 Citation check** `verify_quotes.py` v2: full normalised span; states exact_page / spanning_pages / elsewhere_in_doc / fuzzy_candidate / invalid / empty / empty_but_value_set; furniture removal logged; ±1 page is diagnostic only (UK12). A claim whose quote is not located is void for audit purposes; entailment checked in the audit.
- **Replay:** every published number is reproducible from archived outputs without API access; fresh reruns form a separate stability envelope on six fixed projects.

## 12. Validation and gates (frozen at Phase 3, before scoring)

Gates as proposed (E9), to be fixed with denominators: α ≥ .80 (and AC1) on central constructs; ≥ 95 % joint correctness F1/F2/F4/F7 as screening; no unsupported endorsed primary-outcome cell; type ≥ 90 % exact; citations 100 % located and entailment-checked. Challenge battery 40–60 cases (E15), never pooled with the probability sample. Failure policy with tolerances and actions (E19). Outer audit: sampled source pages, 15–20 DROP documents, OCR/coverage loss (E10). Reporting: GUIDE-LLM primary, Abdurahman et al., TRIPOD-LLM supplement (E2); the instrument is named "human-adjudicated, LLM-assisted measurement pipeline"; raw A, raw B, agreement and adjudicated data reported separately (E1).

## 13. Exposure and sealing

`EXPOSURE_LEDGER.md` is the dated record of what the authors have seen. Replaces the v1.1 "no F-cell value seen" statement (ADR F1). The **endorsement census** (model-only, all 43 projects, one question: is there an endorsed F1 position?) is sealed outside the repository; only its SHA-256 and aggregate counts are committed; the authors use the aggregate to decide the orientation rule and the blind draw.

## 14. Change log and crosswalk

- 2026-11-02 **v2 DRAFT**: rules A–F adopted into §4–§5 and §7; `decision_status` × `implementation_status` with crosswalk (§4.2); project status as four fields (§4.3); rule C admissibility symmetric (§5); F1 actor rule D with `basis` and `analytic_linkability` (§6); **F7 inference from silence deleted**; F11 eight atomic tags with crosswalk; F12 by component; locators with spans and offsets; `unknown_reason`; `processing_state` outside the scale; evidence-language ledger (§9); blank reference workbook and E5 source-first F1 (§10); routing and replay (§11); gates (§12); exposure (§13). Y₂ remains dropped; F9/F10 and the blind-set size are open.
- 2026-10-18 v1.1; 2026-10-18 v1 (see v1.1 §12).

**Columns renamed (fill CSV):** `claim_status` → `decision_status` + `implementation_status`; added `basis`, `design_or_experiment_id`, `retail_or_wholesale`, `reference_participant`, `unknown_reason`, `page_index`, `printed_label`, `issuer`, `decision_authority`, `endorsement_source`; `page` kept as alias of `page_index` for the review builder.
