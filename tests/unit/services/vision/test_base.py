"""
Unit tests for the base computer vision service.
"""

import pytest

from photo_organizer.services.vision.base import (
    ComputerVisionError,
    FaceInfo,
    ObjectInfo,
    SceneInfo,
)


class TestObjectInfo:
    """Tests for the ObjectInfo class."""

    def test_init(self) -> None:
        """Test initializing an ObjectInfo object."""
        # Test with just label and confidence
        obj = ObjectInfo(label="cat", confidence=0.95)
        assert obj.label == "cat"
        assert obj.confidence == 0.95
        assert obj.bounding_box is None
        
        # Test with bounding box
        bbox = (10.0, 20.0, 30.0, 40.0)
        obj = ObjectInfo(label="dog", confidence=0.85, bounding_box=bbox)
        assert obj.label == "dog"
        assert obj.confidence == 0.85
        assert obj.bounding_box == bbox


class TestSceneInfo:
    """Tests for the SceneInfo class."""

    def test_init(self) -> None:
        """Test initializing a SceneInfo object."""
        scene = SceneInfo(label="beach", confidence=0.75)
        assert scene.label == "beach"
        assert scene.confidence == 0.75


class TestFaceInfo:
    """Tests for the FaceInfo class."""

    def test_init(self) -> None:
        """Test initializing a FaceInfo object."""
        # Test with just confidence and bounding box
        bbox = (10.0, 20.0, 30.0, 40.0)
        face = FaceInfo(confidence=0.9, bounding_box=bbox)
        assert face.confidence == 0.9
        assert face.bounding_box == bbox
        assert face.landmarks is None
        
        # Test with landmarks
        landmarks = {
            "left_eye": (15.0, 25.0),
            "right_eye": (35.0, 25.0),
            "nose": (25.0, 30.0),
            "left_mouth": (20.0, 40.0),
            "right_mouth": (30.0, 40.0)
        }
        face = FaceInfo(confidence=0.9, bounding_box=bbox, landmarks=landmarks)
        assert face.confidence == 0.9
        assert face.bounding_box == bbox
        assert face.landmarks == landmarks


class TestComputerVisionError:
    """Tests for the ComputerVisionError class."""

    def test_init(self) -> None:
        """Test initializing a ComputerVisionError object."""
        error = ComputerVisionError("Test error")
        assert str(error) == "Test error"