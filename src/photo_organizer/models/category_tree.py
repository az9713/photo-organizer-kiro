"""
CategoryTree model for hierarchical organization of categories.
"""

from __future__ import annotations

from typing import Dict, List, Optional, Set, Tuple

from photo_organizer.models.category import Category


class CategoryTree:
    """
    Manages a hierarchical tree of categories for organizing images.
    """

    def __init__(self) -> None:
        """Initialize an empty category tree."""
        self._categories: Dict[str, Category] = {}
        self._root_categories: Set[str] = set()

    @property
    def categories(self) -> Dict[str, Category]:
        """Get all categories in the tree."""
        return self._categories.copy()

    @property
    def root_categories(self) -> List[Category]:
        """Get all root categories (categories without parents)."""
        return [self._categories[cat_id] for cat_id in self._root_categories]

    def add_category(self, category: Category) -> None:
        """
        Add a category to the tree.
        
        Args:
            category: The category to add
        """
        if category.id in self._categories:
            raise ValueError(f"Category with ID {category.id} already exists")
        
        self._categories[category.id] = category
        
        if category.parent_id is None:
            self._root_categories.add(category.id)
        elif category.parent_id in self._categories:
            parent = self._categories[category.parent_id]
            parent.child_ids.add(category.id)
        else:
            # If parent doesn't exist yet, add as root temporarily
            self._root_categories.add(category.id)

    def get_category(self, category_id: str) -> Optional[Category]:
        """
        Get a category by its ID.
        
        Args:
            category_id: The ID of the category to get
            
        Returns:
            The category with the given ID, or None if not found
        """
        return self._categories.get(category_id)

    def remove_category(self, category_id: str) -> None:
        """
        Remove a category from the tree.
        
        Args:
            category_id: The ID of the category to remove
        """
        if category_id not in self._categories:
            return
        
        category = self._categories[category_id]
        
        # Update parent's child_ids if parent exists
        if category.parent_id and category.parent_id in self._categories:
            parent = self._categories[category.parent_id]
            if category_id in parent.child_ids:
                parent.child_ids.remove(category_id)
        
        # Update children's parent_id
        for child_id in list(category.child_ids):
            if child_id in self._categories:
                child = self._categories[child_id]
                child.parent_id = None
                self._root_categories.add(child_id)
        
        # Remove from root categories if it's a root
        if category_id in self._root_categories:
            self._root_categories.remove(category_id)
        
        # Remove from categories dictionary
        del self._categories[category_id]

    def get_category_path(self, category_id: str) -> List[Category]:
        """
        Get the path from the root to the specified category.
        
        Args:
            category_id: The ID of the category
            
        Returns:
            A list of categories from the root to the specified category
        """
        if category_id not in self._categories:
            return []
        
        category = self._categories[category_id]
        return category.get_path(self._categories)

    def get_category_depth(self, category_id: str) -> int:
        """
        Get the depth of a category in the tree.
        
        Args:
            category_id: The ID of the category
            
        Returns:
            The depth of the category (0 for root categories)
        """
        path = self.get_category_path(category_id)
        return len(path) - 1 if path else -1

    def add_image_to_category(self, image_id: str, category_id: str) -> None:
        """
        Add an image to a category.
        
        Args:
            image_id: The ID of the image to add
            category_id: The ID of the category to add the image to
        """
        if category_id not in self._categories:
            raise ValueError(f"Category with ID {category_id} does not exist")
        
        category = self._categories[category_id]
        category.add_image(image_id)

    def remove_image_from_category(self, image_id: str, category_id: str) -> None:
        """
        Remove an image from a category.
        
        Args:
            image_id: The ID of the image to remove
            category_id: The ID of the category to remove the image from
        """
        if category_id not in self._categories:
            return
        
        category = self._categories[category_id]
        category.remove_image(image_id)

    def get_categories_for_image(self, image_id: str) -> List[Category]:
        """
        Get all categories that contain the specified image.
        
        Args:
            image_id: The ID of the image
            
        Returns:
            A list of categories that contain the image
        """
        return [
            category for category in self._categories.values()
            if image_id in category.image_ids
        ]

    def get_all_images(self) -> Set[str]:
        """
        Get all image IDs in the tree.
        
        Returns:
            A set of all image IDs in the tree
        """
        all_images = set()
        for category in self._categories.values():
            all_images.update(category.image_ids)
        return all_images

    def get_category_hierarchy(self) -> List[Tuple[Category, int]]:
        """
        Get the category hierarchy as a flat list with depth information.
        
        Returns:
            A list of tuples containing (category, depth)
        """
        result = []
        
        def traverse(category_id: str, depth: int) -> None:
            if category_id not in self._categories:
                return
            
            category = self._categories[category_id]
            result.append((category, depth))
            
            for child_id in sorted(category.child_ids):
                traverse(child_id, depth + 1)
        
        for root_id in sorted(self._root_categories):
            traverse(root_id, 0)
        
        return result

    def merge_categories(self, source_id: str, target_id: str) -> None:
        """
        Merge the source category into the target category.
        
        Args:
            source_id: The ID of the source category
            target_id: The ID of the target category
        """
        if source_id not in self._categories or target_id not in self._categories:
            raise ValueError("Both source and target categories must exist")
        
        if source_id == target_id:
            return
        
        source = self._categories[source_id]
        target = self._categories[target_id]
        
        # Move images from source to target
        for image_id in source.image_ids:
            target.add_image(image_id)
        
        # Move children from source to target
        for child_id in list(source.child_ids):
            if child_id in self._categories:
                child = self._categories[child_id]
                source.remove_child(child)
                target.add_child(child)
        
        # Remove the source category
        self.remove_category(source_id)

    def optimize_hierarchy(self, min_images_per_category: int = 1) -> None:
        """
        Optimize the category hierarchy by merging small categories.
        
        Args:
            min_images_per_category: Minimum number of images a category should have
        """
        # Find categories with fewer images than the minimum
        small_categories = [
            cat_id for cat_id, category in self._categories.items()
            if len(category.image_ids) < min_images_per_category and not category.child_ids
        ]
        
        for cat_id in small_categories:
            if cat_id not in self._categories:
                continue  # Category might have been removed in a previous iteration
            
            category = self._categories[cat_id]
            
            # If it has a parent, merge with parent
            if category.parent_id and category.parent_id in self._categories:
                self.merge_categories(cat_id, category.parent_id)
            # Otherwise, find a sibling or create a generic category
            elif len(self._categories) > 1:
                # Find another category to merge with
                for other_id, other in self._categories.items():
                    if other_id != cat_id and not other.child_ids:
                        self.merge_categories(cat_id, other_id)
                        break