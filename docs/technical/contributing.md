# Contributing to Photo Organizer

Thank you for your interest in contributing to Photo Organizer! This document provides guidelines and instructions for contributing to the project.

## Code of Conduct

Please read and follow our [Code of Conduct](CODE_OF_CONDUCT.md) to foster an inclusive and respectful community.

## Getting Started

### Prerequisites

- Python 3.9 or higher
- Git
- pip package manager

### Setting Up the Development Environment

1. Fork the repository on GitHub.

2. Clone your fork locally:
   ```bash
   git clone https://github.com/your-username/photo-organizer.git
   cd photo-organizer
   ```

3. Create a virtual environment:
   ```bash
   python -m venv venv
   ```

4. Activate the virtual environment:
   - Windows:
     ```bash
     venv\Scripts\activate
     ```
   - macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

5. Install development dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

6. Set up pre-commit hooks:
   ```bash
   pre-commit install
   ```

## Development Workflow

### Branching Strategy

We use a simplified Git flow with the following branches:

- `main`: The main branch contains the latest stable release.
- `develop`: The development branch contains the latest development changes.
- Feature branches: Create a new branch for each feature or bug fix.

### Creating a Feature Branch

Create a new branch for your feature or bug fix:

```bash
git checkout develop
git pull origin develop
git checkout -b feature/your-feature-name
```

### Making Changes

1. Make your changes to the codebase.
2. Write or update tests for your changes.
3. Run the tests to ensure they pass:
   ```bash
   pytest
   ```
4. Run the linter to ensure code quality:
   ```bash
   flake8
   ```
5. Format your code:
   ```bash
   black src tests
   ```

### Committing Changes

1. Stage your changes:
   ```bash
   git add .
   ```

2. Commit your changes with a descriptive message:
   ```bash
   git commit -m "Add feature: your feature description"
   ```

3. Push your changes to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

### Creating a Pull Request

1. Go to the [Photo Organizer repository](https://github.com/example/photo-organizer) on GitHub.
2. Click the "New Pull Request" button.
3. Select your fork and branch as the source.
4. Select the `develop` branch as the target.
5. Fill in the pull request template with details about your changes.
6. Submit the pull request.

## Coding Standards

### Python Style Guide

We follow the [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guide for Python code. Some key points:

- Use 4 spaces for indentation (not tabs).
- Use snake_case for variable and function names.
- Use CamelCase for class names.
- Keep lines under 88 characters.
- Use docstrings for all public modules, functions, classes, and methods.

### Documentation

- Use [Google-style docstrings](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings) for all public modules, functions, classes, and methods.
- Keep docstrings clear, concise, and informative.
- Update documentation when you change code.

Example:

```python
def process_image(image_path, options=None):
    """Process an image with the given options.
    
    Args:
        image_path (str): Path to the image file.
        options (dict, optional): Processing options. Defaults to None.
        
    Returns:
        bool: True if processing was successful, False otherwise.
        
    Raises:
        ValueError: If the image path is invalid.
    """
    # Implementation
```

### Testing

- Write tests for all new features and bug fixes.
- Maintain or improve test coverage.
- Use pytest for testing.
- Name test files with the `test_` prefix.
- Name test functions with the `test_` prefix.

Example:

```python
def test_process_image_with_valid_path():
    """Test that process_image works with a valid path."""
    result = process_image("valid/path/to/image.jpg")
    assert result is True
```

## Pull Request Process

1. Ensure your code follows the coding standards.
2. Update the documentation if necessary.
3. Add or update tests for your changes.
4. Ensure all tests pass.
5. Update the CHANGELOG.md file with your changes.
6. The pull request will be reviewed by maintainers.
7. Address any feedback from the review.
8. Once approved, your pull request will be merged.

## Release Process

1. Update the version number in `__init__.py` according to [Semantic Versioning](https://semver.org/).
2. Update the CHANGELOG.md file with the new version and changes.
3. Create a new git tag:
   ```bash
   git tag -a v1.0.0 -m "Version 1.0.0"
   ```
4. Push the tag:
   ```bash
   git push origin v1.0.0
   ```
5. Create a new release on GitHub with the tag.
6. Build and publish the package to PyPI:
   ```bash
   python -m build
   python -m twine upload dist/*
   ```

## Reporting Bugs

If you find a bug, please report it by creating an issue on the [issue tracker](https://github.com/example/photo-organizer/issues) with the following information:

- A clear, descriptive title.
- A description of the problem, including steps to reproduce.
- The expected behavior and what actually happened.
- Any relevant logs or error messages.
- Your operating system and Python version.

## Requesting Features

If you have an idea for a new feature, please create an issue on the [issue tracker](https://github.com/example/photo-organizer/issues) with the following information:

- A clear, descriptive title.
- A detailed description of the proposed feature.
- Any relevant examples or use cases.
- Whether you're willing to contribute the feature yourself.

## Community

Join our community to discuss the project, ask questions, and get help:

- [GitHub Discussions](https://github.com/example/photo-organizer/discussions)
- [Discord Server](https://discord.gg/example)
- [Mailing List](https://example.com/mailing-list)

## License

By contributing to Photo Organizer, you agree that your contributions will be licensed under the project's [MIT License](LICENSE).