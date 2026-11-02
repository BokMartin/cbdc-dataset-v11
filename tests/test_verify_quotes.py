"""Validity tests for the citation checker (ADR-001 E17): the reviewer's synthetic counterexample must fail now."""
import csv, os, subprocess, sys, tempfile
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = "The Bank would receive payment messages in anonymised form. " * 6 + "The bank cannot link transactions to people. Next sentence here."

def run(quote, page=1, value="no"):
    d = tempfile.mkdtemp(); os.makedirs(os.path.join(d, "texts"))
    open(os.path.join(d, "texts", "doc01.txt"), "w").write("### DOC 1\n\n=== DOC 1 PAGE 1 ===\n" + SRC + "\n\n=== DOC 1 PAGE 2 ===\nOther page text. Footer line\n")
    open(os.path.join(d, "DOCS.csv"), "w").write("doc,doc_id,file\n1,T_1,texts/doc01.txt\n")
    fill = os.path.join(d, "FILL.csv")
    with open(fill, "w", newline="") as f:
        w = csv.writer(f); w.writerow(["cell", "value", "doc", "page", "quote"]); w.writerow(["F1 CB_LINK_ONLINE", value, 1, page, quote])
    subprocess.run([sys.executable, "-I", os.path.join(ROOT, "scripts/extraction/verify_quotes.py"), fill, d], check=True, capture_output=True)
    return list(csv.DictReader(open(fill.replace(".csv", ".verified.csv"))))[0]["quote_verified"]

def test_exact(): assert run("The bank cannot link transactions to people.") == "exact_page"
def test_false_suffix_rejected():
    # same long prefix, reversed final claim (the consultation's probe) — v1 returned exact_page
    q = "The Bank would receive payment messages in anonymised form. " * 6 + "The bank can link transactions to people."
    assert run(q) in ("fuzzy_candidate", "invalid")
def test_wrong_page(): assert run("The bank cannot link transactions to people.", page=2) == "elsewhere_in_doc"
def test_invalid(): assert run("Completely different sentence about offline wallets.") == "invalid"
def test_empty_with_value(): assert run("", value="no") == "empty_but_value_set"
