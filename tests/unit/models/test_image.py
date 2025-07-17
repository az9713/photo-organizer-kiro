"""
Unit tests for the Image model.
"""

import os
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from photo_organizer.models.image import GeoLocation, Image, ImageFormat, ImageMetadata


class TestImageFormat:
    """Tests for the ImageFormat enum."""

    def test_from_extension(self) -> None:
        """Test getting image format from file extension."""
        assert ImageFormat.from_extension("jpg") == ImageFormat.JPEG
        assert ImageFormat.from_extension(".jpg") == ImageFormat.JPEG
        assert ImageFormat.from_extension("JPG") == ImageFormat.JPEG
        assert ImageFormat.from_extension("jpeg") == ImageFormat.JPEG
        assert ImageFormat.from_extension("png") == ImageFormat.PNG
        assert ImageFormat.from_extension("gif") == ImageFormat.GIF
        assert ImageFormat.from_extension("tiff") == ImageFormat.TIFF
        assert ImageFormat.from_extension("tif") == ImageFormat.TIFF
        assert ImageFormat.from_extension("bmp") == ImageFormat.BMP
        assert ImageFormat.from_extension("webp") == ImageFormat.WEBP
        assert ImageFormat.from_extension("unknown") == ImageFormat.UNKNOWN


class TestGeoLocation:
    """Tests for the GeoLocation class."""

    def test_formatted_address_with_all_fields(self) -> None:
        """Test formatted address with all fields."""
        location = GeoLocation(
            latitude=38.8977,
            longitude=-77.0365,
            street="1600 Pennsylvania Ave NW",
            city="Washington",
            postal_code="20500",
            country="United States",
            institution_name="The White House"
        )
        expected = "The White House, 1600 Pennsylvania Ave NW, Washington, 20500"
        assert location.formatted_address == expected

    def test_formatted_address_without_institution(self) -> None:
        """Test formatted address without institution name."""
        location = GeoLocation(
            latitude=38.8977,
            longitude=-77.0365,
            street="1600 Pennsylvania Ave NW",
            city="Washington",
            postal_code="20500",
            country="United States"
        )
        expected = "1600 Pennsylvania Ave NW, Washington, 20500"
        assert location.formatted_address == expected

    def test_formatted_address_with_non_us_country(self) -> None:
        """Test formatted address with non-US country."""
        location = GeoLocation(
            latitude=48.8584,
            longitude=2.2945,
            street="Champ de Mars, 5 Avenue Anatole France",
            city="Paris",
            postal_code="75007",
            country="France",
            institution_name="Eiffel Tower"
        )
        expected = "Eiffel Tower, Champ de Mars, 5 Avenue Anatole France, Paris, 75007, France"
        assert location.formatted_address == expected


class TestImageMetadata:
    """Tests for the ImageMetadata class."""

    def test_formatted_timestamp(self) -> None:
        """Test formatted timestamp."""
        metadata = ImageMetadata(timestamp=datetime(2025, 2, 8, 15, 15))
        assert metadata.formatted_timestamp == "2/8/2025 3:15pm"

    def test_formatted_timestamp_none(self) -> None:
        """Test formatted timestamp when timestamp is None."""
        metadata = ImageMetadata()
        assert metadata.formatted_timestamp is None


@pytest.fixture
def mock_image_file(tmp_path) -> Path:
    """Create a mock image file for testing."""
    image_path = tmp_path / "test_image.jpg"
    # Create an empty file
    image_path.write_text("")
    return image_path


class TestImage:
    """Tests for the Image class."""

    def test_init(self, mock_image_file) -> None:
        """Test initializing an Image object."""
        image = Image(mock_image_file)
        assert image.path == mock_image_file
        assert image.metadata is not None
        assert image.content_tags == []
        assert image.objects == []
        assert image.scenes == []
        assert image.faces == []
        assert image.new_path is None

    def test_init_file_not_found(self) -> None:
        """Test initializing an Image with a non-existent file."""
        with pytest.raises(FileNotFoundError):
            Image("non_existent_file.jpg")

    def test_format(self, mock_image_file) -> None:
        """Test getting the image format."""
        image = Image(mock_image_file)
        assert image.format == ImageFormat.JPEG

    @patch("os.path.getsize")
    def test_size(self, mock_getsize, mock_image_file) -> None:
        """Test getting the file size."""
        mock_getsize.return_value = 1024
        image = Image(mock_image_file)
        assert image.size == 1024
        mock_getsize.assert_called_once_with(mock_image_file)

    def test_dimensions(self, mock_image_file) -> None:
        """Test getting and setting dimensions."""
        image = Image(mock_image_file)
        assert image.dimensions is None
        
        # Set dimensions
        image.dimensions = (800, 600)
        assert image.dimensions == (800, 600)

    def test_filename_and_basename(self, mock_image_file) -> None:
        """Test getting filename and basename."""
        image = Image(mock_image_file)
        assert image.filename == "test_image.jpg"
        assert image.basename == "test_image"

    def test_str_and_repr(self, mock_image_file) -> None:
        """Test string representations."""
        image = Image(mock_image_file)
        assert str(image) == f"Image({mock_image_file})"
        
        # For repr, we need to patch the size and dimensions
        image._size = 1024
        image.dimensions = (800, 600)
        expected_repr = f"Image(path='{mock_image_file}', format={ImageFormat.JPEG}, size=1024, dimensions=(800, 600))"
        assert repr(image) == expected_repr