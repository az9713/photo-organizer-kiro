#!/usr/bin/env python3
"""
Enhanced script to organize images into folders based on their creation date.
"""

import os
import sys
import shutil
import datetime
from pathlib import Path
from PIL import Image
from PIL.ExifTags import TAGS

def get_image_date(image_path):
    """Extract the date from image EXIF data or use file modification date as fallback."""
    try:
        # Try to get EXIF data
        with Image.open(image_path) as img:
            exif_data = img._getexif()
            if exif_data:
                # Look for DateTimeOriginal or DateTime tag
                for tag_id, value in exif_data.items():
                    tag = TAGS.get(tag_id, tag_id)
                    if tag == 'DateTimeOriginal' or tag == 'DateTime':
                        # Parse the date string (format: 'YYYY:MM:DD HH:MM:SS')
                        date_str = value.split()[0].replace(':', '-', 2)
                        return date_str
    except Exception:
        pass
    
    # Fallback to file modification time
    mod_time = os.path.getmtime(image_path)
    date_obj = datetime.datetime.fromtimestamp(mod_time)
    return date_obj.strftime('%Y-%m-%d')

def main():
    """Main entry point for the script."""
    if len(sys.argv) != 3:
        print("Usage: python simple_copy.py <input_path> <output_path>")
        return 1
    
    input_path = sys.argv[1]
    output_path = sys.argv[2]
    
    print(f"Organizing images from {input_path} to {output_path}")
    
    # Create output directory if it doesn't exist
    os.makedirs(output_path, exist_ok=True)
    
    # Scan input path for image files
    print("Scanning for image files...")
    image_paths = []
    for root, _, files in os.walk(input_path):
        for file in files:
            if file.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp')):
                image_paths.append(os.path.join(root, file))
    
    print(f"Found {len(image_paths)} image files")
    
    # Organize images by date
    print("Organizing images by date...")
    organized_count = 0
    for i, path in enumerate(image_paths):
        try:
            print(f"Processing image {i+1}/{len(image_paths)}: {path}")
            
            # Get image date
            image_date = get_image_date(path)
            
            # Create date directory
            date_dir = os.path.join(output_path, image_date)
            os.makedirs(date_dir, exist_ok=True)
            
            # Generate new filename
            filename = os.path.basename(path)
            new_path = os.path.join(date_dir, filename)
            
            # If file already exists, add a suffix
            if os.path.exists(new_path):
                base_name, ext = os.path.splitext(filename)
                counter = 1
                while os.path.exists(new_path):
                    new_filename = f"{base_name}_{counter}{ext}"
                    new_path = os.path.join(date_dir, new_filename)
                    counter += 1
            
            # Copy file
            shutil.copy2(path, new_path)
            organized_count += 1
            
        except Exception as e:
            print(f"Error processing image {path}: {e}")
    
    print(f"Successfully organized {organized_count} of {len(image_paths)} images")
    print(f"Output directory: {output_path}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())