# Photo Organizer Examples

This document provides practical examples of using Photo Organizer in various scenarios.

## Basic Examples

### Organizing a Single Directory

```bash
photo-organizer ~/Pictures/Vacation ~/Pictures/Organized
```

This command will:
- Process all images in the `~/Pictures/Vacation` directory
- Create an organized folder structure in `~/Pictures/Organized`
- Generate a text report at `~/Pictures/Organized/report.txt`

### Organizing Multiple Directories

```bash
photo-organizer ~/Pictures/Vacation ~/Pictures/Family ~/Pictures/Organized
```

This command will:
- Process all images in both the `~/Pictures/Vacation` and `~/Pictures/Family` directories
- Create an organized folder structure in `~/Pictures/Organized`

### Organizing a Directory Tree

```bash
photo-organizer ~/Pictures ~/Pictures/Organized --recursive
```

This command will:
- Process all images in `~/Pictures` and all its subdirectories
- Create an organized folder structure in `~/Pictures/Organized`

## Advanced Examples

### Parallel Processing for Large Collections

```bash
photo-organizer ~/Pictures ~/Pictures/Organized --recursive --parallel --max-workers 8
```

This command will:
- Process all images in `~/Pictures` and all its subdirectories
- Use parallel processing with 8 worker threads
- Create an organized folder structure in `~/Pictures/Organized`

### Custom Similarity Threshold

```bash
photo-organizer ~/Pictures ~/Pictures/Organized --similarity-threshold 0.85
```

This command will:
- Process all images in `~/Pictures`
- Use a higher similarity threshold (0.85 instead of the default 0.7)
- This results in more granular categorization (fewer images per category)

### Generating HTML Reports

```bash
photo-organizer ~/Pictures ~/Pictures/Organized --report html
```

This command will:
- Process all images in `~/Pictures`
- Generate an HTML report at `~/Pictures/Organized/report.html`

### Custom Report Location

```bash
photo-organizer ~/Pictures ~/Pictures/Organized --report both --report-path ~/Documents/photo_report
```

This command will:
- Process all images in `~/Pictures`
- Generate both text and HTML reports at `~/Documents/photo_report.txt` and `~/Documents/photo_report.html`

## GUI Examples

### Basic Workflow

1. Launch the GUI:
   ```bash
   photo-organizer --gui
   ```

2. Click "Open Folder..." and select `~/Pictures/Vacation`

3. Click "Organize" and select `~/Pictures/Organized` as the output directory

4. Wait for processing to complete and view the report

### Drag and Drop

1. Launch the GUI:
   ```bash
   photo-organizer --gui
   ```

2. Drag and drop image files or folders from your file explorer onto the file selection area

3. Click "Organize" and select an output directory

### Using Preferences

1. Launch the GUI:
   ```bash
   photo-organizer --gui
   ```

2. Click "Edit" > "Preferences..."

3. Configure options:
   - Enable recursive processing
   - Enable parallel processing
   - Set max workers to 4
   - Set similarity threshold to 0.8
   - Select HTML report format

4. Click "OK" to save preferences

5. Select input files and organize as usual

## Batch Processing Examples

### Processing with a Script

Create a batch script (`process_photos.sh` or `process_photos.bat`):

```bash
#!/bin/bash
# Process multiple directories in batch

DIRS=("~/Pictures/Vacation2022" "~/Pictures/Vacation2023" "~/Pictures/Family")
OUTPUT="~/Pictures/Organized"

for DIR in "${DIRS[@]}"; do
    echo "Processing $DIR..."
    photo-organizer "$DIR" "$OUTPUT" --recursive
done

echo "All directories processed!"
```

### Scheduling Regular Organization

You can use cron (Linux/macOS) or Task Scheduler (Windows) to run Photo Organizer regularly:

#### Linux/macOS (cron)

Add to crontab (`crontab -e`):
```
# Run every Sunday at 2:00 AM
0 2 * * 0 photo-organizer ~/Pictures ~/Pictures/Organized --recursive
```

#### Windows (PowerShell)

```powershell
# Create a scheduled task to run weekly
$action = New-ScheduledTaskAction -Execute "photo-organizer.exe" -Argument "C:\Users\Username\Pictures C:\Users\Username\Pictures\Organized --recursive"
$trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Sunday -At 2am
Register-ScheduledTask -Action $action -Trigger $trigger -TaskName "Organize Photos" -Description "Weekly photo organization"
```

## Integration Examples

### Post-Processing with Custom Scripts

You can use the organized output as input for further processing:

```bash
#!/bin/bash
# Organize photos and then create a web gallery

# First, organize the photos
photo-organizer ~/Pictures/Vacation ~/Pictures/Organized --recursive

# Then, create a web gallery from the organized photos
gallery-generator ~/Pictures/Organized ~/WebGallery
```

### Using with Cloud Storage

```bash
#!/bin/bash
# Organize photos from cloud storage

# First, sync from cloud
rclone sync remote:Photos ~/Pictures/Cloud

# Then, organize the photos
photo-organizer ~/Pictures/Cloud ~/Pictures/Organized --recursive

# Finally, sync back to cloud if desired
rclone sync ~/Pictures/Organized remote:OrganizedPhotos
```