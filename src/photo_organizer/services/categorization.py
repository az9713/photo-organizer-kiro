"""
Categorization algorithms for the Photo Organizer application.
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Union

import numpy as np
from scipy.cluster.hierarchy import fcluster, linkage

from photo_organizer.models.category import Category
from photo_organizer.models.category_tree import CategoryTree
from photo_organizer.models.image import Image
from photo_organizer.services.vision.similarity import ImageSimilarityService


class CategorizationError(Exception):
    """Exception raised for categorization errors."""
    pass


class CategorizationAlgorithm(ABC):
    """
    Abstract base class for categorization algorithms.
    """
    
    @abstractmethod
    def categorize(self, images: List[Image]) -> CategoryTree:
        """
        Categorize images into a hierarchical structure.
        
        Args:
            images: The images to categorize
            
        Returns:
            A category tree with the categorized images
        """
        pass


class ContentBasedCategorization(CategorizationAlgorithm):
    """
    Categorization algorithm based on image content tags.
    """
    
    def __init__(
        self,
        min_category_size: int = 3,
        max_category_depth: int = 3,
        min_tag_frequency: int = 2
    ) -> None:
        """
        Initialize the ContentBasedCategorization algorithm.
        
        Args:
            min_category_size: The minimum number of images in a category
            max_category_depth: The maximum depth of the category tree
            min_tag_frequency: The minimum frequency of a tag to be considered
        """
        self.min_category_size = min_category_size
        self.max_category_depth = max_category_depth
        self.min_tag_frequency = min_tag_frequency
        self.logger = logging.getLogger(__name__)
    
    def categorize(self, images: List[Image]) -> CategoryTree:
        """
        Categorize images based on their content tags.
        
        Args:
            images: The images to categorize
            
        Returns:
            A category tree with the categorized images
        """
        try:
            # Create a new category tree
            category_tree = CategoryTree()
            
            # Count tag frequencies
            tag_counts = self._count_tag_frequencies(images)
            
            # Filter tags by frequency
            frequent_tags = {tag for tag, count in tag_counts.items() if count >= self.min_tag_frequency}
            
            # Group images by primary tag
            tag_groups = self._group_by_primary_tags(images, frequent_tags)
            
            # Create categories for each tag group
            self._create_categories(tag_groups, category_tree)
            
            # Create subcategories based on secondary tags
            self._create_subcategories(tag_groups, category_tree)
            
            # Optimize the category tree
            category_tree.optimize_hierarchy(self.min_category_size)
            
            return category_tree
        
        except Exception as e:
            self.logger.error(f"Failed to categorize images by content: {e}")
            raise CategorizationError(f"Failed to categorize images by content: {e}")
    
    def _count_tag_frequencies(self, images: List[Image]) -> Dict[str, int]:
        """
        Count the frequency of each tag across all images.
        
        Args:
            images: The images to analyze
            
        Returns:
            A dictionary mapping tags to their frequencies
        """
        tag_counts = Counter()
        
        for image in images:
            if hasattr(image, "content_tags") and image.content_tags:
                tag_counts.update(image.content_tags)
        
        return tag_counts
    
    def _group_by_primary_tags(
        self, images: List[Image], frequent_tags: Set[str]
    ) -> Dict[str, List[Image]]:
        """
        Group images by their primary (most relevant) tag.
        
        Args:
            images: The images to group
            frequent_tags: The set of frequent tags to consider
            
        Returns:
            A dictionary mapping tags to lists of images
        """
        tag_groups = defaultdict(list)
        
        for image in images:
            if not hasattr(image, "content_tags") or not image.content_tags:
                continue
            
            # Find the first tag that is frequent
            primary_tag = None
            for tag in image.content_tags:
                if tag in frequent_tags:
                    primary_tag = tag
                    break
            
            # If no frequent tag is found, use the first tag
            if primary_tag is None and image.content_tags:
                primary_tag = image.content_tags[0]
            
            # Add the image to the group
            if primary_tag:
                tag_groups[primary_tag].append(image)
        
        return tag_groups
    
    def _create_categories(
        self, tag_groups: Dict[str, List[Image]], category_tree: CategoryTree
    ) -> None:
        """
        Create categories for each tag group.
        
        Args:
            tag_groups: The tag groups to create categories for
            category_tree: The category tree to update
        """
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
    
    def _create_subcategories(
        self, tag_groups: Dict[str, List[Image]], category_tree: CategoryTree
    ) -> None:
        """
        Create subcategories based on secondary tags.
        
        Args:
            tag_groups: The tag groups to create subcategories for
            category_tree: The category tree to update
        """
        # Process each tag group
        for tag, group_images in tag_groups.items():
            if len(group_images) < self.min_category_size * 2:
                continue
            
            # Find the category for this tag
            parent_category = None
            for category in category_tree.categories.values():
                if category.name.lower() == tag.lower():
                    parent_category = category
                    break
            
            if parent_category is None:
                continue
            
            # Count secondary tag frequencies within this group
            secondary_tag_counts = Counter()
            for image in group_images:
                if hasattr(image, "content_tags") and len(image.content_tags) > 1:
                    # Skip the primary tag
                    secondary_tags = [t for t in image.content_tags if t != tag]
                    secondary_tag_counts.update(secondary_tags)
            
            # Filter secondary tags by frequency
            frequent_secondary_tags = {
                tag for tag, count in secondary_tag_counts.items()
                if count >= self.min_tag_frequency
            }
            
            # Group images by secondary tag
            secondary_groups = defaultdict(list)
            for image in group_images:
                if not hasattr(image, "content_tags") or len(image.content_tags) <= 1:
                    continue
                
                # Find the first secondary tag that is frequent
                secondary_tag = None
                for t in image.content_tags:
                    if t != tag and t in frequent_secondary_tags:
                        secondary_tag = t
                        break
                
                # Add the image to the group
                if secondary_tag:
                    secondary_groups[secondary_tag].append(image)
            
            # Create subcategories for each secondary tag
            for secondary_tag, subgroup_images in secondary_groups.items():
                if len(subgroup_images) < self.min_category_size:
                    continue
                
                # Create a subcategory
                subcategory = Category(
                    name=f"{parent_category.name} - {secondary_tag.title()}",
                    description=f"Images containing {tag} and {secondary_tag}"
                )
                
                # Add the subcategory to the tree
                category_tree.add_category(subcategory)
                
                # Set the parent-child relationship
                parent = category_tree.get_category(parent_category.id)
                if parent:
                    parent.add_child(subcategory)
                
                # Add images to the subcategory
                for image in subgroup_images:
                    category_tree.add_image_to_category(image.path.name, subcategory.id)
                    
                    # Store the category ID in the image for reference
                    if not hasattr(image, "categories"):
                        image.categories = []
                    
                    image.categories.append(subcategory.id)


class HierarchicalClustering(CategorizationAlgorithm):
    """
    Categorization algorithm based on hierarchical clustering of image features.
    """
    
    def __init__(
        self,
        similarity_service: Optional[ImageSimilarityService] = None,
        similarity_threshold: float = 0.8,
        min_cluster_size: int = 3,
        max_clusters: int = 20
    ) -> None:
        """
        Initialize the HierarchicalClustering algorithm.
        
        Args:
            similarity_service: The similarity service to use
            similarity_threshold: The similarity threshold for clustering
            min_cluster_size: The minimum number of images in a cluster
            max_clusters: The maximum number of clusters to create
        """
        self.similarity_service = similarity_service or ImageSimilarityService()
        self.similarity_threshold = similarity_threshold
        self.min_cluster_size = min_cluster_size
        self.max_clusters = max_clusters
        self.logger = logging.getLogger(__name__)
    
    def categorize(self, images: List[Image]) -> CategoryTree:
        """
        Categorize images using hierarchical clustering.
        
        Args:
            images: The images to categorize
            
        Returns:
            A category tree with the categorized images
        """
        try:
            # Create a new category tree
            category_tree = CategoryTree()
            
            # Extract features from all images
            self.logger.info("Extracting features from images")
            features_map = self._extract_features(images)
            
            # Compute the distance matrix
            self.logger.info("Computing distance matrix")
            distance_matrix = self._compute_distance_matrix(features_map)
            
            # Perform hierarchical clustering
            self.logger.info("Performing hierarchical clustering")
            clusters = self._cluster_images(distance_matrix, images)
            
            # Create categories for each cluster
            self.logger.info("Creating categories")
            self._create_categories(clusters, category_tree)
            
            return category_tree
        
        except Exception as e:
            self.logger.error(f"Failed to categorize images by clustering: {e}")
            raise CategorizationError(f"Failed to categorize images by clustering: {e}")
    
    def _extract_features(self, images: List[Image]) -> Dict[str, np.ndarray]:
        """
        Extract features from all images.
        
        Args:
            images: The images to extract features from
            
        Returns:
            A dictionary mapping image IDs to feature vectors
        """
        features_map = {}
        errors = []
        
        for image in images:
            try:
                # Use the image path as the ID
                image_id = str(image.path)
                
                # Extract features
                features = self.similarity_service.feature_extractor.extract_features(image.path)
                
                # Store the features
                features_map[image_id] = features
            
            except Exception as e:
                self.logger.error(f"Failed to extract features from {image.path}: {e}")
                errors.append((image, e))
        
        if errors:
            self.logger.warning(f"Failed to extract features from {len(errors)} images")
        
        return features_map
    
    def _compute_distance_matrix(self, features_map: Dict[str, np.ndarray]) -> np.ndarray:
        """
        Compute the distance matrix between all images.
        
        Args:
            features_map: A dictionary mapping image IDs to feature vectors
            
        Returns:
            A distance matrix
        """
        # Get the image IDs and features
        image_ids = list(features_map.keys())
        features = np.array([features_map[image_id] for image_id in image_ids])
        
        # Compute the distance matrix
        n = len(features)
        distance_matrix = np.zeros((n, n))
        
        for i in range(n):
            for j in range(i + 1, n):
                # Compute the cosine distance (1 - cosine similarity)
                similarity = np.dot(features[i], features[j])
                distance = 1 - similarity
                
                # Ensure the distance is between 0 and 1
                distance = max(0, min(1, distance))
                
                # Store the distance
                distance_matrix[i, j] = distance
                distance_matrix[j, i] = distance
        
        return distance_matrix
    
    def _cluster_images(
        self, distance_matrix: np.ndarray, images: List[Image]
    ) -> List[List[Image]]:
        """
        Cluster images using hierarchical clustering.
        
        Args:
            distance_matrix: The distance matrix between images
            images: The images to cluster
            
        Returns:
            A list of clusters, where each cluster is a list of images
        """
        # Perform hierarchical clustering
        Z = linkage(distance_matrix, method="average")
        
        # Determine the optimal number of clusters
        max_d = 1 - self.similarity_threshold
        clusters = fcluster(Z, max_d, criterion="distance")
        
        # Group images by cluster
        cluster_groups = defaultdict(list)
        for i, cluster_id in enumerate(clusters):
            cluster_groups[cluster_id].append(images[i])
        
        # Filter clusters by size
        filtered_clusters = [
            cluster for cluster in cluster_groups.values()
            if len(cluster) >= self.min_cluster_size
        ]
        
        # Limit the number of clusters
        if len(filtered_clusters) > self.max_clusters:
            # Sort clusters by size (largest first)
            filtered_clusters.sort(key=len, reverse=True)
            filtered_clusters = filtered_clusters[:self.max_clusters]
        
        return filtered_clusters
    
    def _create_categories(
        self, clusters: List[List[Image]], category_tree: CategoryTree
    ) -> None:
        """
        Create categories for each cluster.
        
        Args:
            clusters: The clusters to create categories for
            category_tree: The category tree to update
        """
        for i, cluster in enumerate(clusters):
            # Generate a name for the cluster based on common tags
            cluster_name = self._generate_cluster_name(cluster, i)
            
            # Create a category for this cluster
            category = Category(
                name=cluster_name,
                description=f"Cluster of {len(cluster)} similar images"
            )
            category_tree.add_category(category)
            
            # Add images to the category
            for image in cluster:
                category_tree.add_image_to_category(image.path.name, category.id)
                
                # Store the category ID in the image for reference
                if not hasattr(image, "categories"):
                    image.categories = []
                
                image.categories.append(category.id)
    
    def _generate_cluster_name(self, cluster: List[Image], cluster_index: int) -> str:
        """
        Generate a name for a cluster based on common tags.
        
        Args:
            cluster: The cluster to generate a name for
            cluster_index: The index of the cluster
            
        Returns:
            A name for the cluster
        """
        # Count tag frequencies within the cluster
        tag_counts = Counter()
        
        for image in cluster:
            if hasattr(image, "content_tags") and image.content_tags:
                tag_counts.update(image.content_tags)
        
        # Find the most common tags
        common_tags = [tag for tag, count in tag_counts.most_common(3)]
        
        if common_tags:
            # Use the most common tags as the name
            return " & ".join(tag.title() for tag in common_tags)
        else:
            # Use a generic name
            return f"Cluster {cluster_index + 1}"


class HybridCategorization(CategorizationAlgorithm):
    """
    Hybrid categorization algorithm that combines content-based and clustering approaches.
    """
    
    def __init__(
        self,
        content_algorithm: Optional[ContentBasedCategorization] = None,
        clustering_algorithm: Optional[HierarchicalClustering] = None
    ) -> None:
        """
        Initialize the HybridCategorization algorithm.
        
        Args:
            content_algorithm: The content-based algorithm to use
            clustering_algorithm: The clustering algorithm to use
        """
        self.content_algorithm = content_algorithm or ContentBasedCategorization()
        self.clustering_algorithm = clustering_algorithm or HierarchicalClustering()
        self.logger = logging.getLogger(__name__)
    
    def categorize(self, images: List[Image]) -> CategoryTree:
        """
        Categorize images using a hybrid approach.
        
        Args:
            images: The images to categorize
            
        Returns:
            A category tree with the categorized images
        """
        try:
            # First, try content-based categorization
            self.logger.info("Performing content-based categorization")
            category_tree = self.content_algorithm.categorize(images)
            
            # Check if we have enough categories
            if len(category_tree.categories) >= 3:
                return category_tree
            
            # If not, try hierarchical clustering
            self.logger.info("Falling back to hierarchical clustering")
            return self.clustering_algorithm.categorize(images)
        
        except Exception as e:
            self.logger.error(f"Failed to categorize images using hybrid approach: {e}")
            raise CategorizationError(f"Failed to categorize images using hybrid approach: {e}")


class CategorizationService:
    """
    Service for categorizing images.
    """
    
    def __init__(self, algorithm: Optional[CategorizationAlgorithm] = None) -> None:
        """
        Initialize the CategorizationService.
        
        Args:
            algorithm: The categorization algorithm to use
        """
        self.algorithm = algorithm or HybridCategorization()
        self.logger = logging.getLogger(__name__)
    
    def categorize(self, images: List[Image]) -> CategoryTree:
        """
        Categorize images into a hierarchical structure.
        
        Args:
            images: The images to categorize
            
        Returns:
            A category tree with the categorized images
        """
        try:
            return self.algorithm.categorize(images)
        
        except Exception as e:
            self.logger.error(f"Failed to categorize images: {e}")
            raise CategorizationError(f"Failed to categorize images: {e}")
    
    def categorize_by_path(self, image_paths: List[Path]) -> Tuple[List[Image], CategoryTree]:
        """
        Categorize images by path.
        
        Args:
            image_paths: The paths to the images
            
        Returns:
            A tuple of (images, category_tree)
        """
        # Create Image objects
        images = []
        for path in image_paths:
            try:
                images.append(Image(path))
            except Exception as e:
                self.logger.error(f"Failed to create Image object for {path}: {e}")
        
        # Categorize the images
        category_tree = self.categorize(images)
        
        return images, category_tree