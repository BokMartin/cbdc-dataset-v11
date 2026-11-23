# Blind agreement of MB and DS on 80 sentences (ADR-012 D8)

Sample: `data/units/AGREEMENT_SAMPLE_facet80_2026-11-22.csv` (80 dictionary hits of evidence documents, 27 projects, drawn by
`scripts/units/draw_facet_sample.py`). Each author coded alone, without a model. Labels as returned:
`data/units/FACET80_LABELS_MB_2026-11-23.csv` and `data/units/FACET80_LABELS_DS_2026-11-23.csv` (labels only, with the SHA-256
of each returned workbook). Scores: `data/units/AGREEMENT_facet80_2026-11-23.json`, computed by
`scripts/units/score_agreement.py --set facet80`. The decision rule is protocol v2 §4, fixed before coding.

## Result

Relevance is scored on the 79 units both coded (MB left one blank). Every facet is scored on the 29 units both marked R. "End
to end" also counts the 3 units only one coder marked R as facet disagreements.

| column | n | raw agreement | Krippendorff's alpha | 95 % interval (bootstrap, conditional on the sample) | Gwet's AC1 | alpha end to end (n = 32) |
|---|---|---|---|---|---|---|
| relevant | 79 | 0.949 | 0.921 | 0.838 to 0.981 | 0.926 | |
| voice | 29 | 1.000 | 1.000 | 1.000 to 1.000 | 1.000 | 0.689 |
| aspect | 29 | 0.931 | 0.920 | 0.792 to 1.000 | 0.924 | 0.819 |
| aspect2 (blank = NONE) | 29 | 0.931 | 0.903 | 0.731 to 1.000 | 0.926 | 0.786 |
| basis | 29 | 1.000 | 1.000 | 1.000 to 1.000 | 1.000 | 0.864 |
| decision | 29 | 1.000 | 1.000 | 1.000 to 1.000 | 1.000 | 0.800 |
| stance | 29 | 1.000 | 1.000 | 1.000 to 1.000 | 1.000 | 0.876 |

The unordered aspect set {aspect, aspect2} is the same for 26 of 29 units and overlaps for 27. Relevance confusion: R|R 29,
N|N 32, U|U 14, R|U 2, U|R 1, N|U 1. Aspect disagreements: DATA_PROTECTION against GENERAL once, GENERAL against ANONYMITY once.

## Decision under protocol v2 §4

Every facet is **kept**: alpha is at least 0.667 on the units both call relevant, and no category with at least 10 uses has more
disagreements than agreements. No joint review is needed; none was held, so the labels above are the blind labels.

## Limits

- 29 units relevant for both coders. That shows that no facet fails badly; it cannot certify the rare categories. On these 29
  units aspect OFFLINE, basis POLICY and decision ENDORSED were never used, decision took only CONSIDERED and NOT_APPLICABLE,
  and voice REPORTED occurs on 4 units. Protocol v2 §4 leaves certification to the reference sample.
- The intervals are bootstrap intervals over these units and say nothing about the corpus.
- The coders are the authors. Relevance agreement rose from alpha 0.456 on the development sample of 17 Nov to 0.921 here, after
  the joint adjudication of 22 Nov (ADR-011), which had read a model proposal. The authors' agreement here is therefore an upper
  bound on what an outside coder would reach, and it is not independent of that adjudication.
