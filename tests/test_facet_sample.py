"""Blind facet sample of 80 sentences (scripts/units/draw_facet_sample.py) on invented units: population, exclusions,
inclusion probabilities, and that a workbook carries no label of anyone."""
import csv
import os
import sys

from openpyxl import load_workbook

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts", "units"))
import draw_facet_sample as dfs  # noqa: E402

MAN = ["doc_key", "id", "project", "tier", "year", "kind", "issuer", "issuer_type", "route", "units_sha256", "stratum", "inclined_group"]


def _w(path, fields, rows):
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fields)
        w.writeheader()
        w.writerows(rows)


def _setup(tmp_path):
    units = tmp_path / "units"
    units.mkdir()
    man = []
    for k, (proj, route, stratum) in enumerate([("AA", "A", "evidence"), ("BB", "D", "evidence"), ("CC", "B", "evidence"), ("WW", "A", "inclined")]):
        key = f"DOC{k}"
        man.append({"doc_key": key, "id": key, "project": proj, "tier": "T1", "year": "2024", "kind": "report", "issuer": "x",
                    "issuer_type": "central_bank", "route": route, "units_sha256": "h", "stratum": stratum, "inclined_group": "" if stratum == "evidence" else "3 wholesale"})
        U = [{"unit_id": f"{key}:p1:s{i}", "page": "1", "para": str(i // 3), "text": f"privacy sentence {key} {i}"} for i in range(60)]
        _w(units / f"{key}.units.csv", ["unit_id", "page", "para", "text"], U)
        _w(units / f"{key}.candidates.csv", ["unit_id", "stratum"], [{"unit_id": u["unit_id"], "stratum": "D" if i % 2 == 0 else "N"} for i, u in enumerate(U)])
    _w(tmp_path / "manifest.csv", MAN, man)
    samples = tmp_path / "samples"
    samples.mkdir()
    _w(samples / "AGREEMENT_SAMPLE_dev_2026-11-13.csv", ["unit_id"], [{"unit_id": "DOC0:p1:s0"}, {"unit_id": "DOC1:p1:s2"}])
    _w(tmp_path / "issuers.csv", ["id", "issuer", "joint_with"], [])
    return units, samples


def test_facet_sample(tmp_path):
    units, samples = _setup(tmp_path)
    s = dfs.main(["--units", str(units), "--issuers", str(tmp_path / "issuers.csv"), "--out", str(tmp_path / "out"), "--date", "2026-11-22",
                  "--n", "20", "--manifest", str(tmp_path / "manifest.csv"), "--samples-dir", str(samples)])
    assert s["n"] == 20 and s["population"] == 3 * 30 - 4  # D hits of the three evidence documents, minus the two paragraphs shown in dev
    rec = list(csv.DictReader(open(s["record"], encoding="utf-8")))
    ids = {r["unit_id"] for r in rec}
    assert not ids & {"DOC0:p1:s0", "DOC0:p1:s2", "DOC1:p1:s0", "DOC1:p1:s2"} and not any(i.startswith("DOC3") for i in ids)  # dev units and INCLINED out
    assert all(int(i.split(":s")[1]) % 2 == 0 for i in ids)  # dictionary hits only
    for r in rec:  # n_h / N_h, and the probabilities add up to the sample size per route
        assert abs(float(r["inclusion_probability"]) - sum(x["route"] == r["route"] for x in rec) / int(r["route_population"])) < 1e-6
    for coder, f in zip(("MB", "DS"), s["workbooks"]):
        ws = load_workbook(f)["CODE"]
        head = [c.value for c in ws[1]]
        assert head == dfs.COLS and not any("model" in (h or "").lower() for h in head)
        coded = [[c.value for c in row[10:16]] for row in ws.iter_rows(min_row=2)]
        assert len(coded) == 20 and all(v is None for row in coded for v in row)  # nothing pre-filled
    assert [r["order_MB"] for r in rec] != [r["order_DS"] for r in rec]
    # a second draw excludes the first one
    s2 = dfs.main(["--units", str(units), "--issuers", str(tmp_path / "issuers.csv"), "--out", str(tmp_path / "out2"), "--date", "2026-11-23",
                   "--n", "20", "--manifest", str(tmp_path / "manifest.csv"), "--samples-dir", str(samples)])
    assert s2["population"] < s["population"] - 19  # the first draw and its paragraphs are out


def test_allocation_is_proportional():
    assert dfs.allocate({"A": 600, "B": 100, "D": 300}, 80) == {"A": 48, "B": 8, "D": 24}
    assert sum(dfs.allocate({"A": 5, "B": 3, "D": 1}, 4).values()) == 4
