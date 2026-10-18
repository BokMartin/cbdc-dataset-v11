# PREDICTIONS v2.2 — draft for registration (CBDC privacy dataset / paper v11)

Status: **draft v2.2, 18 October 2026 (evening)** — v2.1 with Y₂ removed after MEASUREMENT_CONTRACT v1.1 (F3 descriptive only). To be frozen together with MEASUREMENT_CONTRACT_v1 after the worked profiles, then registered on OSF with an external timestamp and the decision record in §6. No F-cell value and no association on v2 data has been computed at the time of writing.

## 1. Framing

The paper is a measurement and data paper with a limited empirical illustration. The main contribution is the validated feature matrix (F1–F11) and the map (architecture type × declared objectives × project status). Institutional associations are illustrations with ~20–50 determinable projects; they are reported whatever they show.

## 2. Outcomes

Primary illustration **Y₁** = F1-based (central bank cannot routinely link online transactions to a person), subject to the orientation rule (≥ 20 determinable projects, minority class ≥ 6). **Y₂ removed (v2.2):** F3 is descriptive only; no hypothesis concerns public-authority access. **Y₃** = F7-based, reported with and without inferred zeros (contract §6.6a). If Y₁ fails the orientation rule, the paper reports descriptive results only and says so.

## 3. Predictors (vintages to be fixed before freeze)

- Shadow economy: World Bank Informal Economy Database (Elgin et al. 2021), DGE-based share of GDP, year = project's decision year or latest available; vintage to be named.
- Liberal democracy: V-Dem `v2x_libdem`, same year rule; vintage to be named.
- Central-bank independence: index and vintage to be named; descriptive use only (§4).
- Monetary-union projects (euro area, ECCU, WAEMU) are excluded from tests with a national predictor and kept in the map; a union-inclusive sensitivity is reported only with a substantively justified aggregate.

## 4. Hypotheses, estimands, decision rules

| | question | direction | estimand | classification |
|---|---|---|---|---|
| H1 | Is a larger informal economy associated with less frequent central-bank separation (Y₁)? | negative | Δ_X = m(q75) − m(q25) from one pre-specified Firth logistic model per predictor on projects with determinable Y; m = predicted probability of Y = 1 | supported if the 95 % interval of Δ lies entirely below −δ; refuted if entirely above −δ; indeterminate otherwise |
| H2 | Is liberal democracy associated with more frequent Y = 1? | positive | same, sign reversed | same with +δ |
| H3 | Central-bank independence | — | descriptive only: Δ with interval, no equivalence claim | not classified |

δ (SESOI on the Δ scale) is set by expert elicitation (authors + consulting professor) before any result is seen and justified economically in the registration; 20 percentage points is a working proposal, not a decision. One-sided conventions as stated above; two primary tests (H1, H2) on Y₁ → no multiplicity correction beyond reporting both; Y₃ results are secondary and labelled as such.

Alongside the model: bounded prevalence difference between pre-defined upper and lower predictor groups, s/n … (s+u)/n, reported as a different estimand. Leave-one-project-out influence reported. Project bootstrap resamples projects; coding uncertainty is reported separately from the audit.

Descriptive results (not tests): architecture × declared-objective cross-tabulation; documented lawful-access route (F3) and ledger technology (F12) by architecture type; change map from per-cell `history` for projects with ≥ 3 dated documents; share of F7 = yes among projects declaring financial inclusion; status distribution; coverage flow registry → eligible projects → core → determinable Y → covariate-complete.

Dropped from earlier versions: Y₂ and its tests (v2.2, see contract §12); H4 (Basel AML index as "pressure"); TRACE-vs-DESIGN as a negative control; wholesale on/off as a robustness check of retail hypotheses; pass/fail outcomes; any correlation with a 1–6 type code.

## 5. Failure policy

If the final frozen-pipeline audit fails its pre-set tolerance (feature/type/Y error vs. the human reference; tolerance to be set relative to δ before the audit), the instrument is reported as failed for the affected cells, or a new version is developed and validated on fresh material. The test split is never reused.

## 6. Decision record (what has been seen)

Seen before this draft: v1 published results (vocabulary-based purpose categories and their correlations with institutional variables — legacy, informed the hypotheses); keyword-presence scans of F-vocabulary in core (Oct 2026); round-1 paragraph coding by both authors (development, α 0.33–0.55 by family); the official project-status table (Oct 2026). Not seen: any F-cell value, any architecture type, any association on v2 data.
