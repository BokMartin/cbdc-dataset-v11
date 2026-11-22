# ADR-009 — Two-axis privacy index as a headline result of the article (21 Nov 2026)

**Status:** decision of MB, 21 Nov 2026 (two choices in the project thread: the index belongs in the article, 18:16; it is a key result, 18:17; form "B. two-axis index", 18:38). **DS to confirm.** Until DS confirms, the amendments in §4 are proposals and are not applied to `PROJECT_BRIEF.md` or the contract. **Related:** ADR-004 §4, ADR-005 §4, contract v12 §5, §7.7, §8; `docs/PRIVACY_INDEX_SPEC_DRAFT_2026-11-21.md`; `scripts/derive_index.py`.

## Context

The brief says the article will not rank projects. ADR-005 replaced "ranking of projects by amount of privacy talk" with the highest rung per aspect, and "Talk index minus Commitment index" with a 2 × 2 table. ADR-004 §4 forbids a count-based talk index. The v1 manuscript (MSED 2026) used a documented-commitment privacy index as its dependent variable. MB wants a privacy index as a key result of the Data & Policy article: index papers are widely read, and the index connects the article to the dissertation.

The sealed endorsement census of 2 Nov (model only, aggregate) found an admissible F1 position for 5 of 43 national projects (plus 3 operational without a documented decision), and some F1 position at any status for 33 of 43. An index built only from admissible cells would be undetermined for most projects.

## Decision (MB)

The current design is version 2 (MB, 21 Nov 21:31 and 21:44; spec §12). Where spec §2 to §4 describe the earlier version, spec §12 is the valid proposal.

1. The article reports a **two-axis privacy index** per project as a key result:
   - **Axis 1, stated design (any status):** how far the design that the documents describe keeps a retail payment from being routinely attributed to an identified person, from the eight privacy cells **F1, F2, F3, F4, F7, F8, F9, F10** at any decision or implementation status (the status-attached view of contract §5). Aggregation is the **compensatory mean** of the eight cells (scores in spec §12.1), reported as an interval [lower, upper]: undetermined cells are bounded, never filled. The lexicographic rule (F1 first), the cap and the four-cell version (F1, F2, F4, F7) are sensitivity variants only.
   - **Axis 2, commitment:** the rung of each of the eight cells (considered 1, tested 2, endorsed 3, operational 4), reported as a profile and as the number of cells at rung 3 or above out of 8. No mean of ranks.
   - Status never enters axis 1; the two axes are never multiplied or summed.
2. The index on admissible cells only (rule C) is reported for every project as the robustness check. Whether to swap primary and robustness is open.
3. **Privacy talk stays beside the index** (MB, 21 Nov 21:44). It is set against commitments on the six aspects that have a matching cell, as a gap by aspect: per project, the number of aspects talked about without an admissible commitment (a count of 2 × 2 cells, spec §12.2). Talk labels never enter the index; ADR-004 §4 and the ban on a difference of a talk and a commitment index stand.
4. MB's expectation (much talk, little commitment) is registered before any data as hypotheses H-TC1 (talk against decided commitments, descriptive only) and H-TC2 (talk against stated design, the discriminating test); spec §12.3.

*History.* MB chose the two-axis form on 21 Nov at 18:38, first on F1, F2, F4, F7 with F1 as a gate. After the review the gate became a lexicographic rule, and the mock dry run showed the index rested almost only on F1. MB then decided (21:31) that all F-cells must matter and that talk against commitments is a key output; spec §12.4 lists every earlier decision this touches.

## Open (for DS and MB before the freeze)

- Compensatory mean with equal weights over the eight cells (proposal); lexicographic rule, cap and four-cell version as sensitivity only.
- Direction of F3 and F9 (a documented access route or re-identification process can also be read as a safeguard); a sensitivity variant drops them.
- Blind double coding of all eight cells for 44 projects, 352 cells (template ready); alternative: all 44 projects for F1, F2, F4, F7 and a sample of 16 for F3, F8, F9, F10. Alpha per cell; a disagreement widens the interval.
- Talk layer for the gap: blind double coding of voice and aspect, and repair of relevance (alpha 0.46); spec §12.5.
- Known cases and external measures for validity (spec §10.2); filling a known case for an unexposed project exposes it.
- Whether separated projects may be ordered in the article: until DS confirms, separation is a diagnostic only (mock: about 4 % of pairs separated, so the index is a profile per project).
- Scope (closed, MB 22 Nov 2026): the full scope is kept and registered; no order of cuts (spec §12.5).
- Whether the index is correlated with covariates in the article (proposal: no; H2 stays on Y1, exploratory).
- Cells resting only on an "inclined but unconfirmed" document (LEANING, ADR-010 in PR 3): proposal in spec §12.6, bound only in the primary index, scored in the `with_leaning` variant, flag `rests_on_leaning`; never counted as a commitment.

## 4. Proposed amendments (not applied until DS confirms)

- `PROJECT_BRIEF.md` §1, "What it will not claim": replace "No ranking of projects by amount of privacy talk" with "No ranking of projects by amount of privacy talk; projects are placed on the two-axis commitment-based privacy index (ADR-009), with intervals, and ordered only where the intervals do not overlap".
- Contract v12, new §8.5 "Privacy index": the definition of the Decision above (version 2), the sensitivity variants of the spec, and the rule that the definition is registered before F-cell production.
- Contract v12 §7.7 unchanged: the type stays nominal; the index is a separate construct.

## Consequences

- The critical path moves from the talk layer to the F-cell instrument at v12 (HANDOFF §5 item 6), which waits for the adoption of contract v12 (HANDOFF §4 decision 4).
- The index definition is part of the material of audit A5.
- Tests MB asked for on 21 Nov (19:36) are prepared on synthetic data: uncertainty and sensitivity analysis (runs now), coding reliability and validity (scripts, input formats and a checklist V1 to V8 in spec §10, to run once the F-cells exist). Mock dry runs of version 2 are in `data/index/mock/`, labelled MOCK.
- Cost of the index itself: none (deterministic script). Cost of the F-cells: as HANDOFF §8.
