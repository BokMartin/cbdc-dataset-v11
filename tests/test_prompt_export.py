import json, os, sys, hashlib
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.join(ROOT, "scripts", "pipeline"))
from export_prompts import render

def test_exported_prompts_match_code():
    meta = json.load(open(os.path.join(ROOT, "pipeline", "PROMPTS.json")))
    out, fresh = render(os.path.join(ROOT, meta["contract"]), os.path.join(ROOT, meta["schema"]))
    for k, v in out.items():
        f = os.path.join(ROOT, "pipeline", "prompts", k + ".md")
        assert os.path.exists(f), k
        assert hashlib.sha256(open(f, encoding="utf-8").read().encode()).hexdigest() == meta["prompts"][k]["sha256"] == fresh["prompts"][k]["sha256"], f"prompt export drifted: {k}"
