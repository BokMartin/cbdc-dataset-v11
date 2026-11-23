# Runner for the three models (draft, 23 Nov 2026; no paid call made yet)

`scripts/pipeline/build_jobs.py` builds the requests of one stage (talk L1, talk L2, extraction) for a set of projects, outside
the repository; `scripts/pipeline/runner.py` sends them to one provider and writes a run record v1 (`docs/RUN_RECORD_SPEC.md`).
Offline tests with fake provider clients: `tests/test_runner.py`.

## Cost (MB, 23 Nov 2026: batch calls, credit auto-reload off)

| provider | model | interface used | saving |
|---|---|---|---|
| Anthropic | claude-opus-5-5 | Message Batches | 50 % on every token; system prompt cached (1 h), cache reads at 0.05 × input |
| OpenAI | gpt-6-astra | Batch API on /v1/responses | 50 %; `prompt_cache_key` per prompt, cached input at 0.1 × |
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
- Extraction header: `decision_authority` and `layer` are not yet in the repository and are written `not_recorded`.
- Header of the talk requests and packing are DRAFT and are fixed at the freeze together with the prompts.
