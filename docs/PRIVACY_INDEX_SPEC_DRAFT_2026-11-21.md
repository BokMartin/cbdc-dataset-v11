# Privacy index: specification (DRAFT, 21 Nov 2026, revised the same evening after a referee-style review)

Status: proposal implementing the decision of MB in [ADR-009](../DECISIONS/ADR-009-privacy-index-headline-2026-11-21.md); DS to confirm. Implementation: `scripts/derive_index.py`, `scripts/index_reliability.py`, `scripts/index_validity.py`; tests `tests/test_derive_index.py` (synthetic cells only). **Nothing here has been computed on project data.** Section 11 lists what the review changed.

## 1. Construct

Axis 1: the extent to which the design that the official documents describe keeps the central bank, intermediaries and the state from routinely attributing a retail payment to an identified natural person. Axis 2: how firmly the competent body holds each element of that design. Not measured: how much a project talks about privacy, data protection in general, or whether a design is desirable. Talk labels never enter the index (ADR-004 §4).

## 2. Components and why these four

| Cell | Protective value | Role |
|---|---|---|
| F1 CB_LINK_ONLINE | no | first key of the lexicographic rule |
| F2 PSP_LINK_ONLINE | no | rest |
| F4 PRIVATE_OFFLINE_AVAILABLE | yes | rest |
| F7 LOW_ID_ROUTE | yes | rest |
| F8 ONBOARDING_ID | no | sensitivity only (overlaps F7; descriptive in the contract) |
| F10 PROGRAMMABLE_RESTRICTIONS [OPEN] | no | sensitivity only (control of use, not identifiability) |
| F3 LAWFUL_ACCESS_ROUTE, F9 TARGETED_REIDENTIFICATION | — | beside the index: direction is ambiguous (a documented route or exceptional process can mean the default is private) and F3 is descriptive by contract |
| data retention | — | not a cell of contract v12; adding it needs a contract change |

The four cells are the ones of the contract that answer "who can routinely attribute a payment to a person, online, offline and at entry". F2 and F7 are not independent (a low-identity route limits what a PSP can attribute); leave-one-out in §7 shows how much each component moves the result.

## 3. Axis 1, stated design (any status)

Each component is 1 (protective), 0 (not protective) or undetermined, from the cell value **at any status**. A considered design therefore scores like an operated one on this axis; the status of every point is shown beside it (axis 2), and the same score on admissible cells only (contract §5, rule C) is reported for every project (§5). Contract §7.1 (primary values only from admissible claims) is respected because the primary F-matrix is unchanged; axis 1 is a status-attached view, labelled as such. In this view F4 and F7 are read as "the documents describe an offline mode / a low-identity route", not "endorse" one. **Open:** the authors may swap the two (admissible as primary, stated as robustness); review item 1.

**Lexicographic rule (primary).** F1 first, then the mean of F2, F4, F7 ("rest"), embedded on [0, 1]:

- F1 protective: 0.5 + 0.5 × rest
- F1 not protective: 0.5 × rest
- F1 undetermined: from 0.5 × rest_lower to 0.5 + 0.5 × rest_upper

The 0.5 is the split point between the two F1 classes, not a tuning constant: every project with a protective F1 lies above every project with a non-protective one, whatever the rest. Alternative rules in the sensitivity analysis: the compensatory mean of the four, and the cap of v0.1 (corrected: it now applies only to a determined F1 = yes).

**Interval.** Nothing is filled: the lower bound counts every undetermined component as not protective, the upper bound as protective (contract §8.4; Manski-type bounds). An unresolved disagreement between the blind coders makes the cell undetermined (§10.3), so it widens the interval.

## 4. Axis 2, commitment profile

Rung of each component that carries a value: considered 1, tested 2, endorsed 3, operational 4; none 0. Reported as a **profile** (four rungs) and as the **number of components at rung 3 or above out of 4** (fixed denominator). Ranks are not averaged (review item 4).

## 5. Robustness: admissible view

Axis 1 computed on admissible cells only (rule C), for every project, beside the primary interval.

## 6. Separation of projects (diagnostic until DS confirms ordering)

Two projects are separated when their intervals do not overlap, or, under the lexicographic rule, when one has a protective and the other a non-protective F1. Until DS confirms ADR-009, the brief and ADR-005 stand: the article orders no projects, and separation is computed only as a diagnostic of how informative the index is (review item 8).

**Expected separation (simulation, design argument, not a measurement; `simulate_separation`, 44 synthetic projects, 200 draws, protective with probability 0.5).** F1 coverage taken from the sealed census aggregate (some F1 position for 33 of 43; admissible for 8 of 43); coverage of the other cells is unknown, so three levels are shown.

| View and coverage | Share of project pairs separated: mean (5th to 95th percentile) |
|---|---|
| stated, F1 0.77, rest 0.77 | 0.45 (0.35 to 0.55) |
| stated, F1 0.77, rest 0.50 | 0.34 (0.25 to 0.42) |
| stated, F1 0.77, rest 0.30 | 0.30 (0.22 to 0.40) |
| admissible, F1 0.19, rest 0.15 | 0.02 (0.00 to 0.04) |
| full coverage (ceiling) | 0.84 (0.81 to 0.87) |

Reading: the stated view can separate roughly a third to a half of all pairs; the admissible view almost none. This is why the admissible view is the robustness check and not the headline (review item 3). The simulation is re-run with the real coverage after F-cell production and before any score is read.

## 7. Test B1: uncertainty and sensitivity analysis (runs now; `uncertainty_analysis`)

Baseline: the separated pairs of the primary index. Reported: the share of them that survive (a) 500 Dirichlet(1) weight draws over the four components (kept in every draw, and on average); (b) the compensatory mean and the corrected cap; (c) leaving out each of F1, F2, F4, F7; (d) the admissible view; (e) adding F8 and F10; (f) dropping route-D cells; (g) dropping inferred cells. This follows the uncertainty-and-sensitivity practice for composite indicators (OECD and JRC 2008; Saisana, Saltelli and Tarantola 2005). Factor analysis and Cronbach's alpha are not used: four binary cells on 44 projects do not support them.

## 8. Not done by the index

No combination with talk labels; no difference of talk and commitment; no association with covariates in the article (H2 stays on Y1, contract §8); no causal language. The external comparison of §10.2 is a validity check of the instrument and is reported as such.

## 9. Literature

Verified by web search in the review of 21 Nov (not re-verified here): Munda and Nardo (2009), *Applied Economics* 41(12), on non-compensatory aggregation, and OECD and JRC (2008) Handbook §6.13: the basis for the lexicographic rule (Mazziotta and Pareto (2016) do not support a gate and are not cited for it); Manski (1989, 1990) on bounds; Alkire and Foster (2011) on counting with cut-offs; Mangano (1998) and Cukierman, Webb and Neyapti (1992) on indices of central-bank independence (the latter used their own weights and stress the gap between legal and actual independence: cite as analogue for coding provisions, not as support for equal weights); Romelli (2022, *Economic Policy*; 2024 is a working paper); Auer and Böhme (2021, BIS Working Paper 948) on CBDC design and privacy. From memory, citation check pending: Saisana, Saltelli and Tarantola (2005), *JRSS A*; Greco et al. (2019), *Social Indicators Research*; Auer, Cornelli and Frost (2023).

## 10. Validation that depends on data: prepared now, to run once the F-cells exist

### 10.1 Checklist (to carry into HANDOFF when ADR-009 is confirmed)

| # | Step | When | Script and input | Done |
|---|---|---|---|---|
| V1 | Freeze this spec, the known cases and the external measures; register with contract v12 | before F-cell production | this file, `data/index/*_DRAFT_*` | no |
| V2 | Both authors code F1, F2, F4, F7 blind for all 44 projects (176 cells) in the coder template, lock the files | before any model output for those projects is opened | `data/index/CODER_TEMPLATE_2026-11-21.csv` | no |
| V3 | Reliability: Krippendorff's alpha per cell (three categories and valued pairs), merge, disagreements to undetermined | after V2 | `scripts/index_reliability.py` | no |
| V4 | Re-run the separation simulation with real coverage | after V3, before reading scores | `simulate_separation` | no |
| V5 | Known cases | after V3 | `scripts/index_validity.py`, `data/index/KNOWN_CASES_DRAFT_2026-11-21.csv` | no |
| V6 | External comparison | after V3 | `scripts/index_validity.py`, `data/index/EXTERNAL_MEASURES_DRAFT_2026-11-21.csv` | no |
| V7 | Uncertainty and sensitivity (B1) on the real cells | after V3 | `uncertainty_analysis` | no |
| V8 | Model F-cells against the merged human cells | after production | contract §12 | no |

### 10.2 Validity (B2)

- **Known cases** (`KNOWN_CASES_DRAFT`): cells whose value the authors fix in advance from an official document; the index must reproduce them, and a miss is reported, never tuned away. Proposed from development cases that are already exposed (EU F1, F4; UK F1). Candidate cases for the Bahamas, China and Nigeria are listed **without** values: filling them exposes those projects for blind coding, so it is the authors' decision and is logged in `EXPOSURE_LEDGER.md`.
- **External measures** (`EXTERNAL_MEASURES_DRAFT`): Spearman rho between the midpoint of the stated interval and each measure, only for projects with interval width ≤ 0.25, with a bootstrap interval and the sign fixed in advance. Proposed: data-protection law in force (convergent, expected +, weak); CBDC project index of Auer, Cornelli and Frost (discriminant, expected 0). V-Dem is not used here, to keep it apart from H2. Trackers are comparison measures only and never evidence for a cell (AGENTS.md).

### 10.3 Reliability (B3) and input format

Each coder fills one copy of the coder template: `project_id, cell, value (yes / no / undetermined), decision_status, implementation_status, quote, page_index`. `index_reliability.py` stops on duplicate rows or values outside the list, reports alpha per cell (undefined, not 1, when all ratings fall in one category), and merges: agreement gives the shared value with the lower of the two rungs; disagreement gives an undetermined cell flagged `coder_disagreement`, which widens the interval. Gate: alpha ≥ .80 per cell (contract §12); a cell below it is reported and the authors decide before any score is read.

**Workload (estimate, not measured):** 176 cells, most of them for T3 projects with four or fewer documents; the coders search with the keyword finder of contract §10. Order of tens of hours per author.

### 10.4 Dry run on MOCK data (21 Nov, MB: "zatím to udělej na mockup datech")

The whole chain runs end to end on invented data: `python scripts/index_mock.py` writes 44 invented projects MOCK01 to MOCK44 (two blind-coder files with about 10 % planted disagreement, six known cases with one planted miss, two invented external measures, tiers); `scripts/index_report.py --label MOCK ...` writes `data/index/mock/MOCK_INDEX_{RESULTS.json, TABLE.csv, REPORT.md, MAP.svg}`. Every file name starts with MOCK, the table and report say MOCK DATA in their first lines, the map carries a watermark, and MOCK project ids refuse any other label (tested). The website build does not read `data/index` (tested). For the real run the same command takes the locked coder files and `--label` with the run date.

What the dry run shows about the design (properties of the method on invented inputs, not results):
- Almost all separation comes from the F1 class: dropping F1 keeps about 7 % of the separated pairs, dropping F2, F4 or F7 keeps 96 to 100 %. Under the lexicographic rule the index is close to "F1 plus a tie-breaker"; this is to be said plainly, or the authors prefer the compensatory mean as primary (it keeps only about 12 % of the lexicographic pairs).
- Weight draws change nothing for the same reason; weights matter only within an F1 class, where intervals are rarely narrow enough to separate.
- The external comparison uses only projects with interval width ≤ 0.25: 12 of 44 here. At that size the invented "discriminant" measure gave rho 0.49 by chance; the real comparison needs either a looser width rule fixed in advance or a statement that it is underpowered.
- The planted known-case miss and the planted coder disagreements are caught and reported.

## 11. Changes after the review of 21 Nov (items as numbered in the review)

1. Axis 1 renamed "stated design (any status)", status shown per point, F4 and F7 read accordingly; swapping primary and robustness left to the authors.
2. Blind double coding of F1, F2, F4, F7 for all 44 projects, alpha per cell, disagreement widens the interval (§10.3).
3. Separation simulated at expected coverage (§6); re-run before scores are read (V4).
4. Axis 2 is a profile and a count out of 4, no mean of ranks.
5. Lexicographic rule replaces the cap; the cap is kept only in sensitivity and no longer applies to the lower bound when F1 is missing (bug fixed, test added).
6. Choice of the four cells justified (§2); leave-one-out kept.
7. Known cases and external measures pre-specified (§10.2).
8. Separation is a diagnostic only until DS confirms ordering (§6).

## 12. Version 2 (MB, 21 Nov 21:31): all F-cells matter, and privacy talk against commitments

MB: an index that rests on F1 alone is useless; all F-cells must matter, privacy statements must come in, and a key output is privacy talk against actual commitments, with the expectation that privacy is talked about a lot and committed to little. Where this section and §2 to §4 differ, this section is the current proposal.

### 12.1 Design index on all eight privacy cells

Cells F1, F2, F3, F4, F7, F8, F9, F10 (F5 and F6 are reserved; F11 objectives and F12 ledger technology are not privacy properties). Scores (`SCORE` in `derive_index.py`):

| Cell | 1 (protective) | 0 | undetermined |
|---|---|---|---|
| F1 CB link | no | yes | anything else |
| F2 PSP link | no | yes | |
| F3 lawful access route | via_PSP | via_CB, via_both | none_stated, n/d |
| F4 private offline | yes | no | |
| F7 low-identity route | yes | no | |
| F8 onboarding ID | no | yes | |
| F9 targeted re-identification | no | yes | |
| F10 programmable restrictions | no | yes | |

F3 and F9 have a direction the authors must confirm (a documented route or process can also be read as a safeguard); a sensitivity variant drops them. Aggregation is the compensatory **mean** of the eight, as an interval; the lexicographic rule and the cap are sensitivity variants. Axis 2 is the rung profile over the eight cells and the count of cells at endorsed or operational.

**MOCK dry run, what it shows about the design:** every cell now moves the result (leaving one out keeps 53 to 91 % of the separated pairs), but with eight cells of which about half are undetermined the intervals are wide: only about 4 % of project pairs are separated in the stated view and none in the admissible view (simulation at that coverage: 2 %, 0 to 5.5 %). The design index is therefore a **profile per project**, not a league table; ordering is in any case not allowed until DS confirms (§6).

### 12.2 Talk against commitments, by aspect (`talk_commitment.py`)

The two layers stay separately measured and meet on the same unit, the (project, aspect) pair, for the six talk aspects that have a matching F-cell:

| Talk aspect (codebook v0.3) | F-cells |
|---|---|
| CB_ACCESS | F1 |
| INTERMEDIARY_DATA | F2 |
| AUTHORITY_ACCESS | F3, F9 |
| OFFLINE | F4 |
| ANONYMITY | F7 |
| IDENTIFICATION | F7, F8 |

DATA_PROTECTION, USER_CONTROL, PETS and GENERAL have no cell: talk on them is reported, with no gap. F10 has no talk aspect.

Per pair: **talk** = at least one own-voice relevant unit on the aspect; **commitment** = admissible (a mapped cell at endorsed or operational), stated (rung 1 or 2), none, or uncertain (blind coders disagree). Per project, over the six aspects: aspects talked about, design stated, committed, and the **gap = number of aspects talked about without an admissible commitment** (bounds for uncertain pairs). This is a count of cells of the 2 × 2 table of ADR-005, not the difference of two scales. Talk intensity (share of own-voice relevant units among candidates, Wilson interval) is reported beside it and never enters the gap.

### 12.3 Hypotheses to register before any data (proposal; MB's expectation, not a finding)

- **H-TC1** (talk exceeds decided commitments): per project, share of aspects talked about minus share with an admissible commitment, > 0. *The MOCK dry run shows this comes out positive even when talk only mirrors designs that are stated but not decided, because decided commitments are rare (the census found an admissible F1 for 5 of 43). It is reported descriptively, not as the test.*
- **H-TC2** (talk without substance; the discriminating test): share of aspects talked about minus share of aspects whose design the documents state at any status, > 0. In the MOCK dry run it is positive in the scenario where talk is frequent regardless of design (31 of 44 projects above, p < 0.001 at the upper bound; 21 above, 13 below, p = 0.11 at the lower bound) and not in the scenario where talk mirrors stated designs (0 above, 20 below).
- Test: one-sided sign test over projects, and the mean difference with a project bootstrap 95 % interval, at the bound least favourable to the hypothesis; the smallest difference of interest δ is set by the authors before the data (as for H2). No causal language.

### 12.4 Which earlier decisions this touches (nothing applied without MB and DS)

| Decision | Effect of version 2 |
|---|---|
| ADR-004 §4 (no count-based talk index) | kept if talk stays beside the index (option recommended to MB on 21 Nov); overturned if talk becomes a component of one number |
| ADR-005 §4 (2 × 2 table instead of Talk minus Commitment) | kept: the gap is a count of 2 × 2 cells on the same aspects; a project-level gap count is new and needs DS's agreement |
| Brief §1 "no difference of a talk and a commitment index" | kept in letter; the gap count must be described as above in the brief |
| ADR-009 v1 (four cells, lexicographic) | replaced by §12.1 |
| Contract v12 §6 (F3 descriptive only; F9, F10 [OPEN]) | F3 and F9 get a score direction, F10 enters the index: contract change, needs both authors |
| HANDOFF §4 decision 1 (blank double coding of voice and aspect, undecided) | becomes necessary: the gap rests on voice and aspect |

### 12.5 What it adds to validation

- **Talk layer:** the gap needs relevance, voice and aspect to be valid. Relevance between the authors is at alpha 0.46 (below the 0.667 of the protocol) and is being repaired; voice and aspect have never been coded blind. So: adjudication and codebook repair, then blank double coding of voice and aspect on 80 to 120 units (HANDOFF decision 1), then the model run of the talk layer (paid, three providers, ADR-006).
- **Commitment layer:** blind double coding of all eight cells for 44 projects is 352 cells (the template is ready), double the four-cell plan; alternative: all 44 projects for F1, F2, F4, F7 and a sample of 16 for F3, F8, F9, F10.
- **Scope:** both layers are needed for the index and the gap, and both are kept in full: all eight cells and the whole talk layer. No order of cuts is kept (MB, 22 Nov 2026).

### 12.6 Cells resting on an "inclined" document (LEANING; proposal, follows ADR-010 in PR 3)

MB (21 Nov 23:29) wants documents that strongly suggest a future retail CBDC without confirming it (for example the BoE and MIT report, Tourbillon, Helvetia, wholesale experiments) kept as "heavily inclined but unconfirmed". A cell whose only value comes from such a document carries the status LEANING (`decision_status = leaning` or `leaning = true`). Proposed handling, for MB and DS to confirm:

- **Primary index:** a LEANING cell is not scored. It only bounds the interval, as an undetermined cell does (nothing is inferred from an inclined document).
- **Variant `with_leaning`:** the LEANING cell is scored at its value. Reported as a sensitivity column (`with_leaning_lower`, `with_leaning_upper`).
- **Flag `rests_on_leaning`:** set when LEANING cells are at least half of the determined cells; such a project is reported with a note.
- **Commitment axis and talk gap:** LEANING never counts as stated or committed (rung 0); `pair_state` marks the pair with `leaning` so the table can show it.
- A value from the project's own document always wins over a LEANING value.
