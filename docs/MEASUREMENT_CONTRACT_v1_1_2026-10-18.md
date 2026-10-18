# MEASUREMENT CONTRACT v1.1 — CBDC privacy dataset / paper v11

Status: **development version 1.1, dated 18 October 2026 (evening)**; supersedes v1 of the same day after the first LLM fills of Norway and the UK and the authors' review (changes in §12). v1 was adopted after four rounds of independent review (12 Oct, 17 Oct ×2, 18 Oct 2026). It is frozen only after the worked profiles (Norway, United Kingdom) and the contrasting development cases have been coded independently by both authors and the definitions below have been corrected where the two codings diverged. Until then every rule may change; every change is logged in §12. Authors: Martin Bok, Dominik Stroukal. Technical collaborator: Claude.

---

## 1. Construct and unit

**Construct.** Publicly documented, current institutional commitments on the privacy and identifiability architecture of a retail central bank digital currency (CBDC), as of the **as-of date 2026-10-18**.

**Adopted commitment** = a concrete design choice announced by the body competent to decide for the project (central bank governing body, ministry, legislature, or a common authority of a monetary union). It need not be implemented or legislated. An option under consideration is not a commitment. A statement conditional on issuance ("if a CBDC is issued, the central bank will not see…") *is* a commitment about the design, unless the document presents it as one option among several.

**Unit of analysis** = project under one decision authority. The euro area (Eurosystem digital euro), the ECCU (ECCB) and WAEMU (BCEAO) are one project each; national documents of member states are sources for that project, never separate observations. All other jurisdictions in core_v1 are separate projects unless a document shows a common authority.

**Scope of evidence** = `core_v1` (frozen 2026-10-18; 109 documents, 56 jurisdictions; `CORE_V1_FREEZE.json`). Layers: official (default); `staff_research = Y` (author-views disclaimer or staff series: never establishes an adopted commitment; its factual description of a pilot may corroborate a cell); wholesale-only documents (flagged, outside the primary retail analysis); background legal layer (still-effective law published before 2018, usable only for F3/F5 legal basis, flagged `background_layer = true`).

**Time.** Current-state matrix with a change log. A later decision of the competent body on the same matter supersedes an earlier one; a later general speech does not supersede an earlier specific rule. Ended projects keep a historical profile marked `historical = true`.

## 2. Retrieval labels (not measurements)

PRIV / TRACE / DESIGN / OWN_PROJECT from the encoder rounds remain **retrieval and description labels**. They say where to look. They never set a cell value.

## 3. Atomic claim schema

One paragraph yields zero or more claims. Fields:

| field | status | content |
|---|---|---|
| `project_id` | inherited | from registry |
| `document_id`, `paragraph_id`, `page` | inherited | locator |
| `authority` | inherited, overridable | issuer and its competence (central bank board / staff / ministry / parliament / consortium); `staff_research` inherited from registry |
| `publication_date` | inherited | from registry; `effective_date` optional |
| `feature_id` | core | F1 … F12 (F3 is a single descriptive cell in v1.1; F5/F6 reserved) |
| `asserted_value` | core | per feature (§4) |
| `claim_status` | core | `option` (considered) / `adopted` (commitment) / `tested` (capability in pilot/PoC) / `operational` (live arrangement) |
| `quote` | core | verbatim span that establishes value **and** status; source language, with English gloss if needed |
| `actor` | conditional | CB / operator / PSP / public authority (which) / user; **mandatory** where the feature distinguishes actors (F1, F2, F3, F9); payer vs. payee stated where the source distinguishes them |
| `transaction_scope` | conditional | online / offline / wallet tier / limit band; **mandatory** where the value depends on mode (F1, F2, F4, F7) |
| `limits` | conditional | amounts, counts, time windows; **mandatory** for F4, F7 when the claim is tiered |
| `modality` | conditional | unconditional / conditional (state the condition); **mandatory** when a condition changes the meaning (F1, F3, F9) |
| `derivation` | core | `explicit` / `inferred` (list premises and the rule from §6) |
| `provenance` | core | `human:MB` / `human:DS` / `model:<name>` / `model+human` |
| `legal_state` | conditional | `in_force` / `adopted_not_effective` / `intended` / `n/d`; **mandatory only** when a value for F3 or F5 is derived from a legal instrument |
| `history` | derived | per cell, the dated sequence of (publication year, document, asserted value, claim_status) over all documents of the project; derived automatically from the claims, never coded by hand (§6.8) |

Rule: **every qualifier needed to derive the cell value must be recorded, unambiguously inherited, or marked `n/d`.** A claim missing a decisive qualifier can only support evidence state `partial`.

## 4. Feature definitions (cells)

Each cell = `value` · `evidence_state` (documented / partial / unknown / conflict / n.a.) · `claim_status` (highest status among supporting claims) · `derivation` · `provenance`. **Absence of mention = unknown, never "no".**

| ID | question | values | decisive qualifiers | traps |
|---|---|---|---|---|
| **F1 CB_LINK_ONLINE** | Can the issuing central bank / core-system operator, in the standard online mode, directly or through a routinely available link attribute a transaction to a person? | yes / no | actor = CB or operator; scope = standard online mode | "CB will not *use* the data" ≠ cannot link. Extraordinary re-identification → F9, not here. Pseudonymisation at the CB counts as *no* only if the CB holds no routine key to identity. |
| **F2 PSP_LINK_ONLINE** | Can the user's payment service provider routinely attribute an online transaction to a person? | yes / no | actor = PSP; scope; payer vs payee | KYC at onboarding does **not** imply F2 = yes (§6). Bearer/token designs where the PSP sees no transaction record → no. |
| **F3 LAWFUL_ACCESS_ROUTE** (descriptive, v1.1) | Does the institution document a route by which a public authority can obtain person-attributable transaction data, and through whom? | via_PSP / via_CB / via_both / none_stated / n/d (+ named authority in `actor`, process in `modality`) | actor = which authority; modality = legal process named; legal_state when derived from law | Descriptive only: no channel split, no aggregate, no outcome. "Same rules as for bank accounts" or "lawful basis under existing law" is a route via_PSP only if the PSP is named as the holder; otherwise n/d with the sentence quoted. Suspicion-based STRs are a route (via_PSP). Never coded ROUTINE/TARGETED: that distinction depends on law outside the corpus (v1 experience, NO and UK). |
| **F4 PRIVATE_OFFLINE_AVAILABLE** | Is an offline mode an adopted commitment in which individual transfer details are not routinely transmitted to or linked with a person by the CB or PSP, including at later synchronisation? | yes / no | limits; synchronisation behaviour; claim_status | Offline offered but privacy undescribed → unknown. Tested capability ≠ adopted. An adopted decision *not* to offer offline → no. |
| **F5 INDEPENDENT_ACCESS_GATE** | Does targeted public-authority access require prior authorisation by an independent body under an applicable adopted rule? | yes / no / n.a. | legal_state | **reserved in v1** (schema only) |
| **F6 NO_COMMERCIAL_REUSE_WITHOUT_CONSENT** | Is commercial use of PSP transaction data without separate user consent prohibited by an adopted rule? | yes / no | — | **reserved in v1** |
| **F7 LOW_ID_ROUTE** | Is there an adopted retail mode in which an eligible user can hold/pay up to a stated limit without verified personal identity (including verification via another account)? | yes / no | limits; onboarding; link to an identified account | KYC-lite that still verifies identity ≠ no identity. Never labelled "anonymity". |
| **F8 ONBOARDING_ID** | Does opening a standard wallet require verified personal identity? | yes / no | wallet tier | Descriptive only; **not** a premise for F2. |
| **F9 TARGETED_REIDENTIFICATION** | Can an online transaction be attributed to a person afterwards under defined extraordinary conditions? By whom, under what condition? | yes / no + actor + condition | actor; modality | Prevents reading F1 = no as absolute. Descriptive only. |
| **F10 PROGRAMMABLE_RESTRICTIONS** | Does the adopted design allow issuer/state-imposed restrictions on use (purpose, expiry, blocking) beyond AML? | yes / no / unknown | — | Must distinguish state-imposed restrictions from user-requested conditional payments. Lower priority; dropped if the pilot shows it overloads coders. |
| **F11 STATED_OBJECTIVES** | Which objectives does the institution declare, and did it explicitly rank one as main? | `stated_objectives` = set of flags {payment_modernisation, financial_inclusion, monetary_sovereignty_transmission, cash_substitute_resilience, aml_cft_tax_enforcement, innovation_competitiveness}, each with a quote; `primary_status` = one_primary / several_joint / unranked / conflict / n/d; `primary_objectives` only when ranking is documented | — | "CBDC will comply with AML rules" is a design requirement, not an objective. A zero flag means "not documented in the checked sources", not absence of motive. Word frequencies may go in an appendix as "linguistic emphasis"; they never set the flags. |
| **F12 LEDGER_TECHNOLOGY** (descriptive, v1.1) | Which ledger technology does the design use or has it chosen? | conventional_centralised / permissioned_DLT / permissionless_DLT / hybrid / undecided / n/d; `platform` free text (e.g. Hyperledger Besu, Corda, custom); `claim_status` decides whether the value is a test or a choice | claim_status; transaction_scope (online core vs offline component) | Tested platforms in a PoC are `tested`, never adopted. "Technology-neutral" statements → undecided. Permissionless is expected to be empty among adopted designs (stated in advance). Descriptive, outside the type and Y; external criterion: comparable fields in the BIS (Auer–Cornelli–Frost) and Atlantic Council trackers are used for a concurrent-validity check of the extraction, never to set the value. |

## 5. Typology (Layer 1, architecture) — deterministic

Online axis: **A** = F1 yes; **B** = F1 no & F2 yes; **C** = F1 no & F2 no. Offline axis: **0** = F4 no; **1** = F4 yes. Six cells A0 … C1; **C0/C1 are expected to be empty** among adopted designs (stated in advance). Missing input → partial assignment (e.g., `B?` = {B0, B1}); F1 unknown → `?`. The type is nominal; it is never coded 1–6 and never correlated. F3, F7–F12 do not enter the type.

## 6. Aggregation and derivation rules

1. Only `adopted` / `operational` claims from official-layer documents set an adopted value; `option` and `tested` claims set the value only with `claim_status` carried along and are never reported as commitments. Staff-research claims corroborate but never establish.
2. Supersession: later decision of the competent body on the same matter wins; a general speech never overrides a specific rule; store the superseded claim with `superseded_by`.
3. Conflict between two adopted claims of equal standing → `evidence_state = conflict`; both stored; adjudication by the authors (not by a model); result and reasoning logged.
4. Citation counts are not votes.
5. **Inference is allowed only as a necessary conclusion from documented premises, with premises and rule attached.** F2 may be inferred = yes only when all three hold and are documented: (i) the PSP holds an identifier → person mapping, (ii) the PSP routinely sees the relevant transaction record, (iii) the PSP can link the two in the same mode for the same participant. "Intermediated model + KYC + customer relationship" alone is insufficient (counter-example: Project Tourbillon). Every inferred cell is flagged; the report shows which types change when only explicit cells are used.
6. *(v1.1)* F3 has no aggregate. The route value is set by the most specific documented statement; conflicting routes across documents → `conflict`.
6a. *(v1.1)* **F7 inference rule.** F7 = no (`derivation = inferred`) when F8 = yes is documented for the standard wallet and no document of the project mentions any other tier, channel or route with lower identification (premises: the F8 claim + the absence statement, both recorded). Otherwise absence of mention = unknown.
7. Missing decisive qualifier → partial.
8. *(v1.1)* **History.** For every cell the pipeline derives `history` = the dated sequence of (year, document, asserted value, claim_status) from all claims of the project, in publication order; the current value is the last adopted/operational claim under the supersession rule, and the sequence is reported with claim_status so that "tested 2023 → undecided 2026" is not read as a reversal. History is a derived output, never hand-coded, and is reported descriptively (change map) only for projects with ≥ 3 dated documents.

## 7. Outcomes (Layer 1 → Y) and purpose layer (Layer 2)

- **Y₁** (primary empirical illustration, conditional): Y₁ = 1 ⇔ F1 = no (adopted); 0 ⇔ F1 = yes; else undetermined. Used as primary only if the pilot meets the orientation rule: ≥ 20 determinable projects and minority class ≥ 6. It measures separation of the central bank from transaction identity, **never** unavailability of data to the state.
- **Y₂ dropped in v1.1.** F3 is descriptive only; no outcome and no hypothesis is built on public-authority access (reason: §12).
- **Y₃**: Y₃ = 1 ⇔ F7 = yes; 0 ⇔ F7 = no (explicit, or inferred under §6.6a and flagged); else undetermined. Results are reported with and without inferred zeros.
- Layer 2 (F11) is descriptive; a pre-specified cross-tabulation architecture × declared objective and one pre-specified co-occurrence (share of F7 = yes among projects declaring financial inclusion) are descriptive results, never causal.

## 8. Naming

No country-level label such as "state control". `aml_cft_tax_enforcement` only when explicitly declared as an objective. F3 is reported as "documented lawful-access route", never as a level of access. Types are A0–C1; Y are binary features. No "explains / drives / effect of"; "is associated with", "co-occurs with".

## 9. Coder protocol (humans)

*(v1.1)* **Development projects** are filled first by the API pipeline (§10) and by an independent second-provider run; both authors then verify every cell against the cited page in a review workbook (value, evidence state, claim status, decisive quote, justification, counter-evidence, `quote_verified`) and record whether a disagreement is a model error or a definition problem. Development verdicts are development material, never the human reference. **Blind test projects** are coded by both authors **independently from the PDFs**, without sight of any model output, filling one matrix workbook each (one row per cell: value, evidence state, claim status, derivation, document, page, quote, qualifiers, note). Original independent codings are preserved before adjudication. Per project the workload is: F1, F2, F4, F7, F8, F10 (yes/no with unknown/partial/conflict allowed), F3 (route), F9, F11, F12. F5/F6 reserved. The keyword finder shipped with the workbook lists page references only, never values.

## 10. Machine protocol (API extraction, later)

Two LLMs from different providers, called through the API with no chat history, receive this contract (§3–§6) as the instruction and return claims in the schema of §3 as JSON, with `provenance = model:<name>`. *(v1.1)* The pipeline is `scripts/extraction/extract_api.py`; both its modes are logged and compared on the development projects: `two-stage` (per-document findings → synthesis from findings only) and `single` (all documents of the project in one request, where the provider's context allows). The mode used for the frozen instrument is fixed before the freeze on the basis of the development comparison, not of the test split. Development on a dev split of human-coded projects; at most five prompt versions, each a dated file with its dev metrics; the test split is scored once with the final prompt. Model–model disagreement → human adjudication; agreements and empty outputs are audited too. Whether extraction runs on all core paragraphs or on encoder-retrieved paragraphs is decided by cost before the freeze; bge-m3 is retained for sample selection and the language ablation.

## 11. Validation (summary; details in PREDICTIONS_v2.1 and the audit plan)

Development: worked profiles (Norway, UK) → contrasting cases (euro area, Canada staff-heavy, Chile/Brazil non-English, Hungary discontinued) → definitions corrected → freeze → OSF registration with decision record. Confirmation: one final audit of the frozen pipeline (stratified, weighted; family-specific recall; feature/type/Y error against the human reference), audit of DROP documents and ingestion, independent full-source reading of all project profiles by both authors.

## 12. Change log

- 2026-10-18 **v1.1** (development), after the authors' review of the Norway and UK LLM fills: (1) **F3 reduced to one descriptive cell** `LAWFUL_ACCESS_ROUTE`; channels and the aggregate removed; **Y₂ dropped** as an outcome, together with the H1/H2 tests on Y₂ in PREDICTIONS — reason: in both worked profiles the aggregate was `partial` and both fills showed that the ROUTINE/TARGETED distinction rests on law outside the corpus (NO: "AML rules the same as for other payment services"; UK: "lawful basis" under existing data-protection law). (2) **F7 inference rule** §6.6a (F8 = yes and no lower-identification route mentioned → F7 = no, inferred, flagged). (3) **F12 LEDGER_TECHNOLOGY** added as a descriptive cell with an external concurrent-validity criterion (BIS and Atlantic Council trackers); permissionless kept as a value, not a feature, because it is expected to be empty. (4) **`history`** derived per cell (§3, §6.8) for the change map. (5) §10: single vs two-stage API mode compared on development projects. Cell count: 20 → 15 coded cells (F1, F2, F3, F4, F7, F8, F9, F10, F11 ×8, F12) plus computed TYPE/Y.

- 2026-10-18 v1 (development): created from the reviewer's specification of 17 Oct and the authors' amendments A1–A8 (18 Oct), with the two corrections of the fourth review (F2 no-inference rule; F3 partial rule) and the purpose layer as non-exclusive flags with `primary_status`.

### 12.1 Addendum 18 Oct 2026 (after the first LLM fills of NO and UK)

- **Development fills are not instrument output.** Fills produced by interactive agents (session-bound, tool-driven reading, no reproducible request record) are development material for revising definitions. Instrument output is only what `scripts/extraction/extract_api.py` produces: two-stage API extraction (per-document findings → synthesis from findings only), with model id, contract/prompt/script SHA-256, raw request/response and token usage logged per run.
- **Temperature.** The Anthropic API rejects `temperature` for current models; sampling is provider-controlled. Reproducibility is recorded as model id + prompt hashes + raw response, not as a temperature setting. The same is recorded for any second provider.
- **Mechanical citation check.** Every quote in instrument output is checked against the cited page of the page-delimited text (`verify_quotes.py`); the `quote_verified` column is part of the output. A quote not found on the cited page (±1) voids the claim for audit purposes.
- **Development vs. blind test.** Jurisdictions whose LLM fills the authors have seen (NO, UK, and any later development jurisdiction) are excluded from the sealed blind test set; the test set is drawn from the remaining core jurisdictions and coded by the humans without sight of any model output.
