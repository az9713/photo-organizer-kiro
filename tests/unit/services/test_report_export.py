"""
Unit tests for the report export functionality.
"""

import os
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, mock_open, patch

import pytest

from photo_organizer.models.image import GeoLocation, Image, ImageMetadata
from photo_organizer.services.reporting import (
    FileMapping,
    FolderNode,
    Report,
    ReportFormat,
    ReportSummary,
)
from photo_organizer.services.report_export import ReportExportService


@pytest.fixture
def sample_folder_structure():
    """Create a sample folder structure for testing."""
    root = FolderNode(name="root", path="/output/path")
    vacation = FolderNode(name="Vacation", path="/output/path/Vacation")
    beach = FolderNode(name="Beach", path="/output/path/Vacation/Beach")
    mountains = FolderNode(name="Mountains", path="/output/path/Vacation/Mountains")
    
    root.add_subfolder(vacation)
    vacation.add_subfolder(beach)
    vacation.add_subfolder(mountains)
    
    beach.add_file("beach1.jpg")
    beach.add_file("beach2.jpg")
    mountains.add_file("mountain1.jpg")
    
    return root


@pytest.fixture
def sample_file_mappings():
    """Create sample file mappings for testing."""
    return [
        FileMapping(
            original_path="/input/path/img1.jpg",
            new_path="/output/path/Vacation/Beach/beach1.jpg",
            category="Vacation/Beach",
            timestamp=datetime(2025, 2, 8, 15, 15),
            geolocation="The White House, 1600 Pennsylvania Ave NW, Washington, 20500",
        ),
        FileMapping(
            original_path="/input/path/img2.jpg",
            new_path="/output/path/Vacation/Beach/beach2.jpg",
            category="Vacation/Beach",
            timestamp=datetime(2025, 2, 9, 10, 30),
            geolocation="Smithsonian National Museum of Natural History, 10th St. & Constitution Ave. NW, Washington, 20560",
        ),
        FileMapping(
            original_path="/input/path/img3.jpg",
            new_path="/output/path/Vacation/Mountains/mountain1.jpg",
            category="Vacation/Mountains",
            timestamp=datetime(2025, 2, 10, 8, 45),
            geolocation="Grand Canyon National Park, Arizona, United States",
        ),
    ]


@pytest.fixture
def sample_report(sample_folder_structure, sample_file_mappings):
    """Create a sample report for testing."""
    summary = ReportSummary(
        total_files=5,
        processed_files=3,
        skipped_files=2,
        error_count=0,
        folders_created=4,
        processing_time=120.5,
    )
    
    return Report(
        summary=summary,
        folder_structure=sample_folder_structure,
        file_mappings=sample_file_mappings,
    )


class TestReportExportService:
    """Tests for the ReportExportService class."""

    def test_init(self):
        """Test initializing a ReportExportService object."""
        service = ReportExportService()
        assert service is not None

    @patch("builtins.open", new_callable=mock_open)
    def test_export_text_report(self, mock_file, sample_report):
        """Test exporting a report in text format."""
        service = ReportExportService()
        
        output_path = "/output/report.txt"
        service.export_report(sample_report, ReportFormat.TEXT, output_path)
        
        mock_file.assert_called_once_with(output_path, "w", encoding="utf-8")
        handle = mock_file()
        
        # Check that the report content was written to the file
        assert handle.write.called
        
        # Check that the report content contains expected sections
        calls = [call[0][0] for call in handle.write.call_args_list]
        content = "".join(calls)
        
        assert "Photo Organizer Report" in content
        assert "Summary" in content
        assert "Folder Structure" in content
        assert "File Mappings" in content
        assert "Total files: 5" in content
        assert "Processed files: 3" in content
        assert "Vacation/Beach" in content
        assert "2/8/2025 3:15pm" in content
        assert "The White House" in content

    @patch("builtins.open", new_callable=mock_open)
    def test_export_html_report(self, mock_file, sample_report):
        """Test exporting a report in HTML format."""
        service = ReportExportService()
        
        output_path = "/output/report.html"
        service.export_report(sample_report, ReportFormat.HTML, output_path)
        
        mock_file.assert_called_once_with(output_path, "w", encoding="utf-8")
        handle = mock_file()
        
        # Check that the report content was written to the file
        assert handle.write.called
        
        # Check that the report content contains expected HTML elements
        calls = [call[0][0] for call in handle.write.call_args_list]
        content = "".join(calls)
        
        assert "<!DOCTYPE html>" in content
        assert "<html>" in content
        assert "<head>" in content
        assert "<title>Photo Organizer Report</title>" in content
        assert "<body>" in content
        assert "<h1>Photo Organizer Report</h1>" in content
        assert "<h2>Summary</h2>" in content
        assert "<h2>Folder Structure</h2>" in content
        assert "<h2>File Mappings</h2>" in content
        assert "Total files: 5" in content
        assert "Processed files: 3" in content
        assert "Vacation/Beach" in content
        assert "2/8/2025 3:15pm" in content
        assert "The White House" in content

    def test_unsupported_format(self, sample_report):
        """Test exporting a report with an unsupported format."""
        service = ReportExportService()
        
        with pytest.raises(ValueError):
            service.export_report(sample_report, "UNSUPPORTED", "/output/report.txt")