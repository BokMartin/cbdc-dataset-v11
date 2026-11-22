"""Reference sample of 400 (ADR-012 D18): direct stratified random draw D 140 / N 50 / O 210 from all eligible units,
with inclusion probabilities, on invented units."""
import csv
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts", "units"))
import draw_agreement_sample as das  # noqa: E402


def _w(path, fields, rows):
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fields)
        w.writeheader()
        w.writerows(rows)


def _frame(tmp_path, n_units=600):
    units = tmp_path / "units"
    units.mkdir()
    man = {}
    for k, stratum in enumerate(["evidence", "evidence", "inclined"]):
        key = f"DOC{k}"
        man[key] = {"doc_key": key, "id": key, "project": f"P{k}", "tier": "T1", "route": "A", "kind": "report", "year": "2024",
                    "units_sha256": "h", "stratum": stratum}
        U = [{"unit_id": f"{key}:s{i}", "page": "1", "para": str(i // 3), "text": f"a plain sentence number {i} of {key}.", "n_words": "6"} for i in range(n_units)]
        _w(units / f"{key}.units.csv", ["unit_id", "page", "para", "text", "n_words"], U)
        # every 10th a dictionary hit, the next one a neighbour, every 50th a random control; the rest never sent
        cand = [{"unit_id": u["unit_id"], "stratum": "D" if i % 10 == 0 else "N" if i % 10 == 1 else "R"} for i, u in enumerate(U) if i % 10 in (0, 1) or i % 50 == 5]
        _w(units / f"{key}.candidates.csv", ["unit_id", "stratum"], cand)
    return units, man


def test_frame_strata_exclusion_and_inclined(tmp_path):
    units, man = _frame(tmp_path)
    pool, _ = das.main_frame(str(units), man, {"DOC0:s0"})
    ids = {u["unit_id"] for u in pool}
    assert not any(i.startswith("DOC2:") for i in ids)            # INCLINED document out
    assert not {"DOC0:s0", "DOC0:s1", "DOC0:s2"} & ids           # whole shown paragraph out
    c = {s: sum(u["stratum"] == s for u in pool) for s in "DNO"}
    assert c == {"D": 119, "N": 119, "O": 959}                   # random controls and unsent units both in O
    assert set(u["stratum"] for u in pool) == {"D", "N", "O"}


def test_stratum_x_is_out(tmp_path):
    units, man = _frame(tmp_path)
    U = list(csv.DictReader(open(units / "DOC1.units.csv", encoding="utf-8")))
    U[7]["text"], U[7]["n_words"] = "Contents", "1"          # a fragment, not a hit, not sent: stratum X
    _w(units / "DOC1.units.csv", list(U[0].keys()), U)
    pool, _ = das.main_frame(str(units), man, set())
    assert "DOC1:s7" not in {u["unit_id"] for u in pool}


def test_draw_allocation_and_probabilities(tmp_path):
    units, man = _frame(tmp_path, n_units=3000)
    pool, _ = das.main_frame(str(units), man, set())
    s = das.draw_main(pool, das.DESIGN["main"]["alloc"], das.DESIGN["main"]["seed"])
    assert len(s) == 400 and len({u["unit_id"] for u in s}) == 400
    for st, n in das.DESIGN["main"]["alloc"].items():
        got = [u for u in s if u["stratum"] == st]
        assert len(got) == n
        frame = sum(u["stratum"] == st for u in pool)
        assert all(u["stratum_frame"] == frame and abs(u["inclusion_probability"] - n / frame) < 1e-9 for u in got)
    again = das.draw_main(das.main_frame(str(units), man, set())[0], das.DESIGN["main"]["alloc"], das.DESIGN["main"]["seed"])
    assert [u["unit_id"] for u in again] == [u["unit_id"] for u in s]   # reproducible from the seed


def test_small_frame_fails(tmp_path):
    units, man = _frame(tmp_path, n_units=100)
    pool, _ = das.main_frame(str(units), man, set())
    with pytest.raises(SystemExit):
        das.draw_main(pool, das.DESIGN["main"]["alloc"], das.DESIGN["main"]["seed"])
