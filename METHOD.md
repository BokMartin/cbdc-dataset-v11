# Method and progress — CBDC Dataset v12

Status as of 3 November 2026. For the supervisor and the authors. The v11 version of this file (18 Oct) is kept in git history; `site/method.html` mirrors this page.

## What the paper is now

A **measurement and data paper** for *Data & Policy*: an audited, cross-project account of who is documented as able to link a retail CBDC payment to a person, under what decision and implementation status, with what uncertainty, from official documents only. Three layers, never mixed: (1) the **commitment matrix** (cells F1–F12 admissible only when documented and endorsed by the competent body or operational, contract v12 rule C); (2) the **privacy-posture layer** (P0–P3 ladder and indicators G1–G9 over every located statement, status attached); (3) **linguistic emphasis** (encoder-labelled paragraph shares and stance), descriptive only. The "table of commitments that disappear under strict rules" is the bridge between layers. A classified institutional illustration (H2, liberal democracy) is **not feasible on the commitment matrix** on current evidence (sealed census: 5 model-labelled endorsed F1 positions of 43) and is either omitted or exploratory on the status-attached view; the authors decide on 6 Nov.

Why v12: the external consultation (28 Oct) showed that v11's status ladder treated conditional statements as commitments and that its genre-based core rubric was applied unevenly; the independent audit (2 Nov) found the executable instrument did not enforce the proposed rules; the uniform gap check (2 Nov) found that the rubric had excluded 354 official documents across the 43 projects, most of them status decisions, legislation and FAQs with explicit privacy statements. The v11 line is tagged `v11-dev-final`; its instrument and rubric are in `archive/v11/`.

## Step by step (v12)

1. **Frame — done.** 48 projects → 46 national → 43 retail candidates (`PROJECT_FRAME.md`); unions out of the national analysis; BO, BR, US excluded with reasons.
2. **Source rule and gap check — rule drafted, check run (2 Nov).** Authority/content rule D1 replaces genre exclusions. Model-assisted search of all 43 projects: 378 candidates, 354 not in the registry; major gaps in 27 projects. **Next: author decision over the 178 priority rows**, download, SHA-256, dated additions, texts; then the one-table source manifest `SOURCE_MANIFEST_v12` (URL, hash, language, route, reuse terms) is frozen with a single as-of date (18 Oct 2026).
3. **Language — ledger kept.** 106 English / 19 non-English of the 125 v11 core documents; routes A (English original) / B (issuer English edition: Norway ingested, Russia 2021 available, Japan pair) / C (checked translation) / D (machine, provisional). Within the 43-frame, evidence only via translation: 7 documents in 6 projects (CL 2, CN, CZ, RU 2025, TW, UY). Both denominators go into the registration.
4. **Instrument — contract v12 draft.** Endorsement rule; `decision_status` × `implementation_status`; symmetric admissibility implemented and tested in `scripts/derive.py`; F7 inference from silence deleted; F11 eight atomic tags; F12 by component; locators with spans; posture layer §6b. Open: F9/F10 retention; routing single vs two-stage (single mislocated pages in a 1.2M-character request; two-stage located 17/17); contract adopted only after the corpus is completed and a new census run.
5. **Development cases.** NO (route B), UK done as development; euro area, Canada, Chile (needs route C), Hungary, one LIVE project next, with time measured. Development verdicts never become the human reference.
6. **Sealed model-only screens — done, to be re-run after step 2.** Endorsement census (one question, F1) and statement survey (2,628 typed statements, 80 % located verbatim) with per-project results sealed off-repository; aggregates committed; release governed by `data/EXPOSURE_ALLOWLIST.json` in code.
7. **Freeze and registration — gate.** Manifest, contract, prompts, routing, gates (α ≥ .80, AC1, ≥ 95 % joint F1/F2/F4/F7 screening, citations 100 % located) frozen; Zenodo DOI for code and, where terms allow, corpus; OSF registration with exposure disclosure and both language denominators; δ elicited only if a classified estimate remains.
8. **Human reference.** Blind reference workbooks (no model columns) for a probability sample of 12–16 projects, locked before any model output is opened, plus source-first F1 (and F7 if kept) for every analytic project; adjudication logged.
9. **Production and audit.** Frozen pipeline, two providers, one scored run on the blind set; challenge battery; outer audit of DROP documents and OCR loss; stability envelope on six fixed projects (Norway among them: its F1 flips between `no` and `n/d` across runs while staying inadmissible).
10. **Analysis and release.** Commitment matrix, posture layer, emphasis layer, change map, missingness bounds; all numbers replayable from archived outputs without API access; website mock data replaced by pipeline output without changing the site.

## Open decisions for the authors (6 Nov)

1. Shape of the paper: measurement-and-data core; H2 omitted or exploratory.
2. Order of work: complete the corpus under D1 before any instrument freeze (recommended by the audit and by the technical collaborator).
3. Blind set 12 vs 16 given hours per week; F9/F10; routing rule; δ only if needed.
