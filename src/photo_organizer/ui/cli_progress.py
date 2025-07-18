"""
Command-line interface progress reporting for the Photo Organizer application.
"""

import sys
import time
from enum import Enum, auto
from typing import Dict, List, Optional, Union


class ProcessingStage(Enum):
    """Stages of the image processing pipeline."""
    INITIALIZING = auto()
    SCANNING = auto()
    ANALYZING = auto()
    CATEGORIZING = auto()
    ORGANIZING = auto()
    REPORTING = auto()
    COMPLETED = auto()


class ProgressBar:
    """A simple progress bar for the command line."""
    
    def __init__(
        self,
        total: int,
        width: int = 50,
        prefix: str = "",
        suffix: str = "",
        fill: str = "█",
        empty: str = "░",
        decimals: int = 1,
        file=sys.stdout,
    ) -> None:
        """
        Initialize a progress bar.
        
        Args:
            total: Total number of items
            width: Width of the progress bar in characters
            prefix: Prefix string
            suffix: Suffix string
            fill: Character to use for filled portion
            empty: Character to use for empty portion
            decimals: Number of decimal places to show in percentage
            file: File to write to
        """
        self.total = total
        self.width = width
        self.prefix = prefix
        self.suffix = suffix
        self.fill = fill
        self.empty = empty
        self.decimals = decimals
        self.file = file
        self.current = 0
        self.start_time = time.time()
        self.last_update_time = self.start_time
        self.update_interval = 0.1  # seconds
    
    def update(self, current: Optional[int] = None) -> None:
        """
        Update the progress bar.
        
        Args:
            current: Current progress value (defaults to incrementing by 1)
        """
        if current is not None:
            self.current = current
        else:
            self.current += 1
        
        # Limit update frequency
        current_time = time.time()
        if current_time - self.last_update_time < self.update_interval and self.current < self.total:
            return
        
        self.last_update_time = current_time
        
        # Calculate progress
        percent = 100 * (self.current / float(self.total))
        filled_length = int(self.width * self.current // self.total)
        bar = self.fill * filled_length + self.empty * (self.width - filled_length)
        
        # Calculate elapsed time and ETA
        elapsed = current_time - self.start_time
        if self.current > 0:
            eta = elapsed * (self.total - self.current) / self.current
            time_info = f" {self._format_time(elapsed)}<{self._format_time(eta)}"
        else:
            time_info = ""
        
        # Print progress bar
        print(
            f"\r{self.prefix} |{bar}| {percent:.{self.decimals}f}% {self.suffix}{time_info}",
            end="",
            file=self.file,
        )
        self.file.flush()
        
        # Print newline when complete
        if self.current >= self.total:
            print(file=self.file)
    
    def _format_time(self, seconds: float) -> str:
        """
        Format time in seconds as a string.
        
        Args:
            seconds: Time in seconds
            
        Returns:
            Formatted time string
        """
        m, s = divmod(int(seconds), 60)
        h, m = divmod(m, 60)
        
        if h > 0:
            return f"{h}h{m:02d}m"
        elif m > 0:
            return f"{m}m{s:02d}s"
        else:
            return f"{s}s"


class CLIProgressReporter:
    """Reporter for progress in the command-line interface."""
    
    def __init__(self, verbose: int = 0, quiet: bool = False) -> None:
        """
        Initialize a CLI progress reporter.
        
        Args:
            verbose: Verbosity level (0-2)
            quiet: Whether to suppress all output
        """
        self.verbose = verbose
        self.quiet = quiet
        self.progress_bars: Dict[str, ProgressBar] = {}
        self.current_stage: Optional[ProcessingStage] = None
        self.stage_start_times: Dict[ProcessingStage, float] = {}
        self.errors: List[Dict[str, str]] = []
    
    def start_stage(self, stage: ProcessingStage) -> None:
        """
        Start a new processing stage.
        
        Args:
            stage: The stage to start
        """
        if self.quiet:
            return
        
        self.current_stage = stage
        self.stage_start_times[stage] = time.time()
        
        if self.verbose > 0:
            stage_name = stage.name.capitalize().replace("_", " ")
            print(f"\n=== {stage_name} ===")
    
    def end_stage(self, stage: ProcessingStage) -> None:
        """
        End a processing stage.
        
        Args:
            stage: The stage to end
        """
        if self.quiet:
            return
        
        if stage in self.stage_start_times:
            elapsed = time.time() - self.stage_start_times[stage]
            
            if self.verbose > 0:
                stage_name = stage.name.capitalize().replace("_", " ")
                print(f"=== {stage_name} completed in {elapsed:.2f} seconds ===\n")
    
    def start_progress(
        self,
        key: str,
        total: int,
        prefix: str = "",
        suffix: str = "",
    ) -> None:
        """
        Start a new progress bar.
        
        Args:
            key: Unique key for the progress bar
            total: Total number of items
            prefix: Prefix string
            suffix: Suffix string
        """
        if self.quiet or self.verbose < 1:
            return
        
        self.progress_bars[key] = ProgressBar(
            total=total,
            prefix=prefix,
            suffix=suffix,
        )
        self.progress_bars[key].update(0)
    
    def update_progress(self, key: str, current: Optional[int] = None) -> None:
        """
        Update a progress bar.
        
        Args:
            key: Key of the progress bar to update
            current: Current progress value
        """
        if self.quiet or self.verbose < 1:
            return
        
        if key in self.progress_bars:
            self.progress_bars[key].update(current)
    
    def log_info(self, message: str) -> None:
        """
        Log an informational message.
        
        Args:
            message: The message to log
        """
        if self.quiet or self.verbose < 1:
            return
        
        print(message)
    
    def log_debug(self, message: str) -> None:
        """
        Log a debug message.
        
        Args:
            message: The message to log
        """
        if self.quiet or self.verbose < 2:
            return
        
        print(f"DEBUG: {message}")
    
    def log_warning(self, message: str) -> None:
        """
        Log a warning message.
        
        Args:
            message: The message to log
        """
        if self.quiet:
            return
        
        print(f"WARNING: {message}", file=sys.stderr)
    
    def log_error(self, message: str, file: Optional[str] = None) -> None:
        """
        Log an error message.
        
        Args:
            message: The error message
            file: The file that caused the error (if applicable)
        """
        print(f"ERROR: {message}", file=sys.stderr)
        
        if file:
            error = {"file": file, "error": message}
            self.errors.append(error)
    
    def get_errors(self) -> List[Dict[str, str]]:
        """
        Get all logged errors.
        
        Returns:
            A list of error dictionaries
        """
        return self.errors