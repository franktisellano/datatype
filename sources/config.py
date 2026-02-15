"""Datatype configuration constants."""

from dataclasses import dataclass

# Font version - follows semantic versioning
FONT_VERSION = "1.100"
FONT_VERSION_MAJOR = 1
FONT_VERSION_MINOR = 1
FONT_VERSION_PATCH = 0

# Font metrics
UPM = 1000          # Units per em
ASCENDER = 800
DESCENDER = -200
CAP_HEIGHT = 700
X_HEIGHT = 500

# Chart dimensions (within UPM)
CHART_WIDTH = 800       # Total width of a chart glyph
CHART_HEIGHT = 840      # Max height for chart drawing area
CHART_BASELINE = -40    # Slightly below baseline for visual centering

# Bar chart
BAR_GAP = 20            # Gap between bars
MAX_BAR_DATA_POINTS = 20

# Sparkline
SPARK_DOT_RADIUS = 40
SPARK_LINE_THICKNESS = 65  # Full thickness of connecting lines
MAX_SPARK_DATA_POINTS = 20

# Pie chart (single percentage)
PIE_RADIUS = 390
PIE_CENTER_X = 420
PIE_CENTER_Y = 350
PIE_STROKE = 60         # Thickness of the unfilled ring portion

# ASCII glyph dimensions
ASCII_WIDTH = 500
SPACE_WIDTH = 250
DIGIT_WIDTH = 500

# Font family info
FAMILY_NAME = "Datatype"
REGULAR_STYLE = "Regular"

# Max data values
MAX_VALUE = 100
MIN_VALUE = 0


@dataclass
class FontParams:
    """Parameterized dimensions for variable font axes and scale variants."""
    max_value: int = 100
    bar_width: int = 180
    sep_width: int = 60
    end_width: int = 40
    seg_width: int = 200
    point_width: int = 16
    line_thickness: int = 65
    bar_fill: float = 0.75      # fraction of bar_width the drawn bar occupies
    pie_stroke: int = 60        # ring thickness for unfilled pie portion


# Scale definitions: (suffix, max_value)
SCALES = [
    ("", 100),         # default: Datatype.ttf
]

# Variable font axis masters: (wdth, wght) → FontParams overrides
# wdth range: 50-150 (OpenType spec compliant: >0, default=100)
# wght range: 100-900 (standard weight axis)
AXIS_MASTERS = [
    # (wdth, wght, bar_width, seg_width, point_width, sep_width, end_width, line_thickness, bar_fill, pie_stroke)
    (100, 400, 405, 450, 36,  0,  90,  65,  0.85,   60),   # Default (Regular) - no separators, bars at 85%
    (50,  400, 90,  100, 8,   0,  20,  65,  0.85,   60),   # wdth min
    (150, 400, 720, 800, 64,  0,  160, 65,  0.85,   60),   # wdth max
    (100, 100, 405, 450, 36,  0,  90,  34,  0.15,   30),   # wght min (Thin) - bars at 15%
    (50,  100, 90,  100, 8,   0,  20,  34,  0.15,   30),   # wdth min + wght min
    (150, 100, 720, 800, 64,  0,  160, 34,  0.15,   30),   # wdth max + wght min
    (100, 900, 405, 450, 36,  0,  90,  130, 1.0,    120),  # wght max (Black) - bars at 100%, touching
    (50,  900, 90,  100, 8,   0,  20,  130, 1.0,    120),  # wdth min + wght max
    (150, 900, 720, 800, 64,  0,  160, 130, 1.0,    120),  # wdth max + wght max
]

# Named instances: (style_name, wdth, wght)
# Google Fonts standard weight instances (at normal width=100) are required
# Custom width combinations showcase the variable axes
NAMED_INSTANCES = [
    # Standard weight instances (required by Google Fonts at wdth=100)
    ("Thin",            100, 100),  # Standard thin
    ("ExtraLight",      100, 200),  # Standard extra light
    ("Light",           100, 300),  # Standard light
    ("Regular",         100, 400),  # Default, balanced
    ("Medium",          100, 500),  # Standard medium
    ("SemiBold",        100, 600),  # Standard semi-bold
    ("Bold",            100, 700),  # Strong emphasis
    ("ExtraBold",       100, 800),  # Standard extra bold
    ("Black",           100, 900),  # Standard black

    # Custom width combinations (showcase variable width axis)
    ("ThinNarrow",      50,  100),  # Ultra-minimal sparklines
    ("LightCompact",    75,  300),  # Subtle, space-efficient charts
    ("SemiBoldCompact", 75,  600),  # Dense dashboards
    ("LightWide",       150, 300),  # Maximum breathing room
    ("MediumWide",      125, 500),  # Prominent, readable charts
    ("BlackWide",       150, 900),  # Maximum impact
]
