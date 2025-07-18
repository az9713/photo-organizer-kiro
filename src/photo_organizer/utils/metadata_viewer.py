"""
Utility for viewing image metadata.
"""

import argparse
import sys
from pathlib import Path

from photo_organizer.services.metadata_extractor import (
    ExifMetadataExtractor,
    MetadataExtractionError,
)


def view_metadata(path: Path) -> None:
    """
    View the metadata of an image file.
    
    Args:
        path: The path to the image file
    """
    extractor = ExifMetadataExtractor()
    
    try:
        metadata = extractor.extract_metadata(path)
        
        print(f"Metadata for {path}:")
        print("-" * 40)
        
        # Print timestamp
        if metadata.timestamp:
            print(f"Timestamp: {metadata.formatted_timestamp}")
        else:
            print("Timestamp: Not available")
        
        # Print geolocation
        if metadata.geolocation:
            print(f"Geolocation:")
            print(f"  Latitude: {metadata.geolocation.latitude}")
            print(f"  Longitude: {metadata.geolocation.longitude}")
            if metadata.geolocation.formatted_address:
                print(f"  Address: {metadata.geolocation.formatted_address}")
        else:
            print("Geolocation: Not available")
        
        # Print camera info
        print("Camera Info:")
        if metadata.camera_make:
            print(f"  Make: {metadata.camera_make}")
        if metadata.camera_model:
            print(f"  Model: {metadata.camera_model}")
        if metadata.exposure_time:
            print(f"  Exposure Time: {metadata.exposure_time} sec")
        if metadata.aperture:
            print(f"  Aperture: f/{metadata.aperture}")
        if metadata.iso:
            print(f"  ISO: {metadata.iso}")
        if metadata.focal_length:
            print(f"  Focal Length: {metadata.focal_length} mm")
        
        if not any([metadata.camera_make, metadata.camera_model, metadata.exposure_time,
                   metadata.aperture, metadata.iso, metadata.focal_length]):
            print("  Not available")
    
    except MetadataExtractionError as e:
        print(f"Error: {e}")


def main() -> int:
    """Main entry point for the metadata viewer utility."""
    parser = argparse.ArgumentParser(description="View image metadata")
    parser.add_argument("paths", nargs="+", help="Paths to image files")
    
    args = parser.parse_args()
    
    for path_str in args.paths:
        path = Path(path_str)
        if path.exists():
            view_metadata(path)
        else:
            print(f"File not found: {path}")
        
        # Add a separator between files
        if len(args.paths) > 1:
            print("\n" + "=" * 40 + "\n")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())