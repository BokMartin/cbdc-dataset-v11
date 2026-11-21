# ADR-009 — Two-axis privacy index as a headline result of the article (21 Nov 2026)

**Status:** decision of MB, 21 Nov 2026 (two choices in the project thread: the index belongs in the article, 18:16; it is a key result, 18:17; form "B. two-axis index", 18:38). **DS to confirm.** Until DS confirms, the amendments in §4 are proposals and are not applied to `PROJECT_BRIEF.md` or the contract. **Related:** ADR-004 §4, ADR-005 §4, contract v12 §5, §7.7, §8; `docs/PRIVACY_INDEX_SPEC_DRAFT_2026-11-21.md`; `scripts/derive_index.py`.

## Context

The brief says the article will not rank projects. ADR-005 replaced "ranking of projects by amount of privacy talk" with the highest rung per aspect, and "Talk index minus Commitment index" with a 2 × 2 table. ADR-004 §4 forbids a count-based talk index. The v1 manuscript (MSED 2026) used a documented-commitment privacy index as its dependent variable. MB wants a privacy index as a key result of the Data & Policy article: index papers are widely read, and the index connects the article to the dissertation.

The sealed endorsement census of 2 Nov (model only, aggregate) found an admissible F1 position for 5 of 43 national projects (plus 3 operational without a documented decision), and some F1 position at any status for 33 of 43. An index built only from admissible cells would be undetermined for most projects.

## Decision (MB)

1. The article reports a **two-axis privacy index** per project as a key result:
   - **Axis 1, stated design (any status):** how far the design that the documents describe keeps a retail payment from being routinely attributed to an identified person, from the values of F1, F2, F4 and F7 at any decision or implementation status (the status-attached view of contract §5). Reported as an interval [lower, upper]: undetermined components are bounded, never filled. *Revised after the review of 21 Nov (proposal):* lexicographic aggregation, F1 first, then the mean of F2, F4, F7, instead of a cap.
   - **Axis 2, commitment:** the rung of each component (considered 1, tested 2, endorsed 3, operational 4), reported as a profile and as the number of components at rung 3 or above out of 4 (*revised: no mean of ranks*).
   - Status never enters axis 1; the two axes are never multiplied or summed.
2. The index on admissible cells only (rule C) is reported for every project as the robustness check. Whether to swap primary and robustness is open (review item 1).
3. Talk labels never enter the index. ADR-004 §4 and the ban on a difference of a talk and a commitment index stand.

## Open (for DS and MB before the freeze)

- Lexicographic rule (proposal, replaces the cap of 0.5); equal weights of F2, F4, F7 (proposal); F8 and F10 only in sensitivity (proposal).
- Blind double coding of F1, F2, F4, F7 for all 44 projects, 176 cells (proposal after the review; MB approved preparing it on 21 Nov), alpha per cell, disagreement widens the interval.
- Known cases and external measures for validity (spec §10.2); filling a known case for an unexposed project exposes it.
- Whether separated projects may be ordered in the article: until DS confirms, separation is a diagnostic only.
- Order of cuts if time runs short (audit A3 item 18): proposal to put F1 to F4, F7, F8 before the talk facets.
- Whether the index is correlated with covariates in the article (proposal: no; H2 stays on Y1, exploratory).

## 4. Proposed amendments (not applied until DS confirms)

- `PROJECT_BRIEF.md` §1, "What it will not claim": replace "No ranking of projects by amount of privacy talk" with "No ranking of projects by amount of privacy talk; projects are placed on the two-axis commitment-based privacy index (ADR-009), with intervals, and ordered only where the intervals do not overlap".
- Contract v12, new §8.5 "Privacy index": the definition of §1 above, the sensitivity variants of the spec, and the rule that the definition is registered before F-cell production.
- Contract v12 §7.7 unchanged: the type stays nominal; the index is a separate construct.

## Consequences

- The critical path moves from the talk layer to the F-cell instrument at v12 (HANDOFF §5 item 6), which waits for the adoption of contract v12 (HANDOFF §4 decision 4).
- The index definition is part of the material of audit A5.
- Tests MB asked for on 21 Nov (19:36) are prepared on synthetic data: uncertainty and sensitivity analysis (runs now), coding reliability and validity (scripts, input formats and a checklist V1 to V8 in spec §10, to run once the F-cells exist).
- Cost of the index itself: none (deterministic script). Cost of the F-cells: as HANDOFF §8.
