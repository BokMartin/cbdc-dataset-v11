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

## Gap-check result (model-assisted, 2 Nov 2026, evening; `data/manifest/GAP_CHECK_2026-11-02.csv`, `.json`)

All 43 projects searched by six Opus agents under the rule above against the 391-row registry: **378 candidate documents, 354 not in the registry** (24 marked "possibly" a companion of a registered item). Coverage judgement: major gaps 27 projects, minor gaps 12, complete 2, unclear 2. By type: press releases 86, reports 59, annual-report sections 50, speeches 47, FAQs 23, legislation 24, consultation papers/responses 27, design notes 13, pilot reports 11, other 38. Confidence: high 206, medium 131, low 41 (mostly PDFs behind bot protection: RBNZ, BCRP, al.gov.mo, parliament sites; to be fetched by the authors from a browser). 34 rows are wholesale-only and flagged. 109 candidates are dated 2025–2026.

What the registry systematically missed, because of the genre exclusions it replaced: (1) **status decisions** in press releases, web pages and annual reports (NO Dec 2025 "not warranted"; NZ Oct 2026 pause; SE Oct 2026 letter to the Riksdag; KE Jun 2023 "not a compelling priority"; HK Oct 2025 wholesale first; CA 2020/2023; AU Sep 2024; SZ 2024/2025 "not at this time"; NA 2025 refocus; HU Dec 2024 pilot ended; TW 2025/2026 "no urgency"); (2) **legislation** (RU 340-FZ, 248-FZ; AE decree-laws; BS regulations and limits 2021/2022; MO Lei 10/2023; ID Law 4/2023; NP 2026 bill; KZ law and NBK resolution 2026; IN Finance Bill 2022); (3) **FAQ pages with explicit privacy statements** (IL, NO, PE, MO, UA, MU, UK GOV.UK stories); (4) a few **primary design documents** (NG eNaira Design Paper 2021; HK Phase 1 report 2023; IL Preliminary Design 2025; KZ White Paper 2022; TH consultation 2021).

Corrections to existing registry rows surfaced by the check: CL "Prueba de Concepto MDBC 2025" is wholesale (flag for the retail matrix); two of three ID documents are wholesale; IL_BoI_2024 and TH_Thailand_n3063e could not be identified on the issuer sites; MG registry rows lack titles and URLs.

Not checked (named in the coverage notes): parliamentary records behind 403 (UK, MO, NP, IN), Hebrew-only forum summaries (IL), Kazakh editions, BCU pre-2021 (site search broken), BI press releases (site did not load), CH Federal Council answers 2020–2026 (search budget), PBOC English site.

Next: author decision per row (`author_decision` column: accept / reject / companion), then download + SHA-256 + `REGISTRY_ADDITIONS_<date>.csv`, texts via `pdf_to_pages.py`, and a **second as-of date** for the manifest, because 109 candidates post-date the core freeze and many are the decisions the matrix needs.


## Companion documents (rule added 13 Nov 2026; MB, ADR-005 section 9)

**Whose voice the paper measures.** The paper is about what the makers of a CBDC say: the executive side of the project, in most cases led by the central bank (with the ministry where it co-leads). A legal text adopted by the legislature or by the government as law-maker is the act of another branch about the project, not the maker speaking.

**COMPANION** = an official document of the project that is not evidence. It is not split into units and enters no talk measure or denominator. It is kept, listed and cited:
1. for the project's **status and timeline** (decisions to issue, pause or stop; launches; legal acts coming into force);
2. as the **record of a legal act or decision** that an evidence document refers to: in the contract's claim schema it may fill `endorsement_source` and `legal_state` of a claim that an evidence document makes. A companion never originates a claim on its own (confirmed by MB on 13 Nov 2026, 17:39; DS to confirm);
3. on the project page it is **linked to the evidence documents of the same project and year**, or of the nearest year where the year has none (`scripts/review/link_companions.py`, `data/manifest/COMPANION_LINKS_<date>.csv`).

Typical companions: press releases and news that announce a document which is itself evidence, FAQ and explainer pages, landing pages, speeches without a position of their own, and legal texts of the legislature or government.

Legal texts (MB, 13 Nov 2026, 17:38): a binding text issued by the central bank itself (regulation, circular, guidelines) is the maker speaking and stays evidence; an act of parliament, a government decree or a bill is a companion. Applied to all legal texts of the evidence set: 14 are companions (RU 339-FZ, 340-FZ, 105-FZ, 248-FZ; KZ Law on payments and NBK Resolution 42 as moved by MB; AE Decree-Laws 54/2023 and 6/2025; JM Bank of Jamaica (Amendment) Act 2022; BS Regulations 2021; ID Law 4/2023; MO Law 10/2023; MU Bank of Mauritius Act; NP Amendment Bill), 4 stay evidence (RU Regulation 820-P, NG eNaira Regulatory Guidelines, PE Circular 0011-2024, BS Regulations 2022).
