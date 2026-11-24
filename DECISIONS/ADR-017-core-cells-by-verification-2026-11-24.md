# ADR-017: core F-cells by source verification of model citations instead of blind coding (24 Nov 2026)

Status: **adopted by MB**, 24 Nov 2026. His words in the project thread, 14:54 UTC: "tohle asi ručně dělat nebudeme, celý ten
princip je, že se tohle udělá strojově ... to co můžeme udělat je že se veme vzorek vybraných paragrafů na které se odkazují se
specifickým závěrem k F1-12 a ověříme, že je to pravda a zda s tím souhlasíme nebo ne ... pročítat nekonečné dokumenty a v tom
hledat jiný paragraf kde by to bylo stated dělat nebude, to je navíc mnohem víc human error proned nez strojově". On a card at
15:01 UTC he chose the variant "every value-bearing cell, plus 10 empty cells" (point 2 below). **DS has not confirmed.**

## Why

Blind coding of the 14 blind core projects from the sources (ADR-012 D1, D2) means 106 evidence documents with 3,739 pages;
even with a page finder about 1,600 pages per author (workbooks of 24 Nov, `scripts/review/build_blind_cell_workbook.py`).
MB judged that manual search of long documents is more error-prone than the machine search it was meant to check.

## Decision

1. **Replaces** for the 14 blind core projects (AU, BS, CA, EU, HK, IL, IN, JM, JP, KZ, NZ, RU, SE, TW): ADR-012 D1 and D2 in
   the part "both authors code every cell from the sources before any model output is opened"; ADR-016 §4 in the part
   "until both authors have locked their blind F-cell coding"; Registration A draft §1 (inter-coder agreement on the 14
   projects) and §2 "Source of cells" and sensitivity variant 5 (index from blind-coded cells only). The blind workbooks of
   24 Nov are not used; they stay as a record.
2. **What is verified.** Cells F1, F2, F3, F4, F7, F8, F9, F10 (the cells of the index and of F3 beside it). For each of the
   112 project-cell keys, the reducer (`scripts/extraction/reduce_v122.py`) gives each model's cell. A key is a
   **verification item** when at least one of the three models gives it a value (yes / no, or an F3 category), at any
   evidence state, including conflict. Every item is verified; there is no sample. In addition, **10 empty keys** (no model
   gives a value) are checked: the 10 with the lowest rank in `data/index/VERIFY_EMPTY_RANK_2026-11-24.csv` (rank by
   SHA-256 of `verify-empty-2026-11-24|project|cell`, fixed and committed before any output is opened). Their inclusion
   probability, 10 / number of empty keys, is stored with them.
3. **What the authors fill in**, each alone: for a verification item, with the page, quote, value and status of each model
   shown: does the quote carry the conclusion (yes / partly / no), is the decision and implementation status right, do they
   agree with the value; if not, the value they read on the cited page or elsewhere in the same document. For an empty key,
   with the document list of the project: is there a value the models missed (with page and quote), or does it stay unknown.
   A limit of time per empty key may be set by the authors.
4. **Disagreements.** Between MB and DS: a joint pass over the source; unresolved stays undetermined and widens the interval.
   Between the authors and the models: the authors' joint value stands, with provenance `model+human`.
5. **What it measures.** Verification measures **precision** of what the models found. It does not measure what they
   missed. Recall is bounded by the agreement of three independent models, by the known cases (UK, NO), and by the 10 empty
   keys, reported as a rate with its interval. Agreement between MB and DS on the verification items is reported.
6. **Paper.** Stated as a deviation from the plan: in the core, cell values were extracted by three models and each
   value-bearing cell was verified against the cited source by both authors independently; blind coding from the sources
   was planned and dropped (this ADR, with its date).
7. **Opening the production outputs of the 14 projects** is allowed once this ADR is merged to `main`. ADR-016 §4 also
   requires the reference sample of 400 talk units to be coded first; that condition is **not changed here**. Open for MB:
   code the reference sample first, or open now and exclude from the reference sample every paragraph shown in
   verification (as for the exposure registry, Registration A §4a).

## Open

- MB wrote "F1-12". Asked whether F11 and F12 are also verified, he answered on 24 Nov 2026, 17:35 UTC: "jen 8" (only the
  eight cells of point 2). Settled.
- MB confirmed the merge of this ADR on 24 Nov 2026, 17:35 UTC ("ano slouci").
- DS has not confirmed. The order of the reference sample and the opening (point 7) is still open, so the outputs of the 14
  projects stay closed until MB chooses.

## Opening (24 Nov 2026)

MB, 17:44 UTC, on the question of point 7: "otevrit hned" (option A): the outputs are opened now and every paragraph shown
in verification is excluded from the reference sample of 400 units when it is drawn (added to the exposure registry,
Registration A §4a). Opened by CL at about 17:50 UTC from `PROD_RUNS_FINAL_2026-11-24b.zip` (SHA-256 `7ae8ad8f…`), with the
requests `PROD_EX2/REQUESTS.jsonl` rebuilt from the frozen inputs (SHA-256 `5590a8da…`, identical to amendment 1 of the
freeze). Verification items: 83 keys with a value, 142 rows; 29 empty keys, 10 drawn (inclusion probability 10/29)
(`data/index/VERIFY_ITEMS_2026-11-24.csv`, `scripts/review/build_verification_workbook.py`). Three-model agreement on the
cells: `docs/EXTRACTION_AGREEMENT_2026-11-24.md`.

After the re-run of failed requests (archive `PROD_RUNS_FINAL_2026-11-24c.zip`, `c23bb74d…`) two rows were added (`KZ-F3-2n`, `KZ-F4-2n`, supplement workbooks `VERIFY_CELLS_{MB,DS}_2026-11-24_DOPLNEK.xlsx`); no row disappeared and the drawn empty keys are unchanged.
