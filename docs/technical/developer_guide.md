# Photo Organizer Developer Guide

This guide provides information for developers who want to contribute to the Photo Organizer project or extend its functionality.

## Development Environment Setup

### Prerequisites

- Python 3.9 or higher
- pip package manager
- Git

### Setting Up the Development Environment

1. Clone the repository:
   ```
   git clone https://github.com/example/photo-organizer.git
   cd photo-organizer
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   ```

3. Activate the virtual environment:
   - Windows:
     ```
     venv\Scripts\activate
     ```
   - macOS/Linux:
     ```
     source venv/bin/activate
     ```

4. Install the package in development mode:
   ```
   pip install -e ".[dev]"
   ```

   This will install the package and all development dependencies.

### Development Dependencies

The development dependencies are specified in the `setup.py` file under the `extras_require` section:

```python
extras_require={
    "dev": [
        "pytest>=7.0.0",
        "pytest-mock>=3.8.0",
        "flake8>=5.0.0",
        "black>=22.6.0",
        "isort>=5.10.0",
        "mypy>=0.971",
    ],
}
```

## Project Structure

The project follows a standard Python package structure:

```
photo-organizer/
├── .github/            # GitHub configuration
├── .kiro/              # Kiro IDE configuration
├── docs/               # Documentation
│   ├── examples.md     # Examples and tutorials
│   ├── installation.md # Installation guide
│   ├── technical/      # Technical documentation
│   └── user_guide.md   # User guide
├── src/                # Source code
│   └── photo_organizer/ # Main package
│       ├── models/     # Data models
│       ├── services/   # Services
│       ├── ui/         # User interfaces
│       └── utils/      # Utilities
├── tests/              # Tests
│   ├── integration/    # Integration tests
│   └── unit/           # Unit tests
├── .flake8             # Flake8 configuration
├── .gitignore          # Git ignore file
├── LICENSE             # License file
├── pyproject.toml      # Project configuration
├── README.txt          # README file
├── requirements.txt    # Dependencies
└── setup.py            # Package setup
```

## Coding Standards

### Code Style

The project follows the [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guide with some modifications:

- Line length: 100 characters
- Docstrings: Google style
- Imports: Sorted using isort
- Formatting: Black

### Type Hints

The project uses type hints throughout the codebase. All functions and methods should have type hints for parameters and return values.

### Documentation

All modules, classes, functions, and methods should have docstrings. The project uses Google-style docstrings:

```python
def example_function(param1: str, param2: int) -> bool:
    """
    Short description of the function.
    
    Args:
        param1: Description of param1
        param2: Description of param2
        
    Returns:
        Description of return value
        
    Raises:
        ValueError: Description of when this error is raised
    """
    pass
```

## Testing

### Running Tests

To run the tests:

```
pytest
```

To run tests with coverage:

```
pytest --cov=photo_organizer
```

To run specific tests:

```
pytest tests/unit/test_core.py
```

### Writing Tests

Tests are organized into unit tests and integration tests:

- Unit tests: Test individual components in isolation
- Integration tests: Test the interaction between components

Each test file should correspond to a module in the source code. For example, the tests for `photo_organizer/core.py` should be in `tests/unit/test_core.py`.

Test classes should be named `Test{ClassName}` and test methods should be named `test_{method_name}`.

Example:

```python
class TestApplicationCore:
    """Tests for the ApplicationCore class."""

    def test_init(self) -> None:
        """Test initializing an ApplicationCore object."""
        core = ApplicationCore()
        assert core is not None
```

## Code Quality Tools

### Linting

To run the linter:

```
flake8 src tests
```

### Formatting

To format the code:

```
black src tests
isort src tests
```

### Type Checking

To run the type checker:

```
mypy src tests
```

## Building and Packaging

### Building the Package

To build the package:

```
python setup.py sdist bdist_wheel
```

### Installing the Package

To install the package in development mode:

```
pip install -e .
```

To install the package with all extras:

```
pip install -e ".[all]"
```

## Continuous Integration

The project uses GitHub Actions for continuous integration. The CI pipeline runs on every push and pull request, and includes:

- Running tests
- Checking code style
- Checking type hints
- Building the package

## Release Process

To release a new version:

1. Update the version number in `src/photo_organizer/__init__.py`
2. Update the changelog
3. Create a new git tag
4. Push the tag to GitHub
5. Build and upload the package to PyPI

## Extension Points

### Adding a New Vision Service

To add a new vision service:

1. Create a new class that inherits from `VisionService` in `photo_organizer/services/vision/`
2. Implement the required methods
3. Register the service in `photo_organizer/services/vision/__init__.py`

Example:

```python
from photo_organizer.services.vision.base import VisionService

class MyVisionService(VisionService):
    """My custom vision service."""
    
    def detect_objects(self, image_data: bytes) -> List[Dict[str, Any]]:
        """
        Detect objects in an image.
        
        Args:
            image_data: Image data as bytes
            
        Returns:
            List of detected objects
        """
        # Implementation
        pass
```

### Adding a New Report Format

To add a new report format:

1. Add a new value to the `ReportFormat` enum in `photo_organizer/services/reporting.py`
2. Implement the formatting method in `photo_organizer/services/report_export.py`

Example:

```python
class ReportFormat(Enum):
    """Supported report formats."""
    TEXT = auto()
    HTML = auto()
    JSON = auto()  # New format

class ReportExportService:
    # ...
    
    def _format_report_json(self, report: Report) -> str:
        """
        Format a report as JSON.
        
        Args:
            report: The report to format
            
        Returns:
            The formatted report as a string
        """
        # Implementation
        pass
```

## Troubleshooting

### Common Development Issues

#### Import Errors

If you get import errors, make sure:

1. The virtual environment is activated
2. The package is installed in development mode
3. The module is in the Python path

#### Test Failures

If tests fail:

1. Check that all dependencies are installed
2. Check that the code is compatible with the test environment
3. Check that the test is correctly set up

#### Type Checking Errors

If type checking fails:

1. Check that all type hints are correct
2. Check that all imports are correct
3. Check that all dependencies have type hints

## Getting Help

If you need help with development:

1. Check the [documentation](https://example.com/photo-organizer/docs)
2. Search for similar issues in the [issue tracker](https://github.com/example/photo-organizer/issues)
3. Ask a question in the [discussions](https://github.com/example/photo-organizer/discussions)
4. Contact the maintainers