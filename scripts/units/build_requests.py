#!/usr/bin/env python3
"""DRAFT (17 Nov 2026, not adopted): the user message of a talk request, in the two forms that calibration will compare.

single(units, i)        one unit per request; context = context.render(), the same string the human coders saw.
page(units, idx)        all candidate units of one page in one request; every paragraph is sent once and each unit to code is
                        marked inside it as »[unit_id] text«. Paragraphs longer than context.LIMIT are cut by the rule of render()
                        around each marked unit and the overlapping windows are merged.
Both end with the list CODE (unit ids in document order). The system prompt is the file in pipeline/prompts/, unchanged.
The form used in production is fixed by the authors after the packing test (ADR-006 B.1).
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from context import LIMIT, render


def single(units, i, header=""):
    u = units[i]; ctx = render(units, i) or ("»" + u["text"] + "«")
    return (header + "\n\n" if header else "") + f"UNIT {u['unit_id']}\n{ctx}\n\nCODE\n{u['unit_id']}\n"


def _window(units, i, limit):
    u = units[i]; lo = hi = i
    while lo > 0 and units[lo - 1]["page"] == u["page"] and units[lo - 1]["para"] == u["para"]: lo -= 1
    while hi + 1 < len(units) and units[hi + 1]["page"] == u["page"] and units[hi + 1]["para"] == u["para"]: hi += 1
    size = lambda a, b: sum(len(units[k]["text"]) + 1 for k in range(a, b + 1))
    while size(lo, hi) > limit and (lo < i - 1 or hi > i + 1):
        if (i - lo) >= (hi - i) and lo < i - 1: lo += 1
        elif hi > i + 1: hi -= 1
        else: lo += 1
    return lo, hi


def page(units, idx, header="", limit=LIMIT):
    """idx: indices of the units to code, all on one page, in document order."""
    assert len({units[i]["page"] for i in idx}) == 1, "one page per request"
    keep = set(); mark = set(idx)
    for i in idx:
        lo, hi = _window(units, i, limit); keep.update(range(lo, hi + 1))
    out, prev = [], None
    for k in sorted(keep):
        if prev is not None and (k != prev + 1 or units[k]["para"] != units[prev]["para"]): out.append("\n")
        out.append((f"»[{units[k]['unit_id']}] {units[k]['text']}«" if k in mark else units[k]["text"]) + " "); prev = k
    body = "".join(out).replace(" \n", "\n\n").strip()
    return (header + "\n\n" if header else "") + f"PAGE {units[idx[0]]['page']}\n{body}\n\nCODE\n" + "\n".join(units[i]["unit_id"] for i in idx) + "\n"
