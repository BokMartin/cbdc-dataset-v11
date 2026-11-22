#!/usr/bin/env python3
"""Reader for the returned disagreement workbook (NESHODY_MB_DS_2026-11-17*.xlsx), sheet RELEVANCE.

The workbook came back on 22 Nov 2026 in a form the builder (`build_disagreement_workbook.py`) did not produce: on 19 Nov an AI
filled the joint columns as a PROPOSAL (label, reason A-D, rule or note), and on 22 Nov MB and DS went through it together and
wrote their answer to each row into a new column O ("souhlas s pravidlo / poznámka nebo alternativa").

Reading of column O (one row = one development unit):
  - "ok" (any case, optionally after "dokument už není v evidenci -")  -> the authors accept the proposed label and rule: agreed.
  - "final : X" with X in R/N/U                                          -> the authors set X themselves: agreed, override.
  - anything else ("?", a coder's initials, a comment)                   -> NOT read as a label; status needs_author_check.
A row is never guessed. The blind labels (`data/units/DEV_LABELS_*`) are never overwritten; the script checks that the workbook's
MB and DS columns equal them, joined on unit_id.

Output: one CSV row per disagreement unit, without any source text (the workbook holds sentences and stays off the repository).
For reason B the general rule sentence is kept ("Pravidlo: ..." up to its first full stop); case notes, which quote the unit, are not.

Rows the workbook leaves unclear can be settled by the authors later in words; those answers are passed in --clarify
(data/units/DEV_ADJUDICATION_CLARIFICATIONS_<date>.csv: unit_id, joint_label, clarified_by, date, source, note_for_prompt) and
are applied only to rows whose workbook answer was unclear.

usage: read_disagreement_workbook.py --workbook <xlsx> --out data/units/DEV_ADJUDICATED_RELEVANCE_MB_DS_<date>.csv --date <YYYY-MM-DD> [--clarify <csv>]
"""
import argparse, csv, glob, hashlib, os, re
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
V = ("R", "N", "U")
COLS = ["unit_id", "project", "mb_blind", "ds_blind", "ai_proposal_label", "ai_proposal_took", "reason", "rule_proposed",
        "authors_response", "joint_label", "status", "basis", "rule_status", "doc_in_current_corpus", "adjudicated_by", "date", "clarification_source", "note_for_prompt", "workbook_sha256"]


def read_response(text):
    """Column O -> (label or None, basis). label None means the row needs the authors."""
    t = re.sub(r"\s+", " ", str(text or "")).strip()
    core = re.sub(r"^dokument už není v evidenci\s*-\s*", "", t, flags=re.I).strip()
    if core.lower() == "ok": return None, "accepted_proposal"
    m = re.fullmatch(r"final\s*:\s*([RNU])", core, flags=re.I)
    if m: return m.group(1).upper(), "authors_override"
    return None, "unclear"


def rule_of(note):
    """The general rule sentence of a reason-B note, without the case-specific remainder."""
    m = re.search(r"Pravidlo:\s*(.+?\.)(?:\s|$)", str(note or ""))
    return m.group(1).strip() if m else ""


def took_of(note):
    m = re.search(r"převzato (MB|DS)", str(note or ""))
    return m.group(1) if m else ("new" if "nové rozhodnutí" in str(note or "") else "")


def adjudicate(row):
    """row: dict with proposal, reason, note, response. Returns joint_label, status, basis, rule_status."""
    label, basis = read_response(row["response"])
    rule = rule_of(row["note"]) if row["reason"] == "B" else ""
    if basis == "accepted_proposal":
        return row["proposal"], "agreed", basis, ("accepted" if rule else "")
    if basis == "authors_override":
        return label, "agreed", basis, ("rejected" if rule and label != row["proposal"] else ("accepted" if rule else ""))
    return "", "needs_author_check", basis, ("open" if rule else "")


def main():
    import openpyxl
    ap = argparse.ArgumentParser(); ap.add_argument("--workbook", required=True); ap.add_argument("--out", required=True); ap.add_argument("--date", required=True); ap.add_argument("--clarify"); a = ap.parse_args()
    clar = {r["unit_id"]: r for r in csv.DictReader(open(a.clarify, encoding="utf-8"))} if a.clarify else {}
    sha = hashlib.sha256(open(a.workbook, "rb").read()).hexdigest()
    ws = openpyxl.load_workbook(a.workbook)["RELEVANCE"]; rows = list(ws.iter_rows(values_only=True)); h = rows[0]
    assert h[2] == "unit_id" and h[9] == "MB" and h[10] == "DS" and h[11] == "spolecny_stitek" and str(h[14]).startswith("souhlas"), "unexpected layout of sheet RELEVANCE"
    blind = {}
    for who in ("MB", "DS"):
        p = sorted(glob.glob(os.path.join(ROOT, f"data/units/DEV_LABELS_{who}_*.csv")))[-1]
        blind[who] = {r["unit_id"]: r for r in csv.DictReader(open(p, encoding="utf-8"))}
    man = {r["doc_key"] for r in csv.DictReader(open(sorted(glob.glob(os.path.join(ROOT, "data/units/UNITS_MANIFEST_*.csv")))[-1], encoding="utf-8"))}
    out = []
    for r in rows[1:]:
        if not r[2]: continue
        u = r[2]; mb, ds = blind["MB"][u], blind["DS"][u]
        wb_mb = "" if str(r[9]) == "(prázdné)" else str(r[9]).strip().upper()
        mb_file = mb["relevant"] or ("" if mb["as_typed"].strip().lower() in ("", "blank") else mb["as_typed"].strip().upper())
        assert wb_mb == mb_file, f"MB column differs from the blind file for {u}"
        assert str(r[10]).strip().upper() == ds["relevant"], f"DS column differs from the blind file for {u}"
        x = {"proposal": str(r[11]).strip().upper(), "reason": str(r[12] or "").strip().upper(), "note": r[13], "response": r[14]}
        joint, status, basis, rs = adjudicate(x); c = clar.pop(u, None)
        if c:
            assert status == "needs_author_check" and c["joint_label"] in V, f"clarification for {u} applies only to an unclear row"
            joint, status, basis = c["joint_label"], "agreed", "authors_clarification"
            if rs == "open": rs = "accepted" if joint == x["proposal"] else "rejected"
        out.append({"unit_id": u, "project": r[3], "mb_blind": mb["relevant"] or ("invalid:" + mb_file if mb_file else "blank"), "ds_blind": ds["relevant"],
                    "ai_proposal_label": x["proposal"], "ai_proposal_took": took_of(x["note"]), "reason": x["reason"], "rule_proposed": rule_of(x["note"]) if x["reason"] == "B" else "",
                    "authors_response": re.sub(r"\s+", " ", str(r[14] or "")).strip(), "joint_label": joint, "status": status, "basis": basis, "rule_status": rs,
                    "doc_in_current_corpus": "yes" if u.split(":p")[0] in man else "no", "adjudicated_by": ("MB+DS jointly" + (", clarified by " + c["clarified_by"] if c else "")) if status == "agreed" else "",
                    "date": (c["date"] if c else a.date) if status == "agreed" else "", "clarification_source": c["source"] if c else "", "note_for_prompt": c["note_for_prompt"] if c else "", "workbook_sha256": sha})
    assert not clar, f"clarifications for units not in the workbook: {sorted(clar)}"
    out.sort(key=lambda d: d["unit_id"])
    with open(a.out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLS); w.writeheader(); w.writerows(out)
    import collections
    print(a.out, len(out), dict(collections.Counter(d["status"] for d in out)), dict(collections.Counter(d["joint_label"] for d in out if d["status"] == "agreed")))


if __name__ == "__main__": main()
