# ADR-019: results on the website, with short quotations from the source documents (27 Nov 2026)

Status: **decided by MB on 27 Nov 2026** (project chat, 10:04 and 10:06 UTC). DS has not confirmed. Recorded by the website assistant.

## Decision

1. **Results go on the website now, marked preliminary** (MB, 10:04 UTC): "vzal výsledky po auditu které máme a začal je
   vkládat na web a web zároveň upravovat". The site shows the privacy index, the cells, the cell history, the relevant
   privacy paragraphs, a PET table and the paper. Every page that shows a result carries the status line of the run
   ("Preliminary model output, not verified by the authors" until ADR-017 verification is locked and ADR-018 is decided) and
   the provenance of the run (freeze tag, reducer commit, input SHA-256).
2. **Short quotations, not whole paragraphs** (MB, 10:06 UTC): "odstavce zveřejníme celé, nebo web ukáže jen krátké citace s
   odkazem na zdroj a stranu. pokud toto neporušuje autorská práva tak udělejme to". The website shows a short quotation
   (at most 300 characters, cut at a sentence or word boundary) with the document, the page and a link to the issuer's own copy.
   Whole paragraphs or whole documents are not published.
3. Second exception to the rule on source text in AGENTS.md: the short quotations above may be written to
   `site/assets/*.json` by `scripts/site/build_results_site.py`, which enforces the length. Nothing else of the source text
   enters the repository.
4. Both combination readings are shown side by side (strict and provisional, `scripts/audit/recompute_results.py` step 4)
   until the authors decide ADR-018. The site does not order projects by index value (index spec §6).

## Why short quotations

The documents are official publications of central banks and public bodies. A short quotation with its source, for the
purpose of showing what a measurement rests on, is the use that the quotation right of copyright law permits (for example
§ 31 of the Czech Copyright Act, Art. 5(3)(d) of Directive 2001/29/EC). Whole paragraphs would go beyond that. This is the
reading of the assistant, not legal advice; MB asked for the variant that does not infringe copyright.

## Consequences

- AGENTS.md, rule on source text: the exception is added with a link here.
- If an issuer objects, the quotation is removed from the JSON by rebuilding with the document excluded.
