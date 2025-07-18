"""
Image similarity analysis services.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

import numpy as np
import tensorflow as tf
from PIL import Image
from scipy.spatial.distance import cosine

from photo_organizer.services.vision.base import ComputerVisionError


class FeatureExtractor:
    """
    Service for extracting features from images.
    """
    
    def __init__(self, model_path: Optional[Path] = None) -> None:
        """
        Initialize the FeatureExtractor.
        
        Args:
            model_path: Path to the feature extraction model
        """
        self.model_path = model_path
        self._model = None
    
    def load_model(self) -> None:
        """Load the feature extraction model."""
        try:
            if self.model_path and self.model_path.exists():
                # Load a saved model
                self._model = tf.keras.models.load_model(str(self.model_path))
            else:
                # Use a pre-trained model
                self._model = tf.keras.applications.MobileNetV2(
                    include_top=False,
                    weights="imagenet",
                    input_shape=(224, 224, 3),
                    pooling="avg"
                )
        
        except Exception as e:
            raise ComputerVisionError(f"Failed to load feature extraction model: {e}")
    
    def extract_features(self, image_path: Path) -> np.ndarray:
        """
        Extract features from an image.
        
        Args:
            image_path: Path to the image
            
        Returns:
            The extracted features as a numpy array
        """
        try:
            # Load the model if not already loaded
            if self._model is None:
                self.load_model()
            
            # Load and preprocess the image
            img = self._load_and_preprocess_image(image_path)
            
            # Extract features
            features = self._model.predict(np.expand_dims(img, axis=0))
            
            # Flatten the features
            features = features.flatten()
            
            # Normalize the features
            features = features / np.linalg.norm(features)
            
            return features
        
        except Exception as e:
            raise ComputerVisionError(f"Failed to extract features from {image_path}: {e}")
    
    def _load_and_preprocess_image(self, image_path: Path) -> np.ndarray:
        """
        Load and preprocess an image for feature extraction.
        
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


class SimilarityAnalyzer:
    """
    Service for analyzing similarity between images.
    """
    
    def __init__(self, feature_extractor: Optional[FeatureExtractor] = None) -> None:
        """
        Initialize the SimilarityAnalyzer.
        
        Args:
            feature_extractor: The feature extractor to use
        """
        self.feature_extractor = feature_extractor or FeatureExtractor()
    
    def compute_similarity(self, image_path1: Path, image_path2: Path) -> float:
        """
        Compute the similarity between two images.
        
        Args:
            image_path1: Path to the first image
            image_path2: Path to the second image
            
        Returns:
            A similarity score between 0 and 1
        """
        try:
            # Extract features from both images
            features1 = self.feature_extractor.extract_features(image_path1)
            features2 = self.feature_extractor.extract_features(image_path2)
            
            # Calculate cosine similarity
            similarity = 1 - cosine(features1, features2)
            
            # Ensure the similarity is between 0 and 1
            similarity = max(0, min(1, similarity))
            
            return float(similarity)
        
        except Exception as e:
            raise ComputerVisionError(f"Failed to compute similarity between {image_path1} and {image_path2}: {e}")
    
    def find_similar_images(
        self, target_image: Path, image_paths: List[Path], threshold: float = 0.8
    ) -> List[Tuple[Path, float]]:
        """
        Find images similar to a target image.
        
        Args:
            target_image: Path to the target image
            image_paths: Paths to the images to compare
            threshold: Similarity threshold (0-1)
            
        Returns:
            A list of tuples (image_path, similarity) for similar images
        """
        try:
            # Extract features from the target image
            target_features = self.feature_extractor.extract_features(target_image)
            
            # Compare with each image
            similar_images = []
            for path in image_paths:
                if path == target_image:
                    continue
                
                # Extract features
                features = self.feature_extractor.extract_features(path)
                
                # Calculate similarity
                similarity = 1 - cosine(target_features, features)
                similarity = max(0, min(1, similarity))
                
                # Add to results if above threshold
                if similarity >= threshold:
                    similar_images.append((path, similarity))
            
            # Sort by similarity (highest first)
            similar_images.sort(key=lambda x: x[1], reverse=True)
            
            return similar_images
        
        except Exception as e:
            raise ComputerVisionError(f"Failed to find similar images to {target_image}: {e}")
    
    def cluster_images(
        self, image_paths: List[Path], threshold: float = 0.8
    ) -> List[List[Path]]:
        """
        Cluster images based on similarity.
        
        Args:
            image_paths: Paths to the images to cluster
            threshold: Similarity threshold (0-1)
            
        Returns:
            A list of clusters, where each cluster is a list of image paths
        """
        try:
            # Extract features for all images
            features_map = {}
            for path in image_paths:
                features = self.feature_extractor.extract_features(path)
                features_map[path] = features
            
            # Initialize clusters
            clusters = []
            remaining_images = set(image_paths)
            
            # Process each image
            while remaining_images:
                # Take the first remaining image as a seed
                seed = next(iter(remaining_images))
                remaining_images.remove(seed)
                
                # Create a new cluster with the seed
                cluster = [seed]
                seed_features = features_map[seed]
                
                # Find similar images
                for path in list(remaining_images):
                    features = features_map[path]
                    
                    # Calculate similarity
                    similarity = 1 - cosine(seed_features, features)
                    similarity = max(0, min(1, similarity))
                    
                    # Add to cluster if above threshold
                    if similarity >= threshold:
                        cluster.append(path)
                        remaining_images.remove(path)
                
                # Add the cluster to the results
                clusters.append(cluster)
            
            return clusters
        
        except Exception as e:
            raise ComputerVisionError(f"Failed to cluster images: {e}")


class ImageSimilarityService:
    """
    Service for image similarity analysis.
    """
    
    def __init__(self, model_dir: Optional[Path] = None) -> None:
        """
        Initialize the ImageSimilarityService.
        
        Args:
            model_dir: Directory containing the feature extraction model
        """
        self.model_dir = model_dir or Path.home() / ".photo_organizer" / "models"
        
        # Create feature extractor
        model_path = self.model_dir / "feature_extraction" if self.model_dir else None
        self.feature_extractor = FeatureExtractor(model_path=model_path)
        
        # Create similarity analyzer
        self.similarity_analyzer = SimilarityAnalyzer(feature_extractor=self.feature_extractor)
    
    def compute_similarity(self, image_path1: Path, image_path2: Path) -> float:
        """
        Compute the similarity between two images.
        
        Args:
            image_path1: Path to the first image
            image_path2: Path to the second image
            
        Returns:
            A similarity score between 0 and 1
        """
        return self.similarity_analyzer.compute_similarity(image_path1, image_path2)
    
    def find_similar_images(
        self, target_image: Path, image_paths: List[Path], threshold: float = 0.8
    ) -> List[Tuple[Path, float]]:
        """
        Find images similar to a target image.
        
        Args:
            target_image: Path to the target image
            image_paths: Paths to the images to compare
            threshold: Similarity threshold (0-1)
            
        Returns:
            A list of tuples (image_path, similarity) for similar images
        """
        return self.similarity_analyzer.find_similar_images(target_image, image_paths, threshold)
    
    def cluster_images(
        self, image_paths: List[Path], threshold: float = 0.8
    ) -> List[List[Path]]:
        """
        Cluster images based on similarity.
        
        Args:
            image_paths: Paths to the images to cluster
            threshold: Similarity threshold (0-1)
            
        Returns:
            A list of clusters, where each cluster is a list of image paths
        """
        return self.similarity_analyzer.cluster_images(image_paths, threshold)