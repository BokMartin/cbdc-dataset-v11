#!/usr/bin/env python3
"""Human coding samples for the privacy-talk instrument (version of 13 Nov 2026, after the independent audit; ADR-005).

Two designs, both drawn before any model has classified a unit, from the candidate units of select_candidates.py:
  dev   development sample, 120 units: D 90 (route A 62, B 9, D 19) · N 15 (11, 1, 3) · R 15 (11, 1, 3). Both authors code ALL facets;
        the result decides which facets are kept, merged or dropped. The codebook and the model prompts may be revised on it.
  main  reference sample, 400 units: D 260 (190, 20, 50) · N 80 (58, 6, 16) · R 60 (44, 4, 12). Drawn only after the document set and
        the codebook are frozen; never contains a dev unit; not used to tune prompts, so it stays a clean reference for the model.
Within a stratum x route cell the route-A units are split by project tier 45 % T1, 35 % T2, 20 % T3; projects take turns (round robin
in hash order), with a cap per document and stratum (dev 2, main 4), units in hash order. Hash = SHA-256(seed | unit_id).
Context shown to the coder is the unit's paragraph from scripts/units/context.py, the same string the model will receive.
Outputs outside the repository (unit text is issuers' copyright): one workbook per coder (READ_ME, CODEBOOK, CODE), rows in a
different hash order for each coder. Repository: data/units/AGREEMENT_SAMPLE_<design>_<date>.csv with unit ids, strata, the SHA-256
of the unit text and of the document's unit file (a re-extraction that changes the text is detected), and the row order per coder.

usage: draw_agreement_sample.py --design dev|main --units <units dir> --issuers data/manifest/ISSUERS_<date>.csv --out <dir> --date 2026-11-13
"""
import argparse, csv, glob, hashlib, json, os, re, sys, collections
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.worksheet.datavalidation import DataValidation
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE); import context
DESIGN = {"dev": {"seed": "talk-v13-dev-2026-11-13", "cap": 2, "quota": {("D", "A"): 62, ("D", "B"): 9, ("D", "D"): 19, ("N", "A"): 11, ("N", "B"): 1, ("N", "D"): 3, ("R", "A"): 11, ("R", "B"): 1, ("R", "D"): 3}},
          "main": {"seed": "talk-v13-main-2026-11-13", "cap": 4, "quota": {("D", "A"): 190, ("D", "B"): 20, ("D", "D"): 50, ("N", "A"): 58, ("N", "B"): 6, ("N", "D"): 16, ("R", "A"): 44, ("R", "B"): 4, ("R", "D"): 12}}}
TIER_SHARE = (("T1", .45), ("T2", .35), ("T3", .20)); SEED = None
ROUTE = {"A": "English original", "B": "issuer's English edition", "D": "MACHINE TRANSLATION"}
WRAP = Alignment(wrap_text=True, vertical="top"); BOLD = Font(bold=True)
COLS = ["n", "unit_id", "project", "issuer (document)", "kind", "year", "text is", "page", "paragraph (unit marked »…«)", "UNIT TO CODE",
        "relevant", "voice", "aspect", "aspect2", "stance", "basis", "decision", "implementation", "modality", "anonymity_rejected", "low_id_tier", "two_statements", "note"]


def clean(t):
    t = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", " ", t)  # control characters are not allowed in a worksheet; the hash in the manifest is of the unit text as unitised
    return ("'" + t) if t and t[0] in "=+-@" else t


def hx(*p): return hashlib.sha256("|".join(p).encode()).hexdigest()


def round_robin(pool, n, taken, cap):
    """pool: units (dicts); projects take turns in hash order, units in hash order, at most `cap` per document."""
    byp = collections.defaultdict(list)
    for u in sorted(pool, key=lambda u: hx(SEED, u["unit_id"])):
        if u["unit_id"] not in taken: byp[u["project"]].append(u)
    order = sorted(byp, key=lambda p: hx(SEED, "project", p)); out = []; perdoc = collections.Counter()
    while len(out) < n and any(byp[p] for p in order):
        for p in order:
            while byp[p]:
                u = byp[p].pop(0)
                if perdoc[u["doc_key"]] < cap: perdoc[u["doc_key"]] += 1; out.append(u); break
            if len(out) >= n: break
    return out


def main():
    global SEED
    ap = argparse.ArgumentParser(); ap.add_argument("--design", required=True, choices=list(DESIGN)); ap.add_argument("--units", required=True); ap.add_argument("--issuers", required=True); ap.add_argument("--out", required=True); ap.add_argument("--date", required=True)
    ap.add_argument("--schema", default=os.path.join(ROOT, "schema/talk_units_v13_DRAFT.json")); ap.add_argument("--codebook", default=os.path.join(ROOT, "docs/TALK_CODEBOOK_cs.tsv"))
    a = ap.parse_args(); D = DESIGN[a.design]; SEED = D["seed"]
    mf = sorted(glob.glob(os.path.join(ROOT, "data/units/UNITS_MANIFEST_*.csv")))[-1]; man = {r["doc_key"]: r for r in csv.DictReader(open(mf, encoding="utf-8"))}
    iss = {r["id"]: r for r in csv.DictReader(open(a.issuers, encoding="utf-8"))}
    taken = set()  # the main sample never contains a unit of a development sample
    if a.design == "main":
        for f in glob.glob(os.path.join(ROOT, "data/units/AGREEMENT_SAMPLE_dev_*.csv")): taken |= {r["unit_id"] for r in csv.DictReader(open(f, encoding="utf-8"))}
    pool = []; text = {}
    for key, m in man.items():
        U = list(csv.DictReader(open(os.path.join(a.units, key + ".units.csv"), encoding="utf-8")))
        st = {r["unit_id"]: r["stratum"] for r in csv.DictReader(open(os.path.join(a.units, key + ".candidates.csv"), encoding="utf-8"))}
        for i, u in enumerate(U):
            if u["unit_id"] in st:
                text[u["unit_id"]] = (context.render(U, i), u["text"], u["page"])
                pool.append({"unit_id": u["unit_id"], "doc_key": key, "project": m["project"], "tier": m["tier"], "route": m["route"], "kind": m["kind"], "year": m["year"], "id": m["id"], "stratum": st[u["unit_id"]], "units_sha256": m["units_sha256"]})
    sample = []
    for (s, rt), q in D["quota"].items():
        cell = [u for u in pool if u["stratum"] == s and u["route"] == rt]
        if rt == "A" and q >= 10:
            parts = [(t, round(q * sh)) for t, sh in TIER_SHARE]; parts[0] = (parts[0][0], q - sum(n for _, n in parts[1:]))
        else: parts = [(None, q)]
        for t, n in parts:
            got = round_robin([u for u in cell if t is None or u["tier"] == t], n, taken, D["cap"]); sample += got; taken |= {u["unit_id"] for u in got}
            if len(got) < n: raise SystemExit(f"quota not filled: {s} {rt} {t}: {len(got)} of {n}")
    S = json.load(open(a.schema))["L2_facets"]; os.makedirs(a.out, exist_ok=True)
    cb = [l.rstrip("\n").split("\t") for l in open(a.codebook, encoding="utf-8") if l.strip()]
    lists = {"relevant": ["R", "N", "U"], "voice": S["voice"], "aspect": S["aspect"], "aspect2": S["aspect"], "stance": S["stance"], "basis": S["basis"], "decision": S["decision"], "implementation": S["implementation"], "modality": S["modality"],
             "anonymity_rejected": ["x"], "low_id_tier": ["x"], "two_statements": ["x"]}
    purpose = ("ZKUŠEBNÍ vzorek: kódujete všechny údaje, aby se ukázalo, které fungují. Podle výsledku se pravidla upraví a slabé údaje vypustí." if a.design == "dev"
               else "OSTRÝ vzorek: pravidla jsou zamčená; výsledek je referenční měření shody.")
    for coder in ("MB", "DS"):
        wb = Workbook(); ws = wb.active; ws.title = "READ_ME"
        for t in [f"Privacy-talk {a.design} sample, coder {coder} (drawn {a.date}, seed {SEED}): {len(sample)} units on sheet CODE. {purpose}",
                  "POSTUP: 1) Přečtěte si list CODEBOOK. 2) List CODE kóduje každý SÁM, bez porady a bez pomoci jazykového modelu; o jednotlivých větách se nebavte, dokud oba neskončíte. 3) Soubor uložte pod stejným názvem a pošlete.",
                  "CO SE KÓDUJE: jen věta ve žlutém sloupci UNIT TO CODE. Sloupec 'paragraph' je odstavec, ve kterém věta stojí (věta je v něm označena »takto«); slouží k pochopení zájmen, odkazů a toho, kdo mluví. Je prázdný, pokud věta stojí sama (nadpis, buňka tabulky). Stejný odstavec dostane i model.",
                  "Sloupec 'relevant': R = věta sama něco říká o soukromí, identifikovatelnosti nebo přístupu k datům uživatelů retailové CBDC; N = neříká; U = nečitelná nebo useknutá. Pokud N nebo U, ostatní sloupce nechte prázdné.",
                  "Pokud R: vyplňte voice, aspect, stance, basis, decision, implementation, modality (rozbalovací seznamy). aspect2 a tři příznaky (x) jen když je potřeba. Do 'note' pište pochybnosti: jsou cenné pro úpravu pravidel.",
                  "Sloupec 'text is' říká, zda čtete anglický originál, anglické vydání vydavatele, nebo STROJOVÝ PŘEKLAD (v něm hranaté závorky obsahují původní termín). Některé věty jsou úlomky tabulek nebo nadpisů: to je součást měření, kódujte, co je napsáno.",
                  "Pořadí řádků je pro každého kodéra jiné (náhodné). Neřaďte list podle projektu: kódujte v daném pořadí. Odhad času: " + ("asi 2 hodiny." if a.design == "dev" else "5 až 6 hodin."),
                  "Shodu spočítá scripts/units/score_agreement.py (Krippendorffovo alfa a AC1 pro každý sloupec, tabulky záměn)."]:
            ws.append([t])
        ws.column_dimensions["A"].width = 160
        for r in ws.iter_rows():
            for c in r: c.alignment = WRAP
        c_ = wb.create_sheet("CODEBOOK")
        for l in cb: c_.append(l)
        for i, wd in enumerate([18, 26, 120], 1): c_.column_dimensions[chr(64 + i)].width = wd
        for r in c_.iter_rows():
            for c in r: c.alignment = WRAP
            if r[0].value and not r[1].value: r[0].font = BOLD
        d = wb.create_sheet("CODE"); d.append(COLS); order = sorted(sample, key=lambda u: hx(SEED, coder, u["unit_id"]))
        for n, u in enumerate(order, 1):
            ctx, t, pg = text[u["unit_id"]]; i_ = iss.get(u["id"], {})
            d.append([n, u["unit_id"], u["project"], (i_.get("issuer") or "") + (" + " + i_["joint_with"] if i_.get("joint_with") else ""), u["kind"], u["year"], ROUTE[u["route"]], pg, clean(ctx), clean(t)] + [""] * (len(COLS) - 10))
            d.cell(n + 1, 10).fill = PatternFill("solid", fgColor="FFF2CC"); u["order_" + coder] = n
        for c, wd in enumerate([5, 14, 7, 22, 12, 6, 14, 5, 60, 60, 9, 11, 18, 18, 11, 15, 14, 16, 12, 8, 8, 8, 30], 1): d.column_dimensions[d.cell(1, c).column_letter].width = wd
        for c in range(1, len(COLS) + 1): d.cell(1, c).font = BOLD; d.cell(1, c).fill = PatternFill("solid", fgColor="DDDDDD")
        for r in d.iter_rows():
            for c in r: c.alignment = WRAP
        for name, vals in lists.items():
            dv = DataValidation(type="list", formula1='"' + ",".join(vals) + '"', allow_blank=True); d.add_data_validation(dv); L = d.cell(1, COLS.index(name) + 1).column_letter; dv.add(f"{L}2:{L}{len(sample) + 1}")
        d.freeze_panes = "K2"
        wb.save(os.path.join(a.out, f"TALK_{a.design.upper()}_SAMPLE_{coder}_{a.date}.xlsx"))
    rows = [{"unit_id": u["unit_id"], "set": a.design, "stratum": u["stratum"], "project": u["project"], "tier": u["tier"], "route": u["route"], "kind": u["kind"],
             "unit_text_sha256": hashlib.sha256(text[u["unit_id"]][1].encode("utf-8")).hexdigest(), "context_sha256": hashlib.sha256(text[u["unit_id"]][0].encode("utf-8")).hexdigest(), "units_file_sha256": u["units_sha256"],
             "order_MB": u["order_MB"], "order_DS": u["order_DS"]} for u in sample]
    with open(os.path.join(ROOT, "data/units", f"AGREEMENT_SAMPLE_{a.design}_{a.date}.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    c = collections.Counter
    print(a.design, len(sample), dict(c(u["stratum"] for u in sample)), dict(c(u["route"] for u in sample)), dict(c(u["tier"] for u in sample)),
          "projects", len({u["project"] for u in sample}), "documents", len({u["doc_key"] for u in sample}), "with paragraph context", sum(bool(text[u["unit_id"]][0]) for u in sample), "manifest", os.path.basename(mf))


if __name__ == "__main__": main()
