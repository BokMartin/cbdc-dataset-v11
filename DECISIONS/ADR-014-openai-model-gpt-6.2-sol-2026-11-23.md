# ADR-014: OpenAI model for talk and extraction is gpt-6.2-sol (23 Nov 2026)

Status: **adopted** by MB, 23 Nov 2026 16:50 UTC ("souhlasím se sol"). DS has not confirmed in his own words.

## Decision

The third model of the three-model design (talk L1, talk L2, F-cell extraction) is `gpt-6.2-sol` instead of `gpt-6-astra`.
This changes the choice of 17 Nov (HANDOFF §1 item 4: `claude-opus-5-5`, `gpt-6-astra`, `deepseek-v4-pro`) and MB's line of
23 Nov 15:21 UTC ("modely se nemění"). Claude and DeepSeek do not change. The route-D translations already made on
`gpt-6-astra` stay as they are (ADR-013 P4); they are not re-run.

## Why

- Cost. gpt-6-astra was about 40 % of the production estimate. Prices on 23 Nov (developers.openai.com/api/docs/pricing, USD
  per 1M, input / cached / output): gpt-6-astra 10 / 1.00 / 50, gpt-6.2-sol 2 / 0.10 / 10; Batch is half. Estimate of the
  whole production with relevance by page: about 415–700 USD with gpt-6-astra, about 285–480 with gpt-6.2-sol
  (`docs/PILOT_API_2026-11-23.md`).
- No loss of quality seen in the pilot (same 100 L1 units of NO and UK and 2 extraction documents, development):
  L1 labels agree with gpt-6-astra on 98 of 100; unanimity with Claude and DeepSeek is 83 of 100 with either OpenAI model;
  both extraction responses pass the v12.2 check with 0 observations rejected (gpt-6-astra failed one request).

## Reservation (to be stated in the paper)

The comparison rests on 100 sentences and two short documents (9 and 12 pages); production documents are on average 4.4
times longer. A weaker model may show only on long documents, and would then show as more disagreements among the three
models, that is, more cells for the authors to adjudicate. The development round on NO and UK is where this is watched; if
gpt-6.2-sol fails there more often than the other two, the choice is put to the authors again before production.

## Consequences

- `pipeline/PRICES.json` has the gpt-6.2-sol row. The runner sends the OpenAI system prompt as a developer message,
  because gpt-6.2 models do not cache `instructions` (measured 23 Nov: 0 cached tokens; with a developer message 1,144 of
  about 1,400 on a Batch run of 10 L1 requests, run `CACHETEST_L1_sol62` outside the repository). The text is unchanged.
- The A4c auditor was a GPT-6 model from the same vendor; the vendor interest declared there now concerns gpt-6.2-sol.
