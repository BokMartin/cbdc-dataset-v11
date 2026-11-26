# Audits by a second model: what they are for, how they are run, what they found

This is the standing reference for every audit of this project. Each audit has its own prompt, brief and report in this folder and its own disposition record in `DECISIONS/`. Updated 26 Nov 2026.

## 1. Why the project is audited

The pipeline (scripts, prompts, samples, documents such as this one) is designed and written by an AI assistant working with the two authors. Three things follow.

- **The designer cannot check itself.** An error in a script or an overstated sentence in a status report looks the same to its author the second time. A model from another vendor, given the files and told to be adversarial, has no stake in the account being right.
- **Some steps cannot be undone.** Human coders can be blind only once; paid model runs over the whole corpus cost several hundred dollars and days of work; a registered protocol cannot be quietly changed. Each such step gets an audit before it, not after.
- **The paper claims auditability.** A reader has to be able to see not only the data but how decisions were reached, which objections were raised and what was done about each. The audit reports and the disposition records are part of that evidence.

## 2. What an audit must answer

1. **Is the assistant's account true and complete?** Every figure recounted from the files; every "done" checked against what the code actually does; everything missing from the status list named.
2. **Is the procedure sound?** Logical and procedural errors: leakage between samples, units or contexts that differ between humans and models, rules that do not test what they claim to test, estimates presented as measurements.
3. **Would a referee accept it?** What the design can support and what the paper must not claim; which reporting standards apply; what the data availability statement can honestly promise.
4. **What would force a re-run or a retraction?** Anything that, found later, costs money, time or a claim.
5. **What should be done instead?** A concrete replacement, with its cost in author hours or dollars, not only an objection.

An audit does **not** establish that the measurement is valid. Validity rests on the authors' blind coding and verification; agreement between models and the approval of an auditing model are evidence of robustness and of procedure, not of truth.

## 3. Rules

1. **The auditor is a different model from the pipeline's author**, run by an author (MB) in a separate conversation. The model used and the date are recorded with the report.
2. **The assistant's brief is the defendant's statement, not evidence.** It lists the weaknesses the assistant already admits and names a file for every claim. The auditor is told to distrust it.
3. **The auditor receives the repository at a recorded commit** plus a small set of extras that hold source text and are never committed (workbooks, example requests, a diagnostic sample of units). It never receives the sealed per-project results of 2 Nov, and it is told not to label data or to produce any part of the dataset.
4. **The prompt asks numbered questions and fixes the output**: a verdict, findings ranked by severity (blocker, major, minor) with file and line, answers in order, and what could not be checked. References must be marked verified or unverified.
5. **The report is stored verbatim**, with the SHA-256 of the returned file in the disposition record.
6. **Every finding is checked before it is accepted.** The assistant verifies each checkable claim against the files and says which it could not check. An auditor can be wrong; a finding is not adopted because it was made.
7. **Dispositions belong to the authors.** The assistant proposes; each row of the disposition record becomes a decision only with an author's decision, dated. Where the authors overrule the auditor, the record says so and why (example: the euro area as a project of its own, ADR-005 §1.2).
8. **Repairs that need no author decision are made at once** and listed with their evidence (a test, a file), separately from what stays open.
9. **A finding is closed only by an artifact**: a test that fails without the repair, a regenerated file, an adopted ADR row. "Closed on paper" is itself something the next audit is asked to look for.

## 4. Register

| | Date | Before which step | Snapshot | Verdict | Files | Dispositions |
|---|---|---|---|---|---|---|
| A1 | 28 Oct 2026 | external consultation on the contract, framing and the Norway and UK development cases, before the first production design | consultation pack of 27 Oct | recommendations by rule and case | (consultation text outside the repository) | [ADR-001](../../DECISIONS/ADR-001-consultation-2026-10-28-dispositions.md) |
| A2 | 2 Nov 2026 | the consultation of 6 Nov and any further model screen | pack of 2 Nov | 21 items and five ranked problems (tests and schema out of step, rule C partly implemented, sealed-survey recounts) | [prompt](PROMPT_OPENAI_AUDIT_2026-11-02.md), [report](INDEPENDENT_AUDIT_OPENAI_2026-11-02.md) | [ADR-002](../../DECISIONS/ADR-002-audit-2026-11-02.md) |
| A3 | 13 Nov 2026 | the main human coding round | `4d4f142` | **do not start the coding round**: frame, duplicate editions and benchmark translations in production, scorer, different context for humans and models | [brief](AUDIT_BRIEF_2026-11-13.md), [prompt](PROMPT_AUDIT_2026-11-13.md), [report](INDEPENDENT_AUDIT_2026-11-13.md) | [ADR-005](../../DECISIONS/ADR-005-audit-2026-11-13-dispositions.md) |
| A4 | 17 Nov 2026 | the paid model runs (calibration and production on three models) | `7e6e4c5` | **calibration NO-GO, production NO-GO**; 18 findings, 8 blockers; a 24-step replacement protocol | [brief](AUDIT_BRIEF_2026-11-17.md), [prompt](PROMPT_AUDIT_2026-11-17.md), [report](INDEPENDENT_AUDIT_2026-11-17.md) | [ADR-007](../../DECISIONS/ADR-007-audit-2026-11-17-dispositions.md) |
| A4b | 22 Nov 2026 | writing the authors' decisions of 22 Nov (D1 to D18) into the repository; registration | `706b2e8` | **decisions not ready to record as adopted; registration NO-GO**; 10 findings, 7 blockers; D7, D12, D13 adopt, D9 reject, the rest amend | [brief](AUDIT_BRIEF_2026-11-22.md), [prompt](PROMPT_AUDIT_2026-11-22.md), [MB's answers](DECISIONS_MB_2026-11-22_verbatim.md), [report](INDEPENDENT_AUDIT_2026-11-22.md) | [ADR-012](../../DECISIONS/ADR-012-audit-2026-11-22-A4b-dispositions.md) |
| A4c | 23 Nov 2026 | F-cell extraction prompt v12.1, before adoption and the development round on NO and UK; Part B: codebook v0.4 and relevance prompt v0.3 | `b60f444` | **development round NO-GO; production NO-GO**; 13 findings, 5 blockers; proposes amendments A1 to A12 and prompt v12.2; Part B conditional adoption. Authors adopted P1 to P4 and B1 as recommended (23 Nov) | [brief](AUDIT_BRIEF_2026-11-23.md), [prompt](PROMPT_AUDIT_2026-11-23.md), [prompt audited](EXTRACTION_PROMPT_v12.1_audited_2026-11-23.md), [test document](TEST_DOCUMENT_synthetic_2026-11-23.md), [report](INDEPENDENT_AUDIT_2026-11-23.md) | [ADR-013](../../DECISIONS/ADR-013-audit-2026-11-23-A4c-extraction-prompt.md) |

| A5 | 26 Nov 2026 | after production, before verification of the core cells and finalization of the results | `e61a562` plus the open PRs 28, 12, 7, 6 as diffs; pack `CBDC_RESULTS_AUDIT_PACK_2026-11-26.zip` (SHA-256 `786a254275d721743ed9632cfa3762e705557c4b61116a6bb7d0ecb875f9db59`) | **supervisor preview GO with conditions; verification with the workbooks of 24 Nov NO-GO; index and hypothesis in the article, results on the website, submission NO-GO**; 13 findings, 5 blockers; 31 deviations (R-01 to R-31); must-not-claim list; 8-step plan | report SHA-256 `a9df9534871adc1b70e8cbfcab38c62650a795be16031e280006e0ef93c3e67d`, prompt `e8fdceab2d825196264f8a8aeb42e4d3ff13791ea5dcda22a04485abd107ed58`, brief `60eb684184cece94d53ce4d92338bf1b9bee71bf185182723e7c6bff0ae4569e` (held in the project folder `audit-2026-11-26/`; see the note below) | [ADR-018 draft](../../DECISIONS/ADR-018-audit-2026-11-26-A5-dispositions-DRAFT.md) |

**Note on A5.** The report, the prompt and the brief of A5 name per-project cell values and talk results of blind core
projects, which stay out of the repository until verification is locked (AGENTS.md; ADR-017). They are therefore registered
here by SHA-256 and will be committed unchanged, with these hashes, when both verification passes are locked. Errata to the
brief found by the audit and checked: 83 keys with a value (not 85); EX2 cached-input share 32.18 / 30.54 / 43.89 % (not 32
to 38 %); the pre-amendment stage EX attempted 5 / 3 / 6 keys and completed 2 / 2 / 6 (not "six per model").

What each audit covered step by step is the column "audited by a second model" of the checklist in [`PROJECT_BRIEF.md`](../../PROJECT_BRIEF.md), section 4. A step changed after its audit is marked "not re-audited" there.

## 5. State of the earlier findings on 26 Nov 2026

The reading of audit A5 (answer 2), checked by the assistant against the files; "closed" only with an artifact (rule 9).

| Finding | State | Artifact, or what is missing |
|---|---|---|
| A4 F01, F06, F15 validity, reference separation, reference sample | **open** | 80-sentence facet agreement (`docs/FACET80_AGREEMENT_2026-11-23.md`); exposure registry now with the pages of the verification workbooks (`data/units/EXPOSURE_REGISTRY_2026-11-26.csv`); the reference sample of 400 is not drawn |
| A4 F02 extraction instrument | partly closed | prompt v12.2, check `v122.py`, reducer with tests; source-layer routing (A5 finding 2) and search closure (A5 finding 6, repaired 26 Nov) kept it open |
| A4 F03 inputs frozen | partly closed | freeze and amendment hashes; the freeze tag was not pushed; Registration B absent |
| A4 F04, F08 translation | open | route D and its flag exist; the source check of `translation_uncertain` observations (ADR-013 P4) has no record |
| A4 F05 run-record check | closed | `tests/test_run_record.py` |
| A4 F07, F12 packing | reopened | page packing reinstated for L1 by ADR-015 |
| A4 F09 publisher metadata | partly closed | issuer check (`docs/ISSUER_CHECK_2026-11-23.md`); decision authority and layer are unknown in every extraction header (A5 finding 2) |
| A4 F10 absence, "first", highest rung | partly closed | status priority in the reducer; the date rule is an open author decision |
| A4 F11 "U" label | closed for new labels | L1 rules, codebook, ADR-013 B1 |
| A4 F13 availability statement | **open** | no rights manifest or data availability statement |
| A4 F14 companion links | open | companion F3 routing exists, no companion is classified in production |
| A4 F16, F17, F18 stopping rule, provider identity, budget | open / closed / closed | no confirmation round; model strings and usage in every run record (`docs/RUN_INCIDENTS_2026-11-26.md`) |
| A4b finding 1 (rule C bypass) | closed | `admissible()` in `scripts/derive.py`, tested |
| A4b D1, D2 blind coding | replaced | ADR-017 (MB only): verification of model citations; two-pass workbooks of 26 Nov |
| A4b D18 reference sample | open | adopted, not drawn |
| A4c findings 1 to 3 | closed | prompt v12.2, typed fields, acceptance fixtures |
| A4c finding 4 cross-document links | open | reducer keeps references, links nothing |
| A4c finding 9 shared translations | open | no record of a source check |
| A4c finding 10 F11, F12, PET | open | raw observations only; PET of unknown scope withheld since 26 Nov |
| A4c finding 11 output budget | open | 37 / 58 / 4 persistent failures; 10 responses lost every claim (`docs/RUN_INCIDENTS_2026-11-26.md`) |
| A5 findings | see the [ADR-018 draft](../../DECISIONS/ADR-018-audit-2026-11-26-A5-dispositions-DRAFT.md) | |

## 6. The next audits

- **A5** was planned before the freeze and the first production call; it was held after production (26 Nov), because production ran before an audit (ADR-016; deviation R-03 of the A5 brief).
- **A6, before submission.** Scope: the manuscript against the data. Every number and every project-level statement traced to a file; every claim checked against the must-not-claim list of A4 (section 5 of that report); the data availability statement against what is actually deposited.

## 7. How to run one

1. Write the brief (`AUDIT_BRIEF_<date>.md`): what exists with file names, what the authors decided, what is proposed and not decided, the money and time at stake, and the weaknesses already known.
2. Write the prompt (`PROMPT_AUDIT_<date>.md`): role, what the auditor receives, reading order, numbered questions, required output. Start from the prompt of the last audit.
3. Commit and push; wait for a green CI run. Build the pack from that commit: `scripts/audit/build_audit_pack.py` (documents, units, translation benchmark) or `scripts/audit/build_run_audit_pack.py` (before model runs). The pack is a zip with the prompt, the brief, the repository and the extras; check it for credentials before it leaves.
4. An author pastes the prompt into the second model and attaches the zip.
5. Store the report here unchanged. Open a disposition record `DECISIONS/ADR-<n>-audit-<date>-dispositions.md`: the hash of the report, what was verified of the auditor's claims and how, proposed dispositions row by row, consequences for time, money and claims.
6. Repair what needs no decision, with tests. Record the authors' decisions as they come. Update sections 4 and 5 of this file and the checklist of `PROJECT_BRIEF.md`.
