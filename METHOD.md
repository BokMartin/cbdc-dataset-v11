# Method and progress — CBDC Dataset v11

Status as of 18 October 2026. Written for the supervisor and for the authors; the website page `site/method.html` carries the same content.

## What the paper is now

A measurement and data paper with a limited empirical illustration. Main contribution: a validated feature matrix of documented privacy and identifiability design choices in retail CBDC projects (F1–F12), a deterministic architecture typology (A0–C1), a descriptive purpose layer (declared objectives) and a time dimension. Institutional associations (informal economy, liberal democracy) are illustrations on 20–50 determinable projects, pre-registered with a smallest effect of interest, reported whatever they show. Title unchanged: *Institutional Determinants of Privacy Design in Central Bank Digital Currencies*.

Why the change: the v1 approach (vocabulary counts → six purpose centres → a privacy index) could not be validated against an external criterion and its headline correlation moved with the sample. Four rounds of independent review (12–18 Oct 2026) converged on the same remedy: measure a few explicit design commitments under a written contract, validate the instrument, keep purposes descriptive.

## Step by step

1. **Corpus v2.2 and core selection — done (18 Oct).** 391 official documents, 85 jurisdictions, each with SHA-256 and source. Three model passes + first author selected the analytical core under a written rubric; an independent LLM audited verdicts and searched for gaps (16 additions). core_v1 frozen: 109 documents / 56 jurisdictions; UK dated supplement of 18 documents (core_v2). Staff research flagged as a separate authority layer.
2. **Official project status — done (17 Oct).** 85 jurisdictions with sources (LIVE 3, PILOT 6, PREPARATION 26, EXPLORATION 27, PAUSED 13, DISCONTINUED 4, BANNED 1, NONE 3). Context and map only, never an outcome.
3. **Measurement contract — v1.1 (18 Oct).** Atomic claim schema; feature definitions with traps; inference rules (F2 only from three documented premises; F7 = no inferred only when F8 = yes and no other route is mentioned); supersession; typology; outcomes. v1.1 after the first two profiles: F3 reduced to a descriptive lawful-access route (Y₂ dropped), F12 ledger technology added, per-cell history derived automatically.
4. **Extraction pipeline — built (18 Oct).** API-based, no chat history; two modes (all documents in one request; per-document findings → synthesis). Every run logs model id, SHA-256 of contract/prompt/script, raw responses, token usage. Mechanical citation check (`quote_verified`). Interactive agent fills are development material only.
5. **Worked profiles Norway and UK — in progress.** Pipeline output under v1.1 (UK: both modes agree on all values but F4; Norway: 4 cells differ, all traceable to one open definition — the status of a design draft published together with a decision not to issue). Authors verify each cell against the cited page and classify each disagreement as model error or definition problem. Open decisions: project status "declined, still exploring"; F12 tested-vs-undecided rule.
6. **Contrasting development cases — next.** Euro area, Canada (staff-heavy), Chile/Brazil (non-English), Hungary (discontinued), one LIVE project. Second provider added for model–model disagreement.
7. **Freeze and registration — gate.** Contract frozen; smallest effect of interest set by elicitation with the supervisor before any cell is computed; predictions v2.2 registered on OSF with decision record and split ledger. Sealed blind test set (6–8 projects whose model output the authors have not seen), coded independently by both authors from the PDFs.
8. **Production extraction and audit.** Frozen pipeline over all core projects, two providers; adjudication logged; one scored run on the blind test set (α and AC1 human–human and model–human; feature/type/Y error vs. human reference); failure policy if tolerance is missed.
9. **Analysis and release.** Pre-specified Firth logistic models per predictor, Δ between predictor quartiles against the registered SESOI; descriptive cross-tabulations (type × objective, F7 among inclusion-declaring projects, F12 by type, change map). Mock data on the site replaced by the output without changing the site.

## Questions for the supervisor

1. Smallest effect of interest: working proposal 20 percentage points in P(Y₁ = 1) between the 25th and 75th predictor percentile — to be set together before any result exists.
2. Commitment status in pre-decision projects: may the typology rest on option-level cells (flagged), or only on adopted ones (most of the map then stays undetermined)?
3. Dropping Y₂: public-authority access depends on law outside the corpus in both profiles; we keep it as a described route and drop the hypothesis. Right call, or build the background legal layer for a subset?
