"""Base ASCII glyphs: .notdef, space, printable ASCII, punctuation."""

import math
from sources.config import UPM, ASCENDER, ASCII_WIDTH, SPACE_WIDTH, DIGIT_WIDTH, CAP_HEIGHT, X_HEIGHT

# Design constants for refined letterforms
STROKE_WEIGHT = 80          # Base stroke thickness (unchanged)
CORNER_RADIUS = 30          # Subtle rounding at intersections (3/8 of stroke)
INNER_CORNER_RADIUS = 15    # Tighter radius for inner corners
CHAMFER_RADIUS = 20         # Smaller radius for terminals/cuts
TERMINAL_CUT = 45           # Angle for terminal cuts (degrees)


def _draw_rect(pen, x0, y0, x1, y1):
    """Draw a rectangle (clockwise winding for outer contours)."""
    pen.moveTo((x0, y0))
    pen.lineTo((x1, y0))
    pen.lineTo((x1, y1))
    pen.lineTo((x0, y1))
    pen.closePath()


def _draw_rect_ccw(pen, x0, y0, x1, y1):
    """Draw a rectangle with counter-clockwise winding (for holes/cutouts).

    TrueType convention: outer contours CW, holes CCW when Y-axis points up.
    Reverses direction from CW rectangle.
    """
    pen.moveTo((x0, y0))
    pen.lineTo((x0, y1))  # up (left edge)
    pen.lineTo((x1, y1))  # right (top edge)
    pen.lineTo((x1, y0))  # down (right edge)
    pen.closePath()  # implicitly back to (x0, y0)


def _draw_rounded_rect(pen, x0, y0, x1, y1, radius=CORNER_RADIUS, ccw=False):
    """Draw rectangle with rounded corners using quadratic curves.

    Args:
        pen: FontTools pen object
        x0, y0: Bottom-left corner
        x1, y1: Top-right corner
        radius: Corner radius (default: CORNER_RADIUS)
        ccw: If True, draw counter-clockwise (for holes). Default False (clockwise)

    Winding: Clockwise by default (outer contours), CCW if ccw=True (holes)
    """
    # Clamp radius to avoid overlap
    max_radius = min((x1 - x0) / 2, (y1 - y0) / 2)
    r = min(radius, max_radius)

    if not ccw:
        # Clockwise winding (for outer contours)
        pen.moveTo((x0 + r, y0))
        pen.lineTo((x1 - r, y0))
        pen.qCurveTo((x1, y0), (x1, y0 + r))
        pen.lineTo((x1, y1 - r))
        pen.qCurveTo((x1, y1), (x1 - r, y1))
        pen.lineTo((x0 + r, y1))
        pen.qCurveTo((x0, y1), (x0, y1 - r))
        pen.lineTo((x0, y0 + r))
        pen.qCurveTo((x0, y0), (x0 + r, y0))
    else:
        # Counter-clockwise winding (for holes/cutouts)
        pen.moveTo((x0 + r, y0))
        pen.qCurveTo((x0, y0), (x0, y0 + r))
        pen.lineTo((x0, y1 - r))
        pen.qCurveTo((x0, y1), (x0 + r, y1))
        pen.lineTo((x1 - r, y1))
        pen.qCurveTo((x1, y1), (x1, y1 - r))
        pen.lineTo((x1, y0 + r))
        pen.qCurveTo((x1, y0), (x1 - r, y0))
        pen.lineTo((x0 + r, y0))

    pen.closePath()


def _draw_vertical_stroke(pen, x_center, y0, y1, thickness=STROKE_WEIGHT,
                          top_radius=CORNER_RADIUS, bottom_radius=CORNER_RADIUS):
    """Vertical stroke with rounded ends.

    Args:
        pen: FontTools pen object
        x_center: Horizontal center of stroke
        y0: Bottom y coordinate
        y1: Top y coordinate
        thickness: Stroke width
        top_radius: Radius for top corners
        bottom_radius: Radius for bottom corners
    """
    half_t = thickness // 2
    radius = min(top_radius, bottom_radius)
    _draw_rounded_rect(pen, x_center - half_t, y0, x_center + half_t, y1, radius=radius)


def _draw_horizontal_stroke(pen, x0, x1, y_center, thickness=STROKE_WEIGHT,
                            left_radius=CORNER_RADIUS, right_radius=CORNER_RADIUS):
    """Horizontal stroke with rounded ends.

    Args:
        pen: FontTools pen object
        x0: Left x coordinate
        x1: Right x coordinate
        y_center: Vertical center of stroke
        thickness: Stroke height
        left_radius: Radius for left corners
        right_radius: Radius for right corners
    """
    half_t = thickness // 2
    radius = min(left_radius, right_radius)
    _draw_rounded_rect(pen, x0, y_center - half_t, x1, y_center + half_t, radius=radius)


def _draw_circle(pen, cx, cy, r):
    """Draw a filled circle using 8 quadratic Bezier arcs (CW winding).

    Ported from sparkline.py - used for zero's center dot.
    """
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


# Simple geometric letterforms - maps char to a draw function
# Each returns (width, draw_func) where draw_func takes a pen

def _make_notdef(pen):
    """Draw .notdef (empty rectangle)."""
    _draw_rect(pen, 50, 0, 450, CAP_HEIGHT)
    _draw_rect(pen, 100, 50, 400, CAP_HEIGHT - 50)  # inner cutout


def _make_block_letter(pen, char):
    """Draw a simple block letter glyph for the given character.

    Uses basic geometric shapes - rectangles and lines.
    """
    w = ASCII_WIDTH
    h = CAP_HEIGHT
    t = 80  # stroke thickness

    upper = char.upper() if char.isalpha() else char

    # Digits
    if char == '0':
        # Outer rectangle with rounded corners
        _draw_rounded_rect(pen, 50, 0, w - 50, h, radius=CORNER_RADIUS)
        # Inner cutout - CCW winding to create hole
        _draw_rect_ccw(pen, 50 + t, t, w - 50 - t, h - t)
        # Vertical centered capsule slash to distinguish from O (half size with rounded ends)
        slash_thickness = int(t * 0.5)
        slash_h = int(h * 0.18)  # Half of previous size
        slash_center_y = h // 2
        # Use vertical stroke helper for capsule shape with rounded ends
        _draw_vertical_stroke(pen, w // 2, slash_center_y - slash_h, slash_center_y + slash_h,
                            thickness=slash_thickness, top_radius=slash_thickness//2,
                            bottom_radius=slash_thickness//2)
    elif char == '1':
        # Center vertical stroke
        _draw_vertical_stroke(pen, w // 2, 0, h, thickness=t)
        # Bottom horizontal base
        _draw_horizontal_stroke(pen, 50, w - 50, t // 2, thickness=t)
        # Angled hat at 30 degrees (top-left to top-center) - simple filled triangle
        import math
        hat_length = int(t * 1.5)
        angle_rad = math.radians(30)
        dx = int(hat_length * math.cos(angle_rad))
        dy = int(hat_length * math.sin(angle_rad))
        # Hat stroke from top-left angled up to center top
        pen.moveTo((w // 2 - t // 2, h))
        pen.lineTo((w // 2 - t // 2 - dx, h - dy))
        pen.lineTo((w // 2 + t // 2 - dx, h - dy))
        pen.lineTo((w // 2 + t // 2, h))
        pen.closePath()
    elif char == '2':
        # Bottom bar
        _draw_horizontal_stroke(pen, 50, w - 50, t // 2, thickness=t)
        # Left lower vertical
        _draw_vertical_stroke(pen, 50 + t // 2, 0, h // 2, thickness=t)
        # Middle horizontal
        _draw_horizontal_stroke(pen, 50, w - 50, h // 2, thickness=t)
        # Right upper vertical
        _draw_vertical_stroke(pen, w - 50 - t // 2, h // 2, h, thickness=t)
        # Top bar
        _draw_horizontal_stroke(pen, 50, w - 50, h - t // 2, thickness=t)
    elif char == '3':
        # Right vertical stroke
        _draw_vertical_stroke(pen, w - 50 - t // 2, 0, h, thickness=t)
        # Bottom bar
        _draw_horizontal_stroke(pen, 50, w - 50, t // 2, thickness=t)
        # Middle horizontal
        _draw_horizontal_stroke(pen, 50, w - 50, h // 2, thickness=t)
        # Top bar
        _draw_horizontal_stroke(pen, 50, w - 50, h - t // 2, thickness=t)
    elif char == '4':
        # Right vertical stroke
        _draw_vertical_stroke(pen, w - 50 - t // 2, 0, h, thickness=t)
        # Left upper vertical
        _draw_vertical_stroke(pen, 50 + t // 2, h // 2, h, thickness=t)
        # Middle horizontal
        _draw_horizontal_stroke(pen, 50, w - 50, h // 2, thickness=t)
    elif char == '5':
        # Bottom bar
        _draw_horizontal_stroke(pen, 50, w - 50, t // 2, thickness=t)
        # Right lower vertical
        _draw_vertical_stroke(pen, w - 50 - t // 2, 0, h // 2, thickness=t)
        # Middle horizontal
        _draw_horizontal_stroke(pen, 50, w - 50, h // 2, thickness=t)
        # Left upper vertical
        _draw_vertical_stroke(pen, 50 + t // 2, h // 2, h, thickness=t)
        # Top bar
        _draw_horizontal_stroke(pen, 50, w - 50, h - t // 2, thickness=t)
    elif char == '6':
        # Left vertical stroke
        _draw_vertical_stroke(pen, 50 + t // 2, 0, h, thickness=t)
        # Bottom bar
        _draw_horizontal_stroke(pen, 50, w - 50, t // 2, thickness=t)
        # Right lower vertical
        _draw_vertical_stroke(pen, w - 50 - t // 2, 0, h // 2, thickness=t)
        # Middle horizontal
        _draw_horizontal_stroke(pen, 50, w - 50, h // 2, thickness=t)
        # Top bar
        _draw_horizontal_stroke(pen, 50, w - 50, h - t // 2, thickness=t)
    elif char == '7':
        # Right vertical stroke
        _draw_vertical_stroke(pen, w - 50 - t // 2, 0, h, thickness=t)
        # Top bar
        _draw_horizontal_stroke(pen, 50, w - 50, h - t // 2, thickness=t)
    elif char == '8':
        # Use the old B design (vertical left + 3 horizontals + 2 right verticals)
        # Left vertical stroke
        _draw_vertical_stroke(pen, 50 + t // 2, 0, h, thickness=t)
        # Bottom horizontal
        _draw_horizontal_stroke(pen, 50, w - 50, t // 2, thickness=t)
        # Top horizontal
        _draw_horizontal_stroke(pen, 50, w - 50, h - t // 2, thickness=t)
        # Middle horizontal
        _draw_horizontal_stroke(pen, 50, w - 50, h // 2, thickness=t)
        # Right upper vertical (rounded bowl)
        _draw_vertical_stroke(pen, w - 50 - t // 2, h // 2, h, thickness=t)
        # Right lower vertical (rounded bowl)
        _draw_vertical_stroke(pen, w - 50 - t // 2, 0, h // 2, thickness=t)
    elif char == '9':
        # Right vertical stroke
        _draw_vertical_stroke(pen, w - 50 - t // 2, 0, h, thickness=t)
        # Left upper vertical
        _draw_vertical_stroke(pen, 50 + t // 2, h // 2, h, thickness=t)
        # Middle horizontal
        _draw_horizontal_stroke(pen, 50, w - 50, h // 2, thickness=t)
        # Top bar
        _draw_horizontal_stroke(pen, 50, w - 50, h - t // 2, thickness=t)
    # Letters (uppercase block shapes)
    elif upper == 'A':
        # Left vertical stroke
        _draw_vertical_stroke(pen, 50 + t // 2, 0, h, thickness=t)
        # Right vertical stroke
        _draw_vertical_stroke(pen, w - 50 - t // 2, 0, h, thickness=t)
        # Top horizontal with rounded corners
        _draw_horizontal_stroke(pen, 50, w - 50, h - t // 2, thickness=t)
        # Crossbar at mid-height with rounded corners
        _draw_horizontal_stroke(pen, 50, w - 50, h // 2, thickness=t)
    elif upper == 'B':
        # Outer rounded rectangle
        _draw_rounded_rect(pen, 50, 0, w - 50, h, radius=CORNER_RADIUS)
        # Upper inner cutout - CCW winding (with indent on left)
        indent = int(t * 0.4)
        _draw_rect_ccw(pen, 50 + t + indent, h // 2 + t // 2, w - 50 - t, h - t)
        # Lower inner cutout - CCW winding (with indent on left)
        _draw_rect_ccw(pen, 50 + t + indent, t, w - 50 - t, h // 2 - t // 2)
    elif upper == 'C':
        # Left vertical stroke
        _draw_vertical_stroke(pen, 50 + t // 2, 0, h, thickness=t)
        # Bottom horizontal with angled right terminal (45° cut)
        cut_offset = int(t * 0.7)  # 45° diagonal offset
        pen.moveTo((50, 0))
        pen.lineTo((w - 50 - cut_offset, 0))
        pen.lineTo((w - 50, cut_offset))
        pen.lineTo((w - 50, t))
        pen.lineTo((50 + t, t))
        pen.lineTo((50 + t, 0))
        pen.closePath()
        # Top horizontal with angled right terminal (45° cut)
        pen.moveTo((50, h - t))
        pen.lineTo((w - 50, h - t))
        pen.lineTo((w - 50 - cut_offset, h))
        pen.lineTo((50, h))
        pen.lineTo((50, h - t))
        pen.closePath()
    elif upper == 'D':
        # Left vertical stroke
        _draw_vertical_stroke(pen, 50 + t // 2, 0, h, thickness=t)
        # Bottom horizontal (shorter)
        _draw_horizontal_stroke(pen, 50, w - 100, t // 2, thickness=t)
        # Top horizontal (shorter)
        _draw_horizontal_stroke(pen, 50, w - 100, h - t // 2, thickness=t)
        # Right vertical (rounded bowl)
        _draw_vertical_stroke(pen, w - 50 - t // 2, 0, h, thickness=t)
    elif upper == 'E':
        # Left vertical stroke
        _draw_vertical_stroke(pen, 50 + t // 2, 0, h, thickness=t)
        # Bottom horizontal with angled terminal
        cut_offset = int(t * 0.7)
        pen.moveTo((50, 0))
        pen.lineTo((w - 50 - cut_offset, 0))
        pen.lineTo((w - 50, cut_offset))
        pen.lineTo((w - 50, t))
        pen.lineTo((50 + t, t))
        pen.lineTo((50 + t, 0))
        pen.closePath()
        # Top horizontal with angled terminal
        pen.moveTo((50, h - t))
        pen.lineTo((w - 50, h - t))
        pen.lineTo((w - 50 - cut_offset, h))
        pen.lineTo((50, h))
        pen.lineTo((50, h - t))
        pen.closePath()
        # Middle horizontal (shorter, with rounded end)
        _draw_horizontal_stroke(pen, 50, w - 100, h // 2, thickness=t)
    elif upper == 'F':
        # Left vertical stroke
        _draw_vertical_stroke(pen, 50 + t // 2, 0, h, thickness=t)
        # Top horizontal with angled terminal
        cut_offset = int(t * 0.7)
        pen.moveTo((50, h - t))
        pen.lineTo((w - 50, h - t))
        pen.lineTo((w - 50 - cut_offset, h))
        pen.lineTo((50, h))
        pen.lineTo((50, h - t))
        pen.closePath()
        # Middle horizontal (shorter, with rounded end)
        _draw_horizontal_stroke(pen, 50, w - 100, h // 2, thickness=t)
    elif upper == 'G':
        # Similar to C but with horizontal bar from center to right edge
        # Left vertical stroke
        _draw_vertical_stroke(pen, 50 + t // 2, 0, h, thickness=t)
        # Bottom horizontal with angled right terminal
        cut_offset = int(t * 0.7)
        pen.moveTo((50, 0))
        pen.lineTo((w - 50 - cut_offset, 0))
        pen.lineTo((w - 50, cut_offset))
        pen.lineTo((w - 50, t))
        pen.lineTo((50 + t, t))
        pen.lineTo((50 + t, 0))
        pen.closePath()
        # Top horizontal with angled right terminal
        pen.moveTo((50, h - t))
        pen.lineTo((w - 50, h - t))
        pen.lineTo((w - 50 - cut_offset, h))
        pen.lineTo((50, h))
        pen.lineTo((50, h - t))
        pen.closePath()
        # Right vertical from bottom to midline
        _draw_vertical_stroke(pen, w - 50 - t // 2, 0, h // 2 + t // 2, thickness=t)
        # Horizontal bar at midline from center to right edge
        _draw_horizontal_stroke(pen, w // 2, w - 50, h // 2, thickness=t)
    elif upper == 'H':
        # Left vertical stroke
        _draw_vertical_stroke(pen, 50 + t // 2, 0, h, thickness=t)
        # Right vertical stroke
        _draw_vertical_stroke(pen, w - 50 - t // 2, 0, h, thickness=t)
        # Crossbar at mid-height
        _draw_horizontal_stroke(pen, 50, w - 50, h // 2, thickness=t)
    elif upper == 'I':
        # Clean vertical stroke with horizontal bars (rounded corners)
        _draw_vertical_stroke(pen, w // 2, 0, h, thickness=t)
        _draw_horizontal_stroke(pen, 100, w - 100, t // 2, thickness=t)
        _draw_horizontal_stroke(pen, 100, w - 100, h - t // 2, thickness=t)
    elif upper == 'J':
        # Right vertical stroke
        _draw_vertical_stroke(pen, w - 50 - t // 2, 0, h, thickness=t)
        # Bottom horizontal
        _draw_horizontal_stroke(pen, 50, w - 50, t // 2, thickness=t)
        # Left short vertical
        _draw_vertical_stroke(pen, 50 + t // 2, 0, h // 4, thickness=t)
    elif upper == 'K':
        import math
        # Left vertical stroke
        _draw_vertical_stroke(pen, 50 + t // 2, 0, h, thickness=t)

        # Horizontal connector from vertical (about 25% of letter width)
        mid_y = h // 2
        connector_length = int((w - 100) * 0.25)
        connector_end_x = 50 + t + connector_length
        _draw_horizontal_stroke(pen, 50 + t, connector_end_x, mid_y, thickness=t)

        # Simple diagonal strokes - just angled rectangles
        half_t = t // 2

        # Upper diagonal: from connector end to top-right
        x0, y0 = connector_end_x, mid_y
        x1, y1 = w - 50, h
        dx = x1 - x0
        dy = y1 - y0
        length = math.sqrt(dx*dx + dy*dy)
        # Perpendicular offset
        px = -dy / length * half_t
        py = dx / length * half_t
        pen.moveTo((x0 - px, y0 - py))
        pen.lineTo((x1 - px, y1 - py))
        pen.lineTo((x1 + px, y1 + py))
        pen.lineTo((x0 + px, y0 + py))
        pen.closePath()

        # Lower diagonal: from connector end to bottom-right
        x1, y1 = w - 50, 0
        dx = x1 - x0
        dy = y1 - y0
        length = math.sqrt(dx*dx + dy*dy)
        px = -dy / length * half_t
        py = dx / length * half_t
        pen.moveTo((x0 - px, y0 - py))
        pen.lineTo((x1 - px, y1 - py))
        pen.lineTo((x1 + px, y1 + py))
        pen.lineTo((x0 + px, y0 + py))
        pen.closePath()
    elif upper == 'L':
        # Left vertical stroke
        _draw_vertical_stroke(pen, 50 + t // 2, 0, h, thickness=t)
        # Bottom horizontal with angled terminal
        cut_offset = int(t * 0.7)
        pen.moveTo((50, 0))
        pen.lineTo((w - 50 - cut_offset, 0))
        pen.lineTo((w - 50, cut_offset))
        pen.lineTo((w - 50, t))
        pen.lineTo((50 + t, t))
        pen.lineTo((50 + t, 0))
        pen.closePath()
    elif upper == 'M':
        # Left vertical stroke
        _draw_vertical_stroke(pen, 50 + t // 2, 0, h, thickness=t)
        # Right vertical stroke
        _draw_vertical_stroke(pen, w - 50 - t // 2, 0, h, thickness=t)
        # Center vertical stroke
        _draw_vertical_stroke(pen, w // 2, 0, h, thickness=t)
        # Top horizontal connecting bar
        _draw_horizontal_stroke(pen, 50, w - 50, h - t // 2, thickness=t)
    elif upper == 'N':
        # Left vertical stroke
        _draw_vertical_stroke(pen, 50 + t // 2, 0, h, thickness=t)
        # Right vertical stroke
        _draw_vertical_stroke(pen, w - 50 - t // 2, 0, h, thickness=t)
        # Top horizontal connecting bar
        _draw_horizontal_stroke(pen, 50, w - 50, h - t // 2, thickness=t)
    elif upper == 'O':
        # Outer rounded rectangle
        _draw_rounded_rect(pen, 50, 0, w - 50, h, radius=CORNER_RADIUS)
        # Inner cutout - CCW winding to create hole
        _draw_rect_ccw(pen, 50 + t, t, w - 50 - t, h - t)
    elif upper == 'P':
        # Left vertical stroke
        _draw_vertical_stroke(pen, 50 + t // 2, 0, h, thickness=t)
        # Top horizontal
        _draw_horizontal_stroke(pen, 50, w - 50, h - t // 2, thickness=t)
        # Middle horizontal
        _draw_horizontal_stroke(pen, 50, w - 50, h // 2, thickness=t)
        # Right vertical (rounded bowl)
        _draw_vertical_stroke(pen, w - 50 - t // 2, h // 2, h, thickness=t)
    elif upper == 'Q':
        # Outer rounded rectangle
        _draw_rounded_rect(pen, 50, 0, w - 50, h, radius=CORNER_RADIUS)
        # Inner cutout - CCW winding to create hole
        _draw_rect_ccw(pen, 50 + t, t, w - 50 - t, h - t)
        # Diagonal tail extending from bottom-right to below baseline
        tail_w = int(t * 0.7)
        pen.moveTo((w - 50 - t - 10, t + 10))
        pen.lineTo((w - 40, -50))
        pen.lineTo((w - 40 + tail_w, -50))
        pen.lineTo((w - 50 - t - 10 + tail_w, t + 10))
        pen.closePath()
    elif upper == 'R':
        import math
        # Outer rounded rectangle (upper half only)
        _draw_rounded_rect(pen, 50, h // 2 - t // 2, w - 50, h, radius=CORNER_RADIUS)
        # Upper inner cutout - CCW winding (with indent on left like B)
        indent = int(t * 0.4)
        _draw_rect_ccw(pen, 50 + t + indent, h // 2 + t // 2, w - 50 - t, h - t)
        # Left vertical stroke (full height)
        _draw_vertical_stroke(pen, 50 + t // 2, 0, h // 2 - t // 2, thickness=t)

        # Right leg diagonal - starting from near the vertical line (like K's kicker)
        half_t = t // 2
        mid_y = h // 2 - t // 2
        # Start from closer to vertical line (similar to K's connector end)
        connector_length = int((w - 100) * 0.2)
        x0, y0 = 50 + t + connector_length, mid_y
        x1, y1 = w - 50, 0
        dx = x1 - x0
        dy = y1 - y0
        length = math.sqrt(dx*dx + dy*dy)
        px = -dy / length * half_t
        py = dx / length * half_t
        pen.moveTo((x0 - px, y0 - py))
        pen.lineTo((x1 - px, y1 - py))
        pen.lineTo((x1 + px, y1 + py))
        pen.lineTo((x0 + px, y0 + py))
        pen.closePath()
    elif upper == 'S':
        # Refined S with smooth curves and angled terminals
        cut_offset = int(t * 0.7)

        # Bottom horizontal bar with angled left terminal
        pen.moveTo((50 + cut_offset, 0))
        pen.lineTo((w - 50, 0))
        pen.lineTo((w - 50, t))
        pen.lineTo((50, t))
        pen.lineTo((50 + cut_offset, 0))
        pen.closePath()

        # Right lower vertical
        _draw_vertical_stroke(pen, w - 50 - t // 2, 0, h // 2, thickness=t)

        # Middle horizontal bar
        _draw_horizontal_stroke(pen, 50, w - 50, h // 2, thickness=t)

        # Left upper vertical
        _draw_vertical_stroke(pen, 50 + t // 2, h // 2, h, thickness=t)

        # Top horizontal bar with angled right terminal
        pen.moveTo((50, h - t))
        pen.lineTo((w - 50 - cut_offset, h - t))
        pen.lineTo((w - 50, h - t + cut_offset))
        pen.lineTo((w - 50, h))
        pen.lineTo((50, h))
        pen.closePath()
    elif upper == 'T':
        # Center vertical stroke
        _draw_vertical_stroke(pen, w // 2, 0, h, thickness=t)
        # Top horizontal
        _draw_horizontal_stroke(pen, 50, w - 50, h - t // 2, thickness=t)
    elif upper == 'U':
        # Left vertical stroke
        _draw_vertical_stroke(pen, 50 + t // 2, 0, h, thickness=t)
        # Right vertical stroke
        _draw_vertical_stroke(pen, w - 50 - t // 2, 0, h, thickness=t)
        # Bottom horizontal
        _draw_horizontal_stroke(pen, 50, w - 50, t // 2, thickness=t)
    elif upper == 'V':
        import math
        # Two diagonal lines meeting at bottom center
        half_t = t // 2
        center_x = w // 2
        bottom_y = 0

        # Left diagonal: from top-left to bottom-center
        x0, y0 = 50, h
        x1, y1 = center_x, bottom_y
        dx = x1 - x0
        dy = y1 - y0
        length = math.sqrt(dx*dx + dy*dy)
        # Perpendicular offset
        px = -dy / length * half_t
        py = dx / length * half_t
        pen.moveTo((x0 - px, y0 - py))
        pen.lineTo((x1 - px, y1 - py))
        pen.lineTo((x1 + px, y1 + py))
        pen.lineTo((x0 + px, y0 + py))
        pen.closePath()

        # Right diagonal: from top-right to bottom-center
        x0, y0 = w - 50, h
        dx = x1 - x0
        dy = y1 - y0
        length = math.sqrt(dx*dx + dy*dy)
        px = -dy / length * half_t
        py = dx / length * half_t
        pen.moveTo((x0 - px, y0 - py))
        pen.lineTo((x1 - px, y1 - py))
        pen.lineTo((x1 + px, y1 + py))
        pen.lineTo((x0 + px, y0 + py))
        pen.closePath()
    elif upper == 'W':
        # Left vertical stroke
        _draw_vertical_stroke(pen, 50 + t // 2, 0, h, thickness=t)
        # Right vertical stroke
        _draw_vertical_stroke(pen, w - 50 - t // 2, 0, h, thickness=t)
        # Center vertical stroke
        _draw_vertical_stroke(pen, w // 2, 0, h, thickness=t)
        # Bottom horizontal connecting bar
        _draw_horizontal_stroke(pen, 50, w - 50, t // 2, thickness=t)
    elif upper == 'X':
        import math
        # Two crossed diagonal lines
        half_t = t // 2

        # Diagonal from top-left to bottom-right
        x0, y0 = 50, h
        x1, y1 = w - 50, 0
        dx = x1 - x0
        dy = y1 - y0
        length = math.sqrt(dx*dx + dy*dy)
        px = -dy / length * half_t
        py = dx / length * half_t
        pen.moveTo((x0 - px, y0 - py))
        pen.lineTo((x1 - px, y1 - py))
        pen.lineTo((x1 + px, y1 + py))
        pen.lineTo((x0 + px, y0 + py))
        pen.closePath()

        # Diagonal from top-right to bottom-left
        x0, y0 = w - 50, h
        x1, y1 = 50, 0
        dx = x1 - x0
        dy = y1 - y0
        length = math.sqrt(dx*dx + dy*dy)
        px = -dy / length * half_t
        py = dx / length * half_t
        pen.moveTo((x0 - px, y0 - py))
        pen.lineTo((x1 - px, y1 - py))
        pen.lineTo((x1 + px, y1 + py))
        pen.lineTo((x0 + px, y0 + py))
        pen.closePath()
    elif upper == 'Y':
        import math
        # Center vertical stem from bottom to mid-height
        mid_y = h // 2
        _draw_vertical_stroke(pen, w // 2, 0, mid_y, thickness=t)

        # Simple diagonal arms - just angled rectangles
        half_t = t // 2
        center_x = w // 2

        # Left diagonal arm: from center-mid to top-left
        x0, y0 = center_x, mid_y
        x1, y1 = 50, h
        dx = x1 - x0
        dy = y1 - y0
        length = math.sqrt(dx*dx + dy*dy)
        # Perpendicular offset
        px = -dy / length * half_t
        py = dx / length * half_t
        pen.moveTo((x0 - px, y0 - py))
        pen.lineTo((x1 - px, y1 - py))
        pen.lineTo((x1 + px, y1 + py))
        pen.lineTo((x0 + px, y0 + py))
        pen.closePath()

        # Right diagonal arm: from center-mid to top-right
        x1, y1 = w - 50, h
        dx = x1 - x0
        dy = y1 - y0
        length = math.sqrt(dx*dx + dy*dy)
        px = -dy / length * half_t
        py = dx / length * half_t
        pen.moveTo((x0 - px, y0 - py))
        pen.lineTo((x1 - px, y1 - py))
        pen.lineTo((x1 + px, y1 + py))
        pen.lineTo((x0 + px, y0 + py))
        pen.closePath()
    elif upper == 'Z':
        import math
        # Top horizontal bar
        _draw_horizontal_stroke(pen, 50, w - 50, h - t // 2, thickness=t)
        # Bottom horizontal bar
        _draw_horizontal_stroke(pen, 50, w - 50, t // 2, thickness=t)

        # Diagonal - balanced length
        half_t = t // 2
        # Start from near right edge, at bottom of top bar
        x0, y0 = w - 50 - half_t, h - t
        # End at near left edge, at top of bottom bar
        x1, y1 = 50 + half_t, t
        dx = x1 - x0
        dy = y1 - y0
        length = math.sqrt(dx*dx + dy*dy)
        px = -dy / length * half_t
        py = dx / length * half_t
        pen.moveTo((x0 - px, y0 - py))
        pen.lineTo((x1 - px, y1 - py))
        pen.lineTo((x1 + px, y1 + py))
        pen.lineTo((x0 + px, y0 + py))
        pen.closePath()
    # Punctuation
    elif char == '.':
        _draw_rect(pen, w // 2 - t // 2, 0, w // 2 + t // 2, t)
    elif char == ',':
        _draw_rect(pen, w // 2 - t // 2, -50, w // 2 + t // 2, t)
    elif char == ':':
        _draw_rect(pen, w // 2 - t // 2, 0, w // 2 + t // 2, t)
        _draw_rect(pen, w // 2 - t // 2, X_HEIGHT - t, w // 2 + t // 2, X_HEIGHT)
    elif char == ';':
        _draw_rect(pen, w // 2 - t // 2, -50, w // 2 + t // 2, t)
        _draw_rect(pen, w // 2 - t // 2, X_HEIGHT - t, w // 2 + t // 2, X_HEIGHT)
    elif char == '!':
        _draw_rect(pen, w // 2 - t // 2, 0, w // 2 + t // 2, t)
        _draw_rect(pen, w // 2 - t // 2, t * 2, w // 2 + t // 2, h)
    elif char == '?':
        _draw_rect(pen, w // 2 - t // 2, 0, w // 2 + t // 2, t)
        _draw_rect(pen, w // 2 - t // 2, t * 2, w // 2 + t // 2, h // 2)
        _draw_rect(pen, 50, h - t, w - 50, h)
        _draw_rect(pen, w - 50 - t, h // 2, w - 50, h)
        _draw_rect(pen, w // 2, h // 2 - t // 2, w - 50, h // 2 + t // 2)
    elif char == '-':
        _draw_rect(pen, 100, h // 2 - t // 2, w - 100, h // 2 + t // 2)
    elif char == '+':
        _draw_rect(pen, 100, h // 2 - t // 2, w - 100, h // 2 + t // 2)
        _draw_rect(pen, w // 2 - t // 2, h // 4, w // 2 + t // 2, h * 3 // 4)
    elif char == '=':
        _draw_rect(pen, 100, h // 2 - t * 2, w - 100, h // 2 - t)
        _draw_rect(pen, 100, h // 2 + t, w - 100, h // 2 + t * 2)
    elif char == '(':
        _draw_rect(pen, w // 2 - t // 2, 0, w // 2 + t // 2, h)
        _draw_rect(pen, w // 2 - t // 2, 0, w // 2 + t * 2, t)
        _draw_rect(pen, w // 2 - t // 2, h - t, w // 2 + t * 2, h)
    elif char == ')':
        _draw_rect(pen, w // 2 - t // 2, 0, w // 2 + t // 2, h)
        _draw_rect(pen, w // 2 - t * 2, 0, w // 2 + t // 2, t)
        _draw_rect(pen, w // 2 - t * 2, h - t, w // 2 + t // 2, h)
    elif char == '{':
        _draw_rect(pen, w // 2, 0, w // 2 + t, h)
        _draw_rect(pen, w // 2 - t, h // 2 - t // 2, w // 2 + t, h // 2 + t // 2)
        _draw_rect(pen, w // 2, 0, w // 2 + t * 2, t)
        _draw_rect(pen, w // 2, h - t, w // 2 + t * 2, h)
    elif char == '}':
        _draw_rect(pen, w // 2 - t, 0, w // 2, h)
        _draw_rect(pen, w // 2 - t, h // 2 - t // 2, w // 2 + t, h // 2 + t // 2)
        _draw_rect(pen, w // 2 - t * 2, 0, w // 2, t)
        _draw_rect(pen, w // 2 - t * 2, h - t, w // 2, h)
    elif char == '[':
        _draw_rect(pen, w // 2 - t // 2, 0, w // 2 + t // 2, h)
        _draw_rect(pen, w // 2 - t // 2, 0, w // 2 + t * 2, t)
        _draw_rect(pen, w // 2 - t // 2, h - t, w // 2 + t * 2, h)
    elif char == ']':
        _draw_rect(pen, w // 2 - t // 2, 0, w // 2 + t // 2, h)
        _draw_rect(pen, w // 2 - t * 2, 0, w // 2 + t // 2, t)
        _draw_rect(pen, w // 2 - t * 2, h - t, w // 2 + t // 2, h)
    elif char == '/':
        _draw_rect(pen, 50, 0, 50 + t, h // 3)
        _draw_rect(pen, w // 2 - t // 2, h // 3 - t, w // 2 + t // 2, h * 2 // 3 + t)
        _draw_rect(pen, w - 50 - t, h * 2 // 3, w - 50, h)
    elif char == '\\':
        _draw_rect(pen, w - 50 - t, 0, w - 50, h // 3)
        _draw_rect(pen, w // 2 - t // 2, h // 3 - t, w // 2 + t // 2, h * 2 // 3 + t)
        _draw_rect(pen, 50, h * 2 // 3, 50 + t, h)
    elif char == "'":
        _draw_rect(pen, w // 2 - t // 2, h - h // 4, w // 2 + t // 2, h)
    elif char == '"':
        _draw_rect(pen, w // 2 - t * 2, h - h // 4, w // 2 - t, h)
        _draw_rect(pen, w // 2 + t, h - h // 4, w // 2 + t * 2, h)
    elif char == '_':
        _draw_rect(pen, 50, 0, w - 50, t)
    elif char == '~':
        _draw_rect(pen, 100, h // 2, w - 100, h // 2 + t)
    elif char == '`':
        _draw_rect(pen, w // 2 - t, h - h // 4, w // 2 + t // 2, h)
    elif char == '@':
        _draw_rect(pen, 50, 0, w - 50, h)
        _draw_rect(pen, 50 + t, t, w - 50 - t, h - t)
        _draw_rect(pen, w // 2, t, w - 50 - t, h // 2)
        _draw_rect(pen, w // 2, t, w // 2 + t, h // 2)
        _draw_rect(pen, w // 2, t, w - 50 - t, t + t)
        _draw_rect(pen, w - 50 - t * 2, t, w - 50 - t, h // 2)
    elif char == '#':
        _draw_rect(pen, w // 3 - t // 2, 50, w // 3 + t // 2, h - 50)
        _draw_rect(pen, w * 2 // 3 - t // 2, 50, w * 2 // 3 + t // 2, h - 50)
        _draw_rect(pen, 80, h // 3 - t // 2, w - 80, h // 3 + t // 2)
        _draw_rect(pen, 80, h * 2 // 3 - t // 2, w - 80, h * 2 // 3 + t // 2)
    elif char == '$':
        _draw_rect(pen, w // 2 - t // 2, 0, w // 2 + t // 2, h)
        _draw_rect(pen, 100, 0, w - 100, t)
        _draw_rect(pen, 100, h - t, w - 100, h)
        _draw_rect(pen, 100, h // 2 - t // 2, w - 100, h // 2 + t // 2)
        _draw_rect(pen, w - 100 - t, 0, w - 100, h // 2)
        _draw_rect(pen, 100, h // 2, 100 + t, h)
    elif char == '%':
        import math
        # Diagonal line from bottom-left to top-right
        half_t = t // 2
        x0, y0 = 50, 0
        x1, y1 = w - 50, h
        dx = x1 - x0
        dy = y1 - y0
        length = math.sqrt(dx*dx + dy*dy)
        px = -dy / length * half_t
        py = dx / length * half_t
        pen.moveTo((x0 - px, y0 - py))
        pen.lineTo((x1 - px, y1 - py))
        pen.lineTo((x1 + px, y1 + py))
        pen.lineTo((x0 + px, y0 + py))
        pen.closePath()

        # Top-left dot (circle)
        dot_radius = int(t * 0.8)
        _draw_circle(pen, 80 + dot_radius, h - 100, dot_radius)

        # Bottom-right dot (circle)
        _draw_circle(pen, w - 80 - dot_radius, 100, dot_radius)
    elif char == '^':
        _draw_rect(pen, w // 2 - t // 2, h - 200, w // 2 + t // 2, h)
        _draw_rect(pen, w // 2 - 100, h - 200, w // 2 + 100, h - 200 + t)
    elif char == '&':
        _draw_rect(pen, 50, 0, 50 + t, h)
        _draw_rect(pen, 50, 0, w - 50, t)
        _draw_rect(pen, 50, h - t, w - 100, h)
        _draw_rect(pen, 50, h // 2 - t // 2, w - 50, h // 2 + t // 2)
        _draw_rect(pen, w - 50 - t, 0, w - 50, h // 2)
    elif char == '*':
        _draw_rect(pen, w // 2 - t // 2, h - 250, w // 2 + t // 2, h)
        _draw_rect(pen, 100, h - 160, w - 100, h - 160 + t)
    elif char == '<':
        _draw_rect(pen, w // 2 - t, h // 2 - t // 2, w - 100, h // 2 + t // 2)
        _draw_rect(pen, w // 2 - t, h - 200, w - 100, h - 200 + t)
        _draw_rect(pen, w // 2 - t, 100, w // 2 + t, h - 100)
    elif char == '>':
        _draw_rect(pen, 100, h // 2 - t // 2, w // 2 + t, h // 2 + t // 2)
        _draw_rect(pen, 100, h - 200, w // 2 + t, h - 200 + t)
        _draw_rect(pen, w // 2 - t, 100, w // 2 + t, h - 100)
    elif char == '|':
        _draw_rect(pen, w // 2 - t // 2, 0, w // 2 + t // 2, h)
    else:
        # Fallback: small square
        _draw_rect(pen, 100, 100, w - 100, h - 100)


def get_ascii_glyph_names():
    """Return list of (glyph_name, unicode_value, width) for all base glyphs."""
    glyphs = []
    # Space
    glyphs.append(("space", 0x0020, SPACE_WIDTH))
    # Printable ASCII 0x21 to 0x7E
    for code in range(0x21, 0x7F):
        char = chr(code)
        name = f"uni{code:04X}"
        if char.isdigit():
            glyphs.append((name, code, DIGIT_WIDTH))
        else:
            glyphs.append((name, code, ASCII_WIDTH))
    return glyphs


def draw_base_glyphs(glyph_drawing_funcs):
    """Register drawing functions for all base glyphs.

    Args:
        glyph_drawing_funcs: dict to populate with {glyph_name: (width, draw_func)}
    """
    # .notdef
    glyph_drawing_funcs[".notdef"] = (ASCII_WIDTH, _make_notdef)

    # Space (no drawing)
    glyph_drawing_funcs["space"] = (SPACE_WIDTH, None)

    # All printable ASCII
    for code in range(0x21, 0x7F):
        char = chr(code)
        name = f"uni{code:04X}"
        width = DIGIT_WIDTH if char.isdigit() else ASCII_WIDTH
        # Create closure to capture char
        def make_draw(c):
            return lambda pen: _make_block_letter(pen, c)
        glyph_drawing_funcs[name] = (width, make_draw(char))
