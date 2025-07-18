"""
Unit tests for the image analysis engine.
"""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from photo_organizer.models.category import Category
from photo_organizer.models.category_tree import CategoryTree
from photo_organizer.models.image import Image, ImageMetadata
from photo_organizer.services.analysis import (
    AnalysisError,
    DefaultImageAnalysisEngine,
    ImageAnalysisService,
)
from photo_organizer.services.metadata_extractor import MetadataExtractor
from photo_organizer.services.vision.detection import DetectionService
from photo_organizer.services.vision.similarity import ImageSimilarityService


class TestDefaultImageAnalysisEngine:
    """Tests for the DefaultImageAnalysisEngine class."""

    def test_init(self) -> None:
        """Test initializing the engine."""
        # Test with default parameters
        engine = DefaultImageAnalysisEngine()
        assert isinstance(engine.metadata_extractor, MetadataExtractor)
        assert isinstance(engine.detection_service, DetectionService)
        assert isinstance(engine.similarity_service, ImageSimilarityService)
        assert engine.similarity_threshold == 0.8
        assert engine.min_category_size == 3
        assert engine.max_category_depth == 3
        
        # Test with custom parameters
        metadata_extractor = MagicMock(spec=MetadataExtractor)
        detection_service = MagicMock(spec=DetectionService)
        similarity_service = MagicMock(spec=ImageSimilarityService)
        
        engine = DefaultImageAnalysisEngine(
            metadata_extractor=metadata_extractor,
            detection_service=detection_service,
            similarity_service=similarity_service,
            similarity_threshold=0.9,
            min_category_size=5,
            max_category_depth=2
        )
        
        assert engine.metadata_extractor == metadata_extractor
        assert engine.detection_service == detection_service
        assert engine.similarity_service == similarity_service
        assert engine.similarity_threshold == 0.9
        assert engine.min_category_size == 5
        assert engine.max_category_depth == 2

    def test_analyze_image(self, tmp_path) -> None:
        """Test analyzing an image."""
        # Create mock services
        metadata_extractor = MagicMock(spec=MetadataExtractor)
        detection_service = MagicMock(spec=DetectionService)
        
        # Mock the extract_metadata method
        metadata = ImageMetadata()
        metadata_extractor.extract_metadata.return_value = metadata
        
        # Mock the analyze_image method
        objects = [MagicMock(label="cat", confidence=0.9), MagicMock(label="dog", confidence=0.8)]
        scenes = [MagicMock(label="indoor", confidence=0.7)]
        detection_service.analyze_image.return_value = (objects, scenes)
        
        # Create the engine
        engine = DefaultImageAnalysisEngine(
            metadata_extractor=metadata_extractor,
            detection_service=detection_service
        )
        
        # Create a test image
        image_path = tmp_path / "test.jpg"
        image_path.touch()
        image = Image(image_path)
        
        # Analyze the image
        analyzed_image = engine.analyze_image(image)
        
        # Check that the services were used
        metadata_extractor.extract_metadata.assert_called_once_with(image_path)
        detection_service.analyze_image.assert_called_once_with(image_path)
        
        # Check the analyzed image
        assert analyzed_image.metadata == metadata
        assert len(analyzed_image.objects) == 2
        assert analyzed_image.objects[0]["label"] == "cat"
        assert analyzed_image.objects[0]["confidence"] == 0.9
        assert analyzed_image.objects[1]["label"] == "dog"
        assert analyzed_image.objects[1]["confidence"] == 0.8
        assert len(analyzed_image.scenes) == 1
        assert analyzed_image.scenes[0]["label"] == "indoor"
        assert analyzed_image.scenes[0]["confidence"] == 0.7
        assert len(analyzed_image.content_tags) == 3
        assert "cat" in analyzed_image.content_tags
        assert "dog" in analyzed_image.content_tags
        assert "indoor" in analyzed_image.content_tags

    def test_analyze_image_error(self, tmp_path) -> None:
        """Test analyzing an image with an error."""
        # Create mock services
        metadata_extractor = MagicMock(spec=MetadataExtractor)
        
        # Mock the extract_metadata method to raise an exception
        metadata_extractor.extract_metadata.side_effect = Exception("Test error")
        
        # Create the engine
        engine = DefaultImageAnalysisEngine(metadata_extractor=metadata_extractor)
        
        # Create a test image
        image_path = tmp_path / "test.jpg"
        image_path.touch()
        image = Image(image_path)
        
        # Check that the error is handled
        with pytest.raises(AnalysisError) as excinfo:
            engine.analyze_image(image)
        
        assert "Failed to analyze image" in str(excinfo.value)

    def test_analyze_images(self, tmp_path) -> None:
        """Test analyzing multiple images."""
        # Create mock services
        metadata_extractor = MagicMock(spec=MetadataExtractor)
        detection_service = MagicMock(spec=DetectionService)
        
        # Mock the extract_metadata method
        metadata = ImageMetadata()
        metadata_extractor.extract_metadata.return_value = metadata
        
        # Mock the analyze_image method
        objects = [MagicMock(label="cat", confidence=0.9)]
        scenes = [MagicMock(label="indoor", confidence=0.7)]
        detection_service.analyze_image.return_value = (objects, scenes)
        
        # Create the engine
        engine = DefaultImageAnalysisEngine(
            metadata_extractor=metadata_extractor,
            detection_service=detection_service
        )
        
        # Create test images
        image_path1 = tmp_path / "test1.jpg"
        image_path1.touch()
        image1 = Image(image_path1)
        
        image_path2 = tmp_path / "test2.jpg"
        image_path2.touch()
        image2 = Image(image_path2)
        
        # Analyze the images
        analyzed_images = engine.analyze_images([image1, image2])
        
        # Check that the services were used
        assert metadata_extractor.extract_metadata.call_count == 2
        assert detection_service.analyze_image.call_count == 2
        
        # Check the analyzed images
        assert len(analyzed_images) == 2
        assert analyzed_images[0].metadata == metadata
        assert analyzed_images[1].metadata == metadata
        assert len(analyzed_images[0].content_tags) == 2
        assert len(analyzed_images[1].content_tags) == 2

    def test_analyze_images_with_errors(self, tmp_path) -> None:
        """Test analyzing multiple images with some errors."""
        # Create mock services
        metadata_extractor = MagicMock(spec=MetadataExtractor)
        detection_service = MagicMock(spec=DetectionService)
        
        # Mock the extract_metadata method to succeed for the first image and fail for the second
        metadata = ImageMetadata()
        metadata_extractor.extract_metadata.side_effect = [metadata, Exception("Test error")]
        
        # Mock the analyze_image method
        objects = [MagicMock(label="cat", confidence=0.9)]
        scenes = [MagicMock(label="indoor", confidence=0.7)]
        detection_service.analyze_image.return_value = (objects, scenes)
        
        # Create the engine
        engine = DefaultImageAnalysisEngine(
            metadata_extractor=metadata_extractor,
            detection_service=detection_service
        )
        
        # Create test images
        image_path1 = tmp_path / "test1.jpg"
        image_path1.touch()
        image1 = Image(image_path1)
        
        image_path2 = tmp_path / "test2.jpg"
        image_path2.touch()
        image2 = Image(image_path2)
        
        # Analyze the images
        analyzed_images = engine.analyze_images([image1, image2])
        
        # Check that the services were used
        assert metadata_extractor.extract_metadata.call_count == 2
        assert detection_service.analyze_image.call_count == 1  # Only for the first image
        
        # Check the analyzed images
        assert len(analyzed_images) == 1
        assert analyzed_images[0].metadata == metadata
        assert len(analyzed_images[0].content_tags) == 2

    def test_categorize_images(self, tmp_path) -> None:
        """Test categorizing images."""
        # Create the engine
        engine = DefaultImageAnalysisEngine()
        
        # Mock the _categorize_by_content method
        with patch.object(engine, "_categorize_by_content") as mock_categorize:
            # Create test images
            image_path1 = tmp_path / "test1.jpg"
            image_path1.touch()
            image1 = Image(image_path1)
            image1.content_tags = ["cat", "indoor"]
            
            image_path2 = tmp_path / "test2.jpg"
            image_path2.touch()
            image2 = Image(image_path2)
            image2.content_tags = ["dog", "outdoor"]
            
            # Categorize the images
            category_tree = engine.categorize_images([image1, image2])
            
            # Check that the categorization method was called
            mock_categorize.assert_called_once()
            
            # Check the category tree
            assert isinstance(category_tree, CategoryTree)

    def test_categorize_images_error(self, tmp_path) -> None:
        """Test categorizing images with an error."""
        # Create the engine
        engine = DefaultImageAnalysisEngine()
        
        # Mock the _categorize_by_content method to raise an exception
        with patch.object(engine, "_categorize_by_content", side_effect=Exception("Test error")):
            # Create test images
            image_path1 = tmp_path / "test1.jpg"
            image_path1.touch()
            image1 = Image(image_path1)
            
            # Check that the error is handled
            with pytest.raises(AnalysisError) as excinfo:
                engine.categorize_images([image1])
            
            assert "Failed to categorize images" in str(excinfo.value)

    def test_generate_tags(self) -> None:
        """Test generating tags from objects and scenes."""
        # Create the engine
        engine = DefaultImageAnalysisEngine()
        
        # Create mock objects and scenes
        objects = [
            MagicMock(label="Cat", confidence=0.9),
            MagicMock(label="Dog", confidence=0.8)
        ]
        scenes = [
            MagicMock(label="Indoor", confidence=0.7),
            MagicMock(label="Living Room", confidence=0.6)
        ]
        
        # Generate tags
        tags = engine._generate_tags(objects, scenes)
        
        # Check the tags
        assert len(tags) == 4
        assert "cat" in tags
        assert "dog" in tags
        assert "indoor" in tags
        assert "living room" in tags
        
        # Check the order (by confidence)
        assert tags[0] == "cat"
        assert tags[1] == "dog"
        assert tags[2] == "indoor"
        assert tags[3] == "living room"

    def test_categorize_by_content(self, tmp_path) -> None:
        """Test categorizing images by content."""
        # Create the engine with a small min_category_size
        engine = DefaultImageAnalysisEngine(min_category_size=1)
        
        # Create a category tree
        category_tree = CategoryTree()
        
        # Create test images
        image_path1 = tmp_path / "test1.jpg"
        image_path1.touch()
        image1 = Image(image_path1)
        image1.content_tags = ["cat", "indoor"]
        
        image_path2 = tmp_path / "test2.jpg"
        image_path2.touch()
        image2 = Image(image_path2)
        image2.content_tags = ["cat", "outdoor"]
        
        image_path3 = tmp_path / "test3.jpg"
        image_path3.touch()
        image3 = Image(image_path3)
        image3.content_tags = ["dog", "outdoor"]
        
        # Categorize the images
        engine._categorize_by_content([image1, image2, image3], category_tree)
        
        # Check the category tree
        assert len(category_tree.categories) == 2  # "Cat" and "Dog" categories
        
        # Check that the images are assigned to the correct categories
        cat_category = None
        dog_category = None
        
        for category in category_tree.categories.values():
            if category.name == "Cat":
                cat_category = category
            elif category.name == "Dog":
                dog_category = category
        
        assert cat_category is not None
        assert dog_category is not None
        assert len(cat_category.image_ids) == 2
        assert len(dog_category.image_ids) == 1

    def test_subcategorize_by_secondary_tags(self, tmp_path) -> None:
        """Test subcategorizing images by secondary tags."""
        # Create the engine with a small min_category_size
        engine = DefaultImageAnalysisEngine(min_category_size=1)
        
        # Create a category tree
        category_tree = CategoryTree()
        
        # Create a parent category
        parent_category = Category(name="Cat", description="Images containing cats")
        category_tree.add_category(parent_category)
        
        # Create test images
        image_path1 = tmp_path / "test1.jpg"
        image_path1.touch()
        image1 = Image(image_path1)
        image1.content_tags = ["cat", "indoor"]
        
        image_path2 = tmp_path / "test2.jpg"
        image_path2.touch()
        image2 = Image(image_path2)
        image2.content_tags = ["cat", "indoor"]
        
        image_path3 = tmp_path / "test3.jpg"
        image_path3.touch()
        image3 = Image(image_path3)
        image3.content_tags = ["cat", "outdoor"]
        
        # Subcategorize the images
        engine._subcategorize_by_secondary_tags([image1, image2, image3], parent_category, category_tree)
        
        # Check the category tree
        assert len(category_tree.categories) == 3  # Parent + 2 subcategories
        
        # Check that the subcategories are created correctly
        indoor_category = None
        outdoor_category = None
        
        for category in category_tree.categories.values():
            if category.name == "Cat - Indoor":
                indoor_category = category
            elif category.name == "Cat - Outdoor":
                outdoor_category = category
        
        assert indoor_category is not None
        assert outdoor_category is not None
        assert len(indoor_category.image_ids) == 2
        assert len(outdoor_category.image_ids) == 1
        assert indoor_category.parent_id == parent_category.id
        assert outdoor_category.parent_id == parent_category.id


class TestImageAnalysisService:
    """Tests for the ImageAnalysisService class."""

    def test_init(self) -> None:
        """Test initializing the service."""
        # Test with default parameters
        service = ImageAnalysisService()
        assert isinstance(service.engine, DefaultImageAnalysisEngine)
        
        # Test with custom parameters
        engine = MagicMock(spec=DefaultImageAnalysisEngine)
        service = ImageAnalysisService(engine=engine)
        assert service.engine == engine

    def test_analyze_image(self, tmp_path) -> None:
        """Test analyzing an image."""
        # Create a mock engine
        engine = MagicMock(spec=DefaultImageAnalysisEngine)
        
        # Mock the analyze_image method
        analyzed_image = MagicMock(spec=Image)
        engine.analyze_image.return_value = analyzed_image
        
        # Create the service
        service = ImageAnalysisService(engine=engine)
        
        # Create a test image
        image_path = tmp_path / "test.jpg"
        image_path.touch()
        
        # Analyze the image
        result = service.analyze_image(image_path)
        
        # Check that the engine was used
        assert engine.analyze_image.call_count == 1
        
        # Check the result
        assert result == analyzed_image

    def test_analyze_image_error(self, tmp_path) -> None:
        """Test analyzing an image with an error."""
        # Create a mock engine
        engine = MagicMock(spec=DefaultImageAnalysisEngine)
        
        # Mock the analyze_image method to raise an exception
        engine.analyze_image.side_effect = Exception("Test error")
        
        # Create the service
        service = ImageAnalysisService(engine=engine)
        
        # Create a test image
        image_path = tmp_path / "test.jpg"
        image_path.touch()
        
        # Check that the error is handled
        with pytest.raises(AnalysisError) as excinfo:
            service.analyze_image(image_path)
        
        assert "Failed to analyze image" in str(excinfo.value)

    def test_analyze_images(self, tmp_path) -> None:
        """Test analyzing multiple images."""
        # Create a mock engine
        engine = MagicMock(spec=DefaultImageAnalysisEngine)
        
        # Mock the analyze_images method
        analyzed_images = [MagicMock(spec=Image), MagicMock(spec=Image)]
        engine.analyze_images.return_value = analyzed_images
        
        # Create the service
        service = ImageAnalysisService(engine=engine)
        
        # Create test images
        image_path1 = tmp_path / "test1.jpg"
        image_path1.touch()
        image_path2 = tmp_path / "test2.jpg"
        image_path2.touch()
        
        # Analyze the images
        results = service.analyze_images([image_path1, image_path2])
        
        # Check that the engine was used
        assert engine.analyze_images.call_count == 1
        
        # Check the results
        assert results == analyzed_images

    def test_categorize_images(self, tmp_path) -> None:
        """Test categorizing images."""
        # Create a mock engine
        engine = MagicMock(spec=DefaultImageAnalysisEngine)
        
        # Mock the analyze_images method
        analyzed_images = [MagicMock(spec=Image), MagicMock(spec=Image)]
        engine.analyze_images.return_value = analyzed_images
        
        # Mock the categorize_images method
        category_tree = MagicMock(spec=CategoryTree)
        engine.categorize_images.return_value = category_tree
        
        # Create the service
        service = ImageAnalysisService(engine=engine)
        
        # Create test images
        image_path1 = tmp_path / "test1.jpg"
        image_path1.touch()
        image_path2 = tmp_path / "test2.jpg"
        image_path2.touch()
        
        # Categorize the images
        results, tree = service.categorize_images([image_path1, image_path2])
        
        # Check that the engine was used
        assert engine.analyze_images.call_count == 1
        assert engine.categorize_images.call_count == 1
        
        # Check the results
        assert results == analyzed_images
        assert tree == category_tree