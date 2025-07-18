"""
Reporting service for the Photo Organizer application.
"""

from __future__ import annotations

import html
import os
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Union


class ReportFormat(Enum):
    """Supported report formats."""
    TEXT = auto()
    HTML = auto()


@dataclass
class FolderNode:
    """Represents a folder in the folder structure."""
    name: str
    path: str
    files: List[str] = field(default_factory=list)
    subfolders: List[FolderNode] = field(default_factory=list)
    
    def add_file(self, filename: str) -> None:
        """Add a file to this folder."""
        self.files.append(filename)
    
    def add_subfolder(self, subfolder: FolderNode) -> None:
        """Add a subfolder to this folder."""
        self.subfolders.append(subfolder)
    
    @property
    def file_count(self) -> int:
        """Get the total number of files in this folder and its subfolders."""
        count = len(self.files)
        for subfolder in self.subfolders:
            count += subfolder.file_count
        return count
    
    @property
    def subfolder_count(self) -> int:
        """Get the total number of subfolders in this folder and its subfolders."""
        count = len(self.subfolders)
        for subfolder in self.subfolders:
            count += subfolder.subfolder_count
        return count


@dataclass
class FileMapping:
    """Represents a mapping from an original file to a new file."""
    original_path: str
    new_path: str
    category: str
    timestamp: Optional[datetime] = None
    geolocation: Optional[str] = None


@dataclass
class ReportSummary:
    """Summary statistics for a report."""
    total_files: int
    processed_files: int
    skipped_files: int
    error_count: int
    folders_created: int
    processing_time: float  # in seconds


@dataclass
class Report:
    """Represents a report of the reorganization process."""
    summary: ReportSummary
    folder_structure: FolderNode
    file_mappings: List[FileMapping]
    errors: List[Dict[str, str]] = field(default_factory=list)


class ReportingService:
    """Service for generating reports of the reorganization process."""
    
    def generate_report(
        self,
        folder_structure: FolderNode,
        file_mappings: List[FileMapping],
        processing_time: float,
        total_files: int,
        processed_files: int,
        skipped_files: int,
        error_count: int,
        errors: Optional[List[Dict[str, str]]] = None,
    ) -> Report:
        """
        Generate a report of the reorganization process.
        
        Args:
            folder_structure: The folder structure created during reorganization
            file_mappings: Mappings from original files to new files
            processing_time: Time taken for processing in seconds
            total_files: Total number of files processed
            processed_files: Number of files successfully processed
            skipped_files: Number of files skipped
            error_count: Number of errors encountered
            errors: List of errors encountered during processing
            
        Returns:
            A Report object containing the report data
        """
        # Calculate the number of folders created
        folders_created = 1  # Root folder
        folders_created += folder_structure.subfolder_count
        
        summary = ReportSummary(
            total_files=total_files,
            processed_files=processed_files,
            skipped_files=skipped_files,
            error_count=error_count,
            folders_created=folders_created,
            processing_time=processing_time,
        )
        
        return Report(
            summary=summary,
            folder_structure=folder_structure,
            file_mappings=file_mappings,
            errors=errors or [],
        )
    
    def save_report(self, report: Report, format: ReportFormat, output_path: str) -> None:
        """
        Save a report to a file.
        
        Args:
            report: The report to save
            format: The format to save the report in
            output_path: The path to save the report to
        """
        if format == ReportFormat.TEXT:
            content = self._format_report_text(report)
        elif format == ReportFormat.HTML:
            content = self._format_report_html(report)
        else:
            raise ValueError(f"Unsupported report format: {format}")
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)
    
    def _format_report_text(self, report: Report) -> str:
        """
        Format a report as plain text.
        
        Args:
            report: The report to format
            
        Returns:
            The formatted report as a string
        """
        lines = []
        
        # Add header
        lines.append("Photo Organizer Report")
        lines.append("=" * 80)
        lines.append("")
        
        # Add summary
        lines.append("Summary")
        lines.append("-" * 80)
        lines.append(f"Total files: {report.summary.total_files}")
        lines.append(f"Processed files: {report.summary.processed_files}")
        lines.append(f"Skipped files: {report.summary.skipped_files}")
        lines.append(f"Errors: {report.summary.error_count}")
        lines.append(f"Folders created: {report.summary.folders_created}")
        lines.append(f"Processing time: {report.summary.processing_time:.2f} seconds")
        lines.append("")
        
        # Add folder structure
        lines.append("Folder Structure")
        lines.append("-" * 80)
        lines.append(self._format_folder_structure_text(report.folder_structure))
        lines.append("")
        
        # Add file mappings
        lines.append("File Mappings")
        lines.append("-" * 80)
        lines.append(self._format_file_mappings_text(report.file_mappings))
        lines.append("")
        
        # Add errors
        if report.errors:
            lines.append("Errors")
            lines.append("-" * 80)
            for error in report.errors:
                lines.append(f"File: {error['file']}")
                lines.append(f"Error: {error['error']}")
                lines.append("")
        
        return "\n".join(lines)
    
    def _format_folder_structure_text(self, folder: FolderNode, indent: int = 0) -> str:
        """
        Format a folder structure as plain text.
        
        Args:
            folder: The root folder of the structure
            indent: The indentation level
            
        Returns:
            The formatted folder structure as a string
        """
        lines = []
        
        # Add folder name
        lines.append(" " * indent + f"- {folder.name}/")
        
        # Add files
        for file in sorted(folder.files):
            lines.append(" " * (indent + 2) + file)
        
        # Add subfolders
        for subfolder in sorted(folder.subfolders, key=lambda f: f.name):
            lines.append(self._format_folder_structure_text(subfolder, indent + 2))
        
        return "\n".join(lines)
    
    def _format_file_mappings_text(self, file_mappings: List[FileMapping]) -> str:
        """
        Format file mappings as plain text.
        
        Args:
            file_mappings: The file mappings to format
            
        Returns:
            The formatted file mappings as a string
        """
        lines = []
        
        # Group file mappings by category
        mappings_by_category: Dict[str, List[FileMapping]] = {}
        for mapping in file_mappings:
            if mapping.category not in mappings_by_category:
                mappings_by_category[mapping.category] = []
            mappings_by_category[mapping.category].append(mapping)
        
        # Format each category
        for category, mappings in sorted(mappings_by_category.items()):
            lines.append(f"Category: {category}")
            for mapping in mappings:
                original_filename = os.path.basename(mapping.original_path)
                new_filename = os.path.basename(mapping.new_path)
                lines.append(f"  {original_filename} -> {new_filename}")
                
                if mapping.timestamp:
                    timestamp = mapping.timestamp.strftime("%-m/%-d/%Y %-I:%M%p").lower()
                    lines.append(f"    Timestamp: {timestamp}")
                
                if mapping.geolocation:
                    lines.append(f"    Location: {mapping.geolocation}")
                
                lines.append("")
        
        return "\n".join(lines)
    
    def _format_report_html(self, report: Report) -> str:
        """
        Format a report as HTML.
        
        Args:
            report: The report to format
            
        Returns:
            The formatted report as a string
        """
        lines = []
        
        # Add HTML header
        lines.append("<!DOCTYPE html>")
        lines.append("<html>")
        lines.append("<head>")
        lines.append("  <title>Photo Organizer Report</title>")
        lines.append("  <style>")
        lines.append("    body { font-family: Arial, sans-serif; margin: 20px; }")
        lines.append("    h1 { color: #333; }")
        lines.append("    h2 { color: #666; margin-top: 30px; }")
        lines.append("    .summary { background-color: #f5f5f5; padding: 10px; border-radius: 5px; }")
        lines.append("    .folder { margin-left: 20px; }")
        lines.append("    .file { margin-left: 40px; color: #333; }")
        lines.append("    .mapping { margin-bottom: 20px; padding: 10px; background-color: #f9f9f9; border-radius: 5px; }")
        lines.append("    .error { color: red; }")
        lines.append("  </style>")
        lines.append("</head>")
        lines.append("<body>")
        
        # Add header
        lines.append("  <h1>Photo Organizer Report</h1>")
        
        # Add summary
        lines.append("  <h2>Summary</h2>")
        lines.append("  <div class='summary'>")
        lines.append(f"    <p>Total files: {report.summary.total_files}</p>")
        lines.append(f"    <p>Processed files: {report.summary.processed_files}</p>")
        lines.append(f"    <p>Skipped files: {report.summary.skipped_files}</p>")
        lines.append(f"    <p>Errors: {report.summary.error_count}</p>")
        lines.append(f"    <p>Folders created: {report.summary.folders_created}</p>")
        lines.append(f"    <p>Processing time: {report.summary.processing_time:.2f} seconds</p>")
        lines.append("  </div>")
        
        # Add folder structure
        lines.append("  <h2>Folder Structure</h2>")
        lines.append(self._format_folder_structure_html(report.folder_structure))
        
        # Add file mappings
        lines.append("  <h2>File Mappings</h2>")
        lines.append(self._format_file_mappings_html(report.file_mappings))
        
        # Add errors
        if report.errors:
            lines.append("  <h2>Errors</h2>")
            for error in report.errors:
                lines.append("  <div class='error'>")
                lines.append(f"    <p>File: {html.escape(error['file'])}</p>")
                lines.append(f"    <p>Error: {html.escape(error['error'])}</p>")
                lines.append("  </div>")
        
        # Add HTML footer
        lines.append("</body>")
        lines.append("</html>")
        
        return "\n".join(lines)
    
    def _format_folder_structure_html(self, folder: FolderNode) -> str:
        """
        Format a folder structure as HTML.
        
        Args:
            folder: The root folder of the structure
            
        Returns:
            The formatted folder structure as a string
        """
        lines = []
        
        lines.append("  <div class='folder'>")
        lines.append(f"    <h3>{html.escape(folder.name)}/</h3>")
        
        # Add files
        if folder.files:
            lines.append("    <ul>")
            for file in sorted(folder.files):
                lines.append(f"      <li class='file'>{html.escape(file)}</li>")
            lines.append("    </ul>")
        
        # Add subfolders
        for subfolder in sorted(folder.subfolders, key=lambda f: f.name):
            lines.append(self._format_folder_structure_html(subfolder))
        
        lines.append("  </div>")
        
        return "\n".join(lines)
    
    def _format_file_mappings_html(self, file_mappings: List[FileMapping]) -> str:
        """
        Format file mappings as HTML.
        
        Args:
            file_mappings: The file mappings to format
            
        Returns:
            The formatted file mappings as a string
        """
        lines = []
        
        # Group file mappings by category
        mappings_by_category: Dict[str, List[FileMapping]] = {}
        for mapping in file_mappings:
            if mapping.category not in mappings_by_category:
                mappings_by_category[mapping.category] = []
            mappings_by_category[mapping.category].append(mapping)
        
        # Format each category
        for category, mappings in sorted(mappings_by_category.items()):
            lines.append(f"  <h3>{html.escape(category)}</h3>")
            
            for mapping in mappings:
                original_filename = os.path.basename(mapping.original_path)
                new_filename = os.path.basename(mapping.new_path)
                
                lines.append("  <div class='mapping'>")
                lines.append(f"    <p><strong>{html.escape(original_filename)}</strong> -> {html.escape(new_filename)}</p>")
                
                if mapping.timestamp:
                    timestamp = mapping.timestamp.strftime("%-m/%-d/%Y %-I:%M%p").lower()
                    lines.append(f"    <p>Timestamp: {html.escape(timestamp)}</p>")
                
                if mapping.geolocation:
                    lines.append(f"    <p>Location: {html.escape(mapping.geolocation)}</p>")
                
                lines.append("  </div>")
        
        return "\n".join(lines)