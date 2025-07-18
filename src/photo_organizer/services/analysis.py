"""
Image analysis engine for the Photo Organizer application.
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Union

from photo_organizer.models.category import Category
from photo_organizer.models.category_tree import CategoryTree
from photo_organizer.models.image import Image
from photo_organizer.services.metadata_extractor import (
    ExifMetadataExtractor,
    MetadataExtractor,
)
from photo_organizer.services.vision.detection import DetectionService
from photo_organizer.services.vision.similarity import ImageSimilarityService


class AnalysisError(Exception):
    """Exception raised for image analysis errors."""
    pass


class ImageAnalysisEngine(ABC):
    """
    Abstract base class for image analysis engines.
    """
    
    @abstractmethod
    def analyze_image(self, image: Image) -> Image:
        """
        Analyze an image to extract metadata and content information.
        
        Args:
            image: The image to analyze
            
        Returns:
            The analyzed image with updated metadata and content information
        """
        pass
    
    @abstractmethod
    def analyze_images(self, images: List[Image]) -> List[Image]:
        """
        Analyze multiple images to extract metadata and content information.
        
        Args:
            images: The images to analyze
            
        Returns:
            The analyzed images with updated metadata and content information
        """
        pass
    
    @abstractmethod
    def categorize_images(self, images: List[Image]) -> CategoryTree:
        """
        Categorize images based on their content and metadata.
        
        Args:
            images: The images to categorize
            
        Returns:
            A category tree with the categorized images
        """
        pass


class DefaultImageAnalysisEngine(ImageAnalysisEngine):
    """
    Default implementation of the image analysis engine.
    """
    
    def __init__(
        self,
        metadata_extractor: Optional[MetadataExtractor] = None,
        detection_service: Optional[DetectionService] = None,
        similarity_service: Optional[ImageSimilarityService] = None,
        similarity_threshold: float = 0.8,
        min_category_size: int = 3,
        max_category_depth: int = 3
    ) -> None:
        """
        Initialize the DefaultImageAnalysisEngine.
        
        Args:
            metadata_extractor: The metadata extractor to use
            detection_service: The detection service to use
            similarity_service: The similarity service to use
            similarity_threshold: The similarity threshold for image clustering
            min_category_size: The minimum number of images in a category
            max_category_depth: The maximum depth of the category tree
        """
        self.metadata_extractor = metadata_extractor or ExifMetadataExtractor()
        self.detection_service = detection_service or DetectionService()
        self.similarity_service = similarity_service or ImageSimilarityService()
        self.similarity_threshold = similarity_threshold
        self.min_category_size = min_category_size
        self.max_category_depth = max_category_depth
        self.logger = logging.getLogger(__name__)
    
    def analyze_image(self, image: Image) -> Image:
        """
        Analyze an image to extract metadata and content information.
        
        Args:
            image: The image to analyze
            
        Returns:
            The analyzed image with updated metadata and content information
        """
        try:
            # Extract metadata
            self.logger.info(f"Extracting metadata from {image.path}")
            image.metadata = self.metadata_extractor.extract_metadata(image.path)
            
            # Detect objects and scenes
            self.logger.info(f"Detecting objects and scenes in {image.path}")
            objects, scenes = self.detection_service.analyze_image(image.path)
            
            # Update image with detected objects and scenes
            image.objects = [
                {"label": obj.label, "confidence": obj.confidence}
                for obj in objects
            ]
            
            image.scenes = [
                {"label": scene.label, "confidence": scene.confidence}
                for scene in scenes
            ]
            
            # Generate content tags
            image.content_tags = self._generate_tags(objects, scenes)
            
            return image
        
        except Exception as e:
            self.logger.error(f"Failed to analyze image {image.path}: {e}")
            raise AnalysisError(f"Failed to analyze image {image.path}: {e}")
    
    def analyze_images(self, images: List[Image]) -> List[Image]:
        """
        Analyze multiple images to extract metadata and content information.
        
        Args:
            images: The images to analyze
            
        Returns:
            The analyzed images with updated metadata and content information
        """
        analyzed_images = []
        errors = []
        
        for image in images:
            try:
                analyzed_image = self.analyze_image(image)
                analyzed_images.append(analyzed_image)
            except AnalysisError as e:
                self.logger.error(f"Error analyzing image {image.path}: {e}")
                errors.append((image, e))
        
        if errors:
            self.logger.warning(f"Failed to analyze {len(errors)} images")
        
        return analyzed_images
    
    def categorize_images(self, images: List[Image]) -> CategoryTree:
        """
        Categorize images based on their content and metadata.
        
        Args:
            images: The images to categorize
            
        Returns:
            A category tree with the categorized images
        """
        try:
            # Create a new category tree
            category_tree = CategoryTree()
            
            # First, categorize by content tags
            self._categorize_by_content(images, category_tree)
            
            # Then, optimize the category tree
            category_tree.optimize_hierarchy(self.min_category_size)
            
            return category_tree
        
        except Exception as e:
            self.logger.error(f"Failed to categorize images: {e}")
            raise AnalysisError(f"Failed to categorize images: {e}")
    
    def _generate_tags(self, objects, scenes) -> List[str]:
        """
        Generate content tags from detected objects and scenes.
        
        Args:
            objects: The detected objects
            scenes: The detected scenes
            
        Returns:
            A list of content tags
        """
        # Extract labels from objects and scenes
        object_labels = [obj.label.lower() for obj in objects]
        scene_labels = [scene.label.lower() for scene in scenes]
        
        # Combine and deduplicate tags
        tags = list(set(object_labels + scene_labels))
        
        # Sort by confidence (highest first)
        tag_confidence = {}
        for obj in objects:
            tag_confidence[obj.label.lower()] = obj.confidence
        
        for scene in scenes:
            tag_confidence[scene.label.lower()] = scene.confidence
        
        tags.sort(key=lambda tag: tag_confidence.get(tag, 0), reverse=True)
        
        return tags
    
    def _categorize_by_content(self, images: List[Image], category_tree: CategoryTree) -> None:
        """
        Categorize images based on their content tags.
        
        Args:
            images: The images to categorize
            category_tree: The category tree to update
        """
        # Group images by primary content tag
        tag_groups = {}
        for image in images:
            if not image.content_tags:
                continue
            
            primary_tag = image.content_tags[0]
            if primary_tag not in tag_groups:
                tag_groups[primary_tag] = []
            
            tag_groups[primary_tag].append(image)
        
        # Create categories for each tag group
        for tag, group_images in tag_groups.items():
            if len(group_images) < self.min_category_size:
                continue
            
            # Create a category for this tag
            category = Category(name=tag.title(), description=f"Images containing {tag}")
            category_tree.add_category(category)
            
            # Add images to the category
            for image in group_images:
                category_tree.add_image_to_category(image.path.name, category.id)
                
                # Store the category ID in the image for reference
                if not hasattr(image, "categories"):
                    image.categories = []
                
                image.categories.append(category.id)
            
            # If the group is large enough, subcategorize by secondary tags
            if len(group_images) > self.min_category_size * 3:
                self._subcategorize_by_secondary_tags(group_images, category, category_tree)
    
    def _subcategorize_by_secondary_tags(
        self, images: List[Image], parent_category: Category, category_tree: CategoryTree
    ) -> None:
        """
        Subcategorize images based on their secondary content tags.
        
        Args:
            images: The images to subcategorize
            parent_category: The parent category
            category_tree: The category tree to update
        """
        # Group images by secondary content tag
        tag_groups = {}
        for image in images:
            if len(image.content_tags) < 2:
                continue
            
            secondary_tag = image.content_tags[1]
            if secondary_tag not in tag_groups:
                tag_groups[secondary_tag] = []
            
            tag_groups[secondary_tag].append(image)
        
        # Create subcategories for each tag group
        for tag, group_images in tag_groups.items():
            if len(group_images) < self.min_category_size:
                continue
            
            # Create a subcategory for this tag
            subcategory = Category(
                name=f"{parent_category.name} - {tag.title()}",
                description=f"Images containing {parent_category.name.lower()} and {tag}"
            )
            
            # Add the subcategory to the tree
            category_tree.add_category(subcategory)
            
            # Set the parent-child relationship
            parent = category_tree.get_category(parent_category.id)
            if parent:
                parent.add_child(subcategory)
            
            # Add images to the subcategory
            for image in group_images:
                category_tree.add_image_to_category(image.path.name, subcategory.id)
                
                # Store the category ID in the image for reference
                if not hasattr(image, "categories"):
                    image.categories = []
                
                image.categories.append(subcategory.id)


class ImageAnalysisService:
    """
    Service for analyzing and categorizing images.
    """
    
    def __init__(self, engine: Optional[ImageAnalysisEngine] = None) -> None:
        """
        Initialize the ImageAnalysisService.
        
        Args:
            engine: The image analysis engine to use
        """
        self.engine = engine or DefaultImageAnalysisEngine()
        self.logger = logging.getLogger(__name__)
    
    def analyze_image(self, image_path: Path) -> Image:
        """
        Analyze an image to extract metadata and content information.
        
        Args:
            image_path: The path to the image
            
        Returns:
            The analyzed image with metadata and content information
        """
        try:
            # Create an Image object
            image = Image(image_path)
            
            # Analyze the image
            return self.engine.analyze_image(image)
        
        except Exception as e:
            self.logger.error(f"Failed to analyze image {image_path}: {e}")
            raise AnalysisError(f"Failed to analyze image {image_path}: {e}")
    
    def analyze_images(self, image_paths: List[Path]) -> List[Image]:
        """
        Analyze multiple images to extract metadata and content information.
        
        Args:
            image_paths: The paths to the images
            
        Returns:
            The analyzed images with metadata and content information
        """
        # Create Image objects
        images = []
        for path in image_paths:
            try:
                images.append(Image(path))
            except Exception as e:
                self.logger.error(f"Failed to create Image object for {path}: {e}")
        
        # Analyze the images
        return self.engine.analyze_images(images)
    
    def categorize_images(self, image_paths: List[Path]) -> Tuple[List[Image], CategoryTree]:
        """
        Analyze and categorize images.
        
        Args:
            image_paths: The paths to the images
            
        Returns:
            A tuple of (analyzed_images, category_tree)
        """
        # Analyze the images
        analyzed_images = self.analyze_images(image_paths)
        
        # Categorize the images
        category_tree = self.engine.categorize_images(analyzed_images)
        
        return analyzed_images, category_tree