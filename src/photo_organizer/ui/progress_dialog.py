"""
Progress dialog for the Photo Organizer application.
"""

import time
from enum import Enum
from typing import Dict, List, Optional, Tuple

from PyQt6.QtCore import QObject, QThread, Qt, pyqtSignal, pyqtSlot
from PyQt6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from photo_organizer.ui.cli_progress import ProcessingStage


class ProgressDialog(QDialog):
    """Dialog for displaying progress of operations."""
    
    def __init__(self, parent=None) -> None:
        """Initialize the progress dialog."""
        super().__init__(parent)
        
        self.setWindowTitle("Processing Images")
        self.setMinimumSize(500, 400)
        self.setModal(True)
        
        self._create_layout()
        self._setup_connections()
        
        self.canceled = False
    
    def _create_layout(self) -> None:
        """Create the dialog layout."""
        layout = QVBoxLayout(self)
        
        # Status label
        self.status_label = QLabel("Initializing...")
        layout.addWidget(self.status_label)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)
        
        # Stage progress
        stage_layout = QHBoxLayout()
        layout.addLayout(stage_layout)
        
        stage_layout.addWidget(QLabel("Stage:"))
        
        self.stage_label = QLabel("Initializing")
        stage_layout.addWidget(self.stage_label)
        
        self.stage_progress = QProgressBar()
        self.stage_progress.setRange(0, 100)
        self.stage_progress.setValue(0)
        stage_layout.addWidget(self.stage_progress)
        
        # Log output
        layout.addWidget(QLabel("Log:"))
        
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        layout.addWidget(self.log_output)
        
        # Buttons
        button_layout = QHBoxLayout()
        layout.addLayout(button_layout)
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self._on_cancel)
        button_layout.addWidget(self.cancel_button)
        
        self.pause_button = QPushButton("Pause")
        self.pause_button.clicked.connect(self._on_pause)
        button_layout.addWidget(self.pause_button)
        
        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.accept)
        self.close_button.setEnabled(False)
        button_layout.addWidget(self.close_button)
    
    def _setup_connections(self) -> None:
        """Set up signal connections."""
        # These will be connected to the worker thread
        pass
    
    def _on_cancel(self) -> None:
        """Handle the Cancel button."""
        self.canceled = True
        self.log_output.append("Canceling operation...")
        self.cancel_button.setEnabled(False)
        self.pause_button.setEnabled(False)
    
    def _on_pause(self) -> None:
        """Handle the Pause button."""
        if self.pause_button.text() == "Pause":
            self.pause_button.setText("Resume")
            self.log_output.append("Operation paused")
            # TODO: Implement pausing
        else:
            self.pause_button.setText("Pause")
            self.log_output.append("Operation resumed")
            # TODO: Implement resuming
    
    def update_progress(self, value: int, maximum: int = 100) -> None:
        """
        Update the overall progress.
        
        Args:
            value: Current progress value
            maximum: Maximum progress value
        """
        self.progress_bar.setMaximum(maximum)
        self.progress_bar.setValue(value)
    
    def update_stage_progress(self, value: int, maximum: int = 100) -> None:
        """
        Update the stage progress.
        
        Args:
            value: Current progress value
            maximum: Maximum progress value
        """
        self.stage_progress.setMaximum(maximum)
        self.stage_progress.setValue(value)
    
    def set_stage(self, stage: ProcessingStage) -> None:
        """
        Set the current processing stage.
        
        Args:
            stage: Current processing stage
        """
        stage_name = stage.name.capitalize().replace("_", " ")
        self.stage_label.setText(stage_name)
        self.status_label.setText(f"Processing: {stage_name}")
        self.log_output.append(f"\n=== {stage_name} ===")
        self.update_stage_progress(0)
    
    def log_message(self, message: str) -> None:
        """
        Log a message.
        
        Args:
            message: Message to log
        """
        self.log_output.append(message)
    
    def log_error(self, message: str) -> None:
        """
        Log an error message.
        
        Args:
            message: Error message to log
        """
        self.log_output.append(f"ERROR: {message}")
    
    def log_warning(self, message: str) -> None:
        """
        Log a warning message.
        
        Args:
            message: Warning message to log
        """
        self.log_output.append(f"WARNING: {message}")
    
    def complete(self) -> None:
        """Mark the operation as complete."""
        self.progress_bar.setValue(self.progress_bar.maximum())
        self.stage_progress.setValue(self.stage_progress.maximum())
        self.status_label.setText("Processing complete")
        self.log_output.append("\n=== Processing complete ===")
        self.cancel_button.setEnabled(False)
        self.pause_button.setEnabled(False)
        self.close_button.setEnabled(True)


class ProgressWorker(QObject):
    """Worker object for processing images in a separate thread."""
    
    # Signals
    progress_updated = pyqtSignal(int, int)
    stage_progress_updated = pyqtSignal(int, int)
    stage_changed = pyqtSignal(ProcessingStage)
    message_logged = pyqtSignal(str)
    error_logged = pyqtSignal(str)
    warning_logged = pyqtSignal(str)
    processing_completed = pyqtSignal()
    processing_canceled = pyqtSignal()
    
    def __init__(self, input_paths: List[str], output_path: str, options: Dict) -> None:
        """
        Initialize the progress worker.
        
        Args:
            input_paths: List of input file paths
            output_path: Output directory path
            options: Processing options
        """
        super().__init__()
        
        self.input_paths = input_paths
        self.output_path = output_path
        self.options = options
        
        self.canceled = False
        self.paused = False
    
    @pyqtSlot()
    def process(self) -> None:
        """Process the images."""
        try:
            # Simulate processing stages
            self._simulate_processing()
            
            if not self.canceled:
                self.processing_completed.emit()
        except Exception as e:
            self.error_logged.emit(f"Error during processing: {e}")
            self.processing_canceled.emit()
    
    def cancel(self) -> None:
        """Cancel processing."""
        self.canceled = True
    
    def pause(self) -> None:
        """Pause processing."""
        self.paused = True
    
    def resume(self) -> None:
        """Resume processing."""
        self.paused = False
    
    def _simulate_processing(self) -> None:
        """Simulate the processing stages for demonstration."""
        # Initializing
        self.stage_changed.emit(ProcessingStage.INITIALIZING)
        self.message_logged.emit("Initializing processing...")
        time.sleep(0.5)
        
        if self.canceled:
            self.processing_canceled.emit()
            return
        
        # Scanning
        self.stage_changed.emit(ProcessingStage.SCANNING)
        self.message_logged.emit(f"Scanning {len(self.input_paths)} input paths...")
        
        total_files = 100  # Simulated total
        self.progress_updated.emit(0, total_files)
        
        for i in range(total_files):
            if self.canceled:
                self.processing_canceled.emit()
                return
            
            while self.paused:
                time.sleep(0.1)
            
            time.sleep(0.01)
            self.stage_progress_updated.emit(i + 1, total_files)
            self.progress_updated.emit(i + 1, total_files * 5)  # Overall progress
            
            if i % 10 == 0:
                self.message_logged.emit(f"Scanned {i + 1} of {total_files} files")
        
        # Analyzing
        self.stage_changed.emit(ProcessingStage.ANALYZING)
        self.message_logged.emit("Analyzing images...")
        
        for i in range(total_files):
            if self.canceled:
                self.processing_canceled.emit()
                return
            
            while self.paused:
                time.sleep(0.1)
            
            time.sleep(0.05)
            self.stage_progress_updated.emit(i + 1, total_files)
            self.progress_updated.emit(total_files + i + 1, total_files * 5)
            
            if i % 10 == 0:
                self.message_logged.emit(f"Analyzed {i + 1} of {total_files} images")
            
            if i == 10:
                self.warning_logged.emit("Low quality image detected")
            
            if i == 20:
                self.error_logged.emit("Failed to analyze image: bad_image.jpg")
        
        # Categorizing
        self.stage_changed.emit(ProcessingStage.CATEGORIZING)
        self.message_logged.emit("Categorizing images...")
        
        for i in range(total_files):
            if self.canceled:
                self.processing_canceled.emit()
                return
            
            while self.paused:
                time.sleep(0.1)
            
            time.sleep(0.02)
            self.stage_progress_updated.emit(i + 1, total_files)
            self.progress_updated.emit(total_files * 2 + i + 1, total_files * 5)
            
            if i % 10 == 0:
                self.message_logged.emit(f"Categorized {i + 1} of {total_files} images")
        
        # Organizing
        self.stage_changed.emit(ProcessingStage.ORGANIZING)
        self.message_logged.emit("Organizing images...")
        
        for i in range(total_files):
            if self.canceled:
                self.processing_canceled.emit()
                return
            
            while self.paused:
                time.sleep(0.1)
            
            time.sleep(0.03)
            self.stage_progress_updated.emit(i + 1, total_files)
            self.progress_updated.emit(total_files * 3 + i + 1, total_files * 5)
            
            if i % 10 == 0:
                self.message_logged.emit(f"Organized {i + 1} of {total_files} images")
        
        # Reporting
        self.stage_changed.emit(ProcessingStage.REPORTING)
        self.message_logged.emit("Generating report...")
        
        for i in range(100):
            if self.canceled:
                self.processing_canceled.emit()
                return
            
            while self.paused:
                time.sleep(0.1)
            
            time.sleep(0.01)
            self.stage_progress_updated.emit(i + 1, 100)
            self.progress_updated.emit(total_files * 4 + i + 1, total_files * 5)
        
        # Completed
        self.stage_changed.emit(ProcessingStage.COMPLETED)
        self.message_logged.emit("Processing completed successfully")
        self.message_logged.emit(f"Processed {total_files - 1} images (1 error)")


class ProgressManager:
    """Manager for processing images with progress reporting."""
    
    def __init__(self, parent=None) -> None:
        """
        Initialize the progress manager.
        
        Args:
            parent: Parent widget
        """
        self.parent = parent
        self.dialog = None
        self.thread = None
        self.worker = None
    
    def start_processing(self, input_paths: List[str], output_path: str, options: Dict) -> None:
        """
        Start processing images.
        
        Args:
            input_paths: List of input file paths
            output_path: Output directory path
            options: Processing options
        """
        # Create dialog
        self.dialog = ProgressDialog(self.parent)
        
        # Create worker and thread
        self.thread = QThread()
        self.worker = ProgressWorker(input_paths, output_path, options)
        self.worker.moveToThread(self.thread)
        
        # Connect signals
        self.thread.started.connect(self.worker.process)
        self.worker.progress_updated.connect(self.dialog.update_progress)
        self.worker.stage_progress_updated.connect(self.dialog.update_stage_progress)
        self.worker.stage_changed.connect(self.dialog.set_stage)
        self.worker.message_logged.connect(self.dialog.log_message)
        self.worker.error_logged.connect(self.dialog.log_error)
        self.worker.warning_logged.connect(self.dialog.log_warning)
        self.worker.processing_completed.connect(self.dialog.complete)
        self.worker.processing_completed.connect(self.thread.quit)
        self.worker.processing_canceled.connect(self.thread.quit)
        
        # Connect dialog buttons
        self.dialog.cancel_button.clicked.connect(self.worker.cancel)
        self.dialog.pause_button.clicked.connect(self._toggle_pause)
        
        # Start processing
        self.thread.start()
        
        # Show dialog
        self.dialog.exec()
        
        # Clean up
        if self.thread.isRunning():
            self.worker.cancel()
            self.thread.quit()
            self.thread.wait()
    
    def _toggle_pause(self) -> None:
        """Toggle pause/resume state."""
        if self.dialog.pause_button.text() == "Pause":
            self.worker.pause()
        else:
            self.worker.resume()