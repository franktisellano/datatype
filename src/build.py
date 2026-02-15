"""Datatype build script: orchestrates font generation."""

import os
import sys
import time
import argparse

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from src.config import FAMILY_NAME, FontParams, SCALES, AXIS_MASTERS, NAMED_INSTANCES
from src.glyphs.base_imported import draw_base_glyphs  # IBM Plex Mono glyphs
from src.glyphs.bar import draw_bar_glyphs, generate_bar_feature_code
from src.glyphs.sparkline import draw_sparkline_glyphs, generate_sparkline_feature_code
from src.glyphs.pie import draw_pie_glyphs, generate_pie_feature_code
from src.font_builder import build_font, build_variable_font, export_static_instance
from src.export import export_font


def _build_master(max_value, params, feature_code):
    """Build a single static master TTFont for given params and feature code."""
    glyph_data = {}

    draw_base_glyphs(glyph_data)
    draw_bar_glyphs(glyph_data, params)
    draw_sparkline_glyphs(glyph_data, params)
    draw_pie_glyphs(glyph_data, params)

    font = build_font(
        glyph_data, feature_code,
        style="Regular",
        family_name=FAMILY_NAME,
    )
    return font


def _build_feature_code(max_value):
    """Generate combined OpenType feature code for a given scale."""
    bar_fea = generate_bar_feature_code(max_value)
    spark_fea = generate_sparkline_feature_code(max_value)
    pie_fea = generate_pie_feature_code()

    return f"""
# Bar chart features
{bar_fea}

# Sparkline features
{spark_fea}

# Pie chart features
{pie_fea}

feature liga {{
    lookup pie_liga;
}} liga;

feature calt {{
    lookup bar_open;
    lookup bar_propagate;
    lookup bar_combine_liga;
    lookup bar_combine_single;
    lookup bar_close;
    lookup spark_open;
    lookup spark_propagate;
    lookup spark_combine_liga;
    lookup spark_combine_single;
    lookup spark_close;
    lookup spark_resolve_pairs;
}} calt;
"""


def build_dev():
    """Build only the default variable font for development."""
    start = time.time()
    output_dir = os.path.join(PROJECT_ROOT, "fonts")

    print("Datatype Dev Build")
    print("=" * 50)

    axes_config = [
        ("wdth", "Width", 0, 50, 100),
        ("wght", "Weight", 100, 400, 900),
    ]

    # Default wdth for named instances
    default_wdth = 50

    # Build only the first scale (default)
    suffix, max_value = SCALES[0]
    scale_label = f"Scale{max_value} (default)"
    print(f"\n── {scale_label} ──")

    # Generate feature code once per scale (GSUB is axis-independent)
    feature_code = _build_feature_code(max_value)

    # Build masters with different axis positions
    masters = []
    for i, (wdth, wght, bw, sw, pw, sep, end, lt, bf, ps) in enumerate(AXIS_MASTERS):
        params = FontParams(
            max_value=max_value,
            bar_width=bw,
            seg_width=sw,
            point_width=pw,
            sep_width=sep,
            end_width=end,
            line_thickness=lt,
            bar_fill=bf,
            pie_stroke=ps,
        )
        print(f"  Building master {i+1}/{len(AXIS_MASTERS)} (wdth={wdth}, wght={wght})...")

        master_font = _build_master(max_value, params, feature_code)
        location = {"Width": wdth, "Weight": wght}
        masters.append((master_font, location))

    # Count glyphs from default master
    default_font = masters[0][0]
    glyph_count = len(default_font.getGlyphOrder())
    print(f"  Glyphs per master: {glyph_count}")

    # Named instances (with custom wdth + wght combinations)
    named_instances = [
        (style, {"Width": wdth, "Weight": wght})
        for style, wdth, wght in NAMED_INSTANCES
    ]

    # Build variable font
    print("  Merging masters into variable font...")
    vf = build_variable_font(masters, axes_config, named_instances)

    # Export variable font
    basename = f"{FAMILY_NAME}{suffix}"
    print(f"  Exporting {basename}...")
    export_font(vf, output_dir, basename)

    elapsed = time.time() - start
    print(f"\nBuild complete in {elapsed:.1f}s")
    print(f"Output: {output_dir}/\n")

def build_all():
    """Build all Datatype variants."""
    start = time.time()
    output_dir = os.path.join(PROJECT_ROOT, "fonts")

    print("Datatype Build")
    print("=" * 50)

    axes_config = [
        ("wdth", "Width", 0, 50, 100),
        ("wght", "Weight", 100, 400, 900),
    ]

    # Default wdth for named instances
    default_wdth = 50

    for suffix, max_value in SCALES:
        print(f"\n── Building Datatype ──")

        # Generate feature code once per scale (GSUB is axis-independent)
        feature_code = _build_feature_code(max_value)

        # Build masters with different axis positions
        masters = []
        for i, (wdth, wght, bw, sw, pw, sep, end, lt, bf, ps) in enumerate(AXIS_MASTERS):
            params = FontParams(
                max_value=max_value,
                bar_width=bw,
                seg_width=sw,
                point_width=pw,
                sep_width=sep,
                end_width=end,
                line_thickness=lt,
                bar_fill=bf,
                pie_stroke=ps,
            )
            print(f"  Building master {i+1}/{len(AXIS_MASTERS)} (wdth={wdth}, wght={wght})...")

            master_font = _build_master(max_value, params, feature_code)
            location = {"Width": wdth, "Weight": wght}
            masters.append((master_font, location))

        # Count glyphs from default master
        default_font = masters[0][0]
        glyph_count = len(default_font.getGlyphOrder())
        print(f"  Glyphs per master: {glyph_count}")

        # Named instances (with custom wdth + wght combinations)
        named_instances = [
            (style, {"Width": wdth, "Weight": wght})
            for style, wdth, wght in NAMED_INSTANCES
        ]

        # Build variable font
        print("  Merging masters into variable font...")
        vf = build_variable_font(masters, axes_config, named_instances)

        # Export variable font
        basename = f"{FAMILY_NAME}{suffix}"
        print(f"  Exporting {basename}...")
        export_font(vf, output_dir, basename)

        # Export static instances
        static_dir = os.path.join(output_dir, "static")
        print(f"  Exporting static instances...")
        for style_name, wdth, wght in NAMED_INSTANCES:
            export_static_instance(
                vf,
                location={"wght": wght, "wdth": wdth},
                output_dir=static_dir,
                basename=f"{FAMILY_NAME}{suffix}",
                style_name=style_name,
                weight_class=wght,
            )

    elapsed = time.time() - start
    print(f"\nBuild complete in {elapsed:.1f}s")
    print(f"Output: {output_dir}/\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build Datatype fonts.")
    parser.add_argument(
        "--dev",
        action="store_true",
        help="Build only the default variable font for development.",
    )
    args = parser.parse_args()

    if args.dev:
        build_dev()
    else:
        build_all()