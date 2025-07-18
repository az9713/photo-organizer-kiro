"""
File operations service for copying and renaming files.
"""

from __future__ import annotations

import hashlib
import os
import re
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

from photo_organizer.models.category import Category
from photo_organizer.models.image import Image
from photo_organizer.services.file_system_manager import (
    DefaultFileSystemManager,
    FileSystemError,
    FileSystemManager,
)


class FileOperationResult:
    """Result of a file operation."""
    
    def __init__(
        self,
        original_path: Path,
        new_path: Optional[Path] = None,
        category_id: Optional[str] = None,
        success: bool = True,
        error: Optional[Exception] = None
    ) -> None:
        """
        Initialize a FileOperationResult.
        
        Args:
            original_path: The original file path
            new_path: The new file path
            category_id: The ID of the category the file was assigned to
            success: Whether the operation was successful
            error: The error that occurred, if any
        """
        self.original_path = original_path
        self.new_path = new_path
        self.category_id = category_id
        self.success = success
        self.error = error


class FileOperations:
    """
    Service for file copying and renaming operations.
    """
    
    def __init__(self, file_system_manager: FileSystemManager) -> None:
        """
        Initialize a FileOperations service.
        
        Args:
            file_system_manager: The file system manager to use
        """
        self.file_system_manager = file_system_manager
    
    def copy_and_rename_file(
        self,
        image: Image,
        destination_dir: Path,
        name_template: str = "{content}_{index}",
        max_name_length: int = 50
    ) -> FileOperationResult:
        """
        Copy and rename a file.
        
        Args:
            image: The image to copy and rename
            destination_dir: The destination directory
            name_template: The template for the new filename
            max_name_length: The maximum length for the new filename
            
        Returns:
            A FileOperationResult with the result of the operation
        """
        try:
            # Ensure the destination directory exists
            self.file_system_manager.create_directory(destination_dir)
            
            # Generate a new filename based on content
            new_filename = self._generate_filename(
                image,
                name_template,
                max_name_length
            )
            
            # Add the file extension
            new_filename = f"{new_filename}{image.path.suffix}"
            
            # Create the full destination path
            destination_path = destination_dir / new_filename
            
            # Ensure the destination path is unique
            destination_path = self._ensure_unique_path(destination_path)
            
            # Copy the file
            self.file_system_manager.copy_file(image.path, destination_path)
            
            # Return the result
            return FileOperationResult(
                original_path=image.path,
                new_path=destination_path
            )
        
        except (FileSystemError, Exception) as e:
            return FileOperationResult(
                original_path=image.path,
                success=False,
                error=e
            )
    
    def copy_images_to_categories(
        self,
        images: Dict[str, Image],
        category_paths: Dict[str, Path],
        name_template: str = "{content}_{index}",
        max_name_length: int = 50
    ) -> List[FileOperationResult]:
        """
        Copy images to their assigned categories.
        
        Args:
            images: A mapping of image IDs to Image objects
            category_paths: A mapping of category IDs to folder paths
            name_template: The template for the new filenames
            max_name_length: The maximum length for the new filenames
            
        Returns:
            A list of FileOperationResults with the results of the operations
        """
        results = []
        
        for image_id, image in images.items():
            # Find the categories for this image
            categories = []
            for category_id, path in category_paths.items():
                if hasattr(image, "categories") and category_id in image.categories:
                    categories.append((category_id, path))
            
            # If no categories, skip this image
            if not categories:
                results.append(FileOperationResult(
                    original_path=image.path,
                    success=False,
                    error=Exception("Image not assigned to any category")
                ))
                continue
            
            # Copy the image to each category
            for category_id, path in categories:
                result = self.copy_and_rename_file(
                    image,
                    path,
                    name_template,
                    max_name_length
                )
                
                # Add the category ID to the result
                result.category_id = category_id
                
                # Add to results
                results.append(result)
        
        return results
    
    def _generate_filename(
        self,
        image: Image,
        template: str,
        max_length: int
    ) -> str:
        """
        Generate a filename for an image based on its content.
        
        Args:
            image: The image to generate a filename for
            template: The template for the filename
            max_length: The maximum length for the filename
            
        Returns:
            A filename for the image
        """
        # Get content tags from the image
        content_tags = getattr(image, "content_tags", [])
        
        # Use the first few tags as the content description
        content = "_".join(content_tags[:3]) if content_tags else "image"
        
        # Sanitize the content
        content = self._sanitize_filename(content)
        
        # Truncate if too long
        if len(content) > max_length:
            content = content[:max_length]
        
        # Generate a unique index based on the image path
        index = self._generate_index(image.path)
        
        # Format the template
        filename = template.format(content=content, index=index)
        
        # Sanitize the final filename
        return self._sanitize_filename(filename)
    
    def _sanitize_filename(self, name: str) -> str:
        """
        Sanitize a filename to be valid on the file system.
        
        Args:
            name: The filename to sanitize
            
        Returns:
            A sanitized filename
        """
        # Replace invalid characters with underscores
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            name = name.replace(char, '_')
        
        # Replace spaces with underscores
        name = name.replace(' ', '_')
        
        # Remove leading/trailing spaces and periods
        name = name.strip('. ')
        
        # If the name is empty, use a default name
        if not name:
            name = "image"
        
        return name
    
    def _generate_index(self, path: Path) -> str:
        """
        Generate a unique index for a file based on its path.
        
        Args:
            path: The file path
            
        Returns:
            A unique index
        """
        # Use a hash of the path as the index
        hash_obj = hashlib.md5(str(path).encode())
        return hash_obj.hexdigest()[:8]
    
    def _ensure_unique_path(self, path: Path) -> Path:
        """
        Ensure a path is unique by adding a suffix if necessary.
        
        Args:
            path: The path to make unique
            
        Returns:
            A unique path
        """
        if not path.exists():
            return path
        
        # Split the path into name and extension
        name = path.stem
        suffix = path.suffix
        parent = path.parent
        
        # Add a suffix to make the path unique
        counter = 1
        while True:
            new_path = parent / f"{name}_{counter}{suffix}"
            if not new_path.exists():
                return new_path
            counter += 1