"""OCR helpers of scripts/frame/ocr_pdf.py that need no tesseract (Jamaica FAQ, 23 Nov 2026)."""
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts", "frame"))
import ocr_pdf as o  # noqa: E402


def test_bullet_glyphs_read_as_letters_become_bullets_but_words_do_not():
    t = "e CBDC is money\n¢ Transferring funds\n«Going to any\neNaira is\ne-money refers"
    assert o.BULLET.sub("• ", t).splitlines() == ["• CBDC is money", "• Transferring funds", "• Going to any", "eNaira is", "e-money refers"]


def test_a_lone_bar_is_a_capital_i():
    assert o.PIPE_I.sub("I", "Can | accept\nHow do |\n| make\na|b") == "Can I accept\nHow do I\nI make\na|b"


def test_blocks_cut_a_spread_into_halves_and_a_question_column_from_its_answer():
    Image = pytest.importorskip("PIL.Image")
    ImageDraw = pytest.importorskip("PIL.ImageDraw")
    dpi = 100
    im = Image.new("L", (1700, 1100), 255)  # a two-page spread, 17 x 11 in
    d = ImageDraw.Draw(im)
    d.rectangle((50, 100, 200, 160), fill=0)    # question, left half
    d.rectangle((260, 100, 800, 140), fill=0)   # its answer, 0.6 in to the right
    d.rectangle((260, 400, 800, 440), fill=0)   # a later answer paragraph, after a blank band
    d.rectangle((900, 100, 1600, 140), fill=0)  # right half, one column
    boxes = o.blocks(im, dpi)
    assert all(b[2] <= 850 for b in boxes[:3]) and all(b[0] >= 850 for b in boxes[3:])
    q, a = boxes[0], boxes[1]
    assert q[0] == 0 and 200 < q[2] < 260 and a[0] == q[2] and q[1] == a[1]
    assert len(boxes) == 4
