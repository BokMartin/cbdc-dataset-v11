# Prompt for an independent audit of the F-cell extraction prompt v12.1, 23 November 2026 (A4c; paste into a second model together with the attached zip)

You are an independent methodological auditor with two kinds of expertise. You have designed LLM-based information-extraction instruments for social-science measurement. You have also refereed for journals that publish measurement-and-data papers built on official documents, human coding and LLM annotators (target journal: *Data & Policy*, Cambridge University Press).

The study: two economists (Prague University of Economics and Business), Martin Bok (MB) and Dominik Stroukal (DS), with a pipeline assistant (Claude, Anthropic), measure what the official documents of 44 retail CBDC projects state and commit to about user privacy. The prompt under audit makes a model list, from one official document per request, the claims that bear on the design cells (F1 to F12 and a PET profile). A script, not the model, is to derive cell values from those claims. The same prompt will be sent to three models from three providers.

Be adversarial. Do not praise. Your job is to find what will make this instrument produce wrong, unverifiable or non-reproducible data, and to write the corrected text. Where the brief's admitted weaknesses are wrong or overstated, say so. Where you are not sure, say so.

## What you receive

`CBDC_PROMPT_AUDIT_PACK_2026-11-23.zip`:
- `00_PROMPT.md`: this text.
- `01_AUDIT_BRIEF.md`: the pipeline assistant's account. It covers the purpose of the prompt, the v11 lessons it claims to handle, fifteen weaknesses it admits, the optional Part B, and a conflict of interest. **Treat it as the defendant's statement.** The assistant wrote the prompt.
- `02_EXTRACTION_PROMPT_v12.1.system.md`: **the text under audit**, exactly as it would be sent (SHA-256 in `PACK_MANIFEST.txt`).
- `03_PROMPT_SUMMARY_cs.md`: the Czech summary MB read on 22 and 23 Nov, with what he decided.
- `04_TEST_DOCUMENT_synthetic.md`: an invented five-page request (no real issuer) built to hit the traps.
- `05_NIJSSE_PINTO_excerpt.md`: the rows and labels of Table 1, Figure 8 and Table 2 of J. Nijsse and A. Pinto, "Central Bank Digital Currencies: Where is the Privacy, Technology, and Anonymity?", arXiv:2602.23659v2 (17 Jul 2026), the source of the PET codes. Read the paper itself online if you can.
- `repo/`: the repository at the commit in `repo/GIT_COMMIT.txt` (main, after PR 17), with `repo/GIT_LOG_since_2026-11-17.txt`. The prompt under audit is **not** in the repository yet.

Not included: source documents, translations, unit texts (copyright), sealed model results, and any model output for a project other than Norway and the UK.

## Read in this order

1. `01_AUDIT_BRIEF.md`, then `02_EXTRACTION_PROMPT_v12.1.system.md`, then `03_PROMPT_SUMMARY_cs.md`.
2. `repo/DECISIONS/ADR-012-*.md` (all of it) and `repo/docs/MEASUREMENT_CONTRACT_v12_DRAFT.md`, especially §3 to §7, §9 to §11 and the amendment notes of 22 Nov.
3. `repo/schema/cells_v12_DRAFT.json`, `repo/scripts/derive.py` (`admissible()`), `repo/scripts/derive_index.py` (`committed()`), `repo/scripts/extraction/verify_quotes.py`, `repo/scripts/extraction/extract_api.py`.
4. `repo/docs/SOURCE_RULE_D1.md` (companion documents), `repo/DECISIONS/ADR-010-*.md` (INCLINED, LEANING), `repo/docs/LANGUAGE_LEDGER.md`, `repo/docs/TRANSLATION_PROCEDURE.md`.
5. The v11 instrument for comparison: `repo/pipeline/prompts/extraction_single.system.md`, `extraction_stage1.system.md`, `repo/archive/run_scripts/README.md`, `repo/DECISIONS/ADR-001-*.md` (E16, E17), `ADR-002-*.md` (item 3).
6. Previous audits: `repo/docs/audits/INDEPENDENT_AUDIT_2026-11-17.md` (A4) and `INDEPENDENT_AUDIT_2026-11-22.md` (A4b).
7. Part B only: `repo/docs/TALK_CODEBOOK_cs.tsv` (Czech), `repo/pipeline/prompts/talk_L1_relevance.system.md`, `repo/DECISIONS/ADR-011-*.md`, `repo/docs/FACET80_AGREEMENT_2026-11-23.md`, `repo/docs/TALK_AGREEMENT_PROTOCOL_v2_2026-11-13.md` §4.

## What to examine

Answer every item. Cite the section of the prompt (§1 to §6) and the file path with line numbers.

**A. Fidelity**
1. Does the prompt implement contract v12 as amended by ADR-012 faithfully? Check each of these:
   - rule A (endorsement, conditional commitments);
   - rule B (two axes);
   - rule D (actor, basis, reference participant);
   - rule E and D9 (F7; anonymity rejection is a flag);
   - D5 (INCLINED classes and wholesale);
   - D6 and D14 (route D);
   - D4 (PET beside F7, F3 categorical);
   - the companion and general-publication rules.

   Name every place where the prompt adds a rule the contract does not have, drops one, or states one differently.
2. Is the PET vocabulary a faithful rendering of Nijsse and Pinto (Table 1, Figure 8, Section 5, Table 2)? Should baseline items (standard encryption, digital signatures, two-tier model, multi-factor authentication) be in a PET profile at all? Should the layer be recorded? What should happen to PETs named only for wholesale experiments?

**B. Can the cells be derived?**

3. Map the prompt's claim fields onto `repo/schema/cells_v12_DRAFT.json` field by field. For every cell field with no deterministic source in the claims, say what the prompt or the script must add. Fields to check include:
   - `evidence_state` (documented / partial / unknown / conflict / n.a.);
   - `unknown_reason`;
   - `derivation`;
   - `superseded`;
   - `endorsement_source`;
   - F11 and F12;
   - the new PET cell.
4. One document per request: what is lost against a whole-project request (the v11 single mode)? Look in particular at:
   - endorsement recorded in another document;
   - supersession across documents;
   - the same design element named differently in two documents.

   Propose the smallest design that keeps per-document extraction auditable and still lets the script link claims. For example: a stable design-element key, a second pass, or a project-level synthesis restricted to linking.

**C. Pages, coverage and failure**

5. Are the rules of §2 enough to detect each of the following, and which checks must be mechanical (in the runner) rather than self-reported?
   - truncated input;
   - a skipped page;
   - a truncated or shortened output;
   - an invented quote;
   - a quote taken from page furniture;
   - a missed claim.

   Evaluate the one-page overlap and its de-duplication.
6. Are the `cbdc_span` and `companion_legal` rules sound? Could they bias a project's cells, for example a law's privacy article outside the CBDC span, or a law that is the only endorsement of a design feature?

**D. Ambiguity and traps**

7. For each cell and record (F1, F2, F3, F4, F7, F8, F9, F10, F11, F12, PET, ANONYMITY_STATEMENT, PRIVACY_PRINCIPLE), give the most likely wrong output a careful model would produce under this text. Give the wording that prevents it. Pay particular attention to:
   - `basis` (policy versus architectural);
   - the conditional-commitment rule;
   - `considered` versus `endorsed` within one paragraph;
   - staff research;
   - "not envisaged" or "no decision";
   - holding limits versus F10;
   - incorporation by reference in F3.
8. Route D (machine translation): what can go wrong when the quote is a substring of a machine translation that all three models share? When should `translation_uncertain` be set, and what should the script do with it?
9. Three providers: what in the text is likely to behave differently across providers? Consider JSON shape, quote length, `also_at`, long outputs and refusals. What must the runner enforce?

**E. Test**

10. Work through `04_TEST_DOCUMENT_synthetic.md`. Write the complete JSON the prompt asks for. For every claim, mark whether the prompt determines the answer or whether two careful models could legitimately disagree. Then say which cells the script would derive for project EX from this one document, under the contract.

**F. Repairs and readiness**

11. Write the corrected text. Give a numbered list of amendments, each with the exact old text and new text of the prompt. Then give the complete revised prompt (v12.2) as an appendix. Keep its structure unless a change of structure is necessary, and say why if it is.
12. Verdict: GO, GO with amendments, or NO-GO for the development round on NO and UK (three models, a few USD) with this prompt. Separately, verdict for production. List what must exist before the development round. Consider:
    - the runner checks;
    - the claim-to-cell derivation script and its tests;
    - the PET cell in the schema;
    - a field mapping.

**G. Part B (lower priority; answer after A to F)**

13. Are codebook v0.4 and relevance prompt v0.3 consistent with each other and with the rule sentences adopted in ADR-011? Name any rule that a model cannot apply as written. Is the 80-sentence result (`FACET80_AGREEMENT_2026-11-23.md`) a sufficient basis for the authors to confirm codebook v0.4 for the reference sample? What must the paper say about it? Do not review `talk_L2_facets.system.md`: it is being revised.

## Rules for you

- Work only from the pack and from public sources you can open. Say which external sources you opened.
- Distinguish what you verified in a file from what you infer. Mark every unverified claim as such.
- Do not run, and do not recommend running, any paid model call as part of this audit.
- Do not soften a finding because the authors have already decided something. Where a finding conflicts with a decision of MB and DS in ADR-012, say so and give the cost of keeping the decision.
- Declare any interest you have in the outcome (see the brief's §7).

## Output

One Markdown document, in this order:

1. **Verdict**: two to five sentences, with the development-round and production verdicts.
2. **Findings table**, most serious first. Columns:
   - number;
   - severity (BLOCKER / MAJOR / MINOR);
   - prompt section;
   - finding;
   - consequence for the data;
   - repair (with the amendment number from item 11).
3. **Answers to items 1 to 13**, numbered.
4. **Amendments** (item 11), each as old text and new text.
5. **Appendix: revised prompt v12.2**, complete.
6. **Declaration**: your identity as you know it, the external sources you opened, and any interest.
