"""
Image model for the Photo Organizer application.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import datetime
from enum import Enum, auto
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union


class ImageFormat(Enum):
    """Supported image formats."""
    JPEG = auto()
    PNG = auto()
    GIF = auto()
    TIFF = auto()
    BMP = auto()
    WEBP = auto()
    UNKNOWN = auto()

    @classmethod
    def from_extension(cls, extension: str) -> ImageFormat:
        """Get the image format from a file extension."""
        extension = extension.lower().lstrip('.')
        format_map = {
            'jpg': cls.JPEG,
            'jpeg': cls.JPEG,
            'png': cls.PNG,
            'gif': cls.GIF,
            'tiff': cls.TIFF,
            'tif': cls.TIFF,
            'bmp': cls.BMP,
            'webp': cls.WEBP,
        }
        return format_map.get(extension, cls.UNKNOWN)


@dataclass
class GeoLocation:
    """Geographic location data."""
    latitude: float
    longitude: float
    street: Optional[str] = None
    city: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None
    institution_name: Optional[str] = None
    
    @property
    def formatted_address(self) -> str:
        """Get a formatted address string."""
        components = []
        
        # Add institution name if available
        if self.institution_name:
            components.append(self.institution_name)
        
        # Add street if available
        if self.street:
            components.append(self.street)
        
        # Add city and postal code if available
        city_postal = []
        if self.city:
            city_postal.append(self.city)
        if self.postal_code:
            city_postal.append(self.postal_code)
        if city_postal:
            components.append(", ".join(city_postal))
        
        # Add country if available and not US
        if self.country and self.country.lower() != "united states":
            components.append(self.country)
        
        return ", ".join(components)


@dataclass
class ImageMetadata:
    """Metadata for an image."""
    timestamp: Optional[datetime] = None
    geolocation: Optional[GeoLocation] = None
    camera_make: Optional[str] = None
    camera_model: Optional[str] = None
    exposure_time: Optional[float] = None
    aperture: Optional[float] = None
    iso: Optional[int] = None
    focal_length: Optional[float] = None
    
    @property
    def formatted_timestamp(self) -> Optional[str]:
        """Get the timestamp formatted as M/D/YYYY h:MMam/pm."""
        if not self.timestamp:
            return None
        
        return self.timestamp.strftime("%-m/%-d/%Y %-I:%M%p").lower()


class Image:
    """
    Represents an image file with its metadata and analysis results.
    """
    
    def __init__(self, path: Union[str, Path]) -> None:
        """
        Initialize an Image object.
        
        Args:
            path: Path to the image file
        """
        self.path = Path(path)
        if not self.path.exists():
            raise FileNotFoundError(f"Image file not found: {path}")
        
        self._format: Optional[ImageFormat] = None
        self._size: Optional[int] = None
        self._dimensions: Optional[Tuple[int, int]] = None
        self.metadata = ImageMetadata()
        self.content_tags: List[str] = []
        self.objects: List[Dict[str, Union[str, float]]] = []
        self.scenes: List[Dict[str, Union[str, float]]] = []
        self.faces: List[Dict[str, Union[str, float, Tuple[int, int, int, int]]]] = []
        self.new_path: Optional[Path] = None
    
    @property
    def format(self) -> ImageFormat:
        """Get the image format."""
        if self._format is None:
            self._format = ImageFormat.from_extension(self.path.suffix)
        return self._format
    
    @property
    def size(self) -> int:
        """Get the file size in bytes."""
        if self._size is None:
            self._size = os.path.getsize(self.path)
        return self._size
    
    @property
    def dimensions(self) -> Optional[Tuple[int, int]]:
        """Get the image dimensions (width, height)."""
        # Note: We're not actually loading the image here to get dimensions
        # This would be implemented using PIL or similar in a real implementation
        return self._dimensions
    
    @dimensions.setter
    def dimensions(self, value: Tuple[int, int]) -> None:
        """Set the image dimensions."""
        self._dimensions = value
    
    @property
    def filename(self) -> str:
        """Get the filename without path."""
        return self.path.name
    
    @property
    def basename(self) -> str:
        """Get the filename without extension."""
        return self.path.stem
    
    def __str__(self) -> str:
        """String representation of the image."""
        return f"Image({self.path})"
    
    def __repr__(self) -> str:
        """Detailed string representation of the image."""
        return (f"Image(path='{self.path}', format={self.format}, "
                f"size={self.size}, dimensions={self.dimensions})")