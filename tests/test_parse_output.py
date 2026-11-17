"""Strict talk parsers: a malformed response is rejected whole and never becomes a label (audit A4 of 17 Nov 2026)."""
import json, os, sys
import pytest
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts", "talk"))
import parse_output as po

IDS = ["XX_doc:p1:s1", "XX_doc:p1:s2", "XX_doc:p2:s9"]
GOOD1 = "XX_doc:p1:s1\tR\nXX_doc:p1:s2\tN\nXX_doc:p2:s9\tU\nEND"


def row(uid, **kw):
    o = {"unit_id": uid, "voice": "OWN", "aspect": "ANONYMITY", "aspect2": "", "stance": "PROTECTS", "basis": "POLICY", "decision": "CONSIDERED",
         "implementation": "UNTESTED_OR_UNREPORTED", "modality": "FIRM", "modal_term": "will", "anonymity_rejected": False, "low_id_tier": False, "two_statements": False}
    o.update(kw); return json.dumps(o)


def test_l1_good():
    assert po.parse_l1(GOOD1, IDS) == {IDS[0]: "R", IDS[1]: "N", IDS[2]: "U"}


@pytest.mark.parametrize("text", [
    "", "   \n", GOOD1[:-4],                                             # empty; no END
    GOOD1.replace("\tN", "\tX"),                                         # label outside the scale
    GOOD1.replace("XX_doc:p1:s2\tN\n", ""),                              # a unit missing
    GOOD1.replace("XX_doc:p1:s2", "XX_doc:p1:s1"),                       # a unit twice
    GOOD1.replace("XX_doc:p1:s2", "XX_doc:p1:s3"),                       # invented id
    "XX_doc:p1:s2\tN\nXX_doc:p1:s1\tR\nXX_doc:p2:s9\tU\nEND",            # reordered
    "Here are the labels:\n" + GOOD1,                                    # prose before
    GOOD1 + "\nI hope this helps.",                                      # prose after
    GOOD1.replace("\tR", " R"),                                          # no tab
    "I cannot help with that.\nEND",                                     # refusal
])
def test_l1_rejects(text):
    with pytest.raises(po.ParseError): po.parse_l1(text, IDS)


def test_l2_good():
    out = po.parse_l2("\n".join(row(i) for i in IDS) + "\nEND", IDS)
    assert out[IDS[0]]["aspect"] == "ANONYMITY" and out[IDS[2]]["two_statements"] is False


@pytest.mark.parametrize("change", [
    {"voice": "MAYBE"}, {"aspect": "PRIVACY"}, {"aspect2": "ANONYMITY"}, {"stance": ""}, {"decision": "REJECTED"},
    {"implementation": None}, {"modality": "firm"}, {"low_id_tier": "false"}, {"modal_term": 3},
])
def test_l2_rejects_values(change):
    with pytest.raises(po.ParseError): po.parse_l2("\n".join([row(IDS[0], **change), row(IDS[1]), row(IDS[2])]) + "\nEND", IDS)


def test_l2_rejects_structure():
    good = [row(i) for i in IDS]
    for text in ("\n".join(good), "\n".join(good[:2]) + "\nEND", "```json\n" + "\n".join(good) + "\n```\nEND",
                 "\n".join([good[0], good[0], good[2]]) + "\nEND", json.dumps({"unit_id": IDS[0]}) + "\nEND"):
        with pytest.raises(po.ParseError): po.parse_l2(text, IDS)
