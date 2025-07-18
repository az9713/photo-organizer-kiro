"""
Unit tests for the object and scene detection services.
"""

from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from photo_organizer.services.vision.base import ComputerVisionError, ObjectInfo, SceneInfo
from photo_organizer.services.vision.detection import (
    DetectionService,
    ObjectDetector,
    SceneDetector,
)


class TestObjectDetector:
    """Tests for the ObjectDetector class."""

    def test_init(self, tmp_path) -> None:
        """Test initializing the detector."""
        # Test with default parameters
        detector = ObjectDetector()
        assert detector.model_path is None
        assert detector.confidence_threshold == 0.5
        assert detector.max_detections == 10
        assert detector._model is None
        assert detector._labels == []
        
        # Test with custom parameters
        model_path = tmp_path / "models" / "object_detection"
        detector = ObjectDetector(
            model_path=model_path,
            confidence_threshold=0.6,
            max_detections=5
        )
        assert detector.model_path == model_path
        assert detector.confidence_threshold == 0.6
        assert detector.max_detections == 5

    @patch("tensorflow.keras.models.load_model")
    def test_load_model_with_path(self, mock_load_model, tmp_path) -> None:
        """Test loading a model with a specified path."""
        # Create a mock model path
        model_path = tmp_path / "models" / "object_detection"
        model_path.parent.mkdir(parents=True, exist_ok=True)
        model_path.touch()
        
        # Create the detector
        detector = ObjectDetector(model_path=model_path)
        
        # Mock the path.exists method
        with patch.object(Path, "exists", return_value=True):
            detector.load_model()
        
        # Check that the model was loaded
        mock_load_model.assert_called_once_with(str(model_path))
        assert len(detector._labels) > 0

    @patch("tensorflow.keras.applications.MobileNetV2")
    def test_load_model_without_path(self, mock_mobilenet) -> None:
        """Test loading a model without a specified path."""
        # Create the detector
        detector = ObjectDetector()
        
        # Load the model
        detector.load_model()
        
        # Check that the pre-trained model was loaded
        mock_mobilenet.assert_called_once_with(weights="imagenet")
        assert len(detector._labels) > 0

    @patch("tensorflow.keras.models.load_model")
    def test_load_model_error(self, mock_load_model) -> None:
        """Test loading a model with an error."""
        # Create the detector
        detector = ObjectDetector()
        
        # Mock load_model to raise an exception
        mock_load_model.side_effect = Exception("Test error")
        
        # Check that the error is handled
        with pytest.raises(ComputerVisionError) as excinfo:
            detector.load_model()
        
        assert "Failed to load object detection model" in str(excinfo.value)

    @patch("tensorflow.keras.models.load_model")
    @patch("photo_organizer.services.vision.detection.ObjectDetector._load_and_preprocess_image")
    def test_detect(self, mock_preprocess, mock_load_model, tmp_path) -> None:
        """Test detecting objects in an image."""
        # Create a mock model
        mock_model = MagicMock()
        mock_load_model.return_value = mock_model
        
        # Mock the model prediction
        mock_predictions = [
            np.array([[0.1, 0.2, 0.9, 0.3, 0.8]])  # Class probabilities
        ]
        mock_model.predict.return_value = mock_predictions
        
        # Mock image preprocessing
        mock_preprocess.return_value = np.zeros((224, 224, 3))
        
        # Create the detector
        detector = ObjectDetector()
        
        # Mock the object labels
        detector._labels = ["background", "person", "cat", "dog", "car"]
        
        # Test with a mock image
        image_path = tmp_path / "test.jpg"
        objects = detector.detect(image_path)
        
        # Check that the model was loaded and used
        mock_model.predict.assert_called_once()
        
        # Check the detected objects
        assert len(objects) == 2  # cat and car have confidence > 0.5
        assert objects[0].label == "cat"
        assert objects[0].confidence == 0.9
        assert objects[1].label == "car"
        assert objects[1].confidence == 0.8

    @patch("tensorflow.keras.models.load_model")
    @patch("photo_organizer.services.vision.detection.ObjectDetector._load_and_preprocess_image")
    def test_detect_error(self, mock_preprocess, mock_load_model, tmp_path) -> None:
        """Test detecting objects with an error."""
        # Create the detector
        detector = ObjectDetector()
        
        # Mock load_model to raise an exception
        mock_load_model.side_effect = Exception("Test error")
        
        # Test with a mock image
        image_path = tmp_path / "test.jpg"
        
        # Check that the error is handled
        with pytest.raises(ComputerVisionError) as excinfo:
            detector.detect(image_path)
        
        assert "Failed to detect objects" in str(excinfo.value)

    def test_load_and_preprocess_image(self, tmp_path) -> None:
        """Test loading and preprocessing an image."""
        # This test would require a real image file, so we'll mock it
        detector = ObjectDetector()
        
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
            result = detector._load_and_preprocess_image(image_path)
            
            # Check that the operations were performed
            mock_open.assert_called_once_with(image_path)
            mock_img.resize.assert_called_once_with((224, 224))
            mock_array.assert_called_once()
            mock_preprocess.assert_called_once()
            
            # Check the result
            assert result.shape == (224, 224, 3)

    def test_get_imagenet_labels(self) -> None:
        """Test getting ImageNet labels."""
        detector = ObjectDetector()
        labels = detector._get_imagenet_labels()
        
        assert len(labels) > 0
        assert "person" in labels
        assert "cat" in labels
        assert "dog" in labels


class TestSceneDetector:
    """Tests for the SceneDetector class."""

    def test_init(self, tmp_path) -> None:
        """Test initializing the detector."""
        # Test with default parameters
        detector = SceneDetector()
        assert detector.model_path is None
        assert detector.confidence_threshold == 0.5
        assert detector.max_detections == 5
        assert detector._model is None
        assert detector._labels == []
        
        # Test with custom parameters
        model_path = tmp_path / "models" / "scene_detection"
        detector = SceneDetector(
            model_path=model_path,
            confidence_threshold=0.6,
            max_detections=3
        )
        assert detector.model_path == model_path
        assert detector.confidence_threshold == 0.6
        assert detector.max_detections == 3

    @patch("tensorflow.keras.models.load_model")
    def test_load_model_with_path(self, mock_load_model, tmp_path) -> None:
        """Test loading a model with a specified path."""
        # Create a mock model path
        model_path = tmp_path / "models" / "scene_detection"
        model_path.parent.mkdir(parents=True, exist_ok=True)
        model_path.touch()
        
        # Create the detector
        detector = SceneDetector(model_path=model_path)
        
        # Mock the path.exists method
        with patch.object(Path, "exists", return_value=True):
            detector.load_model()
        
        # Check that the model was loaded
        mock_load_model.assert_called_once_with(str(model_path))
        assert len(detector._labels) > 0

    @patch("tensorflow.keras.applications.ResNet50")
    def test_load_model_without_path(self, mock_resnet) -> None:
        """Test loading a model without a specified path."""
        # Create the detector
        detector = SceneDetector()
        
        # Load the model
        detector.load_model()
        
        # Check that the pre-trained model was loaded
        mock_resnet.assert_called_once_with(weights="imagenet")
        assert len(detector._labels) > 0

    @patch("tensorflow.keras.models.load_model")
    @patch("photo_organizer.services.vision.detection.SceneDetector._load_and_preprocess_image")
    @patch("photo_organizer.services.vision.detection.SceneDetector._map_to_scenes")
    def test_detect(self, mock_map_to_scenes, mock_preprocess, mock_load_model, tmp_path) -> None:
        """Test detecting scenes in an image."""
        # Create a mock model
        mock_model = MagicMock()
        mock_load_model.return_value = mock_model
        
        # Mock the model prediction
        mock_predictions = [
            np.array([[0.1, 0.2, 0.9, 0.3, 0.8]])  # Class probabilities
        ]
        mock_model.predict.return_value = mock_predictions
        
        # Mock image preprocessing
        mock_preprocess.return_value = np.zeros((224, 224, 3))
        
        # Mock scene mapping
        mock_map_to_scenes.return_value = {
            "beach": 0.9,
            "forest": 0.8,
            "mountain": 0.3
        }
        
        # Create the detector
        detector = SceneDetector()
        
        # Test with a mock image
        image_path = tmp_path / "test.jpg"
        scenes = detector.detect(image_path)
        
        # Check that the model was loaded and used
        mock_model.predict.assert_called_once()
        mock_map_to_scenes.assert_called_once()
        
        # Check the detected scenes
        assert len(scenes) == 2  # beach and forest have confidence > 0.5
        assert scenes[0].label == "beach"
        assert scenes[0].confidence == 0.9
        assert scenes[1].label == "forest"
        assert scenes[1].confidence == 0.8

    def test_map_to_scenes(self) -> None:
        """Test mapping ImageNet classes to scene categories."""
        detector = SceneDetector()
        
        # Mock the labels
        detector._labels = ["beach", "mountain", "forest", "city", "desert"]
        
        # Create mock class probabilities
        class_probs = np.zeros(10)
        class_probs[0] = 0.9  # beach
        class_probs[2] = 0.8  # forest
        class_probs[9] = 0.7  # out of range
        
        # Map to scenes
        scene_probs = detector._map_to_scenes(class_probs)
        
        # Check the mapping
        assert len(scene_probs) == 2
        assert scene_probs["beach"] == 0.9
        assert scene_probs["forest"] == 0.8

    def test_get_scene_labels(self) -> None:
        """Test getting scene labels."""
        detector = SceneDetector()
        labels = detector._get_scene_labels()
        
        assert len(labels) > 0
        assert "beach" in labels
        assert "mountain" in labels
        assert "forest" in labels


class TestDetectionService:
    """Tests for the DetectionService class."""

    def test_init(self, tmp_path) -> None:
        """Test initializing the service."""
        # Test with default parameters
        service = DetectionService()
        assert service.model_dir == Path.home() / ".photo_organizer" / "models"
        assert isinstance(service.object_detector, ObjectDetector)
        assert isinstance(service.scene_detector, SceneDetector)
        
        # Test with custom parameters
        model_dir = tmp_path / "models"
        service = DetectionService(
            model_dir=model_dir,
            object_threshold=0.6,
            scene_threshold=0.7
        )
        assert service.model_dir == model_dir
        assert service.object_detector.confidence_threshold == 0.6
        assert service.scene_detector.confidence_threshold == 0.7

    @patch("photo_organizer.services.vision.detection.ObjectDetector.detect")
    def test_detect_objects(self, mock_detect, tmp_path) -> None:
        """Test detecting objects."""
        # Create mock objects
        mock_objects = [
            ObjectInfo(label="cat", confidence=0.9),
            ObjectInfo(label="dog", confidence=0.8)
        ]
        mock_detect.return_value = mock_objects
        
        # Create the service
        service = DetectionService()
        
        # Test with a mock image
        image_path = tmp_path / "test.jpg"
        objects = service.detect_objects(image_path)
        
        # Check that the detector was used
        mock_detect.assert_called_once_with(image_path)
        
        # Check the detected objects
        assert objects == mock_objects

    @patch("photo_organizer.services.vision.detection.SceneDetector.detect")
    def test_detect_scenes(self, mock_detect, tmp_path) -> None:
        """Test detecting scenes."""
        # Create mock scenes
        mock_scenes = [
            SceneInfo(label="beach", confidence=0.9),
            SceneInfo(label="forest", confidence=0.8)
        ]
        mock_detect.return_value = mock_scenes
        
        # Create the service
        service = DetectionService()
        
        # Test with a mock image
        image_path = tmp_path / "test.jpg"
        scenes = service.detect_scenes(image_path)
        
        # Check that the detector was used
        mock_detect.assert_called_once_with(image_path)
        
        # Check the detected scenes
        assert scenes == mock_scenes

    @patch("photo_organizer.services.vision.detection.ObjectDetector.detect")
    @patch("photo_organizer.services.vision.detection.SceneDetector.detect")
    def test_analyze_image(self, mock_detect_scenes, mock_detect_objects, tmp_path) -> None:
        """Test analyzing an image."""
        # Create mock objects and scenes
        mock_objects = [
            ObjectInfo(label="cat", confidence=0.9),
            ObjectInfo(label="dog", confidence=0.8)
        ]
        mock_scenes = [
            SceneInfo(label="beach", confidence=0.9),
            SceneInfo(label="forest", confidence=0.8)
        ]
        mock_detect_objects.return_value = mock_objects
        mock_detect_scenes.return_value = mock_scenes
        
        # Create the service
        service = DetectionService()
        
        # Test with a mock image
        image_path = tmp_path / "test.jpg"
        objects, scenes = service.analyze_image(image_path)
        
        # Check that the detectors were used
        mock_detect_objects.assert_called_once_with(image_path)
        mock_detect_scenes.assert_called_once_with(image_path)
        
        # Check the detected objects and scenes
        assert objects == mock_objects
        assert scenes == mock_scenes