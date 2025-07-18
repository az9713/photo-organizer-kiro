"""
Unit tests for the GUI application.
"""

import sys
from unittest.mock import MagicMock, patch

import pytest
from PyQt6.QtWidgets import QApplication, QFileDialog, QMainWindow

from photo_organizer.ui.gui_app import MainWindow


@pytest.fixture
def app():
    """Create a QApplication instance for testing."""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app


@pytest.fixture
def main_window(app):
    """Create a MainWindow instance for testing."""
    window = MainWindow()
    yield window
    window.close()


class TestMainWindow:
    """Tests for the MainWindow class."""

    def test_init(self, main_window):
        """Test initializing a MainWindow object."""
        assert isinstance(main_window, QMainWindow)
        assert main_window.windowTitle().startswith("Photo Organizer")
        assert main_window.minimumSize().width() >= 800
        assert main_window.minimumSize().height() >= 600

    def test_menu_bar(self, main_window):
        """Test that the menu bar is created."""
        menu_bar = main_window.menuBar()
        assert menu_bar is not None
        
        # Check that the expected menus exist
        menu_titles = [menu.title() for menu in menu_bar.findChildren(QMenu)]
        assert "&File" in menu_titles
        assert "&Edit" in menu_titles
        assert "&Help" in menu_titles

    def test_tool_bar(self, main_window):
        """Test that the tool bar is created."""
        tool_bars = main_window.findChildren(QToolBar)
        assert len(tool_bars) > 0

    def test_status_bar(self, main_window):
        """Test that the status bar is created."""
        status_bar = main_window.statusBar()
        assert status_bar is not None
        assert main_window.status_label is not None

    def test_central_widget(self, main_window):
        """Test that the central widget is created."""
        central_widget = main_window.centralWidget()
        assert central_widget is not None

    @patch.object(QFileDialog, 'exec')
    @patch.object(QFileDialog, 'selectedFiles')
    def test_on_open_files(self, mock_selected_files, mock_exec, main_window):
        """Test opening files."""
        mock_exec.return_value = True
        mock_selected_files.return_value = ["file1.jpg", "file2.jpg"]
        
        main_window._on_open_files()
        
        assert mock_exec.called
        assert mock_selected_files.called
        assert "Selected 2 files" in main_window.status_label.text()

    @patch.object(QFileDialog, 'exec')
    @patch.object(QFileDialog, 'selectedFiles')
    def test_on_open_folder(self, mock_selected_files, mock_exec, main_window):
        """Test opening a folder."""
        mock_exec.return_value = True
        mock_selected_files.return_value = ["/path/to/folder"]
        
        main_window._on_open_folder()
        
        assert mock_exec.called
        assert mock_selected_files.called
        assert "Selected folder: /path/to/folder" in main_window.status_label.text()

    def test_on_organize(self, main_window):
        """Test organizing images."""
        main_window._on_organize()
        assert "Ready" in main_window.status_label.text()

    def test_on_stop(self, main_window):
        """Test stopping the current operation."""
        main_window._on_stop()
        assert "Ready" in main_window.status_label.text()

    def test_on_preferences(self, main_window):
        """Test opening preferences."""
        main_window._on_preferences()
        assert "Ready" in main_window.status_label.text()

    def test_on_about(self, main_window):
        """Test showing the about dialog."""
        main_window._on_about()
        assert "Ready" in main_window.status_label.text()


def test_run_gui():
    """Test running the GUI."""
    with patch('photo_organizer.ui.gui_app.QApplication') as mock_app:
        mock_app_instance = MagicMock()
        mock_app.return_value = mock_app_instance
        mock_app_instance.exec.return_value = 0
        
        from photo_organizer.ui.gui_app import run_gui
        result = run_gui()
        
        assert mock_app.called
        assert mock_app_instance.exec.called
        assert result == 0