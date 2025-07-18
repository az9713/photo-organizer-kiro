"""
Utility for analyzing and categorizing images.
"""

import argparse
import sys
from pathlib import Path

from photo_organizer.services.analysis import AnalysisError, ImageAnalysisService


def analyze_image(image_path: Path) -> None:
    """
    Analyze an image and print the results.
    
    Args:
        image_path: Path to the image
    """
    service = ImageAnalysisService()
    
    try:
        print(f"Analyzing image: {image_path}")
        print("-" * 40)
        
        # Analyze the image
        image = service.analyze_image(image_path)
        
        # Print metadata
        print("Metadata:")
        if image.metadata.timestamp:
            print(f"  Timestamp: {image.metadata.formatted_timestamp}")
        else:
            print("  Timestamp: Not available")
        
        if image.metadata.geolocation:
            print(f"  Geolocation:")
            print(f"    Latitude: {image.metadata.geolocation.latitude}")
            print(f"    Longitude: {image.metadata.geolocation.longitude}")
            if image.metadata.geolocation.formatted_address:
                print(f"    Address: {image.metadata.geolocation.formatted_address}")
        else:
            print("  Geolocation: Not available")
        
        # Print content information
        print("\nContent:")
        
        if image.objects:
            print("  Objects:")
            for obj in image.objects:
                print(f"    {obj['label']} ({obj['confidence']:.2f})")
        else:
            print("  Objects: None detected")
        
        if image.scenes:
            print("  Scenes:")
            for scene in image.scenes:
                print(f"    {scene['label']} ({scene['confidence']:.2f})")
        else:
            print("  Scenes: None detected")
        
        if image.content_tags:
            print("  Tags:")
            print(f"    {', '.join(image.content_tags)}")
        else:
            print("  Tags: None generated")
    
    except AnalysisError as e:
        print(f"Error: {e}")


def categorize_images(image_dir: Path) -> None:
    """
    Analyze and categorize images in a directory.
    
    Args:
        image_dir: Path to the directory containing images
    """
    service = ImageAnalysisService()
    
    try:
        print(f"Analyzing and categorizing images in: {image_dir}")
        print("-" * 40)
        
        # Find image files in the directory
        image_extensions = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp"}
        image_paths = [
            path for path in image_dir.glob("**/*")
            if path.is_file() and path.suffix.lower() in image_extensions
        ]
        
        if not image_paths:
            print(f"No image files found in {image_dir}")
            return
        
        print(f"Found {len(image_paths)} image files")
        
        # Analyze and categorize the images
        analyzed_images, category_tree = service.categorize_images(image_paths)
        
        print(f"Analyzed {len(analyzed_images)} images")
        
        # Print the category tree
        print("\nCategory Tree:")
        hierarchy = category_tree.get_category_hierarchy()
        
        for category, depth in hierarchy:
            indent = "  " * depth
            image_count = len(category.image_ids)
            print(f"{indent}- {category.name} ({image_count} images)")
            
            # Print the first few images in each category
            if image_count > 0:
                for i, image_id in enumerate(list(category.image_ids)[:3]):
                    print(f"{indent}  - {image_id}")
                
                if image_count > 3:
                    print(f"{indent}  - ... and {image_count - 3} more")
    
    except AnalysisError as e:
        print(f"Error: {e}")


def main() -> int:
    """Main entry point for the analysis utility."""
    parser = argparse.ArgumentParser(description="Analyze and categorize images")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Analyze command
    analyze_parser = subparsers.add_parser("analyze", help="Analyze a single image")
    analyze_parser.add_argument("image", type=str, help="Path to the image")
    
    # Categorize command
    categorize_parser = subparsers.add_parser("categorize", help="Categorize images in a directory")
    categorize_parser.add_argument("directory", type=str, help="Path to the directory containing images")
    
    args = parser.parse_args()
    
    if args.command == "analyze":
        image_path = Path(args.image)
        
        if not image_path.exists():
            print(f"Error: File not found: {image_path}")
            return 1
        
        analyze_image(image_path)
    
    elif args.command == "categorize":
        image_dir = Path(args.directory)
        
        if not image_dir.exists() or not image_dir.is_dir():
            print(f"Error: Directory not found: {image_dir}")
            return 1
        
        categorize_images(image_dir)
    
    else:
        parser.print_help()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())