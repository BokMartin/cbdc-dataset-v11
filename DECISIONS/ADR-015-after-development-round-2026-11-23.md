# ADR-015: changes after the development round on NO and UK (23 Nov 2026)

Status: **adopted** by MB, 23 Nov 2026 18:45 UTC ("ano souhlasím se vším"), on the four proposals of
`docs/DEV_ROUND_2026-11-23.md`. DS has not confirmed in his own words. No prompt text changes.

1. **Extraction requests of at most 60,000 characters** (`build_jobs.py --max-chars`, default now 60000; it was 240,000).
   Owned page ranges stay disjoint with one read-only context page on either side. Reason: in the round Sol returned
   `coverage.complete = false` on the seven longest documents (33 to 118 pages) and Claude hit the 64,000-token output limit
   on one 72-page document. Whole corpus: 417 requests instead of 223, 20.0 M characters instead of 18.9 M.
2. **null read as n/d** in `basis`, `legal_state` and `referenced_law_state`, as already for `modality` (PR 21): the check
   (`scripts/extraction/v122.py`) accepts null where the allowed values include n/d and records n/d. In the round 60 of
   DeepSeek's 115 rejected observations were `legal_state: null`.
3. **Talk L1 by page in production** (one request per page, all candidate units of the page). In the round the page run gave
   the same label as the single-unit run on 97.0 % (Claude) and 96.7 % (Sol) of 2,449 units, three-model Fleiss kappa 0.89
   against 0.81, and all 14 units with a joint human label right for Claude and Sol. This reverses "page packing dropped"
   (HANDOFF §1 item 4).
4. **Re-run of the 8 failed extraction requests** with the new split before production (development, about 3 USD).
