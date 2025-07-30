"""Command-line interface for svg2unicode."""

import argparse
import sys
from pathlib import Path
from typing import Optional

from .converter import svg_to_unicode

def parse_args(args: Optional[list[str]] = None) -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description='Convert SVG files to Unicode block characters for terminal display.'
    )
    parser.add_argument(
        'svg_file',
        type=str,
        help='Path to the SVG file to convert'
    )
    parser.add_argument(
        '-w', '--width',
        type=int,
        default=80,
        help='Width of the output in characters (default: 80)'
    )
    return parser.parse_args(args)

def main() -> None:
    """Run the CLI."""
    args = parse_args()
    
    svg_path = Path(args.svg_file)
    if not svg_path.exists():
        print(f"Error: File not found: {svg_path}", file=sys.stderr)
        sys.exit(1)
    
    try:
        result = svg_to_unicode(svg_path, args.width)
        print(result, end='')
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
