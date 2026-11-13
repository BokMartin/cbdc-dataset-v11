# Human agreement on the privacy-talk codebook: protocol (13 Nov 2026)

Status: written and committed before either coder has coded a unit and before any model has classified a unit. The thresholds in section 4 are a proposal by the pipeline author; MB and DS confirm or change them before they open the sheet CODE, and the change is recorded here with a date.

## 1. Purpose

The unit-based instrument (ADR-004, `docs/PRIVACY_TALK_INSTRUMENT_PROPOSAL_2026-11-12.md`) labels sentence units with a relevance decision and six facets. Before a model is used for measurement, the paper needs to show that two humans applying the written codebook reach the same labels. The human labels are also the reference against which the model is later compared. A facet that humans cannot code consistently is merged or dropped; it is not handed to a model.

## 2. Sample

Drawn by `scripts/units/draw_agreement_sample.py` (seed `talk-v13-agreement-2026-11-13`) from the 18 952 candidate units of the 250 unitised evidence documents (`data/units/CANDIDATES_2026-11-13.csv`); unit ids, strata and text hashes are in `data/units/AGREEMENT_SAMPLE_2026-11-13.csv`.

| set | units | composition |
|---|---|---|
| training | 30 | exposed projects only (NO, UK): 20 dictionary hits, 5 neighbours, 5 random controls |
| main | 400 | 260 dictionary hits (D), 80 neighbours (N), 60 random controls (R); 292 English originals, 30 issuer English editions, 78 machine translations; 201 T1, 140 T2, 59 T3; 42 projects, 151 documents, at most 4 units per document and stratum, projects take turns |

Dictionary hits are over-sampled because facets can only be compared on units both coders find relevant. Route B and D text is over-sampled so that agreement can be reported separately for translated text. The sample is not proportional to the corpus, so its marginal shares say nothing about prevalence; prevalence comes from the full classification, weighted by stratum.

The sample was drawn from all evidence documents as pre-filled on 13 Nov. If the authors later drop a document, its units stay in the agreement sample: agreement is a property of the codebook, not of the final document set.

## 3. Procedure

1. Both coders read the codebook (sheet CODEBOOK; source `docs/TALK_CODEBOOK_cs.tsv`, values in English).
2. Training: each codes the 30 training units alone, then they compare and discuss. Changes to the codebook are written down and committed before step 3. Training units are not scored.
3. Main: each codes the 400 units alone, in the row order of his own workbook (the order differs between coders), without discussion and without a language model. The document's issuer, kind and year and the neighbouring units are shown as context.
4. The two workbooks are scored by `scripts/units/score_agreement.py`. Only after that are disagreements discussed, and only then is a model run on the same units.
5. Model comparison (later): each model's labels against each coder and against the units where both coders agree; test-retest of each model.

## 4. What is reported and the thresholds (proposal)

Per column: number of units, raw agreement, Krippendorff's alpha (nominal) with a bootstrap 95 % interval; for relevance also Gwet's AC1, because alpha is unstable when one category is rare. Relevance is scored on all 400 units, each facet on the units both coders marked relevant (that number is reported). Relevance and aspect are also reported by candidate stratum and by text route.

- alpha ≥ 0.80: the column is used as coded.
- 0.667 ≤ alpha < 0.80: used, reported as tentative, and its categories are checked for a merge that raises agreement.
- alpha < 0.667: the column is not used for measurement in this form. Either categories are merged by a rule written before re-scoring, or the column is dropped. One revision round with a fresh sample of 150 units is allowed; the first-round result is reported in any case.
- If fewer than 120 units are relevant for both coders, facet intervals will be wide; a top-up sample of dictionary hits is then drawn with a new seed, and both rounds are reported.

Conventional reference for the cut-offs: Krippendorff (2004), to be confirmed in the citation check.

## 5. Limits

Two coders who are the paper's authors and who know the projects are not naive coders; agreement between them is an upper bound on what an outside coder would reach. The codebook is in Czech with English values; the units are English. Some units are fragments of tables or headings: they are part of what the instrument meets in practice and are kept.
