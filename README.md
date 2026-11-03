# CBDC Dataset — v12 (in development)

Open dataset and working paper on **documented privacy and identifiability design in retail central bank digital currency (CBDC) projects**, built only from official central-bank and government documents, with every value traceable to a document, a page and a verbatim quote.

> **Status (3 Nov 2026): v12 in development.** v12 replaces the v11 line (tag `v11-dev-final`, files under `archive/v11/`) after an external methodological consultation (28 Oct), an independent audit (2 Nov) and a uniform source gap check (2 Nov). The website is a mock-up of the finished product: only the two development profiles (Norway, United Kingdom) carry real, citation-checked model output, labelled "development · not validated"; all other cell values are seeded placeholders. Nothing here is a finding yet.

Authors: Martin Bok, Dominik Stroukal (Prague University of Economics and Business). Target: *Data & Policy* (measurement and data paper). Previous release (v1, vocabulary-based purpose categories): [cbdcdataset.org](https://cbdcdataset.org).

## What changed from v11 to v12

| | v11 (18 Oct 2026) | v12 (from 3 Nov 2026) |
|---|---|---|
| Source selection | genre-based core rubric (`core_v1` 109 docs + `core_v2` UK 18) | one **source manifest** under an authority/content rule ([SOURCE_RULE_D1](docs/SOURCE_RULE_D1.md)); gap check of all 43 projects found 354 official documents the rubric had excluded (status decisions, legislation, FAQs, design papers) |
| Instrument | contract v1.1: option/adopted/tested/operational ladder; conditional statement = commitment | [contract v12 draft](docs/MEASUREMENT_CONTRACT_v12_DRAFT.md): endorsement by the competent body; `decision_status` × `implementation_status`; symmetric admissibility (rule C); no inference from silence; locators with spans |
| Layers | commitment matrix only | commitment matrix + **privacy-posture layer** (P0–P3 ladder, G1–G9 indicators) + linguistic emphasis, all status-attached, never mixed |
| Language | "both coders English"; 12 non-English documents assumed | evidence-language ledger with routes A/B/C/D; issuer English editions ingested (Norway); registry labels corrected (19 non-English of 125) |
| Validation | development fills reviewed by the authors | blind reference workbooks (no model columns), source-first F1 for every project, sealed model-only surveys with an exposure ledger and allowlist enforced in code, two providers, pre-registered gates |
| Pipeline | extraction script | versioned prompts with hashes, one-command re-run, full-span citation check, coverage-checked mode comparison, dated registry amendments |

## Repository layout

```
docs/                 MEASUREMENT_CONTRACT_v12_DRAFT, SOURCE_RULE_D1, LANGUAGE_LEDGER, PRIVACY_POSTURE_LAYER_DESIGN,
                      DELTA_ELICITATION_FORM, CONSULTATION_BRIEF (cs), audits/ (independent audit + prompt)
DECISIONS/            ADR-001 (dispositions of the 28 Oct consultation), ADR-002 (dispositions of the 2 Nov audit)
EXPOSURE_LEDGER.md    who has seen which model output, when; data/EXPOSURE_ALLOWLIST.json is its machine-readable gate
PROJECT_FRAME.md      48 projects → 46 national → 43 retail candidates (data/frame/projects.csv)
data/registry/        REGISTRY_v2_2.csv (frozen, 391 rows) + dated amendments, additions, source-URL and licence tables
data/manifest/        SOURCE_MANIFEST_v12_DRAFT (one table of evidence documents), GAP_CHECK_2026-11-02 (+ priority subset)
data/census/          aggregates only of the sealed endorsement census and statement survey (SHA-256 of the sealed files)
data/statements/      citation-checked statements for exposed projects only (NO, UK)
data/worked_profiles/ development runs (NO, NO route B, UK), manifests, comparisons, notes
schema/               cells_v1_1.json (v11 runs), cells_v12_DRAFT.json, f11_crosswalk.json
scripts/              frame/ (registry loader, project frame, manifest, language detection, pdf_to_pages, gap-check consolidation)
                      extraction/ (extract_api, verify_quotes, compare_modes)  census/ (sealed surveys, release)  review/ (workbooks)
                      pipeline/ (export_prompts, run_all)  site/ (build_site_data)  derive.py (rule C gate, posture layer)
pipeline/             every rendered prompt with SHA-256 (PROMPTS.json) and how to re-run from any provider
tests/                24 tests (pytest); .github/workflows/verify.yml runs them with a secrets scan
site/                 static website (GitHub Pages, no build step); assets/data.json is generated
archive/              v11/ (contract v1.1, predictions draft, core rubric, corpus changelog, core_v1 freeze), run_scripts/ (hash-verified script versions)
```

PDFs are not redistributed; every manifest row carries the official URL, SHA-256, language, route and reuse-terms class.

## Reproduce

```
python3 -m pytest -q tests                                   # no API key needed
python3 scripts/pipeline/run_all.py --dry-run --model x --texts <texts> --sealed-dir <outside repo> \
    --contract docs/MEASUREMENT_CONTRACT_v12_DRAFT.md --schema schema/cells_v12_DRAFT.json
```

See [pipeline/README.md](pipeline/README.md) for inputs, the one-shot command, and what is deliberately not one-shot (human coding, sealed outputs, provider sampling).

## Licence

Data and documentation: CC BY 4.0. Code: MIT. © 2026 Martin Bok & Dominik Stroukal.
