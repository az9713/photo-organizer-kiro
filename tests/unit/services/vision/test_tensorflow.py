"""
Unit tests for the TensorFlow computer vision service.
"""

from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from photo_organizer.services.vision.base import ComputerVisionError, FaceInfo, ObjectInfo, SceneInfo
from photo_organizer.services.vision.tensorflow import TensorFlowVisionService


class TestTensorFlowVisionService:
    """Tests for the TensorFlowVisionService class."""

    def test_init(self, tmp_path) -> None:
        """Test initializing the service."""
        # Test with default parameters
        service = TensorFlowVisionService()
        assert service.model_dir == Path.home() / ".photo_organizer" / "models"
        assert service.object_detection_threshold == 0.5
        assert service.scene_detection_threshold == 0.5
        assert service.face_detection_threshold == 0.5
        
        # Test with custom parameters
        model_dir = tmp_path / "models"
        service = TensorFlowVisionService(
            model_dir=model_dir,
            object_detection_threshold=0.6,
            scene_detection_threshold=0.7,
            face_detection_threshold=0.8
        )
        assert service.model_dir == model_dir
        assert service.object_detection_threshold == 0.6
        assert service.scene_detection_threshold == 0.7
        assert service.face_detection_threshold == 0.8
        assert model_dir.exists()

    @patch("tensorflow.keras.models.load_model")
    @patch("photo_organizer.services.vision.tensorflow.TensorFlowVisionService._load_and_preprocess_image")
    def test_detect_objects(self, mock_preprocess, mock_load_model, tmp_path) -> None:
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
        
        # Create the service
        service = TensorFlowVisionService(model_dir=tmp_path / "models")
        
        # Mock the object labels
        service._object_labels = ["background", "person", "cat", "dog", "car"]
        
        # Test with a mock image
        image_path = tmp_path / "test.jpg"
        objects = service.detect_objects(image_path)
        
        # Check that the model was loaded and used
        mock_load_model.assert_called_once()
        mock_model.predict.assert_called_once()
        
        # Check the detected objects
        assert len(objects) == 2  # cat and car have confidence > 0.5
        assert objects[0].label == "cat"
        assert objects[0].confidence == 0.9
        assert objects[1].label == "car"
        assert objects[1].confidence == 0.8

    @patch("tensorflow.keras.models.load_model")
    @patch("photo_organizer.services.vision.tensorflow.TensorFlowVisionService._load_and_preprocess_image")
    def test_detect_scenes(self, mock_preprocess, mock_load_model, tmp_path) -> None:
        """Test detecting scenes in an image."""
        # Create a mock model
        mock_model = MagicMock()
        mock_load_model.return_value = mock_model
        
        # Mock the model prediction
        mock_predictions = [
            np.array([[0.1, 0.9, 0.3, 0.8]])  # Class probabilities
        ]
        mock_model.predict.return_value = mock_predictions
        
        # Mock image preprocessing
        mock_preprocess.return_value = np.zeros((224, 224, 3))
        
        # Create the service
        service = TensorFlowVisionService(model_dir=tmp_path / "models")
        
        # Mock the scene labels
        service._scene_labels = ["indoor", "beach", "mountain", "forest"]
        
        # Test with a mock image
        image_path = tmp_path / "test.jpg"
        scenes = service.detect_scenes(image_path)
        
        # Check that the model was loaded and used
        mock_load_model.assert_called_once()
        mock_model.predict.assert_called_once()
        
        # Check the detected scenes
        assert len(scenes) == 2  # beach and forest have confidence > 0.5
        assert scenes[0].label == "beach"
        assert scenes[0].confidence == 0.9
        assert scenes[1].label == "forest"
        assert scenes[1].confidence == 0.8

    @patch("tensorflow.keras.models.load_model")
    @patch("photo_organizer.services.vision.tensorflow.TensorFlowVisionService._load_and_preprocess_image")
    def test_detect_faces(self, mock_preprocess, mock_load_model, tmp_path) -> None:
        """Test detecting faces in an image."""
        # Create a mock model
        mock_model = MagicMock()
        mock_load_model.return_value = mock_model
        
        # Mock the model prediction
        mock_predictions = [
            np.array([[0.9, 0.8]]),  # Face probabilities
            np.array([[[10, 20, 50, 60], [100, 120, 150, 170]]]),  # Bounding boxes
            np.array([[[15, 25, 35, 25, 25, 30, 20, 40, 30, 40]]])  # Landmarks (flattened)
        ]
        mock_model.predict.return_value = mock_predictions
        
        # Mock image preprocessing
        mock_preprocess.return_value = np.zeros((224, 224, 3))
        
        # Create the service
        service = TensorFlowVisionService(model_dir=tmp_path / "models")
        
        # Test with a mock image
        image_path = tmp_path / "test.jpg"
        faces = service.detect_faces(image_path)
        
        # Check that the model was loaded and used
        mock_load_model.assert_called_once()
        mock_model.predict.assert_called_once()
        
        # Check the detected faces
        assert len(faces) == 2
        assert faces[0].confidence == 0.9
        assert faces[0].bounding_box == (20.0, 10.0, 30.0, 50.0)  # (x, y, width, height)
        assert faces[1].confidence == 0.8
        assert faces[1].bounding_box == (120.0, 100.0, 30.0, 50.0)  # (x, y, width, height)

    @patch("photo_organizer.services.vision.tensorflow.TensorFlowVisionService.detect_objects")
    @patch("photo_organizer.services.vision.tensorflow.TensorFlowVisionService.detect_scenes")
    def test_generate_tags(self, mock_detect_scenes, mock_detect_objects, tmp_path) -> None:
        """Test generating tags for an image."""
        # Mock object detection
        mock_detect_objects.return_value = [
            ObjectInfo(label="Cat", confidence=0.9),
            ObjectInfo(label="Dog", confidence=0.8)
        ]
        
        # Mock scene detection
        mock_detect_scenes.return_value = [
            SceneInfo(label="Indoor", confidence=0.7),
            SceneInfo(label="Living Room", confidence=0.6)
        ]
        
        # Create the service
        service = TensorFlowVisionService(model_dir=tmp_path / "models")
        
        # Test with a mock image
        image_path = tmp_path / "test.jpg"
        tags = service.generate_tags(image_path)
        
        # Check that the detection methods were called
        mock_detect_objects.assert_called_once_with(image_path)
        mock_detect_scenes.assert_called_once_with(image_path)
        
        # Check the generated tags
        assert len(tags) == 4
        assert "cat" in tags
        assert "dog" in tags
        assert "indoor" in tags
        assert "living room" in tags
        
        # Check that tags are sorted by confidence
        assert tags[0] == "cat"  # Highest confidence
        assert tags[1] == "dog"
        assert tags[2] == "indoor"
        assert tags[3] == "living room"  # Lowest confidence

    @patch("tensorflow.keras.applications.MobileNetV2")
    @patch("photo_organizer.services.vision.tensorflow.TensorFlowVisionService._load_and_preprocess_image")
    def test_analyze_similarity(self, mock_preprocess, mock_mobilenet, tmp_path) -> None:
        """Test analyzing similarity between two images."""
        # Create a mock model
        mock_model = MagicMock()
        mock_mobilenet.return_value = mock_model
        
        # Mock the model prediction
        mock_model.predict.side_effect = [
            np.array([[0.1, 0.2, 0.3]]),  # Features for image 1
            np.array([[0.2, 0.3, 0.4]])   # Features for image 2
        ]
        
        # Mock image preprocessing
        mock_preprocess.return_value = np.zeros((224, 224, 3))
        
        # Create the service
        service = TensorFlowVisionService(model_dir=tmp_path / "models")
        
        # Test with mock images
        image_path1 = tmp_path / "test1.jpg"
        image_path2 = tmp_path / "test2.jpg"
        similarity = service.analyze_similarity(image_path1, image_path2)
        
        # Check that the model was used
        assert mock_model.predict.call_count == 2
        
        # Check the similarity score
        assert 0 <= similarity <= 1
        assert similarity > 0.9  # The mock features are similar

    def test_load_and_preprocess_image(self, tmp_path) -> None:
        """Test loading and preprocessing an image."""
        # This test would require a real image file, so we'll mock it
        service = TensorFlowVisionService(model_dir=tmp_path / "models")
        
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
            result = service._load_and_preprocess_image(image_path, (224, 224))
            
            # Check that the operations were performed
            mock_open.assert_called_once_with(image_path)
            mock_img.resize.assert_called_once_with((224, 224))
            mock_array.assert_called_once()
            mock_preprocess.assert_called_once()
            
            # Check the result
            assert result.shape == (224, 224, 3)

    def test_get_imagenet_labels(self) -> None:
        """Test getting ImageNet labels."""
        service = TensorFlowVisionService()
        labels = service._get_imagenet_labels()
        
        assert len(labels) > 0
        assert "person" in labels
        assert "cat" in labels
        assert "dog" in labels

    def test_get_scene_labels(self) -> None:
        """Test getting scene labels."""
        service = TensorFlowVisionService()
        labels = service._get_scene_labels()
        
        assert len(labels) > 0
        assert "beach" in labels
        assert "mountain" in labels
        assert "forest" in labels