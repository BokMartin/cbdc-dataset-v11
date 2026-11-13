# Human coding of privacy statements: protocol v2 (13 Nov 2026, after the independent audit)

Replaces the protocol of the same morning, which was withdrawn before any unit was coded (ADR-005). Written and committed before either coder opens a workbook and before any model classifies a unit.

## 1. Two samples with different jobs

| | development sample | reference sample |
|---|---|---|
| purpose | find out which facets two people can code consistently; revise codebook and prompts | measure agreement of the frozen codebook; reference for the model |
| size | 120 units: D 90, N 15, R 15; route A 84, B 11, D 25 | 400 units: D 260, N 80, R 60; route A 292, B 30, D 78 |
| drawn | now, from the evidence set as it stands (`data/units/AGREEMENT_SAMPLE_dev_2026-11-13.csv`) | after the document set and the codebook are frozen; never contains a development unit |
| may be used to tune the model | yes | no |
| coded | both authors, alone, all facets | both authors, alone, the facets that survived |

Draw: `scripts/units/draw_agreement_sample.py --design dev|main` (quotas, round robin over projects, cap per document, seeds in the script).

## 2. What the coder sees

The unit, its paragraph with the unit marked (`scripts/units/context.py`; the model receives the same string), the document's issuer, kind and year, and whether the text is an English original, the issuer's English edition or a machine translation. Codebook: `docs/TALK_CODEBOOK_cs.tsv` v0.3 (Czech explanations, English values), aligned with `pipeline/prompts/talk_L1_relevance.system.md` v0.2 and `talk_L2_facets.system.md` v0.3 and with the contract's rules A (endorsement needs the competent body) and B (decision and implementation are separate axes).

## 3. Scoring (`scripts/units/score_agreement.py`, tested in `tests/test_score_agreement.py`)

Per column: units, raw agreement, Krippendorff's alpha (nominal; reported as undefined when all ratings fall in one category), Gwet's AC1 on the declared category list, counts per category and the confusion table. Relevance on all units; each facet on the units both coders call relevant, and also end to end, where a unit only one coder calls relevant counts as a facet disagreement. Intervals are bootstrap intervals over the units of the sample and are conditional on it: the sample over-represents dictionary hits and translated text by design and says nothing about prevalence in the corpus.

## 4. Decision rule after the development sample

Fixed now, applied to the development result, then frozen for the reference sample.

- A facet is **kept** if alpha ≥ 0.667 on the units both call relevant and no category with at least 10 uses has more disagreements than agreements in the confusion table.
- A facet below that is **repaired once**: categories that are confused with each other are merged by a written rule, or the codebook text is changed; the facet is then re-scored on the same development units as a check of the rule, not as evidence.
- A facet that cannot be repaired is **dropped** from measurement. Relevance, voice and aspect are the minimum instrument; if one of these three fails, the unit-based instrument is not used for the paper and the result is reported.
- With about 90 dictionary hits, roughly 40 to 70 units will be relevant for both coders. That is enough to see which facets fail badly and which categories are confused; it is not enough to certify a facet with rare categories. The reference sample does that.

Thresholds are conventions (Krippendorff 2004; to pass the citation check), not proofs of validity. Both rounds are published whatever they show.

## 5. Limits

The coders are the authors and know the projects; their agreement does not show what an outside coder would reach. Coding shows them source sentences of projects for which they later code F-cells; no model output is shown, and the exposure is logged per unit in the sample file. The development sample is drawn before 153 evidence documents are confirmed by the authors; it tests the codebook, not the corpus.
