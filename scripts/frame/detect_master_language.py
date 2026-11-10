#!/usr/bin/env python3
"""Page-level language detection for EVERY file of the master folder (registry + gap-check candidates), 10 Nov 2026.

Extends detect_doc_language.py (core documents only) to the 763 files of CBDC_MASTER_v12. Text layer: `pdftotext -layout` per page for
PDF, visible text for HTML (script/style removed, one "page"), paragraphs for DOCX. No OCR here: a PDF whose pages carry almost no
text is flagged `scanned_or_image` and needs OCR before anything else. Language: lingua (all languages, high accuracy) on every page
with >= 300 characters. A document is `en` when >= 80 % of detected pages are English, `mixed` when 20-80 %, else its dominant language.

Outputs: <out csv> with master_path, id, sha256, ext, pages, pages_with_text, chars, dominant, share_en, distribution, lang_class, flag;
and, with --cache, one text file per document (<sha256>.txt, pages separated by "=== PAGE n ===") reused by build_translation_pack.py.
Detection is a diagnostic; the ledger decision (route A/B/C/D) is the authors'.

usage: detect_master_language.py --manifest data/manifest/MASTER_MANIFEST_2026-11-10.csv --files <json sha256 -> local path> --cache <dir> --out data/manifest/MASTER_LANGUAGE_2026-11-10.csv
"""
import argparse, csv, json, os, re, subprocess, collections, html as htmllib


def pdf_pages(path):
    try:
        raw = subprocess.run(["pdftotext", "-layout", "-enc", "UTF-8", path, "-"], capture_output=True, timeout=600).stdout.decode("utf-8", "replace")
    except Exception:
        return []
    pages = raw.split("\f")
    return pages[:-1] if pages and not pages[-1].strip() else pages


def html_text(path):
    s = open(path, encoding="utf-8", errors="replace").read()
    s = re.sub(r"(?is)<(script|style|noscript|svg)\b.*?</\1>", " ", s)
    s = re.sub(r"(?i)<(br|/p|/div|/li|/h[1-6]|/tr)\s*/?>", "\n", s); s = re.sub(r"(?s)<[^>]+>", " ", s)
    s = htmllib.unescape(s); s = re.sub(r"[ \t\xa0]+", " ", s); s = re.sub(r"\n\s*\n+", "\n\n", s)
    return [s.strip()]


def docx_text(path):
    import zipfile
    x = zipfile.ZipFile(path).read("word/document.xml").decode("utf-8", "replace")
    x = re.sub(r"</w:p>", "\n", x); x = re.sub(r"<[^>]+>", "", x)
    return [htmllib.unescape(x).strip()]


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--manifest", required=True); ap.add_argument("--files", required=True); ap.add_argument("--cache"); ap.add_argument("--out", required=True)
    a = ap.parse_args(); loc = json.load(open(a.files))
    from lingua import LanguageDetectorBuilder
    det = LanguageDetectorBuilder.from_all_languages().with_preloaded_language_models().build()
    if a.cache: os.makedirs(a.cache, exist_ok=True)
    rows = []
    for r in csv.DictReader(open(a.manifest, encoding="utf-8")):
        p = loc.get(r["sha256"]); base = {"master_path": r["master_path"], "id": r["id"], "sha256": r["sha256"], "ext": r["ext"]}
        if not p or not os.path.exists(p):
            rows.append({**base, "pages": "", "pages_with_text": "", "chars": "", "dominant": "", "share_en": "", "distribution": "", "lang_class": "", "flag": "file_not_available_locally"}); continue
        cf = os.path.join(a.cache, r["sha256"] + ".txt") if a.cache else None
        if cf and os.path.exists(cf):
            pages = re.split(r"=== PAGE \d+ ===\n", open(cf, encoding="utf-8").read())[1:]
        else:
            pages = pdf_pages(p) if r["ext"] == "pdf" else (docx_text(p) if r["ext"] == "docx" else html_text(p))
            if cf: open(cf, "w", encoding="utf-8").write("".join(f"=== PAGE {i} ===\n{t.rstrip()}\n" for i, t in enumerate(pages, 1)))
        langs = collections.Counter(); withtext = 0; chars = 0
        for t in pages:
            t = re.sub(r"\s+", " ", t).strip(); chars += len(t)
            if len(t) >= 100: withtext += 1
            if len(t) < 300: continue
            l = det.detect_language_of(t[:6000]); langs[l.iso_code_639_1.name.lower() if l else "?"] += 1
        tot = sum(langs.values()); top = langs.most_common(1)[0][0] if langs else ""; en = (langs.get("en", 0) / tot) if tot else ""
        flag = ""
        if r["ext"] == "pdf" and (not pages or withtext < max(1, 0.5 * len(pages))): flag = "scanned_or_image (OCR needed)"
        elif not tot: flag = "too_little_text"
        cls = "" if not tot else ("en" if en >= 0.8 else ("mixed:" + top if en >= 0.2 else top))
        rows.append({**base, "pages": len(pages), "pages_with_text": withtext, "chars": chars, "dominant": top, "share_en": round(en, 2) if tot else "", "distribution": " ".join(f"{k}:{v}" for k, v in langs.most_common()), "lang_class": cls, "flag": flag})
    with open(a.out, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    print(a.out, len(rows), dict(collections.Counter(x["lang_class"] or x["flag"] for x in rows)))


if __name__ == "__main__": main()
