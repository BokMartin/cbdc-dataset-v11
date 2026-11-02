# Kde jsme — krátce česky (2. 11. 2026)

**Od 28. 10. (externí konzultace):** všech 6 pravidel a 28 dispozic zapracováno do ADR-001 (`DECISIONS/`), zaveden exposure ledger, zmrazen projektový rámec 48/46/43, pipeline opravena (úplný citační check, stavy selhání, přísná validace, archiv requestů, 16 testů, CI), draft contractu v2 + JSON schéma, parametrizovaný builder review sešitů a slepý referenční sešit, δ elicitační formulář.

**Census (2. 11., model-only, zapečetěno):** ze 43 národních retail kandidátů má schválené (endorsed) stanovisko k F1 jen 5 projektů (3 „ne", 2 „ano"), 3 běží bez popsaného uspořádání, 16 má jen návrh, 9 jen test, 10 nic. Klasifikovaná hypotéza na commitment matici tedy není proveditelná; rozhodnutí o tvaru článku 6. 11. (`docs/CONSULTATION_BRIEF_2026-11-06_cs.md`).

**Platné srovnání módů (Norsko):** 4/7/6 (shoda/hodnota/rozdíl) ze 17 buněk, citace 17/17; rozdíly hlavně ve statusu a popisných buňkách.


## Stav k 18. 10. 2026 (historický)

**Co je hotové:** korpus v2.2 (391 oficiálních dokumentů, 85 jurisdikcí, hash + zdroj u každého) a zmrazený analytický core (109 dokumentů / 56 jurisdikcí, + 18 UK dokumentů jako datovaný přírůstek); oficiální status projektů pro všech 85 jurisdikcí se zdroji; measurement contract v1.1 (definice F1–F12, pravidla odvozování, typologie A0–C1, outcomes); reprodukovatelná API extrakce s úplným logem a strojovou kontrolou citací; vývojové profily Norsko a UK s ověřenými citacemi.

**Co se řeší teď:** ověření norského a britského profilu po buňkách (model vs. definice), dvě otevřená pravidla (status „zamítnuto, zkoumá se dál"; F12 tested vs. undecided).

**Co následuje v pevném pořadí:** kontrastní vývojové případy → zmrazení contractu + SESOI s vedoucím + registrace na OSF → slepý testovací vzorek kódovaný lidmi → produkční extrakce dvěma vendory + audit → analýza a publikace dat.

**Web:** mapa s posuvníkem let, typologie a F-otázky jsou hotový „obal"; čísla kromě Norska a UK jsou **mock** a budou nahrazena výstupem pipeline beze změny webu.

Podrobně anglicky v `METHOD.md` a na stránce *Method & progress*.
