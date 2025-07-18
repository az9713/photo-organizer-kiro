"""
Base classes for computer vision services.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union


class ComputerVisionError(Exception):
    """Exception raised for computer vision errors."""
    pass


@dataclass
class ObjectInfo:
    """Information about a detected object."""
    label: str
    confidence: float
    bounding_box: Optional[Tuple[float, float, float, float]] = None  # (x, y, width, height)


@dataclass
class SceneInfo:
    """Information about a detected scene."""
    label: str
    confidence: float


@dataclass
class FaceInfo:
    """Information about a detected face."""
    confidence: float
    bounding_box: Tuple[float, float, float, float]  # (x, y, width, height)
    landmarks: Optional[Dict[str, Tuple[float, float]]] = None  # e.g., {"left_eye": (x, y)}


class ComputerVisionService(ABC):
    """
    Abstract base class for computer vision services.
    """
    
    @abstractmethod
    def detect_objects(self, image_path: Path) -> List[ObjectInfo]:
        """
        Detect objects in an image.
        
        Args:
            image_path: The path to the image
            
        Returns:
            A list of detected objects
        """
        pass
    
    @abstractmethod
    def detect_scenes(self, image_path: Path) -> List[SceneInfo]:
        """
        Detect scenes in an image.
        
        Args:
            image_path: The path to the image
            
        Returns:
            A list of detected scenes
        """
        pass
    
    @abstractmethod
    def detect_faces(self, image_path: Path) -> List[FaceInfo]:
        """
        Detect faces in an image.
        
        Args:
            image_path: The path to the image
            
        Returns:
            A list of detected faces
        """
        pass
    
    @abstractmethod
    def generate_tags(self, image_path: Path) -> List[str]:
        """
        Generate tags for an image.
        
        Args:
            image_path: The path to the image
            
        Returns:
            A list of tags
        """
        pass
    
    @abstractmethod
    def analyze_similarity(self, image_path1: Path, image_path2: Path) -> float:
        """
        Analyze the similarity between two images.
        
        Args:
            image_path1: The path to the first image
            image_path2: The path to the second image
            
        Returns:
            A similarity score between 0 and 1
        """
        pass