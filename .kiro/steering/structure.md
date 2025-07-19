# Photo Organizer Project Structure

## Architecture Overview

Photo Organizer follows a layered architecture:

1. **User Interface Layer**: CLI and GUI interfaces
2. **Application Layer**: Core application logic and state management
3. **Service Layer**: Business logic for image analysis, categorization, and file operations
4. **Model Layer**: Data structures for images, categories, and reports
5. **Utility Layer**: Helper functions and utilities

## Directory Structure

```
photo_organizer/
├── docs/                    # Documentation
│   ├── examples.md          # Usage examples
│   ├── installation.md      # Installation guide
│   ├── quick_start.md       # Quick start guide
│   ├── user_guide.md        # User guide
│   └── technical/           # Technical documentation
├── pyinstaller/             # PyInstaller configuration
├── src/                     # Source code
│   └── photo_organizer/     # Main package
│       ├── models/          # Data models
│       ├── services/        # Business logic services
│       │   └── vision/      # Computer vision services
│       ├── ui/              # User interfaces
│       └── utils/           # Utilities
└── tests/                   # Tests
    ├── integration/         # Integration tests
    └── unit/                # Unit tests
```

## Key Components

### Models
- `Image`: Represents an image file with metadata and features
- `Category`: Represents a category for organizing images
- `CategoryTree`: Represents a hierarchy of categories

### Services
- `ImageAnalysisService`: Analyzes images to extract features
- `CategorizationService`: Categorizes images based on features
- `FileOperationsService`: Handles file operations
- `ReportingService`: Generates reports

### User Interfaces
- `CLIParser`: Parses command-line arguments
- `CLIProgressReporter`: Reports progress to the console
- `GUIApp`: Main GUI application

### Core Components
- `ApplicationCore`: Main application logic
- `StateManager`: Manages application state
- `TaskScheduler`: Handles parallel processing

## Coding Conventions

### File Organization
- Each module should have a single responsibility
- Related functionality should be grouped in the same package
- Implementation files should be accompanied by test files

### Import Order
1. Standard library imports
2. Third-party library imports
3. Application imports

### Class Structure
- Public methods first
- Protected methods (prefixed with `_`) next
- Private methods (prefixed with `__`) last
- Class methods and static methods grouped with related instance methods

## Testing Structure

- Unit tests mirror the structure of the source code
- Integration tests focus on component interactions
- Test files are named `test_<module>.py`
- Test classes are named `Test<Class>`
- Test methods are named `test_<method>_<scenario>`

## State Management

The application uses a state machine with the following states:
- `IDLE`: Ready to process images
- `RUNNING`: Processing images
- `PAUSED`: Processing paused
- `CANCELING`: Canceling operation
- `COMPLETED`: Processing completed
- `FAILED`: Processing failed