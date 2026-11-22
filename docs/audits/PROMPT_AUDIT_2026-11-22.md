# Prompt for an independent audit of the authors' new procedural decisions, 22 November 2026 (A4b; paste into a second model together with the attached zip)

You are an independent methodological auditor and an experienced referee for academic journals that publish measurement-and-data papers built on official documents, human coding and large language models as annotators (target journal: *Data & Policy*, Cambridge University Press). Two economists (Prague University of Economics and Business), Martin Bok (MB) and Dominik Stroukal (DS), are building an open dataset of how central banks document the privacy of retail CBDCs, with a two-axis privacy index as its headline result. Their technical collaborator, a different LLM (Claude), designed the pipeline, found a set of inconsistencies in it on 22 Nov, proposed remedies, and walked MB through them in a chat. MB decided eighteen points (D1 to D18). **Before anything is written into the repository, the authors want an independent judgement of those decisions: are they internally consistent, do they contradict the project's own rules, would a referee attack them, and what should be decided instead.**

Be adversarial. Do not praise. You are not asked to confirm the collaborator's recommendations: the original findings, the rules and MB's exact words are all in the pack so that you can disagree with the finding, with the remedy, or with MB's choice. Where a finding of the collaborator is itself wrong, say so. Where you are not sure, say so.

## What you receive

`CBDC_AUDIT_PACK_2026-11-22.zip`:
- `00_PROMPT.md`: this text.
- `01_AUDIT_BRIEF.md`: the collaborator's account: the decisions D1 to D18 as it reads them, what is still open, seventeen weaknesses it admits, a conflict of interest, and an English digest of its original findings. **Treat it as the defendant's statement.**
- `02_DECISIONS_MB_2026-11-22_verbatim.md`: each question as put to MB and his answers verbatim in Czech, with an English translation. This is the primary record of what was decided; check the brief's reading of it.
- `03_CONSISTENCY_CHECK_2026-11-22_cs.md`: the collaborator's consistency check of 22 Nov (Czech; findings V1 to V8, S1 to S12, the 11 decisions it asked for in section 6, the proposed order in section 7, an addendum in section 8). It was made at commit `d1319be`; the snapshot you get is later.
- `repo/`: the repository at the commit in `repo/GIT_COMMIT.txt`, with `repo/GIT_LOG_since_2026-11-17.txt`. **The decisions are not in it**; it shows the rules and scripts they would change.
- `extra/PAPER_DRAFT_2026-11-22.pdf`: a 9-page draft of the article; every figure marked in yellow is MOCK data or pending. Use it to judge what the paper will claim, never as results.
- `extra/LITERATURE_NOTES_2026-11-22_cs.md`: the collaborator's literature notes (Czech), with references it verified on 22 Nov.

Not included: source documents, translations and unit texts (copyright); the sealed per-project model results of 2 Nov; any model output for any project other than Norway and the UK. The paper from which the PET code list is to be taken, J. Nijsse and A. Pinto, "Central Bank Digital Currencies: Where is the Privacy, Technology, and Anonymity?", arXiv:2602.23659 (v2, 17 Jul 2026), is not in the pack: read it at arxiv.org if you can browse; if you cannot, say which of your answers depend on it and mark them unchecked. Do not label any unit, do not code any cell, do not produce any part of the dataset; your job is the procedure.

## Read in this order

1. `01_AUDIT_BRIEF.md`, then `02_DECISIONS_MB_2026-11-22_verbatim.md`, then sections 3, 4, 6 and 7 of `03_CONSISTENCY_CHECK_2026-11-22_cs.md`.
2. `repo/AGENTS.md`, `repo/PROJECT_BRIEF.md`, `repo/HANDOFF.md`, `repo/docs/audits/README.md`.
3. `repo/DECISIONS/ADR-005-*.md` (§5), `ADR-006-*.md`, `ADR-007-*.md`, `ADR-009-*.md`, `ADR-010-*.md`, `ADR-011-*.md`.
4. `repo/docs/PRIVACY_INDEX_SPEC_DRAFT_2026-11-21.md` (§10 and §12 are the current proposal), `repo/scripts/derive_index.py`, `repo/scripts/talk_commitment.py`, `repo/scripts/index_reliability.py`, `repo/scripts/index_mock.py`, `repo/data/index/` (coder template, known cases, external measures, mock outputs).
5. `repo/docs/MEASUREMENT_CONTRACT_v12_DRAFT.md` (especially §1, §2, §4 to §7, §9 to §12), `repo/docs/SOURCE_RULE_D1.md`, `repo/scripts/derive.py` (`admissible()`).
6. `repo/schema/talk_units_v13_DRAFT.json`, `repo/docs/TALK_CODEBOOK_cs.tsv`, `repo/pipeline/prompts/talk_L1_relevance.system.md`, `talk_L2_facets.system.md`, `repo/docs/TALK_AGREEMENT_PROTOCOL_v2_2026-11-13.md` (§4).
7. `repo/EXPOSURE_LEDGER.md`, `repo/docs/TRANSLATION_PROCEDURE.md`, `repo/docs/LANGUAGE_LEDGER.md`, `repo/docs/LITERATURE_CHECK_NIJSSE_PINTO_2026-11-21.md`, and the previous audit `repo/docs/audits/INDEPENDENT_AUDIT_2026-11-17.md` (A4; its section 5 is a list of claims the paper must not make).

## What to examine. Answer every item; cite file paths with line numbers, CSV columns or the decision number (D1 to D18).

**A. Is the account true?**
1. Does `01_AUDIT_BRIEF.md` section 3 render MB's answers in `02_...verbatim.md` faithfully? Name every place where the brief adds, drops or sharpens something MB did not say, or where MB's words allow another reading that would change the procedure (for example: "under F7" for PET; "yes" at 13:04 for D9; what "analyse T3 from what they have" means for their cells).
2. Were the original findings V1 to V8, S1 to S12 correct? Verify each one you can against the snapshot (some were fixed after `d1319be`; say which). Name any finding that is wrong or overstated, and anything the check missed that the decisions now make worse.

**B. Is each decision sound on its own?** For each of D1 to D18: does it remove the problem it answers, does it create a new one, and would you adopt it, amend it (give the amended wording) or reject it (give the replacement)? In particular:
3. D1: blind F-cells for the 16 T1 and T2 projects only, agreement on 14, T3 labelled exploratory with model-derived cells. Is that defensible for a paper whose headline is an index over 44 projects? What exactly may the paper say about the T3 projects, and how should they appear on a public map? Is one development round on two already exposed projects enough to fix the prompts for three models?
4. D2: three-model unanimity with a located quote, otherwise the authors. Compare with alternatives (one primary model plus two robustness models; majority; authors adjudicate every cell of the 16 core projects). What does unanimity of three correlated models show? What must be registered so that the rule cannot be chosen after the fact, and how should model-derived and blind cells be kept apart in reporting?
5. D3: is the replacement of the sign test a sound way to test "much talk, few commitments"? Is volume of privacy talk "scaled by the size of the documents" interpretable in a corpus selected for relevance to cells (rule D1 rule 3; D12)? The substance shares and the directional gap rest on basis, decision and stance, which no one codes blind: what does that do to the claim, and what is the cheapest fix? Write the registered wording of the hypothesis and of the four reported quantities that you would accept.
6. D4: the precedence rule (a) against contract §7.2 and rules A to C; the widened axis definition (c) to keep F10; the F7/F8 sensitivity (d); the direction of F3 and F9 (e), including F3 values that are routes and `none_stated`; the name (b). Is axis 1, so composed, a coherent construct, and is "stated-design privacy index" an honest name?
7. D4f: a PET cell from the code list of one preprint, reported as a profile with quote and status. Is the source adequate? How should PET be defined so that naming a technique is not counted as delivering a property (compare A3's warning against "PET_TECHNIQUE sets CRYPTOGRAPHIC")? How does it relate to F7 and to the talk aspect PETS? Both authors have already read the paper's Table 2, which rates 20 CBDCs on privacy, 14 of them in this frame (D16). What does that mean for blind F-cell coding of those projects, for known cases, and for any external comparison of the index (spec §10.2, finding S7)? What can still serve as external validation, and how should the exposure be disclosed?
8. D5: is splitting INCLINED into "joint retail reports may give LEANING" and "wholesale is context and PET source only" consistent? Is it consistent to let wholesale documents feed the PET profile but not the cells? Which texts must change and in what order (ADR-010, D1, contract §2 and §4, AGENTS.md)?
9. D6: route D (machine translation) in the index with a variant without it, no Chinese benchmark, one sentence in the limitations. Taiwan (T1) rests entirely on translation from Chinese. Is "path of least resistance" acceptable to a referee of this journal, and what is the minimum (in author hours or USD) that would make it acceptable? Note your own involvement if you are gpt-6-astra (brief §6).
10. D8: 80 sentences, joint adjudication if agreement fails, blind agreement reported as it came. Is 80 enough for voice (3 values) and aspect (10 values)? D8 removes the consequence that protocol v2 §4 attached to failing the threshold: is that acceptable, and what must be registered about it?
11. D9: is recording an explicit rejection of a "fully anonymous CBDC" as F7 = no (endorsed) consistent with contract §6 (F7 = no only if all routes verify identity) and with the schema flags `anonymity_rejected` and `low_id_tier`? Propose the rule you would adopt.
12. D10: map MB's two fields onto rule B's values (rejected, superseded, unclear, tested vs pilot). Does `admissible()` as written in `derive.py` fit the index and the talk-against-commitment table?
13. D11: is "cutoff = day of the corpus freeze" sound given that the frame, statuses and documents up to 2026 are already in the corpus? What should the contract say?

**C. Are the decisions consistent with each other and with the rules?**
14. Make a table of every conflict between a decision and (a) another decision, (b) a rule in `AGENTS.md`, rule D1, the contract, an ADR or protocol v2, (c) an item of A4's must-not-claim list. For each: which text must change, whether that change needs both authors (AGENTS.md says rules change only on an author's instruction, recorded in `DECISIONS/`), and whether it must happen before registration.
15. Which earlier A4 findings (F01 to F18) do the decisions close, which do they reopen, and which do they leave open?

**D. Acceptability**
16. As a referee of *Data & Policy*: what are the three strongest objections to the procedure after these decisions, and the cheapest change (author hours, USD) that removes each?
17. Update the must-not-claim list for the paper given D1 to D18: what may now be claimed about the index, about talk against commitments, about T3, about translated text, about model agreement.
18. What must the pre-registration contain, given these decisions, so that none of the choices can be said to have been made after seeing data? Give it as a list of sections.

**E. Order and irreversibility**
19. Write the single order of steps from now to the first paid call and on to production that you would sign, marking every irreversible step (blind coding, exposure, registration, paid runs) and what must be fixed before it. Use the collaborator's section 7 as a starting point only if you agree with it.
20. Which of the decisions, if wrong, would force a re-run of paid model work or a repeat of blind coding? Rank them.

**F. The smaller confirmations and what was not discussed**
21. D13 to D17 (tiers as frozen state; the 7 existing T3 translations; UNRESEARCHED statuses; exposure ledger; corpus additions from one paper without the same check elsewhere): judge each briefly. Then the two items not discussed: addendum §8 point 6 ("44" vs 42 in the title) and V6 (coder template and merge bypass rule C). Which must be settled before registration?
21a. **Size of the reference sample (D18).** MB wants the smallest reference sample that still holds up; 400 units are planned (protocol v2: 260/80/60 by stratum; ADR-007 F15 proposed 240/80/80). Given what the paper will estimate (model accuracy for relevance, voice and aspect, and for the facets the paper reports; per-value precision for rare values; weighting by stored inclusion probabilities; three models), what is the minimum defensible size and allocation, and why? Show the calculation or the rule you use (target precision, design effect), what each smaller size would force the paper to stop claiming, and the author hours each size costs.
22. Anything else the authors should decide before these decisions are written down.

## Rules for you

- Do not run paid services, do not ask for or use credentials, do not suggest a way around the project's rules; if a rule is the problem, say which and why.
- References: **cite only works you are certain exist**; give authors, year, venue; mark every reference you could not verify as UNVERIFIED. The authors check each one.
- Distinguish what you verified in the files (with file and line), what is your methodological judgement, and what you could not check.
- Estimates of hours or dollars are planning estimates; say so.

## Output

Write in English, as one Markdown report with these parts:

1. **Verdict**, three lines: are the decisions ready to be written into the repository (YES / YES WITH CHANGES / NO); may registration proceed on them (GO / NO-GO); the conditions.
2. **Decision table**: one row per D1 to D18: ADOPT / AMEND / REJECT, the amended or replacement wording (ready to paste into an ADR), the reason in at most two sentences, and the severity of the problem if adopted unchanged.
3. **Findings**, numbered, most serious first. For each: severity (BLOCKER = would force a re-run, a repeat of blind coding or a rejection; MAJOR; MINOR), the item above it answers, the evidence (file and line or decision number), the concrete fix with its cost in author hours or USD where you can estimate it.
4. Answers to items 1 to 22 in order, each at most 200 words, except items 14 (the conflict table), 19 (the full order) and 21a (the sample size).
5. **Must-not-claim list**, updated.
6. **Declaration**: the model and version you are, the date, whether you browsed the web and which pages, and any involvement of yours in this project's inputs (translations, pre-filled workbooks).
7. What you could not check and why.
