# Photo Organizer Examples and Tutorials

This document provides practical examples and tutorials for using Photo Organizer in various scenarios.

## Basic Examples

### Example 1: Organizing a Vacation Photo Collection

Suppose you have a folder of vacation photos that you want to organize:

```
photo-organizer ~/Pictures/Vacation2025 ~/Pictures/Organized_Vacation --recursive
```

This command will:
1. Scan all images in the Vacation2025 folder and its subfolders
2. Analyze the content of each image
3. Create a logical folder structure in the Organized_Vacation folder
4. Copy and rename the images based on their content
5. Generate an HTML report in the Organized_Vacation folder

### Example 2: Organizing Photos with Custom Settings

For more control over the organization process:

```
photo-organizer ~/Pictures/Family ~/Pictures/Organized_Family --similarity-threshold 0.8 --max-category-depth 4 --report both
```

This command will:
1. Use a higher similarity threshold (0.8) for more specific categories
2. Create a deeper folder hierarchy (up to 4 levels)
3. Generate both HTML and text reports

### Example 3: Processing Large Collections

For large photo collections, enable parallel processing:

```
photo-organizer ~/Pictures/AllPhotos ~/Pictures/Organized_All --recursive --parallel --max-workers 8
```

This command will:
1. Process images in parallel using 8 worker threads
2. Significantly speed up the organization process for large collections

## Tutorials

### Tutorial 1: Organizing Photos by Event

In this tutorial, we'll organize a collection of photos from different events:

1. Prepare your photos:
   - Create a folder for each event (e.g., "Birthday", "Wedding", "Vacation")
   - Place relevant photos in each folder

2. Run Photo Organizer with recursive processing:
   ```
   photo-organizer ~/Pictures/Events ~/Pictures/Organized_Events --recursive
   ```

3. Review the results:
   - Open the HTML report in your browser
   - Check the folder structure created in the output directory
   - Verify that photos are grouped logically

4. Fine-tune if needed:
   - If categories are too broad, increase the similarity threshold
   - If categories are too specific, decrease the similarity threshold
   ```
   photo-organizer ~/Pictures/Events ~/Pictures/Organized_Events_Refined --recursive --similarity-threshold 0.75
   ```

### Tutorial 2: Creating a Photo Archive

In this tutorial, we'll create a well-organized photo archive from a messy collection:

1. Prepare your photos:
   - Gather all photos you want to archive in a single location
   - No need to pre-organize them

2. Run Photo Organizer with a deep category hierarchy:
   ```
   photo-organizer ~/Pictures/Messy ~/Pictures/Archive --recursive --max-category-depth 5
   ```

3. Create a comprehensive report:
   ```
   photo-organizer ~/Pictures/Messy ~/Pictures/Archive --recursive --report both --report-path ~/Documents/photo_archive_report
   ```

4. Review and share the report:
   - Open the HTML report in your browser
   - Share the report with others who need to access the archive

### Tutorial 3: Using the GUI for Interactive Organization

In this tutorial, we'll use the graphical interface for more interactive control:

1. Launch the GUI:
   ```
   photo-organizer --gui
   ```

2. Select input files:
   - Drag and drop files or folders into the application window
   - Or click "Open Files..." or "Open Folder..." to browse for files

3. Configure settings:
   - Click "Edit" > "Preferences..." to open the settings dialog
   - Adjust similarity threshold, category depth, and other options
   - Click "OK" to save settings

4. Select output location:
   - Click "Organize" to start the process
   - Select an output directory when prompted

5. Monitor progress:
   - Watch the progress bar and log messages
   - Use the "Pause" button if needed
   - Wait for the process to complete

6. Review results:
   - The report will open automatically when processing is complete
   - Browse the organized files in the output directory

## Advanced Examples

### Example 4: Batch Processing Multiple Collections

Process multiple collections in sequence:

```bash
#!/bin/bash

collections=("Vacation" "Family" "Work" "Hobbies")

for collection in "${collections[@]}"; do
    photo-organizer ~/Pictures/$collection ~/Pictures/Organized/$collection --recursive
done
```

### Example 5: Integration with Other Tools

Use Photo Organizer as part of a larger workflow:

```bash
#!/bin/bash

# Step 1: Backup original photos
rsync -av ~/Pictures/Original/ ~/Backup/Photos/

# Step 2: Organize photos
photo-organizer ~/Pictures/Original/ ~/Pictures/Organized/ --recursive

# Step 3: Generate thumbnails for web gallery
cd ~/Pictures/Organized/
find . -name "*.jpg" -exec convert {} -resize 200x200 {}.thumb.jpg \;

# Step 4: Create a simple web gallery
echo "<html><body>" > gallery.html
find . -name "*.thumb.jpg" -exec echo "<img src=\"{}\">" \; >> gallery.html
echo "</body></html>" >> gallery.html
```

### Example 6: Custom Report Processing

Extract information from the report for further processing:

```python
import json
import os

# Assuming the report is saved as JSON
with open("report.json", "r") as f:
    report = json.load(f)

# Extract statistics
total_files = report["summary"]["total_files"]
processed_files = report["summary"]["processed_files"]
folders_created = report["summary"]["folders_created"]

print(f"Processed {processed_files} of {total_files} files")
print(f"Created {folders_created} folders")

# Extract file mappings
for mapping in report["file_mappings"]:
    original = mapping["original_path"]
    new = mapping["new_path"]
    category = mapping["category"]
    print(f"{os.path.basename(original)} -> {category}/{os.path.basename(new)}")
```

## Tips and Best Practices

1. **Start Small**: When first using Photo Organizer, start with a small collection to understand how it categorizes your photos.

2. **Use Descriptive Output Paths**: Name your output directories descriptively to help you remember what's in them.

3. **Keep Original Files**: Photo Organizer creates copies of your images by default, so your originals are safe.

4. **Experiment with Settings**: Try different similarity thresholds and category depths to find what works best for your collection.

5. **Use Reports**: Always review the generated reports to understand how your photos were organized.

6. **Regular Organization**: Run Photo Organizer regularly on new photos rather than waiting until you have thousands to process.

7. **Combine with Backup Strategy**: Use Photo Organizer as part of a comprehensive backup and organization strategy.

8. **Pre-filter Large Collections**: For very large collections, consider pre-filtering by date or other criteria before organizing.