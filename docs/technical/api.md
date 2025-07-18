# Photo Organizer API Documentation

This document provides detailed information about the Photo Organizer API, including classes, methods, and interfaces.

## Core API

### ApplicationCore

The `ApplicationCore` class is the main entry point for the application logic.

```python
class ApplicationCore:
    def __init__(
        self,
        progress_reporter: Optional[CLIProgressReporter] = None,
        parallel_processing: bool = False,
        max_workers: int = 4,
    ) -> None:
        """
        Initialize the application core.
        
        Args:
            progress_reporter: Reporter for progress updates
            parallel_processing: Whether to use parallel processing
            max_workers: Maximum number of worker threads for parallel processing
        """
        pass
    
    def process_images(
        self,
        input_paths: List[str],
        output_path: str,
        options: Dict[str, Any],
    ) -> Tuple[bool, Optional[Report]]:
        """
        Process images from input paths to output path.
        
        Args:
            input_paths: List of input file or directory paths
            output_path: Output directory path
            options: Processing options
            
        Returns:
            A tuple of (success, report)
        """
        pass
    
    def cancel(self) -> None:
        """Cancel processing."""
        pass
    
    def pause(self) -> None:
        """Pause processing."""
        pass
    
    def resume(self) -> None:
        """Resume processing."""
        pass
```

#### Processing Options

The `process_images` method accepts a dictionary of options:

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `recursive` | bool | False | Process subdirectories recursively |
| `parallel_processing` | bool | False | Enable parallel processing |
| `max_workers` | int | 4 | Maximum number of worker threads |
| `similarity_threshold` | float | 0.7 | Threshold for image similarity (0.0 to 1.0) |
| `max_category_depth` | int | 3 | Maximum depth of category hierarchy |
| `report_format` | ReportFormat or List[ReportFormat] | ReportFormat.HTML | Format(s) for the report |
| `report_path` | str or Dict[ReportFormat, str] | None | Path(s) for the report file(s) |

## Models

### Image

The `Image` class represents an image file with its metadata and analysis results.

```python
class Image:
    def __init__(self, path: Union[str, Path]) -> None:
        """
        Initialize an Image object.
        
        Args:
            path: Path to the image file
        """
        pass
    
    @property
    def format(self) -> ImageFormat:
        """Get the image format."""
        pass
    
    @property
    def size(self) -> int:
        """Get the file size in bytes."""
        pass
    
    @property
    def dimensions(self) -> Optional[Tuple[int, int]]:
        """Get the image dimensions (width, height)."""
        pass
    
    @property
    def filename(self) -> str:
        """Get the filename without path."""
        pass
    
    @property
    def basename(self) -> str:
        """Get the filename without extension."""
        pass
```

### Category

The `Category` class represents a category for grouping similar images.

```python
@dataclass
class Category:
    name: str
    description: str = ""
    tags: List[str] = field(default_factory=list)
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    parent_id: Optional[str] = None
    child_ids: Set[str] = field(default_factory=set)
    image_ids: Set[str] = field(default_factory=set)
    
    def add_child(self, child: Category) -> None:
        """
        Add a child category to this category.
        
        Args:
            child: The child category to add
        """
        pass
    
    def remove_child(self, child: Category) -> None:
        """
        Remove a child category from this category.
        
        Args:
            child: The child category to remove
        """
        pass
    
    def add_image(self, image_id: str) -> None:
        """
        Add an image to this category.
        
        Args:
            image_id: The ID of the image to add
        """
        pass
    
    def remove_image(self, image_id: str) -> None:
        """
        Remove an image from this category.
        
        Args:
            image_id: The ID of the image to remove
        """
        pass
```

### CategoryTree

The `CategoryTree` class represents a hierarchical tree of categories.

```python
class CategoryTree:
    def __init__(self) -> None:
        """Initialize a CategoryTree object."""
        pass
    
    def add_category(self, category: Category) -> None:
        """
        Add a category to the tree.
        
        Args:
            category: The category to add
        """
        pass
    
    def get_category(self, category_id: str) -> Optional[Category]:
        """
        Get a category by ID.
        
        Args:
            category_id: The ID of the category to get
            
        Returns:
            The category with the given ID, or None if not found
        """
        pass
    
    def remove_category(self, category_id: str) -> None:
        """
        Remove a category from the tree.
        
        Args:
            category_id: The ID of the category to remove
        """
        pass
    
    def add_image_to_category(self, image_id: str, category_id: str) -> None:
        """
        Add an image to a category.
        
        Args:
            image_id: The ID of the image to add
            category_id: The ID of the category to add the image to
        """
        pass
    
    def remove_image_from_category(self, image_id: str, category_id: str) -> None:
        """
        Remove an image from a category.
        
        Args:
            image_id: The ID of the image to remove
            category_id: The ID of the category to remove the image from
        """
        pass
```

## Services

### ImageAnalysisService

The `ImageAnalysisService` class coordinates the analysis of images.

```python
class ImageAnalysisService:
    def __init__(self) -> None:
        """Initialize an ImageAnalysisService object."""
        pass
    
    def analyze_image(self, image: Image) -> None:
        """
        Analyze an image.
        
        Args:
            image: The image to analyze
        """
        pass
```

### CategorizationService

The `CategorizationService` class categorizes images based on their content.

```python
class CategorizationService:
    def __init__(self) -> None:
        """Initialize a CategorizationService object."""
        pass
    
    def categorize_images(
        self,
        images: List[Image],
        similarity_threshold: float = 0.7,
        max_category_depth: int = 3,
        progress_callback: Optional[Callable[[int], None]] = None,
        cancel_check: Optional[Callable[[], bool]] = None,
        pause_check: Optional[Callable[[], bool]] = None,
    ) -> CategoryTree:
        """
        Categorize images.
        
        Args:
            images: List of images to categorize
            similarity_threshold: Threshold for image similarity (0.0 to 1.0)
            max_category_depth: Maximum depth of category hierarchy
            progress_callback: Callback for progress updates
            cancel_check: Function to check if processing should be canceled
            pause_check: Function to check if processing should be paused
            
        Returns:
            A CategoryTree with categorized images
        """
        pass
```

### ReportingService

The `ReportingService` class generates reports of the reorganization process.

```python
class ReportingService:
    def __init__(self) -> None:
        """Initialize a ReportingService object."""
        pass
    
    def generate_report(
        self,
        folder_structure: FolderNode,
        file_mappings: List[FileMapping],
        processing_time: float,
        total_files: int,
        processed_files: int,
        skipped_files: int,
        error_count: int,
        errors: Optional[List[Dict[str, str]]] = None,
    ) -> Report:
        """
        Generate a report of the reorganization process.
        
        Args:
            folder_structure: The folder structure created during reorganization
            file_mappings: Mappings from original files to new files
            processing_time: Time taken for processing in seconds
            total_files: Total number of files processed
            processed_files: Number of files successfully processed
            skipped_files: Number of files skipped
            error_count: Number of errors encountered
            errors: List of errors encountered during processing
            
        Returns:
            A Report object containing the report data
        """
        pass
    
    def save_report(self, report: Report, format: ReportFormat, output_path: str) -> None:
        """
        Save a report to a file.
        
        Args:
            report: The report to save
            format: The format to save the report in
            output_path: The path to save the report to
        """
        pass
```

## User Interface

### CLIParser

The `CLIParser` class parses command-line arguments.

```python
class CLIParser:
    def __init__(self) -> None:
        """Initialize the CLI parser."""
        pass
    
    def parse_args(self, args: Optional[List[str]] = None) -> argparse.Namespace:
        """
        Parse command-line arguments.
        
        Args:
            args: Command-line arguments to parse (defaults to sys.argv[1:])
            
        Returns:
            Parsed arguments as a Namespace object
        """
        pass
    
    def validate_args(self, args: argparse.Namespace) -> Tuple[bool, Optional[str]]:
        """
        Validate parsed arguments.
        
        Args:
            args: Parsed arguments to validate
            
        Returns:
            A tuple of (is_valid, error_message)
        """
        pass
    
    def get_processing_options(self, args: argparse.Namespace) -> Dict[str, Any]:
        """
        Get processing options from parsed arguments.
        
        Args:
            args: Parsed arguments
            
        Returns:
            A dictionary of processing options
        """
        pass
```

### CLIProgressReporter

The `CLIProgressReporter` class reports progress and errors to the console.

```python
class CLIProgressReporter:
    def __init__(self, verbose: int = 0, quiet: bool = False) -> None:
        """
        Initialize a CLI progress reporter.
        
        Args:
            verbose: Verbosity level (0-2)
            quiet: Whether to suppress all output
        """
        pass
    
    def start_stage(self, stage: ProcessingStage) -> None:
        """
        Start a new processing stage.
        
        Args:
            stage: The stage to start
        """
        pass
    
    def end_stage(self, stage: ProcessingStage) -> None:
        """
        End a processing stage.
        
        Args:
            stage: The stage to end
        """
        pass
    
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
        pass
    
    def update_progress(self, key: str, current: Optional[int] = None) -> None:
        """
        Update a progress bar.
        
        Args:
            key: Key of the progress bar to update
            current: Current progress value
        """
        pass
    
    def log_info(self, message: str) -> None:
        """
        Log an informational message.
        
        Args:
            message: The message to log
        """
        pass
    
    def log_debug(self, message: str) -> None:
        """
        Log a debug message.
        
        Args:
            message: The message to log
        """
        pass
    
    def log_warning(self, message: str) -> None:
        """
        Log a warning message.
        
        Args:
            message: The message to log
        """
        pass
    
    def log_error(self, message: str, file: Optional[str] = None) -> None:
        """
        Log an error message.
        
        Args:
            message: The error message
            file: The file that caused the error (if applicable)
        """
        pass
```

## Parallel Processing

### WorkerPool

The `WorkerPool` class manages a pool of worker threads for parallel processing.

```python
class WorkerPool:
    def __init__(
        self,
        max_workers: int = 4,
        name: str = "WorkerPool",
        progress_callback: Optional[Callable[[int, int], None]] = None,
    ) -> None:
        """
        Initialize a worker pool.
        
        Args:
            max_workers: Maximum number of worker threads
            name: Name of the worker pool
            progress_callback: Callback for progress updates
        """
        pass
    
    def map(
        self,
        func: Callable[[T], U],
        items: List[T],
        timeout: Optional[float] = None,
    ) -> List[U]:
        """
        Apply a function to each item in parallel.
        
        Args:
            func: Function to apply
            items: Items to process
            timeout: Timeout in seconds
            
        Returns:
            List of results
        """
        pass
    
    def cancel(self) -> None:
        """Cancel all tasks."""
        pass
    
    def pause(self) -> None:
        """Pause all tasks."""
        pass
    
    def resume(self) -> None:
        """Resume all tasks."""
        pass
```

### TaskScheduler

The `TaskScheduler` class schedules processing tasks.

```python
class TaskScheduler:
    def __init__(
        self,
        max_workers: int = 4,
        progress_callback: Optional[Callable[[str, int, int], None]] = None,
        cancel_check: Optional[Callable[[], bool]] = None,
        pause_check: Optional[Callable[[], bool]] = None,
    ) -> None:
        """
        Initialize a task scheduler.
        
        Args:
            max_workers: Maximum number of worker threads
            progress_callback: Callback for progress updates
            cancel_check: Function to check if processing should be canceled
            pause_check: Function to check if processing should be paused
        """
        pass
    
    def process_batch(
        self,
        name: str,
        func: Callable[[T], U],
        items: List[T],
        timeout: Optional[float] = None,
    ) -> List[U]:
        """
        Process a batch of items in parallel.
        
        Args:
            name: Name of the batch
            func: Function to apply to each item
            items: Items to process
            timeout: Timeout in seconds
            
        Returns:
            List of results
        """
        pass
    
    def cancel_all(self) -> None:
        """Cancel all worker pools."""
        pass
    
    def pause_all(self) -> None:
        """Pause all worker pools."""
        pass
    
    def resume_all(self) -> None:
        """Resume all worker pools."""
        pass
```

## State Management

### StateManager

The `StateManager` class manages the application state.

```python
class StateManager:
    def __init__(self) -> None:
        """Initialize the state manager."""
        pass
    
    @property
    def state(self) -> ProcessingState:
        """Get the current state."""
        pass
    
    def transition(self, event: StateChangeEvent) -> bool:
        """
        Transition to a new state based on an event.
        
        Args:
            event: The event that triggered the transition
            
        Returns:
            True if the transition was successful, False otherwise
        """
        pass
    
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
        pass
    
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
        pass
```

## Enums

### ProcessingStage

The `ProcessingStage` enum represents the stages of the processing pipeline.

```python
class ProcessingStage(Enum):
    """Stages of the image processing pipeline."""
    INITIALIZING = auto()
    SCANNING = auto()
    ANALYZING = auto()
    CATEGORIZING = auto()
    ORGANIZING = auto()
    REPORTING = auto()
    COMPLETED = auto()
```

### ProcessingState

The `ProcessingState` enum represents the possible states of the application.

```python
class ProcessingState(Enum):
    """Processing state of the application."""
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    CANCELING = "canceling"
    COMPLETED = "completed"
    FAILED = "failed"
```

### StateChangeEvent

The `StateChangeEvent` enum represents events that can change the application state.

```python
class StateChangeEvent(Enum):
    """Events that can change the processing state."""
    START = "start"
    PAUSE = "pause"
    RESUME = "resume"
    CANCEL = "cancel"
    COMPLETE = "complete"
    FAIL = "fail"
```

### ReportFormat

The `ReportFormat` enum represents the supported report formats.

```python
class ReportFormat(Enum):
    """Supported report formats."""
    TEXT = auto()
    HTML = auto()
```

### ImageFormat

The `ImageFormat` enum represents the supported image formats.

```python
class ImageFormat(Enum):
    """Supported image formats."""
    JPEG = auto()
    PNG = auto()
    GIF = auto()
    TIFF = auto()
    BMP = auto()
    WEBP = auto()
    UNKNOWN = auto()
```