# Privacy-talk instrument: what the pilot shows and a proposal for v13 (12 Nov 2026)

Status: proposal for the authors (MB, DS). Nothing here changes the contract until they decide. Evidence grade: section 2 is measured on the corpus with a deterministic script and no model (`scripts/census/talk_pilot.py`, aggregates in `data/census/TALK_PILOT_aggregate.json`); sections 3 to 6 are design argument; the literature anchors in section 7 are from memory and must pass a citation check before they enter the paper.

Question (MB, 12 Nov): how to improve the extraction of privacy-related statements so that it says as much as possible for the paper and carries academic weight.

## 1. Where the present system is weak

The posture survey of 2 Nov (one model, one pass, 125 core documents, 2 628 typed statements) was built to design the layer, not to measure. Read as a measuring instrument it has five weaknesses.

1. **Quotation error.** 16 % of the statements could not be located in the document (415 of 2 628). The model writes the quote, so it can mis-quote.
2. **Recall is unknown.** Nothing estimates how many statements the model missed. A count that can only be checked for false positives cannot support a claim that a project "says little".
3. **No defined unit.** A "statement" is whatever the model chose to list. Two coders cannot be compared on agreement when they do not code the same units, so there is no reliability coefficient.
4. **The typology leaks.** OTHER is the largest of the 17 types (389 statements, 15 %), and it mixes the bank's own positions with reported public opinion and literature.
5. **Aggregation is unvalidated.** The Talk index is planned as a count over statement types per project and year. Whether such a number is a property of the project, or of the documents that happened to be collected, had not been tested.

## 2. Pilot: what a sentence-level salience measure looks like on the evidence documents

Corpus: every KEEP / BORDERLINE document of the 43-frame with usable English text: 250 documents of 42 projects, 118 965 sentences (192 English originals, 12 issuer English editions, 46 machine translations; 28 evidence documents have no usable English text yet). Privacy sentence = sentence containing privacy, anonym*, pseudonym*, personal data/information, data protection or confidential* (narrow dictionary); a broad dictionary adds identification, tracing, KYC/AML, minimisation, consent.

| finding | value |
|---|---|
| privacy sentences (narrow) | 3 294, i.e. 2.8 % of all sentences; median document 2.1 %; 39 documents have none |
| concentration | the top 10 % of documents hold 55 % of all privacy sentences |
| counts follow length, shares do not | Spearman with document length: count 0.62, share 0.09; project count vs number of documents 0.67, project share 0.25 |
| document kind matters | pooled salience from 0.2 % (annual reports) and 0.9 % (legislation) to 9 % (technical papers, design notes); kind alone explains 19 % of the variance of document salience |
| how privacy is talked about | of privacy sentences, 51 % carry no modal marker, 21 % possibility (could, might, would, option), 13 % permission, 11 % intention (will), 5 % obligation (shall, must) |
| agreement with the model survey | for the two exposed projects (25 documents): dictionary hits vs number of survey statements, Spearman 0.95 on counts, 0.77 on shares |
| narrow vs broad dictionary | document shares correlate 0.82 |
| **project share of variance (ICC)** | **0.16 to 0.19** of the variance of document salience lies between projects (random-intercept model, with or without document kind, length and year); the rest is between documents of the same project |
| **split-half reliability of a project score** | share-based: **0.49** (5-95 %: 0.14 to 0.72) for the 26 projects with 4+ documents; **0.73** for the 11 projects with 8+ documents; count-based 0.76, but that is the reliability of volume |

Two results are counter-intuitive and matter for the design.

**A project-level talk score from salience is not reliable for most projects.** With an intraclass correlation of about 0.17, the reliability of a project mean over k documents is k·0.17 / (1 + (k−1)·0.17): 0.45 for 4 documents, 0.62 for 8, 0.71 for 12, 0.80 for 20. The median project has 4 evidence documents. A year-by-year line for one project rests on one to three documents per year and is mostly document noise. The decision of 9 Nov to draw yearly series for T1/T2 projects is therefore defensible only for T1 and only with pooled windows or with the documents shown as points.

**Counting is the wrong aggregation.** A count-based index ranks projects by how much they have published (0.67 with the number of documents). It is reliable because publication volume is stable, not because privacy talk is. Shares remove the volume effect but expose how little project signal there is.

Limits of the pilot: a dictionary measures mention, not position; sentence splitting on a layout text layer is rough; document kind comes from the workbook pre-fill; machine-translated documents show lower pooled salience (1.9 % against 2.8 %) but they are also a different mix of genres, so no translation effect can be read from this. A statement-typed measure may have a higher project share of variance than a dictionary; that is an empirical question the new instrument must answer with the same test.

## 3. Proposal: a closed, unit-based instrument in four layers

The change in one sentence: the model stops writing quotes and starts labelling units that exist before it sees them.

**Unitisation.** Every document is split into numbered sentences (unit id = document SHA-256, page, sentence number) by a deterministic script, with the paragraph kept as context. Units, not model output, are what is counted, sampled, hashed and compared.

**L0 Mention (dictionary, no model).** The published dictionaries of section 2. Role: a transparent baseline that anyone can recompute, the denominator of the funnel, and a convergent-validity check for the model layers. Not an outcome.

**L1 Relevance (closed classification).** For each candidate unit the model answers one question: does this sentence make a statement about the privacy, identifiability or data access of retail CBDC users? Candidates are the broad dictionary hits, the encoder's top-ranked units, and a **random sample of the remaining units** (for example 5 %), so that recall is estimated instead of assumed. The model returns unit ids and labels only. Quotation error becomes impossible by construction.

**L2 Facets (replacing the flat list of 17 types).** Each relevant unit is coded on a few closed facets. The 17 types become combinations of facet values, so earlier results map onto the new scheme.

| facet | values | why |
|---|---|---|
| speaker | own position of the issuer / reported (public, respondents, literature, other jurisdictions) | separates what the bank says from what it reports; cleans most of OTHER |
| object | identity / transaction data / balances / unspecified | what is protected or seen |
| observer | central bank / intermediary / public authority / commercial third party / counterparty / nobody / unspecified | who can see |
| direction | restricts visibility / grants visibility / states a trade-off or risk / neutral | G2 against G3 without forcing one value |
| basis of the guarantee | none (declaratory) / policy / legal / architectural / cryptographic | the specificity ladder |
| status | considered / tested / endorsed / operational / rejected | unchanged from the contract |
| modality | coarse: stated as fact or decision / conditional or option; with the source term kept for translated text | the translation benchmark showed will / would / could are not stable across faithful English renderings |

**L3 Commitments.** The F-cells and the admissibility rule, unchanged.

## 4. What to report: a funnel instead of a difference of two indices

The plan of 9 Nov is a Talk index, a Commitment index and their difference. The difference of two indices on different scales is hard to defend: a reviewer will ask what one unit of it means. The same idea can be reported as attrition through the layers, per project and for the corpus:

sentences → privacy mentions (L0) → own-position privacy statements (L1, speaker = own) → statements with a mechanism (basis architectural, cryptographic or legal) → endorsed or operational statements → admissible F-commitments.

Each step is a proportion with a confidence interval, and "privacy talk without commitment" becomes the measured drop between two named steps. The two sub-indices can still be published; the funnel is what carries the argument.

For the talk side, three components, each interpretable on its own, never summed:

- **salience**: share of units that are own-position privacy statements, estimated in a multilevel model (project random effect, document kind and year fixed), reported as the shrunken project estimate with an interval and with the ICC;
- **specificity**: among own-position statements, the share with a mechanism or legal basis against declaratory ones; this is the component closest to the research question;
- **stance**: share framed as trade-off or risk against restricting visibility (already in the contract as the stance ratio).

Rules that follow from the pilot: no count-based index; a project score is published only with its reliability and interval, and flagged below a minimum number of documents; yearly series only as pooled windows or document points; document kind always in the model; T3 projects appear in the corpus-level funnel but get no project score.

## 5. Validation plan (what gives the instrument academic weight)

| property | test | reported as |
|---|---|---|
| reliability | two humans and two models label the same stratified sample of units (L1 and facets) | Krippendorff's alpha per facet, human-human, human-model, model-model; test-retest of each model |
| recall and precision | random sample of non-candidate units judged by humans; precision on flagged units | recall with interval, per dictionary / encoder / model stage |
| measurement invariance to translation | code the five benchmark documents twice, from the issuer's English and from the machine translation | agreement of unit labels and facets; this is the decisive translation test |
| convergent validity | L0 dictionary, encoder labels and L1 on the same units | rank correlations at document level |
| known groups | genres with expected high and low salience (design notes against annual reports) | difference in the expected direction |
| project signal | ICC and split-half reliability of every project-level score, as in section 2 | acceptance criterion fixed in advance (for example reliability ≥ 0.7 to publish a project score) |
| sensitivity | leave-one-document-out per project; dictionary variants; with and without route-D text | range of each project estimate |

All thresholds, samples and seeds are fixed in the registration before coding, as was done for the translation judgement.

## 6. What this costs and what it risks

Cost: one unitisation script; a revised prompt pair (L1, L2) and schema; about 12 000 to 15 000 candidate units to classify (model calls are cheap at this size); a human reliability sample of roughly 400 units for two coders; the benchmark double-coding of five documents. No new documents are needed.

Risks. Facet coding is harder for humans than a flat type, so alpha may be low on some facets; those are then merged or dropped, and that is reported. The project signal may stay small even with typed statements; the paper then says so, and the corpus-level funnel remains the main result. The sealed survey of 2 Nov cannot be re-used as data (it has no units), only as the source of the typology.

## 7. Literature anchors (to be verified by a citation check before use)

- Unit and salience: the Manifesto Project's quasi-sentence coding and salience shares; Benoit et al. on crowd-coded political text.
- Text as data and its validation: Grimmer and Stewart (2013); Gentzkow, Kelly and Taddy (2019); domain dictionaries, Loughran and McDonald (2011).
- Measurement validity: Adcock and Collier (2001); Krippendorff on content-analysis reliability.
- LLM annotation: Gilardi et al. (2023); Ziems et al. (2024); Halterman and Keith (2024) (already cited in the project).
- Central-bank communication as text: Blinder et al. (2008); Hansen and McMahon.
- Talk without commitment: cheap talk, Crawford and Sobel (1982).
- CBDC privacy design space: Auer and Böhme (2020); ECB (2019) on anonymity in CBDC; Bank of Canada staff note on privacy in CBDC technology (2020).

## 8. Decisions for the authors

1. Replace the generative statement survey by the unit-based instrument (L0 to L2)? Recommended.
2. Replace the 17 flat types by facets, keeping a mapping to the old types? Recommended; the facet list above is a draft to cut.
3. Report the funnel as the main result and the difference Talk − Commitment only as a secondary figure? Recommended.
4. Publish project-level talk scores only where reliability passes a pre-set threshold, and yearly series only as pooled windows? Recommended; it narrows the 9 Nov decision.
5. Who codes the human reliability sample, and how many units (proposal: MB and DS, 400 units, stratified by project tier, genre and text route)?

## 9. Correction of 13 Nov 2026: text mode of the units

The pilot of section 2 and the first unitisation (12 Nov) split sentences on the `pdftotext -layout` text layer. That layer keeps side-by-side columns on one line, so in multi-column documents the sentences of two columns were interleaved (found while recording issuers: in about 25 of the 250 documents more than 30 % of the long lines carry a column gap; examples NZ insights dossier, SG Project Orchid, AW 2024). `scripts/units/unitise.py` now reads the PDFs of routes A and B in reading order (no `-layout`); HTML text is unchanged. Units: 185 295 (was 149 067; the increase is table cells and list items that are now separate fragments and are excluded as stratum X), candidates for L1: 18 952 (D 7 037, N 5 792, R 6 123). Route-D text is the machine translation of record and was translated from the layout text; `layout_gap_share` in the units manifest flags the three translated documents with a share above 0.15 (PE CAND-250, TW CAND-345, TW CAND-350). They are not re-translated; they are a sensitivity case.

The figures of section 2 were computed on the layout text. Re-computed on the corrected text (`data/census/TALK_PILOT_aggregate.json`, 13 Nov): 125 178 sentences (was 118 965); project share of variance 0.13 to 0.16 (was 0.16 to 0.19); split-half reliability of the share-based project score 0.46 (was 0.49), of the count-based score 0.78 (was 0.76). The correction makes the project signal slightly weaker, not stronger; both conclusions of section 2 stand. The table of section 2 is left as first written, so that the change is visible.

## 10. Issuer and voice of the documents (13 Nov 2026)

`scripts/review/record_issuers.py` records issuer, issuer type and a document-level voice class for all 278 evidence documents (`data/manifest/ISSUERS_2026-11-13.csv`): 253 central bank, 17 government, 8 legislature; 197 institutional, 20 official speeches, 17 legal texts, 15 joint with external partners, 11 joint with government, 10 staff-authored, 5 meeting records, 2 commissioned from a contractor, 1 official article. It is a pre-fill for the authors (tier workbook of 13 Nov). The document-level class does not replace the unit-level voice facet: 81 documents are not plainly the institution speaking in its own name, which is why the facet is needed.
