# Privacy index: specification (DRAFT, 21 Nov 2026)

Status: proposal implementing the decision of MB in [ADR-009](../DECISIONS/ADR-009-privacy-index-headline-2026-11-21.md); DS to confirm. Implementation: `scripts/derive_index.py`, tests `tests/test_derive_index.py` (synthetic cells only). Nothing here has been computed on project data.

## 1. Construct

The extent to which the documented design of a retail CBDC keeps the central bank, intermediaries and the state from routinely attributing a payment to an identified natural person (axis 1), and how firmly the competent body holds that design (axis 2). Not measured: how much a project talks about privacy, data protection in general, or whether a design is desirable.

## 2. Components

| Cell | Protective value | Dimension | Role |
|---|---|---|---|
| F1 CB_LINK_ONLINE | no | A, central bank and state | core; gate |
| F2 PSP_LINK_ONLINE | no | B, intermediaries | core |
| F7 LOW_ID_ROUTE | yes | C, identity at entry | core |
| F4 PRIVATE_OFFLINE_AVAILABLE | yes | D, offline | core |
| F8 ONBOARDING_ID | no | joins C | sensitivity only |
| F10 PROGRAMMABLE_RESTRICTIONS [OPEN] | no | E, control of use | sensitivity only |
| F3, F9 | ambiguous direction | — | reported beside the index |
| F11, F12 | not privacy | — | outside |

## 3. Axis 1, design privacy

Each component is 1 (protective), 0 (not protective) or undetermined, from the cell value at any status (status-attached view). Dimension score = mean of its components; index = weighted mean of the dimensions (equal weights). **Lower bound** = every undetermined component set to 0; **upper bound** = set to 1. If F1 = yes is determined, both bounds are capped at 0.5 (gate). Nothing is inferred from silence (AGENTS.md).

## 4. Axis 2, commitment

Rung of each component that has a value: considered 1, tested 2, endorsed 3, operational 4 (rejected or superseded claims carry no value). Axis 2 = mean rung / 4. The number of admissible components (rung ≥ 3) is reported beside it.

## 5. Robustness: the strict index

Axis 1 computed on admissible cells only (contract §5, rule C). Reported for every project beside the primary index.

## 6. Ordering

Two projects are ordered on axis 1 only if their intervals do not overlap. No point ranking; the figure is a map of the two axes with interval bars.

## 7. Sensitivity (registered with the definition)

Strict vs status-attached; with F8 and F10; without route-D cells; without inferred cells; without the gate; leave one component out; Dirichlet(1) random weights over the dimensions (share of ordered pairs kept in every draw and on average); T1 and T2 projects only.

## 8. Not done by the index

No combination with talk labels; no difference of talk and commitment; no correlation with covariates in the article (proposal; open in ADR-009); no causal language.

## 9. Literature to compare with (from memory, citation check pending)

OECD and JRC (2008) Handbook on Constructing Composite Indicators; Saisana, Saltelli and Tarantola (2005) on uncertainty and sensitivity analysis of composite indicators; Greco et al. (2019) on weighting and aggregation; indices of central bank independence coded from legal texts (Cukierman, Webb and Neyapti 1992; Romelli 2022, 2024) as the closest methodological analogue; Auer, Cornelli and Frost (2023) on CBDC project data.
