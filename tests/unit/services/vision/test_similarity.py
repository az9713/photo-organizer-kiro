"""
Unit tests for the image similarity analysis services.
"""

from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from photo_organizer.services.vision.base import ComputerVisionError
from photo_organizer.services.vision.similarity import (
    FeatureExtractor,
    ImageSimilarityService,
    SimilarityAnalyzer,
)


class TestFeatureExtractor:
    """Tests for the FeatureExtractor class."""

    def test_init(self, tmp_path) -> None:
        """Test initializing the feature extractor."""
        # Test with default parameters
        extractor = FeatureExtractor()
        assert extractor.model_path is None
        assert extractor._model is None
        
        # Test with custom parameters
        model_path = tmp_path / "models" / "feature_extraction"
        extractor = FeatureExtractor(model_path=model_path)
        assert extractor.model_path == model_path

    @patch("tensorflow.keras.models.load_model")
    def test_load_model_with_path(self, mock_load_model, tmp_path) -> None:
        """Test loading a model with a specified path."""
        # Create a mock model path
        model_path = tmp_path / "models" / "feature_extraction"
        model_path.parent.mkdir(parents=True, exist_ok=True)
        model_path.touch()
        
        # Create the extractor
        extractor = FeatureExtractor(model_path=model_path)
        
        # Mock the path.exists method
        with patch.object(Path, "exists", return_value=True):
            extractor.load_model()
        
        # Check that the model was loaded
        mock_load_model.assert_called_once_with(str(model_path))

    @patch("tensorflow.keras.applications.MobileNetV2")
    def test_load_model_without_path(self, mock_mobilenet) -> None:
        """Test loading a model without a specified path."""
        # Create the extractor
        extractor = FeatureExtractor()
        
        # Load the model
        extractor.load_model()
        
        # Check that the pre-trained model was loaded
        mock_mobilenet.assert_called_once()
        assert "include_top" in mock_mobilenet.call_args[1]
        assert mock_mobilenet.call_args[1]["include_top"] is False
        assert mock_mobilenet.call_args[1]["weights"] == "imagenet"
        assert mock_mobilenet.call_args[1]["pooling"] == "avg"

    @patch("tensorflow.keras.models.load_model")
    def test_load_model_error(self, mock_load_model) -> None:
        """Test loading a model with an error."""
        # Create the extractor
        extractor = FeatureExtractor()
        
        # Mock load_model to raise an exception
        mock_load_model.side_effect = Exception("Test error")
        
        # Check that the error is handled
        with pytest.raises(ComputerVisionError) as excinfo:
            extractor.load_model()
        
        assert "Failed to load feature extraction model" in str(excinfo.value)

    @patch("tensorflow.keras.models.load_model")
    @patch("photo_organizer.services.vision.similarity.FeatureExtractor._load_and_preprocess_image")
    def test_extract_features(self, mock_preprocess, mock_load_model, tmp_path) -> None:
        """Test extracting features from an image."""
        # Create a mock model
        mock_model = MagicMock()
        mock_load_model.return_value = mock_model
        
        # Mock the model prediction
        mock_model.predict.return_value = np.array([[0.1, 0.2, 0.3]])
        
        # Mock image preprocessing
        mock_preprocess.return_value = np.zeros((224, 224, 3))
        
        # Create the extractor
        extractor = FeatureExtractor()
        
        # Test with a mock image
        image_path = tmp_path / "test.jpg"
        features = extractor.extract_features(image_path)
        
        # Check that the model was loaded and used
        mock_model.predict.assert_called_once()
        
        # Check the extracted features
        assert features.shape == (3,)
        assert np.isclose(np.linalg.norm(features), 1.0)  # Check normalization

    @patch("tensorflow.keras.models.load_model")
    @patch("photo_organizer.services.vision.similarity.FeatureExtractor._load_and_preprocess_image")
    def test_extract_features_error(self, mock_preprocess, mock_load_model, tmp_path) -> None:
        """Test extracting features with an error."""
        # Create the extractor
        extractor = FeatureExtractor()
        
        # Mock load_model to raise an exception
        mock_load_model.side_effect = Exception("Test error")
        
        # Test with a mock image
        image_path = tmp_path / "test.jpg"
        
        # Check that the error is handled
        with pytest.raises(ComputerVisionError) as excinfo:
            extractor.extract_features(image_path)
        
        assert "Failed to extract features" in str(excinfo.value)

    def test_load_and_preprocess_image(self, tmp_path) -> None:
        """Test loading and preprocessing an image."""
        # This test would require a real image file, so we'll mock it
        extractor = FeatureExtractor()
        
        with patch("PIL.Image.open") as mock_open, \
             patch("numpy.array") as mock_array, \
             patch("tensorflow.keras.applications.mobilenet_v2.preprocess_input") as mock_preprocess:
            
            # Mock the image operations
            mock_img = MagicMock()
            mock_img.mode = "RGB"
            mock_img.resize.return_value = mock_img
            mock_open.return_value = mock_img
            
            mock_array.return_value = np.zeros((224, 224, 3))
            mock_preprocess.return_value = np.zeros((224, 224, 3))
            
            # Call the method
            image_path = tmp_path / "test.jpg"
            result = extractor._load_and_preprocess_image(image_path)
            
            # Check that the operations were performed
            mock_open.assert_called_once_with(image_path)
            mock_img.resize.assert_called_once_with((224, 224))
            mock_array.assert_called_once()
            mock_preprocess.assert_called_once()
            
            # Check the result
            assert result.shape == (224, 224, 3)


class TestSimilarityAnalyzer:
    """Tests for the SimilarityAnalyzer class."""

    def test_init(self) -> None:
        """Test initializing the analyzer."""
        # Test with default parameters
        analyzer = SimilarityAnalyzer()
        assert isinstance(analyzer.feature_extractor, FeatureExtractor)
        
        # Test with custom parameters
        feature_extractor = MagicMock(spec=FeatureExtractor)
        analyzer = SimilarityAnalyzer(feature_extractor=feature_extractor)
        assert analyzer.feature_extractor == feature_extractor

    def test_compute_similarity(self, tmp_path) -> None:
        """Test computing similarity between two images."""
        # Create a mock feature extractor
        feature_extractor = MagicMock(spec=FeatureExtractor)
        
        # Mock the extract_features method
        feature_extractor.extract_features.side_effect = [
            np.array([0.1, 0.2, 0.3]),  # Features for image 1
            np.array([0.2, 0.3, 0.4])   # Features for image 2
        ]
        
        # Create the analyzer
        analyzer = SimilarityAnalyzer(feature_extractor=feature_extractor)
        
        # Test with mock images
        image_path1 = tmp_path / "test1.jpg"
        image_path2 = tmp_path / "test2.jpg"
        similarity = analyzer.compute_similarity(image_path1, image_path2)
        
        # Check that the feature extractor was used
        assert feature_extractor.extract_features.call_count == 2
        feature_extractor.extract_features.assert_any_call(image_path1)
        feature_extractor.extract_features.assert_any_call(image_path2)
        
        # Check the similarity score
        assert 0 <= similarity <= 1
        assert similarity > 0.9  # The mock features are similar

    def test_compute_similarity_error(self, tmp_path) -> None:
        """Test computing similarity with an error."""
        # Create a mock feature extractor
        feature_extractor = MagicMock(spec=FeatureExtractor)
        
        # Mock the extract_features method to raise an exception
        feature_extractor.extract_features.side_effect = Exception("Test error")
        
        # Create the analyzer
        analyzer = SimilarityAnalyzer(feature_extractor=feature_extractor)
        
        # Test with mock images
        image_path1 = tmp_path / "test1.jpg"
        image_path2 = tmp_path / "test2.jpg"
        
        # Check that the error is handled
        with pytest.raises(ComputerVisionError) as excinfo:
            analyzer.compute_similarity(image_path1, image_path2)
        
        assert "Failed to compute similarity" in str(excinfo.value)

    def test_find_similar_images(self, tmp_path) -> None:
        """Test finding similar images."""
        # Create a mock feature extractor
        feature_extractor = MagicMock(spec=FeatureExtractor)
        
        # Mock the extract_features method
        target_features = np.array([0.1, 0.2, 0.3])
        feature_extractor.extract_features.side_effect = [
            target_features,                # Features for target image
            np.array([0.11, 0.21, 0.31]),   # Features for similar image 1
            np.array([0.5, 0.6, 0.7]),      # Features for dissimilar image
            np.array([0.12, 0.22, 0.32])    # Features for similar image 2
        ]
        
        # Create the analyzer
        analyzer = SimilarityAnalyzer(feature_extractor=feature_extractor)
        
        # Test with mock images
        target_image = tmp_path / "target.jpg"
        image_paths = [
            tmp_path / "similar1.jpg",
            tmp_path / "dissimilar.jpg",
            tmp_path / "similar2.jpg"
        ]
        similar_images = analyzer.find_similar_images(target_image, image_paths, threshold=0.8)
        
        # Check that the feature extractor was used
        assert feature_extractor.extract_features.call_count == 4
        
        # Check the similar images
        assert len(similar_images) == 2
        assert similar_images[0][0] == image_paths[0]  # similar1.jpg
        assert similar_images[1][0] == image_paths[2]  # similar2.jpg
        assert similar_images[0][1] > 0.9  # High similarity
        assert similar_images[1][1] > 0.9  # High similarity

    def test_cluster_images(self, tmp_path) -> None:
        """Test clustering images."""
        # Create a mock feature extractor
        feature_extractor = MagicMock(spec=FeatureExtractor)
        
        # Create image paths
        image_paths = [
            tmp_path / "image1.jpg",
            tmp_path / "image2.jpg",
            tmp_path / "image3.jpg",
            tmp_path / "image4.jpg"
        ]
        
        # Mock the extract_features method to create two clusters
        features = {
            image_paths[0]: np.array([0.1, 0.2, 0.3]),
            image_paths[1]: np.array([0.11, 0.21, 0.31]),
            image_paths[2]: np.array([0.5, 0.6, 0.7]),
            image_paths[3]: np.array([0.51, 0.61, 0.71])
        }
        
        def mock_extract_features(path):
            return features[path]
        
        feature_extractor.extract_features.side_effect = mock_extract_features
        
        # Create the analyzer
        analyzer = SimilarityAnalyzer(feature_extractor=feature_extractor)
        
        # Test clustering
        clusters = analyzer.cluster_images(image_paths, threshold=0.8)
        
        # Check that the feature extractor was used
        assert feature_extractor.extract_features.call_count == 4
        
        # Check the clusters
        assert len(clusters) == 2
        
        # Check that each cluster has the correct images
        if image_paths[0] in clusters[0]:
            assert image_paths[1] in clusters[0]
            assert image_paths[2] in clusters[1]
            assert image_paths[3] in clusters[1]
        else:
            assert image_paths[0] in clusters[1]
            assert image_paths[1] in clusters[1]
            assert image_paths[2] in clusters[0]
            assert image_paths[3] in clusters[0]


class TestImageSimilarityService:
    """Tests for the ImageSimilarityService class."""

    def test_init(self, tmp_path) -> None:
        """Test initializing the service."""
        # Test with default parameters
        service = ImageSimilarityService()
        assert service.model_dir == Path.home() / ".photo_organizer" / "models"
        assert isinstance(service.feature_extractor, FeatureExtractor)
        assert isinstance(service.similarity_analyzer, SimilarityAnalyzer)
        
        # Test with custom parameters
        model_dir = tmp_path / "models"
        service = ImageSimilarityService(model_dir=model_dir)
        assert service.model_dir == model_dir
        assert service.feature_extractor.model_path == model_dir / "feature_extraction"

    @patch("photo_organizer.services.vision.similarity.SimilarityAnalyzer.compute_similarity")
    def test_compute_similarity(self, mock_compute, tmp_path) -> None:
        """Test computing similarity."""
        # Mock the compute_similarity method
        mock_compute.return_value = 0.9
        
        # Create the service
        service = ImageSimilarityService()
        
        # Test with mock images
        image_path1 = tmp_path / "test1.jpg"
        image_path2 = tmp_path / "test2.jpg"
        similarity = service.compute_similarity(image_path1, image_path2)
        
        # Check that the analyzer was used
        mock_compute.assert_called_once_with(image_path1, image_path2)
        
        # Check the similarity score
        assert similarity == 0.9

    @patch("photo_organizer.services.vision.similarity.SimilarityAnalyzer.find_similar_images")
    def test_find_similar_images(self, mock_find, tmp_path) -> None:
        """Test finding similar images."""
        # Create mock results
        mock_results = [
            (tmp_path / "similar1.jpg", 0.9),
            (tmp_path / "similar2.jpg", 0.85)
        ]
        mock_find.return_value = mock_results
        
        # Create the service
        service = ImageSimilarityService()
        
        # Test with mock images
        target_image = tmp_path / "target.jpg"
        image_paths = [
            tmp_path / "similar1.jpg",
            tmp_path / "dissimilar.jpg",
            tmp_path / "similar2.jpg"
        ]
        similar_images = service.find_similar_images(target_image, image_paths, threshold=0.8)
        
        # Check that the analyzer was used
        mock_find.assert_called_once_with(target_image, image_paths, 0.8)
        
        # Check the similar images
        assert similar_images == mock_results

    @patch("photo_organizer.services.vision.similarity.SimilarityAnalyzer.cluster_images")
    def test_cluster_images(self, mock_cluster, tmp_path) -> None:
        """Test clustering images."""
        # Create mock results
        mock_results = [
            [tmp_path / "image1.jpg", tmp_path / "image2.jpg"],
            [tmp_path / "image3.jpg", tmp_path / "image4.jpg"]
        ]
        mock_cluster.return_value = mock_results
        
        # Create the service
        service = ImageSimilarityService()
        
        # Test with mock images
        image_paths = [
            tmp_path / "image1.jpg",
            tmp_path / "image2.jpg",
            tmp_path / "image3.jpg",
            tmp_path / "image4.jpg"
        ]
        clusters = service.cluster_images(image_paths, threshold=0.8)
        
        # Check that the analyzer was used
        mock_cluster.assert_called_once_with(image_paths, 0.8)
        
        # Check the clusters
        assert clusters == mock_results