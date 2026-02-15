"""Font assembly using fontTools FontBuilder."""

import time
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.designspaceLib import (
    DesignSpaceDocument, SourceDescriptor, AxisDescriptor, InstanceDescriptor,
)
from fontTools import varLib
from fontTools.varLib.instancer import instantiateVariableFont
from fontTools.otlLib.builder import buildStatTable

from src.config import (
    UPM, ASCENDER, DESCENDER, FAMILY_NAME, REGULAR_STYLE,
    CAP_HEIGHT, X_HEIGHT, FONT_VERSION,
)


def build_font(glyph_data, feature_code, style=REGULAR_STYLE, family_name=FAMILY_NAME):
    """Build a complete TTF font (single static master).

    Args:
        glyph_data: dict of {glyph_name: (advance_width, draw_func_or_None)}
        feature_code: OpenType feature code string
        style: font style name
        family_name: font family name

    Returns:
        fontTools.ttLib.TTFont
    """
    glyph_names = [".notdef"] + [n for n in glyph_data if n != ".notdef"]
    if ".notdef" not in glyph_data:
        raise ValueError(".notdef glyph is required")

    fb = FontBuilder(UPM, isTTF=True)
    fb.setupGlyphOrder(glyph_names)

    # Build cmap from glyph names (uniXXXX pattern)
    cmap = {}
    for name in glyph_names:
        if name.startswith("uni") and len(name) == 7:
            try:
                code = int(name[3:], 16)
                cmap[code] = name
            except ValueError:
                pass
    if "space" in glyph_names:
        cmap[0x0020] = "space"

    fb.setupCharacterMap(cmap)

    # Draw glyphs
    glyph_table = {}
    for name in glyph_names:
        pen = TTGlyphPen(None)
        width, draw_func = glyph_data[name]
        if draw_func is not None:
            draw_func(pen)
        glyph_table[name] = pen.glyph()

    fb.setupGlyf(glyph_table)

    # Metrics - calculate LSB from actual glyph bounds
    metrics = {}
    for name in glyph_names:
        width = glyph_data[name][0]
        glyph = glyph_table[name]

        # Get glyph bounding box to determine proper LSB
        if hasattr(glyph, 'xMin') and glyph.xMin is not None:
            lsb = glyph.xMin  # Use actual left edge (can be negative for overlap)
        else:
            lsb = 0  # Empty glyph or no contours

        metrics[name] = (width, lsb)
    fb.setupHorizontalMetrics(metrics)

    fb.setupHorizontalHeader(ascent=ASCENDER, descent=DESCENDER)
    fb.setupNameTable({
        "familyName": family_name,
        "styleName": style,
        "copyright": "Copyright 2026 The Datatype Project Authors (https://github.com/franktisellano/datatype)",
        "manufacturer": "Datatype Project",
        "licenseDescription": "This Font Software is licensed under the SIL Open Font License, Version 1.1.",
        "licenseInfoURL": "https://openfontlicense.org",
    })
    fb.setupOS2(
        sTypoAscender=ASCENDER,
        sTypoDescender=DESCENDER,
        sTypoLineGap=0,
        usWinAscent=850,  # Must accommodate tallest glyphs + accents (fontbakery requires ≥811)
        usWinDescent=250,  # Must accommodate deepest glyphs + descenders (fontbakery requires ≥212)
        sxHeight=X_HEIGHT,
        sCapHeight=CAP_HEIGHT,
        achVendID="DTPE",  # Datatype Project
        fsType=0x0000,  # Installable embedding (OFL compliant)
        fsSelection=0x00C0,  # Bit 6: REGULAR + Bit 7: USE_TYPO_METRICS
        usWidthClass=5,  # Medium/Normal (will be overridden by variable font width axis)
        version=4,  # OS/2 table version 4 (supports fsSelection bits 7-9)
    )
    fb.setupPost()
    # Bit 4: Instructions may alter advance width (allows geometry beyond advance width)
    # Timestamps: Font spec uses seconds since 1904-01-01 00:00:00
    # Current time minus 1 day for creation (fonts should have creation in past)
    from datetime import datetime, timedelta
    now = datetime.now()
    epoch_1904 = datetime(1904, 1, 1)
    created_seconds = int((now - timedelta(days=1) - epoch_1904).total_seconds())
    modified_seconds = int((now - epoch_1904).total_seconds())

    fb.setupHead(
        unitsPerEm=UPM,
        flags=0b00010000,
        created=created_seconds,
        modified=modified_seconds
    )

    if feature_code:
        fb.addOpenTypeFeatures(feature_code)

    # Add additional required name table entries
    font = fb.font

    # Add 'gasp' table for proper antialiasing (Google Fonts requirement)
    # 0x000F = gridfit + grayscale + symmetric smoothing + symmetric gridfit
    from fontTools.ttLib.tables._g_a_s_p import table__g_a_s_p
    gasp_table = table__g_a_s_p()
    gasp_table.gaspRange = {0xFFFF: 0x000F}  # All sizes
    font["gasp"] = gasp_table

    # Set PANOSE values for sans-serif proportional font
    # Note: ASCII chars are monospaced, but chart glyphs are wider (mixed width font)
    os2 = font["OS/2"]
    os2.panose.bFamilyType = 2   # Latin Text
    os2.panose.bSerifStyle = 11  # Sans Serif
    os2.panose.bWeight = 5       # Book (will vary with weight axis)
    os2.panose.bProportion = 3   # Modern (mixed proportions)
    os2.panose.bContrast = 0     # Any
    os2.panose.bStrokeVariation = 0  # Any
    os2.panose.bArmStyle = 0     # Any
    os2.panose.bLetterform = 0   # Any
    os2.panose.bMidline = 0      # Any
    os2.panose.bXHeight = 0      # Any

    # Set code page ranges (Latin support)
    os2.ulCodePageRange1 = (
        0x00000001 |  # Latin 1 (1252)
        0x00000002 |  # Latin 2: Eastern Europe (1250)
        0x00000004 |  # Cyrillic (1251) - may add in future
        0x00000008 |  # Greek (1253) - may add in future
        0x00000020 |  # Turkish (1254)
        0x00000040    # Baltic (1257)
    )
    os2.ulCodePageRange2 = 0

    # Set post table isFixedPitch to 0 (not monospaced)
    # ASCII glyphs are fixed-width but chart glyphs are wider (mixed width font)
    post = font["post"]
    post.isFixedPitch = 0

    name_table = font["name"]

    # Name ID 0: Copyright
    copyright_text = "Copyright 2026 The Datatype Project Authors (https://github.com/franktisellano/datatype)"
    name_table.setName(copyright_text, 0, 3, 1, 0x0409)  # Windows
    name_table.setName(copyright_text, 0, 1, 0, 0)       # Mac

    # Name ID 3: Unique Font Identifier
    unique_id = f"{FONT_VERSION};NONE;{family_name}-{style}"
    name_table.setName(unique_id, 3, 3, 1, 0x0409)
    name_table.setName(unique_id, 3, 1, 0, 0)

    # Name ID 4: Full Font Name
    full_name = f"{family_name} {style}"
    name_table.setName(full_name, 4, 3, 1, 0x0409)
    name_table.setName(full_name, 4, 1, 0, 0)

    # Name ID 5: Version String
    version_string = f"Version {FONT_VERSION}"
    name_table.setName(version_string, 5, 3, 1, 0x0409)
    name_table.setName(version_string, 5, 1, 0, 0)

    # Name ID 6: PostScript Name
    ps_name = f"{family_name}-{style}"
    name_table.setName(ps_name, 6, 3, 1, 0x0409)
    name_table.setName(ps_name, 6, 1, 0, 0)

    # Name ID 13: License Description
    license_text = "This Font Software is licensed under the SIL Open Font License, Version 1.1. This license is available with a FAQ at: https://openfontlicense.org"
    name_table.setName(license_text, 13, 3, 1, 0x0409)
    name_table.setName(license_text, 13, 1, 0, 0)

    # Name ID 14: License URL
    license_url = "https://openfontlicense.org"
    name_table.setName(license_url, 14, 3, 1, 0x0409)
    name_table.setName(license_url, 14, 1, 0, 0)

    return font


def build_variable_font(master_fonts, axes_config, named_instances=None):
    """Build a variable font from multiple static masters.

    Args:
        master_fonts: list of (ttFont, location_dict) tuples
            location_dict maps axis name to value, e.g. {"Width": 100, "Weight": 400}
        axes_config: list of (tag, name, min_val, default_val, max_val) tuples
        named_instances: optional list of (style_name, location_dict) tuples
            for fvar named instances

    Returns:
        fontTools.ttLib.TTFont — variable font with fvar/gvar tables
    """
    ds = DesignSpaceDocument()

    # Define axes
    for tag, name, min_val, default_val, max_val in axes_config:
        axis = AxisDescriptor()
        axis.tag = tag
        axis.name = name
        axis.minimum = min_val
        axis.default = default_val
        axis.maximum = max_val
        ds.addAxis(axis)

    # Add sources (masters) — locations use axis names
    for i, (font, location) in enumerate(master_fonts):
        src = SourceDescriptor()
        src.font = font
        src.location = location
        if i == 0:
            src.copyLib = True
            src.copyFeatures = True
            src.copyGroups = True
            src.copyInfo = True
        ds.addSource(src)

    # Add named instances
    if named_instances:
        for style_name, location in named_instances:
            inst = InstanceDescriptor()
            inst.styleName = style_name
            inst.location = location
            ds.addInstance(inst)

    # Build the variable font
    vf, _, _ = varLib.build(ds)

    # Populate STAT table with axis values for named instances
    # This is REQUIRED per OpenType spec for variable fonts with named instances
    # Safari enforces this requirement strictly at weight 600+
    stat_axes = [
        dict(tag="wdth", name="Width"),
        dict(tag="wght", name="Weight"),
    ]

    stat_locations = [
        # Width axis values (OpenType spec compliant: default=100)
        dict(name="Condensed", location=dict(wdth=50)),
        dict(name="SemiCondensed", location=dict(wdth=75)),
        dict(name="Normal", location=dict(wdth=100), flags=0x2),  # ElidableAxisValueName
        dict(name="SemiExpanded", location=dict(wdth=125)),
        dict(name="Expanded", location=dict(wdth=150)),

        # Weight axis values
        dict(name="Thin", location=dict(wght=100)),
        dict(name="ExtraLight", location=dict(wght=200)),
        dict(name="Light", location=dict(wght=300)),
        dict(name="Regular", location=dict(wght=400), flags=0x2),  # ElidableAxisValueName
        dict(name="Medium", location=dict(wght=500)),
        dict(name="SemiBold", location=dict(wght=600)),
        dict(name="Bold", location=dict(wght=700)),
        dict(name="ExtraBold", location=dict(wght=800)),
        dict(name="Black", location=dict(wght=900)),

        # Format 4: Multi-axis combinations for named instances
        dict(name="Light Compact", location=dict(wdth=75, wght=300)),
        dict(name="Regular", location=dict(wdth=100, wght=400), flags=0x2),  # Default instance
        dict(name="Medium Wide", location=dict(wdth=125, wght=500)),
        dict(name="Bold", location=dict(wdth=100, wght=700)),
        dict(name="Thin Narrow", location=dict(wdth=50, wght=100)),
        dict(name="Light Wide", location=dict(wdth=150, wght=300)),
        dict(name="SemiBold Compact", location=dict(wdth=75, wght=600)),
        dict(name="Black Wide", location=dict(wdth=150, wght=900)),
    ]

    buildStatTable(vf, stat_axes, stat_locations)

    # Fix usWidthClass for proper display in font menus
    # For wdth 50-150 with default 100, use class 5 (Normal/Medium)
    vf["OS/2"].usWidthClass = 5

    # Add variable font name table entries
    name_table = vf["name"]

    # Name ID 25: Variations PostScript Name Prefix
    name_table.setName("Datatype", 25, 3, 1, 0x0409)
    name_table.setName("Datatype", 25, 1, 0, 0)

    # Note: Name IDs 16/17 (Typographic Family/Subfamily) are not needed
    # for standard variable fonts per Google Fonts guidelines

    return vf


def export_static_instance(vf, location, output_dir, basename, style_name, weight_class):
    """Export a static font instance from a variable font.

    Args:
        vf: variable TTFont
        location: dict of axis tag → value to pin, e.g. {"wght": 700, "wdth": 15}
        output_dir: output directory
        basename: font family basename (e.g. "Datatype")
        style_name: style name (e.g. "Bold")
        weight_class: OS/2 usWeightClass value
    """
    import copy
    import os

    static = instantiateVariableFont(copy.deepcopy(vf), location)

    # Update name table
    static["name"].setName(style_name, 2, 3, 1, 0x0409)  # styleName
    static["name"].setName(style_name, 2, 1, 0, 0)        # styleName (Mac)
    static["name"].setName(f"{basename}-{style_name}", 6, 3, 1, 0x0409)  # postScriptName
    static["name"].setName(f"{basename}-{style_name}", 6, 1, 0, 0)

    # Update OS/2 weight class
    static["OS/2"].usWeightClass = weight_class

    # Set OS/2 fsSelection flags
    fs_selection = 0x0080  # Bit 7: USE_TYPO_METRICS (required for cross-platform)
    if style_name == "Regular":
        fs_selection |= 0x0040  # Bit 6: REGULAR
    if weight_class >= 700:
        fs_selection |= 0x0020  # Bit 5: BOLD
    static["OS/2"].fsSelection = fs_selection

    # Set head macStyle flags
    mac_style = 0
    if weight_class >= 700:
        mac_style |= 0x0001  # Bit 0: BOLD
    static["head"].macStyle = mac_style

    os.makedirs(output_dir, exist_ok=True)

    ttf_path = os.path.join(output_dir, f"{basename}-{style_name}.ttf")
    static.save(ttf_path)
    print(f"    {ttf_path}")

    static.flavor = "woff2"
    woff2_path = os.path.join(output_dir, f"{basename}-{style_name}.woff2")
    static.save(woff2_path)
    print(f"    {woff2_path}")
