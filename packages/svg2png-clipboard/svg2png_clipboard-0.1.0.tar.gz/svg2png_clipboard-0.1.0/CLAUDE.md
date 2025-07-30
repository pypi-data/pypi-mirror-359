# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This is a macOS utility that converts SVG content from the clipboard to PNG format and copies the PNG back to the clipboard. The tool is designed for quick SVG-to-PNG conversions with a fixed output size of 180×180 pixels.

## Dependencies

- Python 3.8+
- `pyperclipimg` - Python package for clipboard image operations
- `click` - CLI framework
- `rsvg-convert` - Command-line tool for SVG to PNG conversion (install via Homebrew: `brew install librsvg`)
- macOS system tools: `pbpaste`, `osascript`

## Package Structure

```
svg2png_clipboard/
├── __init__.py      # Package metadata
├── core.py          # Core conversion logic with dependency checking
└── cli.py           # Click-based CLI interface
```

## Key Components

### core.py
- Robust dependency checking with helpful error messages
- SVG validation and conversion functions
- Clipboard operations using pyperclipimg
- macOS notification support

### cli.py
- Click-based CLI with options for:
  - Custom output size (`--size`)
  - File input/output (`--input`, `--output`)
  - Notification control (`--no-notification`)
  - Verbose output (`--verbose`)

## Installation & Usage

```bash
# Install with pipx (recommended)
pipx install svg2png-clipboard

# Basic usage
svg2png-clipboard

# With options
svg2png-clipboard --size 512 --verbose
```

## Architecture Notes

- Uses temporary files for SVG/PNG conversion (automatically cleaned up)
- Fixed output size of 180×180 pixels (defined by `IMG_SIZE` constant)
- macOS-specific implementation using `pbpaste` and `osascript`
- Error handling for invalid SVG content