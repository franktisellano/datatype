# Changelog

All notable changes to the Datatype Project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2026-02-15

### Changed
- **OpenType spec compliance**: Width axis range changed from 0-100 to 50-150 (default: 100)
- Added 9 standard weight instances at normal width for Google Fonts compatibility
- Updated PANOSE values to sans-serif proportional (not monospace)
- Improved OS/2 metrics for better cross-platform rendering
- Enhanced STAT table with width axis values

### Added
- Non-breaking space glyph (U+00A0)
- gasp table for proper antialiasing
- Complete Google Fonts submission metadata
- GitHub Actions CI/CD for automated builds and validation

### Fixed
- Copyright format in OFL.txt and font metadata
- Font naming to meet Google Fonts requirements
- Timestamp handling for proper font compilation

## [1.0.0] - 2026-02-15

### Added
- Initial release of Datatype variable font
- Variable axes: Width (wdth: 50-150) and Weight (wght: 100-900)
- Three chart types via OpenType features:
  - Bar charts: `{b:values}` syntax (up to 20 values, 0-100)
  - Sparklines: `{l:values}` syntax (up to 20 points, 0-100)
  - Pie charts: `{p:percentage}` syntax (single percentage value)
- 15 named instances:
  - 9 standard weight instances at normal width (100)
  - 6 custom width combinations showcasing the wdth axis
- Character set: Basic Latin (ASCII) - 94 printable characters
- OpenType features:
  - `calt` (Contextual Alternates) for bar charts and sparklines
  - `liga` (Standard Ligatures) for pie charts
- Google Fonts compatible metadata and structure
- SIL Open Font License 1.1

### Technical Details
- Built with fontTools and Python
- 10,627 glyphs per master across 9 interpolation masters
- Includes glyphs from IBM Plex™ Mono (SIL OFL 1.1)
- Variable font file: `Datatype[wdth,wght].ttf`
- WOFF2 web font format included
- Static instances exported for broader compatibility

### Design Philosophy
- Inline data visualization without JavaScript
- Text-first approach for emails, documentation, and reports
- Monospaced ASCII characters for predictable text layout
- Wider chart glyphs (800 units) for visual prominence
- Variable width axis enables space-efficient to spacious layouts
- Variable weight axis provides subtle to bold visual emphasis

### Known Limitations
- ASCII-only character set (extended Latin planned for future releases)
- Pie charts require `liga` feature (may not work in all applications)
- Width axis not accessible in Google Docs/Sheets/Slides
- Chart syntax is case-sensitive and requires exact format

### Browser/Application Compatibility
- ✅ Modern web browsers (Chrome, Firefox, Safari, Edge)
- ✅ Google Docs/Sheets/Slides (bar charts and sparklines via `calt`)
- ✅ Desktop design applications (Adobe CC, Figma, Sketch)
- ⚠️ Pie charts may require manual `liga` feature enablement
- ⚠️ Some applications don't support variable width axis

[1.1.0]: https://github.com/franktisellano/datatype/releases/tag/v1.1.0
[1.0.0]: https://github.com/franktisellano/datatype/releases/tag/v1.0.0
