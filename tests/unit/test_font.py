"""Structural checks for the checked-in variable font."""

from pathlib import Path

import pytest
from fontTools.ttLib import TTFont

from sources.config import FONT_VERSION


FONT_PATH = (
    Path(__file__).resolve().parents[2]
    / "fonts"
    / "variable"
    / "Datatype[wdth,wght].ttf"
)


@pytest.fixture(scope="module")
def font():
    loaded_font = TTFont(FONT_PATH, lazy=True)
    yield loaded_font
    loaded_font.close()


def test_variable_font_has_required_tables(font):
    required_tables = {
        "cmap",
        "fvar",
        "gvar",
        "GSUB",
        "HVAR",
        "name",
        "OS/2",
        "STAT",
    }

    assert required_tables <= set(font.keys())


def test_variable_axes_match_public_contract(font):
    axes = {
        axis.axisTag: (axis.minValue, axis.defaultValue, axis.maxValue)
        for axis in font["fvar"].axes
    }

    assert axes == {
        "wdth": (50.0, 100.0, 150.0),
        "wght": (100.0, 400.0, 900.0),
    }
    assert len(font["fvar"].instances) == 9


def test_font_version_and_latin_core_coverage(font):
    assert font["head"].fontRevision == pytest.approx(float(FONT_VERSION), abs=0.001)
    assert len(font.getBestCmap()) == 319
    assert font["maxp"].numGlyphs == 10_850
