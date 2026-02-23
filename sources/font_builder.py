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

from sources.config import (
    UPM, ASCENDER, DESCENDER, FAMILY_NAME, REGULAR_STYLE,
    CAP_HEIGHT, X_HEIGHT, FONT_VERSION,
    TYPO_ASCENDER, TYPO_DESCENDER, WIN_ASCENT, WIN_DESCENT,
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

    fb.setupHorizontalHeader(ascent=TYPO_ASCENDER, descent=TYPO_DESCENDER)
    fb.setupNameTable({
        "familyName": family_name,
        "styleName": style,
        "copyright": "Copyright 2026 The Datatype Project Authors (https://github.com/franktisellano/datatype)",
        "manufacturer": "Datatype Project",
        "licenseDescription": "This Font Software is licensed under the SIL Open Font License, Version 1.1.",
        "licenseInfoURL": "https://openfontlicense.org",
    })
    fb.setupOS2(
        sTypoAscender=TYPO_ASCENDER,
        sTypoDescender=TYPO_DESCENDER,
        sTypoLineGap=0,
        usWinAscent=WIN_ASCENT,
        usWinDescent=WIN_DESCENT,
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
    fb.font["head"].fontRevision = float(FONT_VERSION)

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

    # Add 'prep' table with smart dropout control (Google Fonts requirement)
    # B8 01 FF = PUSHW 0x01FF; 85 = SCANCTRL; B0 04 = PUSHB 4; 8D = SCANTYPE
    from fontTools.ttLib import newTable
    from fontTools.ttLib.tables.ttProgram import Program
    prep_table = newTable("prep")
    prep_program = Program()
    prep_program.fromBytecode([0xB8, 0x01, 0xFF, 0x85, 0xB0, 0x04, 0x8D])
    prep_table.program = prep_program
    font["prep"] = prep_table

    # Add 'meta' table with ScriptLangTags (Google Fonts requirement)
    meta_table = newTable("meta")
    meta_table.data = {"dlng": "Latn", "slng": "Latn"}
    font["meta"] = meta_table

    # Set PANOSE values for sans-serif proportional font
    # Note: ASCII chars are monospaced, but chart glyphs are wider (mixed width font)
    os2 = font["OS/2"]
    os2.panose.bFamilyType = 2   # Latin Text
    os2.panose.bSerifStyle = 11  # Sans Serif
    os2.panose.bWeight = 5       # Book (will vary with weight axis)
    os2.panose.bProportion = 9   # Monospaced (ASCII glyphs are fixed-width)
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

    # Name ID 9: Designer
    name_table.setName("Frank Tisellano", 9, 3, 1, 0x0409)  # Windows
    name_table.setName("Frank Tisellano", 9, 1, 0, 0)        # Mac

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

    # Explicitly re-set fontRevision: varLib.build() may override it
    vf["head"].fontRevision = float(FONT_VERSION)

    # Populate STAT table with axis values for named instances
    # This is REQUIRED per OpenType spec for variable fonts with named instances
    # API: single-axis values go in the 'values' field of each axis dict (Format 1/3)
    #      multi-axis Format 4 entries go in a separate 'locations' argument
    stat_axes = [
        dict(tag="wdth", name="Width", values=[
            dict(value=50,    name="UltraCondensed"),   # GF Axis Registry: 50=UltraCondensed
            dict(value=62.5,  name="ExtraCondensed"),   # GF Axis Registry: 62.5=ExtraCondensed (compulsory)
            dict(value=75,    name="Condensed"),
            dict(value=87.5,  name="SemiCondensed"),    # GF Axis Registry: 87.5=SemiCondensed (compulsory)
            dict(value=100,   name="Normal", flags=0x2),  # ElidableAxisValueName
            dict(value=112.5, name="SemiExpanded"),     # GF Axis Registry: 112.5=SemiExpanded (compulsory)
            dict(value=125,   name="Expanded"),          # GF Axis Registry: 125=Expanded
            dict(value=150,   name="ExtraExpanded"),     # GF Axis Registry: 150=ExtraExpanded
        ]),
        dict(tag="wght", name="Weight", values=[
            dict(value=100, name="Thin"),
            dict(value=200, name="ExtraLight"),
            dict(value=300, name="Light"),
            dict(value=400, name="Regular", flags=0x2, linkedValue=700.0),  # Format 3
            dict(value=500, name="Medium"),
            dict(value=600, name="SemiBold"),
            dict(value=700, name="Bold"),
            dict(value=800, name="ExtraBold"),
            dict(value=900, name="Black"),
        ]),
    ]

    buildStatTable(vf, stat_axes)  # No Format 4 locations

    # Strip all Mac platform (platformID=1) name entries — required by GF (no_mac_entries check)
    vf["name"].names = [rec for rec in vf["name"].names if rec.platformID != 1]

    # Fix usWidthClass for proper display in font menus
    # For wdth 50-150 with default 100, use class 5 (Normal/Medium)
    vf["OS/2"].usWidthClass = 5

    # Add variable font name table entries
    name_table = vf["name"]

    # Name ID 25: Variations PostScript Name Prefix (Windows platform only — GF no_mac_entries)
    name_table.setName("Datatype", 25, 3, 1, 0x0409)

    # Note: Name IDs 16/17 (Typographic Family/Subfamily) are not needed
    # for standard variable fonts per Google Fonts guidelines

    return vf


def export_static_instance(vf, location, output_dir, basename, style_name, weight_class, woff2_dir=None):
    """Export a static font instance from a variable font.

    Args:
        vf: variable TTFont
        location: dict of axis tag → value to pin, e.g. {"wght": 700, "wdth": 15}
        output_dir: output directory for TTF files
        basename: font family basename (e.g. "Datatype")
        style_name: style name from NAMED_INSTANCES (e.g. "Black ExtraExpanded")
        weight_class: OS/2 usWeightClass value
        woff2_dir: optional separate output directory for WOFF2 files (defaults to output_dir)
    """
    import copy
    import os

    static = instantiateVariableFont(copy.deepcopy(vf), location)

    # GF Axis Registry weight name lookup
    _WGHT_NAMES = {
        100: "Thin", 200: "ExtraLight", 300: "Light", 400: "Regular",
        500: "Medium", 600: "SemiBold", 700: "Bold", 800: "ExtraBold", 900: "Black",
    }
    # Human-readable width names for nameID 1/16 (no CamelCase — multi-word names use spaces)
    _WDTH_HUMAN = {
        50: "Ultra Condensed", 62.5: "Extra Condensed", 75: "Condensed",
        87.5: "Semi Condensed", 100: "", 112.5: "Semi Expanded",
        125: "Expanded", 150: "Extra Expanded", 200: "Ultra Expanded",
    }
    # Compact width names for PostScript name and filenames (no spaces, CamelCase OK)
    _WDTH_COMPACT = {
        50: "UltraCondensed", 62.5: "ExtraCondensed", 75: "Condensed",
        87.5: "SemiCondensed", 100: "", 112.5: "SemiExpanded",
        125: "Expanded", 150: "ExtraExpanded", 200: "UltraExpanded",
    }

    wght = int(location.get("wght", weight_class))
    wdth = location.get("wdth", 100)
    weight_name = _WGHT_NAMES.get(wght, str(wght))
    human_width = _WDTH_HUMAN.get(wdth, "")
    compact_width = _WDTH_COMPACT.get(wdth, "")

    # Regular (400) and Bold (700) at normal width use the classic 4-style convention:
    # nameID 1 = family basename, nameID 2 = "Regular"/"Bold", no nameID 16/17.
    # All other weights/widths are one-member legacy family groups (nameID 1 includes weight).
    is_classic = wght in (400, 700) and not compact_width

    if is_classic:
        family_name_id1 = basename                       # "Datatype"
        subfamily_id2 = weight_name                      # "Regular" or "Bold"
        full_name = f"{basename} {weight_name}"          # "Datatype Regular", "Datatype Bold"
        ps_name = f"{basename}-{weight_name}"            # "Datatype-Regular", "Datatype-Bold"
        typo_family = None   # nameID 16/17 not set for classic 4-style
        typo_subfamily = None
        if wght == 700:
            fs_selection = 0x00A0   # USE_TYPO_METRICS | BOLD
            mac_style = 0x0001
        else:
            fs_selection = 0x00C0   # USE_TYPO_METRICS | REGULAR
            mac_style = 0
    elif compact_width:
        # Cross-axis: human-readable width precedes weight in name fields
        family_name_id1 = f"{basename} {human_width} {weight_name}"  # "Datatype Extra Expanded Black"
        subfamily_id2 = "Regular"
        full_name = family_name_id1
        ps_name = f"{basename}{compact_width}-{weight_name}"          # "DatatypeExtraExpanded-Black"
        typo_family = f"{basename} {human_width}"                     # "Datatype Extra Expanded"
        typo_subfamily = weight_name                                   # "Black"
        fs_selection = 0x00C0
        mac_style = 0
    else:
        # Weight-only non-standard (Thin, ExtraLight, Light, Medium, SemiBold, ExtraBold, Black)
        family_name_id1 = f"{basename} {weight_name}"   # "Datatype Black"
        subfamily_id2 = "Regular"
        full_name = family_name_id1
        ps_name = f"{basename}-{weight_name}"            # "Datatype-Black"
        typo_family = basename                           # "Datatype"
        typo_subfamily = weight_name                     # "Black"
        fs_selection = 0x00C0
        mac_style = 0

    # Update name table — strip Mac platform entries (GF no_mac_entries requirement)
    name_table = static["name"]
    name_table.names = [r for r in name_table.names if r.platformID != 1]
    name_table.setName(family_name_id1, 1, 3, 1, 0x0409)   # Family Name
    name_table.setName(subfamily_id2, 2, 3, 1, 0x0409)      # Subfamily Name
    name_table.setName(full_name, 4, 3, 1, 0x0409)          # Full Font Name
    name_table.setName(ps_name, 6, 3, 1, 0x0409)            # PostScript Name

    if typo_family is not None:
        name_table.setName(typo_family, 16, 3, 1, 0x0409)   # Typographic Family Name
        name_table.setName(typo_subfamily, 17, 3, 1, 0x0409) # Typographic Subfamily Name
    else:
        # Remove nameID 16/17 — not needed for classic 4-style fonts (Regular, Bold)
        name_table.names = [r for r in name_table.names if r.nameID not in (16, 17)]

    # Update OS/2 weight class
    static["OS/2"].usWeightClass = weight_class

    static["OS/2"].fsSelection = fs_selection
    static["head"].macStyle = mac_style

    os.makedirs(output_dir, exist_ok=True)

    # Filename follows the PostScript name (no spaces) — matches GF canonical_filename spec
    ttf_path = os.path.join(output_dir, f"{ps_name}.ttf")
    static.save(ttf_path)
    print(f"    {ttf_path}")

    # WOFF2 export to separate directory if specified
    woff2_output_dir = woff2_dir if woff2_dir else output_dir
    os.makedirs(woff2_output_dir, exist_ok=True)

    static.flavor = "woff2"
    woff2_path = os.path.join(woff2_output_dir, f"{ps_name}.woff2")
    static.save(woff2_path)
    print(f"    {woff2_path}")
