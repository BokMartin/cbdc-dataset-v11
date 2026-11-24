# Three-model agreement on the F-cells, production extraction of 23 and 24 Nov 2026 (computed 24 Nov 2026)

Measured by a deterministic script on the reducer output (`scripts/extraction/reduce_v122.py`) of the runs `PROD_EX2_claude`,
`PROD_EX2_sol62`, `PROD_EX2_deepseek` (archive `PROD_RUNS_FINAL_2026-11-24b.zip`, SHA-256 `7ae8ad8f…`; requests
`PROD_EX2/REQUESTS.jsonl`, `5590a8da…`). Aggregates only. Cells F1, F2, F3, F4, F7, F8, F9, F10. A cell "has a value" when
the reducer gives yes, no or an F3 category, at any evidence state. These are model outputs, not verified values (ADR-017).

## Requests that passed the v12.2 check (of 376)

claude-opus-5-5 338, gpt-6.2-sol 310, deepseek-v4-pro 372. A failed request supplies nothing, so the search of a project is
closed only when all its requests passed: core projects closed for Claude 4 of 16, Sol 2 of 16, DeepSeek 15 of 16 (all 42
projects: 23, 15, 38). **Much of the "no value" of Claude and Sol is a gap left by failed requests, not a finding.**

## Agreement per project-cell key

| | core 16 (128 keys) | blind 14 (112) | T3 26 (208) |
|---|---|---|---|
| all three, same value | 38 | 29 | 23 |
| all three, no value | 30 | 29 | 126 |
| same value, one model without value | 23 | 21 | 26 |
| same value, two models without value | 29 | 25 | 33 |
| all three valued, values differ | 6 | 6 | 0 |
| values differ, some without value | 2 | 2 | 0 |
| Krippendorff's alpha (value or "none" as category) | 0.52 | 0.50 | 0.54 |
| share of keys where the pair agrees: Claude–Sol / Claude–DeepSeek / Sol–DeepSeek | 0.82 / 0.66 / 0.56 | 0.81 / 0.65 / 0.55 | 0.86 / 0.81 / 0.76 |

Cells with a value in the core 16: Claude 68, Sol 55, DeepSeek 88 of 128.

Reading: the models rarely contradict each other (8 of 128 core keys have two different values; most of them are F7 and F10).
The disagreement is mostly that one model finds a value the others do not, which the failed requests above partly explain.
The alpha treats "no value" as a category and is therefore driven by coverage, not by contradictions.
