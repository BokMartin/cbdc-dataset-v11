# Handoff: where the work stands and how to continue (written 21 Nov 2026, at commit of this file)

For an assistant that opens this repository in a new conversation. Read in this order: [`AGENTS.md`](AGENTS.md) (rules that do not change), [`PROJECT_BRIEF.md`](PROJECT_BRIEF.md) (goal, pipeline map, numbers, checklist), this file (state of play), [`DECISIONS/ADR-007`](DECISIONS/ADR-007-audit-2026-11-17-dispositions.md) (the open audit), `DECISIONS/ADR-008` to `ADR-010` (decided by MB on 21 Nov 2026 and waiting for DS: website and published translations, privacy index, INCLINED documents), [`docs/audits/README.md`](docs/audits/README.md) (what the audits are for). This file is rewritten at every handoff; `PROJECT_BRIEF.md` stays the standing overview.

## 1. Goal

A measurement-and-data article for *Data & Policy* by Martin Bok (MB) and Dominik Stroukal (DS), Prague University of Economics and Business: an open, auditable dataset of how the bodies that design retail CBDCs talk about user privacy and what they commit to, for 44 projects (43 national retail projects and the digital euro). Two layers: **privacy talk** (sentence units of official documents, labelled for relevance and seven facets) and **commitments** (ten feature cells per project, F1 to F12 with F5 and F6 reserved, with located verbatim quotes). No causal claims. Target set by MB on 17 Nov: all model runs finished by the end of November, mid-December at the latest; the authors' own deadline for the paper is 31 Dec 2026.

## 2. State in five lines

1. **No model has labelled a unit and no paid classification call has been made.** The fourth audit by a second model (A4, 17 Nov) returned NO-GO for calibration and for production until listed repairs are made (18 findings, 8 blockers).
2. Corpus: 218 evidence publications decided by an author (229 until 21 Nov 23:54, when MB moved 11 wholesale and BIS Innovation Hub documents to the new INCLINED layer, draft ADR-010, DS to confirm); 207 documents with English text (196 evidence publications and 11 INCLINED documents), 42 of 44 projects (Chile and Czechia have none); 171,865 sentence units; 19,570 candidates for classification.
3. Human inputs so far: both authors coded relevance blind for 120 development units, **agreement 67 %, Krippendorff's alpha 0.46**, below the 0.667 of the protocol; the disagreement sits in the label "U". Both judged 86 translation pairs, **Cohen's kappa 0.38**; MB is far stricter than DS. Neither result may be reported as validation; both are development findings that call for a repaired codebook and a joint adjudication.
4. Decided: three models in full (`claude-opus-5-5`, `gpt-6-astra`, `deepseek-v4-pro`); one unit per request (page packing dropped); validation by verification, with relevance coded blind; translation only for documents of T1 and T2 projects.
5. Repaired after A4 without author input: duplicate text removed (Israel), one header source, translation ingest fails closed, run-record check verifies artifacts, strict output parsers. 69 tests, CI green.

## 3. Decisions in force (the ADR is the authority)

| Decision | Where |
|---|---|
| Frame of 44 projects; the euro area is a project of its own; ECCU out | ADR-005 §1 |
| Evidence = KEEP + BORDERLINE documents of the competent body; legal texts of parliaments and governments are companions (cited, never a source of units) | `docs/SOURCE_RULE_D1.md`, ADR-005 §9, §10 |
| Tiers by number of evidence publications: T1 8 or more, T2 5 to 7, T3 4 or fewer | `data/manifest/TIERS_2026-11-21.csv` (the `tier` column is as of 17 Nov and was not recomputed after the INCLINED decisions, ADR-010) |
| Talk instrument: units, candidates (dictionary hit, neighbour, random control), relevance then facets; schema and prompts are drafts v0.3 | ADR-004, `schema/talk_units_v13_DRAFT.json` |
| The authors do not code the seven facets blind; validation by verification with safeguards | ADR-006 A |
| Three models, full runs, results per model and agreement reported | ADR-006 A.5 |
| A4 dispositions and MB's six decisions of 17 Nov (no split of the target; packing dropped; translation only T1 and T2; Israel duplicate linked) | ADR-007 §2, §4 |
| Every model run leaves a run record; production only through provider APIs | `docs/RUN_RECORD_SPEC.md`, `AGENTS.md` |

Decided by MB on 21 Nov 2026 and waiting for DS (not in force until he confirms; the ADR is the authority):

| Decision | Where |
|---|---|
| The website shows the corpus and never results; nine Taiwanese machine translations are published under the issuer's open licence | ADR-008 |
| A two-axis privacy index on eight F-cells is a key result of the article; privacy talk stays beside the index and is set against commitments by aspect; hypotheses H-TC1 and H-TC2 are to be registered before any data; so far everything runs on mock data only | ADR-009, `docs/PRIVACY_INDEX_SPEC_DRAFT_2026-11-21.md` §12 |
| Document status INCLINED (38 documents) and cell status LEANING, every result reported with and without them; Brazil stays outside the frame | ADR-010 (draft), `data/manifest/TIERS_2026-11-21.csv` |

## 4. Waiting for the authors

Decisions (each stops something):

| # | Decision | Stops | Notes |
|---|---|---|---|
| 1 | Blank double coding of **voice** and **aspect** on 80 to 120 relevant units by both authors (about 1.5 to 3 hours each), or all seven facets labelled exploratory in the paper | what the paper may claim about facets (A4 F01) | MB undecided on 17 Nov. It can be done after the model runs if the units are reserved now and the authors' labels are locked before they see model output. Given the relevance result, repair the rules first |
| 2 | How calibration is run. MB proposed (17 Nov): development rounds on Anthropic only, then one clean run on three models. Proposal of the pipeline author, not yet answered: (a) a short capability probe of all three providers before round 1, (b) three rounds on Claude with changes driven only by defects the authors find in the codebook or prompt, (c) a fresh confirmation set of 40 units on all three models before the freeze | first paid call | ADR-007 is the place to record the answer |
| 3 | Seven machine-translated documents of today's T3 projects (CN 3, PE 3, TH 1) exist only because those projects were T2 on 10 Nov: keep and state it, drop them, or translate the other 14 T3 documents as well | freeze of the corpus | ADR-007 §4.4 |
| 4 | Adoption of the measurement contract v12 (`docs/MEASUREMENT_CONTRACT_v12_DRAFT.md`, open points marked `[OPEN]`). The extraction prompts, generator, schema validation and comparison are still built for contract v1.1 | all F-cell work (A4 F02); the critical path if the commitment layer is to be done by mid-December | the pipeline author owes the authors a list of the open points |
| 5 | Review of issuer, issuer type and document kind for the 207 documents (pre-filled by a model; the facet prompt receives them as input) | facet rounds and production | `data/manifest/ISSUERS_2026-11-13.csv`; 2 to 5 hours |
| 6 | DS confirms ADR-004 to ADR-010 | freeze | |
| 7 | Remaining rows of ADR-007 §2 (F10 wording of "first" and status vector, F13 access statement, F14 cutoff date, F15 reference design, F16 rounds) | freeze | |

Workbooks to fill in (Dropbox folder `Dizertace all the PDFs`; not changed since 17 Nov when checked on 21 Nov):

| File | What | Who |
|---|---|---|
| `NESHODY_MB_DS_2026-11-17.xlsx` | only the rows where the authors differ: 41 development units (relevance) and 35 translation pairs; joint label, reason, and for unclear rules one sentence that would have settled it. The sentences become the codebook repair | MB and DS together |
| `CBDC_TALK_v13/TALK_DEV_FIX_MB_2026-11-17.xlsx`, sheet `U_24` | what MB meant by each of his 24 "U" labels | MB |
| `CBDC_TRANSLATION_v12/TRANSLATION_JUDGEMENT_MB_2026-11-17.xlsx`, sheet `UNMATCHED` | 30 unmatched sentences (DS has done them) | MB |

Reader for the disagreement workbook does not exist yet: write it when the file comes back, store joint labels apart from the blind ones (`DEV_LABELS_*` are never overwritten).

## 5. Open on the pipeline author's side (no author input, no paid call)

1. Runner for three providers with run record, idempotent, with cost cap, tested offline against the failure fixtures of A4 (truncated output, refusal, timeout, duplicate attempt). Not built.
2. Exposure registry (which unit, paragraph and document each author and each model has seen) and exclusion by displayed paragraph in `draw_agreement_sample.py` (A4 F06). Not built.
3. Unitisation reads only pinned successful translation records (rest of A4 F04); unit identifiers bound to a unitisation version (rest of F03).
4. Facet prompt v0.4: a unit admitted by another model is not assumed relevant; explicit not-applicable channel (F12). Codebook and relevance prompt repaired from the authors' adjudication.
5. Scorer of the translation benchmark shows "not judgeable" as its own outcome (F08); usage and price ledger fed by measured usage (F18).
6. F-cell instrument at v12: generator, schema validation, comparison, replay on two status axes (F02). Large; needs decision 4 first.
7. Rights and access manifest and a concrete data availability statement (F13). Data & Policy does not accept "available on request".
8. List of the `[OPEN]` points of contract v12 for the authors.

## 6. Agreed order up to the first production call

Repair inputs and checks (section 5, items 1 to 5) → authors adjudicate disagreements and the codebook is repaired → capability probe of the providers (a few USD; replaces the cost estimate with a measurement) → development rounds → confirmation set → **audit A5** of everything changed since commit `7e6e4c5` → freeze and registration (OSF, Zenodo) → reference sample coded blind → production on three models → verification. The auditor's full 24-step protocol is in `docs/audits/INDEPENDENT_AUDIT_2026-11-17.md`, question 13; `docs/CALIBRATION_PROTOCOL_DRAFT_2026-11-17.md` is superseded by it.

## 7. Data that is not in the repository and where it is

Source documents, translations and unit texts are under the issuers' copyright and never enter the repository. A new conversation starts with an empty workspace; restore from the authors' Dropbox folder `Dizertace all the PDFs` (reachable only when the conversation is linked to MB's computer `desktop-cl6vbje`; otherwise ask MB to attach the zip files).

| What | Where in Dropbox | SHA-256 |
|---|---|---|
| Unit and candidate files of the 207 documents (with text), plus the dropped duplicate | `CBDC_WORKDATA_2026-11-21/CBDC_UNITS_v13_2026-11-21.zip` | `4bb200226e06de34f49c2a8d23dd8da69dddd5feb795680f819159e13683122a` |
| Reading-order text of every PDF by file hash, and `master_local.json` (file hash → path) | `CBDC_WORKDATA_2026-11-21/CBDC_TEXTCACHE_reading_order_2026-11-21.zip` | `c477821a8f4a6521b5ef3e6344cf4f8ef75453f1a965dbfb4cd820ecb8e4ee7c` |
| Layout text of every PDF by file hash | `CBDC_WORKDATA_2026-11-21/CBDC_TEXTCACHE_layout_2026-11-21.zip` | `ccf3ff4ffcf0f57eaaafa4ee4155f5a7d026e5f45549b6fb8b96321516c28ad0` |
| Translations of the three runs, manifests, benchmark workbooks | `CBDC_TRANSLATION_v12/` | in `data/translation/TRANSLATION_MANIFEST_*.csv` |
| Source PDFs by project; document list by country | `CBDC_MASTER_v12/`, `CBDC_corpus_v2/`; `CBDC_MASTER_v12/CBDC_CORPUS_DOCUMENTS_2026-11-17.xlsx` | in `data/manifest/MASTER_MANIFEST_2026-11-10.csv` |
| Audit packs as sent | `CBDC_AUDIT_2026-11-13/`, `CBDC_AUDIT_2026-11-17/` | |
| Returned workbooks of the authors, unchanged | `_ARCHIV_vyplnene_vstupy/` | hashes in the label files and ADRs |

The paths inside `master_local.json` point to the workspace of the conversation that wrote it and must be re-based.

## 8. Providers, money, keys

- Models: `claude-opus-5-5` (the Norway and UK extraction pilots ran on it), `gpt-6-astra` (all translations ran on it; the OpenAI account ran out of credit on 13 Nov, so Peru `CAND-250` is not re-translated), `deepseek-v4-pro` (no account yet).
- MB reported on 17 Nov a free API allowance of 300 USD on Anthropic and holds a Claude Max plan; expiry and whether it covers the Batch API were not confirmed. ChatGPT Plus carries no confirmed API credit.
- Estimates (list prices of 17 Nov, not measurements; reasoning-token use of the classification has never been measured): talk layer on three models, one unit per request, Batch API where offered, 350 to 850 USD; F-cells about 40 to 90 USD per model. Basis and unknowns: ADR-006, ADR-007 §3.
- **Keys are never written to the repository, a file or a log.** Ask MB for them in the conversation and pass them in the environment for one run. CI scans for key patterns.

## 9. Things that have gone wrong before (do not repeat)

1. Saying a check "enforces" something it only looked at. A4 found the translation ingest and the run-record check passing fictitious inputs. Describe a check by what it verifies, and add a negative test.
2. Reporting a human-coded figure before the second coder: MB's "31 % of translation pairs differ in meaning" became 4 % for DS.
3. Row order differs between the two authors' workbooks; always join on `unit_id` or the pair number, never on row position.
4. A returned workbook can have an emptied cell (row 42 of MB's development sample). Compare the returned file with the generated one before interpreting a blank.
5. Never overwrite a workbook an author may be filling in; never delete on the authors' computer without an exact list and a yes.
6. `device_bash` on MB's computer does not work (no hypervisor); file moves and deletions go through the Dropbox connector; files above about 27 MB go through the file-send route.
7. A chat or agent product is not an admissible interface for a production run (hidden system prompt, model not fixed); it is also not a way around API billing.
8. The per-project results of the sealed model screens of 2 Nov stay sealed; only Norway and the UK are exposed to the authors (`EXPOSURE_LEDGER.md`).
9. The workspace of a conversation is not durable. Anything not pushed or not in Dropbox is lost (ADR-003 records one such loss).

## 10. Text to paste into a new conversation

> Pokračujeme v projektu CBDC privacy dataset (článek pro Data & Policy, autoři Martin Bok a Dominik Stroukal). Zdroj pravdy je GitHub `BokMartin/cbdc-dataset-v11`, větev `main`. Naklonuj repo a přečti v tomto pořadí: `AGENTS.md`, `PROJECT_BRIEF.md`, `HANDOFF.md`, `DECISIONS/ADR-007-audit-2026-11-17-dispositions.md`, `DECISIONS/ADR-008` až `ADR-010`, `docs/audits/README.md`. Ověř, že poslední běh CI `verify` je zelený. Pak mi česky shrň stav v pěti bodech a řekni, co ode mě a od Dominika potřebuješ jako první. Nic placeného nespouštěj a nic neměň v pravidlech bez mého souhlasu. Pracovní data mimo repo jsou v Dropboxu ve složce `Dizertace all the PDFs` (viz HANDOFF, oddíl 7); klíče k API ti dám až na vyžádání.
