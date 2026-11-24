#!/usr/bin/env python3
"""Request format and strict response check for the F-cell extraction prompt v12.2 (ADR-013, adopted 23 Nov 2026).

render_request(meta, pages, owned)  the user message: HEADER (the fields of prompt §1), TEXT with `=== PAGE p ===` per page
                                    and one labelled block per paragraph, `[p<page>.b<para>] <text>`, then
                                    `=== END OF REQUEST TEXT ===`. Owned pages are disjoint between requests of one document;
                                    one context page on each side is sent read-only (prompt §2).
blocks_of(user)                     {(page, block_id): text} of a rendered request (the runner re-reads what it sent).
check(text, user)                   the prompt §6 envelope and §4 fields, verified against the request that was sent.
                                    Returns {"state", "problems", "observations", "rejected"}:
                                      state = failed: the request cannot enter derivation (bad envelope, wrong request_id,
                                        coverage not complete, end not seen, a page missing or added, an unreadable page,
                                        an unresolved boundary). Nothing from it is used (prompt §6, audit A4c answer 5).
                                      state = ok_with_validation_problems: the envelope is sound, but some observations
                                        fail a field rule or a quote is not verbatim in its block; those are rejected
                                        one by one, with the reason, and the rest are kept.
                                      state = ok: every observation passed.
Two tolerances (MB, 23 Nov 2026, after the API pilot; prompt unchanged): a response wrapped in exactly one outer Markdown code
fence is read without it (recorded in "notes"); null is read as n/d in modality, basis, legal_state and referenced_law_state
(modality: the prompt §4 row lists it among "concise text or null"; the others after the development round, MB 23 Nov 2026).
A quote passes only if it occurs in the named block of the named page, after collapsing runs of white space; no other
normalisation, no fuzzy match, no match elsewhere (audit A4c answer 5).
"""
import json, re

FIELDS = ["claim_no", "kind", "cell", "asserted_value", "evidence", "decision_status", "implementation_status", "decision_body", "decision_date",
          "endorsement_ref", "basis", "actor", "actor_text", "reference_participant", "transaction_scope", "limits", "modality", "condition",
          "release_horizon", "design_label", "event_date", "retail_or_wholesale", "legal_state", "referenced_law_state", "details", "missing",
          "references", "flags", "justification", "confidence"]
KINDS = {"assertion", "premise", "context", "legal_reference", "status_timeline"}
DECISION = {"considered", "endorsed", "rejected", "superseded", "unclear"}
IMPLEMENTATION = {"untested_or_unreported", "tested", "operational", "unclear"}
BASIS = {"policy", "architectural", "cryptographic", "n/d"}
ACTOR = re.compile(r"^(CB|CB_agent|independent_operator|PSP|user|n/d|public_authority:.+)$")
MODALITY = {"unconditional", "conditional", "n/d"}
FENCE = re.compile(r"```(?:json|JSON)?[ \t]*\n(.*)\n[ \t]*```", re.S)
SCOPE = {"retail", "wholesale", "both", "unknown"}
LEGAL = {"in_force", "adopted_not_effective", "bill", "proposal", "intended", "n/d"}
CONFIDENCE = {"high", "medium", "low"}
FLAGS = {"anonymity_rejected", "analytic_linkability", "balance_reporting", "staff_views_disclaimer", "quote_in_figure_or_table", "translation_uncertain"}
ROLES = {"proposition", "attribution", "qualifier", "reference", "ranking"}
RELATIONS = {"identifies", "cites", "adopts", "replaces", "rejects", "incorporates"}
MISSING_EXTRA = {"authority", "attribution", "project_attribution", "participant", "mode", "design", "translation", "reference_target", "basis"}
BINARY = {"yes", "no", "unspecified", "undecided"}
F11_TAGS = {"payment_modernisation", "financial_inclusion", "monetary_sovereignty", "monetary_policy_transmission", "cash_substitute",
            "payment_resilience", "aml_cft_tax_enforcement", "innovation_competitiveness"}
PET_CODES = {"standard_encryption", "digital_signatures", "blind_signatures", "ring_signatures", "schnorr_signatures", "bbs_plus_signatures",
             "multi_party_computation", "pedersen_commitments", "homomorphic_encryption", "zero_knowledge_proof", "zk_snark", "zk_stark",
             "mixing_privacy_pools", "utxo_model", "secure_hardware", "digital_identity", "two_tier_model", "identity_payment_separation",
             "pseudonymised_settlement", "internal_firewall", "multi_factor_authentication"}
VALUES = {"F1": BINARY, "F2": BINARY | {"mapping", "routine_record", "join_key"}, "F3": {"via_PSP", "via_CB", "via_both", "unspecified"},
          "F4": BINARY, "F7": BINARY, "F8": BINARY, "F9": BINARY, "F10": BINARY,
          "ANONYMITY_STATEMENT": {"rejected", "offered_limited", "offered", "discussed", "undecided"}, "PRIVACY_PRINCIPLE": {"stated"},
          "LEGAL_REFERENCE": {"legal_state_record", "decision_record"}}
F12_VALUES = {"conventional_centralised", "permissioned_DLT", "permissionless_DLT", "hybrid", "undecided", "unspecified"}
MAX_WORDS = 60
END = "=== END OF REQUEST TEXT ==="
HEADER_FIELDS = ["request_id", "doc_key", "project", "issuer", "issuer_type", "decision_authority", "issue_date", "document_type", "layer",
                 "text_route", "text_layer", "pages_total", "page_span", "page_indices", "owned_pages"]


def ws(s): return re.sub(r"\s+", " ", s or "").strip()


def render_request(meta, pages, owned):
    """meta: the header fields except page_indices and owned_pages; pages: {page: [(block_no, text), ...]} of the pages to send
    (owned plus context), in order; owned: the owned page numbers."""
    h = dict(meta, page_indices=json.dumps(sorted(pages)), owned_pages=json.dumps(sorted(owned)))
    body = []
    for p in sorted(pages):
        body.append(f"=== PAGE {p} ===")
        body += [f"[p{p}.b{b}] {ws(t)}" for b, t in pages[p]]
    return "HEADER\n" + "\n".join(f"{k}: {h[k]}" for k in HEADER_FIELDS) + "\n\nTEXT\n" + "\n".join(body) + f"\n{END}\n"


def header_of(user):
    head = user.split("\n\nTEXT\n", 1)[0].split("\n")[1:]
    h = dict(l.split(": ", 1) for l in head)
    for k in ("page_indices", "owned_pages"): h[k] = json.loads(h[k])
    return h


def blocks_of(user):
    out, page = {}, None
    for l in user.split("\n\nTEXT\n", 1)[1].split("\n"):
        m = re.match(r"^=== PAGE (\d+) ===$", l)
        if m: page = int(m.group(1)); continue
        m = re.match(r"^\[(p\d+\.b\d+)\] (.*)$", l)
        if m and page is not None: out[(page, m.group(1))] = m.group(2)
    return out


def _null_or_str(o, k): return o[k] is None or isinstance(o[k], str)


def _check_value(o):
    c, v = o["cell"], o["asserted_value"]
    if not isinstance(c, str) or not isinstance(v, str): return "cell and asserted_value must be strings"
    if o["kind"] == "status_timeline":
        return None if c == "PROJECT_STATUS" and v.strip() else "status_timeline needs cell PROJECT_STATUS and the status phrase"
    if o["kind"] == "legal_reference" and c not in ("F3", "LEGAL_REFERENCE"): return "legal_reference needs cell F3 or LEGAL_REFERENCE"
    if o["kind"] == "premise" and not (c == "F2" and v in ("mapping", "routine_record", "join_key")): return "premise is only F2 mapping, routine_record or join_key"
    if c in VALUES: return None if v in VALUES[c] else f"{c}: value not allowed: {v[:30]!r}"
    if c.startswith("F11 "):
        tag = c[4:]
        if tag == "ranking": return None if v in ("one_primary", "several_joint", "unranked") else "F11 ranking: value not allowed"
        return None if tag in F11_TAGS and v in ("stated", "explicitly_rejected") else "F11: tag or value not allowed"
    if c.startswith("F12 "):
        return None if c[4:] in ("core_ledger", "offline_component", "settlement_layer") and v in F12_VALUES else "F12: component or value not allowed"
    if c == "PET": return None if v in PET_CODES or (v.startswith("other:") and len(v) > 6) else "PET: code not allowed"
    return f"cell not allowed: {c[:30]!r}"


def _check_observation(o, blocks, owned):
    if not isinstance(o, dict): return "observation is not an object"
    if sorted(o) != sorted(FIELDS): return "keys differ from prompt §4: " + ", ".join(sorted(set(o) ^ set(FIELDS))[:5])
    if o["kind"] not in KINDS: return "kind not allowed"
    e = _check_value(o)
    if e: return e
    for k in ("modality", "basis", "legal_state", "referenced_law_state"):   # null where n/d is allowed reads as n/d (MB 23 Nov 2026,
        if o[k] is None: o[k] = "n/d"                                         # pilot and development round)
    for k, allowed in (("decision_status", DECISION), ("implementation_status", IMPLEMENTATION), ("basis", BASIS), ("modality", MODALITY),
                       ("retail_or_wholesale", SCOPE), ("legal_state", LEGAL), ("referenced_law_state", LEGAL), ("confidence", CONFIDENCE)):
        if o[k] not in allowed: return f"{k}: value not allowed: {str(o[k])[:30]!r}"
    if not isinstance(o["actor"], str) or not ACTOR.match(o["actor"]): return "actor not allowed"
    for k in ("decision_body", "decision_date", "actor_text", "reference_participant", "transaction_scope", "limits", "condition",
              "release_horizon", "design_label", "event_date", "justification"):
        if not _null_or_str(o, k): return f"{k}: not a string or null"
    if not isinstance(o["details"], dict): return "details is not an object"
    if not isinstance(o["flags"], list) or set(o["flags"]) - FLAGS: return "flags not allowed"
    if not isinstance(o["missing"], list) or not all(isinstance(x, str) for x in o["missing"]): return "missing is not a list of strings"
    ev = o["evidence"]
    if not isinstance(ev, list) or not ev: return "evidence is empty"
    if not any(isinstance(x, dict) and x.get("role") == "proposition" for x in ev): return "no proposition evidence"
    first = None
    for x in ev:
        if not isinstance(x, dict) or sorted(x) != ["role", "segments"] or x["role"] not in ROLES: return "evidence object malformed"
        if not isinstance(x["segments"], list) or not x["segments"]: return "evidence without segments"
        for s in x["segments"]:
            if not isinstance(s, dict) or sorted(s) != ["block_id", "page_index", "quote"]: return "segment malformed"
            if not isinstance(s["page_index"], int) or isinstance(s["page_index"], bool): return "page_index is not an integer"
            if len(str(s["quote"]).split()) > MAX_WORDS: return f"segment longer than {MAX_WORDS} words"
            b = blocks.get((s["page_index"], s["block_id"]))
            if b is None: return f"block {s['block_id']} is not on page {s['page_index']} of the request"
            if not ws(s["quote"]) or ws(s["quote"]) not in b: return f"quote not verbatim in block {s['block_id']}"
            if x["role"] == "proposition" and first is None: first = s["page_index"]
    if first not in owned: return f"first decisive words on page {first}, which this request does not own"
    r = o["endorsement_ref"]
    if r is not None and (not isinstance(r, int) or isinstance(r, bool) or not 1 <= r <= len(ev)): return "endorsement_ref out of range"
    if o["decision_status"] == "endorsed" and (not o["decision_body"] or r is None): return "endorsed without a named body and located support"
    if not isinstance(o["references"], list): return "references is not a list"
    for x in o["references"]:
        if not isinstance(x, dict) or sorted(x) != ["evidence_ref", "relation", "target_text"] or x["relation"] not in RELATIONS: return "reference malformed"
        if not isinstance(x["evidence_ref"], int) or not 1 <= x["evidence_ref"] <= len(ev): return "reference evidence_ref out of range"
    return None


def check(text, user):
    """See the module docstring."""
    out = {"state": "failed", "problems": [], "observations": [], "rejected": [], "notes": []}
    h = header_of(user); blocks = blocks_of(user); sent = h["page_indices"]; owned = set(h["owned_pages"])
    text = (text or "").strip()
    m = FENCE.fullmatch(text)
    if m: text = m.group(1); out["notes"].append("one outer Markdown code fence removed")   # MB 23 Nov 2026 (API pilot)
    try: o = json.loads(text)
    except Exception: out["problems"].append("response is not one JSON object"); return out
    if not isinstance(o, dict) or sorted(o) != ["claims", "coverage", "doc_key", "request_id"]:
        out["problems"].append("envelope keys differ from prompt §6"); return out
    if o["request_id"] != h["request_id"] or o["doc_key"] != h["doc_key"]: out["problems"].append("request_id or doc_key differs from the request"); return out
    c = o["coverage"]
    if not isinstance(c, dict) or sorted(c) != ["complete", "end_seen", "page_indices_seen", "pending_boundaries", "unreadable_pages"]:
        out["problems"].append("coverage keys differ from prompt §6"); return out
    if c["complete"] is not True: out["problems"].append("coverage.complete is not true")
    if c["end_seen"] is not True: out["problems"].append("end of request text not seen")
    if c["page_indices_seen"] != sent: out["problems"].append(f"pages seen {c['page_indices_seen']} differ from pages sent {sent}")
    if c["unreadable_pages"]: out["problems"].append(f"unreadable pages {c['unreadable_pages']}")
    if c["pending_boundaries"]: out["problems"].append(f"{len(c['pending_boundaries'])} unresolved boundaries")
    if not isinstance(o["claims"], list): out["problems"].append("claims is not a list")
    if out["problems"]: return out
    nos = [x.get("claim_no") if isinstance(x, dict) else None for x in o["claims"]]
    if nos != list(range(1, len(nos) + 1)): out["problems"].append("claim_no is not consecutive from 1"); return out
    for x in o["claims"]:
        e = _check_observation(x, blocks, owned)
        (out["rejected"].append({"claim_no": x.get("claim_no"), "reason": e}) if e else out["observations"].append(x))
    out["state"] = "ok_with_validation_problems" if out["rejected"] else "ok"
    return out
