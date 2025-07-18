"""
State monitoring for the Photo Organizer application.
"""

from typing import Callable, Dict, List, Optional

from PyQt6.QtCore import QObject, QTimer, pyqtSignal, pyqtSlot

from photo_organizer.core import ApplicationCore
from photo_organizer.state import ProcessingState, StateChangeEvent


class StateMonitor(QObject):
    """Monitor for application state changes."""
    
    # Signals
    state_changed = pyqtSignal(ProcessingState)
    progress_updated = pyqtSignal(str, int, int)
    message_logged = pyqtSignal(str)
    error_logged = pyqtSignal(str)
    warning_logged = pyqtSignal(str)
    
    def __init__(self, app_core: ApplicationCore, parent=None) -> None:
        """
        Initialize the state monitor.
        
        Args:
            app_core: Application core
            parent: Parent object
        """
        super().__init__(parent)
        
        self.app_core = app_core
        self.state = app_core.state_manager.state
        
        # Set up state change callbacks
        self._setup_callbacks()
        
        # Set up polling timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._check_state)
        self.timer.start(100)  # Check every 100ms
    
    def _setup_callbacks(self) -> None:
        """Set up callbacks for state changes."""
        # Register state change callbacks
        for state in ProcessingState:
            self.app_core.state_manager.register_state_change_callback(
                state,
                lambda s=state: self._on_state_changed(s)
            )
    
    def _on_state_changed(self, state: ProcessingState) -> None:
        """
        Handle state changes.
        
        Args:
            state: New state
        """
        self.state = state
        self.state_changed.emit(state)
    
    @pyqtSlot()
    def _check_state(self) -> None:
        """Check the current state."""
        current_state = self.app_core.state_manager.state
        
        if current_state != self.state:
            self.state = current_state
            self.state_changed.emit(current_state)
    
    def start_processing(self) -> bool:
        """
        Start processing.
        
        Returns:
            True if the operation was successful, False otherwise
        """
        if self.app_core.state_manager.can_start():
            return self.app_core.state_manager.transition(StateChangeEvent.START)
        return False
    
    def pause_processing(self) -> bool:
        """
        Pause processing.
        
        Returns:
            True if the operation was successful, False otherwise
        """
        if self.app_core.state_manager.can_pause():
            self.app_core.pause()
            return True
        return False
    
    def resume_processing(self) -> bool:
        """
        Resume processing.
        
        Returns:
            True if the operation was successful, False otherwise
        """
        if self.app_core.state_manager.can_resume():
            self.app_core.resume()
            return True
        return False
    
    def cancel_processing(self) -> bool:
        """
        Cancel processing.
        
        Returns:
            True if the operation was successful, False otherwise
        """
        if self.app_core.state_manager.can_cancel():
            self.app_core.cancel()
            return True
        return False
    
    def can_start(self) -> bool:
        """Check if processing can be started."""
        return self.app_core.state_manager.can_start()
    
    def can_pause(self) -> bool:
        """Check if processing can be paused."""
        return self.app_core.state_manager.can_pause()
    
    def can_resume(self) -> bool:
        """Check if processing can be resumed."""
        return self.app_core.state_manager.can_resume()
    
    def can_cancel(self) -> bool:
        """Check if processing can be canceled."""
        return self.app_core.state_manager.can_cancel()