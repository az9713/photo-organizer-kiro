"""
Error handling tests for the Photo Organizer application.
"""

import os
import shutil
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import pytest

from photo_organizer.core import ApplicationCore
from photo_organizer.ui.cli_progress import CLIProgressReporter
from tests.integration.test_dataset import test_dataset


class TestErrorHandling:
    """Error handling tests for the Photo Organizer application."""
    
    @pytest.fixture
    def corrupted_image(self) -> Path:
        """Create a corrupted image file."""
        # Create a temporary file
        fd, path = tempfile.mkstemp(suffix=".jpg")
        os.close(fd)
        
        # Write invalid data to the file
        with open(path, "w") as f:
            f.write("This is not a valid image file")
        
        try:
            yield Path(path)
            
        finally:
            # Clean up
            os.unlink(path)
    
    @pytest.fixture
    def output_dir(self) -> Path:
        """Create a temporary output directory."""
        # Create a temporary directory
        temp_dir = Path(tempfile.mkdtemp())
        
        try:
            yield temp_dir
            
        finally:
            # Clean up
            shutil.rmtree(temp_dir)
    
    def test_corrupted_image(self, corrupted_image: Path, output_dir: Path) -> None:
        """Test handling of corrupted images."""
        # Create a progress reporter
        reporter = CLIProgressReporter(verbose=2)
        
        # Create an application core
        app_core = ApplicationCore(reporter)
        
        # Process the corrupted image
        success, report = app_core.process_images(
            [str(corrupted_image)],
            str(output_dir),
            {
                "recursive": False,
                "parallel_processing": False,
                "similarity_threshold": 0.7,
                "max_category_depth": 3,
            },
        )
        
        # Check that processing was not successful
        assert not success
        assert report is None
        
        # Check that the error was logged
        assert len(reporter.errors) > 0
        assert any("corrupted" in error["error"].lower() for error in reporter.errors)
    
    def test_permission_issues(self, test_dataset: Tuple[Path, Dict[str, List[Path]]]) -> None:
        """Test handling of permission issues."""
        base_dir, dataset = test_dataset
        
        # Create a read-only output directory
        output_dir = base_dir / "readonly_output"
        output_dir.mkdir()
        
        # Make the output directory read-only
        os.chmod(output_dir, 0o444)  # Read-only for all users
        
        try:
            # Create a progress reporter
            reporter = CLIProgressReporter(verbose=2)
            
            # Create an application core
            app_core = ApplicationCore(reporter)
            
            # Get all image paths
            all_images = []
            for category, images in dataset.items():
                all_images.extend(images)
            
            # Process images
            success, report = app_core.process_images(
                [str(path) for path in all_images[:1]],  # Just process one image
                str(output_dir),
                {
                    "recursive": False,
                    "parallel_processing": False,
                    "similarity_threshold": 0.7,
                    "max_category_depth": 3,
                },
            )
            
            # Check that processing was not successful
            assert not success
            assert report is None
            
            # Check that the error was logged
            assert len(reporter.errors) > 0
            assert any("permission" in error["error"].lower() for error in reporter.errors)
            
        finally:
            # Restore permissions so we can delete the directory
            os.chmod(output_dir, 0o777)
    
    def test_invalid_inputs(self, output_dir: Path) -> None:
        """Test handling of invalid inputs."""
        # Create a progress reporter
        reporter = CLIProgressReporter(verbose=2)
        
        # Create an application core
        app_core = ApplicationCore(reporter)
        
        # Test with non-existent input path
        success, report = app_core.process_images(
            ["non_existent_path"],
            str(output_dir),
            {
                "recursive": False,
                "parallel_processing": False,
                "similarity_threshold": 0.7,
                "max_category_depth": 3,
            },
        )
        
        # Check that processing was not successful
        assert not success
        assert report is None
        
        # Check that the error was logged
        assert len(reporter.errors) > 0
        assert any("exist" in error["error"].lower() for error in reporter.errors)
        
        # Test with invalid similarity threshold
        success, report = app_core.process_images(
            [str(output_dir)],  # Use output_dir as input (it exists but has no images)
            str(output_dir),
            {
                "recursive": False,
                "parallel_processing": False,
                "similarity_threshold": 1.5,  # Invalid threshold (should be 0.0-1.0)
                "max_category_depth": 3,
            },
        )
        
        # Check that processing was not successful
        assert not success
        assert report is None
        
        # Check that the error was logged
        assert len(reporter.errors) > 0
        assert any("threshold" in error["error"].lower() for error in reporter.errors)
        
        # Test with invalid max_category_depth
        success, report = app_core.process_images(
            [str(output_dir)],  # Use output_dir as input (it exists but has no images)
            str(output_dir),
            {
                "recursive": False,
                "parallel_processing": False,
                "similarity_threshold": 0.7,
                "max_category_depth": 0,  # Invalid depth (should be >= 1)
            },
        )
        
        # Check that processing was not successful
        assert not success
        assert report is None
        
        # Check that the error was logged
        assert len(reporter.errors) > 0
        assert any("depth" in error["error"].lower() for error in reporter.errors)
    
    def test_error_recovery(self, test_dataset: Tuple[Path, Dict[str, List[Path]]]) -> None:
        """Test recovery from errors."""
        base_dir, dataset = test_dataset
        output_dir = base_dir / "output"
        output_dir.mkdir()
        
        # Create a corrupted image
        corrupted_path = base_dir / "corrupted.jpg"
        with open(corrupted_path, "w") as f:
            f.write("This is not a valid image file")
        
        # Get all image paths
        all_images = [corrupted_path]  # Start with the corrupted image
        for category, images in dataset.items():
            all_images.extend(images)
        
        # Create a progress reporter
        reporter = CLIProgressReporter(verbose=2)
        
        # Create an application core
        app_core = ApplicationCore(reporter)
        
        # Process images
        success, report = app_core.process_images(
            [str(path) for path in all_images],
            str(output_dir),
            {
                "recursive": False,
                "parallel_processing": False,
                "similarity_threshold": 0.7,
                "max_category_depth": 3,
            },
        )
        
        # Check that processing was successful despite the corrupted image
        assert success
        assert report is not None
        
        # Check that the error was logged
        assert len(reporter.errors) > 0
        assert any("corrupted" in error["error"].lower() for error in reporter.errors)
        
        # Check that other images were processed
        assert len(report.file_mappings) > 0
        assert len(list(output_dir.glob("**/*.jpg"))) > 0