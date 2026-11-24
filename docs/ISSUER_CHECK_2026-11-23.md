# Machine check of issuer, issuer type and document kind (23 Nov 2026)

**Decision (MB, 23 Nov 2026, decision card in the project thread):** the manual review of issuer, issuer type and kind of the
evidence documents (HANDOFF row 5; ADR-007 F09, "the ledger itself is still model-pre-filled and awaits the authors' review") is
replaced by a machine check. Only the documents on which the check finds a conflict go to the authors; their decision is recorded
in a fixes file. This changes a written rule; DS to confirm.

## Method

`scripts/review/check_issuers.py` checks each of the 208 documents of `data/units/UNITS_MANIFEST_2026-11-23.csv` against the
ledger `data/manifest/ISSUERS_2026-11-13.csv`, without any model call:

- **issuer**: the ledger's issuer must be named on pages 1 to 6 of the document (main name, acronym of at least 3 letters,
  bracketed forms, a distinctive word stem, the CJK name for TW and JP) and/or agree with the majority issuer of the other documents
  from the same web domain (`SOURCE_MANIFEST`, `MANUAL_DOWNLOADS`). An issuer field that holds an acquisition batch name
  (`v1_corpus`, `wave1_…`) is a conflict.
- **issuer type**: derived from the issuer name by the ledger's own normalisation, with a fallback on central-bank words.
- **kind**: rules on the title only; the first rule that fires decides; a conflict only when a rule fires and disagrees.

Outcome per document: `agree` (both signals), `agree_weak` (one signal), `conflict`, `no_signal`; reasons and signals are in
`data/manifest/ISSUERS_CHECK_2026-11-23.csv`.

## Result

| check | agree | agree_weak | conflict |
|---|---:|---:|---:|
| issuer | 155 | 50 | 3 |
| issuer type | 208 | | 0 |
| kind | 207 | | 1 |

The four conflicts and their fixes (`data/manifest/ISSUER_FIXES_2026-11-23.csv`, decided by MB):

| document | field | was | now |
|---|---|---|---|
| CA_BoC_ScaleDown_page_2024 | issuer, type | v1_corpus, other | Bank of Canada, central_bank |
| JM … Bank-of-Jamaica-s-CBDC-Solution_2021 (speech) | issuer, type | wave1_2026-10, other | Bank of Jamaica, central_bank |
| JM … Privacy-Policy-for-the-Bank-of-Jamaica-Wallet_2022 | issuer, type | wave1_2026-10, other | Bank of Jamaica, central_bank |
| JM … BOJ-Prepares-for-Central-Bank-Digital-Currency_2021 | kind | white_paper | press_release |

`scripts/review/apply_issuer_fixes.py` wrote `data/manifest/ISSUERS_2026-11-23.csv` (the 13 Nov ledger with these fixes; fixed
rows carry `issuer_source = machine_check_2026-11-23`) and updated the same fields in the unit manifest of 23 Nov. Re-running the
check against the new ledger gives 0 conflicts (157 agree, 51 agree_weak).

## Limits

- `agree_weak` (50 documents) rests on one signal only; it is accepted under the decision above, not reviewed.
- The check confirms the publisher, not the speaker or the decision authority (F09 asks for these as separate fields; still open).
- Kind is checked only where the title names it; a wrong kind with a neutral title is not found.
