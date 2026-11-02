#!/usr/bin/env python3
"""Export every prompt the pipeline sends to a model, fully rendered, into pipeline/prompts/ with SHA-256 hashes (pipeline/PROMPTS.json).

The prompts are generated from the contract and the schema by the scripts (extract_api.build_prompts, endorsement_census.SYSTEM,
posture_survey.SYSTEM); this export is the human-readable, versioned copy so that the whole procedure can be re-run from the
repository by any provider's API without reading Python. tests/test_prompt_export.py fails when the export drifts from the code.

usage: export_prompts.py --contract docs/<contract>.md --schema schema/<cells>.json [--out pipeline]
"""
import argparse, hashlib, json, os, sys, datetime as dt
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "scripts", "extraction")); sys.path.insert(0, os.path.join(ROOT, "scripts", "census"))
from extract_api import build_prompts
import endorsement_census, posture_survey

def sha(s): return hashlib.sha256(s.encode("utf-8")).hexdigest()

def render(contract_path, schema_path):
    contract = open(contract_path, encoding="utf-8").read(); schema = json.load(open(schema_path))
    P = build_prompts(schema, contract)
    out = {"extraction_stage1.system": P["stage1"], "extraction_stage2_synthesis.system": P["stage2"], "extraction_single.system": P["single"],
           "endorsement_census.system": endorsement_census.SYSTEM + contract, "posture_survey.system": posture_survey.SYSTEM}
    meta = {"rendered_utc": dt.datetime.now(dt.timezone.utc).isoformat(), "contract": os.path.relpath(contract_path, ROOT), "contract_sha256": sha(contract),
            "schema": os.path.relpath(schema_path, ROOT), "schema_sha256": sha(open(schema_path, encoding="utf-8").read()),
            "prompts": {k: {"file": f"prompts/{k}.md", "sha256": sha(v), "chars": len(v)} for k, v in out.items()},
            "user_message_formats": {
                "extraction_stage1": "PROJECT <jur>, DOCUMENT <n> [<doc_id>] ... followed by the page-delimited text (=== DOC n PAGE p ===)",
                "extraction_stage2_synthesis": "document list (doc, doc_id, title, year, kind, staff flag) + JSON array of stage-1 findings",
                "extraction_single": "PROJECT <jur>\\n\\nDOCUMENTS:\\n<list>\\n\\n########## DOCUMENT n [doc_id] ########## + page-delimited texts of all core documents",
                "endorsement_census": "same as extraction_single (all core documents of one project)",
                "posture_survey": "PROJECT <jur>, DOCUMENT <n> [<doc_id>], year, kind, lang + page-delimited text of one document"},
            "provider_settings": {"anthropic": "messages.stream, max_tokens per stage (32000 extraction, 4000 census, 16000-40000 survey); temperature not settable", "openai": "chat.completions, temperature 0"},
            "note": "Every real run also archives the exact request text (requests/*.txt.gz) and the response; these exports are the rendered prompts for reading and for re-running elsewhere."}
    return out, meta

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--contract", required=True); ap.add_argument("--schema", required=True); ap.add_argument("--out", default=os.path.join(ROOT, "pipeline"))
    a = ap.parse_args(); out, meta = render(a.contract, a.schema); os.makedirs(os.path.join(a.out, "prompts"), exist_ok=True)
    for k, v in out.items(): open(os.path.join(a.out, "prompts", k + ".md"), "w", encoding="utf-8").write(v)
    json.dump(meta, open(os.path.join(a.out, "PROMPTS.json"), "w"), indent=1); print(json.dumps({k: v["sha256"][:12] for k, v in meta["prompts"].items()}, indent=1))
