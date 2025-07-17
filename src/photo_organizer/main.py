#!/usr/bin/env python3
"""
Main entry point for the Photo Organizer application.
"""

import argparse
import sys
from pathlib import Path


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Photo Organizer - Intelligently organize and rename image files."
    )
    parser.add_argument(
        "input_path",
        type=str,
        help="Path to input file or directory containing images to organize",
    )
    parser.add_argument(
        "output_path",
        type=str,
        help="Path to output directory where organized images will be stored",
    )
    parser.add_argument(
        "--gui",
        action="store_true",
        help="Launch the graphical user interface",
    )
    return parser.parse_args()


def main():
    """Main entry point for the application."""
    args = parse_args()
    
    # Validate input path
    input_path = Path(args.input_path)
    if not input_path.exists():
        print(f"Error: Input path '{input_path}' does not exist.", file=sys.stderr)
        return 1
    
    # Validate output path
    output_path = Path(args.output_path)
    if not output_path.exists():
        print(f"Creating output directory: {output_path}")
        output_path.mkdir(parents=True, exist_ok=True)
    
    if args.gui:
        # TODO: Launch GUI
        print("GUI mode not yet implemented.")
        return 1
    else:
        # TODO: Run in CLI mode
        print(f"Processing images from {input_path} to {output_path}")
        print("CLI mode not yet fully implemented.")
        return 0


if __name__ == "__main__":
    sys.exit(main())