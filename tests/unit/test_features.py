"""Unit tests for generated OpenType feature code."""

from sources.build import _build_feature_code
from sources.glyphs.bar import generate_bar_feature_code
from sources.glyphs.pie import generate_pie_feature_code
from sources.glyphs.sparkline import generate_sparkline_feature_code


def test_bar_feature_code_handles_boundary_values():
    feature_code = generate_bar_feature_code(100)

    assert "sub uni007B uni0062 uni003A by bar_start;" in feature_code
    assert "sub bar_d0 by bar_h0;" in feature_code
    assert "sub bar_d9 bar_d9 by bar_h99;" in feature_code
    assert "sub bar_d1 bar_d0 bar_d0 by bar_h100;" in feature_code
    assert "sub uni007D by bar_end;" in feature_code


def test_sparkline_feature_code_resolves_pairs():
    feature_code = generate_sparkline_feature_code(3)

    assert "sub uni007B uni006C uni003A by spark_start;" in feature_code
    assert "sub spark_p0 by spark_0_to_3;" in feature_code
    assert "sub spark_p3 by spark_3_to_0;" in feature_code
    assert "lookup spark_resolve_pairs" in feature_code


def test_pie_feature_code_handles_boundary_values():
    feature_code = generate_pie_feature_code()

    assert (
        "sub uni007B uni0070 uni003A uni0030 uni007D by pie_0;"
        in feature_code
    )
    assert (
        "sub uni007B uni0070 uni003A uni0031 uni0030 uni0030 uni007D "
        "by pie_100;"
        in feature_code
    )


def test_combined_features_register_required_lookups():
    feature_code = _build_feature_code(100)

    assert "feature liga" in feature_code
    assert "lookup pie_liga;" in feature_code
    assert "feature calt" in feature_code
    assert "lookup bar_open;" in feature_code
    assert "lookup spark_resolve_pairs;" in feature_code
