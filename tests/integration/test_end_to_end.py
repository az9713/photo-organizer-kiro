"""
End-to-end tests for the Photo Organizer application.
"""

import os
import shutil
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import pytest

from photo_organizer.core import ApplicationCore
from photo_organizer.ui.cli_progress import CLIProgressReporter


class TestEndToEnd:
    """End-to-end tests for the Photo Organizer application."""
    
    @pytest.fixture
    def test_images_dir(self) -> Path:
        """Create a temporary directory with test images."""
        # Create a temporary directory
        temp_dir = Path(tempfile.mkdtemp())
        
        try:
            # Create test images
            self._create_test_images(temp_dir)
            
            yield temp_dir
            
        finally:
            # Clean up
            shutil.rmtree(temp_dir)
    
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
    
    def _create_test_images(self, directory: Path) -> None:
        """
        Create test images in a directory.
        
        Args:
            directory: Directory to create images in
        """
        # Create subdirectories
        vacation_dir = directory / "vacation"
        vacation_dir.mkdir()
        
        family_dir = directory / "family"
        family_dir.mkdir()
        
        # Create test images
        self._create_test_image(vacation_dir / "beach.jpg", "beach")
        self._create_test_image(vacation_dir / "mountain.jpg", "mountain")
        self._create_test_image(family_dir / "portrait.jpg", "portrait")
        self._create_test_image(family_dir / "group.jpg", "group")
        self._create_test_image(directory / "random.jpg", "random")
    
    def _create_test_image(self, path: Path, content: str) -> None:
        """
        Create a test image file.
        
        Args:
            path: Path to create the image at
            content: Content to write to the image
        """
        # In a real test, we would create actual image files
        # For this test, we'll just create text files with the .jpg extension
        with open(path, "w") as f:
            f.write(f"Test image: {content}")
    
    def test_basic_workflow(self, test_images_dir: Path, output_dir: Path) -> None:
        """Test the basic workflow of the application."""
        # Create a progress reporter
        reporter = CLIProgressReporter(verbose=2)
        
        # Create an application core
        app_core = ApplicationCore(reporter)
        
        # Process images
        success, report = app_core.process_images(
            [str(test_images_dir)],
            str(output_dir),
            {
                "recursive": True,
                "parallel_processing": False,
                "similarity_threshold": 0.7,
                "max_category_depth": 3,
            },
        )
        
        # Check that processing was successful
        assert success
        assert report is not None
        
        # Check that output directory contains files
        assert len(list(output_dir.glob("**/*.jpg"))) > 0
        
        # Check that report contains file mappings
        assert len(report.file_mappings) > 0
        
        # Check that report contains folder structure
        assert report.folder_structure is not None
        assert report.folder_structure.subfolders
    
    def test_parallel_processing(self, test_images_dir: Path, output_dir: Path) -> None:
        """Test parallel processing."""
        # Create a progress reporter
        reporter = CLIProgressReporter(verbose=2)
        
        # Create an application core with parallel processing
        app_core = ApplicationCore(reporter, parallel_processing=True, max_workers=2)
        
        # Process images
        success, report = app_core.process_images(
            [str(test_images_dir)],
            str(output_dir),
            {
                "recursive": True,
                "parallel_processing": True,
                "max_workers": 2,
                "similarity_threshold": 0.7,
                "max_category_depth": 3,
            },
        )
        
        # Check that processing was successful
        assert success
        assert report is not None
        
        # Check that output directory contains files
        assert len(list(output_dir.glob("**/*.jpg"))) > 0
        
        # Check that report contains file mappings
        assert len(report.file_mappings) > 0
        
        # Check that report contains folder structure
        assert report.folder_structure is not None
        assert report.folder_structure.subfolders
    
    def test_cancel_processing(self, test_images_dir: Path, output_dir: Path) -> None:
        """Test canceling processing."""
        # Create a progress reporter
        reporter = CLIProgressReporter(verbose=2)
        
        # Create an application core
        app_core = ApplicationCore(reporter)
        
        # Create a function to cancel processing after a short delay
        def cancel_after_delay():
            import threading
            import time
            
            def cancel():
                time.sleep(0.1)
                app_core.cancel()
            
            thread = threading.Thread(target=cancel)
            thread.daemon = True
            thread.start()
        
        # Start cancellation
        cancel_after_delay()
        
        # Process images
        success, report = app_core.process_images(
            [str(test_images_dir)],
            str(output_dir),
            {
                "recursive": True,
                "parallel_processing": False,
                "similarity_threshold": 0.7,
                "max_category_depth": 3,
            },
        )
        
        # Check that processing was canceled
        assert not success
        assert report is None
    
    def test_pause_resume_processing(self, test_images_dir: Path, output_dir: Path) -> None:
        """Test pausing and resuming processing."""
        # Create a progress reporter
        reporter = CLIProgressReporter(verbose=2)
        
        # Create an application core
        app_core = ApplicationCore(reporter)
        
        # Create a function to pause and resume processing after short delays
        def pause_resume_after_delay():
            import threading
            import time
            
            def pause_resume():
                time.sleep(0.1)
                app_core.pause()
                time.sleep(0.2)
                app_core.resume()
            
            thread = threading.Thread(target=pause_resume)
            thread.daemon = True
            thread.start()
        
        # Start pause/resume
        pause_resume_after_delay()
        
        # Process images
        success, report = app_core.process_images(
            [str(test_images_dir)],
            str(output_dir),
            {
                "recursive": True,
                "parallel_processing": False,
                "similarity_threshold": 0.7,
                "max_category_depth": 3,
            },
        )
        
        # Check that processing was successful
        assert success
        assert report is not None
        
        # Check that output directory contains files
        assert len(list(output_dir.glob("**/*.jpg"))) > 0