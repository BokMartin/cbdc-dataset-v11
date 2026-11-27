# Incident ledger of the production runs (23 to 24 Nov 2026)

Written 26 Nov 2026 after audit A5 (finding 6, finding 7, item 7, item 29). It covers the extraction stage EX2 of the final
archive `PROD_RUNS_FINAL_2026-11-24c.zip` (SHA-256 `c23bb74da5c152ebf3872c9655973f34f2f2f194335240a55ac090ec4a5ef0e1`) and
the pre-amendment stage EX. The counts were recomputed offline from the attempt logs with `scripts/extraction/reduce_v122.py`
(`requests_from_run`) and the rebuilt request file (SHA-256 `5590a8da…`, identical to the freeze). No model call was made.
Aggregates only: no cell value and no source text.

## 1. Requests that failed the v12.2 check

| | Claude | Sol | DeepSeek |
|---|---:|---:|---:|
| requests | 376 | 376 | 376 |
| failed the check (persistent after retries) | 37 | 58 | 4 |
| passed, no rejected claim (`ok`) | 307 | 279 | 167 |
| passed with rejected claims (`ok_with_validation_problems`) | 32 | 39 | 205 |

A failed request supplies nothing (prompt §6). Ranges by the number of models with an accepted response: three 312, two 33,
one 27, none 4 (of 376). The 4 ranges with no accepted response from any model: `HU_HU_Hungary_2025:p1-24`,
`ID_CAND-099:p1-25`, `ID_CAND-099:p26-44`, `NZ_NZ_RBNZ_cbdc-insights-dossier-for-public-1:p35-73`. These, and then the
single-model ranges of the projects that decide the hypothesis, are the first place to look before any paid repair is
considered (audit item 6).

## 2. Passed responses that lost claims

| | Claude | Sol | DeepSeek |
|---|---:|---:|---:|
| claims rejected one by one by the check | 45 | 102 | 682 |
| of which "quote not verbatim in its block" | 14 | 10 | 467 |
| of which "keys differ from prompt §N" (an extra key `confidence`) | 0 | 54 | 0 |
| of which "segment longer than N words" | 6 | 35 | 72 |
| passed responses with an empty claim list | 53 | 58 | 47 |
| passed responses in which **every** emitted claim was rejected | 0 | 1 | 9 |

The ten responses that lost every claim:
- Sol: `KZ_CAND-160:p30-48` (54 claims, all with the extra key `confidence`).
- DeepSeek: `CA_CA_Jasper_Phase12_2017:p25-47`, `HU_CAND-095:p1-1`, `IN_IN_RBI_ConceptNote_2022:p24-44` (16 claims),
  `NG_CAND-206:p51-133`, `NG_CAND-206:p134-211`, `RU_CAND-270:p39-43`, `SE_SE_Riksbank_2017:p37-44`,
  `SE_SE_Riksbank_PaymentsReport_2026:p74-80`, `ZA_CAND-377:p1-25`.

Until 26 Nov the reducer counted these ranges as searched. Since the repair of 26 Nov (`docs/REDUCER_REPAIR_2026-11-26.md`)
they do not close a negative search. An empty claim list in a passed response still counts as "searched, nothing found";
whether a long but off-topic range with an empty list is plausible is an inspection lead, not proof of a fault (audit item 7).

Open, for the authors (agenda ADR-018): an offline diagnostic of what a tolerant check would admit (the Sol key `confidence`
dropped, DeepSeek quotes matched after whitespace and hyphenation normalisation), reported as a sensitivity only. No paid re-run.

## 3. Other incidents

- **Pre-amendment stage EX.** Before amendment 1 of the freeze, the stage EX attempted 5, 3 and 6 request keys (Claude, Sol,
  DeepSeek) and completed 2, 2 and 6; it is kept in the archive and not used for any cell. The brief of 26 Nov said "six per
  model", which describes neither number.
- **Duplicate attempts in DeepSeek's `RESPONSES.jsonl`.** The file holds more than one attempt for some requests; every
  derivation reads the complete attempt from `ATTEMPTS.jsonl` (`requests_from_run`, and step 5 of the recompute script).
- **Cached input share of EX2**: 32.18 % (Claude), 30.54 % (Sol), 43.89 % (DeepSeek) of input tokens, from `RUN_META.json`.
  The brief of 26 Nov gave 32 to 38 %.
- **Line endings.** On Windows `build_jobs.py` wrote CRLF, so the first line of the replay report differed although every
  request body matched. Since 26 Nov the request file is written with LF explicitly.
- **Header layer.** Every EX2 job carries 414 warnings because `decision_authority` and `layer` are never populated in the
  headers: evidence documents default to `official`, inclined documents to `unknown` (audit finding 2). The classification
  of the documents concerned is an author task (agenda ADR-018).
