# ADR-006: validation by verification instead of full blind facet coding; design of the model runs

Status: part A decided by MB on 17 Nov 2026, DS to confirm. Part B proposed by the pipeline author on 17 Nov 2026, **not decided**; it is held until the audit of 17 Nov (A.6) has reported.
This ADR departs from protocol v2 of 13 Nov (`docs/TALK_AGREEMENT_PROTOCOL_v2_2026-11-13.md`) and from the recommendation of audit A3 that both authors code every facet blind; the departure and its cost are stated in A3.

## A. Decided (MB, 17 Nov 2026)

1. **What happened.** MB coded the 120 units of the development sample blind for relevance only (`data/units/DEV_LABELS_MB_2026-11-17.csv`: R 58, N 36, U 24, 2 not filled) and declined to code the seven facets blind: the effort is out of proportion to what it yields, and the data of the paper are the model's labels in any case.
2. **Development rounds.** Three rounds of 40 to 60 new units each, pre-filled by the model; the author marks each label correct or wrong and gives the right value. Each round ends with a versioned prompt change. Development rounds are reported as development, never as validation, and never use the reference sample.
3. **What this can and cannot show.** Agreeing or disagreeing with a pre-filled label is verification, not independent coding: it anchors the reviewer, it gives no inter-coder agreement and it overstates accuracy. The paper says so. Four things keep the claims honest:
   - **Relevance stays independent.** Both authors code relevance blind (MB done; DS to do the same 120 units). Reported: human-human agreement and model-human agreement.
   - **Planted errors.** In the final verification sample 10 to 15 % of the pre-filled facet labels are deliberately wrong, drawn by a committed seed and unknown to the reviewer. The share caught is reported as the detection rate of the verification and bounds how far "verified" can be trusted.
   - **Full verification of what the paper states per project.** Every milestone of the event history and every cell of the talk × commitment table is checked by an author against its source sentence. This is a census, not a sample.
   - **Labelling of the rest.** Stance, modality and basis are reported as model-coded and verified, not as independently validated.
4. **Open for MB.** Row 42 (PE) is empty and row 71 (TH) holds "T"; both are recorded as not filled. Several complete sentences carry "U", which the codebook defines as unreadable or cut off; MB to say whether that was intended.

5. **Three models, full runs (MB, 17 Nov, afternoon).** The whole classification of candidate units and the whole F-cell extraction are run on three models and the paper reports agreement and each model's results, as in the authors' previous paper: `claude-opus-5-5`, `gpt-6-astra` and `deepseek-v4-pro`, the last chosen as an inexpensive model of non-Western origin. This replaces the proposed cross-provider check on a 20 % subsample (B.3) and the choice of one primary model (B.6).
6. **A fourth audit by a second model before any paid production run (MB, 17 Nov)**: on acceptability in academic journals, on what is stored as input and output, on how to calibrate the prompts, and on whether everything needed before calibration exists (`docs/audits/PROMPT_AUDIT_2026-11-17.md`, `AUDIT_BRIEF_2026-11-17.md`). The calibration procedure put to the auditor is `docs/CALIBRATION_PROTOCOL_DRAFT_2026-11-17.md`; the collaborator's own readiness list is `docs/READINESS_BEFORE_CALIBRATION_2026-11-17.md`.
7. **Target date**: all model runs finished by 30 November 2026.

## B. Proposed, awaiting the authors

1. **Requests are packed by page**: one request holds all candidate units of one page with their paragraphs, each unit marked with its identifier, one output line per unit, fail-closed parser. This sends each paragraph once (1.45 M tokens instead of 3.38 M) and cuts 20,059 calls to about 5,500. It changes the instrument, because labels within a request are not independent. Test before adoption: MB's 120 units run both ways; packing is adopted only if packed-against-single agreement is no lower than single-against-single agreement.
2. **Reasoning setting fixed and low** for relevance; low against default tested for facets on the development sample; the chosen setting is a registered run parameter.
3. **Stability replicate on a registered 20 % stratified subsample**, same model, for each of the three models. (The cross-provider subsample of the first draft is replaced by A.5.)
4. **F-cells**: one primary extraction mode on all projects, the second mode on T1 and T2 only.
5. **General publications** (annual reports and the like) are restricted to the pages that name the CBDC, plus one page either side; documents devoted to the CBDC are always sent whole. This is the general rule left open in ADR-005.
6. **Combination of the three models**: dataset label = the value at least two of three models give; facets coded by all models on the union of units any model calls relevant; `NO_MAJORITY` reported and adjudicated where a project-level statement depends on it; a pre-registered agreement check for CN, HK and TW against the rest (calibration draft, section 7).
7. **Admissible interface.** Production, replicate and cross-provider runs go through the provider API with a run record (`docs/RUN_RECORD_SPEC.md`). MB holds a Claude Max plan, whose monthly API credit pays for API calls at list price; this changes who pays, not how the run is made.
8. **Duplicate found on 17 Nov**: `IL_BoI_2024` and `CAND-111` have the same text hash (two PDF files of the Preliminary Design for the Digital Shekel System, 2025). Proposed: link them in `EDITION_LINKS.csv`, re-run unitisation and add a CI check for equal text hashes. Israel stays T1.

## Cost estimate behind B (list prices of 17 Nov 2026; estimate, not a measurement)

Per model, full scope with B.1 to B.5 and the Batch API where offered: about 95 to 140 USD on claude-opus-5-5, 185 to 265 USD on gpt-6-astra, 40 to 50 USD on deepseek-v4-pro; three models together 320 to 455 USD, up to about 600 USD with a 30 % reserve for re-runs. Without these measures two to four times as much. Not included: translation of the 14 non-English T3 documents (readiness row 3), estimated at 10 to 20 USD. Unknowns: reasoning tokens of the classification (not yet measured), the token count of the Claude tokenizer on clean text (assumed 1.5 times the o200k count; 1.7 to 1.9 measured on layout text on 2 Nov), the number of re-runs after the third audit.
