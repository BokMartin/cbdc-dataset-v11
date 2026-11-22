"""A sentence cut by a page break becomes one unit (MB, 22 Nov 2026); nothing else moves."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts", "units"))
from unitise import units_of  # noqa: E402


def _doc(*pages):
    return "".join(f"=== PAGE {i} ===\n{t}\n" for i, t in enumerate(pages, 1))


def test_sentence_across_a_page_break_is_joined():
    text = _doc("The central bank will not see the identity of users because the data on\n",
                "payments stay with the intermediaries. Offline payments are planned for later.\n")
    joined, _ = units_of(text)
    old, _ = units_of(text, join_pages=False)
    assert len(old) == 3 and len(joined) == 2
    p, para, k, s, pe = joined[0]
    assert (p, k, pe) == ("1", 1, "2") and s.endswith("data on payments stay with the intermediaries.")
    assert joined[1][2] == 3 and joined[1][3] == "Offline payments are planned for later."  # identifiers do not shift


def test_hyphen_footnote_and_finished_sentences():
    text = _doc("Users can hold the digital euro without the central bank seeing their pay-\n\n12 See the Opinion of the EDPB on this question.\n",
                "ments at any time. Next sentence here is fine.\n",
                "This page ends with a full sentence.\n",
                "Another page starts with a capital letter and stays apart.\n")
    u, _ = units_of(text)
    assert any(x[3].endswith("seeing their payments at any time.") and x[4] == "2" for x in u)
    assert any(x[3].startswith("12 See the Opinion") for x in u)  # the footnote stays a unit of its own
    assert any(x[3] == "Another page starts with a capital letter and stays apart." for x in u)


def test_heading_or_short_fragment_is_not_joined():
    text = _doc("Long paragraph that ends properly here.\n\nPrivacy\n", "and data protection are discussed below in detail.\n")
    u, _ = units_of(text)
    assert len(u) == 3 and all(x[0] == x[4] for x in u)
