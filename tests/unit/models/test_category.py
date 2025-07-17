"""
Unit tests for the Category model.
"""

import pytest

from photo_organizer.models.category import Category


class TestCategory:
    """Tests for the Category class."""

    def test_init(self) -> None:
        """Test initializing a Category object."""
        category = Category(name="Vacation")
        assert category.name == "Vacation"
        assert category.description == ""
        assert category.tags == []
        assert category.id is not None
        assert category.parent_id is None
        assert category.child_ids == set()
        assert category.image_ids == set()

    def test_init_with_all_fields(self) -> None:
        """Test initializing a Category object with all fields."""
        category = Category(
            name="Vacation",
            description="Summer vacation photos",
            tags=["summer", "beach", "family"],
            id="test-id",
            parent_id="parent-id",
            child_ids={"child-id-1", "child-id-2"},
            image_ids={"image-id-1", "image-id-2"}
        )
        assert category.name == "Vacation"
        assert category.description == "Summer vacation photos"
        assert category.tags == ["summer", "beach", "family"]
        assert category.id == "test-id"
        assert category.parent_id == "parent-id"
        assert category.child_ids == {"child-id-1", "child-id-2"}
        assert category.image_ids == {"image-id-1", "image-id-2"}

    def test_add_child(self) -> None:
        """Test adding a child category."""
        parent = Category(name="Parent", id="parent-id")
        child = Category(name="Child", id="child-id")
        
        parent.add_child(child)
        
        assert child.parent_id == "parent-id"
        assert "child-id" in parent.child_ids

    def test_add_child_self_reference(self) -> None:
        """Test adding a category as a child of itself."""
        category = Category(name="Category", id="category-id")
        
        with pytest.raises(ValueError):
            category.add_child(category)

    def test_add_child_circular_reference(self) -> None:
        """Test adding a child that would create a circular reference."""
        grandparent = Category(name="Grandparent", id="grandparent-id")
        parent = Category(name="Parent", id="parent-id")
        child = Category(name="Child", id="child-id")
        
        grandparent.add_child(parent)
        parent.add_child(child)
        
        # Set up a situation where adding grandparent as a child of child
        # would create a cycle
        child.parent_id = parent.id
        parent.parent_id = grandparent.id
        
        with pytest.raises(ValueError):
            child.add_child(grandparent)

    def test_remove_child(self) -> None:
        """Test removing a child category."""
        parent = Category(name="Parent", id="parent-id")
        child = Category(name="Child", id="child-id")
        
        parent.add_child(child)
        parent.remove_child(child)
        
        assert child.parent_id is None
        assert "child-id" not in parent.child_ids

    def test_add_image(self) -> None:
        """Test adding an image to a category."""
        category = Category(name="Category")
        
        category.add_image("image-id")
        
        assert "image-id" in category.image_ids

    def test_remove_image(self) -> None:
        """Test removing an image from a category."""
        category = Category(name="Category")
        
        category.add_image("image-id")
        category.remove_image("image-id")
        
        assert "image-id" not in category.image_ids

    def test_remove_nonexistent_image(self) -> None:
        """Test removing a non-existent image from a category."""
        category = Category(name="Category")
        
        # This should not raise an exception
        category.remove_image("nonexistent-id")

    def test_get_all_image_ids(self) -> None:
        """Test getting all image IDs in a category and its subcategories."""
        parent = Category(name="Parent", id="parent-id")
        child1 = Category(name="Child1", id="child1-id")
        child2 = Category(name="Child2", id="child2-id")
        
        parent.add_child(child1)
        parent.add_child(child2)
        
        parent.add_image("parent-image")
        child1.add_image("child1-image")
        child2.add_image("child2-image")
        
        category_map = {
            "parent-id": parent,
            "child1-id": child1,
            "child2-id": child2
        }
        
        all_images = parent.get_all_image_ids(category_map)
        
        assert all_images == {"parent-image", "child1-image", "child2-image"}

    def test_get_path(self) -> None:
        """Test getting the path from the root category to a category."""
        root = Category(name="Root", id="root-id")
        parent = Category(name="Parent", id="parent-id")
        child = Category(name="Child", id="child-id")
        
        root.add_child(parent)
        parent.add_child(child)
        
        category_map = {
            "root-id": root,
            "parent-id": parent,
            "child-id": child
        }
        
        path = child.get_path(category_map)
        
        assert len(path) == 3
        assert path[0].id == "root-id"
        assert path[1].id == "parent-id"
        assert path[2].id == "child-id"

    def test_get_path_names(self) -> None:
        """Test getting the path names from the root category to a category."""
        root = Category(name="Root", id="root-id")
        parent = Category(name="Parent", id="parent-id")
        child = Category(name="Child", id="child-id")
        
        root.add_child(parent)
        parent.add_child(child)
        
        category_map = {
            "root-id": root,
            "parent-id": parent,
            "child-id": child
        }
        
        path_names = child.get_path_names(category_map)
        
        assert path_names == ["Root", "Parent", "Child"]