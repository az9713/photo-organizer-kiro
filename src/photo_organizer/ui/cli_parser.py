"""
Command-line interface argument parser for the Photo Organizer application.
"""

import argparse
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from photo_organizer.services.reporting import ReportFormat


class CLIParser:
    """Parser for command-line arguments."""
    
    def __init__(self) -> None:
        """Initialize the CLI parser."""
        self.parser = argparse.ArgumentParser(
            description="Photo Organizer - Intelligently organize and rename image files based on content.",
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        )
        self._configure_parser()
    
    def _configure_parser(self) -> None:
        """Configure the argument parser with all supported options."""
        # Required arguments
        self.parser.add_argument(
            "input_path",
            type=str,
            help="Path to input file or directory containing images to organize",
        )
        self.parser.add_argument(
            "output_path",
            type=str,
            help="Path to output directory where organized images will be stored",
        )
        
        # Optional arguments
        self.parser.add_argument(
            "--gui",
            action="store_true",
            help="Launch the graphical user interface",
        )
        self.parser.add_argument(
            "--recursive",
            "-r",
            action="store_true",
            help="Recursively process subdirectories",
        )
        self.parser.add_argument(
            "--report",
            type=str,
            choices=["text", "html", "both"],
            default="html",
            help="Report format to generate",
        )
        self.parser.add_argument(
            "--report-path",
            type=str,
            help="Path to save the report (defaults to output_path/report.[txt|html])",
        )
        self.parser.add_argument(
            "--parallel",
            action="store_true",
            help="Enable parallel processing",
        )
        self.parser.add_argument(
            "--max-workers",
            type=int,
            default=4,
            help="Maximum number of worker threads for parallel processing",
        )
        self.parser.add_argument(
            "--similarity-threshold",
            type=float,
            default=0.7,
            help="Threshold for image similarity (0.0 to 1.0)",
        )
        self.parser.add_argument(
            "--max-category-depth",
            type=int,
            default=3,
            help="Maximum depth of category hierarchy",
        )
        self.parser.add_argument(
            "--verbose",
            "-v",
            action="count",
            default=0,
            help="Increase verbosity level (can be used multiple times)",
        )
        self.parser.add_argument(
            "--quiet",
            "-q",
            action="store_true",
            help="Suppress all output except errors",
        )
        self.parser.add_argument(
            "--version",
            action="version",
            version="%(prog)s 0.1.0",
            help="Show program's version number and exit",
        )
    
    def parse_args(self, args: Optional[List[str]] = None) -> argparse.Namespace:
        """
        Parse command-line arguments.
        
        Args:
            args: Command-line arguments to parse (defaults to sys.argv[1:])
            
        Returns:
            Parsed arguments as a Namespace object
        """
        return self.parser.parse_args(args)
    
    def validate_args(self, args: argparse.Namespace) -> Tuple[bool, Optional[str]]:
        """
        Validate parsed arguments.
        
        Args:
            args: Parsed arguments to validate
            
        Returns:
            A tuple of (is_valid, error_message)
        """
        # Check if input path exists
        input_path = Path(args.input_path)
        if not input_path.exists():
            return False, f"Input path does not exist: {args.input_path}"
        
        # Check if output path exists or can be created
        output_path = Path(args.output_path)
        if not output_path.exists():
            try:
                output_path.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                return False, f"Cannot create output directory: {args.output_path} ({e})"
        
        # Check if report path is valid
        if args.report_path:
            report_path = Path(args.report_path)
            try:
                report_path.parent.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                return False, f"Cannot create report directory: {report_path.parent} ({e})"
        
        # Check if similarity threshold is valid
        if not 0.0 <= args.similarity_threshold <= 1.0:
            return False, f"Similarity threshold must be between 0.0 and 1.0: {args.similarity_threshold}"
        
        # Check if max category depth is valid
        if args.max_category_depth < 1:
            return False, f"Maximum category depth must be at least 1: {args.max_category_depth}"
        
        # Check if max workers is valid
        if args.max_workers < 1:
            return False, f"Maximum number of workers must be at least 1: {args.max_workers}"
        
        return True, None
    
    def get_processing_options(self, args: argparse.Namespace) -> Dict[str, Any]:
        """
        Get processing options from parsed arguments.
        
        Args:
            args: Parsed arguments
            
        Returns:
            A dictionary of processing options
        """
        options = {
            "recursive": args.recursive,
            "parallel_processing": args.parallel,
            "max_workers": args.max_workers,
            "similarity_threshold": args.similarity_threshold,
            "max_category_depth": args.max_category_depth,
            "verbose": args.verbose,
            "quiet": args.quiet,
        }
        
        # Determine report format
        if args.report == "text":
            options["report_format"] = ReportFormat.TEXT
        elif args.report == "html":
            options["report_format"] = ReportFormat.HTML
        else:  # both
            options["report_format"] = [ReportFormat.TEXT, ReportFormat.HTML]
        
        # Determine report path
        if args.report_path:
            options["report_path"] = args.report_path
        else:
            output_path = Path(args.output_path)
            if args.report == "text":
                options["report_path"] = str(output_path / "report.txt")
            elif args.report == "html":
                options["report_path"] = str(output_path / "report.html")
            else:  # both
                options["report_path"] = {
                    ReportFormat.TEXT: str(output_path / "report.txt"),
                    ReportFormat.HTML: str(output_path / "report.html"),
                }
        
        return options