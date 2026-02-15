"""Base ASCII glyphs imported from IBM Plex Mono.

Glyphs sourced from IBM Plex Mono (Copyright IBM, SIL OFL 1.1)
https://github.com/IBM/plex
"""

import pickle
import os

from sources.config import UPM, ASCENDER, ASCII_WIDTH, SPACE_WIDTH, DIGIT_WIDTH, CAP_HEIGHT, X_HEIGHT

# Load imported glyph data
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_GLYPH_DATA_PATH = os.path.join(os.path.dirname(_SCRIPT_DIR), 'imported_glyphs.pkl')

with open(_GLYPH_DATA_PATH, 'rb') as f:
    _IMPORTED_GLYPHS = pickle.load(f)

# IBM Plex Mono is 600 units wide (monospace), we use 500
# Scale factor to fit our metrics
SCALE_FACTOR = ASCII_WIDTH / 600  # 500 / 600 = 0.833


def _scale_point(point):
    """Scale a point from IBM Plex coordinates to our UPM."""
    return (int(point[0] * SCALE_FACTOR), point[1])


def _draw_imported_glyph(pen, char):
    """Draw an imported glyph from IBM Plex Mono."""
    if char not in _IMPORTED_GLYPHS:
        # Fallback to simple rectangle if glyph not found
        _draw_rect(pen, 50, 0, ASCII_WIDTH - 50, CAP_HEIGHT)
        return

    data = _IMPORTED_GLYPHS[char]
    commands = data['commands']

    for cmd, args in commands:
        if cmd == 'moveTo':
            pen.moveTo(_scale_point(args[0]))
        elif cmd == 'lineTo':
            pen.lineTo(_scale_point(args[0]))
        elif cmd == 'qCurveTo':
            # Quadratic curve - scale all points
            scaled_points = [_scale_point(p) for p in args]
            pen.qCurveTo(*scaled_points)
        elif cmd == 'curveTo':
            # Cubic curve - scale all points
            scaled_points = [_scale_point(p) for p in args]
            pen.curveTo(*scaled_points)
        elif cmd == 'closePath':
            pen.closePath()
        elif cmd == 'endPath':
            pen.endPath()


def _draw_rect(pen, x0, y0, x1, y1):
    """Draw a simple rectangle (fallback)."""
    pen.moveTo((x0, y0))
    pen.lineTo((x1, y0))
    pen.lineTo((x1, y1))
    pen.lineTo((x0, y1))
    pen.closePath()


def _make_notdef(pen):
    """Draw .notdef (empty rectangle)."""
    _draw_rect(pen, 50, 0, 450, CAP_HEIGHT)
    _draw_rect(pen, 100, 50, 400, CAP_HEIGHT - 50)


def _make_block_letter(pen, char):
    """Draw a letter using imported IBM Plex Mono glyph."""
    _draw_imported_glyph(pen, char)


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

    # Non-breaking space (U+00A0) - same as regular space
    glyph_drawing_funcs["uni00A0"] = (SPACE_WIDTH, None)

    # All printable ASCII - use imported glyphs
    for code in range(0x21, 0x7F):
        char = chr(code)
        name = f"uni{code:04X}"
        width = DIGIT_WIDTH if char.isdigit() else ASCII_WIDTH
        # Create closure to capture char
        def make_draw(c):
            return lambda pen: _make_block_letter(pen, c)
        glyph_drawing_funcs[name] = (width, make_draw(char))
