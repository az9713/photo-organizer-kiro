# Photo Organizer

An application to intelligently organize and rename image files based on their content using computer vision techniques.

## Features

- Analyzes images using computer vision to identify content
- Groups similar images together
- Creates logical folder structures with descriptive names
- Supports various image formats including JPEG, PNG, GIF, TIFF, BMP, and WebP
- Provides both CLI and GUI interfaces
- Generates comprehensive reports of the reorganization process

## Installation

### Prerequisites

- Python 3.9 or higher
- pip package manager

### Install from source

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
   pip install -e .
   ```

## Usage

### Command Line Interface

```
photo-organizer <input_path> <output_path> [options]
```

- `input_path`: Path to input file or directory containing images to organize
- `output_path`: Path to output directory where organized images will be stored

Options:
- `--gui`: Launch the graphical user interface

### Graphical User Interface

Run the application with the `--gui` flag:

```
photo-organizer --gui
```

## Development

### Running Tests

```
pytest
```

### Code Formatting

```
black src tests
isort src tests
```

### Linting

```
flake8 src tests
mypy src tests
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.