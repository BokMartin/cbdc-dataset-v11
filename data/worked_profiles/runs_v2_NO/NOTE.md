# Norway — valid single vs two-stage comparison (2 Nov 2026, ADR-001 E11)

Run `NO_anthropic_claude-opus-5-5_both_20261102T122025Z` (extractor v2, contract v1.1, schema v1_1, claude-opus-5-5). All 7 documents processed in stage one (36/36/20/49/30/38/22 findings, 231 total), synthesis `ok` with 0 validation problems; single mode `ok_with_validation_problems` (2 schema problems, see MANIFEST). Citation check v2: **17/17 exact_page** in both modes.

Comparison (`COMPARISON_single_vs_two_stage.csv`, tuple value/evidence/status/doc/page over 17 cells): **4 full, 7 value-only, 6 differ**.

- **F1 no in both modes**, both non-admissible under rule C (single: partial/tested on doc 7; two-stage: partial/option on doc 6). Y₁ for Norway is undetermined under the commitment view in both modes; the earlier "Y₁ = 1" came from a v1 option claim and is withdrawn (EXPOSURE_LEDGER).
- Value differences: F2 (single yes/tested from the Phase-5 sandbox; two-stage n/d), F12 (single permissioned_DLT/tested; two-stage undecided/option — both true of different claims, which is what the v2 "component + selection status" fix is for), F11 cash_substitute and innovation flags, F11 primary_status (several_joint vs one_primary) and primary_objectives wording.
- Status differences: two-stage labelled several F11 objectives `adopted` for a project whose competent body decided in Dec 2025 not to introduce a CBDC; single labelled them `option`. This is the v1.1 status ladder failing, not an extraction-architecture difference: v2's `decision_status` × `implementation_status` and the endorsement rule remove the ambiguity.

Reading: with complete coverage the two modes agree on every yes/no value that matters for the type except F2, and disagree mainly on status labels and on F11/F12 descriptive cells. The withdrawn claim that two-stage is "systematically more conservative" is not supported in either direction by this run; UK pending.
