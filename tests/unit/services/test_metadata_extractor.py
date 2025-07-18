"""
Unit tests for the MetadataExtractor service.
"""

import datetime
from pathlib import Path
from unittest.mock import MagicMock, mock_open, patch

import pytest

from photo_organizer.models.image import GeoLocation, ImageMetadata
from photo_organizer.services.metadata_extractor import (
    ExifMetadataExtractor,
    MetadataExtractionError,
)


class TestExifMetadataExtractor:
    """Tests for the ExifMetadataExtractor class."""

    def test_extract_metadata(self) -> None:
        """Test extracting metadata from an image file."""
        extractor = ExifMetadataExtractor()
        
        # Mock the extract_timestamp and extract_geolocation methods
        timestamp = datetime.datetime(2025, 2, 8, 15, 15)
        geolocation = GeoLocation(latitude=38.8977, longitude=-77.0365)
        
        with patch.object(extractor, "extract_timestamp", return_value=timestamp), \
             patch.object(extractor, "extract_geolocation", return_value=geolocation), \
             patch.object(extractor, "_extract_camera_info", return_value={
                 "make": "Canon",
                 "model": "EOS R5",
                 "exposure_time": 1/125,
                 "aperture": 2.8,
                 "iso": 100,
                 "focal_length": 50.0
             }):
            metadata = extractor.extract_metadata(Path("test.jpg"))
            
            assert metadata.timestamp == timestamp
            assert metadata.geolocation == geolocation
            assert metadata.camera_make == "Canon"
            assert metadata.camera_model == "EOS R5"
            assert metadata.exposure_time == 1/125
            assert metadata.aperture == 2.8
            assert metadata.iso == 100
            assert metadata.focal_length == 50.0

    def test_extract_metadata_error(self) -> None:
        """Test extracting metadata with an error."""
        extractor = ExifMetadataExtractor()
        
        # Mock extract_timestamp to raise an exception
        with patch.object(extractor, "extract_timestamp", side_effect=Exception("Test error")):
            with pytest.raises(MetadataExtractionError) as excinfo:
                extractor.extract_metadata(Path("test.jpg"))
            
            assert "Failed to extract metadata" in str(excinfo.value)

    def test_extract_timestamp(self) -> None:
        """Test extracting a timestamp from an image file."""
        extractor = ExifMetadataExtractor()
        
        # Mock exifread.process_file to return tags with a timestamp
        mock_tags = {
            "EXIF DateTimeOriginal": "2025:02:08 15:15:00"
        }
        
        with patch("exifread.process_file", return_value=mock_tags), \
             patch("builtins.open", mock_open()):
            timestamp = extractor.extract_timestamp(Path("test.jpg"))
            
            assert timestamp == datetime.datetime(2025, 2, 8, 15, 15)

    def test_extract_timestamp_fallback(self) -> None:
        """Test extracting a timestamp with fallback tags."""
        extractor = ExifMetadataExtractor()
        
        # Mock exifread.process_file to return tags with a timestamp in a different tag
        mock_tags = {
            "Image DateTime": "2025:02:08 15:15:00"
        }
        
        with patch("exifread.process_file", return_value=mock_tags), \
             patch("builtins.open", mock_open()):
            timestamp = extractor.extract_timestamp(Path("test.jpg"))
            
            assert timestamp == datetime.datetime(2025, 2, 8, 15, 15)

    def test_extract_timestamp_no_tags(self) -> None:
        """Test extracting a timestamp with no timestamp tags."""
        extractor = ExifMetadataExtractor()
        
        # Mock exifread.process_file to return empty tags
        with patch("exifread.process_file", return_value={}), \
             patch("builtins.open", mock_open()):
            timestamp = extractor.extract_timestamp(Path("test.jpg"))
            
            assert timestamp is None

    def test_extract_timestamp_error(self) -> None:
        """Test extracting a timestamp with an error."""
        extractor = ExifMetadataExtractor()
        
        # Mock open to raise an exception
        with patch("builtins.open", side_effect=IOError("Test error")), \
             patch("builtins.print"):  # Suppress print output
            timestamp = extractor.extract_timestamp(Path("test.jpg"))
            
            assert timestamp is None

    def test_extract_geolocation(self) -> None:
        """Test extracting geolocation data from an image file."""
        extractor = ExifMetadataExtractor()
        
        # Mock exifread.process_file to return tags with GPS data
        mock_tags = {
            "GPS GPSLatitude": "[38, 53, 51.72]",
            "GPS GPSLatitudeRef": "N",
            "GPS GPSLongitude": "[77, 2, 11.4]",
            "GPS GPSLongitudeRef": "W"
        }
        
        with patch("exifread.process_file", return_value=mock_tags), \
             patch("builtins.open", mock_open()):
            geolocation = extractor.extract_geolocation(Path("test.jpg"))
            
            assert geolocation is not None
            assert abs(geolocation.latitude - 38.8977) < 0.001
            assert abs(geolocation.longitude - (-77.0365)) < 0.001

    def test_extract_geolocation_no_gps(self) -> None:
        """Test extracting geolocation data with no GPS tags."""
        extractor = ExifMetadataExtractor()
        
        # Mock exifread.process_file to return empty tags
        with patch("exifread.process_file", return_value={}), \
             patch("builtins.open", mock_open()):
            geolocation = extractor.extract_geolocation(Path("test.jpg"))
            
            assert geolocation is None

    def test_extract_geolocation_error(self) -> None:
        """Test extracting geolocation data with an error."""
        extractor = ExifMetadataExtractor()
        
        # Mock open to raise an exception
        with patch("builtins.open", side_effect=IOError("Test error")), \
             patch("builtins.print"):  # Suppress print output
            geolocation = extractor.extract_geolocation(Path("test.jpg"))
            
            assert geolocation is None

    def test_format_timestamp(self) -> None:
        """Test formatting a timestamp."""
        extractor = ExifMetadataExtractor()
        
        timestamp = datetime.datetime(2025, 2, 8, 15, 15)
        formatted = extractor.format_timestamp(timestamp)
        
        assert formatted == "2/8/2025 3:15pm"

    def test_parse_exif_date(self) -> None:
        """Test parsing an EXIF date string."""
        extractor = ExifMetadataExtractor()
        
        # Test valid date string
        date_str = "2025:02:08 15:15:00"
        timestamp = extractor._parse_exif_date(date_str)
        
        assert timestamp == datetime.datetime(2025, 2, 8, 15, 15)
        
        # Test invalid date string
        with pytest.raises(ValueError):
            extractor._parse_exif_date("invalid")

    def test_convert_to_degrees(self) -> None:
        """Test converting GPS coordinates to decimal degrees."""
        extractor = ExifMetadataExtractor()
        
        # Test with degrees, minutes, seconds
        value = "[38, 53, 51.72]"
        degrees = extractor._convert_to_degrees(value)
        
        assert abs(degrees - 38.8977) < 0.001
        
        # Test with just degrees
        value = "[38, 0, 0]"
        degrees = extractor._convert_to_degrees(value)
        
        assert degrees == 38.0

    def test_parse_rational(self) -> None:
        """Test parsing a rational number string."""
        extractor = ExifMetadataExtractor()
        
        # Test with fraction
        assert extractor._parse_rational("1/2") == 0.5
        
        # Test with integer
        assert extractor._parse_rational("5") == 5.0
        
        # Test with float
        assert extractor._parse_rational("3.14") == 3.14

    def test_extract_camera_info(self) -> None:
        """Test extracting camera information from an image file."""
        extractor = ExifMetadataExtractor()
        
        # Mock exifread.process_file to return tags with camera info
        mock_tags = {
            "Image Make": "Canon",
            "Image Model": "EOS R5",
            "EXIF ExposureTime": "1/125",
            "EXIF FNumber": "2.8",
            "EXIF ISOSpeedRatings": "100",
            "EXIF FocalLength": "50"
        }
        
        with patch("exifread.process_file", return_value=mock_tags), \
             patch("builtins.open", mock_open()):
            camera_info = extractor._extract_camera_info(Path("test.jpg"))
            
            assert camera_info is not None
            assert camera_info["make"] == "Canon"
            assert camera_info["model"] == "EOS R5"
            assert camera_info["exposure_time"] == 1/125
            assert camera_info["aperture"] == 2.8
            assert camera_info["iso"] == 100
            assert camera_info["focal_length"] == 50.0

    def test_extract_camera_info_no_tags(self) -> None:
        """Test extracting camera information with no camera tags."""
        extractor = ExifMetadataExtractor()
        
        # Mock exifread.process_file to return empty tags
        with patch("exifread.process_file", return_value={}), \
             patch("builtins.open", mock_open()):
            camera_info = extractor._extract_camera_info(Path("test.jpg"))
            
            assert camera_info is None

    def test_extract_camera_info_error(self) -> None:
        """Test extracting camera information with an error."""
        extractor = ExifMetadataExtractor()
        
        # Mock open to raise an exception
        with patch("builtins.open", side_effect=IOError("Test error")), \
             patch("builtins.print"):  # Suppress print output
            camera_info = extractor._extract_camera_info(Path("test.jpg"))
            
            assert camera_info is None