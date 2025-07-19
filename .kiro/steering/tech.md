# Photo Organizer Technical Stack

## Programming Language
- Python 3.9+

## Build System
- setuptools (build-backend: setuptools.build_meta)
- pyproject.toml for modern Python packaging

## Dependencies
### Core Dependencies
- pillow (≥9.0.0): Image processing
- exifread (≥3.0.0): EXIF metadata extraction
- geopy (≥2.2.0): Geocoding services
- numpy (≥1.22.0): Numerical operations
- opencv-python (≥4.5.5): Computer vision
- tensorflow (≥2.8.0): Machine learning for image analysis
- scikit-learn (≥1.0.2): Machine learning utilities
- PyQt6 (≥6.2.3): GUI framework

### Development Dependencies
- pytest (≥7.0.0): Testing framework
- pytest-cov (≥3.0.0): Test coverage
- black (≥22.1.0): Code formatting
- flake8 (≥4.0.1): Linting
- mypy (≥0.931): Type checking
- isort (≥5.10.1): Import sorting
- pre-commit (≥2.17.0): Pre-commit hooks
- pyinstaller (≥5.0.0): Executable packaging

## Code Style
- Black formatting with line length of 88
- isort for import sorting (profile: black)
- flake8 for linting
- mypy for type checking with strict settings

## Common Commands

### Installation
```bash
# Development installation
pip install -e ".[dev]"

# User installation
pip install .
```

### Running the Application
```bash
# CLI mode
photo-organizer <input_path> <output_path>

# GUI mode
photo-organizer --gui
```

### Testing
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=photo_organizer

# Generate coverage report
pytest --cov=photo_organizer --cov-report=html
```

### Building
```bash
# Build Python package
python -m build

# Build executable (Windows)
python pyinstaller/build.py
```

### Code Quality
```bash
# Format code
black src tests

# Sort imports
isort src tests

# Lint code
flake8 src tests

# Type check
mypy src
```

## Packaging
- Python package (pip installable)
- Standalone executables via PyInstaller
- Windows installer via NSIS