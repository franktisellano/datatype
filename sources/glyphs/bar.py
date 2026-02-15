"""Bar chart glyph drawing and OpenType feature generation."""

from sources.config import (
    CHART_HEIGHT, CHART_BASELINE,
    FontParams,
)


def _draw_rect(pen, x0, y0, x1, y1):
    pen.moveTo((x0, y0))
    pen.lineTo((x1, y0))
    pen.lineTo((x1, y1))
    pen.lineTo((x0, y1))
    pen.closePath()


def draw_bar_glyphs(glyph_data, params=None):
    """Add bar chart glyphs to glyph_data dict.

    Glyphs created:
    - bar_start: zero-width marker
    - bar_end: zero-width marker (adds right padding)
    - bar_sep: small gap between bars
    - bar_d0..bar_d9: intermediate digit glyphs (zero-width, never rendered)
    - bar_h0..bar_h{max_value}: individual bars at proportional heights
    """
    if params is None:
        params = FontParams()

    bar_width = params.bar_width
    bar_fill = params.bar_fill
    sep_width = params.sep_width
    end_width = params.end_width
    max_value = params.max_value
    drawn_w = max(round(bar_width * bar_fill), 1)
    x_offset = 0  # Left-align bars instead of centering

    # bar_start - zero width trigger glyph
    glyph_data["bar_start"] = (0, None)

    # bar_end - small padding to close the chart
    glyph_data["bar_end"] = (end_width, None)

    # bar_sep - small spacer between bars
    glyph_data["bar_sep"] = (sep_width, None)

    # Intermediate digit glyphs (zero-width, never rendered)
    for d in range(10):
        glyph_data[f"bar_d{d}"] = (0, None)

    # bar_h0 - empty bar (has width but no drawing)
    glyph_data["bar_h0"] = (bar_width, None)

    # bar_h1 through bar_h{max_value}
    for h in range(1, max_value + 1):
        name = f"bar_h{h}"
        height = int(CHART_HEIGHT * h / max_value)

        def make_draw(xo, dw, ht):
            def draw(pen):
                _draw_rect(pen, xo, CHART_BASELINE, xo + dw, CHART_BASELINE + ht)
            return draw

        glyph_data[name] = (bar_width, make_draw(x_offset, drawn_w, height))


def generate_bar_feature_code(max_value=100):
    """Generate OpenType feature code for bar chart substitution.

    Uses intermediate digits + combine strategy:
    1. Ligature: {b: → bar_start
    2. Propagation: digits → bar_dN, commas → bar_sep
    3. Combine (liga): adjacent bar_dN sequences → bar_hNN
    4. Combine (single): remaining lone bar_dN → bar_hN
    5. Close: } → bar_end

    Returns:
        feature code string
    """
    lines = []

    # --- Glyph classes ---
    bar_prop_ctx = ["bar_start", "bar_sep"] + [f"bar_d{i}" for i in range(10)]
    lines.append(f"@bar_prop_ctx = [{' '.join(bar_prop_ctx)}];")

    bar_close_ctx = ["bar_start", "bar_sep"] + [f"bar_h{i}" for i in range(max_value + 1)]
    lines.append(f"@bar_close_ctx = [{' '.join(bar_close_ctx)}];")

    bar_digits = [f"uni003{d}" for d in range(10)]
    lines.append(f"@bar_digits = [{' '.join(bar_digits)}];")
    lines.append("")

    # --- Lookup: opening ligature {b: → bar_start ---
    lines.append("lookup bar_open {")
    lines.append("  sub uni007B uni0062 uni003A by bar_start;")
    lines.append("} bar_open;")
    lines.append("")

    # --- Lookup: digit → intermediate ---
    lines.append("lookup bar_to_intermediate {")
    for d in range(10):
        lines.append(f"  sub uni003{d} by bar_d{d};")
    lines.append("} bar_to_intermediate;")
    lines.append("")

    # --- Lookup: comma → bar_sep ---
    lines.append("lookup bar_comma {")
    lines.append("  sub uni002C by bar_sep;")
    lines.append("} bar_comma;")
    lines.append("")

    # --- Lookup: propagation (calt chain) ---
    lines.append("lookup bar_propagate {")
    lines.append("  sub @bar_prop_ctx @bar_digits' lookup bar_to_intermediate;")
    lines.append("  sub @bar_prop_ctx uni002C' lookup bar_comma;")
    lines.append("} bar_propagate;")
    lines.append("")

    # --- Lookup: combine ligature (multi-digit → value) ---
    lines.append("lookup bar_combine_liga {")
    if max_value >= 100:
        lines.append("  sub bar_d1 bar_d0 bar_d0 by bar_h100;")
    for tens in range(1, 10):
        for ones in range(0, 10):
            val = tens * 10 + ones
            if val > max_value:
                break
            lines.append(f"  sub bar_d{tens} bar_d{ones} by bar_h{val};")
    lines.append("} bar_combine_liga;")
    lines.append("")

    # --- Lookup: combine single (lone intermediate → value) ---
    lines.append("lookup bar_combine_single {")
    for d in range(min(10, max_value + 1)):
        lines.append(f"  sub bar_d{d} by bar_h{d};")
    lines.append("} bar_combine_single;")
    lines.append("")

    # --- Lookup: close substitution ---
    lines.append("lookup bar_close_sub {")
    lines.append("  sub uni007D by bar_end;")
    lines.append("} bar_close_sub;")
    lines.append("")

    # --- Lookup: close (calt chain) ---
    lines.append("lookup bar_close {")
    lines.append("  sub @bar_close_ctx uni007D' lookup bar_close_sub;")
    lines.append("} bar_close;")
    lines.append("")

    return "\n".join(lines)
