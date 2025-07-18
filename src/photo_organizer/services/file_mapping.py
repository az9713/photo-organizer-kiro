"""
File mapping service for the Photo Organizer application.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Dict, List, Optional, Set

from photo_organizer.models.image import GeoLocation, Image
from photo_organizer.services.reporting import FileMapping, FolderNode


class FileMappingService:
    """Service for creating hierarchical file mappings."""
    
    def create_folder_structure(self, images: List[Image], output_path: str) -> FolderNode:
        """
        Create a folder structure from a list of images.
        
        Args:
            images: The images to create the folder structure from
            output_path: The base output path
            
        Returns:
            A FolderNode representing the root of the folder structure
        """
        root = FolderNode(name="root", path=output_path)
        folder_map: Dict[str, FolderNode] = {output_path: root}
        
        for image in images:
            if not image.new_path:
                continue
            
            # Get the directory path
            dir_path = str(image.new_path.parent)
            
            # Create folder nodes for each directory in the path
            self._ensure_folder_path(dir_path, output_path, folder_map)
            
            # Add the file to the leaf folder
            folder = folder_map[dir_path]
            folder.add_file(image.new_path.name)
        
        return root
    
    def create_file_mappings(self, images: List[Image]) -> List[FileMapping]:
        """
        Create file mappings from a list of images.
        
        Args:
            images: The images to create file mappings from
            
        Returns:
            A list of FileMapping objects
        """
        mappings = []
        
        for image in images:
            if not image.new_path:
                continue
            
            # Get the output base path (parent of the first category folder)
            output_base = str(image.new_path.parent.parent.parent)
            
            mapping = FileMapping(
                original_path=str(image.path),
                new_path=str(image.new_path),
                category=self._get_category_from_path(image.new_path, output_base),
                timestamp=image.metadata.timestamp if image.metadata else None,
                geolocation=self._get_formatted_geolocation(image.metadata.geolocation) if image.metadata and image.metadata.geolocation else None,
            )
            
            mappings.append(mapping)
        
        return mappings
    
    def _ensure_folder_path(self, dir_path: str, output_path: str, folder_map: Dict[str, FolderNode]) -> None:
        """
        Ensure that all folders in a path exist in the folder map.
        
        Args:
            dir_path: The directory path to ensure
            output_path: The base output path
            folder_map: A mapping of directory paths to FolderNode objects
        """
        if dir_path in folder_map:
            return
        
        # Get the parent path
        parent_path = os.path.dirname(dir_path)
        
        # Ensure the parent path exists
        if parent_path != output_path and parent_path not in folder_map:
            self._ensure_folder_path(parent_path, output_path, folder_map)
        
        # Create the folder node
        folder = FolderNode(name=os.path.basename(dir_path), path=dir_path)
        folder_map[dir_path] = folder
        
        # Add the folder to its parent
        parent = folder_map[parent_path]
        parent.add_subfolder(folder)
    
    def _get_category_from_path(self, path: Path, output_base: str) -> str:
        """
        Get the category from a path.
        
        Args:
            path: The path to get the category from
            output_base: The base output path
            
        Returns:
            The category as a string
        """
        # Remove the output base and the filename from the path
        relative_path = str(path.parent).replace(output_base, "").lstrip(os.sep)
        
        # Return the relative path as the category
        return relative_path
    
    def _get_formatted_geolocation(self, geolocation: Optional[GeoLocation]) -> Optional[str]:
        """
        Get a formatted geolocation string.
        
        Args:
            geolocation: The geolocation to format
            
        Returns:
            A formatted geolocation string, or None if geolocation is None
        """
        if not geolocation:
            return None
        
        components = []
        
        # Add institution name if available
        if geolocation.institution_name:
            components.append(geolocation.institution_name)
        
        # Add street if available
        if geolocation.street:
            components.append(geolocation.street)
        
        # Add city and postal code if available
        city_postal = []
        if geolocation.city:
            city_postal.append(geolocation.city)
        if geolocation.postal_code:
            city_postal.append(geolocation.postal_code)
        if city_postal:
            components.append(", ".join(city_postal))
        
        # Add country if available and not US
        if geolocation.country and geolocation.country.lower() != "united states":
            components.append(geolocation.country)
        
        return ", ".join(components)