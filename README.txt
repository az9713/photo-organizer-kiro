# Photo Organizer

Photo Organizer is an intelligent application that organizes and categorizes your image collection using computer vision and machine learning techniques.

## Features

- **Intelligent Categorization**: Automatically categorizes images based on content
- **Duplicate Detection**: Identifies similar or duplicate images
- **Metadata Extraction**: Extracts and uses EXIF metadata for organization
- **Geolocation**: Organizes images by location when GPS data is available
- **Customizable**: Adjust similarity thresholds and categorization depth
- **Multiple Interfaces**: Command-line and graphical user interfaces
- **Comprehensive Reports**: Generates detailed reports of the organization process
- **Parallel Processing**: Optimized performance with multi-threading support

## Quick Start

### Installation

```bash
pip install photo-organizer
```

### Basic Usage

```bash
photo-organizer ~/Pictures/Vacation ~/Pictures/Organized
```

### GUI Usage

```bash
photo-organizer --gui
```

## Documentation

- [Quick Start Guide](docs/quick_start.md)
- [User Guide](docs/user_guide.md)
- [Installation Guide](docs/installation.md)
- [Examples](docs/examples.md)
- [Technical Documentation](docs/technical/)

## Requirements

- Python 3.9 or higher
- Dependencies listed in requirements.txt

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Acknowledgments

- TensorFlow for computer vision capabilities
- PyQt6 for the graphical user interface
- All contributors who have helped with the development