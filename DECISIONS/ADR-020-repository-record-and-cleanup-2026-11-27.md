# ADR-020: the repository as the record of the procedure; clean-up after audit A6 (27 Nov 2026)

Status: decisions 1 to 3 by MB on 27 Nov 2026 (decision cards in the project thread, 14:56 UTC); the rest are the assistant's
implementation of them and of audit A6, marked as such. DS has not confirmed.

## Context

MB, 27 Nov 2026: the repository should be at the current version (v12, not v11) and as clean as possible, with what need not
be there removed and backed up; then: "it is key that git contains everything essential about our procedure to the current
results". The assistant proposed merging PRs 29, 7 and 6, removing 25 superseded dated files, deleting the topic branches and
renaming the repository. MB asked for an audit by a second model first. Audit A6 (hashes in
[`docs/provenance/README.md`](../docs/provenance/README.md), section 5) found the proposal unsafe; its findings checked by the
assistant are listed below.

## Decisions

1. **Nothing is deleted to make the repository clean** (MB asked that git hold everything essential; A6 §9 to §11). The 25
   files once proposed for removal stay: they are the only record of intermediate stages that audits A2 to A4b read, and one
   (`data/manifest/ISSUERS_PROPOSED_2026-11-13.csv`) is an input of `scripts/review/record_issuers.py`. Superseded dated files
   are indexed instead, in [`archive/INDEX.md`](../archive/INDEX.md), generated and checked in CI. The v11 line and the mock
   index data stay, labelled there as retired. This narrows AGENTS.md rule 5 ("superseded files leave through git"): a dated
   file is superseded in the index, not removed.
2. **Norges Bank texts** (MB, card, 27 Nov 2026 14:56 UTC: "keep, if the licence allows"). The development profiles of 2 to
   10 Nov contain the full text of seven Norges Bank publications as sent to the model
   (`data/worked_profiles/runs_v2_NO_en*/requests/single.user.txt.gz`, `.../playground_log.txt`), committed under ADR-003.
   Norges Bank permits copies "provided that Norges Bank is quoted as the source", without changes to the content
   (`data/registry/LICENCES_BY_INSTITUTION_2026-11-02.csv`, row NO; https://www.norges-bank.no/en/disclaimer/). They stay as an
   exception to the rule on source text, recorded here and in LICENSE: Norges Bank is the source and owner, the CC BY
   licence of this repository does not cover them, and no other issuer's text may be added on this basis. AGENTS.md is not
   changed by this ADR; a matching line there needs MB's explicit approval of its wording.
3. **Model results of the projects under verification are hidden until verification ends** (MB, card, 27 Nov 2026
   14:56 UTC). The website data on the public branch of PR 7 are to be replaced by a version without the model values of the 14
   projects AU, BS, CA, EU, HK, IL, IN, JM, JP, KZ, NZ, RU, SE, TW (work of the website thread). Earlier commits of the PR stay
   reachable on GitHub; history is not rewritten. Whether the tables of verification items in PRs 28 and 29 are treated the
   same way is asked separately.
4. **Provenance records** (assistant): [`docs/provenance/`](../docs/provenance/README.md) with the anchors of the procedure as
   full SHAs, the production run register (metadata of the twelve production run folders, nine used) and the register of the
   161 files kept outside git with their hashes.
5. **Backup** (assistant): a git bundle of all branches, the branch heads and an export of all PRs are kept in the project
   folder `repo-cleanup-2026-11-27/` (file `SHA256SUMS.txt`). The first bundle of 27 Nov was made from a shallow clone and
   could not be restored (A6 §15); it is marked broken. The second was restored and checked (`git fsck` clean, all 12 heads,
   the freeze and later anchors present).
6. **Deferred** until the items above and the verification question are settled: merging PRs 29, 28, 7, 6, closing PR 12,
   deleting branches, renaming the repository (proposal: `cbdc-dataset`; GitHub redirects old URLs unless the old name is
   reused; links to be tested before and after).

## Audit A6 findings checked by the assistant

- First backup bundle not restorable: confirmed (shallow clone), replaced.
- `ISSUERS_PROPOSED_2026-11-13.csv` read by `record_issuers.py:57`: confirmed.
- `GAP_CHECK_PRESCREEN_2026-11-03.json` is not empty (378 proposals, reconstruction note): confirmed; the proposal was wrong.
- PR 7 changes AGENTS.md (short-quotation exception, ADR-019): confirmed; the proposal's "AGENTS.md unchanged" was wrong.
- Full Norges Bank text in public `main` since 9 Nov: confirmed (837,976 characters per request file).
- PR 7 publishes per-model values for all 42 projects: confirmed on the public branch.
- The pass-1 lock in PR 29 accepts an incomplete workbook (`build_verification_workbook_v2.py`, `lock_pass1`): confirmed;
  to be fixed in PR 29.
- The website builder in PR 7 combines hypothesis flags of 24 Nov with cells recomputed on 26 Nov: confirmed in
  `scripts/site/build_results_site.py`; to be fixed in PR 7.
- Production runs are missing from `docs/RUN_STATEMENT.md`: confirmed; registered in `docs/provenance/` (the run records
  themselves stay outside git).
- ADR-008 to ADR-012 carry DS confirmation relayed by MB on 22 Nov: confirmed; the A6 brief's "DS has confirmed none of
  ADR-008 to ADR-019" was wrong.

Other findings (exposure declarations, run and audit crosswalks, decision index, CI checks of wildcard readers, rights
review of quotations) are listed with their state in the proposed dispositions held in the project folder
(`audit-2026-11-27-repo/NAVRH_VYPORADANI_A6_cs.md`) and are taken up in later changes.
