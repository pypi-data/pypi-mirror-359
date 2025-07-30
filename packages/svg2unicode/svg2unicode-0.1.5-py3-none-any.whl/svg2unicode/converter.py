"""SVG to Unicode converter implementation."""

import io
from pathlib import Path
from typing import Union

import cairosvg
from PIL import Image, ImageOps

# Unicode block characters - from light to dark
# Block-shade characters for full-width raster mode
BLOCKS = [
    ' ',      # 0/8: No block
    '▁',      # 1/8: Lower one eighth block
    '▂',      # 2/8: Lower one quarter block
    '▄',      # 3/8: Lower three eighths block
    '▅',      # 4/8: Lower half block
    '▆',      # 5/8: Lower five eighths block
    '▇',      # 6/8: Lower three quarters block
    '█',      # 7/8: Lower seven eighths block
    '█',      # 8/8: Full block
]

def svg_to_image(svg_path: Union[str, Path], width: int = 80) -> Image.Image:
    """
    Convert an SVG file to a PIL Image.
    
    Args:
        svg_path: Path to the SVG file
        width: Desired width of the output image (height is calculated to maintain aspect ratio)
        
    Returns:
        PIL.Image: Grayscale image
    """
    # Convert SVG to PNG in memory
    png_data = cairosvg.svg2png(url=str(svg_path), output_width=width)
    
    # Convert PNG data to PIL Image
    img = Image.open(io.BytesIO(png_data))
    
    # Convert to grayscale
    img = ImageOps.grayscale(img)
    
    return img

# -------------------------------------------------
#  Single-glyph (Braille) conversion helpers
# -------------------------------------------------
DOT_MAP = {
    (0, 0): 1,  # row, col -> braille dot index
    (1, 0): 2,
    (2, 0): 3,
    (3, 0): 7,
    (0, 1): 4,
    (1, 1): 5,
    (2, 1): 6,
    (3, 1): 8,
}


def image_to_glyph(img: Image.Image) -> str:
    """Convert an image to a single Braille glyph (⣿ range).

    The image is down-sampled to 4 × 8 (width × height) pixels, then each
    column is folded into a single Braille dot column (2 columns → 8 dots).
    A pixel <128 grayscale sets the corresponding dot.
    """
    small = img.resize((4, 8), Image.LANCZOS).convert("L")
    pixels = small.load()

    value = 0
    for y in range(8):
        for x in range(2):  # two columns in Braille cell
            # original image has 4 columns → fold (0,2) into dot col 0; (1,3) into col 1
            px_x = x * 2  # 0 or 2
            # OR the two source columns per braille column
            bright1 = pixels[px_x, y]
            bright2 = pixels[px_x + 1, y]
            dark = (bright1 < 128) or (bright2 < 128)
            if dark:
                dot_index = DOT_MAP[(y // 2, x)]  # y//2 groups rows into 4 levels
                value |= 1 << (dot_index - 1)

    return chr(0x2800 | value)


def svg_to_glyph(svg_path: Union[str, Path]) -> str:
    """Convert an SVG to a single Unicode Braille character."""
    img = svg_to_image(svg_path, width=32)  # small raster for good sampling
    return image_to_glyph(img)

def image_to_unicode(img: Image.Image, width: int = 80) -> str:
    """
    Convert a grayscale PIL Image to Unicode block characters.
    
    Args:
        img: Input grayscale image
        width: Desired width in characters
        
    Returns:
        str: String containing the Unicode block representation
    """
    # Resize image to desired width while maintaining aspect ratio
    aspect_ratio = img.height / img.width
    height = int(width * aspect_ratio * 0.5)  # 0.5 because block characters are roughly 2:1 aspect
    
    if height == 0:
        height = 1
    
    img = img.resize((width, height), Image.LANCZOS)
    
    # Convert to Unicode block characters
    result = []
    pixels = img.load()
    
    for y in range(img.height):
        line = []
        for x in range(img.width):
            # Get pixel brightness (0-255)
            brightness = pixels[x, y]
            # Convert to block character index (0-8)
            block_idx = min(int(brightness / 32), 8)
            line.append(BLOCKS[block_idx])
        result.append(''.join(line) + '\n')
    
    return ''.join(result)

def svg_to_unicode(svg_path: Union[str, Path], width: int = 80) -> str:
    """
    Convert an SVG file to Unicode block characters.
    
    Args:
        svg_path: Path to the SVG file
        width: Desired width in characters
        
    Returns:
        str: Unicode block representation of the SVG
    """
    img = svg_to_image(svg_path, width * 2)  # Multiply by 2 for better resolution
    return image_to_unicode(img, width)
