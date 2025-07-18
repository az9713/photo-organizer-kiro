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
        # TODO: Launch GUI
        print("GUI mode not yet implemented.")
        return 1
    else:
        # Create progress reporter
        reporter = CLIProgressReporter(
            verbose=options["verbose"],
            quiet=options["quiet"],
        )
        
        # Log basic information
        reporter.log_info(f"Processing images from {input_path} to {output_path}")
        if options["verbose"] > 1:
            reporter.log_info("Processing options:")
            for key, value in options.items():
                reporter.log_info(f"  {key}: {value}")
        
        # Simulate processing stages for demonstration
        try:
            # Initializing
            reporter.start_stage(ProcessingStage.INITIALIZING)
            time.sleep(0.5)  # Simulate initialization
            reporter.end_stage(ProcessingStage.INITIALIZING)
            
            # Scanning
            reporter.start_stage(ProcessingStage.SCANNING)
            reporter.start_progress("scan", 100, "Scanning files", "")
            for i in range(100):
                time.sleep(0.01)  # Simulate scanning
                reporter.update_progress("scan", i + 1)
            reporter.end_stage(ProcessingStage.SCANNING)
            
            # Analyzing
            reporter.start_stage(ProcessingStage.ANALYZING)
            reporter.start_progress("analyze", 50, "Analyzing images", "")
            for i in range(50):
                time.sleep(0.05)  # Simulate analysis
                reporter.update_progress("analyze", i + 1)
                if i == 10:
                    reporter.log_warning("Low quality image detected")
                if i == 20:
                    reporter.log_error("Failed to analyze image", "bad_image.jpg")
            reporter.end_stage(ProcessingStage.ANALYZING)
            
            # Categorizing
            reporter.start_stage(ProcessingStage.CATEGORIZING)
            reporter.start_progress("categorize", 50, "Categorizing images", "")
            for i in range(50):
                time.sleep(0.02)  # Simulate categorization
                reporter.update_progress("categorize", i + 1)
            reporter.end_stage(ProcessingStage.CATEGORIZING)
            
            # Organizing
            reporter.start_stage(ProcessingStage.ORGANIZING)
            reporter.start_progress("organize", 50, "Organizing images", "")
            for i in range(50):
                time.sleep(0.03)  # Simulate organization
                reporter.update_progress("organize", i + 1)
            reporter.end_stage(ProcessingStage.ORGANIZING)
            
            # Reporting
            reporter.start_stage(ProcessingStage.REPORTING)
            time.sleep(0.5)  # Simulate report generation
            reporter.end_stage(ProcessingStage.REPORTING)
            
            # Completed
            reporter.start_stage(ProcessingStage.COMPLETED)
            reporter.log_info("Processing completed successfully")
            reporter.log_info(f"Processed 49 images (1 error)")
            reporter.end_stage(ProcessingStage.COMPLETED)
            
            # Show errors if any
            errors = reporter.get_errors()
            if errors:
                reporter.log_info(f"\nEncountered {len(errors)} errors:")
                for error in errors:
                    reporter.log_info(f"  {error['file']}: {error['error']}")
            
            return 0
            
        except KeyboardInterrupt:
            reporter.log_info("\nProcessing interrupted by user")
            return 1
        except Exception as e:
            reporter.log_error(f"Unexpected error: {e}")
            return 1


if __name__ == "__main__":
    sys.exit(main())