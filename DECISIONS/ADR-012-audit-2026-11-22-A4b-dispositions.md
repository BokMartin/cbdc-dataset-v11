# ADR-012: audit A4b of the authors' decisions of 22 Nov 2026: record, verification and proposed dispositions

Status: **record of the audit and of MB's answers to it (22 Nov 2026, 14:21); DS has confirmed nothing.** Rows marked "proposed for confirmation" become MB's decisions only when he confirms the merge of this record. MB took eighteen decisions (D1 to D18) in the project chat on 22 Nov 2026 (his words: [`docs/audits/DECISIONS_MB_2026-11-22_verbatim.md`](../docs/audits/DECISIONS_MB_2026-11-22_verbatim.md)). Before they were written into the repository they were audited by a second model at MB's request (audit A4b). The auditor recommends amending most of them. No rule, contract section or script is changed by this file; the amendments listed in §5 are applied after DS confirms, in one change, as for ADR-009 and ADR-010. DS has confirmed none of it.

Report: [`docs/audits/INDEPENDENT_AUDIT_2026-11-22.md`](../docs/audits/INDEPENDENT_AUDIT_2026-11-22.md), stored unchanged, SHA-256 of the returned file `a53b87ceb2271d5147cc902fdcc60667367e10f4ff6a1a340105cc034b4bc146`. Brief and prompt beside it. Pack `CBDC_AUDIT_PACK_2026-11-22.zip`, SHA-256 `3733c65256aad85200fd38470e60143875a234d18f296313035a9b2c09593c07`, built from `706b2e8` (main after PR 8, CI green). Auditor run by MB in a chat product; the report identifies itself as "OpenAI Codex, based on GPT-6" and says it could not authenticate the name `gpt-6-astra`. It declares a vendor-level interest in D2, D6, D8 and D16 (the same vendor's model made the translations and pre-filled the 19 Nov disagreement workbook).

Verdict of the auditor: decisions **not ready** to be recorded as adopted; registration **NO-GO** until the conditions in its section 1 are met.

## 1. What the pipeline assistant checked of the auditor's claims

| Claim | Checked how | Result |
|---|---|---|
| Finding 1: a conflicted, partial, operational cell is inadmissible for rule C but counts as decided in axis 2 and as "admissible" in the talk-against-commitment table, and gets a stated-design score | ran `admissible()`, `axis2()`, `pair_state()`, `component()` on the invented cell `{value: no, evidence_state: partial, conflict: true, decision_status: unclear, implementation_status: operational}` at `706b2e8` | **confirmed**: `admissible` False, `axis2` decided 1, `pair_state` "admissible", stated component 1. This is V6 of the 22 Nov check, now shown by execution |
| 21a: eligible population of the 196 confirmed evidence texts = 7,461 dictionary hits, 5,726 neighbours, 106,247 others (5,282 random controls + 100,965 unsent) = 119,434; 40,189 excluded X | join of `CORPUS_DOCUMENTS_2026-11-21.csv` (decision KEEP or BORDERLINE) with `UNITS_MANIFEST_2026-11-17.csv` and `CANDIDATES_2026-11-17.csv` | **confirmed** exactly |
| Finding 2: 14 frame projects in Table 2 of Nijsse and Pinto (2026), 9 of them core (BS, EU, IN, JM, JP, KZ, NO, RU, UK) | the paper is not reachable from the assistant's environment | **not checked**; 14 agrees with the count the authors were given on 21 Nov |
| Finding 4 and answer 11: rejecting a "fully anonymous CBDC" does not make F7 = no under contract §6 (rule E) | contract §6, F7 row | **confirmed**; the assistant had admitted the same risk in the brief (§4 item 13) |
| Finding 9: corrections to the 22 Nov check (V3 not inevitable, S3 overstated, S7 unproved, V4 F7/F8 dependence overstated) | not yet re-checked line by line | open; accepted as plausible pending check |
| Other file and line references | spot checks only | not systematically verified |

## 2. Row by row (author decision column empty until MB and DS decide)

"Auditor" = disposition in the report's section 2. "Assistant" = the pipeline assistant's proposal. Wording to adopt is the report's, unless the author decision says otherwise.

| # | MB 22 Nov (short) | Auditor | Assistant | Author decision |
|---|---|---|---|---|
| D1 | core 16 T1+T2, NO/UK development, T3 exploratory, no translation exception | AMEND: authors code the 16 from blank records and adjudicate from sources before any model output; report exposure by source (NO/UK pilot, Table 2) | agree || MB, 14:21 ("s ostatnim souhlasim", with point 6 below): the 16 core cells are coded by both authors from sources before any model output is opened. Auditor's wording otherwise **proposed for MB's confirmation at merge** |
| D2 | adjudicated cell with provenance; three-model unanimity else authors | AMEND: human source-adjudicated record primary in the core; outside the core unanimous claims still need a source check | agree || MB, 14:21, point 6 accepted: in the 16 core projects the authors decide every cell from the sources; the three models are a comparison. Outside the core: auditor's wording proposed for confirmation |
| D3 | much talk / few commitments, four quantities, no sign test | AMEND: registered hypothesis with fixed conventions (answer 5); facet gate; failed facets exploratory | agree; the conventions in answer 5 need MB || **open**: the four quantities stand (MB, 12:37); the auditor's numeric conventions in answer 5 (e.g. ≥ 1 own-voice relevant unit per 100 eligible units; fewer than 2 of 4 protective commitments) need MB's yes |
| D4 | widen axis 1 to keep F10; mean of 8; PET beside F7 | AMEND: primary index on F1, F2, F4, F7; eight-cell composite and F7/F8 grouping as sensitivity; F3 stays categorical (no direction); PET as a multi-valued record | the auditor's version is better grounded, but it reverses MB's 21 Nov "all F-cells must matter" for the headline; MB decides || MB, 14:21, point 1 accepted: "report both numbers side by side (four cells F1, F2, F4, F7 and the eight-cell composite); the eight-cell one as primary only if F3 has no direction and stands beside the mean". F3 is categorical, outside the score. **To clarify:** with F3 beside the mean the broader composite has seven scored cells (F1, F2, F4, F7, F8, F9, F10) |
| D5 | split INCLINED: joint retail reports may give LEANING; wholesale context and PET only | AMEND: three classes; joint retail experiment only as a flagged sensitivity; wholesale PET in a separate context table | agree || proposed for MB's confirmation at merge (consistent with spec §12.6: LEANING is never a commitment and is scored only in the `with_leaning` variant) |
| D6 | machine translation in the index, variant without it | AMEND: routes A/B (and checked C) primary; route D in a labelled extension; Taiwan flagged; a Chinese reader check only if a Taiwan primary value is needed | agree; zero cost option, matches "least resistance" || MB, 14:21, point 2 accepted: **auditor's amendment not taken.** Main result includes machine-translated (route D) documents; a variant without them is reported beside it; Taiwan's dependence on route D is stated. Contract §9 to be aligned with ADR-009 |
| D7 | full scope, no dates or cut lists | ADOPT | adopt || adopted (MB, 12:51) |
| D8 | voice and aspect blind on 80 sentences; joint review if agreement fails | AMEND: same 80 also for basis, decision and stance; fresh relevance check; joint review gives labels but cannot pass the gate | agree; adds about 3 to 6 hours || MB, 14:21, point 6 accepted: the same 80 sentences are also coded blind for decision and stance (auditor: also basis). **Open:** the auditor says joint review cannot pass a failed gate (failed facet → exploratory); MB said on 12:51 that disagreements would be resolved jointly. Needs MB |
| D9 | ANONYMITY → F7; rejection = F7 no endorsed | REJECT: rejection is a flag; F7 = no only under rule E | agree || MB, 14:21, point 3 accepted: **auditor's rejection taken.** A rejection of full anonymity is a flag (`anonymity_rejected`); F7 = no only under rule E |
| D10 | decision and implementation as two fields | AMEND: keep all rule B values; one predicate for every commitment count | agree || proposed for MB's confirmation at merge |
| D11 | cutoff = freeze day (proposal) | AMEND: keep 18 Oct 2026, or a dated amendment with a fixed new date and a uniform eligibility re-check | MB decides || MB, 14:21, point 4 accepted: cutoff stays 18 Oct 2026 as the issue date of a document (auditor's first option) |
| D12 | no second corpus | ADOPT | adopt || adopted (MB, 13:09) |
| D13 | tiers frozen on 17 Nov | ADOPT (count-only grouping as sensitivity) | adopt || adopted (MB, 13:22) |
| D14 | use 7 existing T3 translations | AMEND: only in the translated extension, flagged as historical queue | agree || follows D6: the 7 existing T3 translations are used like the other route-D texts, flagged as made under the earlier queue (auditor's "extension only" not taken because D6 keeps route D in the main result) |
| D15 | statuses of 7 UNRESEARCHED projects | AMEND: dated source per field, MB confirms, unknown stays unknown | agree || proposed for MB's confirmation at merge |
| D16 | complete exposure ledger | AMEND: cell-level entries; DS attests his own reading | agree || proposed for MB's confirmation at merge; DS to attest his own reading |
| D17 | "found via" column, no further literature check | AMEND: either the same bounded check for all 16 core projects, or quarantine the literature-driven additions in a supplement | MB decides || **MB, 22 Nov 2026, 14:21:** "dokuemnty nalezene pres nijsse zkratka pridat a hotovo. stejne jsme je meli najit nasi metoeologii." (*Simply add the documents found through Nijsse and Pinto and that is it; our methodology should have found them anyway.*) Auditor's amendment not taken: no further literature check, no quarantine. DS to confirm. |
| D18 | store inclusion probabilities; smallest defensible reference sample | AMEND: direct stratified random draw from all eligible units (140 / 50 / 210); 400 recommended, 388 minimum at ±7 pp, 300 if only pooled relevance at ±8 pp; no size certifies rare facet values | MB decides the size || 400 units, direct stratified random draw 140 / 50 / 210 with stored inclusion probabilities (presented to MB 13:48, no objection); proposed for confirmation at merge |

## 2a. Nijsse and Pinto (2026): exposure to Table 2 (auditor finding 2 and 8, answer 7)

**MB, 22 Nov 2026, 14:21:** "rozepis jakych 9 z 16 je v tabulce - kazdopadne bych to ignoroval. je to prirozene zkoumame cbdc, oni take. vysledky muzeme mit jine - nebude to validace. jen vyuzivame jejich kvalitne zpracovanych PET definic." (*List which 9 of the 16 are in the table; in any case I would ignore it. It is natural, we study CBDCs and so do they. Our results can differ; it will not be a validation. We only use their well-prepared PET definitions.*)

Recorded consequence: the paper does not present any comparison with Table 2 as validation; the paper is used only as the source of PET definitions. That both authors read Table 2 before coding stays in `EXPOSURE_LEDGER.md` as a disclosure (the 9 core projects named by the auditor: BS, EU, IN, JM, JP, KZ, NO, RU, UK; not re-checked by the assistant). DS to confirm.

## 3. Repairs that need no author decision

- Finding 1 / V6: one validated claim-to-cell path; `axis2()` and `pair_state()` use the same rule-C predicate as `admissible()`; the merge keeps every key and the located quote; negative tests through the report entry point. Not started; to be done before any blind coding or registration.

## 5. Texts to change after DS confirms (one change, not applied here)

ADR-009 (index definition, D4; source of cells, D2), index spec §10 and §12 (D1 to D4, D18), contract v12 §1 (D11), §2 and §4 (D5), §5 to §7 (D4, D9, D10), §9 (D6), §10 (D1, D2), §11 (three models), new PET cell; rule D1 rules 1 and 2 (D5); AGENTS.md "Evidence" (D5); protocol v2 §4 (D8); schema aspect map and codebook ANONYMITY (D9); `scripts/units/draw_agreement_sample.py` (D18); `data/frame/projects.csv` (D15); EXPOSURE_LEDGER (D16); HANDOFF §4 to §6 and PROJECT_BRIEF.

## 4. Consequences

- Registration, blind F-cell coding and the first paid call wait for the author decisions above and for the repair in §3.
- The ledger row for this audit is in `EXPOSURE_LEDGER.md`; the register row in `docs/audits/README.md` §4.
