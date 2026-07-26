"""Pie chart glyph drawing and OpenType feature generation.

Pie charts represent a single percentage: {pie:75} = 75% filled.
Drawn as a filled circle with a wedge cut out for the unfilled portion.
"""

import math
from sources.config import PIE_RADIUS, PIE_CENTER_X, PIE_CENTER_Y, PIE_STROKE, FontParams


def _arc_points(cx, cy, r, start_angle, end_angle):
    """Generate on-curve and control points for a quadratic Bezier arc."""
    points = []
    angle_span = end_angle - start_angle
    n = max(1, int(math.ceil(abs(angle_span) / (math.pi / 4))))

    for i in range(n):
        a0 = start_angle + angle_span * i / n
        a1 = start_angle + angle_span * (i + 1) / n
        mid = (a0 + a1) / 2
        half = (a1 - a0) / 2
        cos_half = math.cos(half)
        if abs(cos_half) < 0.001:
            cos_half = 0.001
        cp_r = r / cos_half

        if i == 0:
            points.append((
                int(cx + r * math.cos(a0)),
                int(cy + r * math.sin(a0))
            ))
        points.append((
            int(cx + cp_r * math.cos(mid)),
            int(cy + cp_r * math.sin(mid))
        ))
        points.append((
            int(cx + r * math.cos(a1)),
            int(cy + r * math.sin(a1))
        ))

    return points


def _draw_arc_path(pen, cx, cy, r, start_angle, end_angle):
    """Draw arc curve segments (assumes pen is already at start position)."""
    pts = _arc_points(cx, cy, r, start_angle, end_angle)
    pen.lineTo(pts[0])
    i = 1
    while i < len(pts) - 1:
        pen.qCurveTo(pts[i], pts[i + 1])
        i += 2


def _draw_empty_circle(pen, cx, cy, r, stroke=30):
    """Draw an empty circle (ring) for pie_0."""
    r_inner = r - stroke
    # Outer circle (clockwise)
    pts_outer = _arc_points(cx, cy, r, 2 * math.pi, 0)
    pen.moveTo(pts_outer[0])
    i = 1
    while i < len(pts_outer) - 1:
        pen.qCurveTo(pts_outer[i], pts_outer[i + 1])
        i += 2
    pen.closePath()
    # Inner circle (counter-clockwise = hole)
    pts_inner = _arc_points(cx, cy, r_inner, 0, 2 * math.pi)
    pen.moveTo(pts_inner[0])
    i = 1
    while i < len(pts_inner) - 1:
        pen.qCurveTo(pts_inner[i], pts_inner[i + 1])
        i += 2
    pen.closePath()


def _draw_full_circle(pen, cx, cy, r):
    """Draw a fully filled circle for pie_100."""
    pts = _arc_points(cx, cy, r, 2 * math.pi, 0)
    pen.moveTo(pts[0])
    i = 1
    while i < len(pts) - 1:
        pen.qCurveTo(pts[i], pts[i + 1])
        i += 2
    pen.closePath()


def _draw_pie_glyph(pen, pct, stroke=PIE_STROKE):
    """Draw a pie chart for a given percentage.

    The filled portion is drawn as a wedge from center.
    The full circle outline is drawn, then the unfilled wedge is cut out
    by drawing it as a counter-clockwise (hole) contour.

    Simpler approach: draw the filled wedge as a solid shape.
    """
    cx, cy, r = PIE_CENTER_X, PIE_CENTER_Y, PIE_RADIUS

    if pct == 0:
        _draw_empty_circle(pen, cx, cy, r, stroke=stroke)
        return

    if pct >= 100:
        _draw_full_circle(pen, cx, cy, r)
        return

    # The filled portion: wedge from 12 o'clock going clockwise
    filled_angle = 2 * math.pi * pct / 100
    start = math.pi / 2          # 12 o'clock
    end = start - filled_angle   # clockwise

    # Draw the filled wedge (center -> arc -> center)
    pen.moveTo((cx, cy))
    _draw_arc_path(pen, cx, cy, r, start, end)
    pen.closePath()

    # Draw the unfilled portion as just an arc (no fill, but we need
    # to represent it as an outline ring segment).
    # Actually for monochrome: draw a thin arc for the unfilled portion
    # to complete the circle outline.
    unfilled_start = end
    unfilled_end = start - 2 * math.pi  # complete the circle

    # Draw as a thin ring segment
    r_inner = r - stroke

    # Outer arc (clockwise direction for the unfilled portion)
    pts_outer = _arc_points(cx, cy, r, unfilled_start, unfilled_end)
    # Inner arc (reverse direction to create the ring)
    pts_inner = _arc_points(cx, cy, r_inner, unfilled_end, unfilled_start)

    pen.moveTo(pts_outer[0])
    i = 1
    while i < len(pts_outer) - 1:
        pen.qCurveTo(pts_outer[i], pts_outer[i + 1])
        i += 2
    # Connect to inner arc
    pen.lineTo(pts_inner[0])
    i = 1
    while i < len(pts_inner) - 1:
        pen.qCurveTo(pts_inner[i], pts_inner[i + 1])
        i += 2
    pen.closePath()


def draw_pie_glyphs(glyph_data, params=None):
    """Add pie chart glyphs: pie_0 through pie_100."""
    if params is None:
        params = FontParams()
    stroke = params.pie_stroke
    width = int(PIE_CENTER_X + PIE_RADIUS + 30)

    for pct in range(0, 101):
        name = f"pie_{pct}"

        def make_draw(p, s):
            def draw(pen):
                _draw_pie_glyph(pen, p, stroke=s)
            return draw

        glyph_data[name] = (width, make_draw(pct, stroke))


def generate_pie_feature_code():
    """Generate OpenType feature code for pie chart substitution.

    Uses direct ligature substitution:
    - {pie:X}  for X in 1-9     -> pie_X       (9 rules)
    - {pie:XY} for XY in 10-99  -> pie_XY      (90 rules)
    """
    lines = []
    lines.append("lookup pie_liga {")

    # {p:100} - three-digit first (longest match priority)
    seq_100 = "uni007B uni0070 uni003A uni0031 uni0030 uni0030 uni007D"
    lines.append(f"  sub {seq_100} by pie_100;")

    # {p:XY} - two-digit (10-99)
    # { = 007B, p = 0070, : = 003A
    for tens in range(1, 10):
        for ones in range(0, 10):
            pct = tens * 10 + ones
            if pct > 99:
                break
            tens_glyph = f"uni003{tens}"
            ones_glyph = f"uni003{ones}"
            seq = f"uni007B uni0070 uni003A {tens_glyph} {ones_glyph} uni007D"
            lines.append(f"  sub {seq} by pie_{pct};")

    # {p:X} - single-digit (0-9)
    for d in range(0, 10):
        seq = f"uni007B uni0070 uni003A uni003{d} uni007D"
        lines.append(f"  sub {seq} by pie_{d};")

    lines.append("} pie_liga;")
    lines.append("")

    return "\n".join(lines)
