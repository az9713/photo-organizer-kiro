#!/usr/bin/env python3
"""
Enhanced Photo Organizer with TensorFlow-based image analysis.
"""

import os
import sys
import shutil
import datetime
import hashlib
from pathlib import Path
from PIL import Image
from PIL.ExifTags import TAGS
import numpy as np
import tensorflow as tf
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input, decode_predictions
from tensorflow.keras.preprocessing import image as keras_image

class TensorFlowImageAnalyzer:
    """An image analyzer that uses TensorFlow for content recognition."""
    
    def __init__(self):
        """Initialize the TensorFlow image analyzer."""
        print("Loading TensorFlow model...")
        self.model = MobileNetV2(weights='imagenet')
        print("TensorFlow model loaded successfully!")
    
    def analyze_image(self, image_path):
        """Analyze an image and return its features."""
        features = {
            'date': self._get_image_date(image_path),
            'size': self._get_image_size(image_path),
            'hash': self._get_image_hash(image_path),
            'colors': self._get_dominant_colors(image_path),
            'metadata': self._get_metadata(image_path),
            'location': self._get_location(image_path),
            'content_tags': self._get_content_tags(image_path),
        }
        return features
    
    def _get_image_date(self, image_path):
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
    
    def _get_image_size(self, image_path):
        """Get the dimensions of an image."""
        try:
            with Image.open(image_path) as img:
                return img.size
        except Exception:
            return (0, 0)
    
    def _get_image_hash(self, image_path):
        """Generate a simple hash of the image content."""
        try:
            with open(image_path, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except Exception:
            return None
    
    def _get_dominant_colors(self, image_path, num_colors=5):
        """Extract dominant colors from the image."""
        try:
            with Image.open(image_path) as img:
                # Resize image to speed up processing
                img = img.resize((100, 100))
                # Convert to RGB if not already
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Get pixel data
                pixels = list(img.getdata())
                
                # Count color frequencies
                color_counts = {}
                for pixel in pixels:
                    # Simplify colors by rounding to nearest 10
                    simplified = tuple(round(c/10)*10 for c in pixel)
                    if simplified in color_counts:
                        color_counts[simplified] += 1
                    else:
                        color_counts[simplified] = 1
                
                # Get most common colors
                dominant = sorted(color_counts.items(), key=lambda x: x[1], reverse=True)[:num_colors]
                return [color for color, _ in dominant]
        except Exception:
            return []
    
    def _get_metadata(self, image_path):
        """Extract metadata from the image."""
        metadata = {}
        try:
            with Image.open(image_path) as img:
                exif_data = img._getexif()
                if exif_data:
                    for tag_id, value in exif_data.items():
                        tag = TAGS.get(tag_id, tag_id)
                        # Skip binary data
                        if isinstance(value, bytes):
                            continue
                        metadata[tag] = str(value)
        except Exception:
            pass
        return metadata
    
    def _get_location(self, image_path):
        """Extract GPS location from image if available."""
        try:
            with Image.open(image_path) as img:
                exif_data = img._getexif()
                if exif_data:
                    for tag_id, value in exif_data.items():
                        tag = TAGS.get(tag_id, tag_id)
                        if tag == 'GPSInfo':
                            # Parse GPS data
                            lat_ref = value.get(1, 'N')
                            lat = value.get(2)
                            lon_ref = value.get(3, 'E')
                            lon = value.get(4)
                            
                            if lat and lon:
                                # Convert to decimal degrees
                                lat_val = self._convert_to_degrees(lat)
                                if lat_ref == 'S':
                                    lat_val = -lat_val
                                
                                lon_val = self._convert_to_degrees(lon)
                                if lon_ref == 'W':
                                    lon_val = -lon_val
                                
                                return (lat_val, lon_val)
        except Exception:
            pass
        return None
    
    def _convert_to_degrees(self, value):
        """Convert GPS coordinates to decimal degrees."""
        d, m, s = value
        return d + (m / 60.0) + (s / 3600.0)
    
    def _get_content_tags(self, image_path):
        """Use TensorFlow to identify content in the image."""
        try:
            # Load and preprocess the image
            img = keras_image.load_img(image_path, target_size=(224, 224))
            x = keras_image.img_to_array(img)
            x = np.expand_dims(x, axis=0)
            x = preprocess_input(x)
            
            # Make prediction
            preds = self.model.predict(x)
            
            # Decode and extract top 5 predictions
            results = decode_predictions(preds, top=5)[0]
            
            # Return list of tags
            return [result[1] for result in results]
        except Exception as e:
            print(f"Error analyzing image content: {e}")
            return []

class TensorFlowCategorizer:
    """A categorizer that uses TensorFlow-based image analysis."""
    
    def categorize_images(self, images):
        """Categorize images based on their features."""
        result = {
            'by_date': self._categorize_by_date(images),
            'by_color': self._categorize_by_color(images),
            'by_size': self._categorize_by_size(images),
            'by_content': self._categorize_by_content(images),
            'by_location': self._categorize_by_location(images),
            'duplicates': self._find_duplicates(images)
        }
        return result
    
    def _categorize_by_date(self, images):
        """Group images by date."""
        categories = {}
        for img_path, features in images.items():
            date = features['date']
            if date not in categories:
                categories[date] = []
            categories[date].append(img_path)
        return categories
    
    def _categorize_by_color(self, images):
        """Group images by dominant color."""
        categories = {
            'red': [],
            'green': [],
            'blue': [],
            'yellow': [],
            'orange': [],
            'purple': [],
            'pink': [],
            'brown': [],
            'black': [],
            'white': [],
            'gray': []
        }
        
        for img_path, features in images.items():
            if not features['colors']:
                continue
                
            # Get the most dominant color
            dominant = features['colors'][0]
            r, g, b = dominant
            
            # Simple color classification
            if max(r, g, b) < 50:
                categories['black'].append(img_path)
            elif min(r, g, b) > 200:
                categories['white'].append(img_path)
            elif abs(r - g) < 30 and abs(r - b) < 30 and abs(g - b) < 30:
                categories['gray'].append(img_path)
            elif r > 1.5 * max(g, b):
                categories['red'].append(img_path)
            elif g > 1.5 * max(r, b):
                categories['green'].append(img_path)
            elif b > 1.5 * max(r, g):
                categories['blue'].append(img_path)
            elif r > 200 and g > 150 and b < 100:
                categories['yellow'].append(img_path)
            elif r > 200 and g < 150 and b < 100:
                categories['orange'].append(img_path)
            elif r > 150 and b > 150 and g < 100:
                categories['purple'].append(img_path)
            elif r > 200 and b > 150 and g < 150:
                categories['pink'].append(img_path)
            elif r > 100 and g > 50 and b < 50:
                categories['brown'].append(img_path)
            else:
                # Default to the channel with highest value
                max_channel = max(r, g, b)
                if max_channel == r:
                    categories['red'].append(img_path)
                elif max_channel == g:
                    categories['green'].append(img_path)
                else:
                    categories['blue'].append(img_path)
                    
        # Remove empty categories
        return {k: v for k, v in categories.items() if v}
    
    def _categorize_by_size(self, images):
        """Group images by size."""
        categories = {
            'small': [],    # < 1MP
            'medium': [],   # 1-5MP
            'large': [],    # 5-10MP
            'xlarge': []    # > 10MP
        }
        
        for img_path, features in images.items():
            width, height = features['size']
            megapixels = (width * height) / 1000000
            
            if megapixels < 1:
                categories['small'].append(img_path)
            elif megapixels < 5:
                categories['medium'].append(img_path)
            elif megapixels < 10:
                categories['large'].append(img_path)
            else:
                categories['xlarge'].append(img_path)
                
        return {k: v for k, v in categories.items() if v}
    
    def _categorize_by_content(self, images):
        """Group images by content tags."""
        categories = {}
        
        for img_path, features in images.items():
            content_tags = features.get('content_tags', [])
            
            for tag in content_tags:
                if tag not in categories:
                    categories[tag] = []
                categories[tag].append(img_path)
                
        # Remove categories with fewer than 2 images
        return {k: v for k, v in categories.items() if len(v) >= 2}
    
    def _categorize_by_location(self, images):
        """Group images by location if GPS data is available."""
        categories = {}
        
        for img_path, features in images.items():
            location = features['location']
            if not location:
                continue
                
            # Round coordinates to group nearby locations
            lat, lon = location
            lat_rounded = round(lat, 2)
            lon_rounded = round(lon, 2)
            location_key = f"{lat_rounded},{lon_rounded}"
            
            if location_key not in categories:
                categories[location_key] = []
            categories[location_key].append(img_path)
            
        return categories
    
    def _find_duplicates(self, images):
        """Find duplicate images based on their hash."""
        hashes = {}
        duplicates = []
        
        for img_path, features in images.items():
            img_hash = features['hash']
            if img_hash:
                if img_hash in hashes:
                    duplicates.append((hashes[img_hash], img_path))
                else:
                    hashes[img_hash] = img_path
        
        return duplicates

class TensorFlowPhotoOrganizer:
    """A photo organizer that uses TensorFlow for image analysis."""
    
    def __init__(self):
        """Initialize the photo organizer."""
        self.analyzer = TensorFlowImageAnalyzer()
        self.categorizer = TensorFlowCategorizer()
    
    def process_images(self, input_path, output_path, organization_type='all'):
        """
        Process images from input path to output path.
        
        Args:
            input_path: Path to input directory or file
            output_path: Path to output directory
            organization_type: Type of organization ('date', 'color', 'size', 'content', 'all')
        """
        print(f"Processing images from {input_path} to {output_path}")
        start_time = datetime.datetime.now()
        
        # Create output directory if it doesn't exist
        os.makedirs(output_path, exist_ok=True)
        
        # Scan input path for image files
        print("Scanning for image files...")
        image_paths = self._scan_for_images(input_path)
        
        if not image_paths:
            print("No image files found.")
            return False
        
        print(f"Found {len(image_paths)} image files")
        
        # Analyze images
        print("Analyzing images...")
        analyzed_images = {}
        for i, path in enumerate(image_paths):
            print(f"Analyzing image {i+1}/{len(image_paths)}: {path}")
            features = self.analyzer.analyze_image(path)
            analyzed_images[path] = features
        
        # Categorize images
        print("Categorizing images...")
        categories = self.categorizer.categorize_images(analyzed_images)
        
        # Organize images based on selected organization type
        print("Organizing images...")
        if organization_type == 'date' or organization_type == 'all':
            self._organize_by_date(categories['by_date'], output_path)
        
        if organization_type == 'color' or organization_type == 'all':
            color_output = os.path.join(output_path, 'by_color')
            self._organize_by_color(categories['by_color'], color_output)
        
        if organization_type == 'size' or organization_type == 'all':
            size_output = os.path.join(output_path, 'by_size')
            self._organize_by_size(categories['by_size'], size_output)
        
        if organization_type == 'content' or organization_type == 'all':
            content_output = os.path.join(output_path, 'by_content')
            self._organize_by_content(categories['by_content'], content_output)
        
        # Handle duplicates
        if categories['duplicates']:
            print("\nPotential duplicate images found:")
            duplicates_dir = os.path.join(output_path, 'duplicates')
            os.makedirs(duplicates_dir, exist_ok=True)
            
            with open(os.path.join(duplicates_dir, 'duplicates.txt'), 'w') as f:
                f.write("# Duplicate Images Report\n\n")
                
                for i, (original, duplicate) in enumerate(categories['duplicates']):
                    print(f"  Original: {original}")
                    print(f"  Duplicate: {duplicate}")
                    print()
                    
                    # Write to report
                    f.write(f"## Duplicate Set {i+1}\n")
                    f.write(f"Original: {original}\n")
                    f.write(f"Duplicate: {duplicate}\n\n")
                    
                    # Copy duplicates to duplicates directory for review
                    try:
                        shutil.copy2(duplicate, os.path.join(duplicates_dir, f"duplicate_{i+1}{os.path.splitext(duplicate)[1]}"))
                    except Exception as e:
                        print(f"Error copying duplicate: {e}")
        
        # Generate report
        end_time = datetime.datetime.now()
        processing_time = (end_time - start_time).total_seconds()
        self._generate_report(analyzed_images, categories, output_path, processing_time)
        
        print(f"Successfully processed {len(image_paths)} images in {processing_time:.2f} seconds")
        print(f"Output directory: {output_path}")
        
        return True
    
    def _scan_for_images(self, input_path):
        """Scan for image files in the input path."""
        image_paths = []
        for root, _, files in os.walk(input_path):
            for file in files:
                if file.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp')):
                    image_paths.append(os.path.join(root, file))
        return image_paths
    
    def _organize_by_date(self, date_categories, output_path):
        """Organize images by date."""
        organized_count = 0
        
        for date, images in date_categories.items():
            # Create date directory
            date_dir = os.path.join(output_path, date)
            os.makedirs(date_dir, exist_ok=True)
            
            # Copy images to date directory
            for path in images:
                try:
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
                    print(f"Error copying image {path}: {e}")
        
        print(f"Organized {organized_count} images into date-based folders")
    
    def _organize_by_color(self, color_categories, output_path):
        """Organize images by dominant color."""
        organized_count = 0
        
        for color, images in color_categories.items():
            # Create color directory
            color_dir = os.path.join(output_path, color)
            os.makedirs(color_dir, exist_ok=True)
            
            # Copy images to color directory
            for path in images:
                try:
                    # Generate new filename
                    filename = os.path.basename(path)
                    new_path = os.path.join(color_dir, filename)
                    
                    # If file already exists, add a suffix
                    if os.path.exists(new_path):
                        base_name, ext = os.path.splitext(filename)
                        counter = 1
                        while os.path.exists(new_path):
                            new_filename = f"{base_name}_{counter}{ext}"
                            new_path = os.path.join(color_dir, new_filename)
                            counter += 1
                    
                    # Copy file
                    shutil.copy2(path, new_path)
                    organized_count += 1
                    
                except Exception as e:
                    print(f"Error copying image {path}: {e}")
        
        print(f"Organized {organized_count} images into color-based folders")
    
    def _organize_by_size(self, size_categories, output_path):
        """Organize images by size."""
        organized_count = 0
        
        for size, images in size_categories.items():
            # Create size directory
            size_dir = os.path.join(output_path, size)
            os.makedirs(size_dir, exist_ok=True)
            
            # Copy images to size directory
            for path in images:
                try:
                    # Generate new filename
                    filename = os.path.basename(path)
                    new_path = os.path.join(size_dir, filename)
                    
                    # If file already exists, add a suffix
                    if os.path.exists(new_path):
                        base_name, ext = os.path.splitext(filename)
                        counter = 1
                        while os.path.exists(new_path):
                            new_filename = f"{base_name}_{counter}{ext}"
                            new_path = os.path.join(size_dir, new_filename)
                            counter += 1
                    
                    # Copy file
                    shutil.copy2(path, new_path)
                    organized_count += 1
                    
                except Exception as e:
                    print(f"Error copying image {path}: {e}")
        
        print(f"Organized {organized_count} images into size-based folders")
    
    def _organize_by_content(self, content_categories, output_path):
        """Organize images by content tags."""
        organized_count = 0
        
        for content, images in content_categories.items():
            # Create content directory
            content_dir = os.path.join(output_path, content)
            os.makedirs(content_dir, exist_ok=True)
            
            # Copy images to content directory
            for path in images:
                try:
                    # Generate new filename
                    filename = os.path.basename(path)
                    new_path = os.path.join(content_dir, filename)
                    
                    # If file already exists, add a suffix
                    if os.path.exists(new_path):
                        base_name, ext = os.path.splitext(filename)
                        counter = 1
                        while os.path.exists(new_path):
                            new_filename = f"{base_name}_{counter}{ext}"
                            new_path = os.path.join(content_dir, new_filename)
                            counter += 1
                    
                    # Copy file
                    shutil.copy2(path, new_path)
                    organized_count += 1
                    
                except Exception as e:
                    print(f"Error copying image {path}: {e}")
        
        print(f"Organized {organized_count} images into content-based folders")
    
    def _generate_report(self, analyzed_images, categories, output_path, processing_time):
        """Generate a report of the organization process."""
        report_path = os.path.join(output_path, 'report.html')
        
        with open(report_path, 'w') as f:
            # Write HTML header
            f.write("""<!DOCTYPE html>
<html>
<head>
    <title>Photo Organizer Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        h1 { color: #2c3e50; }
        h2 { color: #3498db; }
        .stats { background-color: #f8f9fa; padding: 15px; border-radius: 5px; }
        .category { margin-bottom: 20px; }
        table { border-collapse: collapse; width: 100%; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
        tr:nth-child(even) { background-color: #f9f9f9; }
    </style>
</head>
<body>
    <h1>Photo Organizer Report</h1>
""")
            
            # Write summary statistics
            f.write(f"""
    <div class="stats">
        <h2>Summary</h2>
        <p>Total images processed: {len(analyzed_images)}</p>
        <p>Processing time: {processing_time:.2f} seconds</p>
        <p>Potential duplicates found: {len(categories['duplicates'])}</p>
    </div>
""")
            
            # Write date categories
            f.write("""
    <div class="category">
        <h2>Images by Date</h2>
        <table>
            <tr>
                <th>Date</th>
                <th>Number of Images</th>
            </tr>
""")
            
            for date, images in categories['by_date'].items():
                f.write(f"""
            <tr>
                <td>{date}</td>
                <td>{len(images)}</td>
            </tr>
""")
            
            f.write("""
        </table>
    </div>
""")
            
            # Write color categories
            f.write("""
    <div class="category">
        <h2>Images by Color</h2>
        <table>
            <tr>
                <th>Color</th>
                <th>Number of Images</th>
            </tr>
""")
            
            for color, images in categories['by_color'].items():
                f.write(f"""
            <tr>
                <td>{color}</td>
                <td>{len(images)}</td>
            </tr>
""")
            
            f.write("""
        </table>
    </div>
""")
            
            # Write size categories
            f.write("""
    <div class="category">
        <h2>Images by Size</h2>
        <table>
            <tr>
                <th>Size Category</th>
                <th>Number of Images</th>
            </tr>
""")
            
            for size, images in categories['by_size'].items():
                f.write(f"""
            <tr>
                <td>{size}</td>
                <td>{len(images)}</td>
            </tr>
""")
            
            f.write("""
        </table>
    </div>
""")
            
            # Write content categories
            if 'by_content' in categories and categories['by_content']:
                f.write("""
    <div class="category">
        <h2>Images by Content</h2>
        <table>
            <tr>
                <th>Content Tag</th>
                <th>Number of Images</th>
            </tr>
""")
                
                for content, images in categories['by_content'].items():
                    f.write(f"""
            <tr>
                <td>{content}</td>
                <td>{len(images)}</td>
            </tr>
""")
                
                f.write("""
        </table>
    </div>
""")
            
            # Write duplicates
            if categories['duplicates']:
                f.write("""
    <div class="category">
        <h2>Duplicate Images</h2>
        <table>
            <tr>
                <th>Original</th>
                <th>Duplicate</th>
            </tr>
""")
                
                for original, duplicate in categories['duplicates']:
                    f.write(f"""
            <tr>
                <td>{original}</td>
                <td>{duplicate}</td>
            </tr>
""")
                
                f.write("""
        </table>
    </div>
""")
            
            # Write HTML footer
            f.write("""
</body>
</html>
""")
        
        print(f"Report generated: {report_path}")

def main():
    """Main entry point for the script."""
    if len(sys.argv) < 3 or len(sys.argv) > 4:
        print("Usage: python tensorflow_photo_organizer.py <input_path> <output_path> [organization_type]")
        print("Organization types: date, color, size, content, all (default: all)")
        return 1
    
    input_path = sys.argv[1]
    output_path = sys.argv[2]
    organization_type = sys.argv[3] if len(sys.argv) == 4 else 'all'
    
    if organization_type not in ['date', 'color', 'size', 'content', 'all']:
        print("Invalid organization type. Choose from: date, color, size, content, all")
        return 1
    
    organizer = TensorFlowPhotoOrganizer()
    success = organizer.process_images(input_path, output_path, organization_type)
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())