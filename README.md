# CBDC privacy dataset (v12, in development)

Open dataset and working paper on what the official documents of retail central bank digital currency (CBDC) projects say
about user privacy (**talk**) and which privacy design they state (**commitment**), built only from official documents of
the competent bodies, with every value traceable to a document, a page and a quote.

**State on 27 Nov 2026.** 44 projects in the frame, 42 with measured documents (no measurable document for CL and CZ).
Production model runs on three providers are complete (23 and 24 Nov 2026). Their results are **preliminary model output,
not verified by the authors**; verification of the core cells is under way and the combination rule is an open author
decision. Nothing in this repository is a finding yet.

Read first: [PROJECT_BRIEF.md](PROJECT_BRIEF.md) (goal, pipeline, numbers, audits) · [docs/provenance/](docs/provenance/README.md)
(commits, production runs and material outside git behind every result) · [DECISIONS/](DECISIONS/) (who decided what) ·
[docs/audits/](docs/audits/README.md) (independent audits by a second model) · [archive/INDEX.md](archive/INDEX.md) (which
dated file is current, which superseded, which line is retired) · [AGENTS.md](AGENTS.md) (working rules for assistants).

Authors: Martin Bok, Dominik Stroukal (Prague University of Economics and Business). Target: *Data & Policy* (measurement and
data paper). Website: [cbdcdataset.org](https://cbdcdataset.org).

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
PROJECT_BRIEF.md      one page: goal, pipeline, generated numbers, audit coverage
DECISIONS/            ADR-001 onward: every method decision with author, date and basis
docs/                 measurement contract, source rule, translation and unit procedures, freeze, run statement
docs/provenance/      anchors (full SHAs), production run register, register of files kept outside git
docs/audits/          prompts, briefs and reports of the independent audits, and their register
EXPOSURE_LEDGER.md    who has seen which model output or source text, when
data/                 frame, registry, manifests and author decisions, units manifests, samples and labels, run records
                      of development, pilot and translation runs (production records stay outside git, ADR-016)
pipeline/             every prompt with its SHA-256
scripts/, tests/      the pipeline and its tests; .github/workflows/verify.yml runs them and the consistency checks
site/                 the static website (deployed by the authors)
archive/              INDEX.md of dated and retired files; v11/ and run_scripts/ of the v11 line
```

PDFs are not redistributed; every manifest row carries the official URL, SHA-256, language, route and reuse-terms class.

## Reproduce

```
python3 -m pytest -q tests                              # no API key needed
python3 scripts/pipeline/update_brief.py --check        # numbers in the brief match the data files
python3 scripts/pipeline/run_statement.py --check       # every committed run record is complete
```

The production runs and the derivation of the results need the private run archive and unit texts (hashes in
[docs/provenance/](docs/provenance/README.md)); the runner and its use are in [docs/RUNNER.md](docs/RUNNER.md) and
[docs/FREEZE_2026-11-23.md](docs/FREEZE_2026-11-23.md). [pipeline/README.md](pipeline/README.md) describes the earlier
development pipeline.

## Licence

Data and documentation: CC BY 4.0. Code: MIT. © 2026 Martin Bok & Dominik Stroukal. Third-party material is excluded; see [LICENSE](LICENSE).
