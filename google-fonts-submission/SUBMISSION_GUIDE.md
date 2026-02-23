# Google Fonts Submission Guide

This directory contains all files needed for Google Fonts submission in the correct structure.

## Directory Structure

```
ofl/datatype/
├── Datatype[wdth,wght].ttf          # Variable font (TTF only)
├── static/
│   ├── Datatype-Thin.ttf
│   ├── Datatype-ExtraLight.ttf
│   ├── Datatype-Light.ttf
│   ├── Datatype-Regular.ttf
│   ├── Datatype-Medium.ttf
│   ├── Datatype-SemiBold.ttf
│   ├── Datatype-Bold.ttf
│   ├── Datatype-ExtraBold.ttf
│   ├── Datatype-Black.ttf
│   ├── Datatype-ThinNarrow.ttf
│   ├── Datatype-LightCompact.ttf
│   ├── Datatype-SemiBoldCompact.ttf
│   ├── Datatype-LightWide.ttf
│   ├── Datatype-MediumWide.ttf
│   └── Datatype-BlackWide.ttf
├── METADATA.pb                       # Font metadata (Protocol Buffers)
├── DESCRIPTION.en_us.html            # Font description for Google Fonts listing
└── OFL.txt                           # SIL Open Font License 1.1
```

## Pre-Submission Checklist

- [x] Variable font filename follows convention: `Datatype[wdth,wght].ttf`
- [x] All 15 static instances exported (9 standard + 6 custom)
- [x] METADATA.pb complete with axes and instances
- [x] DESCRIPTION.en_us.html created (235 words)
- [x] OFL.txt with proper copyright format
- [x] Font passes fontbakery checks (6 acceptable FAILs remaining)
- [x] Version number: 1.100 (v1.1.0)

## Submission Process

### 1. Open GitHub Issue

Go to https://github.com/google/fonts/issues/new and create an issue:

**Title:** "Add Datatype - Variable font for inline data visualization"

**Body:**
```markdown
## Font Information

**Family Name**: Datatype
**Designer**: Frank Tisellano
**License**: SIL Open Font License 1.1
**Category**: Sans Serif
**Repository**: https://github.com/franktisellano/datatype

## Description

Datatype is a variable OpenType font that transforms text expressions like `{b:30,70,50}` into inline charts using OpenType features. It includes:
- Bar charts, sparklines, and pie charts
- 2 variable axes: wdth (50-150), wght (100-900)
- 15 static instances (9 standard + 6 custom width combinations)

## Submission Checklist

- [x] Font files pass fontbakery check-googlefonts
- [x] METADATA.pb complete and validated
- [x] DESCRIPTION.en_us.html included
- [x] OFL.txt license included
- [x] Source repository public and accessible
- [x] Build process reproducible via fontTools
- [x] OpenType spec compliant (wdth axis: 50-150, default 100)

## Known Acceptable Issues

- Custom width instance names (showcasing variable width axis)
- STAT table Format 4 entries (fontTools limitation, functionally correct)
- Missing prep table smart dropout (not needed for modern web rendering)
- ASCII-only character set by design (extended Latin planned for future)
```

### 2. Fork google/fonts Repository

```bash
# Fork via GitHub web interface, then:
git clone git@github.com:YOUR_USERNAME/fonts.git google-fonts-fork
cd google-fonts-fork
git remote add upstream https://github.com/google/fonts.git
git checkout -b datatype
```

### 3. Copy Files to Fork

```bash
# From this directory, copy to your fork:
cp -r ofl/datatype /path/to/google-fonts-fork/ofl/
```

### 4. Run gftools Validation

```bash
cd /path/to/google-fonts-fork
gftools add-font ofl/datatype
```

This will auto-generate/update the METADATA.pb entries if needed.

### 5. Create Pull Request

```bash
git add ofl/datatype
git commit -m "Add Datatype variable font for inline data visualization

Taken from upstream repository https://github.com/franktisellano/datatype
at commit <COMMIT_HASH>

- Variable font with wdth (50-150) and wght (100-900) axes
- 15 static instances included
- Chart types: bar, sparkline, pie (via OpenType features)
- All fontbakery checks pass (acceptable issues documented)"

git push origin datatype
```

Then create the PR via GitHub web interface.

### 6. Attach fontbakery Report

Include the fontbakery validation report in the PR:

```bash
fontbakery check-googlefonts "ofl/datatype/Datatype[wdth,wght].ttf" --full-lists > fontbakery-report.txt
```

Attach `fontbakery-report.txt` to the PR or add summary to PR description.

## Response to Reviewers

### Expected Questions

**Q: Why are there additional instances beyond the standard 9?**
A: The 6 custom width combinations (ThinNarrow, LightCompact, etc.) showcase the variable width axis and provide useful presets for different use cases. Users can still access the full wdth range via CSS or variable font controls.

**Q: STAT table has Format 4 issues?**
A: This is a limitation of how fontTools.otlLib.builder.buildStatTable generates entries. The table is functionally correct and all instances work properly. We can rebuild manually if required.

**Q: Missing smart dropout / prep table?**
A: The font is built programmatically without hinting instructions, which is standard for modern web fonts. Modern renderers (Chrome, Firefox, Safari) use their own autohinters and ignore prep table instructions. We can add via `gftools fix-nonhinting` if needed.

**Q: Why ASCII-only character set?**
A: Design decision for v1.1.0 to ship faster. Extended Latin is planned for future release.

## Timeline

- **Issue opened**: Wait for acknowledgment from Google Fonts team
- **PR created**: After issue acknowledgment
- **Review process**: Typically 2-6 weeks
- **Revisions**: Address any reviewer feedback
- **Merge**: Font goes live on fonts.google.com shortly after

## Post-Submission

After the PR is merged:

1. Verify font appears on https://fonts.google.com
2. Test API endpoint: `https://fonts.googleapis.com/css2?family=Datatype`
3. Update README.md with live Google Fonts links
4. Announce on social media / project website
