"""The website data: current, nothing beyond the corpus, translations only as listed under ADR-008."""
import csv, json, os, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load(name):
    with open(os.path.join(ROOT, "site", "assets", name), encoding="utf-8") as f:
        return json.load(f)


def test_site_data_is_current():
    r = subprocess.run([sys.executable, "scripts/site/build_site_data.py", "--check"], cwd=ROOT, capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr


def test_every_document_of_the_manifest_is_listed_once():
    tiers = list(csv.DictReader(open(os.path.join(ROOT, "data", "manifest", "TIERS_2026-11-17.csv"), encoding="utf-8")))
    ids = [d["id"] for d in load("documents.json")["documents"]]
    assert sorted(ids) == sorted(t["id"] for t in tiers)


def test_frame_is_44_projects_and_counts_match_brief():
    projects = load("projects.json")["projects"]
    frame = [p for p in projects if p["frame"]]
    assert len(frame) == 44
    assert sum(p["pubs"] for p in frame) == 229  # evidence publications, PROJECT_BRIEF section 3


def test_no_measurement_fields_leak():
    banned = {"cells", "type", "y1", "y3", "statements", "posture", "candidates", "units", "label", "primary"}
    for d in load("documents.json")["documents"]:
        assert not banned & set(d)
    for p in load("projects.json")["projects"]:
        assert not banned & set(p)


def test_translations_only_where_listed():
    listed = {r["id"] for r in csv.DictReader(open(os.path.join(ROOT, "data", "site", "PUBLISHED_TRANSLATIONS_2026-11-21.csv"), encoding="utf-8"))}
    shown = {d["id"] for d in load("documents.json")["documents"] if d.get("tr")}
    assert shown == listed
    assert len(os.listdir(os.path.join(ROOT, "site", "translations"))) == len(listed)
