#!/usr/bin/env python3
"""
Main entry point for the Photo Organizer application.
"""

import sys
import time
from pathlib import Path

from photo_organizer.ui.cli_parser import CLIParser
from photo_organizer.ui.cli_progress import CLIProgressReporter, ProcessingStage


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
        # Launch GUI
        from photo_organizer.ui.gui_app import run_gui
        return run_gui()
    else:
        # Create progress reporter
        reporter = CLIProgressReporter(
            verbose=options["verbose"],
            quiet=options["quiet"],
        )
        
        # Create application core
        from photo_organizer.core import ApplicationCore
        
        app_core = ApplicationCore(reporter)
        
        try:
            # Process images
            success, report = app_core.process_images(
                [str(input_path)],
                str(output_path),
                options,
            )
            
            if success:
                return 0
            else:
                return 1
            
        except KeyboardInterrupt:
            reporter.log_info("\nProcessing interrupted by user")
            app_core.cancel()
            return 1
        except Exception as e:
            reporter.log_error(f"Unexpected error: {e}")
            return 1


if __name__ == "__main__":
    sys.exit(main())