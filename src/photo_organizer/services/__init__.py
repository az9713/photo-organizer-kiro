"""
Services for the Photo Organizer application.
"""

from photo_organizer.services.analysis import (
    AnalysisError,
    DefaultImageAnalysisEngine,
    ImageAnalysisEngine,
    ImageAnalysisService,
)
from photo_organizer.services.file_operations import FileOperationResult, FileOperations
from photo_organizer.services.file_system_manager import (
    DefaultFileSystemManager,
    FileSystemError,
    FileSystemManager,
)
from photo_organizer.services.geolocation import (
    GeocodingError,
    GeocodingService,
    MockGeocodingService,
    NominatimGeocodingService,
)
from photo_organizer.services.image_format import ImageFormatError, ImageFormatService
from photo_organizer.services.metadata_extractor import (
    ExifMetadataExtractor,
    MetadataExtractionError,
    MetadataExtractor,
)
from photo_organizer.services.vision import (
    ComputerVisionError,
    ComputerVisionService,
    FaceInfo,
    ObjectInfo,
    SceneInfo,
    TensorFlowVisionService,
)

__all__ = [
    "FileSystemManager",
    "DefaultFileSystemManager",
    "FileSystemError",
    "FileOperations",
    "FileOperationResult",
    "ImageFormatService",
    "ImageFormatError",
    "MetadataExtractor",
    "ExifMetadataExtractor",
    "MetadataExtractionError",
    "GeocodingService",
    "NominatimGeocodingService",
    "MockGeocodingService",
    "GeocodingError",
    "ComputerVisionService",
    "TensorFlowVisionService",
    "ComputerVisionError",
    "ObjectInfo",
    "SceneInfo",
    "FaceInfo",
    "ImageAnalysisEngine",
    "DefaultImageAnalysisEngine",
    "ImageAnalysisService",
    "AnalysisError",
]