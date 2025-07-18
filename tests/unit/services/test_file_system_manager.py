"""
Unit tests for the FileSystemManager service.
"""

import os
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from photo_organizer.models.category import Category
from photo_organizer.models.category_tree import CategoryTree
from photo_organizer.services.file_system_manager import (
    DefaultFileSystemManager,
    FileSystemError,
)


class TestDefaultFileSystemManager:
    """Tests for the DefaultFileSystemManager class."""

    def test_validate_path(self, tmp_path) -> None:
        """Test validating a path."""
        manager = DefaultFileSystemManager()
        
        # Create a test file
        test_file = tmp_path / "test.txt"
        test_file.write_text("test")
        
        assert manager.validate_path(test_file) is True
        assert manager.validate_path(tmp_path / "nonexistent.txt") is False

    def test_is_file(self, tmp_path) -> None:
        """Test checking if a path is a file."""
        manager = DefaultFileSystemManager()
        
        # Create a test file
        test_file = tmp_path / "test.txt"
        test_file.write_text("test")
        
        assert manager.is_file(test_file) is True
        assert manager.is_file(tmp_path) is False

    def test_is_directory(self, tmp_path) -> None:
        """Test checking if a path is a directory."""
        manager = DefaultFileSystemManager()
        
        # Create a test file
        test_file = tmp_path / "test.txt"
        test_file.write_text("test")
        
        assert manager.is_directory(tmp_path) is True
        assert manager.is_directory(test_file) is False

    def test_create_directory(self, tmp_path) -> None:
        """Test creating a directory."""
        manager = DefaultFileSystemManager()
        
        # Create a test directory
        test_dir = tmp_path / "test_dir"
        manager.create_directory(test_dir)
        
        assert test_dir.exists()
        assert test_dir.is_dir()
        
        # Create a nested directory
        nested_dir = tmp_path / "parent" / "child" / "grandchild"
        manager.create_directory(nested_dir)
        
        assert nested_dir.exists()
        assert nested_dir.is_dir()

    def test_create_directory_error(self, tmp_path) -> None:
        """Test creating a directory with an error."""
        manager = DefaultFileSystemManager()
        
        # Mock os.makedirs to raise an exception
        with patch("pathlib.Path.mkdir", side_effect=PermissionError("Permission denied")):
            with pytest.raises(FileSystemError):
                manager.create_directory(tmp_path / "test_dir")

    def test_list_files(self, tmp_path) -> None:
        """Test listing files in a directory."""
        manager = DefaultFileSystemManager()
        
        # Create test files
        file1 = tmp_path / "file1.txt"
        file2 = tmp_path / "file2.txt"
        file1.write_text("file1")
        file2.write_text("file2")
        
        # Create a subdirectory with a file
        subdir = tmp_path / "subdir"
        subdir.mkdir()
        file3 = subdir / "file3.txt"
        file3.write_text("file3")
        
        # List files non-recursively
        files = manager.list_files(tmp_path)
        assert len(files) == 2
        assert file1 in files
        assert file2 in files
        assert file3 not in files
        
        # List files recursively
        files = manager.list_files(tmp_path, recursive=True)
        assert len(files) == 3
        assert file1 in files
        assert file2 in files
        assert file3 in files

    def test_list_files_nonexistent_directory(self) -> None:
        """Test listing files in a non-existent directory."""
        manager = DefaultFileSystemManager()
        
        with pytest.raises(FileSystemError):
            manager.list_files(Path("nonexistent"))

    def test_list_files_not_a_directory(self, tmp_path) -> None:
        """Test listing files with a path that is not a directory."""
        manager = DefaultFileSystemManager()
        
        # Create a test file
        test_file = tmp_path / "test.txt"
        test_file.write_text("test")
        
        with pytest.raises(FileSystemError):
            manager.list_files(test_file)

    def test_copy_file(self, tmp_path) -> None:
        """Test copying a file."""
        manager = DefaultFileSystemManager()
        
        # Create a test file
        source = tmp_path / "source.txt"
        source.write_text("test content")
        
        # Copy the file
        destination = tmp_path / "destination.txt"
        manager.copy_file(source, destination)
        
        assert destination.exists()
        assert destination.read_text() == "test content"
        
        # Copy to a nested directory
        nested_destination = tmp_path / "nested" / "destination.txt"
        manager.copy_file(source, nested_destination)
        
        assert nested_destination.exists()
        assert nested_destination.read_text() == "test content"

    def test_copy_file_nonexistent_source(self, tmp_path) -> None:
        """Test copying a non-existent file."""
        manager = DefaultFileSystemManager()
        
        with pytest.raises(FileSystemError):
            manager.copy_file(
                Path("nonexistent.txt"),
                tmp_path / "destination.txt"
            )

    def test_copy_file_source_not_a_file(self, tmp_path) -> None:
        """Test copying a path that is not a file."""
        manager = DefaultFileSystemManager()
        
        with pytest.raises(FileSystemError):
            manager.copy_file(
                tmp_path,
                tmp_path / "destination.txt"
            )

    def test_copy_file_error(self, tmp_path) -> None:
        """Test copying a file with an error."""
        manager = DefaultFileSystemManager()
        
        # Create a test file
        source = tmp_path / "source.txt"
        source.write_text("test content")
        
        # Mock shutil.copy2 to raise an exception
        with patch("shutil.copy2", side_effect=PermissionError("Permission denied")):
            with pytest.raises(FileSystemError):
                manager.copy_file(
                    source,
                    tmp_path / "destination.txt"
                )

    def test_create_folder_structure(self, tmp_path) -> None:
        """Test creating a folder structure based on a category tree."""
        manager = DefaultFileSystemManager()
        
        # Create a category tree
        tree = CategoryTree()
        
        # Add categories
        root = Category(name="Root", id="root-id")
        parent1 = Category(name="Parent 1", id="parent1-id")
        parent2 = Category(name="Parent 2", id="parent2-id")
        child1 = Category(name="Child 1", id="child1-id")
        child2 = Category(name="Child 2", id="child2-id")
        
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
        
        # Create the folder structure
        base_path = tmp_path / "output"
        category_paths = manager.create_folder_structure(tree, base_path)
        
        # Check that the folders were created
        assert (base_path / "Root").exists()
        assert (base_path / "Root" / "Parent 1").exists()
        assert (base_path / "Root" / "Parent 2").exists()
        assert (base_path / "Root" / "Parent 1" / "Child 1").exists()
        assert (base_path / "Root" / "Parent 2" / "Child 2").exists()
        
        # Check the category paths mapping
        assert category_paths["root-id"] == base_path / "Root"
        assert category_paths["parent1-id"] == base_path / "Root" / "Parent 1"
        assert category_paths["parent2-id"] == base_path / "Root" / "Parent 2"
        assert category_paths["child1-id"] == base_path / "Root" / "Parent 1" / "Child 1"
        assert category_paths["child2-id"] == base_path / "Root" / "Parent 2" / "Child 2"

    def test_sanitize_folder_name(self) -> None:
        """Test sanitizing folder names."""
        manager = DefaultFileSystemManager()
        
        # Test invalid characters
        assert manager._sanitize_folder_name('test<>:"/\\|?*test') == "test__________test"
        
        # Test leading/trailing spaces and periods
        assert manager._sanitize_folder_name(" .test. ") == "test"
        
        # Test empty name
        assert manager._sanitize_folder_name("") == "Unnamed_Category"
        assert manager._sanitize_folder_name(" . ") == "Unnamed_Category"