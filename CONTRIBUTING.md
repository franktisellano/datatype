# Contributing to Datatype

Thank you for your interest in contributing to Datatype! This document provides guidelines for contributing to the project.

---

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Code Style](#code-style)
- [Testing](#testing)
- [Submitting Changes](#submitting-changes)
- [Reporting Issues](#reporting-issues)

---

## Code of Conduct

Be respectful, inclusive, and constructive in all interactions.

---

## Getting Started

### Prerequisites

- Python 3.9 or later
- pip
- Git

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/franktisellano/datatype.git
cd datatype

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Build fonts
python sources/build.py --dev

# Start development server
python dev/server.py
# Open http://localhost:8080 in your browser
```

---

## Development Workflow

### Understanding the Architecture

Datatype generates OpenType variable fonts using fontTools. The key components:

1. **`sources/config.py`** — Font parameters, scales, axis masters
2. **`sources/glyphs/`** — Glyph drawing modules (bar, sparkline, pie, base)
3. **`sources/font_builder.py`** — Font assembly and variable font generation
4. **`sources/build.py`** — Main build orchestration

**Variable font structure:**
- **9 masters per scale** — Full coverage of width/weight design space
- **2 axes** — wdth (50-150), wght (100-900)
- **GSUB features** — Contextual alternates (`calt`) for chart substitution

### Making Changes

**For glyph design changes:**
1. Edit `sources/glyphs/bar.py`, `sparkline.py`, or `pie.py`
2. Rebuild: `python sources/build.py --dev`
3. Preview in browser: http://localhost:8080

**For font parameters:**
1. Edit `sources/config.py` (AXIS_MASTERS, FontParams)
2. Rebuild: `python sources/build.py`
3. Verify all masters build correctly

**For feature code:**
1. Edit glyph generation functions (e.g., `generate_bar_feature_code()`)
2. Rebuild and test ligature substitution

---

## Code Style

### Python

Follow [PEP 8](https://pep8.org/) guidelines:

```python
# Good
def draw_bar_glyphs(glyph_data, params):
    """Generate bar chart glyphs for all possible height values."""
    for height in range(params.max_value + 1):
        glyph_name = f"bar_h{height}"
        # ...

# Not ideal
def drawBarGlyphs(glyphData,params):
  for h in range(params.max_value+1):  # Missing spaces
    # ...
```

**Conventions:**
- Use 4 spaces for indentation (not tabs)
- Maximum line length: 100 characters
- Use descriptive variable names
- Add docstrings to all functions
- Type hints are encouraged but not required

### JavaScript (for plugins)

```javascript
// Use modern ES6+ syntax
export default function datatypePlugin() {
  return (tree) => {
    visit(tree, 'text', (node) => {
      // ...
    });
  };
}
```

---

## Testing

### Manual Testing Checklist

Before submitting changes, verify:

**Build tests:**
- [ ] `python sources/build.py --dev` completes without errors
- [ ] `python sources/build.py` (full build) completes successfully
- [ ] Output files created in `fonts/` directory

**Visual tests:**
- [ ] Bar charts render correctly (test: `{b:10,50,90}`)
- [ ] Sparklines connect smoothly (test: `{l:20,80,30,70}`)
- [ ] Pie charts fill correctly (test: `{p:25}`, `{p:75}`)
- [ ] Variable axes interpolate smoothly (test width/weight sliders)

**Browser tests:**
- [ ] Chrome: Charts render correctly
- [ ] Firefox: Charts render correctly
- [ ] Safari: Charts render correctly (especially at weight 600+)

**Cross-platform tests** (if modifying build process):
- [ ] macOS build works
- [ ] Windows build works (if applicable)
- [ ] Linux build works (if applicable)

### Automated Testing

Install the development and browser-test dependencies:

```bash
pip install -r requirements-dev.txt
npm install
npx playwright install
```

Run the Python unit tests:

```bash
make test-unit
```

The unit suite checks glyph generation, OpenType feature code, the variable
designspace, font metadata, and the structure of the checked-in variable font.

Run the browser tests in Chromium, Firefox, and WebKit:

```bash
make test-browser
```

The Playwright suite loads the generated WOFF2 file in a real browser and checks
bar, sparkline, and pie substitutions along with variable width and weight
behavior.

Run both suites:

```bash
make test
```

GitHub Actions runs the unit suite, builds fresh fonts, and then runs the browser
suite against those build artifacts for every pull request.

---

## Submitting Changes

### Pull Request Process

1. **Fork the repository** and create a feature branch:
   ```bash
   git checkout -b feature/improve-sparklines
   ```

2. **Make your changes** following the code style guidelines

3. **Test thoroughly** using the manual testing checklist

4. **Commit with clear messages**:
   ```bash
   git commit -m "Improve sparkline segment connections at narrow widths"
   ```

5. **Push to your fork**:
   ```bash
   git push origin feature/improve-sparklines
   ```

6. **Submit a pull request** with:
   - Clear description of what changed
   - Why the change was needed
   - Screenshots/examples (if visual changes)
   - Testing performed

### Commit Message Guidelines

Use imperative mood in the subject line:

```
✅ Good:
- Add support for negative values in bar charts
- Fix sparkline rendering at weight 100
- Update documentation for variable font axes

❌ Not ideal:
- Added support...
- Fixed sparkline...
- Updating documentation...
```

Format:
```
Short summary (50 chars or less)

Longer explanation if needed. Wrap at 72 characters.
Include context, motivation, and impact.

- Use bullet points for multiple changes
- Reference issues: Fixes #123
```

---

## Reporting Issues

### Bug Reports

When reporting bugs, include:

1. **Font version** (check `fonts/Datatype.ttf` metadata or git commit)
2. **Environment**:
   - Browser/application name and version
   - Operating system
   - Font format used (TTF, WOFF2, static instance)
3. **Reproduction steps**:
   - Exact syntax used (e.g., `{b:30,70,50}`)
   - CSS settings (variable axes, font-weight, etc.)
   - Screenshot or screen recording
4. **Expected vs actual behavior**

**Example:**
```
**Bug**: Sparklines disconnect at weight 600 in Safari

**Environment**:
- Safari 17.2 on macOS Sonoma
- Datatype.woff2 v1.0.0
- CSS: font-variation-settings: 'wdth' 50, 'wght' 600

**Steps to reproduce**:
1. Load {l:20,50,80,30} with weight 600
2. Observe gaps between segments

**Expected**: Smooth connected line
**Actual**: Disconnected segments with gaps

[Screenshot attached]
```

### Feature Requests

When requesting features:

1. **Describe the use case** — what problem does this solve?
2. **Proposed solution** — how should it work?
3. **Alternatives considered** — other ways to achieve this?
4. **Examples** — mockups, syntax ideas, similar implementations

---

## Areas for Contribution

We welcome contributions in these areas:

### High Priority
- **Automated tests** — Unit tests, integration tests, visual regression tests
- **CI/CD pipeline** — GitHub Actions for automated builds and validation
- **Documentation** — Improve examples, add troubleshooting guides
- **Accessibility** — Improve semantic HTML, ARIA labels in specimen site

### Feature Ideas
- **Negative values** — Support for negative data points in charts
- **Color variants** — Multi-color chart support (COLR table)
- **New chart types** — Horizontal bars, area charts, scatter plots
- **Custom scales** — User-defined value ranges beyond 0-100
- **Animation** — CSS transitions for chart value changes

### Plugin Contributions
- **Framework integrations** — Svelte, Vue, Angular plugins
- **Build tools** — Vite, esbuild, Parcel plugins
- **Static site generators** — Gatsby, Hugo, Jekyll plugins

---

## Development Tips

### Debugging Glyphs

View generated glyphs using fontTools:

```bash
# Dump glyph data
ttx -t glyf -o - fonts/Datatype.ttf | grep "bar_h50" -A 20

# View specific table
ttx -t fvar fonts/Datatype.ttf
```

### Performance Optimization

The font generates 10,626 glyphs. To reduce build time during development:

1. Use `--dev` flag for faster builds
2. Reduce `max_value` in config.py temporarily
3. Comment out sparkline generation if only working on bar charts

### Font Validation

Validate fonts with fontbakery:

```bash
pip install fontbakery
fontbakery check-opentype fonts/Datatype.ttf
```

---

## Questions?

- **General questions**: Open a [GitHub Discussion](https://github.com/franktisellano/datatype/discussions)
- **Bug reports**: Open an [Issue](https://github.com/franktisellano/datatype/issues)
- **Security issues**: Email frank@example.com (replace with actual email)

---

## License

By contributing to Datatype, you agree that your contributions will be licensed under the SIL Open Font License 1.1 (for font files) and MIT License (for plugin code).

---

Thank you for contributing to Datatype! 🎉
