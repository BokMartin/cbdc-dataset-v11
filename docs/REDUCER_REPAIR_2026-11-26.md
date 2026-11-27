# Reducer repair of 26 Nov 2026 and what it changes

Audit A5 (report held with its SHA-256 in `docs/audits/README.md` §4) found that several predicates of
`scripts/extraction/reduce_v122.py` did not do what the measurement contract and the ADRs say (finding 6, finding 8, finding
10, item 8). These repairs follow the existing rules; none of them is a new rule. MB chose on 26 Nov 2026 (decision card,
option "A i B hned") that the repairs needing no method decision are made. Each has a test that fails on the code of 24 Nov
(`tests/test_extraction_v122.py`).

| repair | rule it follows | test |
|---|---|---|
| A passed response whose every emitted claim the check rejected does not cover its pages, so it cannot close a negative search | prompt §6 ("a failed request supplies nothing"); rule SEARCH_F3 needs a completed search | `test_all_claims_rejected_response_does_not_close_the_search` |
| F2 premises pass the rejected/superseded filter and need a participant, a transaction scope and a design label | contract §7.3 (same participant, scope and design label); rejected or superseded never sets a value | `test_f2_premises_rejected_superseded_or_without_keys_are_not_used` |
| F4 is n.a. only for an adopted exclusion of offline (endorsed or operational); a considered exclusion keeps its value and status | contract rule F: n.a. "for a project that endorsed no offline" | `test_offline_exclusion_only_considered_keeps_its_value` |
| PET of unknown scope, or of retail scope in a document of unknown or companion layer, is withheld in its own table | reducer step 2: "unknown layer or scope withheld" | `test_pet_of_unknown_scope_is_withheld` |
| `combine_models()` needs exactly the three expected models and a non-blank quote with a document and a page | ADR-012 D2: same value, documented, with a quote | `test_combine_models_needs_the_three_models_and_a_located_non_blank_quote` |

Known and **not** changed (an author decision, agenda of ADR-018): the candidate date is the later of the document year and
the event date. Contract §7.2 says both "the newest claim" and "a newer document wins", so the choice is not mechanical.

## What changes in the production cells

Recomputed offline on 26 Nov with `scripts/audit/recompute_results.py` against the frozen archive. Run against the snapshot
of main `e61a562` the script reproduces every result of 24 Nov (exit 0). Run against the repaired code it lists the keys that
change (exit 1 by design). The per-project list is in the project folder (`audit-2026-11-26/cells-2026-11-26/`), outside
the repository until verification is locked.

| | model-cells changed (of 1,008) | how |
|---|---:|---|
| F4 | 9 | n.a. (from a considered exclusion) -> value `no`, status considered; 6 projects |
| F3 | 3 | DeepSeek `none_stated` -> unknown, `search_incomplete` (the all-rejected responses); 3 projects |
| F2 | 0 | no production premise was rejected, superseded or without keys |
| PET | 42 retail mentions withheld (Claude 10, Sol 7, DeepSeek 25) | scope unknown, or retail scope in a document of unknown layer |

The F4 change narrows the upper end of the per-model interval in 9 model-project pairs and moves 6 projects in the
provisional combination of the results package. A value `no` with status considered is not a commitment, so it does not
raise any lower bound. The ADR-012 D2 count of keys with a value is unchanged in the core (14 of 128) and in T3 (4 of 208).
The new verification workbooks of 26 Nov are built from the repaired cells.
