import csv
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts", "units"))
import add_image_text as ait  # noqa: E402


def test_noise_and_norm():
    assert ait.noise("ol 4 poi a Lo 14")
    assert ait.noise("90 90 80 80 Graph")
    assert not ait.noise("Digital Rupiah will complement the physical cash")
    assert ait.norm("Share of Australians, 2013!") == "shareofaustralians2013"


def test_blocks_parse_header():
    raw = ("=== AU/x.pdf PAGE 13 (mean confidence 90.54; verdict partial; lang eng) ===\nGraph 1\n\n"
           "=== AU/y.pdf PAGE 2 (mean confidence 70.00; verdict garbage; lang eng+rus) ===\nzz\n")
    b = ait.blocks(raw)
    assert [(x["pdf"], x["page"], x["verdict"], x["lang"]) for x in b] == [("AU/x.pdf", "13", "partial", "eng"), ("AU/y.pdf", "2", "garbage", "eng+rus")]
    assert b[0]["text"].strip() == "Graph 1"


def test_new_units_keep_ids_and_own_paragraphs(tmp_path, monkeypatch):
    units = tmp_path / "u"; units.mkdir()
    rows = [{"unit_id": "D:p1:s1", "page": "1", "para": "1", "n_words": "5", "text": "The first page has text here.", "page_end": "1"},
            {"unit_id": "D:p2:s2", "page": "2", "para": "1", "n_words": "4", "text": "Figure 3: Model overview.", "page_end": "2"},
            {"unit_id": "D:p3:s3", "page": "3", "para": "2", "n_words": "4", "text": "The third page continues.", "page_end": "3"}]
    with open(units / "D.units.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, list(rows[0])); w.writeheader(); w.writerows(rows)
    (tmp_path / "ocr.txt").write_text("=== X/d.pdf PAGE 2 (mean confidence 91.0; verdict ok; lang eng) ===\n"
                                      "Figure 3: Model overview.\n\nThe central bank cannot see individual payments of users.\n\n"
                                      "90 80 70\n\nol 4 poi a Lo\n", encoding="utf-8")
    with open(tmp_path / "check.csv", "w", newline="", encoding="utf-8") as fh:
        fh.write("pdf,page,text_layer_words,ocr_words,mean_conf,lang,flag,verdict,note\nX/d.pdf,2,4,30,91.0,eng,IMAGE_TEXT,ok,\n")
    with open(tmp_path / "list.csv", "w", newline="", encoding="utf-8") as fh:
        fh.write("doc_key,route,pdf,pdf_sha256,pages\nD,A,X/d.pdf,abc,2\n")
    repo = tmp_path / "repo"; (repo / "data/units").mkdir(parents=True); (repo / "data/manifest").mkdir(parents=True)
    with open(repo / "data/units/UNITS_MANIFEST_2026-01-01.csv", "w", newline="", encoding="utf-8") as fh:
        fh.write("doc_key,text_mode,units,words,units_sha256\nD,reading_order,3,13,x\n")
    monkeypatch.setattr(ait, "ROOT", str(repo))
    rec = ait.main(["--text", str(tmp_path / "ocr.txt"), "--check", str(tmp_path / "check.csv"), "--list", str(tmp_path / "list.csv"),
                    "--units", str(units), "--out", str(tmp_path / "v2"), "--date", "2026-01-01b", "--engine", "t"])
    out = list(csv.DictReader(open(tmp_path / "v2" / "D.units.csv", encoding="utf-8")))
    assert [r["unit_id"] for r in out[:3]] == ["D:p1:s1", "D:p2:s2", "D:p2:s4"]   # existing ids kept, new unit numbered after them
    assert out[2]["para"] != "1" and "cannot see" in out[2]["text"]                # its own block, after the text layer
    assert len(out) == 4                                                           # duplicate caption, axis labels and noise dropped
    assert rec[0]["units_added"] == 1 and rec[0]["units_dropped_duplicate"] == 1
    man = list(csv.DictReader(open(repo / "data/units/UNITS_MANIFEST_2026-01-01b.csv", encoding="utf-8")))
    assert man[0]["text_mode"] == "reading_order+ocr" and man[0]["units"] == "4"
    assert list(csv.DictReader(open(units / "D.units.csv", encoding="utf-8"))) == rows    # input unchanged
