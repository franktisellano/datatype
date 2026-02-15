"""Sparkline glyph drawing and OpenType feature generation."""

import math
from src.config import (
    CHART_HEIGHT, CHART_BASELINE, SPARK_LINE_THICKNESS,
    MAX_VALUE, FontParams,
)

SEG_WIDTH = 200      # width of each connecting segment
POINT_WIDTH = 16     # width of the trailing endpoint (just a tiny cap, no dot)


def _height_for_value(v, max_value):
    """Convert data value to Y coordinate."""
    margin = 60
    usable = CHART_HEIGHT - 2 * margin
    if max_value == 0:
        return int(CHART_BASELINE + margin)
    return int(CHART_BASELINE + margin + usable * v / max_value)


def _draw_circle(pen, cx, cy, r):
    """Draw a filled circle using 8 quadratic Bezier arcs (CW winding)."""
    if r < 1:
        return
    n = 8
    pts = []
    for i in range(n):
        # Negative angles = clockwise in Y-up coords (TrueType convention)
        a0 = -2 * math.pi * i / n
        a1 = -2 * math.pi * (i + 1) / n
        mid = (a0 + a1) / 2
        half = abs(a1 - a0) / 2
        cp_r = r / math.cos(half)
        if i == 0:
            pts.append((round(cx + r * math.cos(a0)), round(cy + r * math.sin(a0))))
        pts.append((round(cx + cp_r * math.cos(mid)), round(cy + cp_r * math.sin(mid))))
        if i < n - 1:
            pts.append((round(cx + r * math.cos(a1)), round(cy + r * math.sin(a1))))
        else:
            pts.append(pts[0])  # close exactly to start (avoids float rounding mismatch)
    pen.moveTo(pts[0])
    i = 1
    while i < len(pts) - 1:
        pen.qCurveTo(pts[i], pts[i + 1])
        i += 2
    pen.closePath()


def _draw_semicircle_arc(pen, cx, cy, r, start_angle, end_point, n_arcs=4, clockwise=False):
    """Draw a 180° arc using quadratic Bezier curves.

    Sweeps from start_angle. Assumes pen is already at the arc start point.
    end_point is the exact target coordinate for the final on-curve point
    (avoids floating-point drift from trig round-trips).
    clockwise: if True, sweep CW (negative angles); if False, sweep CCW.
    """
    arc_span = -math.pi if clockwise else math.pi
    arc_angle = arc_span / n_arcs
    half = abs(arc_angle) / 2
    cp_r = r / math.cos(half)

    for i in range(n_arcs):
        a0 = start_angle + i * arc_angle
        a1 = start_angle + (i + 1) * arc_angle
        mid = (a0 + a1) / 2

        control = (round(cx + cp_r * math.cos(mid)), round(cy + cp_r * math.sin(mid)))
        if i == n_arcs - 1:
            on_curve = end_point
        else:
            on_curve = (round(cx + r * math.cos(a1)), round(cy + r * math.sin(a1)))
        pen.qCurveTo(control, on_curve)


def draw_sparkline_glyphs(glyph_data, params=None):
    """Add sparkline glyphs to glyph_data dict.

    Glyphs created:
    - spark_start: zero-width marker
    - spark_end: small padding
    - spark_sep: zero-width separator
    - spark_d0..spark_d9: intermediate digit glyphs (zero-width, never rendered)
    - spark_p0..spark_p{max_value}: round endpoint dots
    - spark_0_to_0..spark_{max}_to_{max}: stadium-shaped line segments
    """
    if params is None:
        params = FontParams()

    max_value = params.max_value
    seg_width = params.seg_width
    half_t = params.line_thickness // 2

    glyph_data["spark_start"] = (0, None)
    glyph_data["spark_end"] = (20, None)
    glyph_data["spark_sep"] = (0, None)

    # Intermediate digit glyphs (zero-width, never rendered)
    for d in range(10):
        glyph_data[f"spark_d{d}"] = (0, None)

    # Endpoint glyphs — full circle at the last data point's height
    for v in range(0, max_value + 1):
        name = f"spark_p{v}"
        cy = _height_for_value(v, max_value)

        def make_cap(c_y, r):
            def draw(pen):
                _draw_circle(pen, 0, c_y, r)
            return draw

        glyph_data[name] = (params.point_width, make_cap(cy, half_t))

    # Segment glyphs: circle at start + rectangle body + circle at end.
    # Three separate CW contours (matching canvas tool geometry exactly).
    for a in range(0, max_value + 1):
        for b in range(0, max_value + 1):
            name = f"spark_{a}_to_{b}"
            y_start = _height_for_value(a, max_value)
            y_end = _height_for_value(b, max_value)

            def make_segment(ys, ye, sw, ht):
                def draw(pen):
                    if ht < 1:
                        return

                    # Circle at start point
                    _draw_circle(pen, 0, ys, ht)

                    # Circle at end point
                    _draw_circle(pen, sw, ye, ht)

                    # Rectangle body connecting them
                    dx = float(sw)
                    dy = float(ye - ys)
                    length = math.sqrt(dx * dx + dy * dy)

                    nx = -dy / length
                    ny = dx / length
                    ox = ht * nx
                    oy = ht * ny

                    c1 = (round(0 - ox), round(ys - oy))
                    c2 = (round(sw - ox), round(ye - oy))
                    c3 = (round(sw + ox), round(ye + oy))
                    c4 = (round(0 + ox), round(ys + oy))

                    # Rectangle CW
                    pen.moveTo(c1)
                    pen.lineTo(c4)
                    pen.lineTo(c3)
                    pen.lineTo(c2)
                    pen.closePath()
                return draw

            glyph_data[name] = (seg_width, make_segment(y_start, y_end, seg_width, half_t))


def generate_sparkline_feature_code(max_value=100):
    """Generate OpenType feature code for sparkline substitution.

    Uses intermediate digits + combine strategy (same as bars):
    1. Ligature: {l: → spark_start
    2. Propagation: digits → spark_dN, commas → spark_sep
    3. Combine (liga): adjacent spark_dN sequences → spark_pNN
    4. Combine (single): remaining lone spark_dN → spark_pN
    5. Close: } → spark_end
    6. Pair resolution: spark_pA spark_sep spark_pB → spark_A_to_B spark_sep spark_pB
    """
    lines = []

    # --- Glyph classes ---
    spark_prop_ctx = ["spark_start", "spark_sep"] + [f"spark_d{i}" for i in range(10)]
    lines.append(f"@spark_prop_ctx = [{' '.join(spark_prop_ctx)}];")

    spark_close_ctx = ["spark_start", "spark_sep"] + [f"spark_p{i}" for i in range(max_value + 1)]
    lines.append(f"@spark_close_ctx = [{' '.join(spark_close_ctx)}];")

    spark_points = [f"spark_p{i}" for i in range(max_value + 1)]
    lines.append(f"@spark_points = [{' '.join(spark_points)}];")

    spark_digits = [f"uni003{d}" for d in range(10)]
    lines.append(f"@spark_digits = [{' '.join(spark_digits)}];")
    lines.append("")

    # --- Lookup: opening ligature {l: → spark_start ---
    lines.append("lookup spark_open {")
    lines.append("  sub uni007B uni006C uni003A by spark_start;")
    lines.append("} spark_open;")
    lines.append("")

    # --- Lookup: digit → intermediate ---
    lines.append("lookup spark_to_intermediate {")
    for d in range(10):
        lines.append(f"  sub uni003{d} by spark_d{d};")
    lines.append("} spark_to_intermediate;")
    lines.append("")

    # --- Lookup: comma → spark_sep ---
    lines.append("lookup spark_comma {")
    lines.append("  sub uni002C by spark_sep;")
    lines.append("} spark_comma;")
    lines.append("")

    # --- Lookup: propagation (calt chain) ---
    lines.append("lookup spark_propagate {")
    lines.append("  sub @spark_prop_ctx @spark_digits' lookup spark_to_intermediate;")
    lines.append("  sub @spark_prop_ctx uni002C' lookup spark_comma;")
    lines.append("} spark_propagate;")
    lines.append("")

    # --- Lookup: combine ligature (multi-digit → value) ---
    lines.append("lookup spark_combine_liga {")
    if max_value >= 100:
        lines.append("  sub spark_d1 spark_d0 spark_d0 by spark_p100;")
    for tens in range(1, 10):
        for ones in range(0, 10):
            val = tens * 10 + ones
            if val > max_value:
                break
            lines.append(f"  sub spark_d{tens} spark_d{ones} by spark_p{val};")
    lines.append("} spark_combine_liga;")
    lines.append("")

    # --- Lookup: combine single (lone intermediate → value) ---
    lines.append("lookup spark_combine_single {")
    for d in range(min(10, max_value + 1)):
        lines.append(f"  sub spark_d{d} by spark_p{d};")
    lines.append("} spark_combine_single;")
    lines.append("")

    # --- Lookup: close substitution ---
    lines.append("lookup spark_close_sub {")
    lines.append("  sub uni007D by spark_end;")
    lines.append("} spark_close_sub;")
    lines.append("")

    # --- Lookup: close (calt chain) ---
    lines.append("lookup spark_close {")
    lines.append("  sub @spark_close_ctx uni007D' lookup spark_close_sub;")
    lines.append("} spark_close;")
    lines.append("")

    # --- Pair resolution lookups ---
    for b in range(max_value + 1):
        lines.append(f"lookup spark_resolve_to_{b} {{")
        for a in range(max_value + 1):
            lines.append(f"  sub spark_p{a} by spark_{a}_to_{b};")
        lines.append(f"}} spark_resolve_to_{b};")
        lines.append("")

    # --- Pair resolution chain ---
    lines.append("lookup spark_resolve_pairs {")
    for b in range(max_value + 1):
        lines.append(f"  sub @spark_points' lookup spark_resolve_to_{b} spark_sep spark_p{b};")
    lines.append("} spark_resolve_pairs;")
    lines.append("")

    return "\n".join(lines)
