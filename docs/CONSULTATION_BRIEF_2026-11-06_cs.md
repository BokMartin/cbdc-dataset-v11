# Podklad ke konzultaci 6. 11. 2026: CBDC privacy dataset v11 (cíl: Data & Policy, do konce roku)

Autoři: Martin Bok, Dominik Stroukal. Stav k 2. 11. 2026 večer, po nezávislém auditu a gap checku (bude aktualizováno ve čtvrtek). Repo: `cbdc-dataset-v11` (vše auditovatelné: skripty, logy, hashe, testy, CI).

## 1. Kde jsme (fakta, ne plány)

- **Rámec:** 391 dokumentů v korpusu, 125 core dokumentů, **48 projektů, 46 národních, 43 retail kandidátů** (bez unií, bez BO/BR/US; 7 statusů dosud neověřeno). Rámec je zmrazen v `data/frame/projects.csv`.
- **Instrument:** measurement contract v1.1 (F1 až F12, typologie A0 až C1, Y1 = F1, Y3 = F7, Y2 vypuštěno). Draft **contractu v2** zapracovává všech 6 pravidel konzultanta (A až F) a 28 dispozic: endorsement místo „podmíněné = závazek", status jako `decision_status` x `implementation_status`, symetrická přípustnost, F1 aktér = CB + přičitatelní agenti, zrušeno odvozování F7 z mlčení, F11 8 atomických tagů, F12 po komponentách.
- **Pipeline (opraveno 2. 11., 24 testů, CI; nezávislý audit druhým modelem 2. 11. zapracován, viz `DECISIONS/ADR-002-audit-2026-11-02.md`):** úplný citační check (celý citát, ne prefix), stavy `processing_failed`/`incomplete` se zastavením syntézy, přísná validace, archiv všech requestů, hash skriptu i promptů, jeden derivační modul s branou přípustnosti, web napojen přes doc_id.
- **Platné srovnání single vs two-stage (Norsko, kompletní pokrytí):** 4 úplné shody / 7 shoda jen v hodnotě / 6 rozdílů ze 17 buněk; citace 17/17 přesně na straně v obou módech. Shoda je shoda surových hodnot; po bráně přípustnosti je Norsko v obou módech neurčené (F1 partial). Dřívější tvrzení „two-stage je konzervativnější" bylo staženo (neplatné srovnání). **UK (18 dokumentů):** 3/12/2 (shoda surových hodnot, ne měření): single mód dává pod pravidlem C typ B?, Y1 = 1, Y3 = 0, ale two-stage má F1 i F7 jen `partial`, takže **Y1 i Y3 jsou v two-stage neurčené** (oprava po auditu; dřívější tvrzení o shodě v obou módech bylo špatně). Single mód navíc v requestu o 1,2 mil. znaků uvedl u 5 ze 17 citací tištěné číslo strany místo PDF indexu (two-stage 17/17 přesně). Pro routing to mluví pro two-stage, nebo single jen s omezeným rozpočtem; contract v2 ukládá oba lokátory.
- **Exposure ledger:** NO a UK jsou vývojové (exponované). Všechno ostatní je neexponované.
- **Nezávislý audit (OpenAI, 2. 11.):** 21 položek, 5 „not confirmed / with correction" opraveno týž den (`DECISIONS/ADR-002`): UK outcomes v two-stage neurčené, pravidlo C v kódu děravé (opraveno), ukrajinský dokument je anglicky, tvrzení o licencích staženo, posture čísla přepočítána z lokalizovaných citátů. Auditor doporučuje: měřicí a datový článek jako jádro, freeze instrumentu odložit.
- **Gap check podle pravidla D1 (všech 43 projektů):** **378 kandidátů, 354 mimo registr; major gaps u 27 projektů.** Registr systematicky postrádal rozhodnutí o statusu (tiskové zprávy, weby, výroční zprávy), legislativu, FAQ s výroky o privacy a několik primárních designových dokumentů. Prioritní podmnožina k rozhodnutí autorů: 178 řádků (`data/manifest/GAP_CHECK_PRIORITY_2026-11-02.csv`). Chile: registrovaný PoC 2025 je wholesale; Indonésie: 2 ze 3 dokumentů wholesale.
- **Jazyk (opraveno):** 106 anglických / 19 ne-anglických core dokumentů; v rámci 43 je evidence dostupná jen přes překlad u 7 dokumentů v 6 projektech (CL 2, CN, CZ, RU 2025, TW, UY); Norsko a Japonsko mají vydavatelské anglické verze (route B), Rusko 2021 také (k ingestu).

## 2. Klíčový nález: endorsement census (model-only, zapečetěno)

Jeden dotaz na projekt: existuje v korpusu stanovisko kompetentního orgánu, které **schvaluje** požadavek, zda CB může rutinně vázat online platbu na osobu (F1)? Autoři vidí jen agregát; per-projekt hodnoty jsou mimo repo (hash v repu).

| kategorie | n (z 43) |
|---|---|
| endorsed_no | 3 |
| endorsed_yes | 2 |
| operational_undocumented | 3 |
| proposal_only | 16 |
| tested_only | 9 |
| none | 10 |

Stav emise: issued 5, decided_to_issue 3, not_decided 26, decided_not_now 7, discontinued 1, n/d 1. Základ stanoviska: architektonický 28, policy 4, n/d 11.

**Důsledek:** 5 projektů má modelem označené endorsed stanovisko k F1 (ani to není ověřená dolní mez: žádné neprošlo lidskou kontrolou přípustnosti); 3 operational_undocumented se počítají jen tehdy, pokud je živé uspořádání oficiálně popsáno, což census neověřil. Určitelných Y1 je tedy nejvýše kolem 5 až 8, pravděpodobně méně. Orientační pravidlo (≥ 20 určitelných, minorita ≥ 6) **nebude splněno**. Klasifikovaná hypotéza H2 na commitment matici není proveditelná. Evidence grade: jeden model, jeden průchod, bez lidské verifikace; orientační.

## 2b. Co gap check znamená pro census

Census „5 endorsed F1 ze 43" byl spočítán nad korpusem, kterému u 27 projektů chybějí právě rozhodovací dokumenty (zákony, regulace, rozhodnutí o statusu, FAQ s výroky). Po doplnění korpusu se počet endorsed stanovisek pravděpodobně zvýší (Bahamy regulace 2021, Macao zákon 2023, Rusko 340-FZ, SAE dekrety, Izrael FAQ, Norsko FAQ, Peru FAQ…). Census byl screening, ne výsledek; **nový census po doplnění korpusu je podmínkou pro jakékoliv rozhodnutí o H2**, a doplnění korpusu je podmínkou pro freeze. Odhad práce: rozhodnutí autorů nad 178 prioritními řádky (3 až 4 h ve dvou), stažení + hash + texty (1 den strojově, PDF za bot-ochranou ručně), nový census (1 h strojově).

## 3. Rozhodnutí na pátek (v pořadí důležitosti)

0. **Pořadí prací:** nejdřív doplnit korpus podle D1 (rozhodnutí nad prioritními řádky), pak nový census, teprve pak tvar článku a slepá sada. Freeze instrumentu až po tom (doporučení auditora i moje).
1. **Tvar článku.** Varianty: (a) čistě měřicí a datový článek: auditovaný cross-project účet „kdo je dokumentován jako schopný vázat platbu na osobu, s jakým statusem, s jakou nejistotou" + tabulka závazků, které mizí pod přísnými pravidly (konzultant to doporučil jako hlavní aplikaci); (b) H2 jen na status-attached (permisivním) pohledu s jasným štítkem „stanoviska, ne závazky"; (c) obojí, H2 výslovně exploratorní, bez registrovaného rozhodovacího pravidla. Doporučení: **(a) jako jádro, (c) jen pokud census po lidské kontrole dá ≥ 20 určitelných v permisivním pohledu.**
2. **Referenční slepá sada.** Pokud platí (a), slepá sada validuje instrument, ne hypotézu: 12 plných profilů (pravděpodobnostní výběr v anglicky dostupné doméně) + F1 (a F7) source-first pro všech 43 před expozicí modelu. 16 jen při kapacitě ≥ X h/týden (doplnit).
3. **δ (SESOI).** Elicitace jen pokud zůstává klasifikovaná hypotéza; formulář připraven (`DELTA_ELICITATION_FORM.md`). Jinak registrovat odhad s intervaly.
4. **F9 a F10:** ponechat s restrikcemi konzultanta, nebo vypustit. Census měřil jen F1; o F9/F10 nic neříká. Doporučení: vypustit z primárního instrumentu, ponechat jako volitelné buňky ve schématu.
5. **Titul:** držet (rozhodnuto 30. 10.), znovu otevřít při psaní.
6. **Kapacita:** hodin/týden každého autora do 31. 12.; z toho plyne 12 vs 16 a počet vývojových případů (7 navrženo: NO, UK, eurozóna, Kanada, Chile, Maďarsko, 1 LIVE).
7. **Jazyk:** 12 ne-anglických core dokumentů; štítky JP (`zh` je ve skutečnosti `ja`, japonský originál anglického progress reportu) a RU (`ru`, ne `ru/uk`) opravit; routy A/B/C/D podle ledgeru (doplní se ve čtvrtek po rešerši oficiálních EN verzí).

## 4. Co se stane po pátku (pokud padnou rozhodnutí)

Týden 2: contract v2 přijat, vývojové případy 3 až 7 s měřením času. Týden 3: freeze, tag, Zenodo DOI, OSF registrace s exposure disclosure. Týdny 4 až 6: slepé kódování + source-first F1, produkce dvěma vendory, audit. Týdny 7 až 8: analýza, text pro Data & Policy.

## 5. Otevřené technické body (nevyžadují rozhodnutí autorů)

Druhý vendor klíč (až před produkcí); push do GitHubu (lokální commity 3d5151a, 83e6ad6, 27d186f); 7 UNRESEARCHED statusů; rotace přihlašovacích údajů sdílených v chatu.
