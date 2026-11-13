#!/usr/bin/env python3
"""Human agreement sample for the privacy-talk instrument: 400 units for two coders (MB, DS) plus 30 training units.

Drawn BEFORE any model has classified a unit, from the candidate units of select_candidates.py (strata D dictionary hit, N neighbour,
R random control). Nothing here uses model output; the two coders code the same units independently, and the model is run on them later.
Design (fixed here, seed in the manifest):
  training  30 units from the two exposed projects (NO, UK): 20 D, 5 N, 5 R. Coded together, discussed, used to fix the codebook. Not scored.
  main     400 units, NO and UK included but never a training unit:
           stratum x text route quotas  D: A 190, B 20, D 50 · N: A 58, B 6, D 16 · R: A 44, B 4, D 12
           (D is over-sampled because facets can only be compared on relevant units; R checks that coders agree on "not relevant";
           route B and D are over-sampled so that agreement can be reported separately for issuer-English and machine-translated text)
           route-A cells are split by project tier 45 % T1, 35 % T2, 20 % T3; within a group projects take turns (round robin in
           hash order), at most 4 units per document and stratum, units in hash order: no project or long document can dominate.
  hash     SHA-256(seed | unit_id); seed "talk-v13-agreement-2026-11-13". Each coder gets the rows in a different hash order.
Outputs outside the repository (unit text is issuers' copyright): one workbook per coder with sheets READ_ME, CODEBOOK, TRAINING, CODE.
Repository: data/units/AGREEMENT_SAMPLE_<date>.csv (unit ids, strata, SHA-256 of the unit text, row order per coder; no text).

usage: draw_agreement_sample.py --units <units dir> --issuers data/manifest/ISSUERS_2026-11-13.csv --out <dir> --date 2026-11-13
"""
import argparse, csv, glob, hashlib, json, os, re, collections
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.worksheet.datavalidation import DataValidation
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
SEED = "talk-v13-agreement-2026-11-13"
QUOTA = {("D", "A"): 190, ("D", "B"): 20, ("D", "D"): 50, ("N", "A"): 58, ("N", "B"): 6, ("N", "D"): 16, ("R", "A"): 44, ("R", "B"): 4, ("R", "D"): 12}
TRAIN = {"D": 20, "N": 5, "R": 5}; TIER_SHARE = (("T1", .45), ("T2", .35), ("T3", .20)); DOC_CAP = 4
WRAP = Alignment(wrap_text=True, vertical="top"); BOLD = Font(bold=True)


def clean(t):
    t = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", " ", t)  # control characters are not allowed in a worksheet; the hash in the manifest is of the unit text as unitised
    return ("'" + t) if t[:1] in "=+-@" else t


def hx(*p): return hashlib.sha256("|".join(p).encode()).hexdigest()


def round_robin(pool, n, taken, cap=DOC_CAP):
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
    ap = argparse.ArgumentParser(); ap.add_argument("--units", required=True); ap.add_argument("--issuers", required=True); ap.add_argument("--out", required=True); ap.add_argument("--date", required=True)
    ap.add_argument("--schema", default=os.path.join(ROOT, "schema/talk_units_v13_DRAFT.json")); ap.add_argument("--codebook", default=os.path.join(ROOT, "docs/TALK_CODEBOOK_cs.tsv"))
    a = ap.parse_args()
    man = {r["doc_key"]: r for r in csv.DictReader(open(sorted(glob.glob(os.path.join(ROOT, "data/units/UNITS_MANIFEST_*.csv")))[-1], encoding="utf-8"))}
    iss = {r["id"]: r for r in csv.DictReader(open(a.issuers, encoding="utf-8"))}
    pool = []; text = {}
    for key, m in man.items():
        U = list(csv.DictReader(open(os.path.join(a.units, key + ".units.csv"), encoding="utf-8")))
        st = {r["unit_id"]: r["stratum"] for r in csv.DictReader(open(os.path.join(a.units, key + ".candidates.csv"), encoding="utf-8"))}
        for i, u in enumerate(U):
            if u["unit_id"] in st:
                text[u["unit_id"]] = (U[i - 1]["text"] if i else "", u["text"], U[i + 1]["text"] if i + 1 < len(U) else "", u["page"])
                pool.append({"unit_id": u["unit_id"], "doc_key": key, "project": m["project"], "tier": m["tier"], "route": m["route"], "kind": m["kind"], "year": m["year"], "id": m["id"], "stratum": st[u["unit_id"]]})
    taken = set(); train = []
    for s, n in TRAIN.items():
        got = round_robin([u for u in pool if u["stratum"] == s and u["project"] in ("NO", "UK")], n, taken, cap=2); train += got; taken |= {u["unit_id"] for u in got}
    main_ = []
    for (s, rt), q in QUOTA.items():
        cell = [u for u in pool if u["stratum"] == s and u["route"] == rt]
        if rt == "A":
            parts = [(t, round(q * sh)) for t, sh in TIER_SHARE]; parts[0] = (parts[0][0], q - sum(n for _, n in parts[1:]))
            for t, n in parts:
                got = round_robin([u for u in cell if u["tier"] == t], n, taken); main_ += got; taken |= {u["unit_id"] for u in got}
        else:
            got = round_robin(cell, q, taken); main_ += got; taken |= {u["unit_id"] for u in got}
    for u in train: u["set"] = "training"
    for u in main_: u["set"] = "main"
    S = json.load(open(a.schema))["L2_facets"]; os.makedirs(a.out, exist_ok=True)
    cb = [l.rstrip("\n").split("\t") for l in open(a.codebook, encoding="utf-8") if l.strip()]
    cols = ["n", "unit_id", "project", "issuer (document)", "kind", "year", "page", "context before", "UNIT TO CODE", "context after",
            "relevant (R/N/U)", "voice", "aspect", "aspect2 (optional)", "direction", "basis", "status", "modality", "flags (optional)", "note"]
    lists = {11: ["R", "N", "U"], 12: S["voice"], 13: S["aspect"], 14: S["aspect"], 15: S["direction"], 16: S["basis"], 17: S["status"], 18: S["modality"], 19: S["flags"]}
    rows = []
    for coder in ("MB", "DS"):
        wb = Workbook(); ws = wb.active; ws.title = "READ_ME"
        for t in [f"Privacy-talk agreement sample, coder {coder} (drawn {a.date}, seed {SEED}). 30 training units (sheet TRAINING) and {len(main_)} units to code (sheet CODE).",
                  "POSTUP: 1) Oba si přečtěte list CODEBOOK. 2) List TRAINING (30 vět, Norsko a UK) nakódujte každý sám, pak je společně projděte a vyjasněte si pravidla; případné změny pravidel zapište, než začnete s listem CODE. 3) List CODE kóduje každý SÁM, bez porady a bez pomoci jazykového modelu; o jednotlivých větách se nebavte, dokud oba neskončíte.",
                  "CO SE KÓDUJE: jen věta ve sloupci UNIT TO CODE. Sloupce 'context before / after' jsou sousední věty a slouží jen k pochopení zájmen a odkazů.",
                  "Sloupec 'relevant': R = věta sama něco říká o soukromí, identifikovatelnosti nebo přístupu k datům uživatelů retailové CBDC; N = neříká; U = nečitelná nebo useknutá. Pokud N nebo U, ostatní sloupce nechte prázdné.",
                  "Pokud R: vyplňte voice, aspect, direction, basis, status, modality (rozbalovací seznamy). aspect2 a flags jen když je potřeba. Do 'note' pište pochybnosti: jsou cenné pro úpravu pravidel.",
                  "Text některých vět je strojový překlad (hranaté závorky obsahují původní termín) a některé věty jsou úlomky tabulek nebo nadpisů: to je součást měření, kódujte, co je napsáno.",
                  "Pořadí řádků je pro každého kodéra jiné (náhodné), aby se neprojevila únava na stejných větách. Neřaďte list CODE podle projektu: kódujte v daném pořadí. Odhad času: 5 až 6 hodin.",
                  "Po dokončení soubor uložte pod stejným názvem a pošlete; shodu spočítá scripts/units/score_agreement.py (Krippendorffovo alfa pro každý sloupec)."]:
            ws.append([t])
        ws.column_dimensions["A"].width = 160
        for r in ws.iter_rows():
            for c in r: c.alignment = WRAP
        c_ = wb.create_sheet("CODEBOOK")
        for l in cb: c_.append(l)
        for i, wd in enumerate([14, 22, 110], 1): c_.column_dimensions[chr(64 + i)].width = wd
        for r in c_.iter_rows():
            for c in r: c.alignment = WRAP
            if r[0].value and not r[1].value: r[0].font = BOLD
        for name, data in (("TRAINING", train), ("CODE", main_)):
            d = wb.create_sheet(name); d.append(cols); order = sorted(data, key=lambda u: hx(SEED, coder, u["unit_id"]))
            for n, u in enumerate(order, 1):
                b, t, af, pg = text[u["unit_id"]]; i_ = iss.get(u["id"], {})
                d.append([n, u["unit_id"], u["project"], (i_.get("issuer") or "") + (" + " + i_["joint_with"] if i_.get("joint_with") else ""), u["kind"], u["year"], pg, clean(b[:600]), clean(t), clean(af[:600])] + [""] * 10)
                d.cell(n + 1, 9).fill = PatternFill("solid", fgColor="FFF2CC")
                if name == "CODE": u["order_" + coder] = n
            for c, wd in enumerate([5, 14, 7, 22, 12, 6, 5, 38, 70, 38, 9, 11, 18, 18, 11, 15, 15, 12, 16, 30], 1): d.column_dimensions[d.cell(1, c).column_letter].width = wd
            for c in range(1, len(cols) + 1): d.cell(1, c).font = BOLD; d.cell(1, c).fill = PatternFill("solid", fgColor="DDDDDD")
            for r in d.iter_rows():
                for c in r: c.alignment = WRAP
            for c, vals in lists.items():
                dv = DataValidation(type="list", formula1='"' + ",".join(vals) + '"', allow_blank=True); d.add_data_validation(dv); L = d.cell(1, c).column_letter; dv.add(f"{L}2:{L}{len(data) + 1}")
            d.freeze_panes = "I2"
        wb.save(os.path.join(a.out, f"TALK_AGREEMENT_SAMPLE_{coder}_{a.date}.xlsx"))
    for u in train + main_:
        rows.append({"unit_id": u["unit_id"], "set": u["set"], "stratum": u["stratum"], "project": u["project"], "tier": u["tier"], "route": u["route"], "kind": u["kind"],
                     "unit_text_sha256": hashlib.sha256(text[u["unit_id"]][1].encode("utf-8")).hexdigest(), "order_MB": u.get("order_MB", ""), "order_DS": u.get("order_DS", "")})
    with open(os.path.join(ROOT, "data/units", f"AGREEMENT_SAMPLE_{a.date}.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    c = collections.Counter
    print("training", len(train), "main", len(main_), dict(c(u["stratum"] for u in main_)), dict(c(u["route"] for u in main_)), dict(c(u["tier"] for u in main_)),
          "projects", len({u["project"] for u in main_}), "documents", len({u["doc_key"] for u in main_}), "max per project", c(u["project"] for u in main_).most_common(3))


if __name__ == "__main__": main()
