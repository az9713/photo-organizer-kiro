"""
Graphical user interface for the Photo Organizer application.
"""

import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import (
    QApplication,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMenu,
    QMenuBar,
    QPushButton,
    QStatusBar,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from photo_organizer import __version__


class MainWindow(QMainWindow):
    """Main window for the Photo Organizer application."""
    
    def __init__(self) -> None:
        """Initialize the main window."""
        super().__init__()
        
        self.setWindowTitle(f"Photo Organizer {__version__}")
        self.setMinimumSize(800, 600)
        
        self._create_menu_bar()
        self._create_tool_bar()
        self._create_status_bar()
        self._create_central_widget()
    
    def _create_menu_bar(self) -> None:
        """Create the menu bar."""
        menu_bar = self.menuBar()
        
        # File menu
        file_menu = menu_bar.addMenu("&File")
        
        open_action = QAction("&Open...", self)
        open_action.setShortcut("Ctrl+O")
        open_action.setStatusTip("Open files or folders")
        open_action.triggered.connect(self._on_open)
        file_menu.addAction(open_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.setStatusTip("Exit the application")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Edit menu
        edit_menu = menu_bar.addMenu("&Edit")
        
        preferences_action = QAction("&Preferences...", self)
        preferences_action.setStatusTip("Configure application settings")
        preferences_action.triggered.connect(self._on_preferences)
        edit_menu.addAction(preferences_action)
        
        # Help menu
        help_menu = menu_bar.addMenu("&Help")
        
        about_action = QAction("&About", self)
        about_action.setStatusTip("Show information about the application")
        about_action.triggered.connect(self._on_about)
        help_menu.addAction(about_action)
    
    def _create_tool_bar(self) -> None:
        """Create the tool bar."""
        tool_bar = QToolBar("Main Toolbar")
        tool_bar.setIconSize(QSize(16, 16))
        self.addToolBar(tool_bar)
        
        # Open action
        open_action = QAction("Open", self)
        open_action.setStatusTip("Open files or folders")
        open_action.triggered.connect(self._on_open)
        tool_bar.addAction(open_action)
        
        # Organize action
        organize_action = QAction("Organize", self)
        organize_action.setStatusTip("Organize selected images")
        organize_action.triggered.connect(self._on_organize)
        tool_bar.addAction(organize_action)
        
        # Stop action
        stop_action = QAction("Stop", self)
        stop_action.setStatusTip("Stop current operation")
        stop_action.triggered.connect(self._on_stop)
        tool_bar.addAction(stop_action)
    
    def _create_status_bar(self) -> None:
        """Create the status bar."""
        status_bar = QStatusBar(self)
        self.setStatusBar(status_bar)
        
        self.status_label = QLabel("Ready")
        status_bar.addWidget(self.status_label)
    
    def _create_central_widget(self) -> None:
        """Create the central widget."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        # Welcome message
        welcome_label = QLabel("Welcome to Photo Organizer")
        welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(welcome_label)
        
        # Description
        description_label = QLabel(
            "This application helps you organize your photos based on their content."
        )
        description_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(description_label)
        
        # Buttons
        button_layout = QHBoxLayout()
        layout.addLayout(button_layout)
        
        open_button = QPushButton("Open Files...")
        open_button.clicked.connect(self._on_open_files)
        button_layout.addWidget(open_button)
        
        open_folder_button = QPushButton("Open Folder...")
        open_folder_button.clicked.connect(self._on_open_folder)
        button_layout.addWidget(open_folder_button)
    
    def _on_open(self) -> None:
        """Handle the Open action."""
        self.status_label.setText("Opening files or folders...")
        # TODO: Implement file/folder opening
        self.status_label.setText("Ready")
    
    def _on_open_files(self) -> None:
        """Handle the Open Files button."""
        self.status_label.setText("Opening files...")
        
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFiles)
        file_dialog.setNameFilter("Images (*.jpg *.jpeg *.png *.gif *.bmp *.tiff *.webp)")
        
        if file_dialog.exec():
            file_paths = file_dialog.selectedFiles()
            self.status_label.setText(f"Selected {len(file_paths)} files")
            # TODO: Process selected files
        else:
            self.status_label.setText("File selection canceled")
    
    def _on_open_folder(self) -> None:
        """Handle the Open Folder button."""
        self.status_label.setText("Opening folder...")
        
        folder_dialog = QFileDialog(self)
        folder_dialog.setFileMode(QFileDialog.FileMode.Directory)
        folder_dialog.setOption(QFileDialog.Option.ShowDirsOnly, True)
        
        if folder_dialog.exec():
            folder_paths = folder_dialog.selectedFiles()
            if folder_paths:
                self.status_label.setText(f"Selected folder: {folder_paths[0]}")
                # TODO: Process selected folder
        else:
            self.status_label.setText("Folder selection canceled")
    
    def _on_organize(self) -> None:
        """Handle the Organize action."""
        self.status_label.setText("Organizing images...")
        # TODO: Implement image organization
        self.status_label.setText("Ready")
    
    def _on_stop(self) -> None:
        """Handle the Stop action."""
        self.status_label.setText("Stopping current operation...")
        # TODO: Implement stopping current operation
        self.status_label.setText("Ready")
    
    def _on_preferences(self) -> None:
        """Handle the Preferences action."""
        self.status_label.setText("Opening preferences...")
        # TODO: Implement preferences dialog
        self.status_label.setText("Ready")
    
    def _on_about(self) -> None:
        """Handle the About action."""
        self.status_label.setText("Showing about dialog...")
        # TODO: Implement about dialog
        self.status_label.setText("Ready")


def run_gui() -> int:
    """
    Run the graphical user interface.
    
    Returns:
        Exit code
    """
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    return app.exec()