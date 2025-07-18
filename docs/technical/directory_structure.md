# Photo Organizer Directory Structure

This document provides an overview of the Photo Organizer project directory structure.

## Root Directory

```
photo_organizer/
├── .flake8                  # Flake8 configuration
├── .git/                    # Git repository
├── docs/                    # Documentation
├── pyinstaller/             # PyInstaller configuration
├── pyproject.toml           # Project configuration
├── README.txt               # Project README
├── requirements.txt         # Project dependencies
├── setup.py                 # Package setup script
├── src/                     # Source code
└── tests/                   # Tests
```

## Documentation Directory

```
docs/
├── examples.md              # Usage examples
├── installation.md          # Installation guide
├── quick_start.md           # Quick start guide
├── user_guide.md            # User guide
└── technical/               # Technical documentation
    ├── api.md               # API reference
    ├── architecture.md      # Architecture overview
    ├── developer_guide.md   # Developer guide
    └── directory_structure.md  # This file
```

## Source Code Directory

```
src/
└── photo_organizer/         # Main package
    ├── __init__.py          # Package initialization
    ├── core.py              # Core application logic
    ├── main.py              # Entry point
    ├── parallel.py          # Parallel processing utilities
    ├── state.py             # Application state management
    ├── models/              # Data models
    │   ├── __init__.py
    │   ├── category.py      # Category model
    │   ├── category_tree.py # Category hierarchy
    │   └── image.py         # Image model
    ├── services/            # Business logic services
    │   ├── __init__.py
    │   ├── analysis.py      # Image analysis service
    │   ├── categorization.py # Image categorization service
    │   ├── file_mapping.py  # Original to new file mapping
    │   ├── file_operations.py # File operations service
    │   ├── file_system_manager.py # File system management
    │   ├── geolocation.py   # Geolocation services
    │   ├── image_format.py  # Image format detection
    │   ├── metadata_extractor.py # Metadata extraction
    │   ├── reporting.py     # Report generation
    │   └── vision/          # Computer vision services
    │       ├── __init__.py
    │       ├── base.py      # Base vision service
    │       ├── detection.py # Object detection
    │       ├── similarity.py # Image similarity
    │       └── tensorflow.py # TensorFlow implementation
    ├── ui/                  # User interfaces
    │   ├── __init__.py
    │   ├── cli_parser.py    # Command-line argument parser
    │   ├── cli_progress.py  # Command-line progress reporting
    │   ├── config_dialog.py # Configuration dialog
    │   ├── file_selection.py # File selection UI
    │   ├── gui_app.py       # GUI application
    │   ├── progress_dialog.py # Progress dialog
    │   └── state_monitor.py # UI state monitoring
    └── utils/               # Utilities
        ├── __init__.py
        ├── analyze.py       # Analysis utilities
        ├── categorize.py    # Categorization utilities
        ├── detect.py        # Detection utilities
        ├── format_detector.py # File format detection
        ├── geocode.py       # Geocoding utilities
        ├── metadata_viewer.py # Metadata viewing
        ├── similarity.py    # Similarity utilities
        └── vision_analyzer.py # Vision analysis utilities
```

## Tests Directory

```
tests/
├── __init__.py              # Package initialization
├── conftest.py              # Pytest configuration
├── integration/             # Integration tests
│   ├── __init__.py
│   ├── test_cli.py          # CLI integration tests
│   ├── test_dataset.py      # Dataset tests
│   ├── test_end_to_end.py   # End-to-end tests
│   ├── test_error_handling.py # Error handling tests
│   ├── test_gui.py          # GUI integration tests
│   └── test_performance.py  # Performance tests
└── unit/                    # Unit tests
    ├── __init__.py
    ├── test_core.py         # Core tests
    ├── test_parallel.py     # Parallel processing tests
    ├── test_state.py        # State management tests
    ├── models/              # Model tests
    │   ├── __init__.py
    │   ├── test_category.py # Category model tests
    │   ├── test_category_tree.py # Category tree tests
    │   └── test_image.py    # Image model tests
    ├── services/            # Service tests
    │   ├── __init__.py
    │   ├── test_analysis.py # Analysis service tests
    │   ├── test_categorization.py # Categorization service tests
    │   ├── test_file_mapping.py # File mapping tests
    │   ├── test_file_operations.py # File operations tests
    │   ├── test_file_system_manager.py # File system tests
    │   ├── test_geolocation.py # Geolocation tests
    │   ├── test_image_format.py # Image format tests
    │   ├── test_metadata_extractor.py # Metadata tests
    │   ├── test_reporting.py # Reporting tests
    │   └── vision/          # Vision service tests
    │       ├── __init__.py
    │       ├── test_base.py # Base vision tests
    │       ├── test_detection.py # Detection tests
    │       ├── test_similarity.py # Similarity tests
    │       └── test_tensorflow.py # TensorFlow tests
    └── ui/                  # UI tests
        ├── __init__.py
        ├── test_cli_parser.py # CLI parser tests
        ├── test_cli_progress.py # CLI progress tests
        ├── test_config_dialog.py # Config dialog tests
        ├── test_file_selection.py # File selection tests
        ├── test_gui_app.py  # GUI app tests
        ├── test_progress_dialog.py # Progress dialog tests
        └── test_state_monitor.py # State monitor tests
```

## PyInstaller Directory

```
pyinstaller/
├── build.py                 # Build script
└── photo_organizer.spec     # PyInstaller spec file
```

## Understanding the Structure

### Source Code Organization

The source code is organized into several packages:

- **models**: Contains data models that represent the core entities in the application
- **services**: Contains business logic services that implement the application's functionality
- **ui**: Contains user interface components for both command-line and graphical interfaces
- **utils**: Contains utility functions and helper classes

### Test Organization

Tests are organized into two main categories:

- **unit**: Contains unit tests for individual components
- **integration**: Contains integration tests that test multiple components together

Each test package mirrors the structure of the source code package it tests.

### Documentation Organization

Documentation is organized into user-facing and developer-facing documents:

- **User-facing**: Installation guide, user guide, quick start guide, examples
- **Developer-facing**: API reference, architecture overview, developer guide, directory structure