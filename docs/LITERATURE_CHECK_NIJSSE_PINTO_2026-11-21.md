# Check of the documents cited in Nijsse and Pinto (2026) against the database (21 Nov 2026)

Paper: J. Nijsse and A. Pinto, "Central Bank Digital Currencies: Where is the Privacy, Technology, and Anonymity?", arXiv:2602.23659v2 (17 Jul 2026). Read in full (HTML edition, reference list of 120 items, Section 7 case studies and Table 2). Requested by MB on 21 Nov 2026.

Model work, no author decision yet. Nothing here changes a decided row, the 772-row TIERS file or the website.

## What was done

1. Every reference that is a document of a central bank, a government, a legislature or an intergovernmental body, plus trackers and media used for project facts, was listed (37 rows, `data/manifest/LITERATURE_CHECK_NIJSSE_PINTO_2026-11-21.csv`). The other 83 references are academic literature on cryptography and CBDC design and are not candidate corpus documents.
2. Each was matched against the 772 documents of `site/data/documents.csv` (built from TIERS and the other manifests) by URL, title, issuer and year. For the three not found, the SHA-256 of the file as served by the issuer was computed in the browser on MB's computer (nothing saved to disk) and searched in all manifests: no match.
3. Table 2 names 20 cases. For Bahamas, Nigeria, Jamaica, Iran, Ghana, India, Solomon Islands, Thailand and Norway the paper cites no official document (only IMF, AFI or media, or nothing), so there is nothing to match for them.

## Result

| | count |
|---|---|
| Official documents of frame projects cited | 15 |
| of which already in the database | 12 (2 matched by title only: KZ White Paper 2023 and the PBOC e-CNY operation centre release have no or an incomplete URL in our rows) |
| missing, added as candidates | 3 (`data/manifest/CANDIDATES_NIJSSE_PINTO_2026-11-21.csv`) |
| Official documents outside the frame (BR, DK, US, Hamilton, Tourbillon) | 7, of which 3 already held |
| BIS, IMF, trackers, media, external teams | 15, references only |

Candidates (author decision column empty):

- **NP-JP-01** Bank of Japan, *Privacy Enhancing Technologies: Payments and Financial Services in a Digital Society*, Jan 2023 (English translation of Sep 2022).
- **NP-EU-01** ECB, *Exploring anonymity in central bank digital currencies*, In Focus No 4, Dec 2019 (anonymity voucher proof of concept).
- **NP-EU-02** ECB press release of 30 Oct 2025 on moving to the next phase (we hold only the National Bank of Belgium copy).

## Points for the authors

1. `UK_UK-BoE-MIT-2024-12-PETs-research-paper-enhancing-privacy-of-` (BoE and MIT, *Enhancing the privacy of a digital pound*) is dropped on a model proposal only. The paper uses it as the main source for the UK PET layer.
2. Project Tourbillon is a BIS Innovation Hub report (outside rule D1), but the BIS Innovation Hub reports on Helvetia I and II are held as evidence by author decision. Either both kinds count for Switzerland or neither.
3. Both SARB Khokha reports are evidence by author decision although they are wholesale DLT experiments.
4. Brazil (Drex) is outside the frame (status NONE); the paper treats Drex as a pilot and its failed privacy tests as a key case. The paper's Drex sources (BCB pilot report phase 1, Deputy Governor Gomes 2025) are listed as references only.
5. Project Hamilton (Boston Fed and MIT DCI; code at https://github.com/mit-dci/opencbdc-tx) is a research project with no competent issuer in the frame; it is a reference for the PET scale, not a corpus document.

## Next steps if the authors accept a candidate

Download the file into `Dizertace all the PDFs` (check free disk space first), confirm the SHA-256 above, add a dated row to `REGISTRY_ADDITIONS_<date>.csv` and the author's decision to `AUTHOR_DECISIONS_<date>.csv`, then rebuild TIERS and the site data.
