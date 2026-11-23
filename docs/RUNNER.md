# Runner for the three models (no paid call made yet)

`scripts/pipeline/build_jobs.py` builds the requests of one stage (talk L1, talk L2, extraction) for a set of projects, outside
the repository; `scripts/pipeline/runner.py` sends them to one provider and writes a run record v1 (`docs/RUN_RECORD_SPEC.md`).
Offline tests with fake provider clients: `tests/test_runner.py`; prompt v12.2 request, check and reducer:
`tests/test_extraction_v122.py`.

## Extraction with prompt v12.2 (ADR-013)

- **Request** (`build_jobs.py --stage extraction_single`, `scripts/extraction/v122.py render_request`): HEADER with the fields
  of prompt §1, then `=== PAGE p ===` and one labelled block per paragraph, `[p<page>.b<para>] text`, then
  `=== END OF REQUEST TEXT ===`. A document longer than `--max-chars` is split into disjoint owned page ranges; each request
  also carries one read-only context page on either side. Every page 1..pages_total is sent, a page without text as its marker
  only. request_id = `<doc_key>:p<first>-<last>`. `decision_authority` is `unknown` and `layer` is `official` (stratum
  evidence) until `--header-extra` gives them; each such gap is a warning in JOB_META.json.
- **Check** (`v122.check`, called by the runner on every response): a bad envelope, another request_id, coverage not
  complete, end not seen, pages seen not equal to pages sent, an unreadable page or an unresolved boundary fail the whole
  request (a failed attempt, never data). An observation with a field outside prompt §4, a quote not verbatim in its named
  block (white space collapsed, nothing else), first decisive words on a context page, or `endorsed` without a named body and
  located support is rejected alone, with the reason; the rest are kept (`ok_with_validation_problems`).
- **Reducer** (`scripts/extraction/reduce_v122.py`): observations of one model -> the eight cells in the shape that
  `derive.py` and `derive_index.py` read, plus the statutory F3 column (companion legal documents, ADR-013 P2), the PET profile,
  wholesale PET context, descriptive records (F11, F12, status, legal) and the ledger of every decision. Layer rules, status
  precedence, newest document, conflict, F3 via_both and none_stated only from a closed search, the F2 premise join, route D with
  `translation_uncertain` -> partial (P4), policy pledges set no value: see the module docstring. Search closure is true only
  when every owned page of every planned request of every document of the project came from a request that passed the check
  (audit A4c fixture 3). `--drop-route-d` gives the view without route-D documents (fixture 2).
  `python scripts/extraction/reduce_v122.py --job <job> --run-dir <work>/<run> --out <file outside the repository>`.
- Output limits per stage when not given: talk L1 400 expected / 8,000 max tokens, talk L2 800 / 8,000, extraction
  16,000 / 64,000 (reasoning counts toward the limit).

## Cost (MB, 23 Nov 2026: batch calls, credit auto-reload off)

| provider | model | interface used | saving |
|---|---|---|---|
| Anthropic | claude-opus-5-5 | Message Batches | 50 % on every token; system prompt cached (1 h), cache reads at 0.05 × input |
| OpenAI | gpt-6.2-sol (ADR-014) | Batch API on /v1/responses | 50 %; system prompt as a developer message, `prompt_cache_key` per prompt, cached input at 0.05 × |
| DeepSeek | deepseek-v4-pro | Chat Completions, 8 parallel calls | no batch interface; the provider caches repeated prefixes itself |

- `runner.py plan` prints tokens and a cost estimate and makes no call. `run` refuses to start without `--max-usd`; before every
  submission it adds measured cost, the estimate of batches in flight and of the next chunk, cuts the chunk to fit the cap, and
  stops (exit 4) when nothing fits.
- Exhausted credit (HTTP 402, `billing_error`, `insufficient_quota`, "credit balance is too low", "Insufficient Balance") stops
  the run (exit 3). Every paid response is already on disk; batches in flight stay recorded. After a top-up the same command
  collects them and sends only requests without a completed attempt: nothing paid is sent twice.
- Prices: `pipeline/PRICES.json`, list prices with their source. The DeepSeek row is the peak price reported in the press
  (16 Aug 2026), with the cache-hit price set to the miss price: **to be checked on the provider's page before a paid run.**

## Records

Every attempt goes to `<work>/<run>/ATTEMPTS.jsonl` at once (with response text: the work folder is outside the repository).
A response that the strict parser refuses, or that stopped for length or refusal, is a failed attempt, never a label; it is not
re-sent unless `--retry-unparsed` is given (then the retry is a new attempt row). Transport errors and expired batch items are
retried up to `--max-attempts`. A run cannot be continued with another job file, prompt, model or parameters.
`runner.py record` writes `data/<stage>/runs/<run>/` and runs the validator of `run_statement.py`.

## Estimate for the development round on NO and UK (estimate, not a measurement)

Jobs built on 23 Nov from the unit set v13d (25 documents, 2,449 candidate units). "Likely": system prompt cached, 4 characters
per token, output per request as below (reasoning included, never measured). "Cap": no cache, 3 characters per token.

| part | requests | output per request | claude-opus-5-5 | gpt-6-astra | deepseek-v4-pro | three models, likely (cap) |
|---|---:|---:|---:|---:|---:|---:|
| talk L1, one unit per request | 2,449 | 400 | 12 | 31 | 9 | 52 (80) |
| talk L1, one page per request | 578 | 900 | 6 | 15 | 3 | 24 (31) |
| talk L2, about 600 units, one per request | about 600 | 700 | 5 | 12 | 3 | 21 |
| extraction, one request per document | 25 | 16,000 | 5 | 12 | 2 | 19 (22) |

USD at list prices. gpt-6-astra is the largest share in every row. The unknown that moves the total most is reasoning output.

## Not done

- api.openai.com and api.deepseek.com are blocked by the cloud network of this project; Anthropic is reachable. Either the
  hosts are allowed in the environment's network settings, or the runs for those two providers are made on MB's computer.
- Extraction header: `decision_authority` and `layer` per document are not yet in the repository (`unknown` / `official`).
- Not in the reducer yet: links across documents by references (P3), supersession across differently named designs, the
  three-model combination with the human adjudication in the core (only the unanimity rule outside it), the PET taxonomy join.
- Header of the talk requests and packing are DRAFT and are fixed at the freeze together with the prompts.

## Keeping the responses (23 Nov 2026)

Extraction and translation responses hold source text, so only their hashes go into the repository (RUN_RECORD_SPEC
"Responses"). The work folder of a cloud session is lost when the session ends. After every run, and during a long run after
every collected batch, zip the run folder (`<work>/<run>/` with ATTEMPTS.jsonl and STATE.json) together with its job folder to
`/mnt/project-files/<stage>-runs/` and record the zip's SHA-256 in the run's PR. Before zipping, check every
`response_sha256` against its text. The zips of the blind core are stored, not opened, until the blind cells are locked.
The pilot of 23 Nov: `/mnt/project-files/pilot/runs-2026-11-23/PILOT_RUNS_2026-11-23.zip`
(`befa6b34cd3f93aebba1c7ab8658bfe0cad9d56b34528540277cb1b4770deb6a`), all 520 response hashes match.
