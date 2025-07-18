"""
Unit tests for the ApplicationCore class.
"""

import os
import time
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from photo_organizer.core import ApplicationCore
from photo_organizer.models.category import Category
from photo_organizer.models.category_tree import CategoryTree
from photo_organizer.models.image import Image
from photo_organizer.services.reporting import ReportFormat
from photo_organizer.ui.cli_progress import CLIProgressReporter, ProcessingStage


@pytest.fixture
def mock_progress_reporter():
    """Create a mock progress reporter."""
    reporter = MagicMock(spec=CLIProgressReporter)
    reporter.errors = []
    return reporter


@pytest.fixture
def core(mock_progress_reporter):
    """Create an ApplicationCore instance with mock services."""
    core = ApplicationCore(mock_progress_reporter)
    
    # Mock services
    core.file_system_manager = MagicMock()
    core.file_operations = MagicMock()
    core.analysis_service = MagicMock()
    core.categorization_service = MagicMock()
    core.reporting_service = MagicMock()
    core.report_export_service = MagicMock()
    core.file_mapping_service = MagicMock()
    
    return core


class TestApplicationCore:
    """Tests for the ApplicationCore class."""

    def test_init(self, mock_progress_reporter) -> None:
        """Test initializing an ApplicationCore object."""
        core = ApplicationCore(mock_progress_reporter)
        
        assert core.progress_reporter == mock_progress_reporter
        assert core.file_system_manager is not None
        assert core.file_operations is not None
        assert core.analysis_service is not None
        assert core.categorization_service is not None
        assert core.reporting_service is not None
        assert core.report_export_service is not None
        assert core.file_mapping_service is not None
        assert not core.canceled
        assert not core.paused
        assert core.current_stage is None

    def test_cancel(self, core) -> None:
        """Test canceling processing."""
        core.cancel()
        
        assert core.canceled
        core.progress_reporter.log_info.assert_called_once_with("Canceling operation...")

    def test_pause_resume(self, core) -> None:
        """Test pausing and resuming processing."""
        core.pause()
        
        assert core.paused
        core.progress_reporter.log_info.assert_called_once_with("Pausing operation...")
        
        core.resume()
        
        assert not core.paused
        core.progress_reporter.log_info.assert_called_with("Resuming operation...")

    @patch("os.path.exists")
    def test_validate_paths_valid(self, mock_exists, core) -> None:
        """Test validating valid paths."""
        mock_exists.return_value = True
        
        # Should not raise an exception
        core._validate_paths(["input1.jpg", "input2.jpg"], "output")
        
        mock_exists.assert_any_call("input1.jpg")
        mock_exists.assert_any_call("input2.jpg")

    @patch("os.path.exists")
    def test_validate_paths_invalid_input(self, mock_exists, core) -> None:
        """Test validating invalid input paths."""
        mock_exists.side_effect = [False, True]
        
        with pytest.raises(ValueError, match="Input path does not exist"):
            core._validate_paths(["nonexistent.jpg", "input2.jpg"], "output")

    @patch("os.path.exists")
    @patch("os.path.isdir")
    def test_validate_paths_invalid_output(self, mock_isdir, mock_exists, core) -> None:
        """Test validating invalid output path."""
        mock_exists.return_value = True
        mock_isdir.return_value = False
        
        with pytest.raises(ValueError, match="Output path exists but is not a directory"):
            core._validate_paths(["input.jpg"], "output.txt")

    def test_is_image_file(self, core) -> None:
        """Test checking if a file is an image."""
        assert core._is_image_file(Path("image.jpg"))
        assert core._is_image_file(Path("image.jpeg"))
        assert core._is_image_file(Path("image.png"))
        assert core._is_image_file(Path("image.gif"))
        assert core._is_image_file(Path("image.bmp"))
        assert core._is_image_file(Path("image.tiff"))
        assert core._is_image_file(Path("image.tif"))
        assert core._is_image_file(Path("image.webp"))
        assert not core._is_image_file(Path("document.txt"))
        assert not core._is_image_file(Path("archive.zip"))

    @patch("os.path.exists")
    @patch("os.makedirs")
    @patch("time.time")
    def test_process_images_success(self, mock_time, mock_makedirs, mock_exists, core) -> None:
        """Test processing images successfully."""
        # Mock path validation
        mock_exists.return_value = True
        
        # Mock time
        mock_time.side_effect = [0, 100]  # Start time, end time
        
        # Mock scanning
        core._scan_input_paths = MagicMock(return_value=["image1.jpg", "image2.jpg", "image3.jpg"])
        
        # Mock analysis
        image1 = MagicMock(spec=Image)
        image1.path = Path("image1.jpg")
        image1.id = "image1"
        
        image2 = MagicMock(spec=Image)
        image2.path = Path("image2.jpg")
        image2.id = "image2"
        
        image3 = MagicMock(spec=Image)
        image3.path = Path("image3.jpg")
        image3.id = "image3"
        
        core._analyze_images = MagicMock(return_value=[image1, image2, image3])
        
        # Mock categorization
        category_tree = MagicMock(spec=CategoryTree)
        core._categorize_images = MagicMock(return_value=category_tree)
        
        # Mock organization
        core._organize_images = MagicMock(return_value=[image1, image2])
        
        # Mock report generation
        report = MagicMock()
        core._generate_report = MagicMock(return_value=report)
        
        # Mock report export
        core._export_report = MagicMock()
        
        # Process images
        success, result = core.process_images(
            ["input1.jpg", "input2.jpg"],
            "output",
            {"report_format": ReportFormat.HTML},
        )
        
        # Check result
        assert success
        assert result == report
        
        # Check that all stages were started
        core.progress_reporter.start_stage.assert_any_call(ProcessingStage.INITIALIZING)
        core.progress_reporter.start_stage.assert_any_call(ProcessingStage.SCANNING)
        core.progress_reporter.start_stage.assert_any_call(ProcessingStage.ANALYZING)
        core.progress_reporter.start_stage.assert_any_call(ProcessingStage.CATEGORIZING)
        core.progress_reporter.start_stage.assert_any_call(ProcessingStage.ORGANIZING)
        core.progress_reporter.start_stage.assert_any_call(ProcessingStage.REPORTING)
        core.progress_reporter.start_stage.assert_any_call(ProcessingStage.COMPLETED)
        
        # Check that output directory was created
        mock_makedirs.assert_called_once_with("output", exist_ok=True)
        
        # Check that scanning was performed
        core._scan_input_paths.assert_called_once_with(["input1.jpg", "input2.jpg"], False)
        
        # Check that analysis was performed
        core._analyze_images.assert_called_once_with(["image1.jpg", "image2.jpg", "image3.jpg"])
        
        # Check that categorization was performed
        core._categorize_images.assert_called_once()
        
        # Check that organization was performed
        core._organize_images.assert_called_once_with([image1, image2, image3], category_tree, "output")
        
        # Check that report was generated
        core._generate_report.assert_called_once()
        
        # Check that report was exported
        core._export_report.assert_called_once_with(report, ReportFormat.HTML, None, "output")

    @patch("os.path.exists")
    def test_process_images_no_images(self, mock_exists, core) -> None:
        """Test processing with no images found."""
        # Mock path validation
        mock_exists.return_value = True
        
        # Mock scanning
        core._scan_input_paths = MagicMock(return_value=[])
        
        # Process images
        success, result = core.process_images(["input"], "output", {})
        
        # Check result
        assert not success
        assert result is None
        
        # Check warning
        core.progress_reporter.log_warning.assert_called_once_with("No image files found in input paths")

    @patch("os.path.exists")
    def test_process_images_canceled(self, mock_exists, core) -> None:
        """Test processing with cancellation."""
        # Mock path validation
        mock_exists.return_value = True
        
        # Mock scanning
        core._scan_input_paths = MagicMock(return_value=["image1.jpg", "image2.jpg"])
        
        # Set canceled flag
        core.canceled = True
        
        # Process images
        success, result = core.process_images(["input"], "output", {})
        
        # Check result
        assert not success
        assert result is None
        
        # Check info message
        core.progress_reporter.log_info.assert_any_call("Operation canceled")

    @patch("os.path.exists")
    def test_process_images_error(self, mock_exists, core) -> None:
        """Test processing with an error."""
        # Mock path validation
        mock_exists.side_effect = Exception("Test error")
        
        # Process images
        success, result = core.process_images(["input"], "output", {})
        
        # Check result
        assert not success
        assert result is None
        
        # Check error message
        core.progress_reporter.log_error.assert_called_once_with("Error during processing: Test error")

    def test_generate_filename(self, core) -> None:
        """Test generating a filename."""
        # Create mock image and category
        image = MagicMock(spec=Image)
        image.path = Path("image.jpg")
        image.content_tags = ["dog", "beach"]
        
        category = MagicMock(spec=Category)
        category.name = "Vacation"
        
        # Generate filename
        with patch("uuid.uuid4", return_value="12345678-1234-5678-1234-567812345678"):
            filename = core._generate_filename(image, category)
        
        # Check filename
        assert filename.startswith("vacation_dog_12345678")
        assert filename.endswith(".jpg")

    def test_generate_filename_no_tags(self, core) -> None:
        """Test generating a filename with no content tags."""
        # Create mock image and category
        image = MagicMock(spec=Image)
        image.path = Path("image.jpg")
        image.content_tags = []
        
        category = MagicMock(spec=Category)
        category.name = "Vacation"
        
        # Generate filename
        with patch("uuid.uuid4", return_value="12345678-1234-5678-1234-567812345678"):
            filename = core._generate_filename(image, category)
        
        # Check filename
        assert filename.startswith("vacation_12345678")
        assert filename.endswith(".jpg")