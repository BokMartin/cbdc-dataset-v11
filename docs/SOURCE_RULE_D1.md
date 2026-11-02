# Source inclusion rule (ADR-001 D1) and the uniform gap check — draft 2 Nov 2026

Replaces the genre-based exclusions of the core rubric (press releases, FAQs, speeches excluded by type) with one rule applied identically to every project before the source manifest is frozen (ADR D2).

## Rule

A document is **eligible evidence** for a project if all of the following hold:

1. **Authority.** Published by the body competent to decide for the project (central bank, ministry of finance / treasury, legislature or government, or a common union authority), or by a project consortium of which that body is the lead member, on an official channel (institution website or official publication series; an official English edition of the same institution counts as the same document, route B). Documents by other institutions (BIS, IMF, consultancies, news) are never evidence, whatever they contain.
2. **Subject.** About a retail CBDC of that project (wholesale-only documents are flagged and excluded from the retail matrix).
3. **Content.** Contains at least one statement that bears on a contract cell (F1–F12) or on a posture statement type (contract v2 §6b.1), or records a decision on project status (issuance, pause, discontinuation). A genre label does not decide: a press release that announces "the central bank will not see transaction data" is eligible; a 200-page report that never touches design or status is not.
4. **Date.** Published on or before the as-of date (2026-10-18).
5. **Layer.** Staff research (author-views disclaimer or staff series) is eligible as `staff_research = Y`: it may corroborate, never establish (contract §2).

Public speeches by board members on the official site are eligible under 1–3 (they were previously excluded by genre); their status is decided per claim (§4 rule A), not by genre.

## Uniform gap check (per project, before the freeze)

For every project in the frame, a search of the competent authority's official channels for documents that satisfy the rule and are **not** in the registry (391 rows), with: title, date, URL, type, and a one-line note on which cell or statement type the content bears on. Candidates are added to the manifest only after an author confirms eligibility; additions are logged as dated rows (`REGISTRY_ADDITIONS_*.csv`) with URL and SHA-256. The check is run once, by the same procedure for all 43 projects (model-assisted search, author confirmation), and its coverage is reported in the paper (projects checked, candidates found, candidates added, reasons for rejection). Projects whose registry contained only pre-2018 or wholesale material are flagged.

Status: draft; gap-check run started 2 Nov 2026 (model-assisted, see `data/manifest/GAP_CHECK_2026-11-02.csv` when complete).
