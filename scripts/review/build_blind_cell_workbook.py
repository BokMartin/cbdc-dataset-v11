#!/usr/bin/env python3
"""Blank workbooks for the blind F-cell coding of the 14 blind core projects (ADR-012 D1, D2; ADR-016 §4).

Both authors (MB, DS) code the eight index cells F1, F2, F3, F4, F7, F8, F9, F10 of the 14 blind core projects (T1 and T2
of the tiers frozen on 17 Nov 2026, without NO and UK) from the sources, alone, before any model output of these projects
is opened. One workbook per coder, identical except for the coder name. The coding sheet carries exactly the fields of
the coder template of 22 Nov 2026 (`data/index/CODER_TEMPLATE_2026-11-22.csv`, read by `scripts/index_reliability.py`).

Inputs are only the corpus and the unit files: the unit manifest of the v13e unit set, the tiers, document titles and
translation manifests of this repository, and the unit texts (`--units`, used for the page finder and never copied into
the workbook). The script refuses any input path that looks like a model run (`--units` under a `runs` folder or a
PROD_* archive), because the production outputs hold labels of the blind projects (ADR-016 §4).

Page finder (contract v12 §10: "Keyword finder in the workbook lists page references only"): for every evidence
document, the pages whose units match one of six fixed term groups (FINDER below), within the pages sent to extraction
for general publications (CBDC pages ±1, ADR-013 P3) and outside the omitted pages. Page numbers only, no text. The
finder is written to the repository before anyone codes (`data/index/BLIND_CELL_FINDER_<date>.csv`), with the SHA-256 of
its definition, so that it is fixed like a sample (AGENTS.md, "Evidence and measurement").

Outputs:
  <out>/BLIND_CELLS_{MB,DS}_<date>.xlsx              the two workbooks (outside the repository)
  data/index/BLIND_CELL_FINDER_<date>.csv            doc_key, group, pages (page references only)
  data/index/BLIND_CELL_WORKBOOKS_<date>.csv         SHA-256 of each workbook, of the finder definition and of the inputs

usage: build_blind_cell_workbook.py --units <dir with *.units.csv> --out <dir> --date 2026-11-24
"""
import argparse
import csv
import glob
import hashlib
import json
import os
import re
import sys

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.worksheet.datavalidation import DataValidation

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.dirname(HERE))
from index_reliability import ENUMS, FIELDS  # noqa: E402

UNITS_MANIFEST = "data/units/UNITS_MANIFEST_2026-11-23b.csv"
TIERS = "data/manifest/TIERS_2026-11-17.csv"
TIERS_PATHS = "data/manifest/TIERS_2026-11-21.csv"
TITLES = "data/manifest/DOC_TITLES_2026-11-21.csv"
CORPUS = "data/manifest/CORPUS_DOCUMENTS_2026-11-21.csv"
SPANS = "data/manifest/EXTRACTION_HEADER_EXTRA_2026-11-23b.csv"
PROJECTS = "data/frame/projects.csv"
TRANSLATIONS = "data/translation/TRANSLATION_MANIFEST_*.csv"

DEVELOPMENT = ("NO", "UK")  # exposed development projects, not blind (ADR-012 D1)
BLIND = ("AU", "BS", "CA", "EU", "HK", "IL", "IN", "JM", "JP", "KZ", "NZ", "RU", "SE", "TW")
CELLS = ("F1", "F2", "F3", "F4", "F7", "F8", "F9", "F10")
CODERS = ("MB", "DS")

# Six fixed term groups of the page finder. The finder only points; a page outside it can hold the answer.
FINDER = {
    "PRIV": r"privacy\w*|anonym\w*|pseudonym\w*|unlinkab\w*|personal (data|information)|(user|customer|transaction|payment|payer|payee|holder)s?[’']? (data|information)|data (protection|access|sharing|collection|retention)|(cannot|can not|not be able to|will not|does not|do not|unable to) (see|view|access|link)",
    "IDENT": r"anonym\w*|kyc|know[- ]your[- ]customer|customer due diligence|identity verification|verif\w* (of )?(the |their |user |customer )?identit\w*|identity (check|requirement)s?|onboard\w*|tiered (wallets?|accounts?|kyc|access|approach|structure)|wallet tiers?|tier [0-9]|account opening|without (an )?(identity|identification|id)",
    "LAW": r"law enforcement|lawful (access|interception)|court orders?|judicial|tax authorit\w*|police|warrants?|subpoena\w*|re-?identif\w*|de-?anonymi\w*|money[- ]laundering|aml",
    "OFF": r"offline|off-line",
    "PROG": r"programmab\w*|smart contracts?|expir(y|e|es|ing|ation)|purpose[- ]bound|conditional payments?|restrict\w* (on |the )?(use|usage|spending)",
    "PET": r"zero[- ]knowledge|zkp|zk-snark\w*|blind signatures?|ring signatures?|homomorphic|multi-?party computation|secure elements?|privacy[- ]enhancing|pets?\b",
}
FINDER_RX = {k: re.compile(r"\b(" + v + r")\b", re.I) for k, v in FINDER.items()}
GROUP_CELLS = {"PRIV": "F1, F2, F9", "IDENT": "F7, F8", "LAW": "F3, F9", "OFF": "F4", "PROG": "F10", "PET": "volitelné"}
FINDER_SHA = hashlib.sha256(json.dumps(FINDER, sort_keys=True, ensure_ascii=False).encode()).hexdigest()

VALUES = {c: ("yes", "no") for c in CELLS}
VALUES["F3"] = ("via_psp", "via_cb", "via_both", "none_stated")
UNKNOWN_REASON = ("never_addressed", "provisional_only", "privacy_unspecified", "search_incomplete")
FLAGS = ("anonymity_rejected", "analytic_linkability", "balance_reporting", "translation_uncertain",
         "quote_in_figure_or_table", "operational_undocumented_decision")
PET_CODES = ("standard_encryption", "digital_signatures", "blind_signatures", "ring_signatures", "schnorr_signatures",
             "bbs_plus_signatures", "multi_party_computation", "pedersen_commitments", "homomorphic_encryption",
             "zero_knowledge_proof", "zk_snark", "zk_stark", "mixing_privacy_pools", "utxo_model", "secure_hardware",
             "digital_identity", "two_tier_model", "identity_payment_separation", "pseudonymised_settlement",
             "internal_firewall", "multi_factor_authentication", "other")

# Extra columns of the coding sheet beyond the coder template; index_reliability.read() ignores them.
EXTRA = ["unknown_reason", "flags"]
CODE_COLUMNS = ["project_id", "cell", "question", "value", "decision_status", "implementation_status", "evidence_state",
                "unknown_reason", "basis", "text_route", "derivation", "conflict", "document_id", "page_index", "quote",
                "flags", "note"]
assert set(FIELDS) <= set(CODE_COLUMNS) and set(EXTRA) <= set(CODE_COLUMNS)

QUESTION = {
    "F1": "Může centrální banka (nebo její agent) v běžném online režimu rutinně přiřadit platbu plátce identifikované osobě?",
    "F2": "Může PSP plátce v běžném online režimu rutinně přiřadit platbu osobě?",
    "F3": "Je doložena cesta, kterou orgán veřejné moci získá platební údaje přiřaditelné osobě, a přes koho?",
    "F4": "Je pro určený horizont schválen offline režim, ve kterém se údaje o jednotlivých převodech rutinně neposílají CB/PSP ani nepropojují s osobou (ani při synchronizaci)?",
    "F7": "Existuje režim, ve kterém uživatel může do stanoveného limitu držet a platit bez ověřené identity?",
    "F8": "Vyžaduje otevření běžné peněženky ověřenou identitu?",
    "F9": "Je doložen výjimečný postup, kterým lze online platbu dodatečně přiřadit osobě (kdo, z jakých údajů, za jaké podmínky)?",
    "F10": "Umožňuje návrh, aby emitent nebo stát omezil použití peněz (účel, expirace, blokace)?",
}

GREY = PatternFill("solid", fgColor="DDDDDD")
YELLOW = PatternFill("solid", fgColor="FFF2CC")
WRAP = Alignment(wrap_text=True, vertical="top")


def _guard(path):
    p = os.path.abspath(path).replace("\\", "/")
    if re.search(r"(^|/)runs(/|$)|PROD_|_RUNS", p):
        raise SystemExit(f"refused: {path} looks like a model run; the blind workbook is built from units and corpus only")


def _read(rel):
    with open(os.path.join(ROOT, rel), newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def _sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for b in iter(lambda: fh.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def documents():
    """Evidence documents of the 14 blind projects in a fixed order (project, year, id), with a short code per project,
    plus the INCLINED documents of these projects, listed but not for F-cells (ADR-012 D5: wholesale is context and PET)."""
    tiers = _read(TIERS)
    core = sorted({r["project"] for r in tiers if r["tier"] in ("T1", "T2")} - set(DEVELOPMENT))
    if tuple(core) != BLIND:
        raise SystemExit(f"blind core differs from the frozen tiers: {core}")
    paths = {r["id"]: r for r in _read(TIERS_PATHS)}
    titles = {r["id"]: r["title"] for r in _read(TITLES)}
    corpus = {r["id"]: r for r in _read(CORPUS)}
    spans = {r["doc_key"]: r for r in _read(SPANS)}
    trans = {}
    for f in sorted(glob.glob(os.path.join(ROOT, TRANSLATIONS))):
        with open(f, newline="", encoding="utf-8") as fh:
            for r in csv.DictReader(fh):
                if r.get("status") == "ok":
                    trans[r["id"]] = r["translation_file"]
    out = []
    for p in BLIND:
        rows = [r for r in _read(UNITS_MANIFEST) if r["project"] == p]
        rows.sort(key=lambda r: (r["stratum"] != "evidence", r["year"], r["id"]))
        n = 0
        for r in rows:
            ev = r["stratum"] == "evidence"
            n += ev
            sp = spans.get(r["doc_key"], {})
            title = titles.get(r["id"]) or corpus.get(r["id"], {}).get("title") or r["id"]
            out.append({
                "code": f"{p}-{n:02d}" if ev else f"{p}-W{rows.index(r) - n + 1}",
                "project": p, "doc_key": r["doc_key"], "id": r["id"], "for_cells": "ano" if ev else "ne (wholesale, jen PET a kontext)",
                "year": r["year"], "title": title, "issuer": r["issuer"], "kind": r["kind"], "route": r["route"],
                "pages": int(r["pages"]), "span": sp.get("span_pages", "") if sp.get("page_span") == "cbdc_span" else "",
                "omit": sp.get("omit_pages", ""),
                "pdf": paths.get(r["id"], {}).get("master_path", ""), "pdf_sha256": paths.get(r["id"], {}).get("sha256", ""),
                "translation": ("CBDC_TRANSLATION_v12/" + trans[r["id"]]) if r["route"] == "D" and r["id"] in trans else "",
            })
    return out


def finder(docs, units_dir):
    """Pages per document and group (page references only)."""
    rows = []
    for d in docs:
        f = os.path.join(units_dir, d["doc_key"] + ".units.csv")
        if not os.path.exists(f):
            raise SystemExit(f"unit file missing: {f}")
        pages = {}
        with open(f, newline="", encoding="utf-8") as fh:
            for u in csv.DictReader(fh):
                t = re.sub(r"\[[^\]\n]{1,120}\]", " ", u["text"])  # bracketed source terms and translator notes ignored
                pages.setdefault(int(u["page"]), []).append(t)
        allowed = set(map(int, d["span"].split())) if d["span"] else set(pages)
        allowed -= set(map(int, d["omit"].split())) if d["omit"] else set()
        for g, rx in FINDER_RX.items():
            hit = sorted(pg for pg, ts in pages.items() if pg in allowed and any(rx.search(t) for t in ts))
            rows.append({"doc_key": d["doc_key"], "code": d["code"], "group": g, "n_pages": len(hit), "pages": " ".join(map(str, hit))})
        d["finder_pages"] = len({int(x) for r in rows if r["doc_key"] == d["doc_key"] and r["group"] != "PET" for x in r["pages"].split()})
    return rows


NAVOD = [
    "Slepé kódování buněk F, kodér {coder} (sešit vytvořen {date}). Kódujete sami, bez druhého autora, bez výstupů modelů.",
    "PROČ: v 16 projektech jádra rozhodují o buňkách autoři ze zdrojů (ADR-012 D1, D2). U těchto 14 projektů (jádro bez NO a UK) se měří shoda dvou slepých kodérů; modely jsou až srovnání po zamčení obou sešitů (ADR-016 bod 4).",
    "CO SE KÓDUJE: list KODOVANI, 14 projektů × 8 buněk = 112 řádků. Šedé sloupce neměňte, žluté vyplňte. Pravidla k buňkám a polím jsou v listu PRAVIDLA.",
    "CO ČÍST: dokumenty projektu z listu DOKUMENTY (sloupec 'pro buňky' = ano). U obecných publikací (výroční zpráva apod.) jen strany ve sloupci 'strany k čtení', stejně jako dostal model. Dokumenty označené W (wholesale) pro buňky nepoužívejte.",
    "VYHLEDAVAČ: list VYHLEDAVAC ukazuje u každého dokumentu strany, kde se vyskytují pevně dané výrazy ke skupině buněk. Je to jen rejstřík stran, ne výběr textu ani návrh hodnoty. Odpověď může být i jinde; číst víc je vždy dovoleno.",
    "{scope}",
    "KDYŽ SE DOKUMENTY LIŠÍ: platí tvrzení s nejvyšším statusem (endorsed/operational nad considered), při stejném statusu novější dokument. Do buňky zapište vítězné tvrzení, ostatní stručně do 'note'. Dvě rovnocenná tvrzení, která si odporují: conflict = true a evidence_state = conflict.",
    "PRÁZDNÁ BUŇKA NENÍ ODPOVĚĎ: každý řádek má buď hodnotu (value) s citátem, nebo evidence_state unknown / n.a. s důvodem (unknown_reason). Ticho dokumentů je unknown (never_addressed), nikdy no.",
    "CITÁT: doslovně z PDF (u cesty D z anglického strojového překladu, cesta je v listu DOKUMENTY), page_index = číslo strany PDF od 1. Do document_id stačí kód dokumentu (např. EU-03).",
    "PET (volitelné, čeká na rozhodnutí): list PET jen pokud se to rozhodne; jinak nechte prázdný.",
    "ČTENÍ: v listu CTENI u každého dokumentu zapište, co jste četli (jen strany z vyhledávače / celý dokument / nečetl) a přibližně minuty. Slouží pro záznam expozice a pro článek.",
    "ZAMČENÍ: vyplněný sešit pošlete zpět beze změny názvu listů a sloupců. Skript ho zkontroluje, uloží jeho otisk SHA-256 do repa a teprve potom se smí otevřít výstupy modelů k těmto projektům. Po zamčení už se sešit nemění; neshody se řeší společným průchodem nad zdroji.",
    "NEPOROVNÁVEJTE se druhým autorem, nediskutujte hodnoty a neotevírejte výstupy modelů ani web projektu s výsledky, dokud nejsou zamčené oba sešity.",
]

PRAVIDLA = [
    ("ZÁSADA", "", "Kódujete, co dokumenty příslušného orgánu doložitelně říkají o návrhu CBDC pro běžného plátce v běžné online peněžence. Nic nedomýšlejte z obecné praxe, jiných projektů, literatury ani vlastní znalosti práva."),
    ("BUŇKY", "F1", QUESTION["F1"] + " Nezávislý provozovatel, kterého nelze přičíst CB, se do F1 nepočítá (poznámka). Slib 'nebudeme se dívat / nepoužijeme' (basis policy) sám F1 = no nezakládá; potřeba architektonický nebo kryptografický důvod. Analýza pseudonymních dat bez propojení s osobou = flag analytic_linkability, ne F1 = yes. Hlášení zůstatků CB = flag balance_reporting."),
    ("", "F2", QUESTION["F2"] + " KYC, zákaznický vztah nebo alias samy o sobě závěr nedokládají. Závěr z více pasáží (mapa identifikátor → osoba + rutinní přístup k záznamu) jen pokud mluví o stejném účastníkovi, režimu a verzi návrhu; pak derivation = inferred. Testovaný předpoklad nezakládá schválenou produkční hodnotu."),
    ("", "F3", QUESTION["F3"] + " Hodnoty via_psp, via_cb, via_both (obě cesty z různých tvrzení = via_both, ne konflikt), none_stated jen po dokončeném prohledání všech dokumentů projektu. Cesta se nastaví jen když je jasné, kdo data drží a kudy jdou; odkaz 'stejná pravidla jako u bankovních účtů' se cituje. Žádná rekonstrukce z vlastní znalosti práva. 'Likely limited to' není výčet."),
    ("", "F4", QUESTION["F4"] + " Odložené online vypořádání není soukromý offline režim. Jen testovaná schopnost = considered × tested. Možnost bez horizontu spuštění = unknown. Výslovné vyloučení offline pro daný horizont = no."),
    ("", "F7", QUESTION["F7"] + " Zúženo na anonymní držení a placení (ADR-012 D9). Zjednodušené KYC nebo telefonní číslo samo neříká, zda je třeba ověřená identita. F7 = no jen při výslovném požadavku, že VŠECHNY cesty a úrovně ověřují identitu; ticho = unknown (never_addressed). Odmítnutí plné anonymity 'jako hotovost' je jen flag anonymity_rejected, nikdy F7 = no. Ověření příjemce plátce nediskvalifikuje."),
    ("", "F8", QUESTION["F8"] + " Výjimečná úroveň (tier) nemění běžné zakládání peněženky; patří k F7."),
    ("", "F9", QUESTION["F9"] + " Musí jít o skutečný mechanismus propojení (kdo, vstupní data, propojení, spouštěč, výstup). Soudní příkaz je spouštěč. Registr peněženka → osoba bez platební části nestačí. Únik dat nebo obecné riziko nestačí."),
    ("", "F10", QUESTION["F10"] + " Nepatří sem: pravidla vydání a zpětné výměny, limity držby, KYC, soudní obstavení, dobrovolné podmínky uživatele nebo obchodníka. Výslovný obecný zákaz může doložit no; úzké odmítnutí platí jen pro svůj podtyp."),
    ("POLE", "value", "yes / no ve směru otázky (F3 viz výše). Prázdná hodnota = neurčeno; pak vyplňte evidence_state a unknown_reason."),
    ("", "decision_status", "considered = konzultace, návrh, pracovní předpoklad, možnost, doporučení, zpráva o experimentu. endorsed = příslušný orgán výslovně přijal nebo se zavázal (i podmíněně jen budoucím vydáním CBDC). rejected = výslovně odmítnuto. superseded = výslovně nahrazeno novějším. unclear = orgán nebo přičtení nelze doložit. Žánr dokumentu sám status nestanoví."),
    ("", "implementation_status", "untested_or_unreported / tested (pilot nebo test této funkce) / operational (uspořádání skutečně běží) / unclear. Zákon v účinnosti nebo spuštění projektu samy o sobě neznamenají, že konkrétní uspořádání běží."),
    ("", "evidence_state", "documented = máte všechny rozhodující údaje. partial = chybí rozhodující údaj (účastník, režim, horizont, přičtení…). unknown = dokumenty to neřeší nebo nestačí (s unknown_reason). conflict = dvě rovnocenná tvrzení si odporují. n.a. = buňka se nehodí (např. offline výslovně vyloučeno pro F4 nedává smysl dál)."),
    ("", "unknown_reason", "never_addressed = nikde se neřeší; provisional_only = jen předběžně; privacy_unspecified = režim popsán, soukromí ne; search_incomplete = nestihl jsem prohledat."),
    ("", "basis", "policy (pravidlo nebo slib chování) / architectural (kdo jaká data drží, oddělení, klíče) / cryptographic (konkrétní mechanismus výslovně spojený s ochranou). Povinné u F1, F2, F4, F9, pokud je hodnota."),
    ("", "text_route", "Nemusíte vyplňovat: doplní se podle dokumentu (A originál anglicky, B anglické vydání emitenta, D strojový překlad)."),
    ("", "derivation", "explicit = jedna pasáž říká hodnotu přímo. inferred = hodnota plyne z více pasáží; do note uveďte které."),
    ("", "conflict", "true jen pro nevyřešený rozpor rovnocenných tvrzení; jinak nechte prázdné."),
    ("", "document_id, page_index, quote", "Dokument (kód z DOKUMENTY), strana PDF od 1 a doslovný citát (bez vynechávek; delší podporu rozdělte do note). Povinné, pokud je hodnota."),
    ("", "flags", "Volitelné, oddělené čárkou: " + ", ".join(FLAGS) + "."),
    ("", "note", "Volné: další tvrzení, proč unknown, odkud inference, nejistota překladu."),
]


def _header(ws, cols, widths=None):
    for c, name in enumerate(cols, 1):
        x = ws.cell(1, c, name)
        x.font = Font(bold=True)
        x.fill = GREY
        x.alignment = WRAP
        if widths:
            ws.column_dimensions[x.column_letter].width = widths.get(name, 14)
    ws.freeze_panes = "A2"


def _list(ws, col, first, last, vals):
    dv = DataValidation(type="list", formula1='"' + ",".join(vals) + '"', allow_blank=True)
    ws.add_data_validation(dv)
    dv.add(f"{col}{first}:{col}{last}")


def workbook(path, coder, date, docs, finder_rows, scope):
    wb = Workbook()
    ws = wb.active
    ws.title = "NAVOD"
    ws.column_dimensions["A"].width = 150
    for i, line in enumerate(NAVOD, 1):
        x = ws.cell(i, 1, line.format(coder=coder, date=date, scope=scope))
        x.alignment = WRAP
    ws.cell(1, 1).font = Font(bold=True)

    pr = wb.create_sheet("PRAVIDLA")
    _header(pr, ["oddíl", "buňka / pole", "pravidlo"], {"oddíl": 10, "buňka / pole": 26, "pravidlo": 140})
    for i, row in enumerate(PRAVIDLA, 2):
        for c, v in enumerate(row, 1):
            pr.cell(i, c, v).alignment = WRAP

    dc = wb.create_sheet("DOKUMENTY")
    dcols = ["kód", "projekt", "pro buňky", "rok", "název", "vydavatel", "druh", "cesta textu", "stran", "strany k čtení",
             "vynechané strany", "stran ve vyhledávači", "PDF v Dropboxu (Dizertace all the PDFs)", "SHA-256 PDF",
             "anglický překlad (cesta D)", "document id"]
    _header(dc, dcols, {"název": 60, "PDF v Dropboxu (Dizertace all the PDFs)": 60, "anglický překlad (cesta D)": 45,
                        "strany k čtení": 30, "SHA-256 PDF": 20, "document id": 30, "vydavatel": 28})
    for i, d in enumerate(docs, 2):
        vals = [d["code"], d["project"], d["for_cells"], d["year"], d["title"], d["issuer"], d["kind"], d["route"], d["pages"],
                d["span"] or "celý dokument", d["omit"], d.get("finder_pages", ""), d["pdf"], d["pdf_sha256"], d["translation"], d["id"]]
        for c, v in enumerate(vals, 1):
            dc.cell(i, c, v).alignment = WRAP

    fd = wb.create_sheet("VYHLEDAVAC")
    groups = list(FINDER)
    _header(fd, ["kód", "projekt"] + [f"{g} ({GROUP_CELLS[g]})" for g in groups], {"kód": 9, "projekt": 8})
    by = {(r["code"], r["group"]): r["pages"] for r in finder_rows}
    for i, d in enumerate(docs, 2):
        fd.cell(i, 1, d["code"])
        fd.cell(i, 2, d["project"])
        for c, g in enumerate(groups, 3):
            fd.cell(i, c, by.get((d["code"], g), "")).alignment = WRAP
            fd.column_dimensions[fd.cell(1, c).column_letter].width = 40
    n = len(docs) + 3
    fd.cell(n, 1, "Výrazy skupin (pevné, SHA-256 " + FINDER_SHA[:12] + "…):").font = Font(bold=True)
    for j, g in enumerate(groups, 1):
        fd.cell(n + j, 1, g)
        fd.cell(n + j, 3, FINDER[g])

    cd = wb.create_sheet("KODOVANI")
    widths = {"question": 50, "quote": 60, "note": 40, "value": 12, "flags": 22}
    _header(cd, CODE_COLUMNS, widths)
    r = 2
    for p in BLIND:
        for c in CELLS:
            cd.cell(r, 1, p).fill = GREY
            cd.cell(r, 2, c).fill = GREY
            q = cd.cell(r, 3, QUESTION[c])
            q.fill = GREY
            q.alignment = WRAP
            for k in range(4, len(CODE_COLUMNS) + 1):
                cd.cell(r, k).fill = YELLOW
                cd.cell(r, k).alignment = WRAP
            dv = DataValidation(type="list", formula1='"' + ",".join(VALUES[c]) + '"', allow_blank=True)
            cd.add_data_validation(dv)
            dv.add(f"D{r}")
            r += 1
    last = r - 1
    col = {name: cd.cell(1, i + 1).column_letter for i, name in enumerate(CODE_COLUMNS)}
    for f in ("decision_status", "implementation_status", "evidence_state", "basis", "derivation"):
        _list(cd, col[f], 2, last, sorted(v for v in ENUMS[f] if v))
    _list(cd, col["unknown_reason"], 2, last, UNKNOWN_REASON)
    _list(cd, col["text_route"], 2, last, ("A", "B", "C", "D"))
    _list(cd, col["conflict"], 2, last, ("true", "false"))

    pt = wb.create_sheet("PET")
    pcols = ["project_id", "pet_code", "technique_text", "privacy_function", "retail_or_wholesale", "decision_status",
             "implementation_status", "design_label", "document_id", "page_index", "quote", "note"]
    _header(pt, pcols, {"quote": 60, "technique_text": 30, "note": 30})
    _list(pt, "A", 2, 201, BLIND)
    _list(pt, "B", 2, 201, PET_CODES)
    _list(pt, "E", 2, 201, ("retail", "wholesale", "both", "unknown"))
    _list(pt, "F", 2, 201, sorted(v for v in ENUMS["decision_status"] if v))
    _list(pt, "G", 2, 201, sorted(v for v in ENUMS["implementation_status"] if v))

    ct = wb.create_sheet("CTENI")
    _header(ct, ["kód", "projekt", "co jsem četl", "minut", "poznámka"], {"poznámka": 50, "co jsem četl": 26})
    for i, d in enumerate([d for d in docs if d["for_cells"] == "ano"], 2):
        ct.cell(i, 1, d["code"]).fill = GREY
        ct.cell(i, 2, d["project"]).fill = GREY
        for k in (3, 4, 5):
            ct.cell(i, k).fill = YELLOW
    _list(ct, "C", 2, len(docs) + 1, ("strany z vyhledavace", "vic nez vyhledavac", "cely dokument", "necetl"))

    wb.properties.creator = "build_blind_cell_workbook.py"
    wb.save(path)


SCOPE_DEFAULT = ("ROZSAH ČTENÍ (návrh, čeká na Martinovo potvrzení): u každé buňky projděte strany, které vyhledávač uvádí u její "
                 "skupiny; pokud tam odpověď není, stačí unknown se search_incomplete nebo never_addressed. Po zamčení se strany, "
                 "kde modely najdou citát mimo vyhledávač, projdou společně ze zdroje.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--units", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--date", required=True)
    ap.add_argument("--scope", default=SCOPE_DEFAULT)
    a = ap.parse_args()
    _guard(a.units)
    _guard(a.out)
    docs = documents()
    rows = finder(docs, a.units)
    idx = os.path.join(ROOT, "data", "index")
    with open(os.path.join(idx, f"BLIND_CELL_FINDER_{a.date}.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, ["doc_key", "code", "group", "n_pages", "pages"])
        w.writeheader()
        w.writerows(rows)
    os.makedirs(a.out, exist_ok=True)
    rec = []
    for coder in CODERS:
        path = os.path.join(a.out, f"BLIND_CELLS_{coder}_{a.date}.xlsx")
        workbook(path, coder, a.date, docs, rows, a.scope)
        rec.append({"coder": coder, "file": os.path.basename(path), "sha256": _sha(path)})
    inputs = [UNITS_MANIFEST, TIERS, TIERS_PATHS, TITLES, CORPUS, SPANS] + sorted(
        os.path.relpath(f, ROOT) for f in glob.glob(os.path.join(ROOT, TRANSLATIONS)))
    with open(os.path.join(idx, f"BLIND_CELL_WORKBOOKS_{a.date}.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, ["kind", "name", "sha256"])
        w.writeheader()
        for r in rec:
            w.writerow({"kind": "workbook_" + r["coder"], "name": r["file"], "sha256": r["sha256"]})
        w.writerow({"kind": "finder_definition", "name": "FINDER in scripts/review/build_blind_cell_workbook.py", "sha256": FINDER_SHA})
        for f in inputs:
            w.writerow({"kind": "input", "name": f, "sha256": _sha(os.path.join(ROOT, f))})
    ev = [d for d in docs if d["for_cells"] == "ano"]
    print(f"{len(BLIND)} projects, {len(ev)} evidence documents ({sum(d['pages'] for d in ev)} pages), "
          f"{sum(d['finder_pages'] for d in ev)} finder pages without PET; workbooks in {a.out}")


if __name__ == "__main__":
    main()
