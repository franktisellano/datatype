# Datatype

**A variable OpenType font that turns text into inline charts.**

Datatype uses OpenType ligature substitution to transform simple text expressions like `{b:30,70,50,90}` into visual charts—no JavaScript required.

[**View Specimen Site →**](https://franktisellano.github.io/datatype/)

---

## Features

- **Bar charts**: `{b:1,3,7,9,4,2}` — up to 20 values
- **Sparklines**: `{l:2,5,3,8,1,6,4}` — up to 20 points
- **Pie charts**: `{p:75}` — single percentage

**Variable font axes:**
- **Width (wdth)**: 50–150 — controls spacing (default: 100)
- **Weight (wght)**: 100–900 — controls line thickness (default: 400)

---

## Google Fonts

Datatype is available on Google Fonts for easy integration into web projects.

### Using with Google Fonts API

```html
<link href="https://fonts.googleapis.com/css2?family=Datatype:wdth,wght@50,100;100,400;150,900&display=swap" rel="stylesheet">

<style>
  .chart {
    font-family: 'Datatype', sans-serif;
    font-variation-settings: 'wdth' 100, 'wght' 400;
  }
</style>
```

### Google Workspace Compatibility

**Important:** Google Docs, Sheets, and Slides have limited variable font support:

- ✅ **Bar charts and sparklines work** (via `calt` feature)
- ⚠️ **Pie charts may not work** (require `liga` feature, not enabled by default)
- ✅ **Weight axis** (100-900) accessible via font weight selector
- ❌ **Width axis** not accessible in UI (defaults to 100)

For full control over both wdth and wght axes, use the variable font in modern web browsers or install the desktop font files.

---

## Quick Start

### Web (Recommended)

```html
<!DOCTYPE html>
<html>
<head>
  <style>
    @font-face {
      font-family: 'Datatype';
      src: url('Datatype.woff2') format('woff2');
      font-weight: 100 900;
      font-stretch: 0% 100%;
    }

    .chart {
      font-family: 'Datatype', sans-serif;
      font-variation-settings: 'wdth' 100, 'wght' 400;
    }
  </style>
</head>
<body>
  <p class="chart">
    Sales this quarter {l:20,45,60,55,80,95} are up significantly.
  </p>
</body>
</html>
```

### Desktop Applications

1. Download font files from [Releases](https://github.com/franktisellano/datatype/releases)
2. Install TTF files:
   - **macOS**: Copy to `~/Library/Fonts/`
   - **Windows**: Copy to `C:\Windows\Fonts\`
   - **Linux**: Copy to `~/.local/share/fonts/`
3. Use in any application that supports OpenType ligatures

**Note:** Enable ligatures/contextual alternates in your application:
- Adobe apps: Character panel → OpenType → Ligatures

---

## Syntax Reference

### Bar Charts

```
{b:value,value,value,...}
```

- **Values**: 0–100
- **Count**: Up to 20 bars
- **Example**: `{b:15,45,80,30,60,90,20}`

### Sparklines

```
{l:value,value,value,...}
```

- **Values**: 0–100
- **Count**: Up to 20 points
- **Example**: `{l:10,40,25,70,50,90,35,60}`

### Pie Charts

```
{p:value}
```

- **Value**: 0–100 (percentage)
- **Single value** showing percentage filled
- **Example**: `{p:62}`

---

## Building from Source

### Prerequisites

- Python 3.9 or later
- pip

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Build Fonts

```bash
# Build all variants (2 variable fonts + 16 static instances)
python sources/build.py

# Development mode (faster, builds only default variant)
python sources/build.py --dev
```

### Development Server

```bash
# Start dev server with live preview
make dev

# Or manually:
python dev/server.py
# Open http://localhost:8080
```

**Output:**
- `fonts/variable/Datatype[wdth,wght].ttf` — Variable font (TTF, 4.0MB)
- `fonts/variable/Datatype[wdth,wght].woff2` — Variable font (WOFF2, 73KB)
- `fonts/ttf/` — 15 static TTF instances
- `fonts/webfonts/` — 15 static WOFF2 instances

---

## Font Specifications

### Variable Axes

| Axis | Tag | Min | Default | Max |
|------|-----|-----|---------|-----|
| Width | wdth | 50 | 100 | 150 |
| Weight | wght | 100 | 400 | 900 |

### Named Instances

15 static font combinations (9 standard + 6 custom width variants):

**Standard Weight Instances (wdth=100):**
| Instance | Width | Weight |
|----------|-------|--------|
| Thin | 100 | 100 |
| ExtraLight | 100 | 200 |
| Light | 100 | 300 |
| Regular | 100 | 400 |
| Medium | 100 | 500 |
| SemiBold | 100 | 600 |
| Bold | 100 | 700 |
| ExtraBold | 100 | 800 |
| Black | 100 | 900 |

**Custom Width Combinations:**
| Instance | Width | Weight | Use Case |
|----------|-------|--------|----------|
| ThinNarrow | 50 | 100 | Minimal sparklines |
| LightCompact | 75 | 300 | Space-efficient |
| SemiBoldCompact | 75 | 600 | Dense dashboards |
| MediumWide | 125 | 500 | Readable charts |
| LightWide | 150 | 300 | Maximum spacing |
| BlackWide | 150 | 900 | Maximum impact |

### Technical Details

- **Format**: OpenType variable font (TTF/WOFF2)
- **Features**: Contextual Alternates (`calt`), Standard Ligatures (`liga`)
- **Glyph count**: 10,627 (per master, 9 masters total)
- **File size**: 4.0 MB (TTF) / 73 KB (WOFF2)
- **Unicode coverage**: Basic Latin (ASCII)

---

## Browser Support

**Variable fonts:**
- Chrome 62+
- Firefox 62+
- Safari 11+
- Edge 17+

**Ligature substitution:**
- All modern browsers with OpenType feature support

---

## Project Structure

```
datatype/
├── sources/                # Python build scripts
│   ├── build.py           # Main build script
│   ├── config.py          # Font parameters & scales
│   ├── font_builder.py    # FontTools assembly
│   └── glyphs/            # Glyph drawing modules
├── documentation/          # Font description for Google Fonts
├── docs/                   # Specimen website (GitHub Pages)
├── dev/                    # Development server
├── fonts/                  # Generated fonts
│   ├── variable/          # Variable font files
│   ├── ttf/               # Static TTF instances
│   └── webfonts/          # Static WOFF2 instances
└── OFL.txt                 # SIL Open Font License 1.1
```

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines.

**Quick contribution workflow:**
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/my-feature`)
3. Make your changes
4. Test thoroughly (`python sources/build.py`)
5. Submit a pull request

---

## License

This Font Software is licensed under the **SIL Open Font License, Version 1.1**.

See [OFL.txt](OFL.txt) for full license text.

---

## Credits

**Design & Development**: [Frank Tisellano](https://github.com/franktisellano)

**Built with**: [fontTools](https://github.com/fonttools/fonttools)

---

## Links

- [**Specimen Site**](https://franktisellano.github.io/datatype/) — Interactive examples and documentation
- [**Integration Guide**](https://franktisellano.github.io/datatype/integrations.html) — Framework setup and usage tips
- [**Releases**](https://github.com/franktisellano/datatype/releases) — Download font files
- [**Issues**](https://github.com/franktisellano/datatype/issues) — Report bugs or request features

---

Made with ❤️ by Frank Tisellano
