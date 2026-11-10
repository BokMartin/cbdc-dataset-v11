#!/usr/bin/env python3
"""Check the translation responses of one run (API or manual Playground), assemble one English text per document and write the manifest.

For every document of the run folder <pack>/responses/<run>/<doc_key>/ it requires one `<request name>.response.txt` per registered
chunk and checks each response: (1) first line `TRANSLATION doc_key=… chunk=i/n source_sha256=…` equals the request; (2) the marker
lines `=== PAGE x ===` are exactly those of the request, in order; (3) last line `=== END OF CHUNK ===`; (4) the translation of a
non-empty page is not empty and the response is not suspiciously short (< 25 % of the source characters; < 60 % for zh/ja sources is
normal and not flagged); (5) share of the response that is still in the source language (lingua, per page) is reported.
A document passes only if all its chunks pass. Assembled text: <pack>/translations/<run>/<doc_key>.en.txt with the pipeline's page
markers (`=== PAGE n ===`; parts n.k of one page are joined), preceded by a provenance header.
Manifest (repository): data/translation/TRANSLATION_MANIFEST_<run>.csv, one row per document: source SHA-256, request SHA-256s,
response SHA-256s, SHA-256 of the assembled English text, provider, model, system-prompt SHA-256, interface, date, checks, counts of
[TN:] notes and [ILLEGIBLE] marks. For a manual run put the settings in <run folder>/RUN_META.json (template in the pack).
The script never edits a response; a failed chunk is re-run, not repaired.

usage: ingest_translations.py --pack <dir> --date 2026-11-10 --run <run name>
"""
import argparse, csv, hashlib, json, os, re, collections
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))


def sha(s): return hashlib.sha256(s.encode("utf-8")).hexdigest()


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--pack", required=True); ap.add_argument("--date", required=True); ap.add_argument("--run", required=True); a = ap.parse_args()
    system = open(os.path.join(ROOT, "pipeline/prompts/translation.system.md"), encoding="utf-8").read()
    Q = {q["doc_key"]: q for q in csv.DictReader(open(os.path.join(a.pack, f"TRANSLATION_QUEUE_{a.date}.csv"), encoding="utf-8"))}
    reqs = collections.defaultdict(list)
    for r in csv.DictReader(open(os.path.join(a.pack, f"TRANSLATION_REQUESTS_{a.date}.csv"), encoding="utf-8")): reqs[r["doc_key"]].append(r)
    run = os.path.join(a.pack, "responses", a.run); rm = json.load(open(os.path.join(run, "RUN_META.json")))
    if rm.get("system_sha256") and rm["system_sha256"] != sha(system): print("WARNING: RUN_META system_sha256 differs from pipeline/prompts/translation.system.md")
    try:
        from lingua import LanguageDetectorBuilder; det = LanguageDetectorBuilder.from_all_languages().build()
    except Exception: det = None
    outdir = os.path.join(a.pack, "translations", a.run); os.makedirs(outdir, exist_ok=True); rows = []
    for key in sorted(d for d in os.listdir(run) if os.path.isdir(os.path.join(run, d))):
        q = Q[key]; problems = []; pages = collections.OrderedDict(); rsha = []; usha = []; src_chars = 0; out_chars = 0; models = set()
        for r in sorted(reqs[key], key=lambda r: int(r["chunk"])):
            base = os.path.join(run, key, os.path.basename(r["request_file"])[:-4]); usha.append(r["user_sha256"])
            if not os.path.exists(base + ".response.txt"): problems.append(f"chunk {r['chunk']}: no response"); continue
            user = open(os.path.join(a.pack, r["request_file"]), encoding="utf-8").read()
            if sha(user) != r["user_sha256"]: problems.append(f"chunk {r['chunk']}: request file changed")
            text = open(base + ".response.txt", encoding="utf-8").read().replace("\r\n", "\n"); rsha.append(sha(text))
            if os.path.exists(base + ".meta.json"):
                m = json.load(open(base + ".meta.json")); models.add(m.get("model_returned", ""))
                if not m.get("complete", True): problems.append(f"chunk {r['chunk']}: marked incomplete ({m.get('stop_reason')})")
            lines = text.strip().split("\n")
            want = f"TRANSLATION doc_key={key} chunk={r['chunk']}/{r['of']} source_sha256={r['source_sha256']}"
            if lines[0].strip() != want: problems.append(f"chunk {r['chunk']}: header line differs")
            if lines[-1].strip() != "=== END OF CHUNK ===": problems.append(f"chunk {r['chunk']}: END marker missing (truncated?)")
            src = re.split(r"=== PAGE ([\d.]+) ===\n", user.split("--- BEGIN SOURCE TEXT ---\n", 1)[1].rsplit("--- END SOURCE TEXT ---", 1)[0])[1:]
            got = re.split(r"=== PAGE ([\d.]+) ===\n?", "\n".join(lines[1:-1]) + "\n")[1:]
            sm, gm = src[0::2], got[0::2]
            if sm != gm: problems.append(f"chunk {r['chunk']}: page markers differ (source {len(sm)}, response {len(gm)})"); continue
            for n, s, g in zip(sm, src[1::2], got[1::2]):
                s1 = re.sub(r"\s+", " ", s).strip(); g1 = g.strip(); src_chars += len(s1); out_chars += len(g1)
                if len(s1) > 200 and len(g1) < 20: problems.append(f"page {n}: empty translation")
                pages.setdefault(n.split(".")[0], []).append(g1)
        lang = q["language"].replace("mixed:", ""); ratio = round(out_chars / src_chars, 2) if src_chars else 0
        if src_chars and ratio < (0.6 if lang in ("zh", "ja") else 0.25) and lang not in (): problems.append(f"translation short: {ratio} of source characters")
        body = "".join(f"=== PAGE {n} ===\n" + "\n\n".join(p for p in parts if p) + "\n" for n, parts in pages.items())
        left = ""
        if det and pages:
            c = collections.Counter()
            for parts in pages.values():
                t = " ".join(parts)
                if len(t) >= 300: l = det.detect_language_of(t[:4000]); c[l.iso_code_639_1.name.lower() if l else "?"] += 1
            tot = sum(c.values()); left = round(1 - c.get("en", 0) / tot, 2) if tot else ""
            if tot and left > 0.1: problems.append(f"{left:.0%} of pages not detected as English")
        status = "ok" if not problems else "FAILED"
        head = (f"# English machine translation (route D, provisional). doc_key: {key} | source: {q['master_path']} | source_sha256: {q['source_sha256']}\n"
                f"# provider: {rm.get('provider')} | model: {'; '.join(sorted(x for x in models if x)) or rm.get('model') or rm.get('model_requested')} | interface: {rm.get('interface')} | run: {a.run} | system prompt sha256: {sha(system)}\n"
                f"# Not checked by a reader of the source language. Report errors via the project website.\n")
        if status == "ok": open(os.path.join(outdir, key + ".en.txt"), "w", encoding="utf-8", newline="\n").write(head + body)
        rows.append({"doc_key": key, "id": q["id"], "project": q["project"], "year": q["year"], "priority": q["priority"], "source_language": q["language"], "master_path": q["master_path"], "source_sha256": q["source_sha256"],
                     "chunks": len(reqs[key]), "request_sha256": " ".join(usha), "response_sha256": " ".join(rsha), "translation_file": f"translations/{a.run}/{key}.en.txt" if status == "ok" else "",
                     "translation_sha256": sha(head + body) if status == "ok" else "", "pages": len(pages), "source_chars": src_chars, "translation_chars": out_chars, "ratio": ratio, "share_not_english": left,
                     "translator_notes": body.count("[TN:"), "illegible_marks": body.count("[ILLEGIBLE]"), "provider": rm.get("provider", ""), "model": "; ".join(sorted(x for x in models if x)) or rm.get("model") or rm.get("model_requested", ""),
                     "interface": rm.get("interface", ""), "run": a.run, "date_utc": (rm.get("started_utc") or rm.get("date_utc") or "")[:10], "system_sha256": sha(system), "route": "D (machine translation, provisional)" if q["priority"] != "BENCH" else "benchmark only (issuer English edition is the evidence)",
                     "status": status, "problems": "; ".join(problems)})
    dst = os.path.join(ROOT, "data/translation", f"TRANSLATION_MANIFEST_{a.run}.csv")
    with open(dst, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    print(dst, len(rows), "documents;", dict(collections.Counter(r["status"] for r in rows)))
    for r in rows:
        if r["status"] != "ok": print("  FAILED", r["doc_key"], "|", r["problems"][:200])


if __name__ == "__main__": main()
