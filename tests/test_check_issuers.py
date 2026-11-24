"""Rules of the machine check of issuers (scripts/review/check_issuers.py), without unit texts."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts", "review"))
import check_issuers as c  # noqa: E402


def test_domain_keeps_the_registrable_part():
    assert c.domain("https://www.bankofengland.co.uk/paper/2023/x") == "bankofengland.co.uk"
    assert c.domain("https://haldus.eestipank.ee/sites/x.pdf") == "eestipank.ee"
    assert c.domain("https://www.boj.or.jp/en/x") == "boj.or.jp"


def test_name_keys_and_search():
    k = c.name_keys("Sveriges Riksbank")
    assert c.found(k, "The Riksbank's e-krona project")
    assert c.found(c.name_keys("Reserve Bank of New Zealand"), "RBNZ consultation") == "RBNZ"
    assert not c.found({"RBNZ"}, "the rbnzx file")


def test_batch_names_are_not_issuers_and_genre_words_decide_by_title():
    assert c.BATCH.search("wave1_2026-10") and c.BATCH.search("v1_corpus") and not c.BATCH.search("Bank of Jamaica")
    first = lambda t: next((lab for lab, rx, _ in c.KIND_RULES if rx.search(t)), None)
    assert first("Response to the Bank of England and HM Treasury Consultation Paper: The digital pound") == "responses to a consultation"
    assert first("Concept of the platform (with press release of 18 June 2026)") is None
    assert first("BOJ Prepares for CBDC (CBDC Information Press Release 22 March 2021)") == "press release"


def test_same_issuer_ignores_brackets_and_partners():
    assert c.same_issuer("National Bank of Kazakhstan with National Payment Corporation", "National Bank of Kazakhstan")
    assert not c.same_issuer("Bank of Jamaica", "Bank of England")


def test_fixes_refuse_a_stale_old_value_and_update_the_manifest():
    import pytest
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts", "review"))
    import apply_issuer_fixes as af
    led = [{"id": "a", "issuer": "v1_corpus", "issuer_type": "other", "kind": "report", "issuer_source": "x", "check": "issuer is not a central bank"}]
    man = [{"id": "a", "issuer": "v1_corpus", "issuer_type": "other", "kind": "report"}]
    fx = [{"id": "a", "field": "issuer", "old": "v1_corpus", "new": "Bank X"}, {"id": "a", "field": "issuer_type", "old": "other", "new": "central_bank"}]
    led2, man2 = af.apply([dict(r) for r in led], [dict(r) for r in man], fx, "2026-11-23")
    assert man2[0]["issuer"] == "Bank X" and man2[0]["issuer_type"] == "central_bank" and led2[0]["check"] == ""
    with pytest.raises(SystemExit): af.apply([dict(r) for r in led], man, [{"id": "a", "field": "issuer", "old": "wrong", "new": "Y"}], "2026-11-23")
