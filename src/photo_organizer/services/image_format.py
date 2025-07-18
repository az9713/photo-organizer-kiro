"""
Image format detection and validation service.
"""

from __future__ import annotations

import imghdr
import os
from pathlib import Path
from typing import List, Optional, Set

from photo_organizer.models.image import ImageFormat


class ImageFormatError(Exception):
    """Exception raised for image format errors."""
    pass


class ImageFormatService:
    """
    Service for detecting and validating image formats.
    """
    
    # Mapping of imghdr format names to our ImageFormat enum
    _FORMAT_MAP = {
        "jpeg": ImageFormat.JPEG,
        "png": ImageFormat.PNG,
        "gif": ImageFormat.GIF,
        "tiff": ImageFormat.TIFF,
        "bmp": ImageFormat.BMP,
        "webp": ImageFormat.WEBP,
    }
    
    # File extensions for each format
    _EXTENSIONS = {
        ImageFormat.JPEG: {".jpg", ".jpeg", ".jpe", ".jif", ".jfif"},
        ImageFormat.PNG: {".png"},
        ImageFormat.GIF: {".gif"},
        ImageFormat.TIFF: {".tiff", ".tif"},
        ImageFormat.BMP: {".bmp", ".dib"},
        ImageFormat.WEBP: {".webp"},
    }
    
    def __init__(self) -> None:
        """Initialize the ImageFormatService."""
        # Register additional test for WebP format
        imghdr.tests.append(self._test_webp)
    
    def detect_format(self, path: Path) -> Optional[ImageFormat]:
        """
        Detect the format of an image file.
        
        Args:
            path: The path to the image file
            
        Returns:
            The detected ImageFormat, or None if the format is not supported
        """
        try:
            # First try to detect by content
            format_name = imghdr.what(path)
            if format_name:
                return self._FORMAT_MAP.get(format_name, ImageFormat.UNKNOWN)
            
            # If that fails, try to detect by extension
            suffix = path.suffix.lower()
            for format_type, extensions in self._EXTENSIONS.items():
                if suffix in extensions:
                    return format_type
            
            return ImageFormat.UNKNOWN
        
        except (IOError, OSError):
            return None
    
    def is_supported_format(self, path: Path) -> bool:
        """
        Check if a file is a supported image format.
        
        Args:
            path: The path to the file
            
        Returns:
            True if the file is a supported image format, False otherwise
        """
        format_type = self.detect_format(path)
        return format_type is not None and format_type != ImageFormat.UNKNOWN
    
    def get_supported_extensions(self) -> Set[str]:
        """
        Get all supported file extensions.
        
        Returns:
            A set of all supported file extensions
        """
        extensions = set()
        for ext_set in self._EXTENSIONS.values():
            extensions.update(ext_set)
        return extensions
    
    def filter_image_files(self, paths: List[Path]) -> List[Path]:
        """
        Filter a list of paths to include only supported image files.
        
        Args:
            paths: A list of file paths
            
        Returns:
            A list of paths to supported image files
        """
        return [path for path in paths if self.is_supported_format(path)]
    
    def validate_image(self, path: Path) -> None:
        """
        Validate that a file is a supported image format.
        
        Args:
            path: The path to the file
            
        Raises:
            ImageFormatError: If the file is not a supported image format
        """
        if not path.exists():
            raise ImageFormatError(f"File does not exist: {path}")
        
        if not path.is_file():
            raise ImageFormatError(f"Path is not a file: {path}")
        
        format_type = self.detect_format(path)
        if format_type is None:
            raise ImageFormatError(f"Failed to detect format of file: {path}")
        
        if format_type == ImageFormat.UNKNOWN:
            raise ImageFormatError(f"Unsupported image format: {path}")
    
    @staticmethod
    def _test_webp(h, f) -> Optional[str]:
        """
        Test if a file is in WebP format.
        
        Args:
            h: The first 32 bytes of the file
            f: The file object
            
        Returns:
            "webp" if the file is in WebP format, None otherwise
        """
        if h.startswith(b"RIFF") and h[8:12] == b"WEBP":
            return "webp"
        return None