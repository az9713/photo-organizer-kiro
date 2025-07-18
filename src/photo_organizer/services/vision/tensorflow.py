"""
TensorFlow implementation of the computer vision service.
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
    FaceInfo,
    ObjectInfo,
    SceneInfo,
)


class TensorFlowVisionService(ComputerVisionService):
    """
    Computer vision service implementation using TensorFlow.
    """
    
    def __init__(
        self,
        model_dir: Optional[Path] = None,
        object_detection_threshold: float = 0.5,
        scene_detection_threshold: float = 0.5,
        face_detection_threshold: float = 0.5
    ) -> None:
        """
        Initialize the TensorFlowVisionService.
        
        Args:
            model_dir: Directory containing the TensorFlow models
            object_detection_threshold: Confidence threshold for object detection
            scene_detection_threshold: Confidence threshold for scene detection
            face_detection_threshold: Confidence threshold for face detection
        """
        self.model_dir = model_dir or Path.home() / ".photo_organizer" / "models"
        self.object_detection_threshold = object_detection_threshold
        self.scene_detection_threshold = scene_detection_threshold
        self.face_detection_threshold = face_detection_threshold
        
        # Create model directory if it doesn't exist
        self.model_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize models to None
        self._object_detection_model = None
        self._scene_detection_model = None
        self._face_detection_model = None
        self._feature_extraction_model = None
        
        # Initialize class labels
        self._object_labels = []
        self._scene_labels = []
    
    def detect_objects(self, image_path: Path) -> List[ObjectInfo]:
        """
        Detect objects in an image using TensorFlow.
        
        Args:
            image_path: The path to the image
            
        Returns:
            A list of detected objects
        """
        try:
            # Load the model if not already loaded
            if self._object_detection_model is None:
                self._load_object_detection_model()
            
            # Load and preprocess the image
            image = self._load_and_preprocess_image(image_path, (224, 224))
            
            # Run inference
            predictions = self._object_detection_model.predict(np.expand_dims(image, axis=0))
            
            # Process the predictions
            objects = []
            if isinstance(predictions, list):
                # For models that return multiple outputs
                class_probs = predictions[0][0]
                boxes = predictions[1][0] if len(predictions) > 1 else None
            else:
                # For models that return a single output
                class_probs = predictions[0]
                boxes = None
            
            # Get the top predictions
            top_indices = np.argsort(class_probs)[-5:]  # Top 5 predictions
            
            for idx in top_indices:
                confidence = float(class_probs[idx])
                if confidence >= self.object_detection_threshold:
                    label = self._object_labels[idx] if idx < len(self._object_labels) else f"Class_{idx}"
                    
                    # Create bounding box if available
                    bbox = None
                    if boxes is not None and idx < len(boxes):
                        # Convert from [y1, x1, y2, x2] to [x, y, width, height]
                        y1, x1, y2, x2 = boxes[idx]
                        bbox = (float(x1), float(y1), float(x2 - x1), float(y2 - y1))
                    
                    objects.append(ObjectInfo(label=label, confidence=confidence, bounding_box=bbox))
            
            return objects
        
        except Exception as e:
            raise ComputerVisionError(f"Failed to detect objects in {image_path}: {e}")
    
    def detect_scenes(self, image_path: Path) -> List[SceneInfo]:
        """
        Detect scenes in an image using TensorFlow.
        
        Args:
            image_path: The path to the image
            
        Returns:
            A list of detected scenes
        """
        try:
            # Load the model if not already loaded
            if self._scene_detection_model is None:
                self._load_scene_detection_model()
            
            # Load and preprocess the image
            image = self._load_and_preprocess_image(image_path, (224, 224))
            
            # Run inference
            predictions = self._scene_detection_model.predict(np.expand_dims(image, axis=0))
            
            # Process the predictions
            scenes = []
            class_probs = predictions[0]
            
            # Get the top predictions
            top_indices = np.argsort(class_probs)[-3:]  # Top 3 predictions
            
            for idx in top_indices:
                confidence = float(class_probs[idx])
                if confidence >= self.scene_detection_threshold:
                    label = self._scene_labels[idx] if idx < len(self._scene_labels) else f"Scene_{idx}"
                    scenes.append(SceneInfo(label=label, confidence=confidence))
            
            return scenes
        
        except Exception as e:
            raise ComputerVisionError(f"Failed to detect scenes in {image_path}: {e}")
    
    def detect_faces(self, image_path: Path) -> List[FaceInfo]:
        """
        Detect faces in an image using TensorFlow.
        
        Args:
            image_path: The path to the image
            
        Returns:
            A list of detected faces
        """
        try:
            # Load the model if not already loaded
            if self._face_detection_model is None:
                self._load_face_detection_model()
            
            # Load and preprocess the image
            image = self._load_and_preprocess_image(image_path, (224, 224))
            
            # Run inference
            predictions = self._face_detection_model.predict(np.expand_dims(image, axis=0))
            
            # Process the predictions
            faces = []
            if isinstance(predictions, list):
                # For models that return multiple outputs
                face_probs = predictions[0][0]
                boxes = predictions[1][0] if len(predictions) > 1 else None
                landmarks = predictions[2][0] if len(predictions) > 2 else None
            else:
                # For models that return a single output (bounding boxes with confidence)
                boxes = predictions[0]
                face_probs = [box[4] for box in boxes] if boxes.shape[-1] > 4 else [1.0] * len(boxes)
                landmarks = None
            
            for i, confidence in enumerate(face_probs):
                if confidence >= self.face_detection_threshold and i < len(boxes):
                    # Convert from [y1, x1, y2, x2] to [x, y, width, height]
                    if boxes.shape[-1] > 4:
                        # Format: [y1, x1, y2, x2, confidence]
                        y1, x1, y2, x2 = boxes[i][:4]
                    else:
                        # Format: [y1, x1, y2, x2]
                        y1, x1, y2, x2 = boxes[i]
                    
                    bbox = (float(x1), float(y1), float(x2 - x1), float(y2 - y1))
                    
                    # Extract landmarks if available
                    face_landmarks = None
                    if landmarks is not None and i < len(landmarks):
                        face_landmarks = {}
                        landmark_points = landmarks[i].reshape(-1, 2)
                        landmark_names = ["left_eye", "right_eye", "nose", "left_mouth", "right_mouth"]
                        
                        for j, name in enumerate(landmark_names):
                            if j < len(landmark_points):
                                face_landmarks[name] = (float(landmark_points[j][0]), float(landmark_points[j][1]))
                    
                    faces.append(FaceInfo(
                        confidence=float(confidence),
                        bounding_box=bbox,
                        landmarks=face_landmarks
                    ))
            
            return faces
        
        except Exception as e:
            raise ComputerVisionError(f"Failed to detect faces in {image_path}: {e}")
    
    def generate_tags(self, image_path: Path) -> List[str]:
        """
        Generate tags for an image using TensorFlow.
        
        Args:
            image_path: The path to the image
            
        Returns:
            A list of tags
        """
        try:
            # Combine object and scene detection results to generate tags
            objects = self.detect_objects(image_path)
            scenes = self.detect_scenes(image_path)
            
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
        
        except Exception as e:
            raise ComputerVisionError(f"Failed to generate tags for {image_path}: {e}")
    
    def analyze_similarity(self, image_path1: Path, image_path2: Path) -> float:
        """
        Analyze the similarity between two images using TensorFlow.
        
        Args:
            image_path1: The path to the first image
            image_path2: The path to the second image
            
        Returns:
            A similarity score between 0 and 1
        """
        try:
            # Load the model if not already loaded
            if self._feature_extraction_model is None:
                self._load_feature_extraction_model()
            
            # Load and preprocess the images
            image1 = self._load_and_preprocess_image(image_path1, (224, 224))
            image2 = self._load_and_preprocess_image(image_path2, (224, 224))
            
            # Extract features
            features1 = self._feature_extraction_model.predict(np.expand_dims(image1, axis=0))
            features2 = self._feature_extraction_model.predict(np.expand_dims(image2, axis=0))
            
            # Flatten the features
            features1 = features1.flatten()
            features2 = features2.flatten()
            
            # Normalize the features
            features1 = features1 / np.linalg.norm(features1)
            features2 = features2 / np.linalg.norm(features2)
            
            # Calculate cosine similarity
            similarity = np.dot(features1, features2)
            
            # Ensure the similarity is between 0 and 1
            similarity = max(0, min(1, similarity))
            
            return float(similarity)
        
        except Exception as e:
            raise ComputerVisionError(f"Failed to analyze similarity between {image_path1} and {image_path2}: {e}")
    
    def _load_object_detection_model(self) -> None:
        """Load the object detection model."""
        try:
            # Check if the model file exists
            model_path = self.model_dir / "object_detection"
            
            if not model_path.exists():
                # Download a pre-trained model
                self._download_model("object_detection")
            
            # Load the model
            self._object_detection_model = tf.keras.models.load_model(str(model_path))
            
            # Load the class labels
            labels_path = self.model_dir / "object_detection_labels.txt"
            if labels_path.exists():
                with open(labels_path, "r") as f:
                    self._object_labels = [line.strip() for line in f]
            else:
                # Use default ImageNet class labels
                self._object_labels = self._get_imagenet_labels()
        
        except Exception as e:
            raise ComputerVisionError(f"Failed to load object detection model: {e}")
    
    def _load_scene_detection_model(self) -> None:
        """Load the scene detection model."""
        try:
            # Check if the model file exists
            model_path = self.model_dir / "scene_detection"
            
            if not model_path.exists():
                # Download a pre-trained model
                self._download_model("scene_detection")
            
            # Load the model
            self._scene_detection_model = tf.keras.models.load_model(str(model_path))
            
            # Load the class labels
            labels_path = self.model_dir / "scene_detection_labels.txt"
            if labels_path.exists():
                with open(labels_path, "r") as f:
                    self._scene_labels = [line.strip() for line in f]
            else:
                # Use default scene labels
                self._scene_labels = self._get_scene_labels()
        
        except Exception as e:
            raise ComputerVisionError(f"Failed to load scene detection model: {e}")
    
    def _load_face_detection_model(self) -> None:
        """Load the face detection model."""
        try:
            # Check if the model file exists
            model_path = self.model_dir / "face_detection"
            
            if not model_path.exists():
                # Download a pre-trained model
                self._download_model("face_detection")
            
            # Load the model
            self._face_detection_model = tf.keras.models.load_model(str(model_path))
        
        except Exception as e:
            raise ComputerVisionError(f"Failed to load face detection model: {e}")
    
    def _load_feature_extraction_model(self) -> None:
        """Load the feature extraction model."""
        try:
            # Use a pre-trained model for feature extraction
            self._feature_extraction_model = tf.keras.applications.MobileNetV2(
                include_top=False,
                weights="imagenet",
                input_shape=(224, 224, 3),
                pooling="avg"
            )
        
        except Exception as e:
            raise ComputerVisionError(f"Failed to load feature extraction model: {e}")
    
    def _download_model(self, model_type: str) -> None:
        """
        Download a pre-trained model.
        
        Args:
            model_type: The type of model to download
        """
        # In a real implementation, this would download the model from a server
        # For this implementation, we'll use TensorFlow's built-in models
        
        model_path = self.model_dir / model_type
        model_path.mkdir(parents=True, exist_ok=True)
        
        if model_type == "object_detection":
            # Use MobileNetV2 for object detection
            model = tf.keras.applications.MobileNetV2(weights="imagenet")
            model.save(str(model_path))
            
            # Save the class labels
            labels_path = self.model_dir / "object_detection_labels.txt"
            with open(labels_path, "w") as f:
                for label in self._get_imagenet_labels():
                    f.write(f"{label}\n")
        
        elif model_type == "scene_detection":
            # Use ResNet50 for scene detection
            model = tf.keras.applications.ResNet50(weights="imagenet")
            model.save(str(model_path))
            
            # Save the class labels
            labels_path = self.model_dir / "scene_detection_labels.txt"
            with open(labels_path, "w") as f:
                for label in self._get_scene_labels():
                    f.write(f"{label}\n")
        
        elif model_type == "face_detection":
            # For face detection, we would normally use a specialized model
            # For this implementation, we'll use MobileNetV2 as a placeholder
            model = tf.keras.applications.MobileNetV2(weights="imagenet")
            model.save(str(model_path))
    
    def _load_and_preprocess_image(self, image_path: Path, target_size: Tuple[int, int]) -> np.ndarray:
        """
        Load and preprocess an image for TensorFlow.
        
        Args:
            image_path: The path to the image
            target_size: The target size (width, height)
            
        Returns:
            The preprocessed image as a numpy array
        """
        # Load the image
        img = Image.open(image_path)
        
        # Resize the image
        img = img.resize(target_size)
        
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