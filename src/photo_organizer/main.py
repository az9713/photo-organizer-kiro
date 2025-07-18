#!/usr/bin/env python3
"""
Main entry point for the Photo Organizer application.
"""

import sys
from pathlib import Path

from photo_organizer.ui.cli_parser import CLIParser


def main():
    """Main entry point for the application."""
    # Parse command line arguments
    cli_parser = CLIParser()
    args = cli_parser.parse_args()
    
    # Validate arguments
    is_valid, error_message = cli_parser.validate_args(args)
    if not is_valid:
        print(f"Error: {error_message}", file=sys.stderr)
        return 1
    
    # Get processing options
    options = cli_parser.get_processing_options(args)
    
    # Convert paths to Path objects
    input_path = Path(args.input_path)
    output_path = Path(args.output_path)
    
    if args.gui:
        # TODO: Launch GUI
        print("GUI mode not yet implemented.")
        return 1
    else:
        # TODO: Run in CLI mode
        if not options["quiet"]:
            print(f"Processing images from {input_path} to {output_path}")
            if options["verbose"] > 0:
                print("Processing options:")
                for key, value in options.items():
                    print(f"  {key}: {value}")
        
        # TODO: Implement the actual processing
        print("CLI mode not yet fully implemented.")
        return 0


if __name__ == "__main__":
    sys.exit(main())