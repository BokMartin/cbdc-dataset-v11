# ADR-004 — Unit-based privacy-talk instrument (12 Nov 2026)

**Status:** accepted in principle by MB on 12 Nov 2026 ("souhlasím s tvým feedbackem"); DS to confirm; prompts and thresholds are drafts until locked. **Related:** `docs/PRIVACY_TALK_INSTRUMENT_PROPOSAL_2026-11-12.md`, contract §6b, decisions of 9 Nov 2026 on the Talk and Commitment indices.

## Context
The statement survey of 2 Nov lets the model write quotes and choose its own units: 16 % of quotes are not located, recall is unknown, no agreement coefficient can be computed, and OTHER is the largest type. The deterministic pilot of 12 Nov shows that only 16-19 % of the variance of document-level privacy salience lies between projects and that a share-based project score reaches a split-half reliability of 0.49 (4+ documents) and 0.73 (8+ documents); count-based scores follow publication volume.

## Decision
1. Privacy talk is measured on fixed sentence units produced before any model run (`scripts/units/unitise.py`), with a published dictionary layer (L0), a closed relevance classification (L1) on dictionary hits, their neighbours and a random 5 % control sample for recall (`scripts/units/select_candidates.py`), and facet coding of relevant units (L2). Models return unit ids and labels only.
2. The 17 survey types are replaced by facets (voice, object, observer, direction, basis, status, modality) with a crosswalk (`schema/talk_units_v13_DRAFT.json`).
3. The main result is the funnel from sentences to admissible F-commitments; the difference Talk − Commitment is secondary.
4. No count-based index. Project-level talk scores are published only with reliability and interval and only above a threshold fixed in the registration; yearly series only as pooled windows or document points. This narrows the 9 Nov decision on yearly graphs for T1/T2.
5. Every talk component is reported by issuer type (central bank, government, legislature), so that the regulator's own voice is separated from reported opinions (facet voice) and from other institutions (document metadata).

## Open
- Human reliability sample: who codes and how many units (proposal: MB and DS, 400 units, stratified by tier, kind and text route).
- The issuing institution is not recorded for the 111 registry documents among the 250 unitised (their `issuer` field holds the acquisition batch); it must be recorded before any analysis by issuer type.
- 28 evidence documents have no usable English text yet (`data/units/UNITS_NOT_UNITISED_2026-11-12.csv`).
- Encoder stratum for candidate selection; acceptance thresholds (alpha, recall, reliability); registration text.

## State on 12 Nov 2026
250 documents of 42 projects unitised into 149 067 units; 20 607 fragments and boilerplate units excluded; 18 144 units selected for L1 (6 941 dictionary hits, 5 393 neighbours, 5 810 random controls). Prompts L1 and L2 are v0.1 drafts and have not been run.
