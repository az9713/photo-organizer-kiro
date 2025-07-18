"""
Utility for analyzing image similarity.
"""

import argparse
import sys
from pathlib import Path

from photo_organizer.services.vision.base import ComputerVisionError
from photo_organizer.services.vision.similarity import ImageSimilarityService


def compare_images(image_path1: Path, image_path2: Path) -> None:
    """
    Compare two images and print their similarity.
    
    Args:
        image_path1: Path to the first image
        image_path2: Path to the second image
    """
    service = ImageSimilarityService()
    
    try:
        print(f"Comparing images:")
        print(f"  1: {image_path1}")
        print(f"  2: {image_path2}")
        print("-" * 40)
        
        # Compute similarity
        similarity = service.compute_similarity(image_path1, image_path2)
        
        # Print the result
        print(f"Similarity score: {similarity:.4f} ({similarity*100:.1f}%)")
        
        # Interpret the result
        if similarity > 0.9:
            print("Interpretation: Very similar images")
        elif similarity > 0.8:
            print("Interpretation: Similar images")
        elif similarity > 0.6:
            print("Interpretation: Somewhat similar images")
        else:
            print("Interpretation: Different images")
    
    except ComputerVisionError as e:
        print(f"Error: {e}")


def find_similar_images(target_image: Path, image_dir: Path, threshold: float = 0.8) -> None:
    """
    Find images similar to a target image in a directory.
    
    Args:
        target_image: Path to the target image
        image_dir: Path to the directory containing images to compare
        threshold: Similarity threshold (0-1)
    """
    service = ImageSimilarityService()
    
    try:
        print(f"Finding images similar to: {target_image}")
        print(f"In directory: {image_dir}")
        print(f"Similarity threshold: {threshold:.2f}")
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
        
        # Find similar images
        similar_images = service.find_similar_images(target_image, image_paths, threshold)
        
        # Print the results
        if similar_images:
            print(f"Found {len(similar_images)} similar images:")
            for i, (path, similarity) in enumerate(similar_images):
                print(f"  {i+1}. {path.name} - {similarity:.4f} ({similarity*100:.1f}%)")
        else:
            print("No similar images found")
    
    except ComputerVisionError as e:
        print(f"Error: {e}")


def cluster_images(image_dir: Path, threshold: float = 0.8) -> None:
    """
    Cluster images in a directory based on similarity.
    
    Args:
        image_dir: Path to the directory containing images to cluster
        threshold: Similarity threshold (0-1)
    """
    service = ImageSimilarityService()
    
    try:
        print(f"Clustering images in: {image_dir}")
        print(f"Similarity threshold: {threshold:.2f}")
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
        
        # Cluster the images
        clusters = service.cluster_images(image_paths, threshold)
        
        # Print the results
        print(f"Found {len(clusters)} clusters:")
        for i, cluster in enumerate(clusters):
            print(f"Cluster {i+1} ({len(cluster)} images):")
            for j, path in enumerate(cluster):
                print(f"  {j+1}. {path.name}")
            print()
    
    except ComputerVisionError as e:
        print(f"Error: {e}")


def main() -> int:
    """Main entry point for the similarity utility."""
    parser = argparse.ArgumentParser(description="Analyze image similarity")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Compare command
    compare_parser = subparsers.add_parser("compare", help="Compare two images")
    compare_parser.add_argument("image1", type=str, help="Path to the first image")
    compare_parser.add_argument("image2", type=str, help="Path to the second image")
    
    # Find command
    find_parser = subparsers.add_parser("find", help="Find similar images")
    find_parser.add_argument("target", type=str, help="Path to the target image")
    find_parser.add_argument("directory", type=str, help="Path to the directory containing images")
    find_parser.add_argument("--threshold", type=float, default=0.8, help="Similarity threshold (0-1)")
    
    # Cluster command
    cluster_parser = subparsers.add_parser("cluster", help="Cluster images")
    cluster_parser.add_argument("directory", type=str, help="Path to the directory containing images")
    cluster_parser.add_argument("--threshold", type=float, default=0.8, help="Similarity threshold (0-1)")
    
    args = parser.parse_args()
    
    if args.command == "compare":
        image_path1 = Path(args.image1)
        image_path2 = Path(args.image2)
        
        if not image_path1.exists():
            print(f"Error: File not found: {image_path1}")
            return 1
        
        if not image_path2.exists():
            print(f"Error: File not found: {image_path2}")
            return 1
        
        compare_images(image_path1, image_path2)
    
    elif args.command == "find":
        target_image = Path(args.target)
        image_dir = Path(args.directory)
        
        if not target_image.exists():
            print(f"Error: File not found: {target_image}")
            return 1
        
        if not image_dir.exists() or not image_dir.is_dir():
            print(f"Error: Directory not found: {image_dir}")
            return 1
        
        find_similar_images(target_image, image_dir, args.threshold)
    
    elif args.command == "cluster":
        image_dir = Path(args.directory)
        
        if not image_dir.exists() or not image_dir.is_dir():
            print(f"Error: Directory not found: {image_dir}")
            return 1
        
        cluster_images(image_dir, args.threshold)
    
    else:
        parser.print_help()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())