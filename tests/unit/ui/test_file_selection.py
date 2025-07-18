"""
Unit tests for the file selection interface.
"""

import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from PyQt6.QtCore import QMimeData, QUrl, Qt
from PyQt6.QtGui import QDragEnterEvent, QDropEvent
from PyQt6.QtWidgets import QApplication, QFileDialog

from photo_organizer.ui.file_selection import DropArea, FileSelectionWidget


@pytest.fixture
def app():
    """Create a QApplication instance for testing."""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app


@pytest.fixture
def drop_area(app):
    """Create a DropArea instance for testing."""
    widget = DropArea()
    yield widget
    widget.deleteLater()


@pytest.fixture
def file_selection_widget(app):
    """Create a FileSelectionWidget instance for testing."""
    widget = FileSelectionWidget()
    yield widget
    widget.deleteLater()


class TestDropArea:
    """Tests for the DropArea class."""

    def test_init(self, drop_area):
        """Test initializing a DropArea object."""
        assert drop_area.acceptDrops()
        assert drop_area.minimumSize().width() > 0
        assert drop_area.minimumSize().height() > 0

    def test_drag_enter_event_with_urls(self, drop_area):
        """Test drag enter event with URLs."""
        mime_data = QMimeData()
        mime_data.setUrls([QUrl.fromLocalFile("/path/to/file.jpg")])
        
        event = MagicMock(spec=QDragEnterEvent)
        event.mimeData.return_value = mime_data
        
        drop_area.dragEnterEvent(event)
        
        event.acceptProposedAction.assert_called_once()

    def test_drag_enter_event_without_urls(self, drop_area):
        """Test drag enter event without URLs."""
        mime_data = QMimeData()
        
        event = MagicMock(spec=QDragEnterEvent)
        event.mimeData.return_value = mime_data
        
        drop_area.dragEnterEvent(event)
        
        event.ignore.assert_called_once()

    def test_drop_event_with_urls(self, drop_area):
        """Test drop event with URLs."""
        mime_data = QMimeData()
        mime_data.setUrls([
            QUrl.fromLocalFile("/path/to/file1.jpg"),
            QUrl.fromLocalFile("/path/to/file2.jpg"),
        ])
        
        event = MagicMock(spec=QDropEvent)
        event.mimeData.return_value = mime_data
        
        # Connect to the filesDropped signal
        callback = MagicMock()
        drop_area.filesDropped.connect(callback)
        
        drop_area.dropEvent(event)
        
        event.acceptProposedAction.assert_called_once()
        callback.assert_called_once_with(["/path/to/file1.jpg", "/path/to/file2.jpg"])

    def test_drop_event_without_urls(self, drop_area):
        """Test drop event without URLs."""
        mime_data = QMimeData()
        
        event = MagicMock(spec=QDropEvent)
        event.mimeData.return_value = mime_data
        
        drop_area.dropEvent(event)
        
        event.ignore.assert_called_once()


class TestFileSelectionWidget:
    """Tests for the FileSelectionWidget class."""

    def test_init(self, file_selection_widget):
        """Test initializing a FileSelectionWidget object."""
        assert hasattr(file_selection_widget, "drop_area")
        assert hasattr(file_selection_widget, "file_list")
        assert hasattr(file_selection_widget, "add_files_button")
        assert hasattr(file_selection_widget, "add_folder_button")
        assert hasattr(file_selection_widget, "clear_button")
        assert hasattr(file_selection_widget, "remove_selected_button")

    @patch.object(QFileDialog, 'exec')
    @patch.object(QFileDialog, 'selectedFiles')
    def test_on_add_files(self, mock_selected_files, mock_exec, file_selection_widget):
        """Test adding files."""
        mock_exec.return_value = True
        mock_selected_files.return_value = ["/path/to/file1.jpg", "/path/to/file2.jpg"]
        
        # Connect to the selectionChanged signal
        callback = MagicMock()
        file_selection_widget.selectionChanged.connect(callback)
        
        # Mock _add_file to avoid file system access
        with patch.object(file_selection_widget, '_add_file') as mock_add_file:
            file_selection_widget._on_add_files()
            
            assert mock_exec.called
            assert mock_selected_files.called
            assert mock_add_file.call_count == 2
            mock_add_file.assert_any_call("/path/to/file1.jpg")
            mock_add_file.assert_any_call("/path/to/file2.jpg")

    @patch.object(QFileDialog, 'exec')
    @patch.object(QFileDialog, 'selectedFiles')
    def test_on_add_folder(self, mock_selected_files, mock_exec, file_selection_widget):
        """Test adding a folder."""
        mock_exec.return_value = True
        mock_selected_files.return_value = ["/path/to/folder"]
        
        # Connect to the selectionChanged signal
        callback = MagicMock()
        file_selection_widget.selectionChanged.connect(callback)
        
        # Mock _add_folder to avoid file system access
        with patch.object(file_selection_widget, '_add_folder') as mock_add_folder:
            file_selection_widget._on_add_folder()
            
            assert mock_exec.called
            assert mock_selected_files.called
            mock_add_folder.assert_called_once_with("/path/to/folder")

    def test_on_clear(self, file_selection_widget):
        """Test clearing the selection."""
        # Add some files to the selection
        file_selection_widget._selected_paths = {"/path/to/file1.jpg", "/path/to/file2.jpg"}
        
        # Mock the file list
        file_selection_widget.file_list.clear = MagicMock()
        
        # Connect to the selectionChanged signal
        callback = MagicMock()
        file_selection_widget.selectionChanged.connect(callback)
        
        file_selection_widget._on_clear()
        
        assert file_selection_widget.file_list.clear.called
        assert len(file_selection_widget._selected_paths) == 0
        assert callback.called

    def test_on_remove_selected(self, file_selection_widget):
        """Test removing selected files."""
        # Add some files to the selection
        file_selection_widget._selected_paths = {"/path/to/file1.jpg", "/path/to/file2.jpg"}
        
        # Mock the file list
        file_selection_widget.file_list.selectedItems = MagicMock(return_value=[
            MagicMock(data=MagicMock(return_value="/path/to/file1.jpg")),
        ])
        file_selection_widget.file_list.takeItem = MagicMock()
        file_selection_widget.file_list.row = MagicMock(return_value=0)
        
        # Connect to the selectionChanged signal
        callback = MagicMock()
        file_selection_widget.selectionChanged.connect(callback)
        
        file_selection_widget._on_remove_selected()
        
        assert file_selection_widget.file_list.takeItem.called
        assert "/path/to/file1.jpg" not in file_selection_widget._selected_paths
        assert "/path/to/file2.jpg" in file_selection_widget._selected_paths
        assert callback.called

    @patch('os.path.isdir')
    @patch('os.path.isfile')
    def test_add_paths(self, mock_isfile, mock_isdir, file_selection_widget):
        """Test adding paths."""
        mock_isdir.side_effect = lambda path: path == "/path/to/folder"
        mock_isfile.side_effect = lambda path: path != "/path/to/folder"
        
        # Mock _add_folder and _add_file to avoid file system access
        with patch.object(file_selection_widget, '_add_folder') as mock_add_folder:
            with patch.object(file_selection_widget, '_add_file') as mock_add_file:
                file_selection_widget._add_paths([
                    "/path/to/folder",
                    "/path/to/file1.jpg",
                    "/path/to/file2.jpg",
                ])
                
                mock_add_folder.assert_called_once_with("/path/to/folder")
                assert mock_add_file.call_count == 2
                mock_add_file.assert_any_call("/path/to/file1.jpg")
                mock_add_file.assert_any_call("/path/to/file2.jpg")

    @patch('os.walk')
    def test_add_folder(self, mock_walk, file_selection_widget):
        """Test adding a folder."""
        mock_walk.return_value = [
            ("/path/to/folder", [], ["file1.jpg", "file2.jpg"]),
            ("/path/to/folder/subfolder", [], ["file3.jpg"]),
        ]
        
        # Mock _add_file to avoid file system access
        with patch.object(file_selection_widget, '_add_file') as mock_add_file:
            file_selection_widget._add_folder("/path/to/folder")
            
            assert mock_add_file.call_count == 3
            mock_add_file.assert_any_call("/path/to/folder/file1.jpg")
            mock_add_file.assert_any_call("/path/to/folder/file2.jpg")
            mock_add_file.assert_any_call("/path/to/folder/subfolder/file3.jpg")

    @patch('os.path.splitext')
    def test_add_file(self, mock_splitext, file_selection_widget):
        """Test adding a file."""
        mock_splitext.return_value = ("file1", ".jpg")
        
        # Mock the file list
        file_selection_widget.file_list.addItem = MagicMock()
        
        # Connect to the selectionChanged signal
        callback = MagicMock()
        file_selection_widget.selectionChanged.connect(callback)
        
        file_selection_widget._add_file("/path/to/file1.jpg")
        
        assert "/path/to/file1.jpg" in file_selection_widget._selected_paths
        assert file_selection_widget.file_list.addItem.called
        assert callback.called

    @patch('os.path.splitext')
    def test_add_file_unsupported_extension(self, mock_splitext, file_selection_widget):
        """Test adding a file with an unsupported extension."""
        mock_splitext.return_value = ("file1", ".txt")
        
        # Mock the file list
        file_selection_widget.file_list.addItem = MagicMock()
        
        # Connect to the selectionChanged signal
        callback = MagicMock()
        file_selection_widget.selectionChanged.connect(callback)
        
        file_selection_widget._add_file("/path/to/file1.txt")
        
        assert "/path/to/file1.txt" not in file_selection_widget._selected_paths
        assert not file_selection_widget.file_list.addItem.called
        assert not callback.called

    @patch('os.path.splitext')
    def test_add_file_duplicate(self, mock_splitext, file_selection_widget):
        """Test adding a duplicate file."""
        mock_splitext.return_value = ("file1", ".jpg")
        
        # Add the file to the selection
        file_selection_widget._selected_paths.add("/path/to/file1.jpg")
        
        # Mock the file list
        file_selection_widget.file_list.addItem = MagicMock()
        
        # Connect to the selectionChanged signal
        callback = MagicMock()
        file_selection_widget.selectionChanged.connect(callback)
        
        file_selection_widget._add_file("/path/to/file1.jpg")
        
        assert "/path/to/file1.jpg" in file_selection_widget._selected_paths
        assert not file_selection_widget.file_list.addItem.called
        assert not callback.called

    def test_get_selected_paths(self, file_selection_widget):
        """Test getting selected paths."""
        file_selection_widget._selected_paths = {"/path/to/file1.jpg", "/path/to/file2.jpg"}
        
        paths = file_selection_widget.get_selected_paths()
        
        assert len(paths) == 2
        assert "/path/to/file1.jpg" in paths
        assert "/path/to/file2.jpg" in paths