"""Unit tests for chart glyph generation."""

from fontTools.pens.areaPen import AreaPen
from fontTools.pens.recordingPen import RecordingPen

from sources.config import FontParams
from sources.glyphs.base_imported import draw_base_glyphs
from sources.glyphs.bar import draw_bar_glyphs
from sources.glyphs.pie import draw_pie_glyphs
from sources.glyphs.sparkline import draw_sparkline_glyphs


def _record(draw_function):
    pen = RecordingPen()
    draw_function(pen)
    return pen.value


def _signed_area(draw_function):
    pen = AreaPen()
    draw_function(pen)
    return pen.value


def test_bar_glyphs_include_every_height_and_helpers():
    glyphs = {}
    params = FontParams(max_value=10, bar_width=200, bar_fill=0.5)

    draw_bar_glyphs(glyphs, params)

    assert {"bar_start", "bar_end", "bar_sep"} <= glyphs.keys()
    assert all(f"bar_d{digit}" in glyphs for digit in range(10))
    assert all(f"bar_h{height}" in glyphs for height in range(11))
    assert glyphs["bar_h0"] == (200, None)
    assert glyphs["bar_h10"][0] == 200
    assert _record(glyphs["bar_h10"][1])


def test_sparkline_glyphs_cover_every_possible_pair():
    glyphs = {}
    params = FontParams(max_value=2, seg_width=180, point_width=12)

    draw_sparkline_glyphs(glyphs, params)

    expected_segments = {
        f"spark_{start}_to_{end}"
        for start in range(3)
        for end in range(3)
    }
    assert expected_segments <= glyphs.keys()
    assert all(glyphs[name][0] == 180 for name in expected_segments)
    assert _record(glyphs["spark_0_to_2"][1])
    assert _record(glyphs["spark_p2"][1])


def test_pie_glyphs_cover_zero_through_one_hundred():
    glyphs = {}

    draw_pie_glyphs(glyphs)

    assert all(f"pie_{percentage}" in glyphs for percentage in range(101))
    assert len(glyphs) == 101
    assert _record(glyphs["pie_0"][1])
    assert _record(glyphs["pie_50"][1])
    assert _record(glyphs["pie_100"][1])


def test_visible_glyphs_use_truetype_winding():
    base_glyphs = {}
    bar_glyphs = {}
    spark_glyphs = {}
    pie_glyphs = {}

    draw_base_glyphs(base_glyphs)
    draw_bar_glyphs(bar_glyphs, FontParams(max_value=10))
    draw_sparkline_glyphs(spark_glyphs, FontParams(max_value=2))
    draw_pie_glyphs(pie_glyphs)

    # TrueType outer contours wind clockwise, producing a negative signed area.
    assert _signed_area(base_glyphs[".notdef"][1]) < 0
    assert _signed_area(base_glyphs["uni0041"][1]) < 0
    assert _signed_area(bar_glyphs["bar_h10"][1]) < 0
    assert _signed_area(spark_glyphs["spark_0_to_2"][1]) < 0
    assert _signed_area(pie_glyphs["pie_0"][1]) < 0
    assert _signed_area(pie_glyphs["pie_50"][1]) < 0
    assert _signed_area(pie_glyphs["pie_100"][1]) < 0
