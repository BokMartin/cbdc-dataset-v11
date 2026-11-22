# Audits by a second model: what they are for, how they are run, what they found

This is the standing reference for every audit of this project. Each audit has its own prompt, brief and report in this folder and its own disposition record in `DECISIONS/`. Updated 21 Nov 2026.

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

What each audit covered step by step is the column "audited by a second model" of the checklist in [`PROJECT_BRIEF.md`](../../PROJECT_BRIEF.md), section 4. A step changed after its audit is marked "not re-audited" there.

## 5. State of the A4 findings on 21 Nov 2026

| Finding | Severity | State | Evidence or what is missing |
|---|---|---|---|
| F01 verification does not establish validity | blocker for strong claims | **open, authors** | decision on blank double coding of voice and aspect |
| F02 F-cell extraction is not a v12 instrument | blocker | **open** | contract v12 not adopted; generator, validation, comparison at v1.1 |
| F03 inputs not frozen | blocker | partly closed | duplicate removed and tested (`tests/test_corpus_identity.py`); identifiers not yet bound to a unitisation version; development sample not yet reconciled by the authors |
| F04 translation ingest fails open | blocker | partly closed | ingest requires metadata, hashes and an expected inventory; unitisation still reads translations found on disk |
| F05 run-record check passes a fictitious run | blocker | closed | `tests/test_run_record.py` |
| F06 reference separation not implemented | blocker | **open** | exposure registry and block-level exclusion not built |
| F07 factor rule is not a non-inferiority test | blocker for the savings | closed by decision | page packing dropped (MB, 17 Nov); the reasoning test, if run, uses the auditor's paired rule |
| F08 language coverage and translation restrictions conflict | blocker for unrestricted claims | **open, authors** | T3 translation inconsistency (ADR-007 §4.4); benchmark not adjudicated; scorer does not yet show "not judgeable" as an outcome |
| F09 publisher metadata and institutional voice conflated | major | partly closed | one header source, tested; the content awaits the authors' review |
| F10 absence, "first" and "highest rung" | major | open, authors | wording and status vector to adopt |
| F11 "U" mixes unusable text and uncertainty | major | open, confirmed by data | the authors agree on 6 of 30 "U" labels; adjudication workbook issued |
| F12 packing changes context | major | closed by decision; facet prompt change open | |
| F13 availability promise conflicts with the journal | major | open | wording removed from the specification; manifest and statement not written |
| F14 companion links are navigation | major | partly closed | brief wording corrected; cutoff date and claim-specific verification open |
| F15 sampling and scoring | major | open | reference design proposed, not adopted |
| F16 stopping rule | major | open, authors | rounds as proposed by the auditor, not adopted |
| F17 provider identity | major | open | to do at the capability probe |
| F18 arithmetic and budget documentation | minor / major | partly closed | brief corrected; usage ledger not built |

## 6. The next audits

- **A5, before the freeze and the first production call.** Scope: everything changed since `7e6e4c5`: the repairs listed above, the runner and its failure tests, the exposure registry and the draw, the repaired codebook and prompts, the calibration rounds as run (not as planned), the confirmation set, the combination rule for three models, the registered analysis outputs, the cost ledger. For the commitment layer, the adopted contract v12 and the rebuilt extraction instrument. Question to answer: is there anything left that would force a re-run after production?
- **A6, before submission.** Scope: the manuscript against the data. Every number and every project-level statement traced to a file; every claim checked against the must-not-claim list of A4 (section 5 of that report); the data availability statement against what is actually deposited.

## 7. How to run one

1. Write the brief (`AUDIT_BRIEF_<date>.md`): what exists with file names, what the authors decided, what is proposed and not decided, the money and time at stake, and the weaknesses already known.
2. Write the prompt (`PROMPT_AUDIT_<date>.md`): role, what the auditor receives, reading order, numbered questions, required output. Start from the prompt of the last audit.
3. Commit and push; wait for a green CI run. Build the pack from that commit: `scripts/audit/build_audit_pack.py` (documents, units, translation benchmark) or `scripts/audit/build_run_audit_pack.py` (before model runs). The pack is a zip with the prompt, the brief, the repository and the extras; check it for credentials before it leaves.
4. An author pastes the prompt into the second model and attaches the zip.
5. Store the report here unchanged. Open a disposition record `DECISIONS/ADR-<n>-audit-<date>-dispositions.md`: the hash of the report, what was verified of the auditor's claims and how, proposed dispositions row by row, consequences for time, money and claims.
6. Repair what needs no decision, with tests. Record the authors' decisions as they come. Update sections 4 and 5 of this file and the checklist of `PROJECT_BRIEF.md`.
