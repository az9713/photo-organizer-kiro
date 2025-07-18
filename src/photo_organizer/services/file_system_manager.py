"""
FileSystemManager service for handling file system operations.
"""

from __future__ import annotations

import os
import shutil
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

from photo_organizer.models.category import Category
from photo_organizer.models.category_tree import CategoryTree


class FileSystemError(Exception):
    """Exception raised for file system errors."""
    pass


class FileSystemManager(ABC):
    """
    Abstract base class for file system operations.
    """
    
    @abstractmethod
    def validate_path(self, path: Path) -> bool:
        """
        Validate that a path exists.
        
        Args:
            path: The path to validate
            
        Returns:
            True if the path exists, False otherwise
        """
        pass
    
    @abstractmethod
    def is_file(self, path: Path) -> bool:
        """
        Check if a path is a file.
        
        Args:
            path: The path to check
            
        Returns:
            True if the path is a file, False otherwise
        """
        pass
    
    @abstractmethod
    def is_directory(self, path: Path) -> bool:
        """
        Check if a path is a directory.
        
        Args:
            path: The path to check
            
        Returns:
            True if the path is a directory, False otherwise
        """
        pass
    
    @abstractmethod
    def create_directory(self, path: Path) -> None:
        """
        Create a directory.
        
        Args:
            path: The directory path to create
        """
        pass
    
    @abstractmethod
    def list_files(self, directory: Path, recursive: bool = False) -> List[Path]:
        """
        List all files in a directory.
        
        Args:
            directory: The directory to list files from
            recursive: Whether to list files recursively
            
        Returns:
            A list of file paths
        """
        pass
    
    @abstractmethod
    def copy_file(self, source: Path, destination: Path) -> None:
        """
        Copy a file from source to destination.
        
        Args:
            source: The source file path
            destination: The destination file path
        """
        pass
    
    @abstractmethod
    def create_folder_structure(
        self, category_tree: CategoryTree, base_path: Path
    ) -> Dict[str, Path]:
        """
        Create a folder structure based on a category tree.
        
        Args:
            category_tree: The category tree to use for the folder structure
            base_path: The base path for the folder structure
            
        Returns:
            A mapping of category IDs to folder paths
        """
        pass


class DefaultFileSystemManager(FileSystemManager):
    """
    Default implementation of FileSystemManager.
    """
    
    def validate_path(self, path: Path) -> bool:
        """
        Validate that a path exists.
        
        Args:
            path: The path to validate
            
        Returns:
            True if the path exists, False otherwise
        """
        return path.exists()
    
    def is_file(self, path: Path) -> bool:
        """
        Check if a path is a file.
        
        Args:
            path: The path to check
            
        Returns:
            True if the path is a file, False otherwise
        """
        return path.is_file()
    
    def is_directory(self, path: Path) -> bool:
        """
        Check if a path is a directory.
        
        Args:
            path: The path to check
            
        Returns:
            True if the path is a directory, False otherwise
        """
        return path.is_dir()
    
    def create_directory(self, path: Path) -> None:
        """
        Create a directory.
        
        Args:
            path: The directory path to create
        """
        try:
            path.mkdir(parents=True, exist_ok=True)
        except (PermissionError, OSError) as e:
            raise FileSystemError(f"Failed to create directory {path}: {e}")
    
    def list_files(self, directory: Path, recursive: bool = False) -> List[Path]:
        """
        List all files in a directory.
        
        Args:
            directory: The directory to list files from
            recursive: Whether to list files recursively
            
        Returns:
            A list of file paths
        """
        if not self.validate_path(directory):
            raise FileSystemError(f"Directory does not exist: {directory}")
        
        if not self.is_directory(directory):
            raise FileSystemError(f"Path is not a directory: {directory}")
        
        try:
            if recursive:
                return [
                    Path(os.path.join(root, file))
                    for root, _, files in os.walk(directory)
                    for file in files
                ]
            else:
                return [
                    directory / file
                    for file in os.listdir(directory)
                    if (directory / file).is_file()
                ]
        except (PermissionError, OSError) as e:
            raise FileSystemError(f"Failed to list files in {directory}: {e}")
    
    def copy_file(self, source: Path, destination: Path) -> None:
        """
        Copy a file from source to destination.
        
        Args:
            source: The source file path
            destination: The destination file path
        """
        if not self.validate_path(source):
            raise FileSystemError(f"Source file does not exist: {source}")
        
        if not self.is_file(source):
            raise FileSystemError(f"Source is not a file: {source}")
        
        # Create destination directory if it doesn't exist
        self.create_directory(destination.parent)
        
        try:
            shutil.copy2(source, destination)
        except (PermissionError, OSError) as e:
            raise FileSystemError(f"Failed to copy file from {source} to {destination}: {e}")
    
    def create_folder_structure(
        self, category_tree: CategoryTree, base_path: Path
    ) -> Dict[str, Path]:
        """
        Create a folder structure based on a category tree.
        
        Args:
            category_tree: The category tree to use for the folder structure
            base_path: The base path for the folder structure
            
        Returns:
            A mapping of category IDs to folder paths
        """
        # Create the base directory
        self.create_directory(base_path)
        
        # Create a mapping of category IDs to folder paths
        category_paths: Dict[str, Path] = {}
        
        # Get the category hierarchy
        hierarchy = category_tree.get_category_hierarchy()
        
        for category, depth in hierarchy:
            # Get the parent path
            if category.parent_id is None:
                parent_path = base_path
            else:
                parent_path = category_paths.get(category.parent_id, base_path)
            
            # Create the category folder
            folder_path = parent_path / self._sanitize_folder_name(category.name)
            self.create_directory(folder_path)
            
            # Add to the mapping
            category_paths[category.id] = folder_path
        
        return category_paths
    
    def _sanitize_folder_name(self, name: str) -> str:
        """
        Sanitize a folder name to be valid on the file system.
        
        Args:
            name: The folder name to sanitize
            
        Returns:
            A sanitized folder name
        """
        # Replace invalid characters with underscores
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            name = name.replace(char, '_')
        
        # Remove leading/trailing spaces and periods
        name = name.strip('. ')
        
        # If the name is empty, use a default name
        if not name:
            name = "Unnamed_Category"
        
        return name