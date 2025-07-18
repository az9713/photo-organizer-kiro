"""
Unit tests for the categorization algorithms.
"""

from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from photo_organizer.models.category import Category
from photo_organizer.models.category_tree import CategoryTree
from photo_organizer.models.image import Image
from photo_organizer.services.categorization import (
    CategorizationError,
    CategorizationService,
    ContentBasedCategorization,
    HierarchicalClustering,
    HybridCategorization,
)
from photo_organizer.services.vision.similarity import ImageSimilarityService


class TestContentBasedCategorization:
    """Tests for the ContentBasedCategorization class."""

    def test_init(self) -> None:
        """Test initializing the algorithm."""
        # Test with default parameters
        algorithm = ContentBasedCategorization()
        assert algorithm.min_category_size == 3
        assert algorithm.max_category_depth == 3
        assert algorithm.min_tag_frequency == 2
        
        # Test with custom parameters
        algorithm = ContentBasedCategorization(
            min_category_size=5,
            max_category_depth=2,
            min_tag_frequency=3
        )
        assert algorithm.min_category_size == 5
        assert algorithm.max_category_depth == 2
        assert algorithm.min_tag_frequency == 3

    def test_categorize(self, tmp_path) -> None:
        """Test categorizing images."""
        # Create the algorithm with a small min_category_size and min_tag_frequency
        algorithm = ContentBasedCategorization(min_category_size=1, min_tag_frequency=1)
        
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
        category_tree = algorithm.categorize([image1, image2, image3])
        
        # Check the category tree
        assert len(category_tree.categories) > 0
        
        # Check that the images are assigned to categories
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

    def test_categorize_error(self, tmp_path) -> None:
        """Test categorizing images with an error."""
        # Create the algorithm
        algorithm = ContentBasedCategorization()
        
        # Mock the _count_tag_frequencies method to raise an exception
        with patch.object(algorithm, "_count_tag_frequencies", side_effect=Exception("Test error")):
            # Create a test image
            image_path = tmp_path / "test.jpg"
            image_path.touch()
            image = Image(image_path)
            
            # Check that the error is handled
            with pytest.raises(CategorizationError) as excinfo:
                algorithm.categorize([image])
            
            assert "Failed to categorize images by content" in str(excinfo.value)

    def test_count_tag_frequencies(self, tmp_path) -> None:
        """Test counting tag frequencies."""
        # Create the algorithm
        algorithm = ContentBasedCategorization()
        
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
        
        # Count tag frequencies
        tag_counts = algorithm._count_tag_frequencies([image1, image2, image3])
        
        # Check the counts
        assert tag_counts["cat"] == 2
        assert tag_counts["indoor"] == 1
        assert tag_counts["outdoor"] == 2
        assert tag_counts["dog"] == 1

    def test_group_by_primary_tags(self, tmp_path) -> None:
        """Test grouping images by primary tags."""
        # Create the algorithm
        algorithm = ContentBasedCategorization()
        
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
        
        # Define frequent tags
        frequent_tags = {"cat", "outdoor"}
        
        # Group by primary tags
        tag_groups = algorithm._group_by_primary_tags([image1, image2, image3], frequent_tags)
        
        # Check the groups
        assert len(tag_groups) == 2
        assert len(tag_groups["cat"]) == 2
        assert len(tag_groups["outdoor"]) == 1
        assert image1 in tag_groups["cat"]
        assert image2 in tag_groups["cat"]
        assert image3 in tag_groups["outdoor"]

    def test_create_categories(self, tmp_path) -> None:
        """Test creating categories for tag groups."""
        # Create the algorithm with a small min_category_size
        algorithm = ContentBasedCategorization(min_category_size=1)
        
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
        
        # Create tag groups
        tag_groups = {"cat": [image1, image2]}
        
        # Create categories
        algorithm._create_categories(tag_groups, category_tree)
        
        # Check the category tree
        assert len(category_tree.categories) == 1
        
        # Check the category
        category = list(category_tree.categories.values())[0]
        assert category.name == "Cat"
        assert len(category.image_ids) == 2
        assert image_path1.name in category.image_ids
        assert image_path2.name in category.image_ids

    def test_create_subcategories(self, tmp_path) -> None:
        """Test creating subcategories for tag groups."""
        # Create the algorithm with a small min_category_size
        algorithm = ContentBasedCategorization(min_category_size=1)
        
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
        image2.content_tags = ["cat", "outdoor"]
        
        # Create tag groups
        tag_groups = {"cat": [image1, image2]}
        
        # Create subcategories
        algorithm._create_subcategories(tag_groups, category_tree)
        
        # Check the category tree
        assert len(category_tree.categories) == 3  # Parent + 2 subcategories
        
        # Check the subcategories
        indoor_category = None
        outdoor_category = None
        
        for category in category_tree.categories.values():
            if category.name == "Cat - Indoor":
                indoor_category = category
            elif category.name == "Cat - Outdoor":
                outdoor_category = category
        
        assert indoor_category is not None
        assert outdoor_category is not None
        assert len(indoor_category.image_ids) == 1
        assert len(outdoor_category.image_ids) == 1
        assert image_path1.name in indoor_category.image_ids
        assert image_path2.name in outdoor_category.image_ids


class TestHierarchicalClustering:
    """Tests for the HierarchicalClustering class."""

    def test_init(self) -> None:
        """Test initializing the algorithm."""
        # Test with default parameters
        algorithm = HierarchicalClustering()
        assert isinstance(algorithm.similarity_service, ImageSimilarityService)
        assert algorithm.similarity_threshold == 0.8
        assert algorithm.min_cluster_size == 3
        assert algorithm.max_clusters == 20
        
        # Test with custom parameters
        similarity_service = MagicMock(spec=ImageSimilarityService)
        algorithm = HierarchicalClustering(
            similarity_service=similarity_service,
            similarity_threshold=0.9,
            min_cluster_size=5,
            max_clusters=10
        )
        assert algorithm.similarity_service == similarity_service
        assert algorithm.similarity_threshold == 0.9
        assert algorithm.min_cluster_size == 5
        assert algorithm.max_clusters == 10

    @patch("photo_organizer.services.categorization.HierarchicalClustering._extract_features")
    @patch("photo_organizer.services.categorization.HierarchicalClustering._compute_distance_matrix")
    @patch("photo_organizer.services.categorization.HierarchicalClustering._cluster_images")
    @patch("photo_organizer.services.categorization.HierarchicalClustering._create_categories")
    def test_categorize(
        self, mock_create, mock_cluster, mock_compute, mock_extract, tmp_path
    ) -> None:
        """Test categorizing images."""
        # Create the algorithm
        algorithm = HierarchicalClustering()
        
        # Mock the methods
        features_map = {"image1": np.array([0.1, 0.2, 0.3])}
        mock_extract.return_value = features_map
        
        distance_matrix = np.array([[0, 0.5], [0.5, 0]])
        mock_compute.return_value = distance_matrix
        
        clusters = [[MagicMock(spec=Image)]]
        mock_cluster.return_value = clusters
        
        # Create test images
        image_path = tmp_path / "test.jpg"
        image_path.touch()
        image = Image(image_path)
        
        # Categorize the images
        category_tree = algorithm.categorize([image])
        
        # Check that the methods were called
        mock_extract.assert_called_once()
        mock_compute.assert_called_once_with(features_map)
        mock_cluster.assert_called_once_with(distance_matrix, [image])
        mock_create.assert_called_once_with(clusters, category_tree)

    def test_categorize_error(self, tmp_path) -> None:
        """Test categorizing images with an error."""
        # Create the algorithm
        algorithm = HierarchicalClustering()
        
        # Mock the _extract_features method to raise an exception
        with patch.object(algorithm, "_extract_features", side_effect=Exception("Test error")):
            # Create a test image
            image_path = tmp_path / "test.jpg"
            image_path.touch()
            image = Image(image_path)
            
            # Check that the error is handled
            with pytest.raises(CategorizationError) as excinfo:
                algorithm.categorize([image])
            
            assert "Failed to categorize images by clustering" in str(excinfo.value)

    @patch("photo_organizer.services.vision.similarity.FeatureExtractor.extract_features")
    def test_extract_features(self, mock_extract, tmp_path) -> None:
        """Test extracting features from images."""
        # Create the algorithm
        algorithm = HierarchicalClustering()
        
        # Mock the extract_features method
        features = np.array([0.1, 0.2, 0.3])
        mock_extract.return_value = features
        
        # Create test images
        image_path = tmp_path / "test.jpg"
        image_path.touch()
        image = Image(image_path)
        
        # Extract features
        features_map = algorithm._extract_features([image])
        
        # Check the features map
        assert len(features_map) == 1
        assert str(image_path) in features_map
        assert np.array_equal(features_map[str(image_path)], features)

    def test_compute_distance_matrix(self) -> None:
        """Test computing the distance matrix."""
        # Create the algorithm
        algorithm = HierarchicalClustering()
        
        # Create a features map
        features_map = {
            "image1": np.array([1.0, 0.0, 0.0]),
            "image2": np.array([0.0, 1.0, 0.0]),
            "image3": np.array([0.0, 0.0, 1.0])
        }
        
        # Compute the distance matrix
        distance_matrix = algorithm._compute_distance_matrix(features_map)
        
        # Check the distance matrix
        assert distance_matrix.shape == (3, 3)
        assert distance_matrix[0, 0] == 0  # Self-similarity
        assert distance_matrix[1, 1] == 0
        assert distance_matrix[2, 2] == 0
        assert distance_matrix[0, 1] == 1  # Orthogonal vectors
        assert distance_matrix[0, 2] == 1
        assert distance_matrix[1, 2] == 1

    @patch("scipy.cluster.hierarchy.linkage")
    @patch("scipy.cluster.hierarchy.fcluster")
    def test_cluster_images(self, mock_fcluster, mock_linkage, tmp_path) -> None:
        """Test clustering images."""
        # Create the algorithm
        algorithm = HierarchicalClustering()
        
        # Mock the linkage and fcluster functions
        mock_linkage.return_value = "linkage_result"
        mock_fcluster.return_value = np.array([1, 1, 2])  # Two clusters
        
        # Create test images
        image_path1 = tmp_path / "test1.jpg"
        image_path1.touch()
        image1 = Image(image_path1)
        
        image_path2 = tmp_path / "test2.jpg"
        image_path2.touch()
        image2 = Image(image_path2)
        
        image_path3 = tmp_path / "test3.jpg"
        image_path3.touch()
        image3 = Image(image_path3)
        
        # Create a distance matrix
        distance_matrix = np.zeros((3, 3))
        
        # Cluster the images
        clusters = algorithm._cluster_images(distance_matrix, [image1, image2, image3])
        
        # Check the clusters
        assert len(clusters) == 2
        assert len(clusters[0]) == 2  # First cluster has 2 images
        assert len(clusters[1]) == 1  # Second cluster has 1 image
        assert image1 in clusters[0]
        assert image2 in clusters[0]
        assert image3 in clusters[1]

    def test_create_categories(self, tmp_path) -> None:
        """Test creating categories for clusters."""
        # Create the algorithm with a small min_cluster_size
        algorithm = HierarchicalClustering(min_cluster_size=1)
        
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
        image2.content_tags = ["dog", "outdoor"]
        
        # Create clusters
        clusters = [[image1], [image2]]
        
        # Create categories
        algorithm._create_categories(clusters, category_tree)
        
        # Check the category tree
        assert len(category_tree.categories) == 2
        
        # Check the categories
        cat_category = None
        dog_category = None
        
        for category in category_tree.categories.values():
            if "Cat" in category.name:
                cat_category = category
            elif "Dog" in category.name:
                dog_category = category
        
        assert cat_category is not None
        assert dog_category is not None
        assert len(cat_category.image_ids) == 1
        assert len(dog_category.image_ids) == 1
        assert image_path1.name in cat_category.image_ids
        assert image_path2.name in dog_category.image_ids

    def test_generate_cluster_name(self, tmp_path) -> None:
        """Test generating a name for a cluster."""
        # Create the algorithm
        algorithm = HierarchicalClustering()
        
        # Create test images
        image_path1 = tmp_path / "test1.jpg"
        image_path1.touch()
        image1 = Image(image_path1)
        image1.content_tags = ["cat", "indoor"]
        
        image_path2 = tmp_path / "test2.jpg"
        image_path2.touch()
        image2 = Image(image_path2)
        image2.content_tags = ["cat", "pet"]
        
        # Generate a name for a cluster with common tags
        cluster = [image1, image2]
        name = algorithm._generate_cluster_name(cluster, 0)
        
        # Check the name
        assert name == "Cat"
        
        # Generate a name for a cluster without common tags
        image3 = Image(image_path1)
        image3.content_tags = []
        
        cluster = [image3]
        name = algorithm._generate_cluster_name(cluster, 1)
        
        # Check the name
        assert name == "Cluster 2"


class TestHybridCategorization:
    """Tests for the HybridCategorization class."""

    def test_init(self) -> None:
        """Test initializing the algorithm."""
        # Test with default parameters
        algorithm = HybridCategorization()
        assert isinstance(algorithm.content_algorithm, ContentBasedCategorization)
        assert isinstance(algorithm.clustering_algorithm, HierarchicalClustering)
        
        # Test with custom parameters
        content_algorithm = MagicMock(spec=ContentBasedCategorization)
        clustering_algorithm = MagicMock(spec=HierarchicalClustering)
        
        algorithm = HybridCategorization(
            content_algorithm=content_algorithm,
            clustering_algorithm=clustering_algorithm
        )
        
        assert algorithm.content_algorithm == content_algorithm
        assert algorithm.clustering_algorithm == clustering_algorithm

    def test_categorize_content_based(self, tmp_path) -> None:
        """Test categorizing images using content-based approach."""
        # Create mock algorithms
        content_algorithm = MagicMock(spec=ContentBasedCategorization)
        clustering_algorithm = MagicMock(spec=HierarchicalClustering)
        
        # Mock the categorize methods
        content_tree = CategoryTree()
        for i in range(3):
            category = Category(name=f"Category {i}")
            content_tree.add_category(category)
        
        content_algorithm.categorize.return_value = content_tree
        
        # Create the algorithm
        algorithm = HybridCategorization(
            content_algorithm=content_algorithm,
            clustering_algorithm=clustering_algorithm
        )
        
        # Create test images
        image_path = tmp_path / "test.jpg"
        image_path.touch()
        image = Image(image_path)
        
        # Categorize the images
        category_tree = algorithm.categorize([image])
        
        # Check that the content algorithm was used
        content_algorithm.categorize.assert_called_once_with([image])
        clustering_algorithm.categorize.assert_not_called()
        
        # Check the category tree
        assert category_tree == content_tree

    def test_categorize_clustering(self, tmp_path) -> None:
        """Test categorizing images using clustering approach."""
        # Create mock algorithms
        content_algorithm = MagicMock(spec=ContentBasedCategorization)
        clustering_algorithm = MagicMock(spec=HierarchicalClustering)
        
        # Mock the categorize methods
        content_tree = CategoryTree()
        for i in range(2):  # Only 2 categories, not enough
            category = Category(name=f"Category {i}")
            content_tree.add_category(category)
        
        clustering_tree = CategoryTree()
        for i in range(5):
            category = Category(name=f"Cluster {i}")
            clustering_tree.add_category(category)
        
        content_algorithm.categorize.return_value = content_tree
        clustering_algorithm.categorize.return_value = clustering_tree
        
        # Create the algorithm
        algorithm = HybridCategorization(
            content_algorithm=content_algorithm,
            clustering_algorithm=clustering_algorithm
        )
        
        # Create test images
        image_path = tmp_path / "test.jpg"
        image_path.touch()
        image = Image(image_path)
        
        # Categorize the images
        category_tree = algorithm.categorize([image])
        
        # Check that both algorithms were used
        content_algorithm.categorize.assert_called_once_with([image])
        clustering_algorithm.categorize.assert_called_once_with([image])
        
        # Check the category tree
        assert category_tree == clustering_tree

    def test_categorize_error(self, tmp_path) -> None:
        """Test categorizing images with an error."""
        # Create the algorithm
        algorithm = HybridCategorization()
        
        # Mock the content_algorithm.categorize method to raise an exception
        with patch.object(algorithm.content_algorithm, "categorize", side_effect=Exception("Test error")):
            # Create a test image
            image_path = tmp_path / "test.jpg"
            image_path.touch()
            image = Image(image_path)
            
            # Check that the error is handled
            with pytest.raises(CategorizationError) as excinfo:
                algorithm.categorize([image])
            
            assert "Failed to categorize images using hybrid approach" in str(excinfo.value)


class TestCategorizationService:
    """Tests for the CategorizationService class."""

    def test_init(self) -> None:
        """Test initializing the service."""
        # Test with default parameters
        service = CategorizationService()
        assert isinstance(service.algorithm, HybridCategorization)
        
        # Test with custom parameters
        algorithm = MagicMock(spec=HybridCategorization)
        service = CategorizationService(algorithm=algorithm)
        assert service.algorithm == algorithm

    def test_categorize(self, tmp_path) -> None:
        """Test categorizing images."""
        # Create a mock algorithm
        algorithm = MagicMock(spec=HybridCategorization)
        
        # Mock the categorize method
        category_tree = CategoryTree()
        algorithm.categorize.return_value = category_tree
        
        # Create the service
        service = CategorizationService(algorithm=algorithm)
        
        # Create test images
        image_path = tmp_path / "test.jpg"
        image_path.touch()
        image = Image(image_path)
        
        # Categorize the images
        result = service.categorize([image])
        
        # Check that the algorithm was used
        algorithm.categorize.assert_called_once_with([image])
        
        # Check the result
        assert result == category_tree

    def test_categorize_error(self, tmp_path) -> None:
        """Test categorizing images with an error."""
        # Create a mock algorithm
        algorithm = MagicMock(spec=HybridCategorization)
        
        # Mock the categorize method to raise an exception
        algorithm.categorize.side_effect = Exception("Test error")
        
        # Create the service
        service = CategorizationService(algorithm=algorithm)
        
        # Create test images
        image_path = tmp_path / "test.jpg"
        image_path.touch()
        image = Image(image_path)
        
        # Check that the error is handled
        with pytest.raises(CategorizationError) as excinfo:
            service.categorize([image])
        
        assert "Failed to categorize images" in str(excinfo.value)

    def test_categorize_by_path(self, tmp_path) -> None:
        """Test categorizing images by path."""
        # Create a mock algorithm
        algorithm = MagicMock(spec=HybridCategorization)
        
        # Mock the categorize method
        category_tree = CategoryTree()
        algorithm.categorize.return_value = category_tree
        
        # Create the service
        service = CategorizationService(algorithm=algorithm)
        
        # Create test images
        image_path1 = tmp_path / "test1.jpg"
        image_path1.touch()
        
        image_path2 = tmp_path / "test2.jpg"
        image_path2.touch()
        
        # Categorize the images
        images, tree = service.categorize_by_path([image_path1, image_path2])
        
        # Check that the algorithm was used
        algorithm.categorize.assert_called_once()
        
        # Check the results
        assert len(images) == 2
        assert tree == category_tree