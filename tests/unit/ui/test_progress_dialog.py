"""
Unit tests for the progress dialog.
"""

from unittest.mock import MagicMock, patch

import pytest
from PyQt6.QtCore import QThread
from PyQt6.QtWidgets import QApplication, QDialog

from photo_organizer.ui.cli_progress import ProcessingStage
from photo_organizer.ui.progress_dialog import ProgressDialog, ProgressManager, ProgressWorker


@pytest.fixture
def app():
    """Create a QApplication instance."""
    return QApplication([])


class TestProgressDialog:
    """Tests for the ProgressDialog class."""

    def test_init(self, app) -> None:
        """Test initializing a ProgressDialog object."""
        dialog = ProgressDialog()
        assert dialog.windowTitle() == "Processing Images"
        assert dialog.minimumSize().width() >= 500
        assert dialog.minimumSize().height() >= 400
        assert dialog.isModal()
        assert not dialog.canceled

    def test_update_progress(self, app) -> None:
        """Test updating progress."""
        dialog = ProgressDialog()
        
        dialog.update_progress(50, 100)
        
        assert dialog.progress_bar.maximum() == 100
        assert dialog.progress_bar.value() == 50

    def test_update_stage_progress(self, app) -> None:
        """Test updating stage progress."""
        dialog = ProgressDialog()
        
        dialog.update_stage_progress(75, 100)
        
        assert dialog.stage_progress.maximum() == 100
        assert dialog.stage_progress.value() == 75

    def test_set_stage(self, app) -> None:
        """Test setting the current stage."""
        dialog = ProgressDialog()
        
        dialog.set_stage(ProcessingStage.ANALYZING)
        
        assert dialog.stage_label.text() == "Analyzing"
        assert dialog.status_label.text() == "Processing: Analyzing"
        assert "=== Analyzing ===" in dialog.log_output.toPlainText()

    def test_log_message(self, app) -> None:
        """Test logging a message."""
        dialog = ProgressDialog()
        
        dialog.log_message("Test message")
        
        assert "Test message" in dialog.log_output.toPlainText()

    def test_log_error(self, app) -> None:
        """Test logging an error message."""
        dialog = ProgressDialog()
        
        dialog.log_error("Test error")
        
        assert "ERROR: Test error" in dialog.log_output.toPlainText()

    def test_log_warning(self, app) -> None:
        """Test logging a warning message."""
        dialog = ProgressDialog()
        
        dialog.log_warning("Test warning")
        
        assert "WARNING: Test warning" in dialog.log_output.toPlainText()

    def test_complete(self, app) -> None:
        """Test marking the operation as complete."""
        dialog = ProgressDialog()
        dialog.progress_bar.setMaximum(100)
        dialog.stage_progress.setMaximum(100)
        
        dialog.complete()
        
        assert dialog.progress_bar.value() == 100
        assert dialog.stage_progress.value() == 100
        assert dialog.status_label.text() == "Processing complete"
        assert "=== Processing complete ===" in dialog.log_output.toPlainText()
        assert not dialog.cancel_button.isEnabled()
        assert not dialog.pause_button.isEnabled()
        assert dialog.close_button.isEnabled()

    def test_on_cancel(self, app) -> None:
        """Test handling the Cancel button."""
        dialog = ProgressDialog()
        
        dialog._on_cancel()
        
        assert dialog.canceled
        assert "Canceling operation..." in dialog.log_output.toPlainText()
        assert not dialog.cancel_button.isEnabled()
        assert not dialog.pause_button.isEnabled()

    def test_on_pause(self, app) -> None:
        """Test handling the Pause button."""
        dialog = ProgressDialog()
        
        # Test pausing
        dialog._on_pause()
        
        assert dialog.pause_button.text() == "Resume"
        assert "Operation paused" in dialog.log_output.toPlainText()
        
        # Test resuming
        dialog._on_pause()
        
        assert dialog.pause_button.text() == "Pause"
        assert "Operation resumed" in dialog.log_output.toPlainText()


class TestProgressWorker:
    """Tests for the ProgressWorker class."""

    def test_init(self) -> None:
        """Test initializing a ProgressWorker object."""
        worker = ProgressWorker(["input1.jpg", "input2.jpg"], "output", {"option": "value"})
        
        assert worker.input_paths == ["input1.jpg", "input2.jpg"]
        assert worker.output_path == "output"
        assert worker.options == {"option": "value"}
        assert not worker.canceled
        assert not worker.paused

    def test_cancel(self) -> None:
        """Test canceling processing."""
        worker = ProgressWorker([], "", {})
        
        worker.cancel()
        
        assert worker.canceled

    def test_pause_resume(self) -> None:
        """Test pausing and resuming processing."""
        worker = ProgressWorker([], "", {})
        
        worker.pause()
        assert worker.paused
        
        worker.resume()
        assert not worker.paused

    @patch("time.sleep")
    def test_process_canceled(self, mock_sleep) -> None:
        """Test processing with cancellation."""
        worker = ProgressWorker(["input.jpg"], "output", {})
        
        # Mock signals
        worker.stage_changed = MagicMock()
        worker.message_logged = MagicMock()
        worker.processing_canceled = MagicMock()
        worker.processing_completed = MagicMock()
        
        # Cancel immediately after starting
        worker.canceled = True
        
        worker.process()
        
        worker.stage_changed.assert_called_once_with(ProcessingStage.INITIALIZING)
        worker.message_logged.assert_called_once()
        worker.processing_canceled.assert_called_once()
        worker.processing_completed.assert_not_called()


class TestProgressManager:
    """Tests for the ProgressManager class."""

    def test_init(self) -> None:
        """Test initializing a ProgressManager object."""
        manager = ProgressManager()
        
        assert manager.parent is None
        assert manager.dialog is None
        assert manager.thread is None
        assert manager.worker is None

    @patch("photo_organizer.ui.progress_dialog.ProgressDialog")
    @patch("photo_organizer.ui.progress_dialog.QThread")
    @patch("photo_organizer.ui.progress_dialog.ProgressWorker")
    def test_start_processing(self, mock_worker_class, mock_thread_class, mock_dialog_class) -> None:
        """Test starting processing."""
        # Mock objects
        mock_dialog = MagicMock()
        mock_dialog_class.return_value = mock_dialog
        
        mock_thread = MagicMock()
        mock_thread_class.return_value = mock_thread
        
        mock_worker = MagicMock()
        mock_worker_class.return_value = mock_worker
        
        # Create manager and start processing
        manager = ProgressManager()
        manager.start_processing(["input.jpg"], "output", {"option": "value"})
        
        # Check that objects were created
        mock_dialog_class.assert_called_once()
        mock_thread_class.assert_called_once()
        mock_worker_class.assert_called_once_with(["input.jpg"], "output", {"option": "value"})
        
        # Check that worker was moved to thread
        mock_worker.moveToThread.assert_called_once_with(mock_thread)
        
        # Check that signals were connected
        assert mock_thread.started.connect.called
        assert mock_worker.progress_updated.connect.called
        assert mock_worker.stage_progress_updated.connect.called
        assert mock_worker.stage_changed.connect.called
        assert mock_worker.message_logged.connect.called
        assert mock_worker.error_logged.connect.called
        assert mock_worker.warning_logged.connect.called
        assert mock_worker.processing_completed.connect.called
        assert mock_worker.processing_canceled.connect.called
        
        # Check that thread was started
        mock_thread.start.assert_called_once()
        
        # Check that dialog was shown
        mock_dialog.exec.assert_called_once()
        
        # Check cleanup
        mock_thread.isRunning.assert_called_once()

    def test_toggle_pause(self) -> None:
        """Test toggling pause/resume state."""
        manager = ProgressManager()
        
        # Set up mocks
        manager.dialog = MagicMock()
        manager.worker = MagicMock()
        
        # Test pausing
        manager.dialog.pause_button.text.return_value = "Pause"
        manager._toggle_pause()
        manager.worker.pause.assert_called_once()
        manager.worker.resume.assert_not_called()
        
        # Test resuming
        manager.dialog.pause_button.text.return_value = "Resume"
        manager._toggle_pause()
        manager.worker.resume.assert_called_once()