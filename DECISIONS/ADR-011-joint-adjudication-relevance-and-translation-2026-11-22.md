# ADR-011: joint adjudication of the authors' disagreements on relevance and on the translation benchmark (22 Nov 2026)

Status: **decided by MB and DS jointly on 22 Nov 2026**, reported by MB in the project thread (11:06 and 11:31 UTC). Recorded by the pipeline assistant. The blind labels and judgements are not changed; the joint answers are stored apart from them. Basis: HANDOFF §4 (workbook `NESHODY_MB_DS_2026-11-17.xlsx`), ADR-007 §6.

## 1. What was decided

**Relevance, 41 development units** where the blind labels of MB and DS differ or one is missing: a joint label for every unit, U 17, N 12, R 12 (`data/units/DEV_ADJUDICATED_RELEVANCE_MB_DS_2026-11-22.csv`). 36 rows from the authors' answers in the returned workbook, 5 settled by MB in words the same day (`data/units/DEV_ADJUDICATION_CLARIFICATIONS_2026-11-22.csv`). For reason B the file keeps the rule sentence the authors accepted (or, in one case, rejected); these sentences are the input for the codebook repair.

**Translation benchmark, 35 pairs** where the two judges' codes differ: a joint code for every pair, S 24, D 5, M 2, W 2, X 2 (`data/translation/benchmark/JUDGEMENT_ADJUDICATED_MB_DS_2026-11-22.csv`); every pair checked against the registered key by hash.

## 2. Rule for judging translation (MB for MB and DS, 22 Nov, 11:31 UTC)

> "Obecně chceme ne tak přísné rozdíly v překladu. Pouze pokud se tam změní klíčové slovo které udává váhu statementu (could na will atd.) a nebo pokud je špatně spárovaný úsek."

Reading: a pair is S unless a word that sets the force of the statement changes (modality such as could, may, will, must, should; this gives W or X) or the meaning otherwise changes materially (M), or the two segments are mispaired or cut (D). Synonyms and paraphrase of the same content (privacy and data protection, register and ledger, due diligence and checks) are S. The 35 joint codes follow this rule.

Not yet applied: `docs/TRANSLATION_PROCEDURE.md` and the instructions of the judgement workbook still carry the stricter reading of 11 Nov. Whether the rule is written into them, and whether the 51 pairs on which the judges agreed are re-read under it, is open for the authors.

## 3. Notes for the prompts (MB, 22 Nov)

- Chapter titles of an outline or table of contents are not relevant; the chapters themselves can be (Madagascar RFI).
- The unit plus its paragraph can miss the key sentence of a passage (e-MOP: managed anonymity); a note for the extraction design.

## 4. What these results are and are not

The workbook was pre-filled on 19 Nov with an AI proposal (gpt-6-astra according to MB); the authors went through every row by hand and decided themselves (`EXPOSURE_LEDGER.md`, 22 Nov). The joint answers are an adjudication, not an independent coding: they repair the codebook and the judging rule and are never reported as agreement or validation. The development units stay out of the reference sample.
