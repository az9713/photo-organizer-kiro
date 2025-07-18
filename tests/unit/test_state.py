"""
Unit tests for the state management system.
"""

import threading
import time
from unittest.mock import MagicMock

import pytest

from photo_organizer.state import ProcessingState, StateChangeEvent, StateManager


class TestStateManager:
    """Tests for the StateManager class."""

    def test_init(self) -> None:
        """Test initializing a StateManager object."""
        manager = StateManager()
        
        assert manager.state == ProcessingState.IDLE
        assert manager.is_idle()
        assert not manager.is_running()
        assert not manager.is_paused()
        assert not manager.is_canceling()
        assert not manager.is_completed()
        assert not manager.is_failed()

    def test_transition_valid(self) -> None:
        """Test valid state transitions."""
        manager = StateManager()
        
        # IDLE -> RUNNING
        assert manager.transition(StateChangeEvent.START)
        assert manager.state == ProcessingState.RUNNING
        assert manager.is_running()
        
        # RUNNING -> PAUSED
        assert manager.transition(StateChangeEvent.PAUSE)
        assert manager.state == ProcessingState.PAUSED
        assert manager.is_paused()
        
        # PAUSED -> RUNNING
        assert manager.transition(StateChangeEvent.RESUME)
        assert manager.state == ProcessingState.RUNNING
        assert manager.is_running()
        
        # RUNNING -> CANCELING
        assert manager.transition(StateChangeEvent.CANCEL)
        assert manager.state == ProcessingState.CANCELING
        assert manager.is_canceling()
        
        # CANCELING -> COMPLETED
        assert manager.transition(StateChangeEvent.COMPLETE)
        assert manager.state == ProcessingState.COMPLETED
        assert manager.is_completed()
        
        # COMPLETED -> RUNNING
        assert manager.transition(StateChangeEvent.START)
        assert manager.state == ProcessingState.RUNNING
        assert manager.is_running()
        
        # RUNNING -> FAILED
        assert manager.transition(StateChangeEvent.FAIL)
        assert manager.state == ProcessingState.FAILED
        assert manager.is_failed()
        
        # FAILED -> RUNNING
        assert manager.transition(StateChangeEvent.START)
        assert manager.state == ProcessingState.RUNNING
        assert manager.is_running()

    def test_transition_invalid(self) -> None:
        """Test invalid state transitions."""
        manager = StateManager()
        
        # IDLE -> PAUSED (invalid)
        assert not manager.transition(StateChangeEvent.PAUSE)
        assert manager.state == ProcessingState.IDLE
        
        # IDLE -> CANCELING (invalid)
        assert not manager.transition(StateChangeEvent.CANCEL)
        assert manager.state == ProcessingState.IDLE
        
        # IDLE -> COMPLETED (invalid)
        assert not manager.transition(StateChangeEvent.COMPLETE)
        assert manager.state == ProcessingState.IDLE
        
        # IDLE -> FAILED (invalid)
        assert not manager.transition(StateChangeEvent.FAIL)
        assert manager.state == ProcessingState.IDLE

    def test_state_change_callback(self) -> None:
        """Test state change callbacks."""
        manager = StateManager()
        
        # Register callbacks
        running_callback = MagicMock()
        paused_callback = MagicMock()
        
        manager.register_state_change_callback(ProcessingState.RUNNING, running_callback)
        manager.register_state_change_callback(ProcessingState.PAUSED, paused_callback)
        
        # Transition to RUNNING
        manager.transition(StateChangeEvent.START)
        running_callback.assert_called_once()
        paused_callback.assert_not_called()
        
        # Transition to PAUSED
        manager.transition(StateChangeEvent.PAUSE)
        running_callback.assert_called_once()
        paused_callback.assert_called_once()

    def test_event_callback(self) -> None:
        """Test event callbacks."""
        manager = StateManager()
        
        # Register callbacks
        start_callback = MagicMock()
        pause_callback = MagicMock()
        
        manager.register_event_callback(StateChangeEvent.START, start_callback)
        manager.register_event_callback(StateChangeEvent.PAUSE, pause_callback)
        
        # Trigger START event
        manager.transition(StateChangeEvent.START)
        start_callback.assert_called_once()
        pause_callback.assert_not_called()
        
        # Trigger PAUSE event
        manager.transition(StateChangeEvent.PAUSE)
        start_callback.assert_called_once()
        pause_callback.assert_called_once()

    def test_callback_exception(self) -> None:
        """Test that exceptions in callbacks are caught."""
        manager = StateManager()
        
        # Register a callback that raises an exception
        def failing_callback():
            raise ValueError("Test exception")
        
        manager.register_state_change_callback(ProcessingState.RUNNING, failing_callback)
        
        # Transition to RUNNING (should not raise an exception)
        manager.transition(StateChangeEvent.START)
        assert manager.state == ProcessingState.RUNNING

    def test_can_methods(self) -> None:
        """Test the can_* methods."""
        manager = StateManager()
        
        # IDLE state
        assert manager.can_start()
        assert not manager.can_pause()
        assert not manager.can_resume()
        assert not manager.can_cancel()
        
        # RUNNING state
        manager.transition(StateChangeEvent.START)
        assert not manager.can_start()
        assert manager.can_pause()
        assert not manager.can_resume()
        assert manager.can_cancel()
        
        # PAUSED state
        manager.transition(StateChangeEvent.PAUSE)
        assert not manager.can_start()
        assert not manager.can_pause()
        assert manager.can_resume()
        assert manager.can_cancel()
        
        # CANCELING state
        manager.transition(StateChangeEvent.RESUME)
        manager.transition(StateChangeEvent.CANCEL)
        assert not manager.can_start()
        assert not manager.can_pause()
        assert not manager.can_resume()
        assert not manager.can_cancel()
        
        # COMPLETED state
        manager.transition(StateChangeEvent.COMPLETE)
        assert manager.can_start()
        assert not manager.can_pause()
        assert not manager.can_resume()
        assert not manager.can_cancel()
        
        # FAILED state
        manager.transition(StateChangeEvent.START)
        manager.transition(StateChangeEvent.FAIL)
        assert manager.can_start()
        assert not manager.can_pause()
        assert not manager.can_resume()
        assert not manager.can_cancel()