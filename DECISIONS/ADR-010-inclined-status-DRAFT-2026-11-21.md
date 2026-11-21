# ADR-010 (DRAFT, not in force): status INCLINED for documents "heavily inclined but unconfirmed", one rule for BIS Innovation Hub and wholesale projects, Brazil (21 Nov 2026)

Status: **proposal** written by the pipeline assistant from MB's answers of 21 Nov 2026, 22:29. It amends the source rule D1 (`docs/SOURCE_RULE_D1.md`) and ADR-005 (frame and evidence), so it needs MB's answers to the open points below and DS's confirmation before any row changes. No decided row has been changed.

## What MB said (21 Nov 2026, answers to the four questions of the Nijsse and Pinto check)

1. BoE and MIT, *Enhancing the privacy of a digital pound* (dropped on a model proposal): not to stay out; "kept in as heavily inclined but unconfirmed".
2. Project Tourbillon (BIS Innovation Hub) and Project Helvetia (BIS Innovation Hub reports held as evidence): "same treatment".
3. Wholesale experiments such as Khokha: "same treatment ... implies future use in retail".
4. Brazil: keep it if we have the documents.
5. Countries in Table 2 of the paper without a cited official document: rely on what our extraction finds (no change).

## Proposed definition

**INCLINED** is a document decision next to KEEP, BORDERLINE, COMPANION, DROP and WHOLESALE. It marks an official document that the authors lean towards counting but have not confirmed as evidence of the project's retail design, because it is (a) a joint or hosted report of a body outside rule D1 in which the competent central bank takes part (BIS Innovation Hub centres, joint reports with universities), or (b) about a wholesale or experimental arrangement of the competent body that may carry over to retail.

| | KEEP / BORDERLINE (evidence) | INCLINED (proposed) | COMPANION |
|---|---|---|---|
| Listed and cited on the website | yes | yes, with its own label | yes |
| Split into sentence units | yes | **open point A** | no |
| Counts in talk measures and denominators | yes | **open point A** | no |
| Can establish an F-cell commitment | yes (contract rules A to C) | no | no |
| Can corroborate an F-cell | yes | yes, like `staff_research = Y` | fills `endorsement_source` / `legal_state` only |
| Tier count (T1 to T3) | yes | no | no |

**Open point A** (decision for MB): either (A1, recommended) INCLINED documents are split into units and labelled, but every result is reported with and without them as a separate stratum, so the main measures keep the evidence base the authors have confirmed; or (A2) they count fully, like BORDERLINE; or (A3) they are cited only, like companions.

Reason for A1: the paper can then show what the confirmed evidence says and how much the inclined documents add, without a reviewer being able to say the base was widened after the fact. It costs translation and units for the INCLINED documents that are not in English.

## Rows this would change (`data/manifest/PROPOSED_INCLINED_2026-11-21.csv`, 38 rows, plus candidates)

| Group | Rows | Now | Proposed | Author yes needed |
|---|---|---|---|---|
| 1 BoE and MIT report | 1 | dropped (model) | INCLINED | no, MB decided |
| 2 Switzerland | Tourbillon (candidate NP-CH-01) | not held | INCLINED | no, MB decided |
| 2 Switzerland | Helvetia I and II | evidence (author) | INCLINED or stays evidence | **yes, open point B** |
| 3 Wholesale, model flag | 25 (incl. 6 SNB Helvetia pages) | wholesale (model) | INCLINED | no, MB decided the rule; per-row check suggested, several are press releases that may be companions |
| 3 Wholesale, author evidence | 9 (Khokha 1 and 2, Jasper I-II and III, Acacia, Garuda x3, BCL DCB prototype) | evidence (author) | INCLINED or stays evidence | **yes, open point B** |
| 4 Brazil | BR_Brazil_2023 plus candidates NP-BR-01 (Drex pilot report phase 1) and NP-BR-02 (Gomes speech) | outside frame | BR enters the frame as project 45 | **yes, open point C** |

**Open point B**: "same treatment" either moves the 11 wholesale and BIS Innovation Hub documents the authors already decided as evidence down to INCLINED (one rule for all of them, recommended for consistency), or keeps them as evidence and lifts only the model-flagged rows to INCLINED.

**Open point C**: Brazil. Held: one BCB document (2023 press-conference deck on the pilot, evidence by author, borderline, no English text). Dropbox has no other BCB document (searched 21 Nov; only an HRF tracker page, not eligible). With the two candidates Brazil would be a T3 project with 1 to 3 documents. Adding it changes the frame of 44 projects (ADR-005 §1), the project status table (status NONE now) and the website.

## Consequences if adopted

- `docs/SOURCE_RULE_D1.md`: add INCLINED after rule 5 and amend rule 1 ("BIS ... never are") for joint reports in which the competent central bank takes part.
- ADR-005 §1 (frame) if Brazil enters; ADR-005 §9-10 (evidence) for the new status.
- New `AUTHOR_DECISIONS_<date>.csv` rows for every changed document; TIERS and site data rebuilt; `PROJECT_BRIEF.md` numbers updated.
- Corpus freeze moves: INCLINED documents need text, translation (T1 and T2 rule of ADR-007 applies) and units before calibration.
- DS confirms.
