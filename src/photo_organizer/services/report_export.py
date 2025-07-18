"""
Report export service for the Photo Organizer application.
"""

from __future__ import annotations

import html
import os
from pathlib import Path
from typing import Dict, List, Optional, Set, Union

from photo_organizer.services.reporting import (
    FileMapping,
    FolderNode,
    Report,
    ReportFormat,
    ReportSummary,
)


class ReportExportService:
    """Service for exporting reports in various formats."""
    
    def export_report(self, report: Report, format: ReportFormat, output_path: str) -> None:
        """
        Export a report to a file.
        
        Args:
            report: The report to export
            format: The format to export the report in
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