# Photo Organizer Installation Guide

This guide provides detailed instructions for installing Photo Organizer on different platforms.

## System Requirements

- **Operating System**: Windows 10+, macOS 10.14+, or Linux (Ubuntu 18.04+, Fedora 30+, etc.)
- **Python**: Version 3.9 or higher
- **RAM**: Minimum 4GB, 8GB+ recommended for large photo collections
- **Disk Space**: 500MB for installation, plus space for your photos
- **GPU**: Optional, but recommended for faster image analysis

## Installing Python

Photo Organizer requires Python 3.9 or higher. If you don't have Python installed, follow these instructions:

### Windows

1. Download the latest Python installer from [python.org](https://www.python.org/downloads/)
2. Run the installer
3. Check "Add Python to PATH" during installation
4. Click "Install Now"
5. Verify installation by opening Command Prompt and typing:
   ```
   python --version
   ```

### macOS

1. Install Homebrew if you don't have it:
   ```
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```
2. Install Python:
   ```
   brew install python
   ```
3. Verify installation:
   ```
   python3 --version
   ```

### Linux

#### Ubuntu/Debian
```
sudo apt update
sudo apt install python3 python3-pip python3-venv
```

#### Fedora
```
sudo dnf install python3 python3-pip
```

#### Arch Linux
```
sudo pacman -S python python-pip
```

## Installing Photo Organizer

### Method 1: Using pip (Recommended)

The simplest way to install Photo Organizer is using pip:

```
pip install photo-organizer
```

To upgrade to the latest version:

```
pip install --upgrade photo-organizer
```

### Method 2: From Source

For the latest development version or to contribute to the project:

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

### Method 3: Standalone Executable

For users who prefer not to install Python, we provide standalone executables:

1. Download the latest release for your platform from [GitHub Releases](https://github.com/example/photo-organizer/releases)
2. Extract the archive
3. Run the executable:
   - Windows: `photo-organizer.exe`
   - macOS: `photo-organizer.app`
   - Linux: `photo-organizer`

## Installing Dependencies

Photo Organizer depends on several libraries for image processing and computer vision. Most dependencies are installed automatically, but some may require additional steps:

### TensorFlow Installation

TensorFlow is a critical dependency for the image analysis features. Here are important considerations for installing TensorFlow:

#### TensorFlow Version Compatibility

For Windows users:
- TensorFlow 2.10 is the last version that supports native GPU on Windows
- For newer versions, use WSL2 or the CPU-only version

```bash
# For Windows with GPU support (recommended)
pip install "tensorflow<2.11"

# For CPU-only (all platforms)
pip install tensorflow
```

#### NumPy Compatibility

TensorFlow has specific NumPy version requirements:
- TensorFlow 2.10 works best with NumPy 1.24.x (not compatible with NumPy 2.x)
- If you encounter errors about NumPy, downgrade to a compatible version:

```bash
pip install numpy==1.24.3
```

#### Visual C++ Redistributable Requirement

On Windows, TensorFlow requires Microsoft Visual C++ Redistributable:
1. Download and install [Microsoft Visual C++ Redistributable](https://aka.ms/vs/17/release/vc_redist.x64.exe)
2. Restart your computer after installation

#### TensorFlow with GPU Support (Optional)

For faster image analysis, you can install TensorFlow with GPU support:

1. Install CUDA and cuDNN following the [TensorFlow GPU guide](https://www.tensorflow.org/install/gpu)
2. For Windows, use:
   ```
   pip install "tensorflow<2.11"
   ```
3. For Linux/macOS, use:
   ```
   pip install tensorflow[and-cuda]
   ```

### PyQt6 on Linux

On some Linux distributions, you may need to install additional packages for PyQt6:

#### Ubuntu/Debian
```
sudo apt install python3-pyqt6 libxcb-xinerama0
```

#### Fedora
```
sudo dnf install python3-qt6
```

#### Arch Linux
```
sudo pacman -S python-pyqt6
```

## Verifying Installation

To verify that Photo Organizer is installed correctly:

1. Open a terminal or command prompt
2. Run:
   ```
   photo-organizer --version
   ```

You should see the version number of Photo Organizer.

## Troubleshooting

### Common Installation Issues

#### "Command not found" Error

If you get a "command not found" error when trying to run Photo Organizer, make sure:

1. Python is in your PATH
2. The package was installed correctly
3. If using a virtual environment, it is activated

#### Missing Dependencies

If you encounter errors about missing dependencies:

1. Try reinstalling with all dependencies:
   ```
   pip install --force-reinstall photo-organizer[all]
   ```

2. Check if any system libraries are missing (especially on Linux)

#### Permission Errors

If you get permission errors during installation:

1. On Windows, run Command Prompt as Administrator
2. On macOS/Linux, use `sudo` or install in a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate
   pip install photo-organizer
   ```

### Getting Help

If you encounter issues not covered in this guide, please:

1. Check the [FAQ](https://example.com/photo-organizer/faq)
2. Search for similar issues in the [issue tracker](https://github.com/example/photo-organizer/issues)
3. Submit a new issue with detailed information about your installation problem

## Next Steps

After installation, check out the [User Guide](user_guide.md) to learn how to use Photo Organizer.