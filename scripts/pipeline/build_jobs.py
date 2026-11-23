#!/usr/bin/env python3
"""Build a job for scripts/pipeline/runner.py: the requests of one stage for a set of projects, written OUTSIDE the repository
(the user messages hold unit text, under the issuers' copyright). The repository gets only hashes, through the run record.

  talk_L1     every candidate unit of the documents (<doc>.candidates.csv), packed one unit per request (single) or one page
              per request (page); request = header + scripts/units/build_requests.py single() / page()
  talk_L2     the units listed in --units-file (the union of units any model called relevant), same packing
  extraction_single  one request per document, or per page range when the text is longer than --max-chars (consecutive ranges
              share one page, as the extraction prompt v12 says); the text is rebuilt from the unit files with `=== PAGE p ===`
              lines and ends with `=== END OF REQUEST TEXT ===`

The header of a talk request (DRAFT, fixed at the freeze with the prompts): `DOCUMENT <doc_key> | issuer <issuer> | issuer_type
<type> | kind <kind> | year <year>`, from the unit manifest, whose issuer fields come from the checked issuer ledger.
The extraction header lists the fields of prompt v12 §1; fields the repository does not hold yet are written `not_recorded` and
listed in JOB_META.json `warnings` (a development run may go ahead with them; a production run may not).

usage: build_jobs.py --stage talk_L1 --units <units dir> --projects NO UK --prompt pipeline/prompts/talk_L1_relevance.system.md
                     --out <job dir> [--packing single|page] [--units-file ids.txt] [--max-chars 240000] [--date 2026-11-23]
"""
import argparse, csv, glob, hashlib, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "scripts", "units"))
import build_requests as br  # noqa: E402


def sha(s): return hashlib.sha256(s.encode("utf-8")).hexdigest()
def sha_file(p): return hashlib.sha256(open(p, "rb").read()).hexdigest()
def rel(p): return os.path.relpath(p, ROOT).replace(os.sep, "/")
def rd(p): return list(csv.DictReader(open(p, encoding="utf-8")))


def latest(pattern):
    c = sorted(glob.glob(os.path.join(ROOT, pattern)))
    if not c: raise SystemExit(f"no file {pattern}")
    return c[-1]


def load_units(path):
    return [{**u, "page": int(u["page"]), "para": int(u["para"])} for u in rd(path)]


def talk_header(m):
    return f"DOCUMENT {m['doc_key']} | issuer {m['issuer']} | issuer_type {m['issuer_type']} | kind {m['kind']} | year {m['year']}"


def talk_requests(units, code_ids, m, packing):
    idx = {u["unit_id"]: i for i, u in enumerate(units)}; want = [idx[c] for c in code_ids if c in idx]
    missing = [c for c in code_ids if c not in idx]
    if missing: raise SystemExit(f"{m['doc_key']}: {len(missing)} units to code are not in the unit file, e.g. {missing[0]}")
    h = talk_header(m); out = []
    if packing == "single":
        for i in sorted(want): out.append(([units[i]["unit_id"]], br.single(units, i, h)))
    else:
        pages = {}
        for i in sorted(want): pages.setdefault(units[i]["page"], []).append(i)
        for p, ii in sorted(pages.items()): out.append(([units[i]["unit_id"] for i in ii], br.page(units, ii, h)))
    return out


def page_texts(units):
    pages = {}
    for u in units: pages.setdefault(u["page"], {}).setdefault(u["para"], []).append(u["text"])
    return {p: "\n\n".join(" ".join(t) for _, t in sorted(paras.items())) for p, paras in sorted(pages.items())}


def ranges(pages, max_chars):
    """[(first, last)] of consecutive page ranges under max_chars; consecutive ranges share one page."""
    ps = sorted(pages); out, s = [], 0
    while s < len(ps):
        e, size = s, len(pages[ps[s]])
        while e + 1 < len(ps) and size + len(pages[ps[e + 1]]) <= max_chars: e += 1; size += len(pages[ps[e]])
        out.append((ps[s], ps[e]))
        if e == len(ps) - 1: break
        s = e if e > s else e + 1
    return out


EXTRACTION_FIELDS = ["doc_key", "project", "issuer", "issuer_type", "decision_authority", "issue_date", "document_type", "layer", "text_route", "text_layer",
                     "pages_total", "pages_in_this_request", "page_span"]


def extraction_requests(units, m, max_chars, extra):
    pages = page_texts(units); total = int(m.get("pages") or max(pages)); out = []
    for a, b in ranges(pages, max_chars):
        h = {"doc_key": m["doc_key"], "project": m["project"], "issuer": m["issuer"], "issuer_type": m["issuer_type"],
             "decision_authority": extra.get("decision_authority", "not_recorded"), "issue_date": m["year"], "document_type": m["kind"],
             "layer": extra.get("layer", "not_recorded"), "text_route": m["route"], "text_layer": "ocr" if "ocr" in m["text_mode"] else "reading_order",
             "pages_total": str(total), "pages_in_this_request": f"{a}-{b} of {total}", "page_span": extra.get("page_span", "whole_document")}
        body = "\n".join(f"=== PAGE {p} ===\n{pages[p]}" for p in sorted(pages) if a <= p <= b)
        out.append((f"{m['doc_key']}:p{a}-{b}", [m["doc_key"]], "HEADER\n" + "\n".join(f"{k}: {h[k]}" for k in EXTRACTION_FIELDS) + "\n\nTEXT\n" + body + "\n=== END OF REQUEST TEXT ===\n"))
    return out


def prompt_version(text):
    m = re.search(r"(?i)prompt version:\s*([^\n(]+)", text) or re.search(r"(?i)\bv(\d+(?:\.\d+)*)\b", text)
    return m.group(1).strip() if m else "unversioned"


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", required=True, choices=["talk_L1", "talk_L2", "extraction_single"]); ap.add_argument("--units", required=True)
    ap.add_argument("--projects", nargs="+", required=True); ap.add_argument("--prompt", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--packing", choices=["single", "page"], default="single"); ap.add_argument("--units-file"); ap.add_argument("--max-chars", type=int, default=240000)
    ap.add_argument("--header-extra", help="CSV doc_key,decision_authority,layer,page_span for the extraction header")
    a = ap.parse_args(argv)
    manp = latest("data/units/UNITS_MANIFEST_*.csv"); man = [m for m in rd(manp) if m["project"] in a.projects]
    if not man: raise SystemExit("no document of these projects in the unit manifest")
    system = open(a.prompt, "rb").read().decode("utf-8")
    extra = {r["doc_key"]: r for r in rd(a.header_extra)} if a.header_extra else {}
    only = set(open(a.units_file, encoding="utf-8").read().split()) if a.units_file else None
    if a.stage == "talk_L2" and only is None: raise SystemExit("talk_L2 needs --units-file (the units any model called relevant)")
    reqs, inputs, warnings = [], [{"file": rel(manp), "sha256": sha_file(manp), "rows": len(man)}], []
    for m in sorted(man, key=lambda x: x["doc_key"]):
        up = os.path.join(a.units, m["doc_key"] + ".units.csv")
        if not os.path.exists(up): raise SystemExit(f"unit file missing: {up}")
        units = load_units(up); inputs.append({"file": "units/" + os.path.basename(up), "sha256": sha_file(up), "rows": len(units), "in_repository": False})
        if a.stage == "extraction_single":
            x = extra.get(m["doc_key"], {})
            for f in ("decision_authority", "layer"):
                if not x.get(f): warnings.append(f"{m['doc_key']}: {f} not_recorded")
            for key, ids, user in extraction_requests(units, m, a.max_chars, x): reqs.append({"request_key": key, "unit_ids": ids, "user": user})
            continue
        cp = os.path.join(a.units, m["doc_key"] + ".candidates.csv")
        code = [c["unit_id"] for c in rd(cp)] if a.stage == "talk_L1" else [u["unit_id"] for u in units if u["unit_id"] in only]
        if a.stage == "talk_L1": inputs.append({"file": "units/" + os.path.basename(cp), "sha256": sha_file(cp), "rows": len(code), "in_repository": False})
        for ids, user in talk_requests(units, code, m, a.packing):
            reqs.append({"request_key": ids[0] if a.packing == "single" else f"{m['doc_key']}:p{units[[u['unit_id'] for u in units].index(ids[0])]['page']}", "unit_ids": ids, "user": user})
    if a.units_file: inputs.append({"file": os.path.abspath(a.units_file), "sha256": sha_file(a.units_file), "rows": len(only), "in_repository": False})
    os.makedirs(a.out, exist_ok=True)
    with open(os.path.join(a.out, "REQUESTS.jsonl"), "w", encoding="utf-8") as fh:
        for r in reqs: fh.write(json.dumps({**r, "user_sha256": sha(r["user"])}, ensure_ascii=False) + "\n")
    open(os.path.join(a.out, "SYSTEM_PROMPT.md"), "wb").write(system.encode("utf-8"))
    fn = {"talk_L1": f"scripts/units/build_requests.py {a.packing}()", "talk_L2": f"scripts/units/build_requests.py {a.packing}()",
          "extraction_single": "scripts/pipeline/build_jobs.py extraction_requests()"}[a.stage]
    meta = {"stage": a.stage, "projects": a.projects, "system_prompt_file": rel(os.path.abspath(a.prompt)) if os.path.abspath(a.prompt).startswith(ROOT) else a.prompt,
            "system_prompt_version": prompt_version(system), "system_sha256": sha(system),
            "user_message_format": f"{fn} with header of scripts/pipeline/build_jobs.py (script_sha256 {sha_file(os.path.abspath(__file__))[:16]}…, build_requests {sha_file(br.__file__)[:16]}…)",
            "packing": {"single": "one unit per request", "page": "all units to code of one page per request"}[a.packing] if a.stage != "extraction_single" else f"one document per request, page ranges of at most {a.max_chars} characters with one shared page",
            "inputs": inputs, "requests": len(reqs), "units_to_code": sum(len(r["unit_ids"]) for r in reqs), "user_chars": sum(len(r["user"]) for r in reqs),
            "request_keys": [r["request_key"] for r in reqs], "warnings": warnings}
    json.dump(meta, open(os.path.join(a.out, "JOB_META.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print(f"{a.stage}: {len(reqs)} requests, {meta['units_to_code']} units, {meta['user_chars']:,} characters of user text -> {a.out}" + (f"; {len(warnings)} warnings" if warnings else ""))
    return meta


if __name__ == "__main__":
    main()
