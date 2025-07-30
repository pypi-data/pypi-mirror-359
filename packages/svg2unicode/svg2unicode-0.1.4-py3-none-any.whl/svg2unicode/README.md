# SVG to Unicode

Convert SVG files to Unicode block characters for terminal display.

## Installation

```bash
pip install svg2unicode
```

## Usage

### Command Line

```bash
svg2unicode path/to/your/image.svg
```

Options:
- `-w`, `--width`: Width of the output in characters (default: 80)

### Python API

```python
from svg2unicode import svg_to_unicode

# Convert SVG to unicode blocks
result = svg_to_unicode("path/to/your/image.svg", width=80)
print(result)
```

## Examples

```bash
# Display an SVG file at 40 characters width
svg2unicode example.svg -w 40
```

## Requirements

- Python 3.7+
- Pillow
- CairoSVG

## License

MIT
