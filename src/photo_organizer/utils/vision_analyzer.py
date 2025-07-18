"""
Utility for analyzing images using computer vision.
"""

import argparse
import sys
from pathlib import Path

from photo_organizer.services.vision import ComputerVisionError, TensorFlowVisionService


def analyze_image(image_path: Path) -> None:
    """
    Analyze an image using computer vision and print the results.
    
    Args:
        image_path: The path to the image
    """
    service = TensorFlowVisionService()
    
    try:
        print(f"Analyzing image: {image_path}")
        print("-" * 40)
        
        # Detect objects
        print("Detecting objects...")
        objects = service.detect_objects(image_path)
        
        if objects:
            print(f"Found {len(objects)} objects:")
            for i, obj in enumerate(objects):
                print(f"  {i+1}. {obj.label} ({obj.confidence:.2f})")
        else:
            print("No objects detected.")
        
        print()
        
        # Detect scenes
        print("Detecting scenes...")
        scenes = service.detect_scenes(image_path)
        
        if scenes:
            print(f"Found {len(scenes)} scenes:")
            for i, scene in enumerate(scenes):
                print(f"  {i+1}. {scene.label} ({scene.confidence:.2f})")
        else:
            print("No scenes detected.")
        
        print()
        
        # Detect faces
        print("Detecting faces...")
        faces = service.detect_faces(image_path)
        
        if faces:
            print(f"Found {len(faces)} faces.")
        else:
            print("No faces detected.")
        
        print()
        
        # Generate tags
        print("Generating tags...")
        tags = service.generate_tags(image_path)
        
        if tags:
            print(f"Generated {len(tags)} tags:")
            print(f"  {', '.join(tags)}")
        else:
            print("No tags generated.")
    
    except ComputerVisionError as e:
        print(f"Error: {e}")


def main() -> int:
    """Main entry point for the vision analyzer utility."""
    parser = argparse.ArgumentParser(description="Analyze images using computer vision")
    parser.add_argument("paths", nargs="+", help="Paths to image files")
    
    args = parser.parse_args()
    
    for path_str in args.paths:
        path = Path(path_str)
        if path.exists():
            analyze_image(path)
        else:
            print(f"File not found: {path}")
        
        # Add a separator between files
        if len(args.paths) > 1:
            print("\n" + "=" * 40 + "\n")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())