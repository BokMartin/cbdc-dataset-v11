CBDC_MASTER_v12 — one folder with every document the project holds (built 9 Nov 2026, completed 10 Nov 2026)

Layout: <CODE>/<file>. CODE = project code of the registry (ISO-2 country; EU = all euro-area members and the ECB;
BCEAO, ECCU, BIS, UN = multi-country or international issuers). 777 files, 1 873 MB: 610 PDF, 166 HTML, 1 DOCX.

Contents
  391  registry documents of the v11 corpus (Dizertace all the PDFs / CBDC_corpus_v2), copied unchanged
    3  Norges Bank English editions (NO_memo_*_en.pdf), re-downloaded from norges-bank.no on 9 Nov 2026, SHA-256 identical to the registry
  369  gap-check candidates: all 365 candidates of GAP_CHECK_PRESCREEN_2026-11-03 whose link works (fetched 5, 9 and 10 Nov 2026) plus
       4 PDFs linked from fetched HTML pages ("__official-download.pdf" / "__attachment-1.pdf" next to the page of the same name).
       Named <CODE>__<date>__<title>.<ext>. The first 126 also sit in Dropbox "new cbdc files/<CODE>/" (same bytes).
       17 of the HTML files are JS-rendered pages saved as rendered DOM (type_flag rendered_page); 29 HTML pages change bytes at every
       fetch (dynamic_html: the recorded hash is of the kept file); 1 Kazakh rule is a .docx; the Peruvian Circular 0011-2024-BCRP was
       fetched from bcrp.gob.pe because the pre-screened elperuano.pe URL pointed at an unrelated document (noted in the download manifest).

   14  issuer English editions of non-English documents (route B), fetched 10 Nov 2026 after the English-edition check, named
       <CODE>__<date>__<title>__EN.<ext>: Kazakhstan 6 (NPCK), Japan 2 (MOF provisional translations), Russia 3 (Digital Ruble Concept
       2021 and two press releases), China 3 (governors' speeches, BIS central bankers' speeches). Listed with the original they
       belong to in data/translation/ENGLISH_EDITIONS_2026-11-10.csv; the decision on the document is the decision on its original.

MASTER_MANIFEST_2026-11-10.csv lists every file with project, source (registry/candidate), id (registry doc_id or CAND-<row> of the
pre-screen = the id of the all-documents workbook), year, title, size, SHA-256, the registry SHA-256 and hash_check (2 files DIFFER from the
registry hash: a newer version of the same page/PDF; noted), the v11 verdict and the PRE-FILLED v12 decision with its source
(MB v11 / model triage / model pre-screen). The decision of record is made in SOURCE_DECISION_WORKBOOK_ALL_v12_2026-11-10.xlsx
(column decision_v12), not here. Download provenance (URL, fetch status, content type, page count): MANUAL_DOWNLOADS_2026-11-10.csv.

Not in this folder: the English AMCM Annual Report 2025 (394 MB, manual download), 13 candidates that could not be retrieved (2 dead URLs, 7 behind RBI bot protection, 1 host that does not resolve,
1 broken TLS chain, 1 geo-blocked site, 1 file of 407 MB), each with its reason in MANUAL_DOWNLOADS_2026-11-10.csv (status not_retrieved),
and nothing from the authors' own notes. Source of truth for all lists: github.com/BokMartin/cbdc-dataset-v11, data/manifest/.
