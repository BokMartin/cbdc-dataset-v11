# ADR-018 (DRAFT): dispositions of audit A5 of 26 Nov 2026

Status: **draft**. Part A and Part B below are carried out on MB's choice of 26 Nov 2026, 14:41 UTC (decision card in the
project thread, option "A i B hned": the repairs that need no method decision, and new verification workbooks). Part C is
open for both authors. **DS has not confirmed anything in this record**, nor ADR-014 to ADR-017.

Report: audit A5 by a second model (astra), returned 26 Nov 2026, SHA-256
`a9df9534871adc1b70e8cbfcab38c62650a795be16031e280006e0ef93c3e67d`. It is held unchanged in the project folder
`audit-2026-11-26/` with the prompt and the brief, and registered in `docs/audits/README.md` §4 (it names per-project values
of blind projects, so it is committed when verification is locked). Verdicts: supervisor preview GO with conditions;
starting verification with the workbooks of 24 Nov NO-GO; index and hypothesis in the article NO-GO; results on the website
NO-GO; submission NO-GO. 13 findings, 5 blockers.

## What the assistant checked of the auditor's claims

Checked against the files and confirmed: finding 2 (the 414 header warnings; layer and decision authority never populated),
finding 4 (101,149 eligible units unsent; frame 119,615), finding 5 (83 keys with a value, 144 rows; the KZ supplement adds
rows, not keys), finding 6 (10 passed responses lost every claim; rejected claims 45 / 102 / 682), finding 7 (312 / 33 / 27 /
4 ranges with three, two, one, no accepted response), finding 8 (the reducer predicates, by reading the code and by tests that
fail on the code of 24 Nov), finding 11 and item 29 (the defects of the replay script), the errata to the brief (cached input
shares, pre-amendment attempts). The D2 hypothesis count (core L = 0, U = 14) matches the assistant's recomputation.

The assistant disagrees on one severity: finding 2 is **major, not blocker**. The documents concerned (about 4 legislation,
3 research and 10 government documents) were kept as evidence by the authors; classifying them is a bounded author task
(C8), after which the reducer runs again. It also proposed that verification can start after the workbook repair (Part B)
rather than after the whole of Part C; MB chose that.

## Part A. Repairs with no method decision (done 26 Nov)

| | repair | artifact |
|---|---|---|
| A1 | replay script repaired: results found in subfolders, absolute paths, exit 1 on any mismatch, differing keys listed, hash mismatch fails, step 7 asserts, upper publication count for the upper reading, D2 L and U | `scripts/audit/recompute_results.py` (the pack copy stays as audited); against `e61a562` it reproduces everything (exit 0) |
| A2 | errata to the A5 brief | `docs/audits/README.md` §4, note on A5 |
| A3 | reducer predicates follow the contract (all-rejected responses, F2 premises, F4 n.a., PET of unknown scope, `combine_models`) | `scripts/extraction/reduce_v122.py`, 6 new tests, `docs/REDUCER_REPAIR_2026-11-26.md` |
| A4 | the pages of the verification workbooks (24 and 26 Nov) enter the exposure registry; every paragraph of such a page counts as shown | `scripts/units/exposure_registry.py`, `data/units/EXPOSURE_REGISTRY_2026-11-26.csv` (1,114 blocks added) |
| A5 | incident ledger of the production runs | `docs/RUN_INCIDENTS_2026-11-26.md` |
| A6 | audit registered, state of earlier findings rewritten | `docs/audits/README.md` §4, §5 |
| A7 | request file written with LF | `scripts/pipeline/build_jobs.py` |

## Part B. New verification workbooks (done 26 Nov; amends ADR-017 point 3)

`scripts/review/build_verification_workbook_v2.py`, items `data/index/VERIFY_ITEMS_2026-11-26.csv`, hashes
`data/index/VERIFY_WORKBOOKS_2026-11-26.csv`. Built from the repaired cells. The workbooks of 24 Nov stay as the record.

- **Two passes.** Pass 1 shows the question and the places to read, no model value, status, name or quote; the author gives
  value, statuses, basis, document layer and supporting place, or "insufficient support". Pass 1 is locked by hash
  (`data/index/VERIFY_PASS1_LOCK.csv`) before pass 2 is built for that author; the script refuses otherwise. Pass 2 shows
  one row per model with its value, statuses and quote beside the author's pass-1 answer, and asks for the reason of any
  change. This amends ADR-017 point 3, which showed the model values from the start.
- **Random order** of keys (seed 20261126, recorded in the items file), instead of project by project.
- **Search sheet** for keys without a place to read: the drawn empty keys and the keys whose only value is an F3
  `none_stated` without a locator, with one neutral reason, so the sheet does not reveal which is which.
- **NO and UK** added (15 keys), flagged as development projects; their empty keys are not drawn (C6).
- **Counts:** 100 keys to read (85 in the 14 projects, 15 in NO and UK), 3 negative-search keys, 10 of 25 empty keys drawn by
  the ADR-017 rank (inclusion probability 0.4). The F4 repair gave 4 keys a value that were empty on 24 Nov, so the empty set
  shrank from 29 to 25 and one drawn key changed.

## Part C. For both authors (open)

| | question | assistant's recommendation |
|---|---|---|
| C1 | source of the headline index and hypothesis | verified cells; the D2 / strict / provisional grid only as sensitivity (no combination rule was ever decided) |
| C2 | talk combination | 2 of 3 as a rule stated after the fact, named so; weighting of the control stratum as sensitivity |
| C3 | unknown commitment status | keep the present treatment (0 at the lower bound) and describe it |
| C4 | empty keys: 10 or all 25 | all 25 |
| C5 | optional blind subset | not done; the replacement of blind coding disclosed |
| C6 | NO and UK verification and their empty keys | verify; report 16 projects and a named 14-project robustness result |
| C7 | BS and JM status diagnostic | a short check against the source |
| C8 | layer of about 17 documents (legislation, research, government) | authors classify, reducer runs again |
| C9 | rejected claims | offline diagnostic of a tolerant check as sensitivity only, no paid re-run |
| C10 | PET | map free names to the Nijsse and Pinto vocabulary; a profile, not a scale |
| C11 | registration | retrospective OSF deposit of freeze and deviations; prospective registration of the remaining steps before verification starts |
| C12 | ADR-008 (website shows no results) | keep |
| C13 | D2 source check outside the core | the 4 D2 keys, not 23 |
| C14 | DS confirmation of ADR-014 to ADR-017 and of this record | before the article |
| C15 | candidate date rule (document year or event date) | an author choice; contract §7.2 reads both ways |
