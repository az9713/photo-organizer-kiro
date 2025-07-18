"""
Utility for detecting image formats.
"""

import argparse
import sys
from pathlib import Path

from photo_organizer.services.image_format import ImageFormatError, ImageFormatService


def detect_format(path: Path) -> None:
    """
    Detect the format of an image file and print the result.
    
    Args:
        path: The path to the image file
    """
    service = ImageFormatService()
    
    try:
        format_type = service.detect_format(path)
        if format_type is None:
            print(f"Failed to detect format of {path}")
        else:
            print(f"{path}: {format_type.name}")
    except Exception as e:
        print(f"Error: {e}")


def main() -> int:
    """Main entry point for the format detector utility."""
    parser = argparse.ArgumentParser(description="Detect image formats")
    parser.add_argument("paths", nargs="+", help="Paths to image files")
    
    args = parser.parse_args()
    
    for path_str in args.paths:
        path = Path(path_str)
        if path.exists():
            detect_format(path)
        else:
            print(f"File not found: {path}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())