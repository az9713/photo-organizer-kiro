"""
File selection interface for the Photo Organizer application.
"""

import os
from pathlib import Path
from typing import List, Optional, Set

from PyQt6.QtCore import QMimeData, QSize, Qt, pyqtSignal
from PyQt6.QtGui import QDragEnterEvent, QDragMoveEvent, QDropEvent
from PyQt6.QtWidgets import (
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)


class DropArea(QFrame):
    """A widget that accepts drag and drop of files and folders."""
    
    filesDropped = pyqtSignal(list)
    
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """
        Initialize a drop area.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.setAcceptDrops(True)
        self.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Sunken)
        self.setMinimumSize(400, 200)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        label = QLabel("Drop files or folders here")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
        
        self.setLayout(layout)
    
    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        """
        Handle drag enter events.
        
        Args:
            event: The drag enter event
        """
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()
    
    def dragMoveEvent(self, event: QDragMoveEvent) -> None:
        """
        Handle drag move events.
        
        Args:
            event: The drag move event
        """
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()
    
    def dropEvent(self, event: QDropEvent) -> None:
        """
        Handle drop events.
        
        Args:
            event: The drop event
        """
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            
            paths = []
            for url in event.mimeData().urls():
                path = url.toLocalFile()
                paths.append(path)
            
            self.filesDropped.emit(paths)
        else:
            event.ignore()


class FileSelectionWidget(QWidget):
    """Widget for selecting files and folders."""
    
    selectionChanged = pyqtSignal()
    
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """
        Initialize a file selection widget.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        
        self._selected_paths: Set[str] = set()
        self._supported_extensions = {
            ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".tif", ".webp"
        }
        
        self._create_ui()
    
    def _create_ui(self) -> None:
        """Create the user interface."""
        layout = QVBoxLayout(self)
        
        # Drop area
        self.drop_area = DropArea()
        self.drop_area.filesDropped.connect(self._on_files_dropped)
        layout.addWidget(self.drop_area)
        
        # Buttons
        button_layout = QHBoxLayout()
        layout.addLayout(button_layout)
        
        self.add_files_button = QPushButton("Add Files...")
        self.add_files_button.clicked.connect(self._on_add_files)
        button_layout.addWidget(self.add_files_button)
        
        self.add_folder_button = QPushButton("Add Folder...")
        self.add_folder_button.clicked.connect(self._on_add_folder)
        button_layout.addWidget(self.add_folder_button)
        
        self.clear_button = QPushButton("Clear")
        self.clear_button.clicked.connect(self._on_clear)
        button_layout.addWidget(self.clear_button)
        
        # Selected files list
        self.file_list = QListWidget()
        self.file_list.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        self.file_list.setMinimumHeight(200)
        layout.addWidget(self.file_list)
        
        # Remove selected button
        self.remove_selected_button = QPushButton("Remove Selected")
        self.remove_selected_button.clicked.connect(self._on_remove_selected)
        layout.addWidget(self.remove_selected_button)
        
        self.setLayout(layout)
    
    def _on_files_dropped(self, paths: List[str]) -> None:
        """
        Handle dropped files.
        
        Args:
            paths: List of file paths
        """
        self._add_paths(paths)
    
    def _on_add_files(self) -> None:
        """Handle the Add Files button."""
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFiles)
        file_dialog.setNameFilter(
            "Images (*.jpg *.jpeg *.png *.gif *.bmp *.tiff *.tif *.webp)"
        )
        
        if file_dialog.exec():
            file_paths = file_dialog.selectedFiles()
            self._add_paths(file_paths)
    
    def _on_add_folder(self) -> None:
        """Handle the Add Folder button."""
        folder_dialog = QFileDialog(self)
        folder_dialog.setFileMode(QFileDialog.FileMode.Directory)
        folder_dialog.setOption(QFileDialog.Option.ShowDirsOnly, True)
        
        if folder_dialog.exec():
            folder_paths = folder_dialog.selectedFiles()
            if folder_paths:
                self._add_paths(folder_paths)
    
    def _on_clear(self) -> None:
        """Handle the Clear button."""
        self.file_list.clear()
        self._selected_paths.clear()
        self.selectionChanged.emit()
    
    def _on_remove_selected(self) -> None:
        """Handle the Remove Selected button."""
        selected_items = self.file_list.selectedItems()
        
        for item in selected_items:
            path = item.data(Qt.ItemDataRole.UserRole)
            self._selected_paths.remove(path)
            self.file_list.takeItem(self.file_list.row(item))
        
        self.selectionChanged.emit()
    
    def _add_paths(self, paths: List[str]) -> None:
        """
        Add paths to the selection.
        
        Args:
            paths: List of file or folder paths
        """
        for path in paths:
            if os.path.isdir(path):
                self._add_folder(path)
            elif os.path.isfile(path):
                self._add_file(path)
    
    def _add_folder(self, folder_path: str) -> None:
        """
        Add a folder and its contents to the selection.
        
        Args:
            folder_path: Path to the folder
        """
        for root, _, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                self._add_file(file_path)
    
    def _add_file(self, file_path: str) -> None:
        """
        Add a file to the selection.
        
        Args:
            file_path: Path to the file
        """
        # Check if the file is an image
        _, ext = os.path.splitext(file_path)
        if ext.lower() not in self._supported_extensions:
            return
        
        # Check if the file is already in the selection
        if file_path in self._selected_paths:
            return
        
        # Add the file to the selection
        self._selected_paths.add(file_path)
        
        # Add the file to the list widget
        item = QListWidgetItem(os.path.basename(file_path))
        item.setData(Qt.ItemDataRole.UserRole, file_path)
        item.setToolTip(file_path)
        self.file_list.addItem(item)
        
        self.selectionChanged.emit()
    
    def get_selected_paths(self) -> List[str]:
        """
        Get the selected file paths.
        
        Returns:
            List of selected file paths
        """
        return list(self._selected_paths)