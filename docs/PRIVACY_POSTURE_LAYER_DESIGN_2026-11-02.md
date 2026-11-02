# Privacy-posture layer: design memo from the sealed statement survey (2 Nov 2026)

Purpose. The endorsement census showed that the strict commitment matrix (contract v2 rule C) determines Y₁ for roughly 5–8 of 43 national retail projects. The authors' response (MB, 2 Nov): report that the official documentation gives no specific answer for most projects, and add a **more sensitive but still auditable** layer beneath the commitment matrix, plus a clearly separated "privacy talk" layer. This memo proposes that layer from a model-only survey of every statement about privacy/identifiability in the 125 core documents. Per-document results are sealed (off-repo; SHA-256 in `data/census/POSTURE_SURVEY_aggregate.json`); the authors see aggregates and example quotes from the two already-exposed projects (NO, UK) only. Evidence grade: one model (claude-opus-5-5), one pass, no human verification; counts are design input, not results.

## 1. What the corpus contains (aggregate, 125 documents, 2,628 typed statements)

| statement type | statements | retail projects with ≥ 1 (of 43) | … endorsed | … operational | … tested | … considered only |
|---|---|---|---|---|---|---|
| PRIVACY_AS_RISK_OR_TRADEOFF | 361 | 32 | 0 | 0 | 8 | 31 |
| LAWFUL_ACCESS | 262 | 38 | 9 | 4 | 10 | 33 |
| PRINCIPLE (privacy as goal/requirement, no mechanism) | 254 | 34 | 8 | 2 | 10 | 28 |
| PSP_HOLDS_IDENTITY | 202 | 32 | 5 | 7 | 8 | 23 |
| TIERED_LOW_ID | 142 | 24 | 5 | 3 | 6 | 17 |
| PET_TECHNIQUE | 140 | 12 | 0 | 0 | 9 | 10 |
| PSEUDONYMISATION | 137 | 20 | 1 | 4 | 7 | 13 |
| CB_NO_PERSONAL_DATA | 136 | 22 | 3 | 2 | 6 | 17 |
| CB_SEES_DATA | 112 | 30 | 2 | 2 | 6 | 25 |
| PROGRAMMABILITY | 111 | 29 | 4 | 2 | 5 | 23 |
| USER_CONTROL_CONSENT | 101 | 20 | 3 | 0 | 5 | 17 |
| DATA_MINIMISATION | 90 | 17 | 4 | 1 | 4 | 13 |
| LEGAL_COMMITMENT | 75 | 21 | 4 | 4 | 1 | 17 |
| OFFLINE_PRIVACY | 61 | 11 | 0 | 0 | 3 | 10 |
| ANONYMITY_REJECTED | 44 | 12 | 4 | 0 | 0 | 11 |
| NO_COMMERCIAL_USE | 11 | 5 | 0 | 0 | 0 | 4 |
| OTHER (public-opinion results, wholesale confidentiality, digital-ID, ledger visibility, data reuse) | 389 | 40 | 9 | 10 | 13 | 35 |

Three facts that shape the design:

1. **Privacy is discussed almost everywhere, decided almost nowhere.** 40 of 43 projects have at least one architectural statement in the raw survey; after the mechanical citation check and the eligibility rule (located, not rejected, not staff research) it is 35, and endorsed or operational architectural statements of *any* kind exist in 13 (`data/census/POSTURE_LADDER_aggregate.json`; the figure 41 in the first version of this memo was a counting error, audit item 9). The commitment matrix is not wrong, it is simply the top rung of a ladder most projects have not climbed.
2. **CB_NO_PERSONAL_DATA and CB_SEES_DATA co-occur in 12 projects on located claims** (5 have only "no", 11 only "sees", 15 neither; raw survey: 17 / 5 / 13 / 8). Within a project the position moves across documents, designs and years. A single F1 value hides this; the posture layer should record *both* directions with status and date, and the paper should show the movement.
3. The most frequent type is privacy framed as **risk, trade-off or public concern** (32 projects), never endorsed. That is "privacy talk" in the authors' sense, and it is measurable as a stance, not as sentiment.

## 2. Proposed layer A: posture ladder (ordinal, per project, derived from claims)

Derived mechanically from atomic claims with the same pipeline, citation check and status fields as the F-cells (contract v2 §3). One value per project at the as-of date, with the claim history beside it.

| level | definition | survey count (43) |
|---|---|---|
| **P3 commitment** | ≥ 1 *endorsed or operational* architectural claim about identifiability (types CB_NO_PERSONAL_DATA, CB_SEES_DATA, PSP_HOLDS_IDENTITY, PSEUDONYMISATION, TIERED_LOW_ID, OFFLINE_PRIVACY, ANONYMITY_REJECTED, PET_TECHNIQUE); rejected-only and staff-research claims never count | 13 (raw 15) |
| **P2 architecture considered or tested** | ≥ 1 architectural claim of those types with status considered/tested, none endorsed | 22 (raw 25) |
| **P1 principle only** | privacy/data protection stated as principle, legal commitment, data minimisation or user control, without an architectural claim | 3 (raw 1) |
| **P0 silent or not located** | no located eligible statement about user privacy/identifiability (lawful access, programmability and risk talk do not count); the export separates search complete, nothing found from quotes not located | 5 (raw 2) |

P3 is wider than F1: it counts any endorsed architectural position (e.g. "PSPs hold identity", "no cash-like anonymity"), not only the CB-linkage question. Y₁ stays defined on F1; the ladder is the descriptive layer that shows where the 35 undetermined projects sit. It is ordinal, never scored or correlated as a number; cross-tabulated with project status and the H2 covariate descriptively.

## 3. Proposed layer B: low-threshold indicators (binary, any status recorded)

Each is a yes/not_documented cell with status, basis, locator and quote, so "sensitive" means *low evidential threshold*, not *loose definition*. Status and basis stay attached and are reported, so a reviewer can see that "yes (considered, policy basis)" is not a commitment.

| id | question | from survey type | retail projects with ≥ 1 (raw → located) |
|---|---|---|---|
| G1 PRIVACY_PRINCIPLE_STATED | privacy / data protection stated as a design principle, objective or requirement | PRINCIPLE | 34 → 25 |
| G2 CB_NO_DATA_STATEMENT | any statement that the CB will not / cannot see or hold personal or transaction-identity data (basis policy / architectural / cryptographic recorded) | CB_NO_PERSONAL_DATA | 22 → 17 |
| G3 CB_DATA_STATEMENT | any statement that the CB will or may see or hold such data | CB_SEES_DATA | 30 → 23 |
| G4 LOW_ID_TIER_MENTIONED | a tier/wallet without full identity verification mentioned as option, test or decision | TIERED_LOW_ID | 24 → 19 |
| G5 CASH_ANONYMITY_REJECTED | explicit statement that cash-like anonymity will not be offered | ANONYMITY_REJECTED | 12 → 11 |
| G6 PET_NAMED | a named privacy-enhancing technique considered or tested | PET_TECHNIQUE | 12 → 10 |
| G7 DATA_MINIMISATION_STATED | collect/retain only what is necessary | DATA_MINIMISATION | 17 → 12 |
| G8 LEGAL_PRIVACY_COMMITMENT | statutory or legislative privacy commitment named | LEGAL_COMMITMENT | 21 → 18 |
| G9 PRIVACY_AS_RISK | privacy discussed as risk, trade-off, public concern or adoption barrier | PRIVACY_AS_RISK_OR_TRADEOFF | 32 → 26 |

F3 (lawful access) and F10 (programmability) already cover LAWFUL_ACCESS and PROGRAMMABILITY; USER_CONTROL_CONSENT and NO_COMMERCIAL_USE map to the reserved F6 and are too thin (5 projects) to carry. G2 and G3 together replace the loss of information in a single F1 value: both can be yes for one project, with dates.

Traps carried over from the contract: "will not use" is policy basis, never architectural; a statement in a staff paper is `staff_research` and sets nothing; status is attached to the claim, not the document genre.

## 4. Layer C: "privacy talk" (linguistic emphasis), separate and labelled

The authors want to keep a phrase-count/sentiment layer as a supplementary dataset. Recommendation:

- **Keep** a per-document emphasis measure, but build it from the validated encoder labels (share of paragraphs labelled PRIV / TRACE in encoder round 1), not from raw word counts; word counts can be an appendix column.
- **Replace sentiment** with **stance**: share of privacy statements of type PRIVACY_AS_RISK_OR_TRADEOFF vs. PRINCIPLE + architectural types (from layer B), i.e. privacy framed as a problem vs. as a design goal. Central-bank prose is deliberately neutral; a sentiment score on it measures the detector, not the bank.
- The layer is descriptive, lives in its own table, never sets a cell, never enters Y or the illustration, and is labelled "linguistic emphasis" in the paper (contract v1.1 F11 trap already says this).

## 5. What changes in contract v2 and the plan

- Contract v2: add §6b "posture layer" with P0–P3 and G1–G9 (definitions above), derived from the same claims; add the claim types to `schema/cells_v2`; `derive.py` gets `posture_level(claims)`; the website shows ladder + G-indicators under the "status-attached" banner.
- The posture layer does **not** change rule C, Y₁ or the exposure rules. Human verification of G-cells is a source-check of quotes (not blind coding) except for the blind sample, where G-cells are coded with the F-cells.
- Paper framing: the commitment matrix answers "who has decided"; the posture layer answers "who has said what, with what status"; the table of commitments that disappear under strict rules is the bridge between them. The census result ("5 endorsed F1 positions out of 43") is reported as a finding, not hidden.
- Exposure: the survey is sealed like the census; this memo and the definitions were written after a model pass over the whole corpus and before any human coding (entry in `EXPOSURE_LEDGER.md`).

## 6. Example statements (exposed projects only: NO, UK)

- PRINCIPLE: NO doc 3 p. 4, considered, policy: "Can provide the desired degree of data protection (beyond requirements under EEA law)".
- CB_NO_PERSONAL_DATA: NO doc 7 p. 11, tested, architectural: "customer information and identity data remain at th[e banks]"; UK doc 3 p. 57 (F1 source), adopted in the single-mode fill.
- ANONYMITY_REJECTED: NO doc 2 p. 17, considered, policy: "Det vurderes ikke som nødvendig at DSP skal gi samme grad av anonymitet som kontanter."
- TIERED_LOW_ID: NO doc 2 p. 26, considered: limited access for persons not meeting the requirements, small amounts, one identified party.
- PROGRAMMABILITY: NO doc 6 p. 17, considered: "CBDC should not be programmable money".
- NO_COMMERCIAL_USE: UK doc 3 p. 78, considered, legal: "Any commercial use of personal data would need to comply with UK data protection laws."

## 6a. Citation check of the survey itself

Of 2,628 survey statements, 2,094 (80 %) are located verbatim on the cited page, 19 elsewhere in the document, 100 are fuzzy candidates and **415 (16 %) are not located**. The posture layer uses located claims only; the 16 % is the survey model's quotation error rate and is reported as such.

## 7. Side finding from the survey: the Norway memos are in Norwegian

Quotes from NO documents 1, 2 and 4 came back in Norwegian. Page-level language detection of all 125 core documents (`scripts/frame/detect_doc_language.py`, `data/frame/doc_language_detect.csv`) finds **nine registry labels wrong**: eight documents labelled `en` are not English (NO ×3 Norwegian, CZ 2022 Czech, SI ×3 Slovenian, CN 2025 Chinese) and the AT document labelled `de` is the English summary. The non-English core set is therefore 19 documents, not 12; within the 43-frame it affects **NO (3 of 7 documents), CZ (its only document), CN, CL ×2, RU ×2, TW**. The worked profile Norway was partly coded from Norwegian text by the models. Norges Bank publishes English editions of Memo 1/2018, 2/2019 and 1/2021 (to be verified and added as route B). `LANGUAGE_LEDGER.md` is amended accordingly.
