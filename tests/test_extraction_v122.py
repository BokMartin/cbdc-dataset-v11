"""Offline tests of the v12.2 request format, the strict response check and the claim-to-cell reducer (ADR-013, audit A4c
answer 12). Synthetic text only; no model call."""
import copy
import json
import os
import sys

HERE = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
sys.path.insert(0, os.path.join(HERE, "..", "scripts", "extraction"))
import v122  # noqa: E402
import reduce_v122 as rd  # noqa: E402
from derive import admissible  # noqa: E402
from derive_index import CORE, committed, privacy_index  # noqa: E402

TEXT = {1: [(1, "Cover page.")], 2: [(1, "Introduction to the digital currency.")],
        3: [(1, "The central bank will not be able to see who pays whom."), (2, "Wallets are opened at banks.")],
        4: [(1, "Offline payments will be private, as cash is."), (2, "The intermediary keeps the records.")],
        5: [(1, "Annex.")]}
META = {"request_id": "NO-01:p3-4", "doc_key": "NO-01", "project": "NO", "issuer": "Norges Bank", "issuer_type": "central_bank",
        "decision_authority": "unknown", "issue_date": "2025", "document_type": "report", "layer": "official", "text_route": "A",
        "text_layer": "reading_order", "pages_total": "5", "page_span": "whole_document"}


def request(owned=(3, 4), rid="NO-01:p3-4"):
    send = {p: TEXT[p] for p in range(min(owned) - 1, max(owned) + 2) if p in TEXT}
    return v122.render_request(dict(META, request_id=rid), send, list(owned))


def obs(no, cell, value, page=3, block=1, quote=None, dec="endorsed", impl="untested_or_unreported", basis="architectural", scope="retail",
        kind="assertion", flags=(), missing=(), event_date=None, details=None, participant=None, tscope=None, design=None):
    quote = quote if quote is not None else dict(TEXT.get(page, [(1, "x")])).get(block, "x")
    return {"claim_no": no, "kind": kind, "cell": cell, "asserted_value": value,
            "evidence": [{"role": "proposition", "segments": [{"page_index": page, "block_id": f"p{page}.b{block}", "quote": quote}]}],
            "decision_status": dec, "implementation_status": impl, "decision_body": "Executive Board" if dec == "endorsed" else None,
            "decision_date": None, "endorsement_ref": 1 if dec == "endorsed" else None, "basis": basis, "actor": "CB", "actor_text": None,
            "reference_participant": participant, "transaction_scope": tscope, "limits": None, "modality": "unconditional", "condition": None,
            "release_horizon": None, "design_label": design, "event_date": event_date, "retail_or_wholesale": scope, "legal_state": "n/d",
            "referenced_law_state": "n/d", "details": details or {}, "missing": list(missing), "references": [], "flags": list(flags),
            "justification": None, "confidence": "high"}


def response(claims, user, **cov):
    h = v122.header_of(user)
    c = {"page_indices_seen": h["page_indices"], "unreadable_pages": [], "pending_boundaries": [], "end_seen": True, "complete": True}
    c.update(cov)
    return json.dumps({"request_id": h["request_id"], "doc_key": h["doc_key"], "claims": claims, "coverage": c})


# ---------- request format and parser ----------

def test_render_and_read_back():
    u = request()
    h = v122.header_of(u)
    assert h["page_indices"] == [2, 3, 4, 5] and h["owned_pages"] == [3, 4] and h["request_id"] == "NO-01:p3-4"
    assert v122.blocks_of(u)[(3, "p3.b1")] == "The central bank will not be able to see who pays whom."
    assert u.rstrip().endswith(v122.END) and "=== PAGE 2 ===" in u


def test_clean_response_ok():
    u = request()
    r = v122.check(response([obs(1, "F1", "no"), obs(2, "F4", "yes", page=4)], u), u)
    assert r["state"] == "ok" and len(r["observations"]) == 2 and not r["rejected"]


def test_false_complete_payload_with_unreadable_owned_page_fails():
    """A4c fixture 3, parser half: every expected id, normal ending, but an owned page unreadable -> the request is unusable."""
    u = request(owned=(3, 4, 5), rid="NO-01:p3-5")
    r = v122.check(response([obs(1, "F1", "no")], u, unreadable_pages=[5]), u)
    assert r["state"] == "failed" and not r["observations"]


def test_page_swap_or_omission_fails():
    u = request()
    assert v122.check(response([], u, page_indices_seen=[2, 4, 3, 5]), u)["state"] == "failed"
    assert v122.check(response([], u, page_indices_seen=[2, 3, 5]), u)["state"] == "failed"
    assert v122.check(response([], u, end_seen=False), u)["state"] == "failed"
    assert v122.check(response([], u, complete=False), u)["state"] == "failed"
    assert v122.check(response([], u, pending_boundaries=[{"page": 4}]), u)["state"] == "failed"


def test_envelope_and_request_id():
    u = request()
    good = json.loads(response([], u))
    assert v122.check(json.dumps(dict(good, extra=1)), u)["state"] == "failed"
    assert v122.check(json.dumps(dict(good, request_id="NO-01:p1-2")), u)["state"] == "failed"
    assert v122.check("not json", u)["state"] == "failed"
    assert v122.check(json.dumps(dict(good, claims=[obs(2, "F1", "no")])), u)["state"] == "failed"  # claim_no not from 1


def test_quote_must_be_verbatim_in_its_block():
    u = request()
    bad_quote = obs(1, "F1", "no", quote="The central bank cannot see who pays whom.")
    wrong_block = obs(2, "F1", "no", page=3, block=2, quote="The central bank will not be able to see who pays whom.")
    ok = obs(3, "F4", "yes", page=4, quote="Offline payments  will be\nprivate")  # white space collapses, nothing else
    r = v122.check(response([bad_quote, wrong_block, ok], u), u)
    assert r["state"] == "ok_with_validation_problems" and [o["claim_no"] for o in r["observations"]] == [3]
    assert all("not verbatim" in x["reason"] for x in r["rejected"])


def test_first_proposition_on_context_page_rejected_and_field_rules():
    u = request()
    ctx = obs(1, "F1", "no", page=2, quote="Introduction")  # page 2 is context only
    endorsed_unlocated = dict(obs(2, "F1", "no"), endorsement_ref=None)
    long_quote = obs(3, "F1", "no", quote=" ".join(["word"] * 61))
    bad_enum = dict(obs(4, "F1", "no"), basis="legal")
    r = v122.check(response([ctx, endorsed_unlocated, long_quote, bad_enum], u), u)
    assert r["state"] == "ok_with_validation_problems" and not r["observations"] and len(r["rejected"]) == 4
    assert "does not own" in r["rejected"][0]["reason"] and "endorsed" in r["rejected"][1]["reason"]


# ---------- reducer ----------

DOCS = {"NO-01": {"doc_key": "NO-01", "project": "NO", "layer": "official", "text_route": "A", "issue_date": "2023-05-01"},
        "NO-02": {"doc_key": "NO-02", "project": "NO", "layer": "official", "text_route": "D", "issue_date": "2025-03-01"},
        "NO-W": {"doc_key": "NO-W", "project": "NO", "layer": "wholesale_context", "text_route": "A", "issue_date": "2025-06-01"},
        "NO-S": {"doc_key": "NO-S", "project": "NO", "layer": "staff_research", "text_route": "A", "issue_date": "2025-06-01"},
        "NO-L": {"doc_key": "NO-L", "project": "NO", "layer": "companion_legal", "text_route": "A", "issue_date": "2025-06-01"},
        "NO-J": {"doc_key": "NO-J", "project": "NO", "layer": "inclined_joint_retail", "text_route": "A", "issue_date": "2025-06-01"}}


def req(doc, observations, owned=(1,), state="ok", rid=None):
    return {"request_id": rid or f"{doc}:p{owned[0]}-{owned[-1]}", "doc_key": doc, "owned_pages": list(owned), "state": state,
            "observations": observations, "model": "test"}


def protective_set(doc="NO-01"):
    return [obs(1, "F1", "no"), obs(2, "F2", "no"), obs(3, "F4", "yes"), obs(4, "F7", "yes"), obs(5, "F8", "no"), obs(6, "F9", "no"), obs(7, "F10", "no")]


def test_fixture1_f3_and_pet_never_move_the_intervals():
    """A4c fixture 1 through the reducer: seven protective documented values; F3 via_PSP, via_CB, none_stated (closed search),
    and a PET insertion: both intervals stay [1, 1], only the F3 category changes."""
    rows = []
    for f3 in ("via_PSP", "via_CB", None):
        o = protective_set() + ([obs(8, "F3", f3)] if f3 else [])
        rows.append(rd.reduce_project("NO", {"NO-01": DOCS["NO-01"]}, [req("NO-01", o)]))
    pet = protective_set() + [obs(8, "PET", "blind_signatures")]
    rows.append(rd.reduce_project("NO", {"NO-01": DOCS["NO-01"]}, [req("NO-01", pet)]))
    cats = []
    for r in rows:
        ix = privacy_index(r["cells"])
        for k in ("stated", "admissible", "core4_stated", "core4_admissible"):
            assert (ix[k]["lower"], ix[k]["upper"]) == (1, 1), (k, ix[k])
        cats.append(ix["F3"]["value"])
    assert cats == ["via_psp", "via_cb", "none_stated", "none_stated"] and rows[3]["pet"][0]["code"] == "blind_signatures"
    assert rows[2]["cells"]["F3"]["derivation"] == "inferred" and rows[2]["search_closed"]


def test_fixture2_newer_route_d_decision_wins_and_no_d_view_reexposes_a():
    """A4c fixture 2: older eligible A document says F1 yes; newer D-only decision says F1 no; a wholesale test of the same
    project says F1 no and must never supply the retail value."""
    a = req("NO-01", [obs(1, "F1", "yes")])
    d = req("NO-02", [obs(1, "F1", "no")])
    w = req("NO-W", [obs(1, "F1", "no", scope="wholesale", impl="tested", dec="considered")])
    main = rd.reduce_project("NO", DOCS_AD := {k: DOCS[k] for k in ("NO-01", "NO-02", "NO-W")}, [a, d, w])
    assert main["cells"]["F1"]["value"] == "no" and main["cells"]["F1"]["document_id"] == "NO-02"
    assert main["cells"]["F1"]["counter_evidence"] == ["NO-01:p1-1#1"]
    no_d = rd.reduce_project("NO", DOCS_AD, [a, d, w], drop_route_d=True)
    assert no_d["cells"]["F1"]["value"] == "yes" and no_d["cells"]["F1"]["document_id"] == "NO-01"
    alone = rd.reduce_project("NO", DOCS_AD, [w])  # the wholesale test alone: no retail value, not even as a fallback
    assert alone["cells"]["F1"]["value"] == "" and alone["cells"]["F1"]["evidence_state"] == "unknown"
    assert any(x["use"].startswith("wholesale") for x in alone["ledger"])


def test_fixture3_unreadable_page_request_unusable_replacement_contributes_search_stays_open():
    failed = req("NO-01", [obs(1, "F1", "no")], owned=(3, 4, 5), state="failed", rid="NO-01:p3-5")
    replacement = req("NO-01", [obs(1, "F4", "yes", page=4)], owned=(3, 4), rid="NO-01:p3-4")
    r = rd.reduce_project("NO", {"NO-01": DOCS["NO-01"]}, [failed, replacement])
    assert r["cells"]["F1"]["evidence_state"] == "unknown" and r["cells"]["F1"]["unknown_reason"] == "search_incomplete"
    assert r["cells"]["F4"]["value"] == "yes" and not r["search_closed"] and "[5]" in r["gaps"][0]
    assert r["cells"]["F3"]["value"] == ""  # no none_stated from an open search


def test_policy_only_protective_value_sets_nothing():
    r = rd.reduce_project("NO", {"NO-01": DOCS["NO-01"]}, [req("NO-01", [obs(1, "F1", "no", basis="policy"), obs(2, "F7", "yes", basis="policy")])])
    assert r["cells"]["F1"]["value"] == "" and r["cells"]["F1"]["unknown_reason"] == "policy_only"
    assert r["cells"]["F7"]["value"] == "yes"  # F7 is not under the basis rule


def test_f2_inference_needs_the_same_participant_scope_and_design():
    same = dict(participant="PSP", tscope="online retail", design="v1")
    prem = [obs(1, "F2", "mapping", kind="premise", **same), obs(2, "F2", "routine_record", kind="premise", **same),
            obs(3, "F2", "join_key", kind="premise", **same)]
    r = rd.reduce_project("NO", {"NO-01": DOCS["NO-01"]}, [req("NO-01", prem)])
    assert r["cells"]["F2"]["value"] == "yes" and r["cells"]["F2"]["derivation"] == "inferred"
    cross = copy.deepcopy(prem); cross[2]["design_label"] = "v2"
    r = rd.reduce_project("NO", {"NO-01": DOCS["NO-01"]}, [req("NO-01", cross)])
    assert r["cells"]["F2"]["value"] == ""


def test_opposite_claims_of_equal_standing_conflict():
    r = rd.reduce_project("NO", {"NO-01": DOCS["NO-01"]}, [req("NO-01", [obs(1, "F9", "no"), obs(2, "F9", "yes", page=4)])])
    c = r["cells"]["F9"]
    assert c["evidence_state"] == "conflict" and c["value"] == "" and len(c["claim_ids"]) == 2
    assert not committed(c, "F9")


def test_higher_status_beats_newer_lower_status():
    a = req("NO-01", [obs(1, "F7", "yes", impl="operational")])
    d = req("NO-02", [obs(1, "F7", "no", dec="considered")])
    r = rd.reduce_project("NO", {k: DOCS[k] for k in ("NO-01", "NO-02")}, [a, d])
    assert r["cells"]["F7"]["value"] == "yes"


def test_f3_routes_combine_and_none_stated_only_when_closed():
    r = rd.reduce_project("NO", {"NO-01": DOCS["NO-01"]}, [req("NO-01", [obs(1, "F3", "via_PSP"), obs(2, "F3", "via_CB", page=4)])])
    assert r["cells"]["F3"]["value"] == "via_both" and committed(r["cells"]["F3"], "F3")
    open_ = rd.reduce_project("NO", {"NO-01": DOCS["NO-01"]}, [req("NO-01", [], owned=(1, 2)), req("NO-01", [], owned=(3,), state="failed")])
    assert open_["cells"]["F3"]["value"] == "" and open_["cells"]["F3"]["unknown_reason"] == "search_incomplete"


def test_companion_legal_f3_goes_to_the_statutory_column_only():
    lr = obs(1, "F3", "via_PSP", kind="legal_reference")
    r = rd.reduce_project("NO", {k: DOCS[k] for k in ("NO-01", "NO-L")}, [req("NO-01", []), req("NO-L", [lr])])
    assert r["statutory_F3"] and r["statutory_F3"][0]["value"] == "via_PSP"
    assert r["cells"]["F3"]["value"] == "none_stated"  # the maker's own documents state no route


def test_leaning_only_without_an_official_value_and_never_committed():
    j = req("NO-J", [obs(1, "F4", "yes")])
    r = rd.reduce_project("NO", {k: DOCS[k] for k in ("NO-01", "NO-J")}, [req("NO-01", []), j])
    c = r["cells"]["F4"]
    assert c["value"] == "yes" and c["leaning"] == "true" and not committed(c, "F4") and not admissible(c, cell_id="F4")
    ix = privacy_index(r["cells"])
    assert ix["stated"]["components"]["F4"] is None and ix["stated_with_leaning"]["components"]["F4"] == 1
    r = rd.reduce_project("NO", {k: DOCS[k] for k in ("NO-01", "NO-J")}, [req("NO-01", [obs(1, "F4", "no")]), j])
    assert r["cells"]["F4"]["value"] == "no" and r["cells"]["F4"]["leaning"] == ""


def test_staff_research_never_establishes():
    r = rd.reduce_project("NO", {k: DOCS[k] for k in ("NO-01", "NO-S")}, [req("NO-01", []), req("NO-S", [obs(1, "F1", "no")])])
    assert r["cells"]["F1"]["value"] == "" and r["cells"]["F1"]["unknown_reason"] == "never_addressed"
    assert any("staff research" in x["use"] for x in r["ledger"])


def test_route_d_translation_uncertain_is_partial():
    r = rd.reduce_project("NO", {"NO-02": DOCS["NO-02"]}, [req("NO-02", [obs(1, "F8", "no", flags=["translation_uncertain"])])])
    c = r["cells"]["F8"]
    assert c["value"] == "no" and c["evidence_state"] == "partial" and not committed(c, "F8")
    assert any("source check pending" in p for p in c["problems"])


def test_missing_basis_or_qualifier_is_partial():
    r = rd.reduce_project("NO", {"NO-01": DOCS["NO-01"]}, [req("NO-01", [obs(1, "F9", "no", basis="n/d"), obs(2, "F10", "no", missing=["mode"])])])
    assert r["cells"]["F9"]["evidence_state"] == "partial" and r["cells"]["F10"]["evidence_state"] == "partial"


def test_offline_explicitly_excluded_is_na():
    r = rd.reduce_project("NO", {"NO-01": DOCS["NO-01"]}, [req("NO-01", [obs(1, "F4", "no", details={"offline_mode": "explicitly_excluded"})])])
    assert r["cells"]["F4"]["evidence_state"] == "n.a." and r["cells"]["F4"]["value"] == ""


def test_rejected_and_superseded_never_set_a_value_and_superseded_field_is_a_string():
    r = rd.reduce_project("NO", {"NO-01": DOCS["NO-01"]}, [req("NO-01", [obs(1, "F7", "yes", dec="rejected"), obs(2, "F1", "no")])])
    assert r["cells"]["F7"]["value"] == ""
    assert r["cells"]["F1"]["superseded"] == "" and isinstance(r["cells"]["F1"]["superseded"], str)
    assert committed(r["cells"]["F1"], "F1")
    # A legacy boolean in the superseded field: derive.admissible() reads any non-empty text, so False (text "False") blocks
    # admission; the reducer therefore always writes the empty string.
    assert not admissible(dict(r["cells"]["F1"], superseded=False), cell_id="F1")
    assert not admissible(dict(r["cells"]["F1"], superseded="True"), cell_id="F1")


def test_duplicate_occurrence_counted_once_and_descriptive_records_kept():
    o = obs(1, "F1", "no")
    r = rd.reduce_project("NO", {"NO-01": DOCS["NO-01"]}, [req("NO-01", [o, dict(o, claim_no=2), obs(3, "F11 financial_inclusion", "stated")])])
    assert r["cells"]["F1"]["claim_ids"] == ["NO-01:p1-1#1"] and r["descriptive"][0]["record"] == "F11 financial_inclusion"


def test_combine_models_unanimity():
    a = {"F1": {"value": "no", "evidence_state": "documented", "quote": "q"}}
    b = {"F1": {"value": "no", "evidence_state": "documented", "quote": "q2"}}
    c = {"F1": {"value": "yes", "evidence_state": "documented", "quote": "q3"}}
    assert rd.combine_models({"a": a, "b": b})["F1"]["value"] == "no"
    x = rd.combine_models({"a": a, "b": b, "c": c})["F1"]
    assert x["value"] == "" and x["to_authors"]


def test_requests_from_run_reads_a_work_folder(tmp_path):
    u = request()
    (tmp_path / "REQUESTS.jsonl").write_text(json.dumps({"request_key": "NO-01:p3-4", "unit_ids": ["NO-01"], "user": u}) + "\n")
    (tmp_path / "ATTEMPTS.jsonl").write_text(json.dumps({"request_key": "NO-01:p3-4", "complete": True, "model_returned": "m",
                                                         "text": response([obs(1, "F1", "no")], u)}) + "\n")
    rs = rd.requests_from_run(str(tmp_path / "ATTEMPTS.jsonl"), str(tmp_path / "REQUESTS.jsonl"))
    assert rs[0]["state"] == "ok" and rs[0]["owned_pages"] == [3, 4]
    out = rd.reduce_project("NO", {"NO-01": DOCS["NO-01"]}, rs)
    assert out["cells"]["F1"]["value"] == "no" and out["cells"]["F1"]["page_index"] == 3


def test_runner_extraction_stage_end_to_end_with_a_fake_client(tmp_path):
    """build_jobs-shaped extraction job -> runner (fake Anthropic client, no network) -> requests_from_run -> reducer.
    One request answers cleanly, one returns a false-complete payload with an unreadable owned page."""
    import contextlib, hashlib, types
    sys.path.insert(0, os.path.join(HERE, "..", "scripts", "pipeline"))
    import runner
    d = tmp_path / "job"; d.mkdir()
    (d / "SYSTEM_PROMPT.md").write_text("SYSTEM v12.2\n")
    users = {"NO-01:p3-4": request(), "NO-01:p5-5": v122.render_request(dict(META, request_id="NO-01:p5-5"), {4: TEXT[4], 5: TEXT[5]}, [5])}
    with open(d / "REQUESTS.jsonl", "w") as fh:
        for k, u in users.items(): fh.write(json.dumps({"request_key": k, "unit_ids": ["NO-01"], "user": u, "user_sha256": hashlib.sha256(u.encode()).hexdigest()}) + "\n")
    json.dump({"stage": "extraction_single", "system_prompt_file": "pipeline/prompts/extraction_v12.2.system.md", "system_prompt_version": "12.2",
               "user_message_format": "test", "packing": "test", "inputs": [{"file": "units/x.csv", "sha256": "a" * 64, "rows": 1, "in_repository": False}],
               "request_keys": list(users)}, open(d / "JOB_META.json", "w"))

    class Fake:
        def __init__(self):
            fake = self
            class Messages:
                @contextlib.contextmanager
                def stream(self, **p):
                    u = p["messages"][0]["content"]; h = v122.header_of(u)
                    t = response([obs(1, "F1", "no")], u) if h["request_id"] == "NO-01:p3-4" else response([], u, unreadable_pages=[5])
                    yield types.SimpleNamespace(get_final_message=lambda: {"id": "m", "model": "claude-opus-5-5", "stop_reason": "end_turn",
                                                                           "content": [{"type": "text", "text": t}],
                                                                           "usage": {"input_tokens": 100, "output_tokens": 50}})
            self.messages = Messages()

    work = tmp_path / "work"
    runner.main(["run", "--job", str(d), "--provider", "anthropic", "--model", "claude-opus-5-5", "--work", str(work), "--run", "t",
                 "--purpose", "development", "--max-usd", "1"], client=Fake())
    rs = rd.requests_from_run(str(work / "t" / "ATTEMPTS.jsonl"), str(d / "REQUESTS.jsonl"))
    assert [r["state"] for r in rs] == ["ok", "failed"] and "unreadable" in rs[1]["problems"][0]
    out = rd.reduce_project("NO", {"NO-01": DOCS["NO-01"]}, rs)
    assert out["cells"]["F1"]["value"] == "no" and not out["search_closed"] and "[5]" in out["gaps"][0]


def test_pilot_tolerances_fence_and_null_modality():
    """MB 23 Nov 2026: one outer code fence is removed; modality null reads as n/d. Two fences or prose around stay failures."""
    import v122 as _v
    assert _v.FENCE.fullmatch('```json\n{"a": 1}\n```').group(1) == '{"a": 1}'
    assert _v.FENCE.fullmatch('```\n{"a": 1}\n```')
    assert not _v.FENCE.fullmatch('Here it is:\n```json\n{"a": 1}\n```')
