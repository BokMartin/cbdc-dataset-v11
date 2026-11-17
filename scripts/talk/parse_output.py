#!/usr/bin/env python3
"""Strict parsers for the output of the two talk prompts (audit A4, 17 Nov 2026: F05, question 12, protocol step 7).

A response is either accepted whole or rejected whole with a reason. Nothing is repaired, guessed or defaulted: a malformed response
never becomes an N, a U or an empty facet. The caller records the reason in CALLS.csv (parsed_ok = False, parse_error) and the
request counts as failed.

parse_l1(text, ids)  -> {unit_id: "R"|"N"|"U"}
parse_l2(text, ids)  -> {unit_id: {facet: value, ...}}
Both raise ParseError(reason). `ids` is the list of unit ids of the request, in order. Allowed values come from the schema file.
"""
import json, os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_S = json.load(open(os.path.join(ROOT, "schema", "talk_units_v13_DRAFT.json"), encoding="utf-8"))
L1_VALUES = set(_S["L1_relevance"]["values"])
_F = _S["L2_facets"]
_vals = lambda v: set(v["values"]) if isinstance(v, dict) else set(v)
ENUM = {k: _vals(_F[k]) for k in ("voice", "aspect", "stance", "basis", "decision", "implementation", "modality")}
ENUM["aspect2"] = ENUM["aspect"] | {""}
FLAGS = list(_F["flags"]["values"] if isinstance(_F["flags"], dict) else _F["flags"])
L2_KEYS = ["unit_id", "voice", "aspect", "aspect2", "stance", "basis", "decision", "implementation", "modality", "modal_term"] + FLAGS


class ParseError(ValueError):
    pass


def _lines(text):
    if text is None or not text.strip(): raise ParseError("empty response")
    lines = [l.rstrip("\r") for l in text.strip("\n").split("\n")]
    if lines[-1].strip() != "END": raise ParseError("no END line (truncated, refused or extra text after the output)")
    body = lines[:-1]
    if any(not l.strip() for l in body): raise ParseError("blank line inside the output")
    return body


def _order(got, ids):
    if len(set(ids)) != len(ids): raise ParseError("request lists a unit id twice")
    if len(set(got)) != len(got): raise ParseError("unit id returned twice: " + ", ".join(sorted({g for g in got if got.count(g) > 1})[:3]))
    extra = [g for g in got if g not in set(ids)]; missing = [i for i in ids if i not in set(got)]
    if extra: raise ParseError("unit id not in the request: " + ", ".join(extra[:3]))
    if missing: raise ParseError("unit id missing from the output: " + ", ".join(missing[:3]))
    if got != list(ids): raise ParseError("unit ids not in the order of the request")


def parse_l1(text, ids):
    out, got = {}, []
    for l in _lines(text):
        parts = l.split("\t")
        if len(parts) != 2: raise ParseError(f"line is not <unit_id><TAB><label>: {l[:80]!r}")
        uid, lab = parts
        if lab not in L1_VALUES: raise ParseError(f"label not in {sorted(L1_VALUES)}: {lab[:20]!r}")
        got.append(uid); out[uid] = lab
    _order(got, ids); return out


def parse_l2(text, ids):
    out, got = {}, []
    for l in _lines(text):
        try: o = json.loads(l)
        except Exception: raise ParseError(f"line is not a JSON object: {l[:80]!r}")
        if not isinstance(o, dict): raise ParseError("line is not a JSON object")
        if sorted(o) != sorted(L2_KEYS): raise ParseError("keys differ from the schema: " + ", ".join(sorted(set(o) ^ set(L2_KEYS))[:5]))
        for k, allowed in ENUM.items():
            if not isinstance(o[k], str) or o[k] not in allowed: raise ParseError(f"{k}: value not allowed: {str(o[k])[:30]!r}")
        if o["aspect2"] and o["aspect2"] == o["aspect"]: raise ParseError("aspect2 repeats aspect")
        if not isinstance(o["modal_term"], str): raise ParseError("modal_term is not a string")
        for f in FLAGS:
            if not isinstance(o[f], bool): raise ParseError(f"{f}: not true/false")
        if not isinstance(o["unit_id"], str): raise ParseError("unit_id is not a string")
        got.append(o["unit_id"]); out[o["unit_id"]] = {k: o[k] for k in L2_KEYS if k != "unit_id"}
    _order(got, ids); return out
