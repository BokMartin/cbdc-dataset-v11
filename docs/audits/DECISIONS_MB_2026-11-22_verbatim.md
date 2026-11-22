# MB's decisions of 22 Nov 2026, in his own words (source record for audit A4b)

What this is: the questions the pipeline assistant put to Martin Bok (MB) in the project chat on 22 Nov 2026 between 12:24 and 13:17 UTC, going through section 6 of the consistency check (`03_CONSISTENCY_CHECK_2026-11-22_cs.md`) one point at a time, and MB's answers **verbatim in Czech**, each followed by an English translation made by the assistant. The questions are summarised in English; the answers are not summarised. Dominik Stroukal (DS) did not take part and has confirmed none of this. Nothing below has been written into the repository.

Translation note: MB writes informally and without diacritics in places; the translation keeps his meaning and does not smooth over ambiguity. Where the assistant restated an answer to MB and he did not object, that is marked "restated by the assistant, not contradicted".

---

## Point 1. When blind F-cell coding and registration happen (finding V1)

**Proposal put to MB:** register the index definition, hypotheses and known cases now, before the first paid call; run the provider probe and development rounds only on units of development projects (NO, UK, maybe others), leaving the rest unexposed; lock the blind cells before verifying production output; state in the registration the true number of blind-coded projects (at most 40: NO and UK are exposed, CL and CZ have no English text); the authors could code the Czech CNB documents from the original.

**MB, 12:28:**
> Definici indexu, hypotézy a známé případy zaregistrovat hned, před prvním placeným voláním. - ano tady souhlasím jen si musíme být jisti finální podobou indexu a hypotézy. Vývojová kola a sondu poskytovatelů pouštět jen na větách z vývojových projektů (NO, UK a případně další, které určíte). Ostatní projekty zůstanou nedotčené. - ano souhlasím, vývojové kolo bych udělal z důvodu času a námahy jen jedno na NO a UK jako nejvíce robustní z pohledu dokumentů. Slepé buňky zamknout dřív, než začnete ověřovat produkční výstupy modelů. - co je přesně definice slepé bunky? ale ano souhlasím. Do registrace napsat skutečný počet slepě kódovaných projektů, nejvýš 40, protože NO a UK už znáte a CL a CZ nemají anglický text. Dokumenty ČNB můžete kódovat přímo z češtiny. kodovat bychom měli ty země kde máme dostatatek relevantních T1 T2 dokumentů bez ohledu na jazyk dokumentu, proto jsme řešili překlady. k ČNB dokumentům se budeme stavět jako k ostatním i když rozumíme česky. - stejně by měl proběhnout překlad do aj.

*English:* "Register the index definition, hypotheses and known cases now, before the first paid call: yes, I agree here, we just have to be sure of the final form of the index and the hypotheses. Development rounds and provider probe only on units of development projects: yes, I agree; for reasons of time and effort I would do only one development round, on NO and UK, as the most robust in terms of documents. Lock blind cells before verifying production model outputs: what exactly is the definition of a blind cell? but yes, I agree. True number of blind-coded projects, at most 40...: we should code the countries where we have enough relevant T1 T2 documents regardless of the language of the document, that is why we dealt with translations. We will treat the CNB documents like the others even though we understand Czech; translation into English should happen anyway."

**Follow-up by the assistant (12:29):** a blind cell is one F-cell value for one project that each author fills alone, from the project's documents only, before seeing what a model or the other author said. If only T1 and T2 are coded, that is 15 projects (16 with Canada), 13 to 14 after removing NO and UK; the index for the 28 T3 projects would rest on the model plus author verification. Czechia is T3 and the translation rule allows machine translation only for projects with five or more publications (like Chile): should an exception be written so CZ (and CL?) get translated? It is a paid call.

**MB, 12:32:**
> proč odečítat NO a UK? u nich to uděláme znova. přece extrakce poběží na třech modelech. ano něco jsme na nich testovali ale budeme s nima pracovat v extrakci standartně. jen je využijeme na testovací kolo. [...] ne zádný překlad držme se našeho přístupu. No tedy máme 16 relevantních CBDC projektů.znalyzujeme všechny t1 a t2 dokumenty co jsme určili a u zemí kde není dostatečný počet dokumentů zkrátka uvedeme že se jedná o exploratory / často uncompleted CBDC research. ale výsledky z toho co zatím mají uvést můžeme. at mapa na webu nepůsobí prázdně

*English:* "Why subtract NO and UK? We will do them again. The extraction will run on three models after all. Yes, we tested something on them, but we will work with them in the extraction as standard; we will just use them for the test round. [...] No, no translation, let us stick to our approach. So we have 16 relevant CBDC projects. We will analyse all T1 and T2 documents we have determined, and for countries without a sufficient number of documents we will simply state that this is exploratory / often uncompleted CBDC research. But we can report results from what they have so far, so that the map on the website does not look empty."

**Restated by the assistant (12:32), not contradicted:** the core of the analysis is the 16 T1 and T2 projects; T3 projects are analysed from what they have and labelled in the paper and on the map as exploratory, often unfinished CBDC research. No exception to the translation rule: CZ and CL stay without readable text, so the paper speaks of a frame of 44 projects measured on 42. NO and UK stay in extraction and index and run as standard on three models; the authors' own coding of NO and UK is not presented as blind, so inter-coder agreement counts 14 projects and NO and UK are reported as development cases.

## Point 2. Source of the index cells and combination of three models (V2)

**Proposal:** the index source is the adjudicated cell, with its provenance stated (blind-coded, or model plus verification); the index is also reported from blind cells only; with three models a cell has a value only when all three agree and the quote is located; otherwise the two authors decide.

**MB, 12:34:** "ano" (*yes*).

## Point 3. Wording of the talk-against-commitment hypotheses (V3)

**Proposal:** report the gap descriptively with intervals and no test against zero; measure "talk without substance" inside the sentences (share of privacy sentences naming a concrete mechanism, share naming a concrete decision); add a directional version (aspects where the maker promises protection but the described design does not deliver it); report by tier T1/T2/T3; regenerate the mock data with the design-to-talk coupling.

**MB, 12:35:**
> nevím jestli si to správně pochopil - chceme měřit to, že například v dokumentech UK je (a ted si vymýšlím) 500 vět o privacy - tváří se to jako klíčové téma stále omývané. ale pak zjistíme, v F1-12 commitments a volba PET zas tolik privacy nenabízí - tedy o privacy se hodně mluví ale reálné commitments chybí. a to už je zajímavý output.

*English:* "I don't know if you understood correctly: we want to measure that, for example, in the UK documents there are (I am making this up) 500 sentences about privacy; it looks like a key topic, constantly repeated. But then we find that in the F1-12 commitments and the choice of PET not that much privacy is offered; that is, privacy is talked about a lot but real commitments are missing. And that is already an interesting output."

**Assistant's answer (12:36):** this stays the main output. On the UK example: (1) how much is said: privacy sentences scaled by document length; (2) how much has substance: share naming a mechanism or decision; (3) what is committed: F-cells and PET, i.e. the index with its interval; (4) where it contradicts: aspects with a promise of protection whose described design does not deliver it. Only one number is dropped: the sign test of "aspects with talk but no design minus aspects with design but no talk" against zero, because every design sentence is also talk, so the test is positive for almost any data. The brief forbids subtracting a talk share from a commitment share into one number, so they are shown side by side.

**MB, 12:37:**
> ano to dává smysl - ale ještě si tyhle naše utvrzené návrhy necháme zuaditovat druhým LLM až tady skončíme

*English:* "Yes, that makes sense, but we will still have these settled proposals of ours audited by a second LLM when we finish here."

## Point 4. Composition and name of axis 1 (V4)

**Proposal:** (1) rule: the latest claim at the highest status reached applies; concurrent incompatible variants give an undetermined cell flagged "variants open"; (2) call it "stated-design privacy index" in the paper; (3) either report F10 beside the mean, or widen the definition of the axis to "control over the payment and its attribution" and keep F10 in the mean; (4) keep eight cells in the main index and treat F7 and F8 as one component in a sensitivity variant; (5) decide the direction of F3 and F9 before registration, proposal: less access by authorities and no later re-identification means more privacy.

**MB, 12:44:**
> u 3 ky mi dává větší smysl rozšířit definici. Jinak klíčové je zakomponovat ty definice PET z druhého článku pod F7 jak jsme říkali. vytěžit z toho článku co nejvíce dovedeme. je to ideální zdroj definic PET a technických solution vzhledem k privacy. Jinak souhlasím s tím co navrhuješ

*English:* "For 3, widening the definition makes more sense to me. Otherwise the key thing is to incorporate those PET definitions from the other paper under F7, as we said. Extract from that paper as much as we can. It is the ideal source of PET definitions and technical solutions with respect to privacy. Otherwise I agree with what you propose."

**Assistant (12:44):** PET definitions and classification from Nijsse and Pinto (arXiv 2602.23659) taken as a published code list; for each project, which technique the documents name, with quote and status. Question: yesterday PET was agreed as a new cell of its own, reported as a profile beside the index, not part of the numeric scale; today "under F7". Is PET a separate cell attached to the anonymity aspect, beside F7, or should the PET choice change the value of F7? Recommended the first: the same technique can sit in a design where the central bank still sees everything, so it would bias F7.

**MB, 12:46:**
> k PET co navrhujes a opět se řídit tím -že novější dokument má větší váhu než starší. jinak souhlasím se vším v bode 5

*English:* "On PET, what you propose, and again follow the rule that a newer document has more weight than an older one. Otherwise I agree with everything in point 5."

## Point 5. May a wholesale document give a retail cell a LEANING value? (V5)

**Proposal:** split the INCLINED layer in two. Joint retail reports in which the maker takes part (today 2 documents: BoE and MIT, Tourbillon) may give a LEANING value. Wholesale experiments stay in the database and on the website as context and as a source for the PET profile, but give no value to a retail cell. After DS confirms, align rule D1, the contract and AGENTS.md with ADR-010 in one PR.

**MB, 12:46** (same message as above): "jinak souhlasím se vším v bode 5" (*otherwise I agree with everything in point 5*).

## Point 6. Translation check and translated documents in the index (V7)

**Proposal:** (1) a Chinese benchmark pair (the 2021 e-CNY white paper has an official English edition; translate the Chinese original by the same procedure and compare; one small paid call); (2) main index from all readable documents including machine translation, plus a variant from English originals and issuer editions only; align the contract with ADR-009; (3) report translation-check results by text route.

**MB, 12:47:**
> u překladů a problemy s překladu chci cestu nejmenšího odporu. zkrátka pokud vznikne problém a bude to překladový problém tak to je ten nejmenší problém. tedy vyber takové řešení prosím

*English:* "For translations and translation problems I want the path of least resistance. Simply, if a problem arises and it is a translation problem, that is the smallest problem. So please choose such a solution."

**Assistant (12:47), not contradicted:** no Chinese test and no extra paid call; machine-translated documents enter the index normally; a variant without them is computed automatically beside the main result; the paper states it in one sentence among the limitations; the contract is aligned with ADR-009.

## Point 7. Deadline and order of cuts (V8, S10)

**MB, 12:48:**
> tady ti asi nerozumím - rozved ten problém prosím . Deadliny ted prosím neřeš vůbec. jak se to stihne se to stihne

*English:* "I probably don't understand you here, please elaborate the problem. Please do not deal with deadlines at all now. It will be done when it is done."

**Assistant (12:48):** the problem was only that the repository holds two different lists of "what we drop if time runs out" that contradict each other, one of which drops cells now in the index; proposal: remove both lists and register the full scope; any later omission is recorded as a deviation with a reason.

**MB, 12:51:**
> prosím všechny takovéhle time specific věci z repa odstran - repo má sloužit k postupu a výstupu prace ale tyto interní problémy mě a Dominika by neměly vůbec obsahovat a určitě by neměli zasahovat do kvality práce. Bunky chceme všechny co jsme si definovali. se slepým kodováním souhlasím. - raději 80 vět - i to je dost. pokud shoda nevýjde tak to opět projdeme spolu aby byla shoda mezi námi

*English:* "Please remove all such time-specific things from the repo. The repo is to serve the procedure and the output of the work, but it should not contain these internal problems of mine and Dominik's at all, and they certainly should not interfere with the quality of the work. We want all the cells we defined. I agree with the blind coding [point 8]: rather 80 sentences, even that is a lot. If agreement does not come out, we will again go through it together so that there is agreement between us."

(Applied: PR 11, merged 22 Nov 13:11 UTC, commit `6f83b67`: dates and cut lists removed from the working documents; audit reports unchanged.)

## Point 8. Blind coding of voice and aspect (S4)

See MB's 12:51 message above. **Restated by the assistant (12:52), not contradicted:** both authors label voice and aspect blind on 80 sentences; if agreement falls short they go through the disagreements together as on 22 Nov; the blind agreement is reported as it came out, and the final labels are the joint ones.

## Point 9. ANONYMITY and F7; how to record a rejected variant (S1, S2)

**Proposal:** (a) map the talk aspect ANONYMITY to F7, but narrow it in the codebook to anonymous holding and anonymous paying; general sentences ("privacy matters to us") go to GENERAL. (b) An explicit rejection ("we will not introduce a fully anonymous CBDC") is a decision, so it is recorded as a value (F7 = no) with status endorsed, plus an automatic check that the cell's quote and the label of the same sentence do not contradict each other.

**MB, 13:04:** "ano souhlasím." (*yes, I agree*). The assistant asked at 13:04 whether this "yes" referred to point 9 or to PR 11; MB's next message (13:05) answered the PR 11 questions and did not object to reading 13:04 as agreement with point 9.

## Point 10. Status as two fields instead of one ladder (S3)

**Proposal:** report status as two fields side by side, decision (none, considered, endorsed) and implementation (none, pilot, operational); what counts as a commitment is set by the contract's single admissibility rule (`admissible()`), not by a rung on a ladder; both scripts call the same rule.

**MB, 13:11** (quoting the proposal): "Stav hlásit jako dvě pole vedle sebe: rozhodnutí (žádné, zvažováno, schváleno) a zavedení (žádné, pilot, provoz)." *(Report status as two fields side by side: decision (none, considered, endorsed) and implementation (none, pilot, operational).)* **Restated by the assistant (13:11), not contradicted:** point 10 recorded including commitment by the one admissibility rule.

## Point 11 and six smaller confirmations (points 12 to 17)

**Proposals put to MB (13:17, one message, "write the numbers where you disagree"):**
- 11. Cutoff of the corpus = the day the corpus is frozen before the production run; a full issue date for every document.
- 12. Tiers T1 to T3 are named in the documents as the state frozen on 17 Nov, because they are no longer purely a function of the number of publications (Canada has four and stays T2).
- 13. The seven machine translations that already exist for T3 projects (e.g. China, Peru, Thailand) are used, and the paper says so. The rule for new translations does not change.
- 14. The status of seven projects listed as "unresearched" (among them Kazakhstan and Taiwan of T1, and Nigeria) is filled in from their own documents and sent to MB for confirmation.
- 15. The exposure ledger (ends 13 Nov) is completed: development sample, translation judgement, today's adjudication, reading of Nijsse and Pinto. Question: does it still hold that Dominik has not read Table 2 of that paper?
- 16. Corpus additions from the literature: on 21 Nov documents were added only for projects cited by Nijsse and Pinto (EU, JP, CH, UK). A column "found via" is added to the document list and one sentence to the paper; the same check is not done for the other T1 and T2 projects.
- 17. Accuracy on the whole corpus: the 400-unit reference sample is drawn by quotas and stores no inclusion probability. The draw is changed to store it; this costs nothing and lets the paper claim model accuracy on the whole corpus.

**MB, 13:22:**
> 15. ano dopln - nevím jakou tabulku z jakého článku myslíš.  17 - čím menší referenční vzorek co ještě projde tím lepší. jinak souhlasím

*English:* "15. Yes, complete it; I don't know which table from which paper you mean. 17: the smaller the reference sample that still passes, the better. Otherwise I agree."

So points 11 to 14 and 16 are accepted as proposed; 15 accepted; 17 accepted, with MB's added wish that the reference sample be as small as can still be defended (today planned at 400 units).

## Outside the eleven points: the second corpus (ADR-005 §5)

**Question (13:06):** ADR-005 §5 records the A3 proposal of two corpora: the commitment corpus (today's) and a talk corpus of all official retail-CBDC communication of each project, privacy-related or not, never collected. Without it, "500 privacy sentences for the UK" holds, but "privacy is a third of the Bank of England's CBDC communication" does not, because the corpus is selected. Options: keep as is (result named "privacy statements in the selected evidence corpus", no claim about the share of total communication), or collect the second corpus.

**MB, 13:09:** "nechat jak je" (*keep it as it is*).

**Follow-up on 15 (MB, 13:22):** asked whether Dominik has read Table 2 of Nijsse and Pinto (the table that rates 20 CBDCs on privacy, 14 of them in this project's frame), MB answered:
> ano četl

*English:* "yes, he read it." Both authors have therefore read that table before any blind F-cell coding.

## Not yet discussed with MB

The engineering repair V6 (needs no author decision) and addendum §8 point 6 ("44 projects" in the title; point 1 above says "frame 44, measured 42").
