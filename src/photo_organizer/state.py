"""
State management for the Photo Organizer application.
"""

import enum
import threading
import time
from typing import Callable, Dict, List, Optional, Set, Tuple, Union


class ProcessingState(enum.Enum):
    """Processing state of the application."""
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    CANCELING = "canceling"
    COMPLETED = "completed"
    FAILED = "failed"


class StateChangeEvent(enum.Enum):
    """Events that can change the processing state."""
    START = "start"
    PAUSE = "pause"
    RESUME = "resume"
    CANCEL = "cancel"
    COMPLETE = "complete"
    FAIL = "fail"


class StateManager:
    """Manager for processing state."""
    
    # State transition table
    # (current_state, event) -> new_state
    _transitions = {
        (ProcessingState.IDLE, StateChangeEvent.START): ProcessingState.RUNNING,
        (ProcessingState.RUNNING, StateChangeEvent.PAUSE): ProcessingState.PAUSED,
        (ProcessingState.RUNNING, StateChangeEvent.CANCEL): ProcessingState.CANCELING,
        (ProcessingState.RUNNING, StateChangeEvent.COMPLETE): ProcessingState.COMPLETED,
        (ProcessingState.RUNNING, StateChangeEvent.FAIL): ProcessingState.FAILED,
        (ProcessingState.PAUSED, StateChangeEvent.RESUME): ProcessingState.RUNNING,
        (ProcessingState.PAUSED, StateChangeEvent.CANCEL): ProcessingState.CANCELING,
        (ProcessingState.CANCELING, StateChangeEvent.COMPLETE): ProcessingState.COMPLETED,
        (ProcessingState.CANCELING, StateChangeEvent.FAIL): ProcessingState.FAILED,
        (ProcessingState.COMPLETED, StateChangeEvent.START): ProcessingState.RUNNING,
        (ProcessingState.FAILED, StateChangeEvent.START): ProcessingState.RUNNING,
    }
    
    def __init__(self) -> None:
        """Initialize the state manager."""
        self._state = ProcessingState.IDLE
        self._lock = threading.RLock()
        self._state_change_callbacks: Dict[ProcessingState, List[Callable[[], None]]] = {}
        self._event_callbacks: Dict[StateChangeEvent, List[Callable[[], None]]] = {}
    
    @property
    def state(self) -> ProcessingState:
        """Get the current state."""
        with self._lock:
            return self._state
    
    def transition(self, event: StateChangeEvent) -> bool:
        """
        Transition to a new state based on an event.
        
        Args:
            event: The event that triggered the transition
            
        Returns:
            True if the transition was successful, False otherwise
        """
        with self._lock:
            # Check if the transition is valid
            transition_key = (self._state, event)
            if transition_key not in self._transitions:
                return False
            
            # Get the new state
            new_state = self._transitions[transition_key]
            
            # Update the state
            old_state = self._state
            self._state = new_state
            
            # Call event callbacks
            self._call_callbacks(self._event_callbacks.get(event, []))
            
            # Call state change callbacks
            self._call_callbacks(self._state_change_callbacks.get(new_state, []))
            
            return True
    
    def register_state_change_callback(
        self,
        state: ProcessingState,
        callback: Callable[[], None],
    ) -> None:
        """
        Register a callback for a state change.
        
        Args:
            state: The state to register the callback for
            callback: The callback to register
        """
        with self._lock:
            if state not in self._state_change_callbacks:
                self._state_change_callbacks[state] = []
            
            self._state_change_callbacks[state].append(callback)
    
    def register_event_callback(
        self,
        event: StateChangeEvent,
        callback: Callable[[], None],
    ) -> None:
        """
        Register a callback for an event.
        
        Args:
            event: The event to register the callback for
            callback: The callback to register
        """
        with self._lock:
            if event not in self._event_callbacks:
                self._event_callbacks[event] = []
            
            self._event_callbacks[event].append(callback)
    
    def _call_callbacks(self, callbacks: List[Callable[[], None]]) -> None:
        """
        Call a list of callbacks.
        
        Args:
            callbacks: The callbacks to call
        """
        for callback in callbacks:
            try:
                callback()
            except Exception as e:
                # Log the exception but don't propagate it
                print(f"Error in state change callback: {e}")
    
    def is_running(self) -> bool:
        """Check if the processing is running."""
        return self.state == ProcessingState.RUNNING
    
    def is_paused(self) -> bool:
        """Check if the processing is paused."""
        return self.state == ProcessingState.PAUSED
    
    def is_canceling(self) -> bool:
        """Check if the processing is being canceled."""
        return self.state == ProcessingState.CANCELING
    
    def is_completed(self) -> bool:
        """Check if the processing is completed."""
        return self.state == ProcessingState.COMPLETED
    
    def is_failed(self) -> bool:
        """Check if the processing has failed."""
        return self.state == ProcessingState.FAILED
    
    def is_idle(self) -> bool:
        """Check if the processing is idle."""
        return self.state == ProcessingState.IDLE
    
    def can_start(self) -> bool:
        """Check if the processing can be started."""
        return self.state in {ProcessingState.IDLE, ProcessingState.COMPLETED, ProcessingState.FAILED}
    
    def can_pause(self) -> bool:
        """Check if the processing can be paused."""
        return self.state == ProcessingState.RUNNING
    
    def can_resume(self) -> bool:
        """Check if the processing can be resumed."""
        return self.state == ProcessingState.PAUSED
    
    def can_cancel(self) -> bool:
        """Check if the processing can be canceled."""
        return self.state in {ProcessingState.RUNNING, ProcessingState.PAUSED}