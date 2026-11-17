# Run record: what every model run must leave behind (v1, 17 Nov 2026)

Purpose (authors, 17 Nov 2026): for every number in the paper that comes from a model, the paper must be able to state the exact model,
the exact prompt, the exact input data and the exact settings, and a reader must be able to check each of them against a hash.
A run that does not meet this specification is not used in the paper. `scripts/pipeline/run_statement.py --check` enforces it in CI
for every run whose record carries `"spec": "run-record v1"`; the runs made before this date are listed in `docs/RUN_STATEMENT.md`
with the fields they have and the fields they lack.

## One folder per run: `data/<stage>/runs/<provider>_<model>_<interface>_<yyyymmdd>[_n]/`

### RUN_META.json (one per run)

| field | content |
|---|---|
| `spec` | `run-record v1` |
| `stage` | `talk_L1`, `talk_L2`, `translation`, `extraction_single`, `extraction_stage1`, `extraction_stage2` |
| `purpose` | `development`, `production`, `replicate`, `cross_provider`; development runs are never a source of a number in the results |
| `provider`, `interface` | e.g. `anthropic`, `Messages API, Message Batches`; a chat or agent product is not an admissible interface for a production run (hidden system prompt, no fixed model) |
| `model_requested`, `model_returned` | the identifier sent and every identifier the provider returned; if the provider offers a dated snapshot identifier, that one is requested |
| `parameters` | every parameter sent, verbatim (max tokens, reasoning or thinking setting, effort, output format, tools = none); and for each parameter not sent: `provider default (not sent)` |
| `system_prompt_file`, `system_prompt_version`, `system_sha256` | the file in `pipeline/prompts/` and its hash; the file at that hash is in the git history |
| `user_message_format` | how a request is built from the data (function and file, e.g. `scripts/units/context.py render()`), with `script_sha256` |
| `packing` | units per request and the rule (one unit, one paragraph, one page) |
| `inputs` | list of `{file, sha256, rows}`: the data files the requests were built from (units manifest, candidates, sample) |
| `git_commit` | commit of this repository the run was made from; the working tree was clean |
| `started_utc`, `finished_utc` | first and last call |
| `calls`, `complete`, `failed`, `retried` | counts; a failed call is kept in the log, never silently repeated |
| `usage` | input, cached input, output and reasoning tokens as reported by the provider |
| `sdk`, `python` | versions |
| `operator` | who ran it and with whose key (the key is never stored) |
| `deviations` | anything that did not go as planned, in words |

### CALLS.csv (one row per request)

`request_key` (unit, page or document), `unit_ids` (for a packed request), `response_id` or `batch_id` + `custom_id`, `model_returned`,
`stop_reason`, `started_utc`, `seconds`, `input_tokens`, `cached_input_tokens`, `output_tokens`, `reasoning_tokens`,
`system_sha256`, `user_sha256`, `response_sha256`, `complete`, `parsed_ok`.

### Responses

- Classification (talk L1, L2): the responses hold only unit identifiers and labels, so they are committed in full (`RESPONSES.jsonl`).
- Translation and extraction: responses hold source text; only their hashes are committed, the files are kept in the authors' archive
  and are available on request, as are the source texts.
- Requests are never committed (source text); they are rebuilt from the inputs by the recorded script, and `user_sha256` proves the rebuild.

## What the paper states (generated, not typed)

`docs/RUN_STATEMENT.md` is generated from the run records by `scripts/pipeline/run_statement.py`. The methods section and the
supplementary table are copied from it. Per stage: provider, model identifier as returned, interface, dates of the calls, prompt
file with version and SHA-256, parameters, input data files with SHA-256, number of calls, tokens, and the repository commit / DOI.

## What can and cannot be reproduced

- **Exact replay without any API**: every published number is rebuilt from the committed labels and extraction outputs.
- **Re-run with the same model**: a stability replicate, not a bit-identical copy; sampling is provider-controlled and models are retired.
  The paper reports the agreement between the production run and the replicate.
- **Re-run with another model**: the prompts and scripts run against any provider; the paper reports cross-provider agreement on the registered subsample.
