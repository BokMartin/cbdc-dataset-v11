# ADR-011: joint adjudication of the authors' disagreements on relevance and on the translation benchmark (22 Nov 2026)

Status: **decided by MB and DS jointly on 22 Nov 2026**, reported by MB in the project thread (11:06 and 11:31 UTC). Recorded by the pipeline assistant. The blind labels and judgements are not changed; the joint answers are stored apart from them. Basis: HANDOFF §4 (workbook `NESHODY_MB_DS_2026-11-17.xlsx`), ADR-007 §6.

## 1. What was decided

**Relevance, 41 development units** where the blind labels of MB and DS differ or one is missing: a joint label for every unit, U 17, N 13, R 11 after one revision of 22 Nov (§5.4; before it U 17, N 12, R 12) (`data/units/DEV_ADJUDICATED_RELEVANCE_MB_DS_2026-11-22.csv`). 36 rows from the authors' answers in the returned workbook, 5 settled by MB in words the same day (`data/units/DEV_ADJUDICATION_CLARIFICATIONS_2026-11-22.csv`). For reason B the file keeps the rule sentence the authors accepted (or, in one case, rejected); these sentences are the input for the codebook repair.

**Translation benchmark, 35 pairs** where the two judges' codes differ: a joint code for every pair, S 24, D 5, M 2, W 2, X 2 (`data/translation/benchmark/JUDGEMENT_ADJUDICATED_MB_DS_2026-11-22.csv`); every pair checked against the registered key by hash.

## 2. Rule for judging translation (MB for MB and DS, 22 Nov, 11:31 UTC)

> "Obecně chceme ne tak přísné rozdíly v překladu. Pouze pokud se tam změní klíčové slovo které udává váhu statementu (could na will atd.) a nebo pokud je špatně spárovaný úsek."

Reading: a pair is S unless a word that sets the force of the statement changes (modality such as could, may, will, must, should; this gives W or X) or the meaning otherwise changes materially (M), or the two segments are mispaired or cut (D). Synonyms and paraphrase of the same content (privacy and data protection, register and ledger, due diligence and checks) are S. The 35 joint codes follow this rule.

The 51 pairs on which the judges had agreed were re-read by MB and DS under this rule; none changed (MB, 22 Nov, 11:36 UTC). Whether the rule governs future judging is proposed in `docs/TRANSLATION_PROCEDURE.md` (section "Joint adjudication") and waits for the authors' confirmation.

## 3. Notes for the prompts (MB, 22 Nov)

- Chapter titles of an outline or table of contents are not relevant; the chapters themselves can be (Madagascar RFI).
- The unit plus its paragraph can miss the key sentence of a passage (e-MOP: managed anonymity); a note for the extraction design.

## 4. What these results are and are not

The workbook was pre-filled on 19 Nov with an AI proposal (gpt-6-astra according to MB); the authors went through every row by hand and decided themselves (`EXPOSURE_LEDGER.md`, 22 Nov). The joint answers are an adjudication, not an independent coding: they repair the codebook and the judging rule and are never reported as agreement or validation. The development units stay out of the reference sample.

## 5. Repair of the codebook and the relevance prompt (proposal, 22 Nov)

Codebook v0.4 DRAFT (`docs/TALK_CODEBOOK_cs.tsv`) and relevance prompt v0.3 DRAFT (`pipeline/prompts/talk_L1_relevance.system.md`) carry the accepted rule sentences of §1 and the notes of §3. Proposal of the pipeline assistant until the authors confirm it. Points where the joint labels and the rules do not fit together, for the authors:

1. **Headings.** v0.3 coded a heading that names the topic as N; the joint labels give U to stand-alone headings, captions, abbreviations and bibliographic fragments, but N to the Madagascar outline. Proposed: outline and table-of-contents entries N, stand-alone headings in running text U. **Agreed by MB, 22 Nov, 11:45 UTC.**
2. **Thailand, accounting sentence with the AML/CFT heading of the next section stuck to it.** Joint label R, while the accepted rule says a stuck heading does not change how a complete sentence is judged (the proposal keeps the rule). Either the unit is an exception or the authors state what makes it R. MB, 22 Nov, 11:50 UTC, after reading the unit and its paragraph: R, the unit as marked is relevant to privacy in the CBDC solution. Consequence: the heading of the next section is read as part of the unit; the codebook and prompt say so, and the rule "a stuck heading does not change relevance" is dropped.
3. **Russia 2020, a digital rouble with a unique number like a banknote.** Joint label R; the proposed rule "a unique identifier without a statement on tracing is not enough" was rejected, but no replacement sentence was given. MB, 22 Nov, 11:45 UTC: R is clear from the context of the document. Note: coders and models see only the paragraph (prompt rule 5: text only), so a unit that is relevant only from the wider document will not be found relevant by the instrument; this unit stays R as an adjudicated label and no general rule is added.
4. **Scope.** The accepted rules count AML/CFT measures, confidentiality of the system and technical limits on data access as relevant even without the word privacy, including in a wholesale prototype (Jasper) and a payment pilot (Hungary). v0.3 says privacy of wholesale participants is N. Proposed: keep wholesale participants N unless the unit is about data of end users. MB, 22 Nov, 11:50 UTC, after reading the Jasper unit: **N**. This revises the joint label of `CA_CA_Jasper_Phase12_2017:p22:s938` from R to N (`data/units/DEV_ADJUDICATION_REVISIONS_2026-11-22.csv`); the codebook and prompt limit the technical-mechanism rule to end users' data.
