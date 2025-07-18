"""
Unit tests for the CLI argument parser.
"""

import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from photo_organizer.services.reporting import ReportFormat
from photo_organizer.ui.cli_parser import CLIParser


class TestCLIParser:
    """Tests for the CLIParser class."""

    def test_init(self) -> None:
        """Test initializing a CLIParser object."""
        parser = CLIParser()
        assert parser.parser is not None

    def test_parse_args_minimal(self) -> None:
        """Test parsing minimal arguments."""
        parser = CLIParser()
        args = parser.parse_args(["input_path", "output_path"])
        
        assert args.input_path == "input_path"
        assert args.output_path == "output_path"
        assert not args.gui
        assert not args.recursive
        assert args.report == "html"
        assert args.report_path is None
        assert not args.parallel
        assert args.max_workers == 4
        assert args.similarity_threshold == 0.7
        assert args.max_category_depth == 3
        assert args.verbose == 0
        assert not args.quiet

    def test_parse_args_full(self) -> None:
        """Test parsing all arguments."""
        parser = CLIParser()
        args = parser.parse_args([
            "input_path",
            "output_path",
            "--gui",
            "--recursive",
            "--report", "text",
            "--report-path", "report.txt",
            "--parallel",
            "--max-workers", "8",
            "--similarity-threshold", "0.5",
            "--max-category-depth", "5",
            "--verbose",
            "--quiet",
        ])
        
        assert args.input_path == "input_path"
        assert args.output_path == "output_path"
        assert args.gui
        assert args.recursive
        assert args.report == "text"
        assert args.report_path == "report.txt"
        assert args.parallel
        assert args.max_workers == 8
        assert args.similarity_threshold == 0.5
        assert args.max_category_depth == 5
        assert args.verbose == 1
        assert args.quiet

    def test_validate_args_valid(self) -> None:
        """Test validating valid arguments."""
        parser = CLIParser()
        
        with tempfile.TemporaryDirectory() as input_dir:
            with tempfile.TemporaryDirectory() as output_dir:
                args = parser.parse_args([input_dir, output_dir])
                is_valid, error = parser.validate_args(args)
                
                assert is_valid
                assert error is None

    def test_validate_args_invalid_input(self) -> None:
        """Test validating arguments with invalid input path."""
        parser = CLIParser()
        
        with tempfile.TemporaryDirectory() as output_dir:
            args = parser.parse_args(["nonexistent_path", output_dir])
            is_valid, error = parser.validate_args(args)
            
            assert not is_valid
            assert "Input path does not exist" in error

    @patch("pathlib.Path.mkdir")
    def test_validate_args_invalid_output(self, mock_mkdir) -> None:
        """Test validating arguments with invalid output path."""
        parser = CLIParser()
        mock_mkdir.side_effect = PermissionError("Permission denied")
        
        with tempfile.TemporaryDirectory() as input_dir:
            args = parser.parse_args([input_dir, "/invalid/output/path"])
            is_valid, error = parser.validate_args(args)
            
            assert not is_valid
            assert "Cannot create output directory" in error

    def test_validate_args_invalid_similarity(self) -> None:
        """Test validating arguments with invalid similarity threshold."""
        parser = CLIParser()
        
        with tempfile.TemporaryDirectory() as input_dir:
            with tempfile.TemporaryDirectory() as output_dir:
                args = parser.parse_args([
                    input_dir,
                    output_dir,
                    "--similarity-threshold", "1.5",
                ])
                is_valid, error = parser.validate_args(args)
                
                assert not is_valid
                assert "Similarity threshold must be between 0.0 and 1.0" in error

    def test_validate_args_invalid_category_depth(self) -> None:
        """Test validating arguments with invalid category depth."""
        parser = CLIParser()
        
        with tempfile.TemporaryDirectory() as input_dir:
            with tempfile.TemporaryDirectory() as output_dir:
                args = parser.parse_args([
                    input_dir,
                    output_dir,
                    "--max-category-depth", "0",
                ])
                is_valid, error = parser.validate_args(args)
                
                assert not is_valid
                assert "Maximum category depth must be at least 1" in error

    def test_validate_args_invalid_workers(self) -> None:
        """Test validating arguments with invalid number of workers."""
        parser = CLIParser()
        
        with tempfile.TemporaryDirectory() as input_dir:
            with tempfile.TemporaryDirectory() as output_dir:
                args = parser.parse_args([
                    input_dir,
                    output_dir,
                    "--max-workers", "0",
                ])
                is_valid, error = parser.validate_args(args)
                
                assert not is_valid
                assert "Maximum number of workers must be at least 1" in error

    def test_get_processing_options_text_report(self) -> None:
        """Test getting processing options with text report."""
        parser = CLIParser()
        args = parser.parse_args([
            "input_path",
            "output_path",
            "--report", "text",
        ])
        
        options = parser.get_processing_options(args)
        
        assert options["report_format"] == ReportFormat.TEXT
        assert options["report_path"] == "output_path/report.txt"

    def test_get_processing_options_html_report(self) -> None:
        """Test getting processing options with HTML report."""
        parser = CLIParser()
        args = parser.parse_args([
            "input_path",
            "output_path",
            "--report", "html",
        ])
        
        options = parser.get_processing_options(args)
        
        assert options["report_format"] == ReportFormat.HTML
        assert options["report_path"] == "output_path/report.html"

    def test_get_processing_options_both_reports(self) -> None:
        """Test getting processing options with both report formats."""
        parser = CLIParser()
        args = parser.parse_args([
            "input_path",
            "output_path",
            "--report", "both",
        ])
        
        options = parser.get_processing_options(args)
        
        assert isinstance(options["report_format"], list)
        assert ReportFormat.TEXT in options["report_format"]
        assert ReportFormat.HTML in options["report_format"]
        assert isinstance(options["report_path"], dict)
        assert options["report_path"][ReportFormat.TEXT] == "output_path/report.txt"
        assert options["report_path"][ReportFormat.HTML] == "output_path/report.html"

    def test_get_processing_options_custom_report_path(self) -> None:
        """Test getting processing options with custom report path."""
        parser = CLIParser()
        args = parser.parse_args([
            "input_path",
            "output_path",
            "--report", "text",
            "--report-path", "custom_report.txt",
        ])
        
        options = parser.get_processing_options(args)
        
        assert options["report_format"] == ReportFormat.TEXT
        assert options["report_path"] == "custom_report.txt"