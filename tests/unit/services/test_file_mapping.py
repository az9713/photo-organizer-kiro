"""
Unit tests for the hierarchical file mapping functionality.
"""

import os
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from photo_organizer.models.image import GeoLocation, Image, ImageMetadata
from photo_organizer.services.reporting import FileMapping, FolderNode
from photo_organizer.services.file_mapping import FileMappingService


@pytest.fixture
def mock_image_file(tmp_path):
    """Create a mock image file for testing."""
    image_path = tmp_path / "test_image.jpg"
    image_path.write_text("")
    return image_path


@pytest.fixture
def sample_images(mock_image_file):
    """Create sample images with metadata."""
    images = []
    
    # Image 1
    image1 = MagicMock(spec=Image)
    image1.path = Path("/input/path/img1.jpg")
    image1.filename = "img1.jpg"
    image1.new_path = Path("/output/path/Vacation/Beach/beach1.jpg")
    image1.metadata = ImageMetadata(
        timestamp=datetime(2025, 2, 8, 15, 15),
        geolocation=GeoLocation(
            latitude=38.8977,
            longitude=-77.0365,
            street="1600 Pennsylvania Ave NW",
            city="Washington",
            postal_code="20500",
            country="United States",
            institution_name="The White House",
        ),
    )
    images.append(image1)
    
    # Image 2
    image2 = MagicMock(spec=Image)
    image2.path = Path("/input/path/img2.jpg")
    image2.filename = "img2.jpg"
    image2.new_path = Path("/output/path/Vacation/Beach/beach2.jpg")
    image2.metadata = ImageMetadata(
        timestamp=datetime(2025, 2, 9, 10, 30),
        geolocation=GeoLocation(
            latitude=38.8977,
            longitude=-77.0365,
            street="10th St. & Constitution Ave. NW",
            city="Washington",
            postal_code="20560",
            country="United States",
            institution_name="Smithsonian National Museum of Natural History",
        ),
    )
    images.append(image2)
    
    # Image 3
    image3 = MagicMock(spec=Image)
    image3.path = Path("/input/path/img3.jpg")
    image3.filename = "img3.jpg"
    image3.new_path = Path("/output/path/Vacation/Mountains/mountain1.jpg")
    image3.metadata = ImageMetadata(
        timestamp=datetime(2025, 2, 10, 8, 45),
        geolocation=GeoLocation(
            latitude=36.1069,
            longitude=-112.1129,
            country="United States",
            institution_name="Grand Canyon National Park",
        ),
    )
    images.append(image3)
    
    return images


class TestFileMappingService:
    """Tests for the FileMappingService class."""

    def test_init(self):
        """Test initializing a FileMappingService object."""
        service = FileMappingService()
        assert service is not None

    def test_create_folder_structure(self, sample_images):
        """Test creating a folder structure from images."""
        service = FileMappingService()
        
        folder_structure = service.create_folder_structure(sample_images, "/output/path")
        
        assert folder_structure.name == "root"
        assert folder_structure.path == "/output/path"
        assert len(folder_structure.subfolders) == 1
        
        vacation = folder_structure.subfolders[0]
        assert vacation.name == "Vacation"
        assert vacation.path == "/output/path/Vacation"
        assert len(vacation.subfolders) == 2
        
        # Check Beach folder
        beach = next(f for f in vacation.subfolders if f.name == "Beach")
        assert beach.path == "/output/path/Vacation/Beach"
        assert len(beach.files) == 2
        assert "beach1.jpg" in beach.files
        assert "beach2.jpg" in beach.files
        
        # Check Mountains folder
        mountains = next(f for f in vacation.subfolders if f.name == "Mountains")
        assert mountains.path == "/output/path/Vacation/Mountains"
        assert len(mountains.files) == 1
        assert "mountain1.jpg" in mountains.files

    def test_create_file_mappings(self, sample_images):
        """Test creating file mappings from images."""
        service = FileMappingService()
        
        file_mappings = service.create_file_mappings(sample_images)
        
        assert len(file_mappings) == 3
        
        # Check first mapping
        mapping1 = next(m for m in file_mappings if m.original_path == "/input/path/img1.jpg")
        assert mapping1.new_path == "/output/path/Vacation/Beach/beach1.jpg"
        assert mapping1.category == "Vacation/Beach"
        assert mapping1.timestamp == datetime(2025, 2, 8, 15, 15)
        assert mapping1.geolocation == "The White House, 1600 Pennsylvania Ave NW, Washington, 20500"
        
        # Check second mapping
        mapping2 = next(m for m in file_mappings if m.original_path == "/input/path/img2.jpg")
        assert mapping2.new_path == "/output/path/Vacation/Beach/beach2.jpg"
        assert mapping2.category == "Vacation/Beach"
        assert mapping2.timestamp == datetime(2025, 2, 9, 10, 30)
        assert mapping2.geolocation == "Smithsonian National Museum of Natural History, 10th St. & Constitution Ave. NW, Washington, 20560"
        
        # Check third mapping
        mapping3 = next(m for m in file_mappings if m.original_path == "/input/path/img3.jpg")
        assert mapping3.new_path == "/output/path/Vacation/Mountains/mountain1.jpg"
        assert mapping3.category == "Vacation/Mountains"
        assert mapping3.timestamp == datetime(2025, 2, 10, 8, 45)
        assert mapping3.geolocation == "Grand Canyon National Park"

    def test_get_category_from_path(self):
        """Test getting a category from a path."""
        service = FileMappingService()
        
        path = Path("/output/path/Vacation/Beach/beach1.jpg")
        category = service._get_category_from_path(path, "/output/path")
        
        assert category == "Vacation/Beach"

    def test_get_formatted_geolocation(self):
        """Test getting a formatted geolocation."""
        service = FileMappingService()
        
        # Test with all fields
        geolocation1 = GeoLocation(
            latitude=38.8977,
            longitude=-77.0365,
            street="1600 Pennsylvania Ave NW",
            city="Washington",
            postal_code="20500",
            country="United States",
            institution_name="The White House",
        )
        formatted1 = service._get_formatted_geolocation(geolocation1)
        assert formatted1 == "The White House, 1600 Pennsylvania Ave NW, Washington, 20500"
        
        # Test with non-US country
        geolocation2 = GeoLocation(
            latitude=48.8584,
            longitude=2.2945,
            street="Champ de Mars, 5 Avenue Anatole France",
            city="Paris",
            postal_code="75007",
            country="France",
            institution_name="Eiffel Tower",
        )
        formatted2 = service._get_formatted_geolocation(geolocation2)
        assert formatted2 == "Eiffel Tower, Champ de Mars, 5 Avenue Anatole France, Paris, 75007, France"
        
        # Test with minimal fields
        geolocation3 = GeoLocation(
            latitude=36.1069,
            longitude=-112.1129,
            country="United States",
            institution_name="Grand Canyon National Park",
        )
        formatted3 = service._get_formatted_geolocation(geolocation3)
        assert formatted3 == "Grand Canyon National Park"