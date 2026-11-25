# ADR-010 (DRAFT, not in force): status INCLINED for documents "heavily inclined but unconfirmed", one rule for BIS Innovation Hub and wholesale projects, Brazil (21 Nov 2026)

Status: **proposal** written by the pipeline assistant from MB's answers of 21 Nov 2026, 22:29. It amends the source rule D1 (`docs/SOURCE_RULE_D1.md`) and ADR-005 (frame and evidence), so it needs MB's answers to the open points below and DS's confirmation before any row changes. No decided row has been changed.

**DS confirmed on 22 Nov 2026, relayed by MB in the project chat at 16:08 UTC** ("ano dominik je potvrdil", answering whether DS had also confirmed ADR-008 to ADR-010). What MB decided here (point A: option A1; status LEANING) is therefore in force for both authors, as narrowed by ADR-012 D5 (three classes: confirmed retail evidence; a joint retail report attributable to the project gives LEANING at most, flagged, sensitivity only; wholesale is context and PET only). Points that were still open on 21 Nov stay open unless an ADR records an answer. The file name keeps "DRAFT" so that links do not break.

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
| Split into sentence units | yes | yes (A1) | no |
| Counts in talk measures and denominators | yes | separate stratum; every result reported with and without (A1) | no |
| Can establish an F-cell commitment | yes (contract rules A to C) | no; it can set a **LEANING** value (below) | no |
| Can corroborate an F-cell | yes | yes, like `staff_research = Y` | fills `endorsement_source` / `legal_state` only |
| Tier count (T1 to T3) | yes | no | no |

**Point A, decided by MB on 21 Nov 2026, 22:32 (option A1; DS to confirm):** INCLINED documents are split into units and labelled, but every result is reported with and without them as a separate stratum, so the main measures keep the evidence base the authors have confirmed. Rejected alternatives: (A2) count fully, like BORDERLINE; (A3) cited only, like companions.

Reason for A1: the paper can then show what the confirmed evidence says and how much the inclined documents add, without a reviewer being able to say the base was widened after the fact. It costs translation and units for the INCLINED documents that are not in English.

## Cell status LEANING (MB, 21 Nov 2026, 22:33; proposal for the contract)

MB: where a country has no confirmation from the policy maker itself, the project should still get a "leaning" based on the INCLINED documents that do not come directly from the policy maker.

Proposed rule:

1. **LEANING** is a cell status of its own, below every status the policy maker's own documents can give (contract v12 status axis). It records what an INCLINED document says about a cell; it is never a commitment.
2. It is set only when no KEEP or BORDERLINE document of the competent body yields a value for that cell. A value from the policy maker's own documents always replaces it; a conflict between the two is listed, not resolved in favour of the leaning.
3. It needs a located verbatim quote under the same rules A to C as any claim (no inference from silence); the claim record carries `source_status = INCLINED` and the cell `decision_status = leaning`, the field the index script of PR 2 reads (`is_leaning()` in `scripts/derive_index.py`).
4. Results and the website show it with its own label. Every cell count, table and figure of the commitment layer is reported twice: confirmed only, and confirmed plus LEANING, consistent with point A.

### Consequence for the privacy index (PR 2, ADR-009)

The index needs one more status level. Proposal for that thread: in the main index a LEANING cell is treated as unconfirmed, so it enters the interval only as one bound (the lower and upper bounds as if the cell were missing, with the leaning value marked inside the interval); a second variant scores LEANING cells at their value and is reported next to the main one as a sensitivity result. A project whose index rests mainly on LEANING cells is flagged. The decision belongs to the index thread and to MB and DS.

## Rows this would change (`data/manifest/PROPOSED_INCLINED_2026-11-21.csv`, 38 rows, plus candidates)

| Group | Rows | Now | Proposed | Author yes needed |
|---|---|---|---|---|
| 1 BoE and MIT report | 1 | dropped (model) | INCLINED | no, MB decided |
| 2 Switzerland | Tourbillon (candidate NP-CH-01) | not held | INCLINED | no, MB decided |
| 2 Switzerland | Helvetia I and II | evidence (author) | INCLINED or stays evidence | **yes, open point B** |
| 3 Wholesale, model flag | 25 (incl. 6 SNB Helvetia pages) | wholesale (model) | INCLINED | no, MB decided the rule; per-row check suggested, several are press releases that may be companions |
| 3 Wholesale, author evidence | 9 (Khokha 1 and 2, Jasper I-II and III, Acacia, Garuda x3, BCL DCB prototype) | evidence (author) | INCLINED or stays evidence | **yes, open point B** |
| 4 Brazil | BR_Brazil_2023; NP-BR-01, NP-BR-02 | outside frame | no change: Brazil stays out (MB, 23:52) | decided |

**Point B, decided by MB on 21 Nov 2026, 23:54** ("the 11 wholesale documents as the additional layer, leaning sources that can support"): the 11 move to INCLINED. Applied together with groups 1 to 3 in `data/manifest/AUTHOR_DECISIONS_2026-11-21.csv` (38 rows: 25 WHOLESALE, 5 KEEP, 6 BORDERLINE, 1 DROP, 1 candidate) and `TIERS_2026-11-21.csv`. Original wording of the question: "same treatment" either moves the 11 wholesale and BIS Innovation Hub documents the authors already decided as evidence down to INCLINED (one rule for all of them, recommended for consistency), or keeps them as evidence and lifts only the model-flagged rows to INCLINED.

**Point C, decided by MB on 21 Nov 2026, 23:52: Brazil stays out of the frame** ("brazilii tedy vynechejme"). BR_Brazil_2023 stays as it is (outside the frame); NP-BR-01 and NP-BR-02 are references only, not corpus candidates. The two files were saved to `CBDC_MASTER_v12/BR/` for reference (SHA-256 in the candidates file). Background: Held: one BCB document (2023 press-conference deck on the pilot, evidence by author, borderline, no English text). Dropbox has no other BCB document (searched 21 Nov; only an HRF tracker page, not eligible). With the two candidates Brazil would be a T3 project with 1 to 3 documents. Adding it changes the frame of 44 projects (ADR-005 §1), the project status table (status NONE now) and the website.

## Consequences if adopted

- `docs/SOURCE_RULE_D1.md`: add INCLINED after rule 5 and amend rule 1 ("BIS ... never are") for joint reports in which the competent central bank takes part.
- ADR-005 §9-10 (evidence) for the new status.
- New `AUTHOR_DECISIONS_<date>.csv` rows for every changed document; TIERS and site data rebuilt; `PROJECT_BRIEF.md` numbers updated.
- Corpus freeze moves: INCLINED documents need text, translation (T1 and T2 rule of ADR-007 applies) and units before calibration.
- DS confirms.

## Applied on 21 Nov 2026 (MB as author; DS to confirm)

- `TIERS_2026-11-21.csv` supersedes `TIERS_2026-11-17.csv`: 776 rows = 772 + 4 documents found through the Nijsse and Pinto check (NP-EU-01, NP-EU-02, NP-JP-01 as CANDIDATE; NP-CH-01 Tourbillon as INCLINED). Brazil's two files are in the master folder for reference only (`MASTER_MANIFEST_2026-11-21.csv`, 783 files).
- Evidence publications in the frame: 229 -> 218. Projects affected: AU 6->5, CA 6->4, CH 4->2, EU 15->14, ID 4->1, ZA 4->2.
- **Tiers (MB, 22 Nov 2026, 00:05; DS to confirm): moving a document to INCLINED does not lower a project's tier.** Tiers stay as of 17 Nov (`TIERS_2026-11-17.csv`). Counted without INCLINED, Canada would have 4 evidence publications instead of 6 (Jasper I-II and Jasper III moved) and fall from T2 to T3; MB decided that Canada stays T2. No tier changes upward either.
- Bank of Canada documents of its own on retail CBDC that are companion or dropped, mostly on a model proposal, for the authors to review (they would raise Canada's evidence count if accepted): CAND-040 *Privacy in CBDC technology* (Staff Analytical Note 2020-9, companion, model), CAND-042 *Archetypes for a retail CBDC* (SAN 2022-14, companion, model), CAND-044 *A Digital Canadian Dollar: what we heard 2020-23* (dropped, author), CA_BoC_2017 (SDP 2017-16, dropped), CA_BoC_PublicMoney_SDP2024_11 (dropped).
- Units of the INCLINED documents are kept; the pipeline has to mark them as a separate stratum before any run (open engineering, not yet built).
- Website: new categories "Inclined" and "Candidate".
