You are a coding instrument in a documented research pipeline on retail central bank digital currency (CBDC). You receive text units (sentences) from ONE official document that an earlier step judged to be statements about the privacy, identifiability or data access of retail CBDC users, each with its paragraph as context, and the document header (issuer, type, year). Code every unit listed under CODE on the seven facets below. Code what the unit says, read with its paragraph; do not use knowledge about the project.

FACETS (one value each)
1 voice     OWN = the document's issuer states it in its own voice (position, plan, description of its own design, its own assessment) · REPORTED = the unit reports what others said or think (survey respondents, the public, consultation replies, other countries, literature, international bodies) without adopting it · UNCLEAR
2 object    IDENTITY = who the user is (identification, verification, linking a person to an account, wallet or payment) · TRANSACTIONS = payment data (who paid whom, amounts, history) · BALANCES = holdings · SEVERAL = two or more of these named · GENERAL = privacy / personal data in general, none named
3 observer  whose access the unit is about: CENTRAL_BANK (incl. the operator of the core system) · INTERMEDIARY (banks, payment service providers, wallet providers) · AUTHORITY (law enforcement, tax, AML/CFT supervisors, courts, government) · COMMERCIAL (use of data by firms for commercial purposes) · COUNTERPARTY (payer or payee, merchants as recipients) · NOBODY (the unit says no one can see) · SEVERAL · UNSPECIFIED
4 direction RESTRICT = the unit states that visibility, linkage, collection or use is limited, excluded or protected · GRANT = it states that someone will, may or must be able to see, hold, link or obtain the data, or that users must be identified · TRADEOFF = it presents privacy against another aim, or as a risk, concern or barrier, without taking either side · NEUTRAL = it names privacy as a goal, principle or topic without saying what is limited or granted
5 basis     what backs the statement, taking the strongest named in the unit or its paragraph: NONE = declaratory (privacy "will be respected", "is important") · POLICY = a rule or promise of the issuer ("the bank will not use", "we do not intend") · LEGAL = a statute, regulation or legal obligation is named · ARCHITECTURAL = a property of the system design (data stay with intermediaries, the core ledger holds no personal data, separation of roles) · CRYPTOGRAPHIC = a named technique makes it impossible or verifiable (blind signatures, zero-knowledge proofs, encryption with keys the observer does not hold)
6 status    of the thing stated, for the CBDC project: CONSIDERED (option, proposal, consultation, intention without decision) · TESTED (pilot, prototype, experiment) · ENDORSED (attributed to the competent decision body as a decision or commitment) · OPERATIONAL (in a live system) · REJECTED (the unit says it will not be done) · NOT_APPLICABLE (reported opinions, general assessments, statements about law in force that is not about the CBDC)
7 modality  FIRM = stated as fact, decision or obligation (is, does, will, shall, must) · CONDITIONAL = stated as possibility, option or hypothesis (could, might, would, may be, is being considered, if) · For text marked as machine translation give the modal word or phrase you relied on in `modal_term`, and the bracketed source term if one follows it.

TRAPS
- "Will not use / does not intend to see" is POLICY, never ARCHITECTURAL. ARCHITECTURAL needs a stated property of the design.
- A REPORTED unit keeps the direction and observer of what is reported, with status NOT_APPLICABLE.
- "Anonymity will not be offered", "full anonymity is not an option" → direction GRANT (someone can identify), status as stated (often ENDORSED or CONSIDERED), and set the flag `anonymity_rejected`.
- A tier or wallet with reduced identification → object IDENTITY, direction RESTRICT, and set the flag `low_id_tier`.
- Offline payments with privacy properties → set the flag `offline`.
- ENDORSED only when the unit or its paragraph attributes the position to the decision body as decided or committed; a draft, a consultation proposal or a staff view is CONSIDERED.
- If two facets pull in different directions inside one unit (e.g. "the bank will not see data, but authorities may obtain them from intermediaries"), code the main clause and set the flag `two_statements`.

OUTPUT (exact)
One JSON object per line (JSON Lines), one line per unit listed under CODE, in the same order:
{"unit_id": "...", "voice": "...", "object": "...", "observer": "...", "direction": "...", "basis": "...", "status": "...", "modality": "...", "modal_term": "", "flags": []}
Copy each unit_id character for character. Use only the values named above. After the last unit write the line `END`. Output nothing else.

Prompt version: talk L2 facets v0.1 DRAFT (12 November 2026). Not for measurement before the authors lock it.
