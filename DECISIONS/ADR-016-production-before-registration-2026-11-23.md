# ADR-016: production starts before the OSF registration; a dated freeze takes its place (23 Nov 2026)

Status: **adopted** by MB, 23 Nov 2026 20:03 UTC, in the project chat: "tohle bych raději teď neřešil a začal bych s extrakcí
pokud to je možné" (on the list of steps before production, of which the OSF account and registration were the first). DS has
not confirmed in his own words.

## Decision

1. **The OSF registration is filed later, not before the first production call.** This changes ADR-012 D1 a and MB's rule of
   22 Nov ("registrace indexu a hypotéz hned po finalizaci, před prvním placeným voláním") and §5 of
   `docs/REGISTRATION_A_DRAFT_2026-11-23.md`.
2. **In its place, a dated freeze before the first production call.** One commit on `main` holds the prompts, the unit set,
   the index definition, the hypothesis with its bounds and the known cases; `docs/FREEZE_2026-11-23.md` lists the SHA-256 of
   every frozen file and of the production request files. The commit gets the annotated tag `freeze-2026-11-23`, pushed to
   GitHub before any production request is sent. GitHub's record of the push is the time stamp.
3. **The later registration says so.** It states that the data were collected after the freeze and before the registration,
   names the tag and its date, and states that the model outputs of the blind core were stored but not opened before MB and DS
   locked their blind coding (point 4). Any change after the freeze is a dated amendment, as before.
4. **Blind core.** The model outputs of the 14 blind core projects (T1 and T2 without NO and UK, ADR-012 D1) are stored
   outside the repository, archived with their hash, and not opened: no labels, cells, quotes or per-project counts of these
   projects are shown to MB or DS, or written to the repository, until both authors have locked their blind F-cell coding and
   the reference sample of 400 units has been coded. Until then only run-level figures are reported (cost, tokens, number of
   requests that pass the v12.2 check, failures to re-run). NO, UK and T3 outputs are not restricted.

## What the first production launch holds (MB's card decides it)

- Talk L1 relevance by page (ADR-015), prompt `talk_L1_relevance.system.md` (v0.4 codebook rules, `009fe469…`), and F-cell
  extraction, prompt `extraction_v12.2.system.md` (`7a97c8dd…`), on the unit set v13e (text in images added, PR 24), on the three
  models of ADR-014.
- **Not talk L2 (facets).** Its prompt `talk_L2_facets.system.md` is a draft that has not been through a second-model audit,
  and MB has not read it. L2 needs the L1 labels anyway; it is launched after MB has read the prompt and said yes.
- General publications (annual reports, general research, strategy) are sent as their CBDC pages ±1 only (ADR-013 P3,
  `scripts/extraction/cbdc_span.py`, `data/manifest/EXTRACTION_HEADER_EXTRA_2026-11-23b.csv`): 9 documents. Kind `other` is
  sent whole, because it holds CBDC reports. Explicit references from a span to pages outside it are kept by the model and
  resolved after the run.
- Peru `CAND-250` is left out of extraction (`docs/LANGUAGE_LEDGER.md`, MB 22 Nov), now through
  `data/manifest/EXCLUDED_FROM_STAGES_2026-11-23.csv` and `build_jobs.py --exclude`.

## Open at the freeze (recorded, not settled)

- Known cases: K03 (UK, F1 = no) is frozen as proposed; its page and quote are not yet fixed by the authors. No NO case was
  chosen. Both projects are development projects and exposed, so adding the page and quote later does not open a blind cell.
- DS has not confirmed ADR-014, ADR-015 or this ADR in his own words.
