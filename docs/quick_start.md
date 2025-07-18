# Photo Organizer Quick Start Guide

## Installation

```bash
pip install photo-organizer
```

For detailed installation instructions, see the [Installation Guide](installation.md).

## Command Line Usage

### Basic Organization

Organize all images in a directory:

```bash
photo-organizer ~/Pictures/Vacation ~/Pictures/Organized
```

### Recursive Organization

Organize all images in a directory and its subdirectories:

```bash
photo-organizer ~/Pictures/Vacation ~/Pictures/Organized --recursive
```

### Parallel Processing

Speed up organization with parallel processing:

```bash
photo-organizer ~/Pictures/Vacation ~/Pictures/Organized --recursive --parallel
```

### Generate Reports

Generate both HTML and text reports:

```bash
photo-organizer ~/Pictures/Vacation ~/Pictures/Organized --report both
```

## GUI Usage

### Launch the GUI

```bash
photo-organizer --gui
```

### Organize Images

1. **Select Images**:
   - Click "Open Files..." or "Open Folder..."
   - Or drag and drop files/folders

2. **Configure Options** (optional):
   - Click "Edit" > "Preferences..."

3. **Start Processing**:
   - Click "Organize"
   - Select an output directory when prompted

4. **View Results**:
   - When processing is complete, the report will open automatically
   - Organized images will be in the selected output directory

## Next Steps

For more detailed information, refer to the [User Guide](user_guide.md).