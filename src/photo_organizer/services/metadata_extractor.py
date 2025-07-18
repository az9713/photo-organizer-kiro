"""
MetadataExtractor service for extracting metadata from images.
"""

from __future__ import annotations

import datetime
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Optional, Tuple, Union

import exifread

from photo_organizer.models.image import GeoLocation, ImageMetadata


class MetadataExtractionError(Exception):
    """Exception raised for metadata extraction errors."""
    pass


class MetadataExtractor(ABC):
    """
    Abstract base class for metadata extraction.
    """
    
    @abstractmethod
    def extract_metadata(self, image_path: Path) -> ImageMetadata:
        """
        Extract metadata from an image file.
        
        Args:
            image_path: The path to the image file
            
        Returns:
            The extracted metadata
        """
        pass
    
    @abstractmethod
    def extract_timestamp(self, image_path: Path) -> Optional[datetime.datetime]:
        """
        Extract the timestamp from an image file.
        
        Args:
            image_path: The path to the image file
            
        Returns:
            The extracted timestamp, or None if not available
        """
        pass
    
    @abstractmethod
    def extract_geolocation(self, image_path: Path) -> Optional[GeoLocation]:
        """
        Extract geolocation data from an image file.
        
        Args:
            image_path: The path to the image file
            
        Returns:
            The extracted geolocation data, or None if not available
        """
        pass
    
    @abstractmethod
    def format_timestamp(self, timestamp: datetime.datetime) -> str:
        """
        Format a timestamp according to the required format.
        
        Args:
            timestamp: The timestamp to format
            
        Returns:
            The formatted timestamp string
        """
        pass


class ExifMetadataExtractor(MetadataExtractor):
    """
    Metadata extractor implementation using exifread.
    """
    
    def extract_metadata(self, image_path: Path) -> ImageMetadata:
        """
        Extract metadata from an image file.
        
        Args:
            image_path: The path to the image file
            
        Returns:
            The extracted metadata
        """
        try:
            metadata = ImageMetadata()
            
            # Extract timestamp
            metadata.timestamp = self.extract_timestamp(image_path)
            
            # Extract geolocation
            metadata.geolocation = self.extract_geolocation(image_path)
            
            # Extract camera info
            camera_info = self._extract_camera_info(image_path)
            if camera_info:
                metadata.camera_make = camera_info.get("make")
                metadata.camera_model = camera_info.get("model")
                metadata.exposure_time = camera_info.get("exposure_time")
                metadata.aperture = camera_info.get("aperture")
                metadata.iso = camera_info.get("iso")
                metadata.focal_length = camera_info.get("focal_length")
            
            return metadata
        
        except Exception as e:
            raise MetadataExtractionError(f"Failed to extract metadata from {image_path}: {e}")
    
    def extract_timestamp(self, image_path: Path) -> Optional[datetime.datetime]:
        """
        Extract the timestamp from an image file.
        
        Args:
            image_path: The path to the image file
            
        Returns:
            The extracted timestamp, or None if not available
        """
        try:
            with open(image_path, "rb") as f:
                tags = exifread.process_file(f, details=False)
            
            # Try different EXIF tags for the timestamp
            date_tags = [
                "EXIF DateTimeOriginal",
                "EXIF DateTimeDigitized",
                "Image DateTime"
            ]
            
            for tag in date_tags:
                if tag in tags:
                    date_str = str(tags[tag])
                    return self._parse_exif_date(date_str)
            
            return None
        
        except Exception as e:
            # Log the error but don't raise an exception
            print(f"Warning: Failed to extract timestamp from {image_path}: {e}")
            return None
    
    def extract_geolocation(self, image_path: Path) -> Optional[GeoLocation]:
        """
        Extract geolocation data from an image file.
        
        Args:
            image_path: The path to the image file
            
        Returns:
            The extracted geolocation data, or None if not available
        """
        try:
            with open(image_path, "rb") as f:
                tags = exifread.process_file(f, details=False)
            
            # Check if GPS info is available
            if "GPS GPSLatitude" not in tags or "GPS GPSLongitude" not in tags:
                return None
            
            # Extract latitude and longitude
            lat = self._convert_to_degrees(tags["GPS GPSLatitude"])
            lon = self._convert_to_degrees(tags["GPS GPSLongitude"])
            
            # Check latitude and longitude reference
            if "GPS GPSLatitudeRef" in tags and str(tags["GPS GPSLatitudeRef"]) == "S":
                lat = -lat
            
            if "GPS GPSLongitudeRef" in tags and str(tags["GPS GPSLongitudeRef"]) == "W":
                lon = -lon
            
            # Create GeoLocation object
            return GeoLocation(
                latitude=lat,
                longitude=lon
            )
        
        except Exception as e:
            # Log the error but don't raise an exception
            print(f"Warning: Failed to extract geolocation from {image_path}: {e}")
            return None
    
    def format_timestamp(self, timestamp: datetime.datetime) -> str:
        """
        Format a timestamp according to the required format.
        
        Args:
            timestamp: The timestamp to format
            
        Returns:
            The formatted timestamp string in the format "M/D/YYYY h:MMam/pm"
        """
        return timestamp.strftime("%-m/%-d/%Y %-I:%M%p").lower()
    
    def _extract_camera_info(self, image_path: Path) -> Optional[Dict[str, Union[str, float, int]]]:
        """
        Extract camera information from an image file.
        
        Args:
            image_path: The path to the image file
            
        Returns:
            A dictionary with camera information, or None if not available
        """
        try:
            with open(image_path, "rb") as f:
                tags = exifread.process_file(f, details=False)
            
            camera_info = {}
            
            # Extract camera make and model
            if "Image Make" in tags:
                camera_info["make"] = str(tags["Image Make"])
            
            if "Image Model" in tags:
                camera_info["model"] = str(tags["Image Model"])
            
            # Extract exposure time
            if "EXIF ExposureTime" in tags:
                exposure_str = str(tags["EXIF ExposureTime"])
                if "/" in exposure_str:
                    num, denom = exposure_str.split("/")
                    camera_info["exposure_time"] = float(num) / float(denom)
                else:
                    camera_info["exposure_time"] = float(exposure_str)
            
            # Extract aperture
            if "EXIF FNumber" in tags:
                aperture_str = str(tags["EXIF FNumber"])
                if "/" in aperture_str:
                    num, denom = aperture_str.split("/")
                    camera_info["aperture"] = float(num) / float(denom)
                else:
                    camera_info["aperture"] = float(aperture_str)
            
            # Extract ISO
            if "EXIF ISOSpeedRatings" in tags:
                iso_str = str(tags["EXIF ISOSpeedRatings"])
                camera_info["iso"] = int(iso_str)
            
            # Extract focal length
            if "EXIF FocalLength" in tags:
                focal_length_str = str(tags["EXIF FocalLength"])
                if "/" in focal_length_str:
                    num, denom = focal_length_str.split("/")
                    camera_info["focal_length"] = float(num) / float(denom)
                else:
                    camera_info["focal_length"] = float(focal_length_str)
            
            return camera_info if camera_info else None
        
        except Exception as e:
            # Log the error but don't raise an exception
            print(f"Warning: Failed to extract camera info from {image_path}: {e}")
            return None
    
    def _parse_exif_date(self, date_str: str) -> datetime.datetime:
        """
        Parse an EXIF date string into a datetime object.
        
        Args:
            date_str: The EXIF date string in the format "YYYY:MM:DD HH:MM:SS"
            
        Returns:
            A datetime object
        """
        # EXIF dates are in the format "YYYY:MM:DD HH:MM:SS"
        date_parts = date_str.split(" ")
        if len(date_parts) != 2:
            raise ValueError(f"Invalid EXIF date format: {date_str}")
        
        date_part = date_parts[0].replace(":", "-")
        time_part = date_parts[1]
        
        # Parse the date and time
        return datetime.datetime.fromisoformat(f"{date_part}T{time_part}")
    
    def _convert_to_degrees(self, value) -> float:
        """
        Convert GPS coordinates from the EXIF format to decimal degrees.
        
        Args:
            value: The EXIF GPS coordinate value
            
        Returns:
            The coordinate in decimal degrees
        """
        # GPS coordinates in EXIF are stored as a tuple of three rational values
        # representing degrees, minutes, and seconds
        d = str(value).replace("[", "").replace("]", "").split(",")
        
        # Parse degrees, minutes, and seconds
        degrees = self._parse_rational(d[0])
        minutes = self._parse_rational(d[1])
        seconds = self._parse_rational(d[2])
        
        # Convert to decimal degrees
        return degrees + (minutes / 60.0) + (seconds / 3600.0)
    
    def _parse_rational(self, rational_str: str) -> float:
        """
        Parse a rational number string into a float.
        
        Args:
            rational_str: The rational number string in the format "X/Y"
            
        Returns:
            The parsed float value
        """
        rational_str = rational_str.strip()
        if "/" in rational_str:
            num, denom = rational_str.split("/")
            return float(num) / float(denom)
        else:
            return float(rational_str)