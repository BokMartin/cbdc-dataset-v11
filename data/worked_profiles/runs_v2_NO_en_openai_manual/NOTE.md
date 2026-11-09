# Norway, route B, second provider by hand (OpenAI Playground, 3 Nov 2026)

The archived single request of `runs_v2_NO_en` (system 18f17658…, user 7aa016ce…) was pasted by MB into the OpenAI Responses
Playground (model id shown: `gpt-6-astra`, reasoning medium; temperature, top_p and max_output_tokens not exposed by that model,
so they are `null` = not set, not zero). The Playground's own code export (`playground_log.txt`) carries both input texts and the
response; their SHA-256 match the archived request and `response.txt` exactly (`export_input_texts_verified: true` in MANUAL_META).
`ingest_manual_response.py` stored the raw response, re-parsed and validated it with the pipeline's own parser and wrote `FILL_single.csv`
(5 validation problems: free-text `derivation` on F2, `n/d` as claim_status/derivation on F4 and F7).

Citation check: 17/17 `exact_page`. Comparison with the Anthropic runs on the same documents and prompt:
single vs single 0 full / 13 value / 4 differ; Anthropic two-stage vs OpenAI single 2 full / 12 value / 3 differ.
Pattern: the two providers agree on values and locators and disagree on the evidence label (OpenAI `documented` where Anthropic `partial`),
which is a definition question for the contract, not a model error. Manual run: development comparison only (caveat in MANIFEST).

Provenance note (9 Nov 2026): the working container was lost on 6–9 Nov; this folder was rebuilt by re-running the ingestion on the same
`response.txt` and `meta.json` (hashes unchanged), after restoring `runs_v2_NO_en/requests/*.gz` from the Playground export (hashes verified).
The run folder's timestamp therefore reads 2026-11-09; the response is the one of 3 Nov.
