#!/usr/bin/env python3
"""Translation queue and request pack for the non-English documents of T1/T2 projects (route D of the language ledger), 10 Nov 2026.

MB, 9-10 Nov 2026: every non-English document is translated into English by a second LLM and the pipeline works in English only
(a translation error is preferred to model bias; a translation-vs-original sub-sample is kept for comparison).

Queue (one row per non-English document of a T1/T2 project with decision KEEP / BORDERLINE / RECHECK):
  priority  A = evidence (KEEP/BORDERLINE) · B = RECHECK (translate only if the authors keep it) · RB = the issuer publishes its own
            English edition of the same document (route B: that edition is the evidence; NO translation request is built) · BENCH = a
            route-B document chosen as translation-quality benchmark (translated with the same prompt and compared with the issuer's English)
            The English-edition check of 10 Nov 2026 is in data/translation/ROUTE_B_PAIRS.csv (status full_edition / partial / unofficial /
            none_found, URL, how it was verified, confidence); only full_edition changes the route. LANGUAGE_OVERRIDES.csv sets the language
            of files whose text layer could not be detected (scans of English originals leave the queue).
  input_mode  text = text layer usable (requests are built) · ocr_or_pdf = scanned / garbled text layer (no request built: OCR first, or
            give the PDF itself to a vision model with the same system prompt) · no_file = document not retrieved
Request pack (written OUTSIDE the repository: source texts are the issuers' copyright): <pack>/requests/<A_evidence|B_recheck_later|BENCH_quality_check>/<doc_key>/<doc_key>.chunk-XX-of-NN.txt,
each a complete user message (header with doc_key, source SHA-256, chunk and page range; then the page-marked source text).
Chunks are cut at page markers (a page longer than the limit is split at paragraph breaks into parts PAGE n.k); limit --chars
(default 18 000 characters; 9 000 for zh / ja, whose characters carry more text).
Repository gets only: data/translation/TRANSLATION_QUEUE_<date>.csv and TRANSLATION_REQUESTS_<date>.csv (per chunk: pages, characters,
SHA-256 of the exact user message), so any later run can prove it sent the same bytes.

usage: build_translation_pack.py --tiers data/manifest/TIERS_2026-11-10.csv --cache <text cache dir> --pack <dir> --date 2026-11-10 [--route-b data/translation/ROUTE_B_PAIRS.csv]
"""
import argparse, csv, glob, hashlib, os, re, collections
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
DENSE = {"zh", "ja", "ko"}
NAMES = {"ru": "Russian", "zh": "Chinese", "ja": "Japanese", "es": "Spanish", "nb": "Norwegian Bokmål", "sl": "Slovenian", "fi": "Finnish", "nl": "Dutch", "th": "Thai", "tr": "Turkish", "sv": "Swedish",
         "de": "German", "fr": "French", "pt": "Portuguese", "cs": "Czech", "id": "Indonesian", "is": "Icelandic", "hu": "Hungarian", "uk": "Ukrainian", "ne": "Nepali", "ar": "Arabic"}


def sha(s): return hashlib.sha256(s.encode("utf-8")).hexdigest()


def units(text, limit):
    """[(marker label, text)] : pages, long pages split at paragraph breaks into parts n.k"""
    parts = re.split(r"=== PAGE (\d+) ===\n", text)[1:]; out = []
    for n, t in zip(parts[0::2], parts[1::2]):
        t = t.rstrip()
        if len(t) <= limit: out.append((n, t)); continue
        paras = re.split(r"(\n\s*\n)", t); cur = ""; k = 1
        for p in paras:
            while len(p) > limit:  # a single paragraph longer than the limit: hard cut at a line break
                cut = p.rfind("\n", 0, limit); cut = cut if cut > limit // 2 else limit
                if cur: out.append((f"{n}.{k}", cur)); k += 1; cur = ""
                out.append((f"{n}.{k}", p[:cut])); k += 1; p = p[cut:]
            if len(cur) + len(p) > limit and cur.strip(): out.append((f"{n}.{k}", cur)); k += 1; cur = ""
            cur += p
        if cur.strip(): out.append((f"{n}.{k}", cur))
    return out


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--tiers", required=True); ap.add_argument("--cache", required=True); ap.add_argument("--pack", required=True); ap.add_argument("--date", required=True)
    ap.add_argument("--route-b", default=os.path.join(ROOT, "data/translation/ROUTE_B_PAIRS.csv")); ap.add_argument("--chars", type=int, default=18000); ap.add_argument("--chars-dense", type=int, default=9000)
    a = ap.parse_args()
    rb = {r["id"]: r for r in csv.DictReader(open(a.route_b, encoding="utf-8"))} if os.path.exists(a.route_b) else {}
    ovp = os.path.join(ROOT, "data/translation/LANGUAGE_OVERRIDES.csv"); ov = {r["id"]: r for r in csv.DictReader(open(ovp, encoding="utf-8"))} if os.path.exists(ovp) else {}
    eds = {}
    for f in sorted(glob.glob(os.path.join(ROOT, "data/translation/ENGLISH_EDITIONS_*.csv"))):
        for e in csv.DictReader(open(f, encoding="utf-8")): eds[e["parallel_of"]] = e
    queue = []; reqs = []
    for r in csv.DictReader(open(a.tiers, encoding="utf-8")):
        if r["tier"] not in ("T1", "T2") or r["decision_v12"] not in ("KEEP", "BORDERLINE", "RECHECK"): continue
        if r["id"] in ov: r["language"] = ov[r["id"]]["language"]
        if r["language"] == "en": continue
        lang = r["language"].replace("mixed:", ""); key = re.sub(r"[^A-Za-z0-9_-]+", "-", f"{r['project']}_{r['id']}")[:70]
        b = rb.get(r["id"])
        full = b and b["status"] == "full_edition"
        prio = ("BENCH" if b["benchmark"] == "yes" else "RB") if full else ("A" if r["decision_v12"] in ("KEEP", "BORDERLINE") else "B")
        cf = os.path.join(a.cache, r["sha256"] + ".txt") if r["sha256"] else ""
        if not r["master_path"]: mode = "no_file"
        elif r["text_flag"].startswith(("scanned", "garbled", "too_little")) or not lang or not os.path.exists(cf): mode = "ocr_or_pdf"
        else: mode = "text"
        q = {"doc_key": key, "priority": prio, "input_mode": mode, "tier": r["tier"], "project": r["project"], "year": r["year"], "id": r["id"], "decision_v12": r["decision_v12"], "language": r["language"],
             "share_en": r["share_en"], "pages": r["pages"], "chars": "", "chunks": "", "title": r["title"], "master_path": r["master_path"], "source_sha256": r["sha256"],
             "issuer_english_edition": (f"{b['status']}: {b['english_edition']}" if b else "not checked"), "check_confidence": (b["confidence"] if b else ""),
             "english_edition_file": (lambda e: (f"CBDC_MASTER_v12/{e['project']}/{e['fname']} (sha256 {e['sha256']}, {e['pages'] or 1} p.)" if e and e["fname"] else (e["status"] if e else "")))(eds.get(r["id"])),
             "note": "; ".join(x for x in [(b["note"] if b else ""), r["text_flag"], (ov[r["id"]]["basis"] if r["id"] in ov else "")] if x)}
        if mode == "text" and prio != "RB":
            limit = a.chars_dense if lang in DENSE else a.chars
            us = units(open(cf, encoding="utf-8").read(), limit); chunks = []; cur = []; size = 0
            for u in us:
                if cur and size + len(u[1]) > limit: chunks.append(cur); cur = []; size = 0
                cur.append(u); size += len(u[1])
            if cur: chunks.append(cur)
            q["chars"] = sum(len(t) for _, t in us); q["chunks"] = len(chunks)
            pf = {"A": "A_evidence", "B": "B_recheck_later", "BENCH": "BENCH_quality_check"}[prio]; d = os.path.join(a.pack, "requests", pf, key); os.makedirs(d, exist_ok=True)
            for i, ch in enumerate(chunks, 1):
                body = "".join(f"=== PAGE {n} ===\n{t}\n" for n, t in ch)
                msg = (f"TRANSLATION REQUEST\ndoc_key: {key}\nproject: {r['project']} | year: {r['year']} | source language (detected): {NAMES.get(lang, lang)} ({lang})\n"
                       f"title: {r['title']}\nsource file: {r['master_path']}\nsource_sha256: {r['sha256']}\ntext layer: pdftotext -layout (PDF) / visible text (HTML), no OCR\n"
                       f"chunk: {i} of {len(chunks)} | markers PAGE {ch[0][0]} to PAGE {ch[-1][0]} | text_sha256: {sha(body)}\n--- BEGIN SOURCE TEXT ---\n{body}--- END SOURCE TEXT ---\n")
                fn = f"{key}.chunk-{i:02d}-of-{len(chunks):02d}.txt"; open(os.path.join(d, fn), "w", encoding="utf-8", newline="\n").write(msg)
                reqs.append({"doc_key": key, "chunk": i, "of": len(chunks), "first_marker": ch[0][0], "last_marker": ch[-1][0], "markers": len(ch), "chars": len(body), "priority": prio, "request_file": f"requests/{pf}/{key}/{fn}", "user_sha256": sha(msg), "source_sha256": r["sha256"]})
        if mode == "text" and r["master_path"].endswith(".html") and (q["chars"] or 0) > 60000 and not q["note"]:
            q["note"] = "long HTML page (whole law or page with boilerplate): consider translating only the cited provisions"
        queue.append(q)
    order = {"A": 0, "B": 1, "BENCH": 2, "RB": 3}
    queue.sort(key=lambda q: (order[q["priority"]], q["tier"], q["project"], q["year"], q["doc_key"]))
    os.makedirs(os.path.join(ROOT, "data/translation"), exist_ok=True)
    for name, rows in [(f"TRANSLATION_QUEUE_{a.date}.csv", queue), (f"TRANSLATION_REQUESTS_{a.date}.csv", reqs)]:
        for dst in (os.path.join(ROOT, "data/translation", name), os.path.join(a.pack, name)):
            with open(dst, "w", newline="", encoding="utf-8") as f:
                w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    c = collections.Counter((q["priority"], q["input_mode"]) for q in queue)
    print(len(queue), "documents;", dict(c)); print(len(reqs), "requests;", sum(r["chars"] for r in reqs), "source characters")
    for p in "A", "B", "BENCH", "RB": print(p, "text-mode docs", sum(1 for q in queue if q["priority"] == p and q["input_mode"] == "text"), "requests", sum(q["chunks"] or 0 for q in queue if q["priority"] == p))


if __name__ == "__main__": main()
