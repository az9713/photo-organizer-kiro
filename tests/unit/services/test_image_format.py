"""
Unit tests for the ImageFormatService.
"""

import os
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from photo_organizer.models.image import ImageFormat
from photo_organizer.services.image_format import ImageFormatError, ImageFormatService


class TestImageFormatService:
    """Tests for the ImageFormatService class."""

    def test_detect_format_by_content(self, tmp_path) -> None:
        """Test detecting image format by content."""
        service = ImageFormatService()
        
        # Mock imghdr.what to return specific formats
        with patch("imghdr.what") as mock_what:
            # Test JPEG
            mock_what.return_value = "jpeg"
            assert service.detect_format(Path("test.jpg")) == ImageFormat.JPEG
            
            # Test PNG
            mock_what.return_value = "png"
            assert service.detect_format(Path("test.png")) == ImageFormat.PNG
            
            # Test GIF
            mock_what.return_value = "gif"
            assert service.detect_format(Path("test.gif")) == ImageFormat.GIF
            
            # Test TIFF
            mock_what.return_value = "tiff"
            assert service.detect_format(Path("test.tiff")) == ImageFormat.TIFF
            
            # Test BMP
            mock_what.return_value = "bmp"
            assert service.detect_format(Path("test.bmp")) == ImageFormat.BMP
            
            # Test WebP
            mock_what.return_value = "webp"
            assert service.detect_format(Path("test.webp")) == ImageFormat.WEBP
            
            # Test unknown format
            mock_what.return_value = "unknown"
            assert service.detect_format(Path("test.xyz")) == ImageFormat.UNKNOWN

    def test_detect_format_by_extension(self, tmp_path) -> None:
        """Test detecting image format by extension when content detection fails."""
        service = ImageFormatService()
        
        # Mock imghdr.what to return None (content detection fails)
        with patch("imghdr.what", return_value=None):
            # Test JPEG extensions
            assert service.detect_format(Path("test.jpg")) == ImageFormat.JPEG
            assert service.detect_format(Path("test.jpeg")) == ImageFormat.JPEG
            assert service.detect_format(Path("test.jpe")) == ImageFormat.JPEG
            assert service.detect_format(Path("test.jif")) == ImageFormat.JPEG
            assert service.detect_format(Path("test.jfif")) == ImageFormat.JPEG
            
            # Test PNG extension
            assert service.detect_format(Path("test.png")) == ImageFormat.PNG
            
            # Test GIF extension
            assert service.detect_format(Path("test.gif")) == ImageFormat.GIF
            
            # Test TIFF extensions
            assert service.detect_format(Path("test.tiff")) == ImageFormat.TIFF
            assert service.detect_format(Path("test.tif")) == ImageFormat.TIFF
            
            # Test BMP extensions
            assert service.detect_format(Path("test.bmp")) == ImageFormat.BMP
            assert service.detect_format(Path("test.dib")) == ImageFormat.BMP
            
            # Test WebP extension
            assert service.detect_format(Path("test.webp")) == ImageFormat.WEBP
            
            # Test unknown extension
            assert service.detect_format(Path("test.xyz")) == ImageFormat.UNKNOWN

    def test_detect_format_error(self) -> None:
        """Test detecting format with an error."""
        service = ImageFormatService()
        
        # Mock imghdr.what to raise an exception
        with patch("imghdr.what", side_effect=IOError("Test error")):
            assert service.detect_format(Path("test.jpg")) is None

    def test_is_supported_format(self) -> None:
        """Test checking if a format is supported."""
        service = ImageFormatService()
        
        # Mock detect_format to return specific formats
        with patch.object(service, "detect_format") as mock_detect:
            # Test supported formats
            mock_detect.return_value = ImageFormat.JPEG
            assert service.is_supported_format(Path("test.jpg")) is True
            
            # Test unknown format
            mock_detect.return_value = ImageFormat.UNKNOWN
            assert service.is_supported_format(Path("test.xyz")) is False
            
            # Test detection failure
            mock_detect.return_value = None
            assert service.is_supported_format(Path("test.jpg")) is False

    def test_get_supported_extensions(self) -> None:
        """Test getting all supported extensions."""
        service = ImageFormatService()
        extensions = service.get_supported_extensions()
        
        # Check that all expected extensions are included
        assert ".jpg" in extensions
        assert ".jpeg" in extensions
        assert ".png" in extensions
        assert ".gif" in extensions
        assert ".tiff" in extensions
        assert ".tif" in extensions
        assert ".bmp" in extensions
        assert ".webp" in extensions
        
        # Check that the total count is correct (there are more extensions than listed above)
        assert len(extensions) >= 10

    def test_filter_image_files(self) -> None:
        """Test filtering a list of paths to include only image files."""
        service = ImageFormatService()
        
        # Create a list of paths
        paths = [
            Path("image1.jpg"),
            Path("image2.png"),
            Path("document.pdf"),
            Path("image3.gif"),
            Path("text.txt")
        ]
        
        # Mock is_supported_format to return True for image files
        def mock_is_supported(path):
            return path.suffix.lower() in [".jpg", ".png", ".gif"]
        
        with patch.object(service, "is_supported_format", side_effect=mock_is_supported):
            filtered = service.filter_image_files(paths)
            
            assert len(filtered) == 3
            assert Path("image1.jpg") in filtered
            assert Path("image2.png") in filtered
            assert Path("image3.gif") in filtered
            assert Path("document.pdf") not in filtered
            assert Path("text.txt") not in filtered

    def test_validate_image(self, tmp_path) -> None:
        """Test validating an image file."""
        service = ImageFormatService()
        
        # Create a test path
        test_path = tmp_path / "test.jpg"
        
        # Mock path.exists and path.is_file to return True
        with patch.object(Path, "exists", return_value=True), \
             patch.object(Path, "is_file", return_value=True), \
             patch.object(service, "detect_format", return_value=ImageFormat.JPEG):
            # This should not raise an exception
            service.validate_image(test_path)

    def test_validate_image_not_exists(self, tmp_path) -> None:
        """Test validating a non-existent image file."""
        service = ImageFormatService()
        
        # Create a test path
        test_path = tmp_path / "nonexistent.jpg"
        
        # Mock path.exists to return False
        with patch.object(Path, "exists", return_value=False):
            with pytest.raises(ImageFormatError) as excinfo:
                service.validate_image(test_path)
            
            assert "does not exist" in str(excinfo.value)

    def test_validate_image_not_a_file(self, tmp_path) -> None:
        """Test validating a path that is not a file."""
        service = ImageFormatService()
        
        # Create a test path
        test_path = tmp_path / "directory"
        
        # Mock path.exists to return True and path.is_file to return False
        with patch.object(Path, "exists", return_value=True), \
             patch.object(Path, "is_file", return_value=False):
            with pytest.raises(ImageFormatError) as excinfo:
                service.validate_image(test_path)
            
            assert "not a file" in str(excinfo.value)

    def test_validate_image_detection_failure(self, tmp_path) -> None:
        """Test validating an image with format detection failure."""
        service = ImageFormatService()
        
        # Create a test path
        test_path = tmp_path / "test.jpg"
        
        # Mock path.exists and path.is_file to return True, but detect_format to return None
        with patch.object(Path, "exists", return_value=True), \
             patch.object(Path, "is_file", return_value=True), \
             patch.object(service, "detect_format", return_value=None):
            with pytest.raises(ImageFormatError) as excinfo:
                service.validate_image(test_path)
            
            assert "Failed to detect format" in str(excinfo.value)

    def test_validate_image_unsupported_format(self, tmp_path) -> None:
        """Test validating an image with an unsupported format."""
        service = ImageFormatService()
        
        # Create a test path
        test_path = tmp_path / "test.xyz"
        
        # Mock path.exists and path.is_file to return True, but detect_format to return UNKNOWN
        with patch.object(Path, "exists", return_value=True), \
             patch.object(Path, "is_file", return_value=True), \
             patch.object(service, "detect_format", return_value=ImageFormat.UNKNOWN):
            with pytest.raises(ImageFormatError) as excinfo:
                service.validate_image(test_path)
            
            assert "Unsupported image format" in str(excinfo.value)

    def test_webp_detection(self) -> None:
        """Test WebP format detection."""
        service = ImageFormatService()
        
        # Create mock WebP header
        webp_header = b"RIFF\x00\x00\x00\x00WEBP\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
        
        # Test the WebP detection function
        assert service._test_webp(webp_header, None) == "webp"
        
        # Test with non-WebP header
        non_webp_header = b"JPEG\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
        assert service._test_webp(non_webp_header, None) is None