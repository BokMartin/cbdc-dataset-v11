# Synthetic test request for the extraction prompt (invented; no real issuer)

Everything below is invented by the pipeline assistant for this audit. "Bank of Examplia" and the "digital exa" do not exist. The text is built to hit the traps the prompt claims to handle. The block between the two lines of `~~~` is exactly what the runner would send as the user message.

~~~
HEADER
doc_key: EX_BoEx_2025-05_design-note
project: EX
issuer: Bank of Examplia
issuer_type: central_bank
decision_authority: Board of the Bank of Examplia
issue_date: 2025-05-12
document_type: design note
layer: official
text_route: A
text_layer: reading_order
pages_total: 5
pages_in_this_request: 1-5 of 5
page_span: whole_document

TEXT
=== PAGE 1 ===
Bank of Examplia | Digital exa: design note 2 | May 2025
DIGITAL EXA
Design note 2: privacy and data
i
=== PAGE 2 ===
Bank of Examplia | Digital exa: design note 2 | May 2025
1. Decisions taken so far
On 3 March 2025 the Board decided that, if the digital exa is issued, it will be distributed only through supervised intermediaries, which will onboard users and verify their identity. The Bank will not look at the personal data of users. The Bank's ledger will record only pseudonymous wallet identifiers, and the Bank will hold no information that links these identifiers to persons. Privacy is a fundamental right and a key design principle of the digital exa.
A fully anonymous digital exa, like cash, will not be offered.
2
=== PAGE 3 ===
Bank of Examplia | Digital exa: design note 2 | May 2025
2. Options under study
Staff are exploring an offline mode based on secure elements in phones, in which the details of an offline payment would not be shared with intermediaries
=== PAGE 4 ===
Bank of Examplia | Digital exa: design note 2 | May 2025
until the device next connects, when only the net balance would be reported. In a 2024 experiment with the University of Examplia, blind signatures were tested to make offline tokens unlinkable to the payer. Wallets with a balance of up to 500 exa could be opened with a phone number only; no decision has been taken on such wallets. Expiry dates for stimulus payments are not envisaged. A holding limit of 3,000 exa per person is under consideration.
Law enforcement authorities may obtain transaction data from intermediaries under the same rules as for bank accounts. In exceptional cases, with a court order, the operator of the pseudonym registry may be asked to link a wallet identifier to a person. The core ledger will be a centralised system operated by the Bank.
3
=== PAGE 5 ===
Bank of Examplia | Digital exa: design note 2 | May 2025
Annex A Tab1e of resu1ts  ▯▯▯ 0f th3 pi1ot ▯▯ wa11et  ▯▯▯▯ 4 ▯ 7 ▯▯ ex@ ▯▯ ▯▯▯
=== END OF REQUEST TEXT ===
~~~

## What the auditor is asked to do with it

Write the JSON the prompt asks for (question 10 of the prompt). For every claim, say whether the prompt determines the answer, or whether two careful models could legitimately disagree, and why. Include at least:

- the page-2 sentences on the Board decision, on "will not look at" (basis) and on the pseudonymous ledger (basis and status: is the second sentence covered by the Board decision?);
- the sentence about cash-like anonymity (flag, not F7 = no);
- the offline sentence that runs from page 3 to page 4 (`spans_pages`, status, basis, F4);
- the 2024 experiment (PET `blind_signatures`, status, `design_or_experiment_id`, whether it belongs to the retail design);
- the phone-number wallets (F7 status; F8);
- "not envisaged" for expiry dates (F10 value and status);
- the holding limit (not F10);
- lawful access "under the same rules as for bank accounts" (F3);
- the court-order linkage (F9; actor);
- the centralised ledger (F12 core_ledger; status);
- running headers, printed page labels `i`, `2`, `3`, and the garbled page 5 (`unreadable_pages`);
- `cells_with_no_claim`.
