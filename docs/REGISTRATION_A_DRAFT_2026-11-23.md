# Registration A: index, hypothesis and known cases (DRAFT, 23 Nov 2026; not registered, not confirmed by the authors)

Purpose (ADR-012 D1 a): register the index definition, the hypothesis and the known cases **before the first paid call** and
before any blind coding of F-cells. Every rule below is copied from a decision already taken. The source is given in brackets.
Items marked **AUTHORS** are not yet decided and must be settled before this text goes to OSF. This draft covers parts 6, 7 and
11 of the auditor's registration list (INDEPENDENT_AUDIT_2026-11-22 §18). The other parts go in Registration B, before the
reference sample and production.

## 1. Population

- Frame: 44 retail CBDC projects. 42 have readable text; CL and CZ are unavailable (ADR-012 D1 f).
- Core: the 16 projects of the tiers frozen on 17 Nov 2026 (ADR-012 D13). T1 is EU, IL, JM, JP, KZ, SE, TW, UK. T2 is AU, BS, CA,
  HK, IN, NO, NZ, RU.
- NO and UK are development projects. Both authors saw model fills for them in October (EXPOSURE_LEDGER, 18 Oct). They are coded
  and measured like the others, but they are not called blind, so inter-coder agreement is reported on the 14 other core projects
  (D1 d, g).
- T3: 28 projects, reported as exploratory, "often unfinished CBDC research" (D1 e).
- Corpus cutoff: issue date on or before 18 Oct 2026 (D11).

## 2. Index (stated-design privacy index)

**Construct.** The index measures the extent to which the design described in the official documents keeps the central bank,
intermediaries and the state from routinely attributing a retail payment to an identified natural person (index spec §1).
Talk labels never enter the index.

**Primary number.** The mean of seven cells, F1, F2, F4, F7, F8, F9 and F10, with an interval (D4). Each cell is scored from
its value at any status:

| cell | 1 (more privacy) | 0 |
|---|---|---|
| F1 central bank can link online payments to a person | no | yes |
| F2 intermediary can link online payments | no | yes |
| F4 private offline payments available | yes | no |
| F7 low-identity route (narrowed to anonymous holding and paying, D9) | yes | no |
| F8 identity required at onboarding | no | yes |
| F9 targeted re-identification possible | no | yes |
| F10 programmable restrictions | no | yes |

Direction rule (MB, 22 Nov): less access, less identification and no re-identification mean more privacy.

**Interval.** Nothing is imputed. The lower bound scores every undetermined cell 0 and the upper bound scores it 1 (index spec
§3, Manski-type bounds). A disagreement between the blind coders that adjudication does not resolve makes the cell undetermined.

**Reported beside the primary number, outside the mean:**
- The four-cell index, F1, F2, F4 and F7, as the narrower variant (D4).
- F3 (lawful access route) as a category (D4).
- The PET profile: a separate multi-valued record beside F7. Its codes come from Nijsse and Pinto (2026), and it is a profile,
  not a scale (D4).
- Axis 2: per cell, the decision status and the implementation status as two fields. The number of cells that pass the one
  admissibility predicate (`scripts/derive_index.py committed()`) is shown out of a fixed denominator (D10).

**Sensitivity variants, registered now:**
1. F7 and F8 grouped as one component.
2. The admissible view, using committed cells only.
3. Without route-D (machine-translated) cells. The main result includes them, and Taiwan's dependence on route D is stated (D6).
4. `with_leaning`, where LEANING cells come only from joint retail reports. LEANING is never a commitment (D5).
5. Index from blind-coded cells only (D2).
6. Leaving out each cell in turn, and Dirichlet weights (index spec §7).

**Source of cells.**
- In the 16 core projects, both authors code every cell from the sources, in the blank coder template, before any model output
  is opened. They then adjudicate. The three models are a comparison (D1, D2).
- Outside the core, a cell has a value only if all three models agree, give a located quote, and pass a source check. Otherwise
  the authors decide (D2).

**Not allowed.** No league table and no ordering of projects until DS confirms the ordering (index spec §6). No causal language.

## 3. Hypothesis "much talk, few commitments" (D3)

Per core project p:

- **Much talk (T_p):** own-voice privacy talk in at least two distinct publications, **and** at least 1 own-voice relevant unit
  per 100 eligible units.
- **Few commitments (C_p):** fewer than 2 of the four protective commitments F1, F2, F4 and F7. A commitment means the cell holds
  its protective value and passes `committed()`.
- **The hypothesis holds** if a majority of the 16 core projects (9 or more) meet both T_p and C_p. It is **inconclusive** if the
  bounds straddle a majority. There is no sign test.

**Bounds (MB, 23 Nov 2026: the stricter variant, as proposed).** Each project gets a lower and an upper reading.
- Lower: an undetermined cell counts as committed, and a unit without a majority label counts as not relevant.
- Upper: the reverse of the lower reading.
- L = the number of projects that meet both T_p and C_p at the lower reading. U = the number at the upper reading.
- The hypothesis holds if L ≥ 9, fails if U ≤ 8, and is inconclusive otherwise.

**Denominator (MB, 23 Nov 2026: as proposed).**
- "Eligible units" are all units of the project's evidence texts, after excluding headings and furniture (stratum X).
- "Own-voice relevant" is relevance R with voice OWN, under the combination rule of the three models fixed at the freeze
  (Registration B).

**Reported beside the hypothesis.** Neither of these quantities decides it.
- The volume of talk relative to text length.
- The share of relevant sentences that state a mechanism (basis other than NONE) or a decision (decision ENDORSED).
- The index with its interval and the PET profile.
- The directional gap: aspects talked about without a commitment.

**If the facet gate fails.** A facet that fails the agreement gate is exploratory, and the headline claim that rests on it is
withheld (D8). On the 80 sentences of 23 Nov all facets passed (docs/FACET80_AGREEMENT_2026-11-23.md), as an upper bound.

## 4. Known cases (index spec §10.2, V5)

A known case is a cell whose value the authors fix in advance from an official document, with page and quote. The index must
reproduce it, and a miss is reported, never tuned away. Only cells that are already exposed may be used (auditor §8: "freeze
only documented development known cases").

| case | project | cell | expected | exposure | status |
|---|---|---|---|---|---|
| K03 | UK | F1 | no | UK is a development project (exposed 18 Oct) | proposed; **AUTHORS:** fix page and quote (BoE CP 970, 2024) |
| new | NO | **AUTHORS:** choose 1 or 2 cells from the October development profile | | NO is a development project (exposed 18 Oct) | to be proposed |
| K01, K02 | EU | F4 yes, F1 no | | EU is a core project, coded blind | **dropped** (MB, 23 Nov 2026: EU stays in the core; the two values are not fixed in advance, so EU can be coded blind) |
| K04 to K07 | BS, CN, NG | F7 / F1 | not filled | filling a value exposes the project; BS is core | recommended: leave out |

## 4a. Reference sample: what is excluded (MB, 23 Nov 2026)

The reference sample of 400 units (D18) leaves out every block of `data/units/EXPOSURE_REGISTRY_*.csv`: the paragraphs shown to
the authors and the paragraphs labelled in development runs (`scripts/units/exposure_registry.py`, `blocks()` without
`shown_only`).

## 5. Before this goes to OSF

1. The authors settle every AUTHORS item above (open: the page and quote of K03 and the NO cases). DS confirms MB's answers of 23 Nov.
2. DS confirms the replacement of the manual issuer review by the machine check (docs/ISSUER_CHECK_2026-11-23.md). Issuer and
   kind enter the request headers.
3. The extraction prompt v12.1 is adopted after the second-model audit, and codebook v0.4 and relevance prompt v0.3 are
   confirmed. Registration B fixes their SHA-256.
4. An OSF account exists (MB).
