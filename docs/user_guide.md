# Photo Organizer User Guide

## Introduction

Photo Organizer is an intelligent application designed to help you organize your photo collection based on image content. Using advanced computer vision techniques, it analyzes your images, groups similar photos together, and creates a logical folder structure with descriptive names.

This guide will help you get started with Photo Organizer and make the most of its features.

## Installation

### Prerequisites

- Python 3.9 or higher
- pip package manager

### Installing from Source

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

4. Install the package:
   ```
   pip install -e .
   ```

### Installing from PyPI

```
pip install photo-organizer
```

## Getting Started

### Command Line Interface

Photo Organizer provides a command-line interface for quick and scriptable use.

#### Basic Usage

```
photo-organizer <input_path> <output_path>
```

- `input_path`: Path to a file or directory containing images to organize
- `output_path`: Path to a directory where organized images will be stored

#### Examples

Organize a single image:
```
photo-organizer vacation.jpg organized_photos/
```

Organize all images in a directory:
```
photo-organizer vacation_photos/ organized_photos/
```

Organize images recursively:
```
photo-organizer photo_collection/ organized_photos/ --recursive
```

#### Command Line Options

| Option | Description |
|--------|-------------|
| `--recursive`, `-r` | Process subdirectories recursively |
| `--parallel` | Enable parallel processing |
| `--max-workers N` | Maximum number of worker threads (default: 4) |
| `--similarity-threshold X` | Threshold for image similarity (0.0 to 1.0, default: 0.7) |
| `--max-category-depth N` | Maximum depth of category hierarchy (default: 3) |
| `--report FORMAT` | Report format: text, html, or both (default: html) |
| `--report-path PATH` | Custom path for the report file |
| `--verbose`, `-v` | Increase verbosity level (can be used multiple times) |
| `--quiet`, `-q` | Suppress all output except errors |
| `--version` | Show version information and exit |
| `--help` | Show help message and exit |

### Graphical User Interface

Photo Organizer also provides a graphical user interface for a more interactive experience.

To launch the GUI:

```
photo-organizer --gui
```

#### GUI Features

1. **File Selection**: Drag and drop files or folders, or use the file browser to select images.
2. **Configuration**: Access settings through the Edit > Preferences menu.
3. **Processing**: Click the "Organize" button to start processing.
4. **Progress Monitoring**: View real-time progress and logs during processing.
5. **Reports**: View and save reports after processing.

## Features

### Image Analysis

Photo Organizer analyzes your images using computer vision to identify:

- Objects and scenes
- People and faces
- Locations and landmarks
- Colors and compositions

### Categorization

Based on the analysis, Photo Organizer groups similar images together using:

- Content similarity
- Temporal proximity
- Geolocation data
- Hierarchical clustering

### Organization

Photo Organizer creates a logical folder structure with:

- Descriptive folder names based on content
- Hierarchical organization (up to the specified depth)
- Meaningful file names that reflect content
- Preservation of original files

### Reporting

After organizing your images, Photo Organizer generates a comprehensive report with:

- Summary statistics
- Folder structure visualization
- File mapping (original to new locations)
- Metadata information (timestamps, locations)
- Processing errors (if any)

## Advanced Usage

### Customizing Similarity Threshold

The similarity threshold controls how similar images must be to be grouped together. A higher threshold results in more specific categories, while a lower threshold creates broader categories.

```
photo-organizer photos/ organized/ --similarity-threshold 0.8
```

### Controlling Category Depth

The maximum category depth controls how deep the folder hierarchy can be. A higher value allows for more specific categorization, while a lower value creates a flatter structure.

```
photo-organizer photos/ organized/ --max-category-depth 4
```

### Parallel Processing

For large collections, parallel processing can significantly speed up the organization process.

```
photo-organizer photos/ organized/ --parallel --max-workers 8
```

### Custom Reports

You can generate reports in different formats and save them to custom locations.

```
photo-organizer photos/ organized/ --report both --report-path custom_report
```

## Troubleshooting

### Common Issues

#### Application Crashes with Out of Memory Error

- Process fewer images at once
- Reduce the number of worker threads
- Close other memory-intensive applications

#### Images Not Being Categorized Correctly

- Try adjusting the similarity threshold
- Ensure images are not corrupted
- Check if images have valid metadata

#### Permission Errors

- Ensure you have read access to input files
- Ensure you have write access to the output directory
- Run the application with appropriate permissions

### Getting Help

If you encounter issues not covered in this guide, please:

1. Check the [FAQ](https://example.com/photo-organizer/faq)
2. Search for similar issues in the [issue tracker](https://github.com/example/photo-organizer/issues)
3. Submit a new issue with detailed information about your problem

## License

Photo Organizer is licensed under the MIT License. See the LICENSE file for details.