# Provenance: where every result comes from

This folder lets a reader find, for the results of 24 Nov 2026 and their repair of 26 Nov, the exact code, inputs and runs,
and where the material that is not in this public repository is kept. Policy: [ADR-020](../../DECISIONS/ADR-020-repository-record-and-cleanup-2026-11-27.md).
The dated and superseded files of the repository are listed in [`archive/INDEX.md`](../../archive/INDEX.md).

## 1. Anchors (full commit SHAs)

| Anchor | Commit | What it fixes |
|---|---|---|
| v12 start | `8cdf5add98568467baf1c3615d3578863222b903` (3 Nov 2026) | first commit of the v12 line; the v11 line before it is in `archive/v11/`. The tag `v11-dev-final` is not on GitHub (see section 4) |
| Freeze | `7f99c3420dc8cbb07eb99eee71d6c265152de477` (merge of PR 25, 23 Nov 2026 20:43:23 UTC) | every frozen input and prompt of production ([`docs/FREEZE_2026-11-23.md`](../FREEZE_2026-11-23.md)); the first production record starts at 20:44:57 UTC |
| Extraction code EX2 | `1ff1369c192aec3c8e6fda6c9e9f6f9b82279d60` (23 Nov 2026 21:20 UTC) | freeze amendment 1: pages in another script left out; code of the extraction runs PROD_EX2 |
| L2 run records | `d7573a4df4a5b2cd07251a0dfaabbb96f4832dd7` (merge of PR 26, 24 Nov 2026) | code of the facet runs PROD_L2 |
| Original results | `e61a5629ebf0d9e82cf34ba9e93f09140d73716b` (merge of PR 27, 24 Nov 2026) | reducer and derivation that produced the preliminary results package of 24 Nov |
| Repaired reducer | `e69b4b4778644e4096506b9920817ac3eb5fd9d4` (head of PR 29, 27 Nov 2026) | reducer after audit A5 ([`docs/REDUCER_REPAIR_2026-11-26.md`](../REDUCER_REPAIR_2026-11-26.md) in PR 29); the website data of 27 Nov name this commit |

The original and the repaired results are two versions and are never mixed in one table without saying so.
In the core of 16 projects the repair moved the provisional interval of the hypothesis from [10, 14] to [13, 14]; the
strict rule and the frozen rule ADR-012 D2 give [0, 14] in both versions (audit A6, replay with the stored responses).
Which combination rule is primary is an open author decision (ADR-018, part C).

## 2. Production runs

[`PRODUCTION_RUNS_2026-11-24.csv`](PRODUCTION_RUNS_2026-11-24.csv): the twelve production run folders of 23 and 24 Nov 2026,
nine used for the results and three stopped streams of stage EX that preceded the freeze amendment. Metadata only: model
requested and returned, prompt and its SHA-256, code commit, times, calls, tokens, input hashes, and the SHA-256 of each run
record. The responses themselves are not public: they carry the labels of the 14 projects under verification (ADR-016
point 4). They are in the archive `PROD_RUNS_FINAL_2026-11-24c.zip`, SHA-256
`c23bb74da5c152ebf3872c9655973f34f2f2f194335240a55ac090ec4a5ef0e1`. Development, pilot and translation runs, whose records are
in this repository, are in [`docs/RUN_STATEMENT.md`](../RUN_STATEMENT.md).

## 3. Material outside the repository

[`OUTSIDE_GIT_2026-11-27.csv`](OUTSIDE_GIT_2026-11-27.csv): every file kept in the authors' private project folder (161
files on 27 Nov 2026), with its size, SHA-256 and what it is. Uploads by the authors are not listed. It holds what may not be
public (source texts and units, responses with blind labels, author workbooks, private document links) and what is
pending (audit A5 and A6 reports until verification is locked, the paper draft). Files whose bytes are also in the
repository are listed too, so that a copy can be matched to its original. A public deposit of the cleared parts is planned
after verification.

## 4. Tags

The cloud sessions cannot push tags. The tags cited in the repository, `v11-dev-final` and `freeze-2026-11-23`, are therefore
not on GitHub as of 27 Nov 2026. The commits above identify the same states; a tag added later is a locator with its own date,
not evidence of when the freeze happened (the merge time is).

## 5. Audit A6 (repository), 27 Nov 2026

Registered by SHA-256; held in the project folder `audit-2026-11-27-repo/` and committed unchanged when verification is
locked, like A5 (the report discusses the exposure of the projects under verification).

| File | SHA-256 |
|---|---|
| prompt `00_PROMPT_A6_2026-11-27.md` | `195f3ee1dd091cf47873ff7bc8d8e358b35d2e33d41128e5f22446a32798ff97` |
| brief `01_AUDIT_BRIEF_A6_2026-11-27.md` | `9a79c41b4dfa2551e2d7425271fc7cae189390f74d6bc9113831b855800ecf7f` |
| pack `CBDC_REPO_AUDIT_PACK_2026-11-27.zip` | `40f5d370572b9871cdd60ef1beb93082115a5d94bcf8120cca498ba1907d5087` |
| report `INDEPENDENT_AUDIT_A6_2026-11-27.md` | `424ac4c7caaf3c9f88fb653c90caa91d5ad2212f7e30485575beec60a0832725` |

Verdict: the clean-up as proposed (merge PRs 29, 7, 6, remove 25 dated files, delete branches, rename) **BLOCKER**; a
staged clean-up with changes may proceed. Dispositions: ADR-020.
