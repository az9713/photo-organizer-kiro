"""
Unit tests for the CategoryTree model.
"""

import pytest

from photo_organizer.models.category import Category
from photo_organizer.models.category_tree import CategoryTree


class TestCategoryTree:
    """Tests for the CategoryTree class."""

    def test_init(self) -> None:
        """Test initializing a CategoryTree object."""
        tree = CategoryTree()
        assert tree.categories == {}
        assert tree.root_categories == []

    def test_add_category(self) -> None:
        """Test adding a category to the tree."""
        tree = CategoryTree()
        category = Category(name="Test Category")
        
        tree.add_category(category)
        
        assert category.id in tree.categories
        assert category in tree.root_categories

    def test_add_duplicate_category(self) -> None:
        """Test adding a duplicate category to the tree."""
        tree = CategoryTree()
        category = Category(name="Test Category")
        
        tree.add_category(category)
        
        with pytest.raises(ValueError):
            tree.add_category(category)

    def test_add_category_with_parent(self) -> None:
        """Test adding a category with a parent to the tree."""
        tree = CategoryTree()
        parent = Category(name="Parent")
        child = Category(name="Child")
        
        tree.add_category(parent)
        child.parent_id = parent.id
        tree.add_category(child)
        
        assert parent.id in tree.categories
        assert child.id in tree.categories
        assert parent in tree.root_categories
        assert child not in tree.root_categories
        assert child.id in parent.child_ids

    def test_get_category(self) -> None:
        """Test getting a category by ID."""
        tree = CategoryTree()
        category = Category(name="Test Category")
        
        tree.add_category(category)
        
        retrieved = tree.get_category(category.id)
        assert retrieved == category
        
        nonexistent = tree.get_category("nonexistent")
        assert nonexistent is None

    def test_remove_category(self) -> None:
        """Test removing a category from the tree."""
        tree = CategoryTree()
        category = Category(name="Test Category")
        
        tree.add_category(category)
        tree.remove_category(category.id)
        
        assert category.id not in tree.categories
        assert category not in tree.root_categories

    def test_remove_category_with_children(self) -> None:
        """Test removing a category that has children."""
        tree = CategoryTree()
        parent = Category(name="Parent")
        child = Category(name="Child")
        
        tree.add_category(parent)
        child.parent_id = parent.id
        parent.child_ids.add(child.id)
        tree.add_category(child)
        
        tree.remove_category(parent.id)
        
        assert parent.id not in tree.categories
        assert child.id in tree.categories
        assert child in tree.root_categories
        assert child.parent_id is None

    def test_get_category_path(self) -> None:
        """Test getting the path from root to a category."""
        tree = CategoryTree()
        root = Category(name="Root")
        parent = Category(name="Parent")
        child = Category(name="Child")
        
        tree.add_category(root)
        
        parent.parent_id = root.id
        root.child_ids.add(parent.id)
        tree.add_category(parent)
        
        child.parent_id = parent.id
        parent.child_ids.add(child.id)
        tree.add_category(child)
        
        path = tree.get_category_path(child.id)
        
        assert len(path) == 3
        assert path[0].name == "Root"
        assert path[1].name == "Parent"
        assert path[2].name == "Child"

    def test_get_category_depth(self) -> None:
        """Test getting the depth of a category in the tree."""
        tree = CategoryTree()
        root = Category(name="Root")
        parent = Category(name="Parent")
        child = Category(name="Child")
        
        tree.add_category(root)
        
        parent.parent_id = root.id
        root.child_ids.add(parent.id)
        tree.add_category(parent)
        
        child.parent_id = parent.id
        parent.child_ids.add(child.id)
        tree.add_category(child)
        
        assert tree.get_category_depth(root.id) == 0
        assert tree.get_category_depth(parent.id) == 1
        assert tree.get_category_depth(child.id) == 2
        assert tree.get_category_depth("nonexistent") == -1

    def test_add_image_to_category(self) -> None:
        """Test adding an image to a category."""
        tree = CategoryTree()
        category = Category(name="Test Category")
        
        tree.add_category(category)
        tree.add_image_to_category("image-id", category.id)
        
        assert "image-id" in category.image_ids

    def test_add_image_to_nonexistent_category(self) -> None:
        """Test adding an image to a non-existent category."""
        tree = CategoryTree()
        
        with pytest.raises(ValueError):
            tree.add_image_to_category("image-id", "nonexistent")

    def test_remove_image_from_category(self) -> None:
        """Test removing an image from a category."""
        tree = CategoryTree()
        category = Category(name="Test Category")
        
        tree.add_category(category)
        tree.add_image_to_category("image-id", category.id)
        tree.remove_image_from_category("image-id", category.id)
        
        assert "image-id" not in category.image_ids

    def test_get_categories_for_image(self) -> None:
        """Test getting all categories that contain an image."""
        tree = CategoryTree()
        category1 = Category(name="Category 1")
        category2 = Category(name="Category 2")
        
        tree.add_category(category1)
        tree.add_category(category2)
        
        tree.add_image_to_category("image-id", category1.id)
        tree.add_image_to_category("image-id", category2.id)
        
        categories = tree.get_categories_for_image("image-id")
        
        assert len(categories) == 2
        assert category1 in categories
        assert category2 in categories

    def test_get_all_images(self) -> None:
        """Test getting all images in the tree."""
        tree = CategoryTree()
        category1 = Category(name="Category 1")
        category2 = Category(name="Category 2")
        
        tree.add_category(category1)
        tree.add_category(category2)
        
        tree.add_image_to_category("image1", category1.id)
        tree.add_image_to_category("image2", category1.id)
        tree.add_image_to_category("image3", category2.id)
        
        all_images = tree.get_all_images()
        
        assert all_images == {"image1", "image2", "image3"}

    def test_get_category_hierarchy(self) -> None:
        """Test getting the category hierarchy."""
        tree = CategoryTree()
        root = Category(name="Root")
        parent1 = Category(name="Parent 1")
        parent2 = Category(name="Parent 2")
        child1 = Category(name="Child 1")
        child2 = Category(name="Child 2")
        
        tree.add_category(root)
        
        parent1.parent_id = root.id
        root.child_ids.add(parent1.id)
        tree.add_category(parent1)
        
        parent2.parent_id = root.id
        root.child_ids.add(parent2.id)
        tree.add_category(parent2)
        
        child1.parent_id = parent1.id
        parent1.child_ids.add(child1.id)
        tree.add_category(child1)
        
        child2.parent_id = parent2.id
        parent2.child_ids.add(child2.id)
        tree.add_category(child2)
        
        hierarchy = tree.get_category_hierarchy()
        
        assert len(hierarchy) == 5
        assert hierarchy[0][0] == root
        assert hierarchy[0][1] == 0  # depth
        
        # Check that all categories are in the hierarchy
        categories = [item[0] for item in hierarchy]
        assert root in categories
        assert parent1 in categories
        assert parent2 in categories
        assert child1 in categories
        assert child2 in categories
        
        # Check depths
        depths = {item[0].name: item[1] for item in hierarchy}
        assert depths["Root"] == 0
        assert depths["Parent 1"] == 1
        assert depths["Parent 2"] == 1
        assert depths["Child 1"] == 2
        assert depths["Child 2"] == 2

    def test_merge_categories(self) -> None:
        """Test merging two categories."""
        tree = CategoryTree()
        source = Category(name="Source")
        target = Category(name="Target")
        child = Category(name="Child")
        
        tree.add_category(source)
        tree.add_category(target)
        
        source.add_child(child)
        tree.add_category(child)
        
        tree.add_image_to_category("image1", source.id)
        tree.add_image_to_category("image2", source.id)
        
        tree.merge_categories(source.id, target.id)
        
        # Source should be removed
        assert source.id not in tree.categories
        
        # Target should have the images from source
        assert "image1" in target.image_ids
        assert "image2" in target.image_ids
        
        # Child should now be a child of target
        assert child.parent_id == target.id
        assert child.id in target.child_ids

    def test_optimize_hierarchy(self) -> None:
        """Test optimizing the category hierarchy."""
        tree = CategoryTree()
        parent = Category(name="Parent")
        child1 = Category(name="Child 1")
        child2 = Category(name="Child 2")
        
        tree.add_category(parent)
        
        child1.parent_id = parent.id
        parent.child_ids.add(child1.id)
        tree.add_category(child1)
        
        child2.parent_id = parent.id
        parent.child_ids.add(child2.id)
        tree.add_category(child2)
        
        # Add images to parent and child2, but not child1
        tree.add_image_to_category("image1", parent.id)
        tree.add_image_to_category("image2", child2.id)
        
        # Optimize with min_images_per_category=1
        tree.optimize_hierarchy(min_images_per_category=1)
        
        # child1 should be merged with parent since it has no images
        assert child1.id not in tree.categories
        assert child2.id in tree.categories  # child2 has an image, so it should remain