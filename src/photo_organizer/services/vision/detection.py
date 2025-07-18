"""
Object and scene detection services.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

import numpy as np
import tensorflow as tf
from PIL import Image

from photo_organizer.services.vision.base import (
    ComputerVisionError,
    ComputerVisionService,
    ObjectInfo,
    SceneInfo,
)


class ObjectDetector:
    """
    Service for detecting objects in images.
    """
    
    def __init__(
        self,
        model_path: Optional[Path] = None,
        confidence_threshold: float = 0.5,
        max_detections: int = 10
    ) -> None:
        """
        Initialize the ObjectDetector.
        
        Args:
            model_path: Path to the object detection model
            confidence_threshold: Minimum confidence threshold for detections
            max_detections: Maximum number of detections to return
        """
        self.model_path = model_path
        self.confidence_threshold = confidence_threshold
        self.max_detections = max_detections
        self._model = None
        self._labels = []
    
    def load_model(self) -> None:
        """Load the object detection model."""
        try:
            if self.model_path and self.model_path.exists():
                # Load a saved model
                self._model = tf.keras.models.load_model(str(self.model_path))
            else:
                # Use a pre-trained model
                self._model = tf.keras.applications.MobileNetV2(weights="imagenet")
            
            # Load ImageNet labels
            self._labels = self._get_imagenet_labels()
        
        except Exception as e:
            raise ComputerVisionError(f"Failed to load object detection model: {e}")
    
    def detect(self, image_path: Path) -> List[ObjectInfo]:
        """
        Detect objects in an image.
        
        Args:
            image_path: Path to the image
            
        Returns:
            A list of detected objects
        """
        try:
            # Load the model if not already loaded
            if self._model is None:
                self.load_model()
            
            # Load and preprocess the image
            img = self._load_and_preprocess_image(image_path)
            
            # Run inference
            predictions = self._model.predict(np.expand_dims(img, axis=0))
            
            # Process the predictions
            if isinstance(predictions, list):
                # For models that return multiple outputs
                class_probs = predictions[0][0]
            else:
                # For models that return a single output
                class_probs = predictions[0]
            
            # Get the top predictions
            top_indices = np.argsort(class_probs)[-self.max_detections:][::-1]
            
            # Create ObjectInfo objects
            objects = []
            for idx in top_indices:
                confidence = float(class_probs[idx])
                if confidence >= self.confidence_threshold:
                    label = self._labels[idx] if idx < len(self._labels) else f"Class_{idx}"
                    objects.append(ObjectInfo(label=label, confidence=confidence))
            
            return objects
        
        except Exception as e:
            raise ComputerVisionError(f"Failed to detect objects in {image_path}: {e}")
    
    def _load_and_preprocess_image(self, image_path: Path) -> np.ndarray:
        """
        Load and preprocess an image for object detection.
        
        Args:
            image_path: Path to the image
            
        Returns:
            The preprocessed image as a numpy array
        """
        # Load the image
        img = Image.open(image_path)
        
        # Resize the image
        img = img.resize((224, 224))
        
        # Convert to RGB if needed
        if img.mode != "RGB":
            img = img.convert("RGB")
        
        # Convert to numpy array
        img_array = np.array(img)
        
        # Preprocess for TensorFlow models
        img_array = tf.keras.applications.mobilenet_v2.preprocess_input(img_array)
        
        return img_array
    
    def _get_imagenet_labels(self) -> List[str]:
        """
        Get the ImageNet class labels.
        
        Returns:
            A list of class labels
        """
        # This is a simplified list of ImageNet labels
        return [
            "person", "bicycle", "car", "motorcycle", "airplane", "bus", "train", "truck", "boat",
            "traffic light", "fire hydrant", "stop sign", "parking meter", "bench", "bird", "cat",
            "dog", "horse", "sheep", "cow", "elephant", "bear", "zebra", "giraffe", "backpack",
            "umbrella", "handbag", "tie", "suitcase", "frisbee", "skis", "snowboard", "sports ball",
            "kite", "baseball bat", "baseball glove", "skateboard", "surfboard", "tennis racket",
            "bottle", "wine glass", "cup", "fork", "knife", "spoon", "bowl", "banana", "apple",
            "sandwich", "orange", "broccoli", "carrot", "hot dog", "pizza", "donut", "cake", "chair",
            "couch", "potted plant", "bed", "dining table", "toilet", "tv", "laptop", "mouse",
            "remote", "keyboard", "cell phone", "microwave", "oven", "toaster", "sink", "refrigerator",
            "book", "clock", "vase", "scissors", "teddy bear", "hair drier", "toothbrush"
        ]


class SceneDetector:
    """
    Service for detecting scenes in images.
    """
    
    def __init__(
        self,
        model_path: Optional[Path] = None,
        confidence_threshold: float = 0.5,
        max_detections: int = 5
    ) -> None:
        """
        Initialize the SceneDetector.
        
        Args:
            model_path: Path to the scene detection model
            confidence_threshold: Minimum confidence threshold for detections
            max_detections: Maximum number of detections to return
        """
        self.model_path = model_path
        self.confidence_threshold = confidence_threshold
        self.max_detections = max_detections
        self._model = None
        self._labels = []
    
    def load_model(self) -> None:
        """Load the scene detection model."""
        try:
            if self.model_path and self.model_path.exists():
                # Load a saved model
                self._model = tf.keras.models.load_model(str(self.model_path))
            else:
                # Use a pre-trained model
                self._model = tf.keras.applications.ResNet50(weights="imagenet")
            
            # Load scene labels
            self._labels = self._get_scene_labels()
        
        except Exception as e:
            raise ComputerVisionError(f"Failed to load scene detection model: {e}")
    
    def detect(self, image_path: Path) -> List[SceneInfo]:
        """
        Detect scenes in an image.
        
        Args:
            image_path: Path to the image
            
        Returns:
            A list of detected scenes
        """
        try:
            # Load the model if not already loaded
            if self._model is None:
                self.load_model()
            
            # Load and preprocess the image
            img = self._load_and_preprocess_image(image_path)
            
            # Run inference
            predictions = self._model.predict(np.expand_dims(img, axis=0))
            
            # Process the predictions
            if isinstance(predictions, list):
                # For models that return multiple outputs
                class_probs = predictions[0][0]
            else:
                # For models that return a single output
                class_probs = predictions[0]
            
            # Map ImageNet classes to scene categories
            scene_probs = self._map_to_scenes(class_probs)
            
            # Get the top predictions
            scenes = []
            for label, confidence in scene_probs.items():
                if confidence >= self.confidence_threshold:
                    scenes.append(SceneInfo(label=label, confidence=confidence))
            
            # Sort by confidence and limit to max_detections
            scenes.sort(key=lambda x: x.confidence, reverse=True)
            return scenes[:self.max_detections]
        
        except Exception as e:
            raise ComputerVisionError(f"Failed to detect scenes in {image_path}: {e}")
    
    def _load_and_preprocess_image(self, image_path: Path) -> np.ndarray:
        """
        Load and preprocess an image for scene detection.
        
        Args:
            image_path: Path to the image
            
        Returns:
            The preprocessed image as a numpy array
        """
        # Load the image
        img = Image.open(image_path)
        
        # Resize the image
        img = img.resize((224, 224))
        
        # Convert to RGB if needed
        if img.mode != "RGB":
            img = img.convert("RGB")
        
        # Convert to numpy array
        img_array = np.array(img)
        
        # Preprocess for TensorFlow models
        img_array = tf.keras.applications.resnet50.preprocess_input(img_array)
        
        return img_array
    
    def _map_to_scenes(self, class_probs: np.ndarray) -> Dict[str, float]:
        """
        Map ImageNet class probabilities to scene categories.
        
        Args:
            class_probs: Class probabilities from the model
            
        Returns:
            A dictionary mapping scene labels to confidence scores
        """
        # This is a simplified mapping from ImageNet classes to scene categories
        scene_probs = {}
        
        # Get the top ImageNet classes
        top_indices = np.argsort(class_probs)[-10:][::-1]
        
        for idx in top_indices:
            if idx < len(self._labels):
                scene_label = self._labels[idx]
                scene_probs[scene_label] = float(class_probs[idx])
        
        return scene_probs
    
    def _get_scene_labels(self) -> List[str]:
        """
        Get the scene class labels.
        
        Returns:
            A list of scene labels
        """
        # This is a simplified list of scene labels
        return [
            "beach", "mountain", "forest", "city", "desert", "field", "lake", "ocean", "river",
            "street", "sunset", "sunrise", "night", "indoor", "outdoor", "building", "house",
            "office", "restaurant", "park", "garden", "playground", "stadium", "airport", "station",
            "bridge", "harbor", "waterfall", "snow", "rain", "fog", "cloudy", "sunny"
        ]


class DetectionService:
    """
    Service for detecting objects and scenes in images.
    """
    
    def __init__(
        self,
        model_dir: Optional[Path] = None,
        object_threshold: float = 0.5,
        scene_threshold: float = 0.5
    ) -> None:
        """
        Initialize the DetectionService.
        
        Args:
            model_dir: Directory containing the detection models
            object_threshold: Confidence threshold for object detection
            scene_threshold: Confidence threshold for scene detection
        """
        self.model_dir = model_dir or Path.home() / ".photo_organizer" / "models"
        
        # Create object and scene detectors
        object_model_path = self.model_dir / "object_detection" if self.model_dir else None
        scene_model_path = self.model_dir / "scene_detection" if self.model_dir else None
        
        self.object_detector = ObjectDetector(
            model_path=object_model_path,
            confidence_threshold=object_threshold
        )
        
        self.scene_detector = SceneDetector(
            model_path=scene_model_path,
            confidence_threshold=scene_threshold
        )
    
    def detect_objects(self, image_path: Path) -> List[ObjectInfo]:
        """
        Detect objects in an image.
        
        Args:
            image_path: Path to the image
            
        Returns:
            A list of detected objects
        """
        return self.object_detector.detect(image_path)
    
    def detect_scenes(self, image_path: Path) -> List[SceneInfo]:
        """
        Detect scenes in an image.
        
        Args:
            image_path: Path to the image
            
        Returns:
            A list of detected scenes
        """
        return self.scene_detector.detect(image_path)
    
    def analyze_image(self, image_path: Path) -> Tuple[List[ObjectInfo], List[SceneInfo]]:
        """
        Analyze an image to detect objects and scenes.
        
        Args:
            image_path: Path to the image
            
        Returns:
            A tuple of (objects, scenes)
        """
        objects = self.detect_objects(image_path)
        scenes = self.detect_scenes(image_path)
        return objects, scenes