"""SVG to Unicode converter implementation."""

import io
import math
from pathlib import Path
from typing import Optional, Union

import cairosvg
from PIL import Image, ImageOps

# Unicode block characters - from light to dark
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
