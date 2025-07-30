# svg2png-clipboard

Convert SVG content from clipboard to PNG and copy it back - perfect for quickly converting SVG icons for use in applications that don't support SVG.

## Features

- 📋 Read SVG directly from clipboard
- 🖼️ Convert to PNG with customizable size
- 📋 Copy PNG back to clipboard automatically
- 💾 Optional file input/output
- 🔔 macOS notifications
- ✅ Robust error handling and dependency checking

## Requirements

- macOS (uses `pbpaste` and `osascript`)
- Python 3.8+
- `rsvg-convert` (from librsvg)

## Installation

### Using pipx (Recommended)

```bash
# Install system dependency first
brew install librsvg

# Install with pipx
pipx install svg2png-clipboard
```

### Using pip

```bash
# Install system dependency
brew install librsvg

# Install package
pip install svg2png-clipboard
```

### From source

```bash
# Clone repository
git clone https://github.com/yourusername/svg2png-clipboard
cd svg2png-clipboard

# Install system dependency
brew install librsvg

# Install package
pip install -e .
```

## Usage

### Basic usage (clipboard to clipboard)

```bash
# Copy SVG to clipboard, then:
svg2png-clipboard
```

### Specify output size

```bash
svg2png-clipboard --size 512  # Creates 512x512 PNG
```

### File operations

```bash
# Read from file, copy to clipboard
svg2png-clipboard --input icon.svg

# Read from clipboard, save to file
svg2png-clipboard --output icon.png

# Read from file, save to file
svg2png-clipboard --input icon.svg --output icon.png
```

### Other options

```bash
# Disable notifications
svg2png-clipboard --no-notification

# Verbose output
svg2png-clipboard --verbose

# Show help
svg2png-clipboard --help
```

## Examples

1. **Quick icon conversion**: Copy an SVG icon from a website, run `svg2png-clipboard`, paste the PNG anywhere

2. **Batch conversion with custom size**:
   ```bash
   svg2png-clipboard -i logo.svg -o logo-256.png -s 256
   ```

3. **Debug mode**:
   ```bash
   svg2png-clipboard --verbose
   ```

## Troubleshooting

### "rsvg-convert is not installed"

Install librsvg using Homebrew:
```bash
brew install librsvg
```

### "This tool only works on macOS"

This tool requires macOS-specific utilities (`pbpaste`, `osascript`). For other platforms, consider using the file input/output options with platform-specific clipboard tools.

### Invalid SVG content

Make sure the clipboard contains valid SVG. You can verify with:
```bash
pbpaste | head -n 5
```

## Development

```bash
# Install in development mode
pip install -e ".[dev]"

# Run tests (if available)
pytest

# Build package
python -m build
```

## License

MIT License

## Author

Hsieh-Ting Lin, the Lizard 🦎