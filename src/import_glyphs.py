"""Import glyphs from IBM Plex Mono for ASCII characters."""

from fontTools.ttLib import TTFont
from fontTools.pens.recordingPen import RecordingPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.cu2quPen import Cu2QuPen

# QWERTY characters to import
QWERTY_CHARS = [
    # Numbers
    '0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
    # Uppercase letters
    'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
    'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
    # Lowercase letters
    'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
    'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
    # Symbols
    '!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '-', '_', '=', '+',
    '[', ']', '{', '}', '\\', '|', ';', ':', "'", '"', ',', '.', '/', '?',
    '<', '>', '`', '~', ' '
]


def extract_glyphs():
    """Extract glyph data from IBM Plex Mono."""
    source_font = TTFont('src/IBMPlexMono-Regular.otf')

    # Get the glyph set and character map
    glyph_set = source_font.getGlyphSet()
    cmap = source_font.getBestCmap()

    extracted = {}

    for char in QWERTY_CHARS:
        code = ord(char)
        if code not in cmap:
            print(f"Warning: {char} (U+{code:04X}) not in source font")
            continue

        glyph_name = cmap[code]
        glyph = glyph_set[glyph_name]

        # Record the drawing commands, converting cubics to quadratics
        recording_pen = RecordingPen()
        cu2qu_pen = Cu2QuPen(recording_pen, 1.0)  # Convert cubics to quadratics
        glyph.draw(cu2qu_pen)
        pen = recording_pen

        # Get advance width
        width = glyph.width

        # Store the commands and width
        extracted[char] = {
            'width': width,
            'commands': pen.value,
            'glyph_name': glyph_name
        }

    print(f"Extracted {len(extracted)} glyphs from IBM Plex Mono")
    return extracted


def generate_draw_function(char, data):
    """Generate Python code for a draw function."""
    commands = data['commands']
    width = data['width']

    # Convert recording pen commands to Python code
    lines = []
    for cmd, args in commands:
        if cmd == 'moveTo':
            lines.append(f"    pen.moveTo({args[0]})")
        elif cmd == 'lineTo':
            lines.append(f"    pen.lineTo({args[0]})")
        elif cmd == 'qCurveTo':
            # Quadratic curve - args is a list of points
            points_str = ', '.join(str(p) for p in args)
            lines.append(f"    pen.qCurveTo({points_str})")
        elif cmd == 'curveTo':
            # Cubic curve (convert to quadratic if needed)
            points_str = ', '.join(str(p) for p in args)
            lines.append(f"    pen.curveTo({points_str})")
        elif cmd == 'closePath':
            lines.append(f"    pen.closePath()")
        elif cmd == 'endPath':
            lines.append(f"    pen.endPath()")

    code = '\n'.join(lines)
    return width, code


if __name__ == '__main__':
    glyphs = extract_glyphs()

    # Print sample for testing
    print("\nSample glyph 'A':")
    if 'A' in glyphs:
        width, code = generate_draw_function('A', glyphs['A'])
        print(f"Width: {width}")
        print(f"Drawing code:\n{code}")

    # Save extracted data
    import pickle
    with open('src/imported_glyphs.pkl', 'wb') as f:
        pickle.dump(glyphs, f)
    print(f"\nSaved glyph data to src/imported_glyphs.pkl")
