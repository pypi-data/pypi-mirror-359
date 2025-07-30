"""
SVG to Unicode Block Character Converter

This package provides functionality to convert SVG files to Unicode block characters
for display in terminal environments.
"""

from .cli import main
from .converter import svg_to_unicode, image_to_unicode, svg_to_image

__version__ = "0.1.0"
__all__ = ['svg_to_unicode', 'image_to_unicode', 'svg_to_image', 'main']
