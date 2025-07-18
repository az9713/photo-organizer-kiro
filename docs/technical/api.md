# Photo Organizer API Reference

This document provides a reference for the Photo Organizer API, which can be used to integrate Photo Organizer functionality into other applications.

## Core API

### ApplicationCore

The main entry point for the Photo Organizer functionality.

```python
from photo_organizer.core import ApplicationCore
from photo_organizer.ui.cli_progress import CLIProgressReporter

# Create a progress reporter
reporter = CLIProgressReporter(verbose=1)

# Create the application core
app_core = ApplicationCore(reporter)

# Process images
success, report = app_core.process_images(
    input_paths=["path/to/images"],
    output_path="path/to/output",
    options={
        "recursive": True,
        "report_format": "text",
    },
)

# Check if processing was successful
if success:
    print(f"Processing complete. Report saved to: {report}")
else:
    print("Processing failed.")
```

#### ApplicationCore Methods

##### `__init__(self, progress_reporter, parallel_processing=False, max_workers=None)`

Initialize the ApplicationCore.

- **Parameters**:
  - `progress_reporter`: An object implementing the ProgressReporter interface
  - `parallel_processing`: Whether to use parallel processing (default: False)
  - `max_workers`: Maximum number of worker threads for parallel processing (default: None)

##### `process_images(self, input_paths, output_path, options=None)`

Process images from the input paths and organize them in the output path.

- **Parameters**:
  - `input_paths`: List of paths to files or directories containing images
  - `output_path`: Path to a directory where organized images will be stored
  - `options`: Dictionary of processing options (default: None)
- **Returns**:
  - `success`: Boolean indicating whether processing was successful
  - `report_path`: Path to the generated report, or None if no report was generated

##### `cancel(self)`

Cancel the current processing operation.

- **Returns**:
  - `success`: Boolean indicating whether cancellation was successful

## State Management API

### StateManager

Manages the application state and provides a way for components to observe state changes.

```python
from photo_organizer.state import StateManager, ApplicationState

# Create a state manager
state_manager = StateManager()

# Get the current state
current_state = state_manager.state

# Register a state change observer
def on_state_change(old_state, new_state):
    print(f"State changed from {old_state.name} to {new_state.name}")

state_manager.add_observer(on_state_change)

# Transition to a new state
state_manager.transition_to(ApplicationState.PROCESSING)
```

#### StateManager Methods

##### `__init__(self)`

Initialize the StateManager with the IDLE state.

##### `add_observer(self, observer)`

Add an observer function that will be called when the state changes.

- **Parameters**:
  - `observer`: A function that takes two parameters (old_state, new_state)

##### `remove_observer(self, observer)`

Remove an observer function.

- **Parameters**:
  - `observer`: The observer function to remove

##### `transition_to(self, state)`

Transition to a new state.

- **Parameters**:
  - `state`: The new state to transition to
- **Returns**:
  - `success`: Boolean indicating whether the transition was successful

##### `can_transition_to(self, state)`

Check if a transition to the given state is valid.

- **Parameters**:
  - `state`: The state to check
- **Returns**:
  - `valid`: Boolean indicating whether the transition is valid

## Services API

### ImageAnalysisService

Analyzes images to extract features.

```python
from photo_organizer.services.analysis import ImageAnalysisService
from photo_organizer.models.image import Image

# Create an image analysis service
analysis_service = ImageAnalysisService()

# Create an image object
image = Image("path/to/image.jpg")

# Analyze the image
analysis_service.analyze_image(image)

# Access image features
print(f"Objects detected: {image.objects}")
print(f"Scene type: {image.scene_type}")
print(f"Location: {image.location}")
```

#### ImageAnalysisService Methods

##### `__init__(self, vision_service=None)`

Initialize the ImageAnalysisService.

- **Parameters**:
  - `vision_service`: A vision service to use for analysis (default: None, uses TensorFlowVisionService)

##### `analyze_image(self, image)`

Analyze an image to extract features.

- **Parameters**:
  - `image`: An Image object to analyze
- **Returns**:
  - `image`: The analyzed Image object

### CategorizationService

Categorizes images based on their content.

```python
from photo_organizer.services.categorization import CategorizationService
from photo_organizer.models.image import Image

# Create a categorization service
categorization_service = CategorizationService()

# Create image objects
images = [
    Image("path/to/image1.jpg"),
    Image("path/to/image2.jpg"),
]

# Analyze images first
# ...

# Categorize images
category_tree = categorization_service.categorize_images(images)

# Access categories
for category in category_tree.get_categories():
    print(f"Category: {category.name}")
    for image in category.images:
        print(f"  - {image.path}")
```

#### CategorizationService Methods

##### `__init__(self, similarity_threshold=0.7, max_category_depth=3)`

Initialize the CategorizationService.

- **Parameters**:
  - `similarity_threshold`: Threshold for image similarity (0.0 to 1.0, default: 0.7)
  - `max_category_depth`: Maximum depth of category hierarchy (default: 3)

##### `categorize_images(self, images)`

Categorize a list of images.

- **Parameters**:
  - `images`: List of Image objects to categorize
- **Returns**:
  - `category_tree`: A CategoryTree object containing the categorized images

### FileOperationsService

Handles file operations for organizing images.

```python
from photo_organizer.services.file_operations import FileOperationsService
from photo_organizer.models.category_tree import CategoryTree

# Create a file operations service
file_ops_service = FileOperationsService()

# Create a category tree with images
# ...

# Organize files
file_mappings = file_ops_service.organize_files(
    category_tree,
    "path/to/output",
)

# Access file mappings
for original, new in file_mappings.items():
    print(f"{original} -> {new}")
```

#### FileOperationsService Methods

##### `__init__(self)`

Initialize the FileOperationsService.

##### `organize_files(self, category_tree, output_path)`

Organize files according to the category tree.

- **Parameters**:
  - `category_tree`: A CategoryTree object containing categorized images
  - `output_path`: Path to a directory where organized images will be stored
- **Returns**:
  - `file_mappings`: Dictionary mapping original file paths to new file paths

### ReportingService

Generates reports about the organization process.

```python
from photo_organizer.services.reporting import ReportingService, ReportFormat

# Create a reporting service
reporting_service = ReportingService()

# Generate a report
report_path = reporting_service.generate_report(
    "path/to/output/report",
    ReportFormat.TEXT,
    file_mappings,
    errors,
)

print(f"Report generated at: {report_path}")
```

#### ReportingService Methods

##### `__init__(self)`

Initialize the ReportingService.

##### `generate_report(self, output_path, report_format, file_mappings, errors=None)`

Generate a report about the organization process.

- **Parameters**:
  - `output_path`: Path where the report will be saved
  - `report_format`: Format of the report (ReportFormat.TEXT, ReportFormat.HTML, or ReportFormat.BOTH)
  - `file_mappings`: Dictionary mapping original file paths to new file paths
  - `errors`: List of errors encountered during processing (default: None)
- **Returns**:
  - `report_path`: Path to the generated report

## Models API

### Image

Represents an image file with its metadata.

```python
from photo_organizer.models.image import Image

# Create an image object
image = Image("path/to/image.jpg")

# Access image properties
print(f"Path: {image.path}")
print(f"Format: {image.format}")
print(f"Size: {image.size}")
print(f"Creation date: {image.creation_date}")
```

#### Image Properties

- `path`: Path to the image file
- `format`: Format of the image (JPEG, PNG, etc.)
- `size`: Size of the image in bytes
- `dimensions`: Dimensions of the image (width, height)
- `creation_date`: Creation date of the image
- `modification_date`: Last modification date of the image
- `exif_data`: EXIF metadata of the image
- `location`: Geographic location where the image was taken
- `objects`: List of objects detected in the image
- `scene_type`: Type of scene in the image
- `colors`: Dominant colors in the image
- `tags`: List of tags associated with the image

### Category

Represents a category for organizing images.

```python
from photo_organizer.models.category import Category
from photo_organizer.models.image import Image

# Create a category
category = Category(name="Vacation", description="Vacation photos")

# Add images to the category
image1 = Image("path/to/image1.jpg")
image2 = Image("path/to/image2.jpg")
category.add_image(image1)
category.add_image(image2)

# Access category properties
print(f"Name: {category.name}")
print(f"Description: {category.description}")
print(f"Image count: {len(category.images)}")
```

#### Category Properties

- `name`: Name of the category
- `description`: Description of the category
- `images`: List of images in the category
- `parent`: Parent category, or None if this is a root category
- `children`: List of child categories

### CategoryTree

Represents a hierarchy of categories.

```python
from photo_organizer.models.category_tree import CategoryTree
from photo_organizer.models.category import Category

# Create a category tree
category_tree = CategoryTree()

# Add categories
vacation = Category(name="Vacation", description="Vacation photos")
beach = Category(name="Beach", description="Beach photos")
mountains = Category(name="Mountains", description="Mountain photos")

category_tree.add_category(vacation)
category_tree.add_child_category(vacation, beach)
category_tree.add_child_category(vacation, mountains)

# Access categories
for category in category_tree.get_categories():
    print(f"Category: {category.name}")
    for child in category.children:
        print(f"  - Child: {child.name}")
```

#### CategoryTree Methods

##### `__init__(self)`

Initialize an empty CategoryTree.

##### `add_category(self, category)`

Add a root category to the tree.

- **Parameters**:
  - `category`: The Category object to add

##### `add_child_category(self, parent, child)`

Add a child category to a parent category.

- **Parameters**:
  - `parent`: The parent Category object
  - `child`: The child Category object

##### `get_categories(self)`

Get all categories in the tree.

- **Returns**:
  - `categories`: List of all Category objects in the tree

##### `get_root_categories(self)`

Get the root categories in the tree.

- **Returns**:
  - `root_categories`: List of root Category objects in the tree

## UI API

### CLIProgressReporter

Reports progress for command-line interfaces.

```python
from photo_organizer.ui.cli_progress import CLIProgressReporter

# Create a CLI progress reporter
reporter = CLIProgressReporter(verbose=1)

# Report progress
reporter.start_task("Processing images", total=10)
for i in range(10):
    # Do some work
    reporter.update_progress(i + 1)
reporter.end_task()

# Report an error
reporter.report_error("Error processing image", file="path/to/image.jpg", exception=Exception("Some error"))
```

#### CLIProgressReporter Methods

##### `__init__(self, verbose=1, quiet=False)`

Initialize the CLIProgressReporter.

- **Parameters**:
  - `verbose`: Verbosity level (0-3, default: 1)
  - `quiet`: Whether to suppress all output except errors (default: False)

##### `start_task(self, description, total=None)`

Start a new task.

- **Parameters**:
  - `description`: Description of the task
  - `total`: Total number of steps in the task (default: None)

##### `update_progress(self, current, description=None)`

Update the progress of the current task.

- **Parameters**:
  - `current`: Current step number
  - `description`: Description of the current step (default: None)

##### `end_task(self)`

End the current task.

##### `report_error(self, message, file=None, exception=None)`

Report an error.

- **Parameters**:
  - `message`: Error message
  - `file`: File where the error occurred (default: None)
  - `exception`: Exception that caused the error (default: None)

### ProgressDialog

Reports progress for graphical user interfaces.

```python
from PyQt6.QtWidgets import QApplication
from photo_organizer.ui.progress_dialog import ProgressDialog

# Create a Qt application
app = QApplication([])

# Create a progress dialog
dialog = ProgressDialog()

# Show the dialog
dialog.show()

# Report progress
dialog.start_task("Processing images", total=10)
for i in range(10):
    # Do some work
    dialog.update_progress(i + 1)
dialog.end_task()

# Close the dialog
dialog.close()
```

#### ProgressDialog Methods

##### `__init__(self, parent=None)`

Initialize the ProgressDialog.

- **Parameters**:
  - `parent`: Parent widget (default: None)

##### `start_task(self, description, total=None)`

Start a new task.

- **Parameters**:
  - `description`: Description of the task
  - `total`: Total number of steps in the task (default: None)

##### `update_progress(self, current, description=None)`

Update the progress of the current task.

- **Parameters**:
  - `current`: Current step number
  - `description`: Description of the current step (default: None)

##### `end_task(self)`

End the current task.

##### `report_error(self, message, file=None, exception=None)`

Report an error.

- **Parameters**:
  - `message`: Error message
  - `file`: File where the error occurred (default: None)
  - `exception`: Exception that caused the error (default: None)