# Exposure ledger — who has seen what, and when

Purpose: the pre-registration will disclose prior exposure instead of claiming that no cell value had been seen (consultation Part I §4, F1 in ADR-001). This ledger is append-only; every entry names the person, the material, the date and the consequence for later blind work. Model outputs count as exposure for the person who read them. "MB" = Martin Bok, "DS" = Dominik Stroukal, "CL" = Claude (technical collaborator), "MI" = supervisor.

## Rule

A project whose model-generated cell values any author has read is **exposed** and cannot enter the blind reference set or count as unexposed for the primary-outcome reference. Aggregate counts that reveal no per-project value are recorded but do not expose projects. The supervisor's exposure is recorded because he takes part in the δ elicitation.

## Entries

| Date | Who | Material | Per-project values seen? | Consequence |
|---|---|---|---|---|
| ≤ 2026-07 | MB, DS, MI | v1 manuscript results (MSED 2026): vocabulary-based purpose categories, privacy index, correlations with institutional variables for 49 jurisdictions | yes, v1 constructs (not F-cells) | Hypotheses H1/H2 were informed by v1 results; disclosed in registration |
| 2026-10-17 | MB, DS | Encoder round 1: 120 paragraphs (116 paired), retrieval labels PRIV/TRACE/DESIGN/OWN_PROJECT | paragraph labels, not cells | none for F-cells |
| 2026-10-17 | MB, CL | Keyword-presence scans of F-vocabulary across core documents | counts per document | none for values |
| 2026-10-17 | MB | Official project status table (85 jurisdictions) | status, not cells | none |
| 2026-10-18 | MB, CL | Agent fills (contract v1) for **NO** and **UK**, with quotes and justifications | **yes** | NO, UK exposed |
| 2026-10-18 | MB | Review workbook `LLM_REVIEW_NO_Norway.xlsx`; MB recorded verdicts (sided with agent fill in 19/20 cells) | yes (NO) | NO exposed; anchoring risk recorded |
| 2026-10-18 | MB, CL | API fills (contract v1.1, single and two-stage) for NO and UK; review workbooks v1.1 | yes | NO, UK exposed |
| 2026-10-18 | MB, DS (sent), MI (sent 1-pager) | Website mock-up with seeded placeholder values for 68 projects (labelled MOCK) and real development values for NO/UK | mock values are not data; NO/UK real | none beyond NO/UK |
| 2026-10-27 | CL (external LLM consultant) | Consultation pack incl. NO/UK fills; consultant's review quotes NO/UK values | yes (NO, UK) | none beyond NO/UK |
| 2026-10-28 | MB, CL | Consultation document (Parts I–V) | discusses NO/UK only | none beyond NO/UK |
| 2026-11-02 | CL | Reconstruction of archived script versions; project frame recomputed from registry | no values | none |
| 2026-11-02 | CL (model only) | Endorsement census, 43 national retail candidates, one request per project (`scripts/census/endorsement_census.py`, claude-opus-5-5, contract v1.1 as definition source). Per-project file sealed off-repo (`census_sealed/ENDORSEMENT_CENSUS_sealed.jsonl`, SHA-256 in `data/census/ENDORSEMENT_CENSUS_aggregate.json`); the census log is off-repo too. Authors receive the aggregate only. | model yes; **authors no** | none for authors; census values are not instrument output and are never merged into profiles |
| 2026-11-02 | CL | Valid single vs two-stage NO run (v2 extractor, complete coverage) | yes (NO, already exposed) | none beyond NO |

## Planned entries (to be filled when they happen)

- Development cases 3–7 (euro area, Canada, Chile, Hungary, one LIVE project): exposed on the date each author first reads a model output for them.
- Blind set draw (Phase 3): list sealed by hash; published after scoring.
- δ elicitation: independent written answers from MB, DS, MI dated and stored before the joint session.

## Statements withdrawn

- `01_STATUS_SUMMARY_2026-10-27.md` line 28 ("UK: both API modes agree on all values but F4; Norway: 4 cells differ … two-stage is systematically more conservative"): withdrawn 2 Nov 2026. The two-stage runs lacked stage-one output for NO documents 2 and 4 and UK document 4 (parse failures), so the comparison did not isolate the extraction architecture (consultation Part IV §2–3).
- `PREDICTIONS_v2_2_DRAFT` lines 3 and 42 ("no F-cell value has been computed / seen"): withdrawn; replaced by this ledger.
- Website label "Real · verified quotes" for NO/UK: replaced by "development extraction — not validated" (Phase 0).
