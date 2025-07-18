"""
Test dataset for the Photo Organizer application.
"""

import os
import shutil
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import pytest


class TestDataset:
    """Test dataset for the Photo Organizer application."""
    
    @staticmethod
    def create_test_dataset(base_dir: Path) -> Dict[str, List[Path]]:
        """
        Create a test dataset with various image types.
        
        Args:
            base_dir: Base directory to create the dataset in
            
        Returns:
            Dictionary mapping category names to lists of image paths
        """
        # Create directories
        vacation_dir = base_dir / "vacation"
        vacation_dir.mkdir(exist_ok=True)
        
        family_dir = base_dir / "family"
        family_dir.mkdir(exist_ok=True)
        
        nature_dir = base_dir / "nature"
        nature_dir.mkdir(exist_ok=True)
        
        # Create images
        dataset = {
            "vacation": [
                TestDataset._create_test_image(vacation_dir / "beach1.jpg", "beach"),
                TestDataset._create_test_image(vacation_dir / "beach2.jpg", "beach"),
                TestDataset._create_test_image(vacation_dir / "mountain1.jpg", "mountain"),
                TestDataset._create_test_image(vacation_dir / "mountain2.jpg", "mountain"),
                TestDataset._create_test_image(vacation_dir / "city1.jpg", "city"),
            ],
            "family": [
                TestDataset._create_test_image(family_dir / "portrait1.jpg", "portrait"),
                TestDataset._create_test_image(family_dir / "portrait2.jpg", "portrait"),
                TestDataset._create_test_image(family_dir / "group1.jpg", "group"),
                TestDataset._create_test_image(family_dir / "group2.jpg", "group"),
            ],
            "nature": [
                TestDataset._create_test_image(nature_dir / "forest1.jpg", "forest"),
                TestDataset._create_test_image(nature_dir / "forest2.jpg", "forest"),
                TestDataset._create_test_image(nature_dir / "river1.jpg", "river"),
                TestDataset._create_test_image(nature_dir / "river2.jpg", "river"),
            ],
            "misc": [
                TestDataset._create_test_image(base_dir / "random1.jpg", "random"),
                TestDataset._create_test_image(base_dir / "random2.jpg", "random"),
            ],
        }
        
        # Create different image formats
        formats = [
            ("png", "PNG image"),
            ("gif", "GIF image"),
            ("bmp", "BMP image"),
            ("tiff", "TIFF image"),
            ("webp", "WebP image"),
        ]
        
        dataset["formats"] = []
        
        for ext, content in formats:
            path = base_dir / f"image.{ext}"
            dataset["formats"].append(TestDataset._create_test_image(path, content))
        
        # Create a corrupted image
        corrupted_path = base_dir / "corrupted.jpg"
        with open(corrupted_path, "w") as f:
            f.write("This is not a valid image file")
        
        dataset["corrupted"] = [corrupted_path]
        
        return dataset
    
    @staticmethod
    def _create_test_image(path: Path, content: str) -> Path:
        """
        Create a test image file.
        
        Args:
            path: Path to create the image at
            content: Content to write to the image
            
        Returns:
            Path to the created image
        """
        # In a real test, we would create actual image files
        # For this test, we'll just create text files with image extensions
        with open(path, "w") as f:
            f.write(f"Test image: {content}")
        
        return path


@pytest.fixture
def test_dataset() -> Tuple[Path, Dict[str, List[Path]]]:
    """Create a temporary test dataset."""
    # Create a temporary directory
    temp_dir = Path(tempfile.mkdtemp())
    
    try:
        # Create test dataset
        dataset = TestDataset.create_test_dataset(temp_dir)
        
        yield temp_dir, dataset
        
    finally:
        # Clean up
        shutil.rmtree(temp_dir)