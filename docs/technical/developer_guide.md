# Photo Organizer Developer Guide

This guide provides information for developers who want to contribute to the Photo Organizer project or extend its functionality.

## Project Structure

```
photo_organizer/
├── __init__.py
├── main.py                 # Entry point
├── core.py                 # Core application logic
├── state.py                # Application state management
├── parallel.py             # Parallel processing utilities
├── models/                 # Data models
│   ├── __init__.py
│   ├── image.py            # Image model
│   ├── category.py         # Category model
│   └── category_tree.py    # Category hierarchy
├── services/               # Business logic services
│   ├── __init__.py
│   ├── analysis.py         # Image analysis service
│   ├── categorization.py   # Image categorization service
│   ├── file_operations.py  # File operations service
│   ├── file_system_manager.py  # File system management
│   ├── file_mapping.py     # Original to new file mapping
│   ├── geolocation.py      # Geolocation services
│   ├── image_format.py     # Image format detection
│   ├── metadata_extractor.py  # Metadata extraction
│   ├── reporting.py        # Report generation
│   └── vision/             # Computer vision services
│       ├── __init__.py
│       ├── base.py         # Base vision service
│       ├── detection.py    # Object detection
│       ├── similarity.py   # Image similarity
│       └── tensorflow.py   # TensorFlow implementation
└── ui/                     # User interfaces
    ├── __init__.py
    ├── cli_parser.py       # Command-line argument parser
    ├── cli_progress.py     # Command-line progress reporting
    ├── gui_app.py          # GUI application
    ├── file_selection.py   # File selection UI
    ├── config_dialog.py    # Configuration dialog
    ├── progress_dialog.py  # Progress dialog
    └── state_monitor.py    # UI state monitoring
```

## Development Environment Setup

### Prerequisites

- Python 3.9 or higher
- pip package manager
- Git

### Setting Up the Development Environment

1. Clone the repository:
   ```bash
   git clone https://github.com/example/photo-organizer.git
   cd photo-organizer
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   ```

3. Activate the virtual environment:
   - Windows:
     ```bash
     venv\Scripts\activate
     ```
   - macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

4. Install development dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

### Running Tests

Run the test suite:

```bash
pytest
```

Run tests with coverage:

```bash
pytest --cov=photo_organizer
```

### Code Style

This project follows PEP 8 style guidelines. Use flake8 to check your code:

```bash
flake8 src tests
```

Use black to format your code:

```bash
black src tests
```

## Architecture

Photo Organizer follows a layered architecture:

1. **UI Layer**: Command-line and graphical interfaces
2. **Application Layer**: Core application logic
3. **Service Layer**: Business logic services
4. **Model Layer**: Data models

### Key Components

#### Core Application

The `ApplicationCore` class in `core.py` is the main entry point for the application logic. It coordinates the various services and manages the application state.

#### State Management

The `StateManager` class in `state.py` manages the application state and provides a way for components to observe state changes.

#### Services

Services implement the business logic of the application:

- **ImageAnalysisService**: Analyzes images to extract features
- **CategorizationService**: Categorizes images based on their content
- **FileOperationsService**: Handles file operations
- **ReportingService**: Generates reports

#### Models

Models represent the data structures used by the application:

- **Image**: Represents an image file with its metadata
- **Category**: Represents a category for organizing images
- **CategoryTree**: Represents a hierarchy of categories

#### User Interfaces

The application provides two user interfaces:

- **Command-line Interface**: Implemented in `cli_parser.py` and `cli_progress.py`
- **Graphical User Interface**: Implemented in `gui_app.py` and related files

## Extending Photo Organizer

### Adding a New Vision Service

To add a new vision service:

1. Create a new class that inherits from `VisionServiceBase` in `services/vision/base.py`
2. Implement the required methods
3. Register the service in `services/vision/__init__.py`

Example:

```python
from photo_organizer.services.vision.base import VisionServiceBase

class MyVisionService(VisionServiceBase):
    def __init__(self):
        super().__init__()
        # Initialize your service
        
    def detect_objects(self, image):
        # Implement object detection
        pass
        
    def compute_similarity(self, image1, image2):
        # Implement similarity computation
        pass
```

### Adding a New Report Format

To add a new report format:

1. Add a new format to the `ReportFormat` enum in `services/reporting.py`
2. Implement a new report generator method in `ReportingService`

Example:

```python
def generate_xml_report(self, output_path, file_mappings, errors):
    # Implement XML report generation
    pass
```

### Adding a New UI

To add a new user interface:

1. Create a new module in the `ui` package
2. Implement the interface using the `StateManager` to observe application state
3. Use the `ApplicationCore` to perform operations

## Building and Packaging

### Building a Wheel Package

```bash
python -m build
```

### Building Standalone Executables

The project uses PyInstaller to create standalone executables:

```bash
python -m pyinstaller pyinstaller/photo_organizer.spec
```

Or use the build script:

```bash
python pyinstaller/build.py
```

## Release Process

1. Update version number in `__init__.py`
2. Update CHANGELOG.md
3. Create a new git tag:
   ```bash
   git tag -a v1.0.0 -m "Version 1.0.0"
   ```
4. Build the package:
   ```bash
   python -m build
   ```
5. Upload to PyPI:
   ```bash
   python -m twine upload dist/*
   ```
6. Create a GitHub release with the built executables

## Troubleshooting Development Issues

### Common Issues

1. **Import errors**:
   - Make sure you've installed the package in development mode
   - Check that you're running from the correct virtual environment

2. **Test failures**:
   - Check that all dependencies are installed
   - Look for specific error messages in the test output

3. **Build failures**:
   - Check that PyInstaller is installed
   - Ensure all dependencies are correctly specified in setup.py

### Getting Help

If you encounter issues not covered here:

1. Check the existing issues on GitHub
2. Ask for help in the developer chat
3. Submit a new issue with detailed information about the problem