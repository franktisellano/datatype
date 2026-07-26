"""Tests for the variable-font designspace configuration."""

from sources.config import AXIS_MASTERS, NAMED_INSTANCES


def test_designspace_contains_all_axis_corners_and_default():
    locations = {(master[0], master[1]) for master in AXIS_MASTERS}

    assert locations == {
        (50, 100),
        (50, 400),
        (50, 900),
        (100, 100),
        (100, 400),
        (100, 900),
        (150, 100),
        (150, 400),
        (150, 900),
    }
    assert AXIS_MASTERS[0][:2] == (100, 400)


def test_named_instances_include_all_standard_weights():
    normal_width_instances = {
        (style, weight)
        for style, width, weight in NAMED_INSTANCES
        if width == 100
    }

    assert normal_width_instances == {
        ("Thin", 100),
        ("ExtraLight", 200),
        ("Light", 300),
        ("Regular", 400),
        ("Medium", 500),
        ("SemiBold", 600),
        ("Bold", 700),
        ("ExtraBold", 800),
        ("Black", 900),
    }
