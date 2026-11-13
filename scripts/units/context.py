#!/usr/bin/env python3
"""One context rule for human coders and for the model (audit of 13 Nov 2026, items 13 and 17).

The context of a unit is its PARAGRAPH: all units with the same page and paragraph number, in order, with the unit to code marked
as »…«. If the paragraph is longer than `limit` characters, whole units are dropped from its far ends until it fits; the unit to
code and its direct neighbours always stay. A unit that is alone in its paragraph (headings, table cells) has no context.
Both the coders' workbook (draw_agreement_sample.py) and the model requests must call render(); nothing else may build context.
"""
LIMIT = 1500


def render(units, i, limit=LIMIT):
    """units: list of dicts with page, para, text (one document, in order); i: index of the unit to code. Returns the context string."""
    u = units[i]; lo = i
    while lo > 0 and units[lo - 1]["page"] == u["page"] and units[lo - 1]["para"] == u["para"]: lo -= 1
    hi = i
    while hi + 1 < len(units) and units[hi + 1]["page"] == u["page"] and units[hi + 1]["para"] == u["para"]: hi += 1
    if lo == hi: return ""
    size = lambda a, b: sum(len(units[k]["text"]) + 1 for k in range(a, b + 1))
    while size(lo, hi) > limit and (lo < i - 1 or hi > i + 1):
        if (i - lo) >= (hi - i) and lo < i - 1: lo += 1
        elif hi > i + 1: hi -= 1
        else: lo += 1
    return " ".join(("»" + units[k]["text"] + "«") if k == i else units[k]["text"] for k in range(lo, hi + 1))
