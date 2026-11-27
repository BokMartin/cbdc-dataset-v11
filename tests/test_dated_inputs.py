"""Scripts that pick their input by date (latest match of a wildcard) must find one (audit A6, 27 Nov 2026)."""
import glob, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

WILDCARD_INPUTS = [
    "data/manifest/ISSUERS_PROPOSED_*.csv",        # scripts/review/record_issuers.py
    "data/units/UNITS_MANIFEST_*.csv",             # record_issuers.py, update_brief.py
    "data/units/CANDIDATES_*.csv",                 # update_brief.py
    "data/units/UNITS_NOT_UNITISED_*.csv",         # update_brief.py
    "data/manifest/TIERS_*.csv",                   # update_brief.py
    "data/manifest/MASTER_MANIFEST_*.csv",         # update_brief.py
    "data/manifest/COMPANION_LINKS_*.csv",         # update_brief.py
    "data/manifest/MANUAL_DOWNLOADS*.csv",         # scripts/review/check_issuers.py
]


def test_every_wildcard_input_resolves():
    missing = [p for p in WILDCARD_INPUTS if not glob.glob(os.path.join(ROOT, p))]
    assert not missing, f"no file matches {missing}"


def test_archive_index_is_current():
    import subprocess, sys
    r = subprocess.run([sys.executable, os.path.join(ROOT, "scripts/provenance/build_archive_index.py"), "--check"], capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
