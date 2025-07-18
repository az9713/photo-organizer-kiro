"""
Unit tests for the CLI progress reporting.
"""

import io
import time
from unittest.mock import MagicMock, patch

import pytest

from photo_organizer.ui.cli_progress import CLIProgressReporter, ProcessingStage, ProgressBar


class TestProgressBar:
    """Tests for the ProgressBar class."""

    def test_init(self) -> None:
        """Test initializing a ProgressBar object."""
        bar = ProgressBar(total=100)
        assert bar.total == 100
        assert bar.current == 0
        assert bar.width == 50
        assert bar.prefix == ""
        assert bar.suffix == ""
        assert bar.fill == "█"
        assert bar.empty == "░"
        assert bar.decimals == 1

    def test_update_increment(self) -> None:
        """Test updating a progress bar by incrementing."""
        output = io.StringIO()
        bar = ProgressBar(total=10, file=output)
        
        bar.update()  # Increment by 1
        assert bar.current == 1
        
        # Check that output contains the progress bar
        output_text = output.getvalue()
        assert "|" in output_text
        assert "10.0%" in output_text

    def test_update_specific(self) -> None:
        """Test updating a progress bar to a specific value."""
        output = io.StringIO()
        bar = ProgressBar(total=10, file=output)
        
        bar.update(5)  # Set to 5
        assert bar.current == 5
        
        # Check that output contains the progress bar
        output_text = output.getvalue()
        assert "|" in output_text
        assert "50.0%" in output_text

    def test_update_complete(self) -> None:
        """Test updating a progress bar to completion."""
        output = io.StringIO()
        bar = ProgressBar(total=10, file=output)
        
        bar.update(10)  # Complete
        assert bar.current == 10
        
        # Check that output contains the progress bar and ends with a newline
        output_text = output.getvalue()
        assert "|" in output_text
        assert "100.0%" in output_text
        assert output_text.endswith("\n")

    def test_format_time(self) -> None:
        """Test formatting time."""
        bar = ProgressBar(total=10)
        
        assert bar._format_time(30) == "30s"
        assert bar._format_time(90) == "1m30s"
        assert bar._format_time(3600) == "1h00m"
        assert bar._format_time(3661) == "1h01m"


class TestCLIProgressReporter:
    """Tests for the CLIProgressReporter class."""

    def test_init(self) -> None:
        """Test initializing a CLIProgressReporter object."""
        reporter = CLIProgressReporter()
        assert reporter.verbose == 0
        assert not reporter.quiet
        assert reporter.progress_bars == {}
        assert reporter.current_stage is None
        assert reporter.stage_start_times == {}
        assert reporter.errors == []

    def test_start_stage(self) -> None:
        """Test starting a processing stage."""
        reporter = CLIProgressReporter(verbose=1)
        
        with patch("builtins.print") as mock_print:
            reporter.start_stage(ProcessingStage.ANALYZING)
            
            assert reporter.current_stage == ProcessingStage.ANALYZING
            assert ProcessingStage.ANALYZING in reporter.stage_start_times
            mock_print.assert_called_once()

    def test_start_stage_quiet(self) -> None:
        """Test starting a processing stage in quiet mode."""
        reporter = CLIProgressReporter(quiet=True)
        
        with patch("builtins.print") as mock_print:
            reporter.start_stage(ProcessingStage.ANALYZING)
            
            assert reporter.current_stage == ProcessingStage.ANALYZING
            assert ProcessingStage.ANALYZING not in reporter.stage_start_times
            mock_print.assert_not_called()

    def test_end_stage(self) -> None:
        """Test ending a processing stage."""
        reporter = CLIProgressReporter(verbose=1)
        
        # Start the stage first
        reporter.start_stage(ProcessingStage.ANALYZING)
        
        with patch("builtins.print") as mock_print:
            reporter.end_stage(ProcessingStage.ANALYZING)
            mock_print.assert_called_once()

    def test_start_progress(self) -> None:
        """Test starting a progress bar."""
        reporter = CLIProgressReporter(verbose=1)
        
        with patch("photo_organizer.ui.cli_progress.ProgressBar.update") as mock_update:
            reporter.start_progress("test", 100, "Processing", "files")
            
            assert "test" in reporter.progress_bars
            assert reporter.progress_bars["test"].total == 100
            assert reporter.progress_bars["test"].prefix == "Processing"
            assert reporter.progress_bars["test"].suffix == "files"
            mock_update.assert_called_once_with(0)

    def test_update_progress(self) -> None:
        """Test updating a progress bar."""
        reporter = CLIProgressReporter(verbose=1)
        
        # Start the progress bar first
        reporter.progress_bars["test"] = MagicMock()
        
        reporter.update_progress("test", 50)
        reporter.progress_bars["test"].update.assert_called_once_with(50)

    def test_log_info(self) -> None:
        """Test logging an info message."""
        reporter = CLIProgressReporter(verbose=1)
        
        with patch("builtins.print") as mock_print:
            reporter.log_info("Info message")
            mock_print.assert_called_once_with("Info message")

    def test_log_info_quiet(self) -> None:
        """Test logging an info message in quiet mode."""
        reporter = CLIProgressReporter(quiet=True)
        
        with patch("builtins.print") as mock_print:
            reporter.log_info("Info message")
            mock_print.assert_not_called()

    def test_log_debug(self) -> None:
        """Test logging a debug message."""
        reporter = CLIProgressReporter(verbose=2)
        
        with patch("builtins.print") as mock_print:
            reporter.log_debug("Debug message")
            mock_print.assert_called_once_with("DEBUG: Debug message")

    def test_log_debug_low_verbosity(self) -> None:
        """Test logging a debug message with low verbosity."""
        reporter = CLIProgressReporter(verbose=1)
        
        with patch("builtins.print") as mock_print:
            reporter.log_debug("Debug message")
            mock_print.assert_not_called()

    def test_log_warning(self) -> None:
        """Test logging a warning message."""
        reporter = CLIProgressReporter()
        
        with patch("builtins.print") as mock_print:
            reporter.log_warning("Warning message")
            mock_print.assert_called_once()
            args, kwargs = mock_print.call_args
            assert args[0] == "WARNING: Warning message"
            assert kwargs["file"].__name__ == "stderr"

    def test_log_error(self) -> None:
        """Test logging an error message."""
        reporter = CLIProgressReporter()
        
        with patch("builtins.print") as mock_print:
            reporter.log_error("Error message", "file.jpg")
            mock_print.assert_called_once()
            args, kwargs = mock_print.call_args
            assert args[0] == "ERROR: Error message"
            assert kwargs["file"].__name__ == "stderr"
            
            assert len(reporter.errors) == 1
            assert reporter.errors[0]["file"] == "file.jpg"
            assert reporter.errors[0]["error"] == "Error message"

    def test_get_errors(self) -> None:
        """Test getting all logged errors."""
        reporter = CLIProgressReporter()
        
        reporter.errors = [
            {"file": "file1.jpg", "error": "Error 1"},
            {"file": "file2.jpg", "error": "Error 2"},
        ]
        
        errors = reporter.get_errors()
        assert len(errors) == 2
        assert errors[0]["file"] == "file1.jpg"
        assert errors[1]["file"] == "file2.jpg"