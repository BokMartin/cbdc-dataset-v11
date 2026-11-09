# ADR-003 — Loss of the working container and restoration of the repository (9 Nov 2026)

**Status:** accepted (MB, 9 Nov 2026). **Supersedes:** nothing. **Related:** `ways-of-working` rule "GitHub is the source of truth".

## What happened

Between 6 and 9 Nov 2026 the cloud container in which the repository and the working directories lived was replaced. Lost were the
local clone with six commits made after the last bundle (3 Nov, commit 8cdf5ad), the page-delimited texts of the 125 core documents, the
NO/UK/NO_en run folders outside the repository, the sealed census and survey outputs, and the scratch files of the gap-check download.
Nothing had been pushed to GitHub since 18 Oct, which is exactly the failure the "source of truth" rule exists to prevent.

## What was restored, and how

| Item | Source | Fidelity |
|---|---|---|
| Repository up to 8cdf5ad (21 commits, tag `v11-dev-final`) | `cbdc-dataset_v12_2026-11-03.bundle` | bit-identical |
| `docs/PROCESS_v12.md` | text read verbatim in the working session before the loss | identical text, new commit |
| `scripts/frame/prescreen_gap_check.py`, `scripts/extraction/ingest_manual_response.py`, `scripts/review/build_source_review_workbook.py` | read verbatim in the session before the loss | identical code, new commits |
| `data/manifest/GAP_CHECK_PRESCREEN_2026-11-03.csv` | proposals, load_bearing and reasons carried row by row in `SOURCE_DECISION_WORKBOOK_v12_2026-11-03.xlsx` (CANDIDATES sheet), re-joined to `GAP_CHECK_2026-11-02.csv` on project + URL + title (378/378 matched) | same model outputs; the archived requests (`prescreen_requests/`) and per-project response ids are lost; `.json` says so |
| `data/manifest/V11_DROPS_PRESCREEN_2026-11-03.csv` | DOCUMENTS sheet, triage labels mapped back (recheck → KEEP? = accept, recheck = verify_first, …) | same proposals and reasons |
| `runs_v2_NO_en/requests/single.{system,user}.txt.gz` | OpenAI Playground code export (`playground_log.txt`), which embeds both input texts | SHA-256 identical to the run manifest |
| `runs_v2_NO_en_openai_manual/` | re-ingestion of the same `response.txt` + `meta.json` | response hash identical; folder timestamp is 9 Nov |
| `texts/NO_en/` (7 documents, 267 pages) | reconstructed from the archived user prompt | page markers and text as sent to the model |
| Manual download list and progress table (5 Nov) | `/mnt/user-data/outputs` | identical |

Not restored (to be regenerated, not recovered): page texts of the other 118 core documents (`scripts/frame/pdf_to_pages.py` over the
PDFs in the authors' Dropbox corpus), `runs_v2_NO` and `runs_v2_UK` request archives (their verified fills, comparisons and manifests are in
the repository), sealed per-project census and survey files (by design off-repository; aggregates are committed; both screens are to be
re-run on the completed corpus anyway, §6b of the contract), the link-check JSON (rebuilt from the workbook's link-check column as
`url_status_2026-11-03_reconstructed.json`, 721 URLs).

## Decisions

1. Every working session ends with a push to GitHub; a bundle in `/mnt/user-data/outputs` is a fallback, not a substitute.
2. Request archives of development runs (`requests/*.gz`) are committed with the run from now on; they are small (≤ 250 kB) and are the
   only thing that makes a run replayable without the API.
3. Page texts are regenerated from the PDFs by script and are not treated as primary data; the primary data are the PDFs with their SHA-256.
4. Reconstructed files carry this ADR in their provenance; no reconstructed file is presented as the original artefact.
