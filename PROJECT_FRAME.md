# Project frame — from registry rows to analysable projects (recomputed 2 Nov 2026)

Unit of analysis = one retail CBDC project per decision authority (contract §1). Counts are recomputed by `scripts/frame/project_frame.py` from `data/registry/REGISTRY_v2_2.csv` and `data/jurisdictions/JURISDICTION_STATUS_2026-10-17.csv`; this file is its rendered output and replaces every earlier planning figure ("56 jurisdictions", "56–70 projects", "40–50 determinable").

## Funnel

| Step | Count | Rule |
|---|---:|---|
| Registry rows (documents) | 391 | all official documents registered with SHA-256; URL present for all 125 core documents after the 2 Nov amendment, still blank for 40 non-core registry rows |
| Registry codes | 92 | 85 jurisdictions + 3 unions (EU, ECCU, BCEAO) + BIS, UN + euro-area national central banks counted under their own codes |
| Core-flagged documents (core_v1 + core_v2) | 125 | 109 frozen core_v1 (77 KEEP, 32 BORDERLINE) + 16 dated UK additions |
| Core codes | 56 | |
| **Candidate projects** after euro-area consolidation (20 national codes → EU) and exclusion of BIS/UN | **48** | |
| of which monetary unions present in core | 2 | EU, ECCU (BCEAO/WAEMU has registry rows but no core document) |
| **National candidate projects** | **46** | excluded from tests with national predictors: the 2 unions |
| Non-retail or statutory restriction (BO, BR wholesale-only; US dated statutory restriction) | −3 | status NONE / BANNED |
| **National retail candidates** | **43** | before measurement and covariate eligibility |

Status of the 43 (official status table, Oct 2026; 7 added jurisdictions not yet researched): LIVE 3 · PILOT 5 · PREPARATION 5 · EXPLORATION 14 · PAUSED 7 · DISCONTINUED 2 · unresearched 7 (BT, KZ, KE, MU, NP, TW, NG — status to be established under the same rule before freeze).

## What still reduces the analytic sample (to be measured, not assumed)

1. **Admissible F1 under rule C** (endorsed or operational, documented, all qualifiers): unknown until the endorsement census (Phase 1) — the largest open question of the project.
2. **Language route** (Part V): BO, CL, TW have no English-labelled core document; JP, RU, UY, EU have mixed labels. Projects whose decisive evidence has only route D (machine-only) stay provisional.
3. **Covariates**: World Bank informal-economy share and V-Dem `v2x_libdem` for a common year ≤ 2025; missing X → outside the covariate frame.
4. **Historical projects** (DISCONTINUED: EC, HU; PW): in the descriptive dataset, outside the current-documentation cross-section unless the registered rule says otherwise.

## Language labels of core documents (registry metadata, unverified)

en 113 · es 4 · ru/uk 2 · zh 2 (one is `JP_BoJ_Pilot_JP`, label suspect) · fi 1 · nl 1 · sl 1 · de 1. Audit in Phase 1 (ADR-001 H3).

## Orientation rule for the illustration

The registered illustration (H2 on Y₁) runs only if ≥ 20 projects have an admissible Y₁ and the minority class has ≥ 6, on the covariate-complete national frame. If the census shows this is unlikely, the paper is prepared as matrix + descriptive application (minimum viable paper, ADR-001 G4) without waiting for the blind set.
