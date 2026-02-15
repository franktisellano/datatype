"""Datatype font export to .ttf and .woff2 formats."""

import os
from fontTools.ttLib import TTFont


def export_font(font, output_dir, basename, is_variable=False):
    """Export font as .ttf and .woff2.

    Args:
        font: fontTools TTFont object
        output_dir: output directory path
        basename: filename without extension (e.g. 'Datatype-Regular')
        is_variable: if True, append axis tags in brackets (e.g. 'Datatype[wdth,wght].ttf')
    """
    os.makedirs(output_dir, exist_ok=True)

    # Variable font filenames include axis tags in brackets (alphabetically ordered, wght last)
    if is_variable:
        ttf_filename = f"{basename}[wdth,wght].ttf"
        woff2_filename = f"{basename}[wdth,wght].woff2"
    else:
        ttf_filename = f"{basename}.ttf"
        woff2_filename = f"{basename}.woff2"

    ttf_path = os.path.join(output_dir, ttf_filename)
    woff2_path = os.path.join(output_dir, woff2_filename)

    # Save TTF
    font.save(ttf_path)
    print(f"  Saved {ttf_path}")

    # Save WOFF2
    font.flavor = "woff2"
    font.save(woff2_path)
    print(f"  Saved {woff2_path}")

    # Reset flavor for any further use
    font.flavor = None
