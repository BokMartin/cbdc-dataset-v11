# Archived extraction-script versions used in the development runs

Each file is the exact text of `extract_api.py` whose SHA-256 (UTF-8 text, universal newlines — the script's own hashing convention) is recorded in the run manifests. The three intermediate versions were never committed on 18 Oct 2026 (the script was patched between runs); they were reconstructed on 2 Nov 2026 by reversing the recorded patches and are verified by hash. This closes the provenance gap named in the consultation (Part IV §6). From Phase 1 on, every run copies the script it was run with into its own run folder.

| File | SHA-256 (prefix) | Runs | Notes |
|---|---|---|---|
| `extract_api_67d852e8.py` | 67d852e8… | NO v1 `20261018T123819Z`, UK v1 `20261018T124736Z` | committed as 50bc586; contract v1; two-stage only; `messages.create`, max_tokens 16000 |
| `extract_api_a1f25912.py` | a1f25912… | NO `both_20261018T134857Z`, UK `both_20261018T135122Z` | contract v1.1 cells (F3 single, F12), single mode added; exception text stored instead of raw response; no salvage, no resume |
| `extract_api_e3387295.py` | e3387295… | NO `two-stage_20261018T140158Z` (failed stage 2: SDK required streaming) | salvage of truncated arrays, `--resume`, raw text preserved on parse failure, max_tokens 32000 |
| `extract_api_e1cd7870.py` | e1cd7870… | NO `two-stage_20261018T140215Z`, UK `two-stage_20261018T141047Z` | streaming calls |
| `extract_api_e9aa87cc.py` | e9aa87cc… | none (post-run patch) | value `unknown`/empty → `n/d` in `write_fill`; version shipped in the consultation pack |

An earlier NO run `20261018T123748Z` (hash db1456d0…) failed on every document (`temperature` rejected by the provider) and produced no rows; its script differed from 67d852e8 only by passing `temperature=0`. Not archived separately.
