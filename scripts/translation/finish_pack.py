#!/usr/bin/env python3
"""Complete the translation pack after build_translation_pack.py: copy the system prompt, write the assignment for the second LLM
(TASK_FOR_LLM.md, English), the operator's instructions (ZADANI_cs.md, Czech), the RUN_META template and the Excel view of the queue.
All counts in the texts are computed from the queue, so the documents cannot drift from the pack.

usage: finish_pack.py --pack <dir> --date 2026-11-10
"""
import argparse, csv, hashlib, json, os, collections
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--pack", required=True); ap.add_argument("--date", required=True); a = ap.parse_args(); P = a.pack
    Q = list(csv.DictReader(open(os.path.join(P, f"TRANSLATION_QUEUE_{a.date}.csv"), encoding="utf-8")))
    R = list(csv.DictReader(open(os.path.join(P, f"TRANSLATION_REQUESTS_{a.date}.csv"), encoding="utf-8")))
    system = open(os.path.join(ROOT, "pipeline/prompts/translation.system.md"), encoding="utf-8").read(); h = hashlib.sha256(system.encode("utf-8")).hexdigest()
    open(os.path.join(P, "SYSTEM_PROMPT_translation.md"), "w", encoding="utf-8", newline="\n").write(system)
    n = {p: (sum(1 for q in Q if q["priority"] == p), sum(1 for q in Q if q["priority"] == p and q["chunks"]), sum(1 for r in R if r["priority"] == p), sum(int(r["chars"]) for r in R if r["priority"] == p)) for p in ("A", "B", "BENCH", "RB")}
    langs = collections.Counter(q["language"].replace("mixed:", "") for q in Q if q["priority"] == "A" and q["chunks"])
    notext = [q for q in Q if q["priority"] in ("A", "B") and not q["chunks"]]
    os.makedirs(os.path.join(P, "responses", "RUN_NAME_example"), exist_ok=True)
    json.dump({"run": "<folder name, e.g. openai_<model>_20261111>", "provider": "<openai | anthropic | google | ...>", "model": "<exact model id>", "interface": "<API | Playground | chat with file upload / agent mode>",
               "operator": "MB", "date_utc": "2026-11-..", "temperature": None, "top_p": None, "max_output_tokens": None, "reasoning": "<as set>", "one_request_per_conversation": "<yes | no: batch session>",
               "other": "<tools, anything else shown in the settings>", "system_sha256": h,
               "notes": "System prompt = SYSTEM_PROMPT_translation.md, unchanged. Responses saved unedited as <request name>.response.txt (UTF-8)."},
              open(os.path.join(P, "responses", "RUN_NAME_example", "RUN_META.json"), "w"), indent=1, ensure_ascii=False)
    task = f"""# Task: translate official CBDC documents into English (research pipeline, translation v1.1)

You are given this archive. Your job is to translate the request files in `requests/A_evidence/` into English, one response file per request file, following `SYSTEM_PROMPT_translation.md` exactly. Read that file first: it is the binding specification (output format, completeness, preservation of commitment wording, key terms, damaged input).

## What is in the archive
- `SYSTEM_PROMPT_translation.md` : the translation rules. SHA-256 `{h}`.
- `requests/A_evidence/<doc_key>/<doc_key>.chunk-XX-of-NN.txt` : {n['A'][2]} request files for {n['A'][1]} documents ({', '.join(f'{k} {v}' for k, v in langs.most_common())} by detected language). Each file is one complete request: a header and a page-marked chunk of the source text. This is the work.
- `requests/B_recheck_later/` ({n['B'][2]} files) and `requests/BENCH_quality_check/` ({n['BENCH'][2]} files) : do NOT translate these unless you are told to. They are a later batch and a quality benchmark.
- `TRANSLATION_REQUESTS_{a.date}.csv`, `TRANSLATION_QUEUE_{a.date}.csv/.xlsx` : registers (file list, hashes, document metadata). You do not need to change them.

## How to work
1. Process the request files of `requests/A_evidence/` in alphabetical order of path. Translate every file; do not sample, skip or merge files.
2. Treat every request file as an independent job. Do not use other chunks, other documents or anything you know about the project or the institution to fill in, correct or harmonise a translation. The only shared element is the list of fixed English terms in rule 4 of the system prompt.
3. For each request file write exactly one response file with the same name and the ending `.response.txt` instead of `.txt`, in `responses/<doc_key>/`. Example: `requests/A_evidence/KZ_CAND-152/KZ_CAND-152.chunk-01-of-01.txt` -> `responses/KZ_CAND-152/KZ_CAND-152.chunk-01-of-01.response.txt`. Plain text, UTF-8, no Markdown fences.
4. The response file contains only what the system prompt specifies: line 1 `TRANSLATION doc_key=... chunk=i/n source_sha256=...` (values copied from the request header), then every `=== PAGE x ===` marker of the request, unchanged and in order, each followed by the English translation of the text under it, and the last line `=== END OF CHUNK ===`.
5. Translate the full text yourself, sentence by sentence. Do not summarise, do not shorten long or repetitive passages (legal texts, tables, lists), do not write placeholders such as "[continues]" or "[table omitted]", and do not use an external machine-translation tool or script to produce the text.
6. Do not compute or alter any hash. Copy `source_sha256` from the header character for character.
7. If the output for one request would be cut off by your length limit, stop, and produce that file again in full in a fresh step; never deliver a response that lacks the END line. If a request cannot be translated at all (unreadable input), still write the response file with the header line, the markers, `[ILLEGIBLE]` under each marker and the END line.
8. Before delivering, check every response file: header line equals the request (doc_key, chunk, source_sha256); same number and order of PAGE markers as the request; END line present; no page left empty unless it is empty in the request; no remaining untranslated paragraphs except text that was already English.

## What to deliver
- A single archive `responses.zip` containing the `responses/` folder with one `.response.txt` per request file ({n['A'][2]} files).
- A file `responses/RUN_META.json` with: your exact model name and version, the date (UTC), the interface or tool you ran in, whether each request was a separate conversation or you worked through the files in one session, and any settings you know (temperature, reasoning effort, output limit).
- A file `responses/NOTES.txt` listing any request you could not complete or had to redo, and nothing else. Do not add commentary on the content of the documents.

If you cannot finish all {n['A'][2]} files in one go, deliver the complete files you have, list the missing request files in `NOTES.txt`, and continue with the remaining files when asked. A partial but exact delivery is acceptable; an abridged translation is not.
"""
    open(os.path.join(P, "TASK_FOR_LLM.md"), "w", encoding="utf-8", newline="\n").write(task)
    cs = f"""# Zadání překladu (v12, balík z {a.date}, prompt v1.1)

## Co je v archivu
- `TASK_FOR_LLM.md` : zadání pro druhé LLM (anglicky). Dáš mu ho spolu s archivem.
- `SYSTEM_PROMPT_translation.md` : pravidla překladu (prompt v1.1, SHA-256 {h[:8]}…{h[-6:]}).
- `requests/A_evidence/` : {n['A'][2]} požadavků pro {n['A'][1]} dokumentů evidence, {n['A'][3]:,} znaků. Tohle se překládá teď.
- `requests/B_recheck_later/` : {n['B'][2]} požadavků pro {n['B'][1]} dokumentů RECHECK. Až po tvém rozhodnutí ve workbooku.
- `requests/BENCH_quality_check/` : {n['BENCH'][2]} požadavků pro {n['BENCH'][1]} dokumentů, kde máme i anglické vydání vydavatele. Slouží jen k měření kvality překladu (doporučuji pustit stejným modelem po dávce A).
- `TRANSLATION_QUEUE_{a.date}.xlsx` : fronta ({len(Q)} dokumentů) + výsledek kontroly anglických vydání + seznam stažených anglických vydání. {n['RB'][0]} dokumentů priority RB se nepřekládá (evidence je anglické vydání).
- `responses/RUN_NAME_example/RUN_META.json` : šablona záznamu o běhu.

Bez připraveného požadavku: {', '.join(q['doc_key'] + ' (' + q['input_mode'] + ')' for q in notext) or 'nic'}. Sken potřebuje OCR nebo nahrát PDF přímo do modelu se stejným promptem.

## Tři způsoby, od nejlepšího
1. **API (doporučeno, čistá volání).** `OPENAI_API_KEY=… python3 scripts/translation/translate_api.py --pack <složka> --date {a.date} --provider openai --model <id> --run <jméno běhu> --priority A`. Každý požadavek je samostatné volání bez historie; skript ukládá odpovědi i metadata. Zkouška: `--only KZ_CAND-152`.
2. **Playground.** System message = celý `SYSTEM_PROMPT_translation.md`. Pro každý soubor nová konverzace, vložit obsah souboru, odpověď uložit beze změny jako `responses/<běh>/<doc_key>/<stejné jméno>.response.txt`. Vhodné na zkoušku nebo pár dokumentů, {n['A'][2]} ručních kroků je moc.
3. **Druhé LLM s nahraným archivem (agent / chat se soubory).** Nahraj zip a jako pokyn vlož `TASK_FOR_LLM.md`. Model vrátí `responses.zip`; rozbal ho do `responses/<jméno běhu>/`. Pozor: v tomto režimu model vidí víc souborů v jedné relaci, takže to není „jedno čisté volání na požadavek". Zadání mu to zakazuje využívat a v `RUN_META.json` to musí být přiznané (`one_request_per_conversation: no`); v článku to pak uvedeme jako omezení. Chatové modely také rády zkracují dlouhé texty; kontrolní skript to odhalí podle značek stran a délky.

## Po překladu (vždy)
`python3 scripts/translation/ingest_translations.py --pack <složka> --date {a.date} --run <jméno běhu>`
Zkontroluje hlavičku, značky stran, koncový řádek, prázdné strany, poměr délky a podíl nepřeloženého textu; složí `translations/<běh>/<doc_key>.en.txt` a zapíše `data/translation/TRANSLATION_MANIFEST_<běh>.csv` s řetězcem hashů zdroj → požadavek → odpověď → anglický text. Odpovědi neopravuj ručně; vadný kus se pouští znovu.

Hash model nepočítá, jen opisuje hash zdroje z hlavičky; všechny hashe počítají skripty z uložených souborů.
"""
    open(os.path.join(P, "ZADANI_cs.md"), "w", encoding="utf-8", newline="\n").write(cs)
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill
    from openpyxl.utils import get_column_letter
    wb = Workbook(); ws = wb.active; ws.title = "QUEUE"; hdr = list(Q[0].keys()); ws.append(hdr)
    col = {"A": "C6EFCE", "B": "FCE4D6", "BENCH": "DDEBF7", "RB": "D9D9D9"}
    for q in Q:
        ws.append([q[k] for k in hdr]); ws.cell(ws.max_row, 2).fill = PatternFill("solid", fgColor=col[q["priority"]])
        if q["input_mode"] != "text": ws.cell(ws.max_row, 3).fill = PatternFill("solid", fgColor="F8CBAD")
    for i, w in enumerate([34, 8, 11, 5, 7, 6, 22, 12, 9, 7, 6, 9, 7, 60, 50, 18, 60, 10, 60, 60], 1): ws.column_dimensions[get_column_letter(i)].width = w
    for c in ws[1]: c.font = Font(bold=True)
    ws.freeze_panes = "B2"; ws.auto_filter.ref = ws.dimensions
    for name, f in [("ENGLISH_EDITION_CHECK", "data/translation/ROUTE_B_PAIRS.csv"), ("ENGLISH_EDITIONS_HELD", f"data/translation/ENGLISH_EDITIONS_{a.date}.csv")]:
        rows = list(csv.DictReader(open(os.path.join(ROOT, f), encoding="utf-8"))); w2 = wb.create_sheet(name); w2.append(list(rows[0].keys()))
        for r in rows: w2.append(list(r.values()))
        for i in range(1, len(rows[0]) + 1): w2.column_dimensions[get_column_letter(i)].width = 30
        for c in w2[1]: c.font = Font(bold=True)
    wb.save(os.path.join(P, f"TRANSLATION_QUEUE_{a.date}.xlsx"))
    print("pack finished:", {k: v for k, v in n.items()}, "system prompt", h[:12])


if __name__ == "__main__": main()
