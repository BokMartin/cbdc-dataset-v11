#!/usr/bin/env python3
"""Issuer and voice of every evidence document (KEEP / BORDERLINE, 43-frame), one table for the authors to confirm.

Why: the privacy-talk instrument asks WHO speaks. The registry rows (documents of the v11 corpus) carried the acquisition batch in the
issuer field, so 111 of the 250 unitised documents had no issuing institution on record (unitise.py, 12 Nov 2026).
Sources of each row, stated in `issuer_source`:
  proposed_2026-11-13  registry rows: issuer proposed by the model from the title page / first units (data/manifest/ISSUERS_PROPOSED_<date>.csv)
  prescreen_record     candidate rows: the issuer string recorded at the gap check, normalised by the rules below
Normalised fields: issuer_type = institution that publishes (central_bank / government / legislature / other); joint_with; voice_class:
  institutional          the institution speaks in its own name
  joint_with_government  central bank together with the ministry / treasury
  joint_with_external    with a research centre, vendor, BIS hub or pilot participants (parts of the text are not the bank's position)
  commissioned_external  written by a contractor for the institution
  staff_authored         signed staff or research paper (contract rule: staff research sets no cell)
  official_speech        speech, interview or signed article of a governor / board member
  meeting_record         minutes or presentations of stakeholder groups (participants' views inside)
  legal_text             act, bill, regulation, gazette
`reports_views` = yes when the genre reports what others said (consultation responses, minutes, survey reports): unit-level coding still
decides the voice of each sentence; this column only warns the reader.
Mechanical checks on the unitised text (no model): `name_on_first_pages` (the issuer's name key occurs on pages 1-6) and
`disclaimer_unit` (first unit saying that views are the authors' own). A row with voice_class institutional AND a disclaimer is flagged.
All of it is a PRE-FILL until the authors confirm it in the tier workbook (columns 'issuer (authors)', 'voice (authors)').

usage: record_issuers.py --tiers data/manifest/TIERS_2026-11-10.csv --workbook <ALL xlsx> --units <units dir> --date 2026-11-13
"""
import argparse, csv, glob, os, re, collections
import openpyxl
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
DISC = re.compile(r"(views?|opinions?|findings|conclusions) expressed .{0,80}(authors?|staff)|sole(ly)? (the )?responsibility of the authors?|(are|is) (solely )?(those|that) of the (respective )?authors?", re.I)
INTL = re.compile(r"(do(es)? not necessarily reflect|views of) .{0,60}(World Bank|International Monetary Fund|IMF|Bank for International Settlements)", re.I)
CB = re.compile(r"bank|monetary authority|riksbank|banco|banque|banka|národní|seðlabank|cbrt|cbuae|centrale", re.I)


def norm(issuer, kind):
    s = issuer or ""; lo = s.lower(); first = re.split(r"[/;(]| and | with ", s)[0].strip()
    leg = bool(re.search(r"parliament|duma|assembly|legislat|gazette|law of|\bdpr\b|house of representatives", lo)) or kind == "legislation"
    gov = bool(re.search(r"ministr|treasury|government|federal", lo))
    cb = bool(CB.search(first)) and not re.match(r"(government|ministry|hm treasury|republic|russian federation|uae federal)", first.lower())
    typ = "central_bank" if cb else "legislature" if leg and not gov else "government" if gov else "legislature" if leg else "other"
    s0 = re.sub(r"\([^)]*\)", lambda k: k.group(0) if re.search(r"\bwith\b|partner", k.group(0)) else "", s)  # departments, speakers and portals in brackets are not co-issuers
    m = re.search(r"\b(?:and|with|/)\s+(.+)$", s0)
    joint = re.sub(r"[()]", "", m.group(1)).strip() if m and not re.search(r"gazette|portal|council|president", m.group(1).lower()) else ""
    if kind == "legislation" or re.search(r"gazette|law of the|\bbill\b|legislation portal|rulebook", lo): voice = "legal_text"
    elif re.search(r"\((deputy )?governor|board member|\(president\)|\bgovernor\b", lo) or kind == "speech": voice = "official_speech"
    elif re.search(r"\bstaff\b|\([A-Z][^()]+, [A-Z][^()]+\)", s) or kind == "research_general": voice = "staff_authored"
    elif kind == "minutes": voice = "meeting_record"
    elif gov and CB.search(s): voice = "joint_with_government"
    elif joint and cb: voice = "joint_with_external"
    else: voice = "institutional"
    return typ, joint, voice


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--tiers", required=True); ap.add_argument("--workbook", required=True); ap.add_argument("--units", required=True); ap.add_argument("--date", required=True)
    a = ap.parse_args()
    ws = openpyxl.load_workbook(a.workbook, read_only=True)["ALL_DOCUMENTS"]; R = list(ws.iter_rows(values_only=True)); h = R[0]; W = {r[h.index("id")]: dict(zip(h, r)) for r in R[1:]}
    prop = {r["id"]: r for r in csv.DictReader(open(sorted(glob.glob(os.path.join(ROOT, "data/manifest/ISSUERS_PROPOSED_*.csv")))[-1], encoding="utf-8"))}
    um = {r["id"]: r for r in csv.DictReader(open(sorted(glob.glob(os.path.join(ROOT, "data/units/UNITS_MANIFEST_*.csv")))[-1], encoding="utf-8"))}
    out = []
    for r in csv.DictReader(open(a.tiers, encoding="utf-8")):
        if r["decision_v12"] not in ("KEEP", "BORDERLINE") or r["tier"] == "out_of_frame": continue
        w = W.get(r["id"], {}); kind = w.get("kind") or ""
        if r["id"] in prop:
            p = prop[r["id"]]; issuer, typ, joint, voice, key, note, src = p["issuer"], p["issuer_type"], p["joint_with"], p["voice_class"], p["name_key"], p["note"], "proposed_" + a.date
        else:
            issuer = w.get("issuer") or ""; typ, joint, voice = norm(issuer, kind); key = re.split(r"[/;(,]| and | with ", issuer)[0].strip(); note = ""; src = "prescreen_record"
        name = disc = ""
        if r["id"] in um:
            U = list(csv.DictReader(open(os.path.join(a.units, um[r["id"]]["doc_key"] + ".units.csv"), encoding="utf-8")))
            head = " ".join(u["text"] for u in U if u["page"] in ("1", "2", "3", "4", "5", "6"))
            name = ("yes" if re.search(key, head, re.I) else "no") if key and src != "prescreen_record" else ""  # key is a regular expression chosen with the proposal
            d = next((u for u in U[:max(150, len(U) // 8)] if DISC.search(u["text"])), None); disc = d["unit_id"] if d else ""
            if any(INTL.search(u["text"]) for u in U[:max(150, len(U) // 8)]): note = (note + "; " if note else "") + "disclaimer of an international organisation in the front matter: check who publishes"
        rep = "yes" if kind in ("consultation_response", "minutes") or voice in ("meeting_record", "commissioned_external") or re.search(r"respondents' views|participants' views|external feedback", note) else ""
        flag = "; ".join(x for x in ["disclaimer found but voice institutional: check" if disc and voice == "institutional" else "", "issuer name not found on pages 1-6: check" if name == "no" else "", "check who publishes" if "international organisation" in note else "", "disclaimer found: staff paper?" if disc and voice in ("joint_with_external", "official_speech", "joint_with_government") else "",
                                     "issuer is not a central bank" if typ != "central_bank" else ""] if x)
        out.append({"id": r["id"], "project": r["project"], "tier": r["tier"], "year": r["year"], "kind": kind, "issuer": issuer, "issuer_type": typ, "joint_with": joint, "voice_class": voice, "reports_views": rep,
                    "issuer_source": src, "unitised": "yes" if r["id"] in um else "no", "name_on_first_pages": name, "disclaimer_unit": disc, "check": flag, "note": note})
    f = os.path.join(ROOT, "data/manifest", f"ISSUERS_{a.date}.csv")
    with open(f, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out[0].keys())); w.writeheader(); w.writerows(out)
    c = collections.Counter
    print(len(out), "evidence documents;", dict(c(o["issuer_type"] for o in out)), dict(c(o["voice_class"] for o in out)), "; source", dict(c(o["issuer_source"] for o in out)),
          "; name not found", sum(o["name_on_first_pages"] == "no" for o in out), "; disclaimers", sum(bool(o["disclaimer_unit"]) for o in out), "; flagged", sum(bool(o["check"]) for o in out))


if __name__ == "__main__": main()
