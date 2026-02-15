"""Datatype font export to .ttf and .woff2 formats."""

import os
from fontTools.ttLib import TTFont


def export_font(font, output_dir, basename):
    """Export font as .ttf and .woff2.

    Args:
        font: fontTools TTFont object
        output_dir: output directory path
        basename: filename without extension (e.g. 'Datatype-Regular')
    """
    os.makedirs(output_dir, exist_ok=True)

    ttf_path = os.path.join(output_dir, f"{basename}.ttf")
    woff2_path = os.path.join(output_dir, f"{basename}.woff2")

    # Save TTF
    font.save(ttf_path)
    print(f"  Saved {ttf_path}")

    # Save WOFF2
    font.flavor = "woff2"
    font.save(woff2_path)
    print(f"  Saved {woff2_path}")

    # Reset flavor for any further use
    font.flavor = None
