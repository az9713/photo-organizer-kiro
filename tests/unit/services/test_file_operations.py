"""
Unit tests for the FileOperations service.
"""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from photo_organizer.models.image import Image
from photo_organizer.services.file_operations import FileOperationResult, FileOperations
from photo_organizer.services.file_system_manager import FileSystemError


class TestFileOperationResult:
    """Tests for the FileOperationResult class."""

    def test_init(self) -> None:
        """Test initializing a FileOperationResult."""
        original_path = Path("/path/to/original.jpg")
        new_path = Path("/path/to/new.jpg")
        category_id = "category-id"
        
        # Test successful result
        result = FileOperationResult(
            original_path=original_path,
            new_path=new_path,
            category_id=category_id,
            success=True
        )
        
        assert result.original_path == original_path
        assert result.new_path == new_path
        assert result.category_id == category_id
        assert result.success is True
        assert result.error is None
        
        # Test failed result
        error = Exception("Test error")
        result = FileOperationResult(
            original_path=original_path,
            success=False,
            error=error
        )
        
        assert result.original_path == original_path
        assert result.new_path is None
        assert result.category_id is None
        assert result.success is False
        assert result.error == error


class TestFileOperations:
    """Tests for the FileOperations class."""

    def test_copy_and_rename_file(self, tmp_path) -> None:
        """Test copying and renaming a file."""
        # Create a mock file system manager
        fs_manager = MagicMock()
        fs_manager.create_directory = MagicMock()
        fs_manager.copy_file = MagicMock()
        
        # Create a mock image
        source_path = tmp_path / "source.jpg"
        image = MagicMock(spec=Image)
        image.path = source_path
        image.content_tags = ["beach", "sunset", "vacation"]
        
        # Create a FileOperations instance
        file_ops = FileOperations(fs_manager)
        
        # Mock the _ensure_unique_path method to return a predictable path
        destination_path = tmp_path / "destination" / "beach_sunset_vacation_12345678.jpg"
        file_ops._ensure_unique_path = MagicMock(return_value=destination_path)
        
        # Call copy_and_rename_file
        result = file_ops.copy_and_rename_file(
            image,
            tmp_path / "destination"
        )
        
        # Check that the file system manager was called correctly
        fs_manager.create_directory.assert_called_once_with(tmp_path / "destination")
        fs_manager.copy_file.assert_called_once_with(source_path, destination_path)
        
        # Check the result
        assert result.original_path == source_path
        assert result.new_path == destination_path
        assert result.success is True
        assert result.error is None

    def test_copy_and_rename_file_error(self, tmp_path) -> None:
        """Test copying and renaming a file with an error."""
        # Create a mock file system manager
        fs_manager = MagicMock()
        fs_manager.create_directory = MagicMock()
        fs_manager.copy_file = MagicMock(side_effect=FileSystemError("Test error"))
        
        # Create a mock image
        source_path = tmp_path / "source.jpg"
        image = MagicMock(spec=Image)
        image.path = source_path
        image.content_tags = ["beach", "sunset", "vacation"]
        
        # Create a FileOperations instance
        file_ops = FileOperations(fs_manager)
        
        # Mock the _ensure_unique_path method to return a predictable path
        destination_path = tmp_path / "destination" / "beach_sunset_vacation_12345678.jpg"
        file_ops._ensure_unique_path = MagicMock(return_value=destination_path)
        
        # Call copy_and_rename_file
        result = file_ops.copy_and_rename_file(
            image,
            tmp_path / "destination"
        )
        
        # Check the result
        assert result.original_path == source_path
        assert result.new_path is None
        assert result.success is False
        assert isinstance(result.error, FileSystemError)

    def test_copy_images_to_categories(self, tmp_path) -> None:
        """Test copying images to categories."""
        # Create a mock file system manager
        fs_manager = MagicMock()
        
        # Create mock images
        image1 = MagicMock(spec=Image)
        image1.path = tmp_path / "image1.jpg"
        image1.content_tags = ["beach", "sunset"]
        image1.categories = ["category1", "category2"]
        
        image2 = MagicMock(spec=Image)
        image2.path = tmp_path / "image2.jpg"
        image2.content_tags = ["mountains", "snow"]
        image2.categories = ["category2"]
        
        images = {
            "image1": image1,
            "image2": image2
        }
        
        # Create category paths
        category_paths = {
            "category1": tmp_path / "output" / "Category1",
            "category2": tmp_path / "output" / "Category2"
        }
        
        # Create a FileOperations instance
        file_ops = FileOperations(fs_manager)
        
        # Mock the copy_and_rename_file method
        def mock_copy_and_rename(image, dest_dir, *args, **kwargs):
            return FileOperationResult(
                original_path=image.path,
                new_path=dest_dir / f"{image.path.stem}_new{image.path.suffix}"
            )
        
        file_ops.copy_and_rename_file = MagicMock(side_effect=mock_copy_and_rename)
        
        # Call copy_images_to_categories
        results = file_ops.copy_images_to_categories(images, category_paths)
        
        # Check the results
        assert len(results) == 3  # image1 to category1, image1 to category2, image2 to category2
        
        # Check that copy_and_rename_file was called correctly
        assert file_ops.copy_and_rename_file.call_count == 3
        
        # Check that each image was copied to the correct categories
        category_counts = {"category1": 0, "category2": 0}
        for result in results:
            assert result.success is True
            if result.category_id == "category1":
                assert result.original_path == image1.path
                category_counts["category1"] += 1
            elif result.category_id == "category2":
                assert result.original_path in [image1.path, image2.path]
                category_counts["category2"] += 1
        
        assert category_counts["category1"] == 1
        assert category_counts["category2"] == 2

    def test_copy_images_to_categories_no_categories(self, tmp_path) -> None:
        """Test copying images with no assigned categories."""
        # Create a mock file system manager
        fs_manager = MagicMock()
        
        # Create a mock image with no categories
        image = MagicMock(spec=Image)
        image.path = tmp_path / "image.jpg"
        image.content_tags = ["beach", "sunset"]
        
        images = {"image": image}
        category_paths = {"category1": tmp_path / "output" / "Category1"}
        
        # Create a FileOperations instance
        file_ops = FileOperations(fs_manager)
        
        # Call copy_images_to_categories
        results = file_ops.copy_images_to_categories(images, category_paths)
        
        # Check the results
        assert len(results) == 1
        assert results[0].original_path == image.path
        assert results[0].success is False
        assert "not assigned to any category" in str(results[0].error)

    def test_generate_filename(self, tmp_path) -> None:
        """Test generating a filename for an image."""
        # Create a mock file system manager
        fs_manager = MagicMock()
        
        # Create a mock image
        image = MagicMock(spec=Image)
        image.path = tmp_path / "image.jpg"
        image.content_tags = ["beach", "sunset", "vacation", "extra", "tags"]
        
        # Create a FileOperations instance
        file_ops = FileOperations(fs_manager)
        
        # Mock the _generate_index method to return a predictable index
        file_ops._generate_index = MagicMock(return_value="12345678")
        
        # Test with default template
        filename = file_ops._generate_filename(image, "{content}_{index}", 50)
        assert filename == "beach_sunset_vacation_12345678"
        
        # Test with custom template
        filename = file_ops._generate_filename(image, "photo_{content}", 50)
        assert filename == "photo_beach_sunset_vacation"
        
        # Test with max length
        filename = file_ops._generate_filename(image, "{content}_{index}", 10)
        assert filename == "beach_suns"
        
        # Test with no content tags
        image.content_tags = []
        filename = file_ops._generate_filename(image, "{content}_{index}", 50)
        assert filename == "image_12345678"

    def test_sanitize_filename(self) -> None:
        """Test sanitizing a filename."""
        # Create a mock file system manager
        fs_manager = MagicMock()
        
        # Create a FileOperations instance
        file_ops = FileOperations(fs_manager)
        
        # Test with invalid characters
        assert file_ops._sanitize_filename('test<>:"/\\|?*test') == "test__________test"
        
        # Test with spaces
        assert file_ops._sanitize_filename("test with spaces") == "test_with_spaces"
        
        # Test with leading/trailing spaces and periods
        assert file_ops._sanitize_filename(" .test. ") == "test"
        
        # Test with empty name
        assert file_ops._sanitize_filename("") == "image"
        assert file_ops._sanitize_filename(" . ") == "image"

    def test_generate_index(self, tmp_path) -> None:
        """Test generating an index for a file."""
        # Create a mock file system manager
        fs_manager = MagicMock()
        
        # Create a FileOperations instance
        file_ops = FileOperations(fs_manager)
        
        # Test with a path
        path = tmp_path / "image.jpg"
        index = file_ops._generate_index(path)
        
        # The index should be a string of 8 hexadecimal characters
        assert isinstance(index, str)
        assert len(index) == 8
        assert all(c in "0123456789abcdef" for c in index)
        
        # The same path should always generate the same index
        assert file_ops._generate_index(path) == index
        
        # Different paths should generate different indices
        other_path = tmp_path / "other.jpg"
        other_index = file_ops._generate_index(other_path)
        assert other_index != index

    def test_ensure_unique_path(self, tmp_path) -> None:
        """Test ensuring a path is unique."""
        # Create a mock file system manager
        fs_manager = MagicMock()
        
        # Create a FileOperations instance
        file_ops = FileOperations(fs_manager)
        
        # Test with a non-existent path
        path = tmp_path / "image.jpg"
        
        # Mock Path.exists to return False
        with patch.object(Path, "exists", return_value=False):
            unique_path = file_ops._ensure_unique_path(path)
            assert unique_path == path
        
        # Test with an existing path
        with patch.object(Path, "exists", side_effect=[True, True, False]):
            unique_path = file_ops._ensure_unique_path(path)
            assert unique_path == tmp_path / "image_2.jpg"