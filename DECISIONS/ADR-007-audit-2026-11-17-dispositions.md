# ADR-007: independent audit of 17 Nov 2026 (A4, before the paid model runs): verification and proposed dispositions

Status: **proposed by the pipeline author on 17 Nov 2026; no author has decided any row.** Report: `docs/audits/INDEPENDENT_AUDIT_2026-11-17.md` (SHA-256 of the returned file b226b7f2ab9cb64a819a69db4efecbdc2d868272a8305349c748f9b7b976d5c5), prompt and brief beside it, audited snapshot `7e6e4c5`. Verdict of the auditor: calibration NO-GO, production NO-GO, each until the listed repairs.

## 1. What the pipeline author checked of the auditor's claims

| Finding | Checked how | Result |
|---|---|---|
| F03 duplicate Israel text; 14 development units from documents no longer in the unit manifest; empty text cell `CODE!J42` | recount from the manifests; the returned workbook against the generated one | confirmed. The 14 units come from 11 documents that the authors moved out of evidence on 13 Nov after the sample was drawn. `J42` holds text in the generated workbook and is empty in the returned one: the cell was emptied on the coder's side, which is why row 42 has no label |
| F04 translation ingest accepts a response without per-call metadata | `ingest_translations.py` lines 33, 52 to 57, 98 to 100 | confirmed: every hash comparison runs only if the metadata file exists; `--expect` is optional. The description "fail-closed" was wrong |
| F05 run-record check passes a fictitious run | reading of `run_statement.py` | confirmed: presence of fields and column names only. The statement of 17 Nov that CI "enforces" the specification was too strong; corrected in `docs/RUN_RECORD_SPEC.md` |
| F06 the draw excludes only unit identifiers | `draw_agreement_sample.py` | confirmed |
| F09 117 of 208 unit-manifest rows disagree with the issuer ledger on `issuer_type` | join of the two files | confirmed: 113 rows say `not_recorded` |
| F12 a page request shows a unit more context than its single request | `build_requests.py` (union of windows) | confirmed by construction |
| F13 Data & Policy does not accept "available on request" | the journal's research-transparency policy, fetched 17 Nov | confirmed; the specification said exactly that and is corrected |
| F18 "283 companions linked to evidence of the same year" | `COMPANION_LINKS_2026-11-13.csv` | confirmed false: same year 194, nearest year 87, no link 2; the generated brief is corrected |
| Reference R1 (GUIDE-LLM, Nature Human Behaviour 2026) | the checklist's own site | exists, items A.1 to G.1 as the auditor describes. R2 to R5 are well-known works; not re-fetched. R7 to R9 (DeepSeek documentation) not re-fetched |
| F01, F07, F10, F15, F16, F17 | methodological judgments | not checkable by recount; the author of this ADR agrees with them in substance (section 2) |
| F02, F08, F11, F14 | consistent with the readiness list and the files | accepted |

## 2. Proposed dispositions

| # | Finding (severity) | Proposed disposition | Needs |
|---|---|---|---|
| F01 | Verification does not establish validity (BLOCKER for the strong claims) | **Blank double coding of voice and aspect** on about 120 relevant units of the reference, both authors, before any facet output is shown; the five other facets are released as model-coded and exploratory. Planted errors are kept and reported only as an attention check, never as an accuracy bound. Source-first checks of project statements include model negatives and earlier documents | authors (the choice ADR-006 A.3 left open; about 2 to 4 hours each) |
| F02 | F-cell extraction is not a v12 instrument (BLOCKER) | **The commitment layer leaves the November target.** November: talk layer. December: adopt contract v12, rebuild generator, schema validation, comparison and replay on two status axes, calibrate on NO, UK and three contrasting cases the authors agree to expose. If December does not suffice, reduce to F1 to F4, F7, F8 | authors |
| F03 | Inputs not frozen (BLOCKER) | Canonical publication identity; link the Israel pair and regenerate; identifiers bound to a unitisation version; raw and displayed text hashes; row 42 coded again from the registered text; the 14 units kept as marked historical development material | MB: yes to the Israel link, row 42, row 71 |
| F04 | Translation ingest fails open (BLOCKER) | Rebuild: metadata and every hash required, expected inventory mandatory, duplicate identities rejected, unitisation reads only pinned successful manifest rows; negative fixtures in CI; re-verify the three existing runs | none |
| F05 | Run-record check certifies a fictitious run (BLOCKER) | Rebuild: typed schema, legacy allowlist, hash and inventory verification, attempts separate from logical requests, endpoint enumerations; negative fixtures in CI | none |
| F06 | Reference separation not implemented (BLOCKER) | Exposure registry of every displayed and model-labelled span; exclusion by canonical block. With page packing dropped (F07, F12) the block is the displayed paragraph plus duplicates; otherwise the page | authors approve the estimand |
| F07 | Factor rule is not a non-inferiority test (BLOCKER for the savings) | **Drop page packing** (it changes the instrument, needs page-level exclusion and cannot be shown equivalent on 120 units). Keep one unit per request, the view the coders saw. Test only the reasoning setting, with the auditor's paired rule; if inconclusive, provider default. Batch API and cached system prompt stay (operational) | authors (cost rises; section 3) |
| F08 | Language coverage and translation restrictions conflict (BLOCKER for unrestricted claims) | Translate the 14 T3 documents before the freeze; one adopted rule for what machine-translated text may support; unjudgeable pairs shown as their own outcome (S 46.7 %, W 4.0 %, X 4.6 %, M 24.2 %, not judgeable 20.5 %) | authors; OpenAI credit |
| F09 | Publisher metadata and institutional voice conflated (MAJOR) | One reviewed header source for humans, models and analysis; speaker, publisher and decision authority as separate fields; an authority filter for talk milestones | authors review about 208 rows (2 to 5 hours) |
| F10 | Absence, "first" and "highest rung" exceed what is observed (MAJOR) | Wording: "earliest located in the searched corpus"; unknown kept apart from no finding; a status and basis vector instead of a ladder; raw model tuples kept, incoherent majority tuples flagged | authors (changes the event-history wording of ADR-005 §4) |
| F11 | "U" mixes unusable text and coder uncertainty (MAJOR) | U = content cannot be determined from the text; a separate uncertainty note; both coders re-instructed with invented examples; audit of 60 excluded and 60 retained units | MB, DS |
| F12 | Packing changes context and dependency (MAJOR) | Resolved by dropping packing; the facet prompt is told that a unit admitted by another model is not assumed relevant and gets an explicit not-applicable channel | none |
| F13 | Availability promise conflicts with the journal (MAJOR) | Rights and access manifest; deposit of all lawful analytical outputs; restricted-access procedure stated concretely; draft statement of the auditor (question 19) as the starting text | authors |
| F14 | Companion links are navigation, not proof of endorsement (MAJOR) | Wording corrected; URLs joined into the links file; claim-specific verification when a companion is used as endorsement source; one cutoff date adopted | authors (cutoff) |
| F15 | Sampling and scoring do not support population or rare-value claims (MAJOR) | Reference of 400 as a probability design with recorded inclusion probabilities (D/N/R 240/80/80); clustered bootstrap; second aspect and flags scored if used; replicate at request level | none beyond approval |
| F16 | No-change is not a stopping rule (MAJOR) | Adopt the auditor's rounds: at most three rounds of 40 units (24/8/8) with 20 deep-reviewed, a single proven defect may trigger a change, a fresh confirmation set of 40, scope reduced where gates are not met | authors |
| F17 | Provider identity and diversity (MAJOR) | Archive each provider's model, endpoint, price and terms pages on the day of the run; capability probes under a small cap; fixed sentinel requests for drift; refusals counted separately; the CN/HK/TW check reported against the blind reference within matched strata, not as agreement | none |
| F18 | Arithmetic and budget documentation (MINOR / MAJOR) | Brief corrected; a per-stage usage and price ledger fed by measured probe usage replaces the estimate | none |

## 3. Consequences the authors should see before deciding

1. **Time.** The auditor's sequence up to the first production call has about a dozen steps with author input (scope, C0, metadata, U rule, three rounds, confirmation set, 400-unit relevance reference by both authors, 120-unit blank facet coding). A talk layer run on three models by 30 November is possible only if these are done within about ten days; the commitment layer is not.
2. **Money.** Without page packing and with the provider's default reasoning the talk layer on three models is estimated at 350 to 850 USD (Batch API where offered; the range is the unmeasured reasoning usage). The capability probe of the auditor's step 8, a few dollars, replaces this estimate with a measurement before anything else is spent.
3. **Claims.** With voice and aspect independently coded the paper can call relevance, voice and aspect validated and the remaining facets model-coded. Without it every facet is exploratory, and the talk × commitment table and the event history rest on exploratory labels.
