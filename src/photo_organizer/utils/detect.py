"""
Utility for detecting objects and scenes in images.
"""

import argparse
import sys
from pathlib import Path

from photo_organizer.services.vision.detection import (
    ComputerVisionError,
    DetectionService,
)


def detect_image_content(image_path: Path) -> None:
    """
    Detect objects and scenes in an image and print the results.
    
    Args:
        image_path: The path to the image
    """
    service = DetectionService()
    
    try:
        print(f"Analyzing image: {image_path}")
        print("-" * 40)
        
        # Analyze the image
        objects, scenes = service.analyze_image(image_path)
        
        # Print detected objects
        if objects:
            print(f"Detected {len(objects)} objects:")
            for i, obj in enumerate(objects):
                print(f"  {i+1}. {obj.label} ({obj.confidence:.2f})")
        else:
            print("No objects detected.")
        
        print()
        
        # Print detected scenes
        if scenes:
            print(f"Detected {len(scenes)} scenes:")
            for i, scene in enumerate(scenes):
                print(f"  {i+1}. {scene.label} ({scene.confidence:.2f})")
        else:
            print("No scenes detected.")
        
        # Generate tags
        tags = [obj.label for obj in objects] + [scene.label for scene in scenes]
        tags = list(set(tags))  # Remove duplicates
        
        print()
        print(f"Generated {len(tags)} tags:")
        print(f"  {', '.join(tags)}")
    
    except ComputerVisionError as e:
        print(f"Error: {e}")


def main() -> int:
    """Main entry point for the detection utility."""
    parser = argparse.ArgumentParser(description="Detect objects and scenes in images")
    parser.add_argument("paths", nargs="+", help="Paths to image files")
    
    args = parser.parse_args()
    
    for path_str in args.paths:
        path = Path(path_str)
        if path.exists():
            detect_image_content(path)
        else:
            print(f"File not found: {path}")
        
        # Add a separator between files
        if len(args.paths) > 1:
            print("\n" + "=" * 40 + "\n")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())