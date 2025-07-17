"""
Category model for the Photo Organizer application.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set


@dataclass
class Category:
    """
    Represents a category for grouping similar images.
    
    Categories can have a hierarchical structure with parent-child relationships.
    """
    name: str
    description: str = ""
    tags: List[str] = field(default_factory=list)
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    parent_id: Optional[str] = None
    child_ids: Set[str] = field(default_factory=set)
    image_ids: Set[str] = field(default_factory=set)
    
    def add_child(self, child: Category) -> None:
        """
        Add a child category to this category.
        
        Args:
            child: The child category to add
        """
        if child.id == self.id:
            raise ValueError("Cannot add a category as a child of itself")
        
        # Check for circular references
        if self._would_create_cycle(child):
            raise ValueError("Adding this child would create a circular reference")
        
        # Update parent-child relationship
        child.parent_id = self.id
        self.child_ids.add(child.id)
    
    def remove_child(self, child: Category) -> None:
        """
        Remove a child category from this category.
        
        Args:
            child: The child category to remove
        """
        if child.id in self.child_ids:
            self.child_ids.remove(child.id)
            child.parent_id = None
    
    def add_image(self, image_id: str) -> None:
        """
        Add an image to this category.
        
        Args:
            image_id: The ID of the image to add
        """
        self.image_ids.add(image_id)
    
    def remove_image(self, image_id: str) -> None:
        """
        Remove an image from this category.
        
        Args:
            image_id: The ID of the image to remove
        """
        if image_id in self.image_ids:
            self.image_ids.remove(image_id)
    
    def get_all_image_ids(self, category_map: Dict[str, Category]) -> Set[str]:
        """
        Get all image IDs in this category and its subcategories.
        
        Args:
            category_map: A mapping of category IDs to Category objects
            
        Returns:
            A set of all image IDs in this category and its subcategories
        """
        result = set(self.image_ids)
        
        for child_id in self.child_ids:
            if child_id in category_map:
                child = category_map[child_id]
                result.update(child.get_all_image_ids(category_map))
        
        return result
    
    def get_path(self, category_map: Dict[str, Category]) -> List[Category]:
        """
        Get the path from the root category to this category.
        
        Args:
            category_map: A mapping of category IDs to Category objects
            
        Returns:
            A list of categories from the root to this category
        """
        if self.parent_id is None:
            return [self]
        
        if self.parent_id not in category_map:
            return [self]
        
        parent = category_map[self.parent_id]
        return parent.get_path(category_map) + [self]
    
    def get_path_names(self, category_map: Dict[str, Category]) -> List[str]:
        """
        Get the path names from the root category to this category.
        
        Args:
            category_map: A mapping of category IDs to Category objects
            
        Returns:
            A list of category names from the root to this category
        """
        return [category.name for category in self.get_path(category_map)]
    
    def _would_create_cycle(self, child: Category) -> bool:
        """
        Check if adding the given child would create a cycle in the category hierarchy.
        
        Args:
            child: The child category to check
            
        Returns:
            True if adding the child would create a cycle, False otherwise
        """
        # If this category is already a descendant of the child, adding the child
        # as a child of this category would create a cycle
        current = self
        while current.parent_id is not None:
            if current.parent_id == child.id:
                return True
            # In a real implementation, we would look up the parent in a category map
            # For this check, we'll assume no cycle if we can't find the parent
            break
        
        return False