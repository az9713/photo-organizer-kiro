"""
Utility for categorizing images.
"""

import argparse
import sys
from pathlib import Path

from photo_organizer.services.categorization import (
    CategorizationError,
    CategorizationService,
    ContentBasedCategorization,
    HierarchicalClustering,
    HybridCategorization,
)


def categorize_images(
    image_dir: Path, algorithm: str = "hybrid", min_category_size: int = 3
) -> None:
    """
    Categorize images in a directory.
    
    Args:
        image_dir: Path to the directory containing images
        algorithm: The categorization algorithm to use
        min_category_size: The minimum number of images in a category
    """
    # Create the appropriate algorithm
    if algorithm == "content":
        categorization_algorithm = ContentBasedCategorization(min_category_size=min_category_size)
    elif algorithm == "clustering":
        categorization_algorithm = HierarchicalClustering(min_cluster_size=min_category_size)
    else:  # hybrid
        content_algorithm = ContentBasedCategorization(min_category_size=min_category_size)
        clustering_algorithm = HierarchicalClustering(min_cluster_size=min_category_size)
        categorization_algorithm = HybridCategorization(
            content_algorithm=content_algorithm,
            clustering_algorithm=clustering_algorithm
        )
    
    # Create the categorization service
    service = CategorizationService(algorithm=categorization_algorithm)
    
    try:
        print(f"Categorizing images in: {image_dir}")
        print(f"Using algorithm: {algorithm}")
        print(f"Minimum category size: {min_category_size}")
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
        
        # Categorize the images
        images, category_tree = service.categorize_by_path(image_paths)
        
        print(f"Categorized {len(images)} images into {len(category_tree.categories)} categories")
        
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
    
    except CategorizationError as e:
        print(f"Error: {e}")


def main() -> int:
    """Main entry point for the categorization utility."""
    parser = argparse.ArgumentParser(description="Categorize images")
    parser.add_argument("directory", type=str, help="Path to the directory containing images")
    parser.add_argument(
        "--algorithm",
        type=str,
        choices=["hybrid", "content", "clustering"],
        default="hybrid",
        help="Categorization algorithm to use"
    )
    parser.add_argument(
        "--min-category-size",
        type=int,
        default=3,
        help="Minimum number of images in a category"
    )
    
    args = parser.parse_args()
    
    image_dir = Path(args.directory)
    
    if not image_dir.exists() or not image_dir.is_dir():
        print(f"Error: Directory not found: {image_dir}")
        return 1
    
    categorize_images(image_dir, args.algorithm, args.min_category_size)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())