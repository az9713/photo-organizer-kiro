# Photo Organizer Testing Guide

This document provides guidelines and instructions for testing the Photo Organizer application.

## Testing Philosophy

Photo Organizer follows a comprehensive testing approach that includes:

1. **Unit Testing**: Testing individual components in isolation
2. **Integration Testing**: Testing interactions between components
3. **End-to-End Testing**: Testing complete workflows
4. **Performance Testing**: Testing application performance
5. **Error Handling Testing**: Testing error handling and recovery

## Test Directory Structure

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
    ├── services/            # Service tests
    └── ui/                  # UI tests
```

## Running Tests

### Running All Tests

To run all tests:

```bash
pytest
```

### Running Specific Tests

To run a specific test file:

```bash
pytest tests/unit/test_core.py
```

To run a specific test function:

```bash
pytest tests/unit/test_core.py::test_process_images
```

To run tests matching a pattern:

```bash
pytest -k "process"
```

### Running Tests with Coverage

To run tests with coverage:

```bash
pytest --cov=photo_organizer
```

To generate a coverage report:

```bash
pytest --cov=photo_organizer --cov-report=html
```

The coverage report will be generated in the `htmlcov` directory.

## Test Categories

### Unit Tests

Unit tests test individual components in isolation. They are located in the `tests/unit` directory.

Example:

```python
def test_analyze_image():
    """Test that analyze_image correctly analyzes an image."""
    # Create a mock image
    image = Image("path/to/image.jpg")
    
    # Create a mock vision service
    vision_service = MockVisionService()
    
    # Create the analysis service with the mock vision service
    analysis_service = ImageAnalysisService(vision_service)
    
    # Analyze the image
    result = analysis_service.analyze_image(image)
    
    # Check the result
    assert result is not None
    assert image.objects is not None
    assert image.scene_type is not None
```

### Integration Tests

Integration tests test interactions between components. They are located in the `tests/integration` directory.

Example:

```python
def test_end_to_end_workflow():
    """Test the end-to-end workflow of the application."""
    # Create a temporary directory for input and output
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create input and output directories
        input_dir = os.path.join(temp_dir, "input")
        output_dir = os.path.join(temp_dir, "output")
        os.makedirs(input_dir)
        os.makedirs(output_dir)
        
        # Create test images
        create_test_images(input_dir)
        
        # Run the application
        app = ApplicationCore()
        success, report = app.process_images(
            [input_dir],
            output_dir,
            {"recursive": True}
        )
        
        # Check the result
        assert success
        assert report is not None
        assert os.path.exists(os.path.join(output_dir, "report.txt"))
        assert len(os.listdir(output_dir)) > 1
```

### Performance Tests

Performance tests test the performance of the application. They are located in the `tests/integration/test_performance.py` file.

Example:

```python
def test_parallel_vs_sequential():
    """Test parallel vs sequential processing performance."""
    # Create a large set of test images
    images = create_large_test_dataset()
    
    # Measure sequential processing time
    start_time = time.time()
    app = ApplicationCore(parallel_processing=False)
    app.process_images(images, "output", {})
    sequential_time = time.time() - start_time
    
    # Measure parallel processing time
    start_time = time.time()
    app = ApplicationCore(parallel_processing=True)
    app.process_images(images, "output", {})
    parallel_time = time.time() - start_time
    
    # Check that parallel processing is faster
    assert parallel_time < sequential_time
```

### Error Handling Tests

Error handling tests test the application's ability to handle errors. They are located in the `tests/integration/test_error_handling.py` file.

Example:

```python
def test_corrupted_image():
    """Test handling of corrupted images."""
    # Create a corrupted image
    image_path = create_corrupted_image()
    
    # Run the application
    app = ApplicationCore()
    success, report = app.process_images(
        [image_path],
        "output",
        {}
    )
    
    # Check that the application handled the error
    assert success  # The application should still succeed
    assert len(app.errors) == 1  # There should be one error
    assert "corrupted" in app.errors[0]["message"]  # The error should mention corruption
```

## Test Fixtures

Test fixtures are defined in the `tests/conftest.py` file. They provide reusable components for tests.

Example:

```python
@pytest.fixture
def test_image():
    """Create a test image."""
    with tempfile.NamedTemporaryFile(suffix=".jpg") as f:
        # Create a minimal valid JPEG file
        f.write(b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00\x48\x00\x48\x00\x00\xff\xdb\x00\x43\x00\xff\xc0\x00\x11\x08\x00\x01\x00\x01\x03\x01\x11\x00\xff\xc4\x00\x1f\x00\x00\x01\x05\x01\x01\x01\x01\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\xff\xda\x00\x08\x01\x01\x00\x00\x3f\x00\xd2\xcf\x20\xff\xd9")
        f.flush()
        yield f.name
```

## Mocking

Mocking is used to isolate components during testing. The `unittest.mock` module is used for mocking.

Example:

```python
@patch("photo_organizer.services.vision.tensorflow.TensorFlowVisionService.detect_objects")
def test_analyze_image_with_mock(mock_detect_objects):
    """Test analyze_image with a mock vision service."""
    # Configure the mock
    mock_detect_objects.return_value = ["person", "dog"]
    
    # Create an image
    image = Image("path/to/image.jpg")
    
    # Create the analysis service
    analysis_service = ImageAnalysisService()
    
    # Analyze the image
    result = analysis_service.analyze_image(image)
    
    # Check that the mock was called
    mock_detect_objects.assert_called_once()
    
    # Check the result
    assert "person" in image.objects
    assert "dog" in image.objects
```

## Test Data

Test data is created dynamically during tests. Helper functions are provided to create test data.

Example:

```python
def create_test_image(path, content=None):
    """Create a test image file."""
    # Create a minimal valid JPEG file
    with open(path, "wb") as f:
        f.write(b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00\x48\x00\x48\x00\x00\xff\xdb\x00\x43\x00\xff\xc0\x00\x11\x08\x00\x01\x00\x01\x03\x01\x11\x00\xff\xc4\x00\x1f\x00\x00\x01\x05\x01\x01\x01\x01\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\xff\xda\x00\x08\x01\x01\x00\x00\x3f\x00\xd2\xcf\x20\xff\xd9")
```

## Continuous Integration

Photo Organizer uses GitHub Actions for continuous integration. The CI pipeline runs tests on multiple platforms and Python versions.

The CI configuration is defined in the `.github/workflows/ci.yml` file.

## Test Coverage

Photo Organizer aims for high test coverage. The coverage report is generated during CI and is available as an artifact.

To check the current coverage:

```bash
pytest --cov=photo_organizer
```

## Writing Good Tests

### Test Naming

Test names should be descriptive and follow the pattern `test_<function_name>_<scenario>`.

Example:
- `test_process_images_with_valid_input`
- `test_process_images_with_invalid_input`
- `test_analyze_image_with_corrupted_image`

### Test Structure

Tests should follow the Arrange-Act-Assert (AAA) pattern:

1. **Arrange**: Set up the test data and environment
2. **Act**: Perform the action being tested
3. **Assert**: Check that the result is as expected

Example:

```python
def test_categorize_images():
    """Test that categorize_images correctly categorizes images."""
    # Arrange
    images = [
        Image("path/to/image1.jpg"),
        Image("path/to/image2.jpg"),
    ]
    images[0].objects = ["person", "dog"]
    images[1].objects = ["car", "tree"]
    
    categorization_service = CategorizationService()
    
    # Act
    category_tree = categorization_service.categorize_images(images)
    
    # Assert
    assert len(category_tree.get_categories()) > 0
    assert any(category.name == "People" for category in category_tree.get_categories())
    assert any(category.name == "Vehicles" for category in category_tree.get_categories())
```

### Test Independence

Tests should be independent of each other. Each test should set up its own environment and clean up after itself.

### Test Edge Cases

Tests should cover edge cases and error conditions, not just the happy path.

Example edge cases:
- Empty input
- Invalid input
- Boundary conditions
- Resource limitations
- Concurrent access

## Debugging Tests

### Using pdb

You can use the Python debugger (pdb) to debug tests:

```bash
pytest --pdb tests/unit/test_core.py
```

### Using print

You can use print statements to debug tests:

```python
def test_something():
    result = some_function()
    print(f"Result: {result}")
    assert result == expected
```

Run pytest with the `-s` option to see print output:

```bash
pytest -s tests/unit/test_core.py
```

## Test Documentation

Tests should be well-documented. Each test function should have a docstring that explains what it tests.

Example:

```python
def test_process_images_with_valid_input():
    """
    Test that process_images correctly processes images with valid input.
    
    This test:
    1. Creates test images
    2. Calls process_images with valid input
    3. Checks that the images are processed correctly
    4. Checks that the report is generated
    """
    # Test implementation
```