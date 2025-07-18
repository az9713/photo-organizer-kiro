"""
Unit tests for the state monitor.
"""

from unittest.mock import MagicMock, patch

import pytest
from PyQt6.QtCore import QTimer

from photo_organizer.state import ProcessingState, StateChangeEvent
from photo_organizer.ui.state_monitor import StateMonitor


@pytest.fixture
def mock_app_core():
    """Create a mock ApplicationCore."""
    app_core = MagicMock()
    app_core.state_manager = MagicMock()
    app_core.state_manager.state = ProcessingState.IDLE
    app_core.state_manager.can_start.return_value = True
    app_core.state_manager.can_pause.return_value = False
    app_core.state_manager.can_resume.return_value = False
    app_core.state_manager.can_cancel.return_value = False
    return app_core


@pytest.fixture
def app():
    """Create a QApplication instance."""
    from PyQt6.QtWidgets import QApplication
    return QApplication([])


class TestStateMonitor:
    """Tests for the StateMonitor class."""

    def test_init(self, mock_app_core, app) -> None:
        """Test initializing a StateMonitor object."""
        monitor = StateMonitor(mock_app_core)
        
        assert monitor.app_core == mock_app_core
        assert monitor.state == ProcessingState.IDLE
        assert monitor.timer.isActive()
        assert monitor.timer.interval() == 100

    def test_on_state_changed(self, mock_app_core, app) -> None:
        """Test handling state changes."""
        monitor = StateMonitor(mock_app_core)
        
        # Connect to state_changed signal
        mock_callback = MagicMock()
        monitor.state_changed.connect(mock_callback)
        
        # Trigger state change
        monitor._on_state_changed(ProcessingState.RUNNING)
        
        assert monitor.state == ProcessingState.RUNNING
        mock_callback.assert_called_once_with(ProcessingState.RUNNING)

    def test_check_state(self, mock_app_core, app) -> None:
        """Test checking the current state."""
        monitor = StateMonitor(mock_app_core)
        
        # Connect to state_changed signal
        mock_callback = MagicMock()
        monitor.state_changed.connect(mock_callback)
        
        # Change state in app_core
        mock_app_core.state_manager.state = ProcessingState.RUNNING
        
        # Check state
        monitor._check_state()
        
        assert monitor.state == ProcessingState.RUNNING
        mock_callback.assert_called_once_with(ProcessingState.RUNNING)

    def test_start_processing(self, mock_app_core, app) -> None:
        """Test starting processing."""
        monitor = StateMonitor(mock_app_core)
        
        # Set up mock
        mock_app_core.state_manager.transition.return_value = True
        
        # Start processing
        result = monitor.start_processing()
        
        assert result is True
        mock_app_core.state_manager.transition.assert_called_once_with(StateChangeEvent.START)

    def test_start_processing_cannot_start(self, mock_app_core, app) -> None:
        """Test starting processing when it cannot be started."""
        monitor = StateMonitor(mock_app_core)
        
        # Set up mock
        mock_app_core.state_manager.can_start.return_value = False
        
        # Start processing
        result = monitor.start_processing()
        
        assert result is False
        mock_app_core.state_manager.transition.assert_not_called()

    def test_pause_processing(self, mock_app_core, app) -> None:
        """Test pausing processing."""
        monitor = StateMonitor(mock_app_core)
        
        # Set up mock
        mock_app_core.state_manager.can_pause.return_value = True
        
        # Pause processing
        result = monitor.pause_processing()
        
        assert result is True
        mock_app_core.pause.assert_called_once()

    def test_pause_processing_cannot_pause(self, mock_app_core, app) -> None:
        """Test pausing processing when it cannot be paused."""
        monitor = StateMonitor(mock_app_core)
        
        # Set up mock
        mock_app_core.state_manager.can_pause.return_value = False
        
        # Pause processing
        result = monitor.pause_processing()
        
        assert result is False
        mock_app_core.pause.assert_not_called()

    def test_resume_processing(self, mock_app_core, app) -> None:
        """Test resuming processing."""
        monitor = StateMonitor(mock_app_core)
        
        # Set up mock
        mock_app_core.state_manager.can_resume.return_value = True
        
        # Resume processing
        result = monitor.resume_processing()
        
        assert result is True
        mock_app_core.resume.assert_called_once()

    def test_resume_processing_cannot_resume(self, mock_app_core, app) -> None:
        """Test resuming processing when it cannot be resumed."""
        monitor = StateMonitor(mock_app_core)
        
        # Set up mock
        mock_app_core.state_manager.can_resume.return_value = False
        
        # Resume processing
        result = monitor.resume_processing()
        
        assert result is False
        mock_app_core.resume.assert_not_called()

    def test_cancel_processing(self, mock_app_core, app) -> None:
        """Test canceling processing."""
        monitor = StateMonitor(mock_app_core)
        
        # Set up mock
        mock_app_core.state_manager.can_cancel.return_value = True
        
        # Cancel processing
        result = monitor.cancel_processing()
        
        assert result is True
        mock_app_core.cancel.assert_called_once()

    def test_cancel_processing_cannot_cancel(self, mock_app_core, app) -> None:
        """Test canceling processing when it cannot be canceled."""
        monitor = StateMonitor(mock_app_core)
        
        # Set up mock
        mock_app_core.state_manager.can_cancel.return_value = False
        
        # Cancel processing
        result = monitor.cancel_processing()
        
        assert result is False
        mock_app_core.cancel.assert_not_called()

    def test_can_methods(self, mock_app_core, app) -> None:
        """Test the can_* methods."""
        monitor = StateMonitor(mock_app_core)
        
        # Set up mocks
        mock_app_core.state_manager.can_start.return_value = True
        mock_app_core.state_manager.can_pause.return_value = False
        mock_app_core.state_manager.can_resume.return_value = True
        mock_app_core.state_manager.can_cancel.return_value = False
        
        # Check can_* methods
        assert monitor.can_start() is True
        assert monitor.can_pause() is False
        assert monitor.can_resume() is True
        assert monitor.can_cancel() is False