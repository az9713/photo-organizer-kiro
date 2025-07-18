"""
Core application logic for the Photo Organizer application.
"""

import os
import time
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union

from photo_organizer.models.category import Category
from photo_organizer.models.category_tree import CategoryTree
from photo_organizer.models.image import Image, ImageFormat
from photo_organizer.parallel import TaskScheduler
from photo_organizer.services.analysis import ImageAnalysisService
from photo_organizer.services.categorization import CategorizationService
from photo_organizer.services.file_mapping import FileMappingService
from photo_organizer.services.file_operations import FileOperationsService
from photo_organizer.services.file_system_manager import FileSystemManager
from photo_organizer.services.report_export import ReportExportService
from photo_organizer.services.reporting import FileMapping, FolderNode, Report, ReportFormat, ReportingService
from photo_organizer.ui.cli_progress import CLIProgressReporter, ProcessingStage


class ApplicationCore:
    """Core application logic for the Photo Organizer application."""
    
    def __init__(
        self,
        progress_reporter: Optional[CLIProgressReporter] = None,
        parallel_processing: bool = False,
        max_workers: int = 4,
    ) -> None:
        """
        Initialize the application core.
        
        Args:
            progress_reporter: Reporter for progress updates
            parallel_processing: Whether to use parallel processing
            max_workers: Maximum number of worker threads for parallel processing
        """
        self.progress_reporter = progress_reporter or CLIProgressReporter()
        
        # Initialize services
        self.file_system_manager = FileSystemManager()
        self.file_operations = FileOperationsService()
        self.analysis_service = ImageAnalysisService()
        self.categorization_service = CategorizationService()
        self.reporting_service = ReportingService()
        self.report_export_service = ReportExportService()
        self.file_mapping_service = FileMappingService()
        
        # State
        self.canceled = False
        self.paused = False
        self.current_stage = None
        
        # Parallel processing
        self.parallel_processing = parallel_processing
        self.max_workers = max_workers
        
        if parallel_processing:
            self._init_task_scheduler(max_workers)
    
    def _init_task_scheduler(self, max_workers: int) -> None:
        """
        Initialize the task scheduler for parallel processing.
        
        Args:
            max_workers: Maximum number of worker threads
        """
        # Create progress callback
        def progress_callback(name: str, processed: int, total: int) -> None:
            self.progress_reporter.update_progress(name, processed)
        
        # Create task scheduler
        self.task_scheduler = TaskScheduler(
            max_workers=max_workers,
            progress_callback=progress_callback,
            cancel_check=lambda: self.canceled,
            pause_check=lambda: self.paused,
        )
    
    def process_images(
        self,
        input_paths: List[str],
        output_path: str,
        options: Dict[str, Any],
    ) -> Tuple[bool, Optional[Report]]:
        """
        Process images from input paths to output path.
        
        Args:
            input_paths: List of input file or directory paths
            output_path: Output directory path
            options: Processing options
            
        Returns:
            A tuple of (success, report)
        """
        start_time = time.time()
        
        try:
            # Reset state
            self.canceled = False
            self.paused = False
            
            # Configure parallel processing
            parallel_processing = options.get("parallel_processing", self.parallel_processing)
            max_workers = options.get("max_workers", self.max_workers)
            
            if parallel_processing and not hasattr(self, "task_scheduler"):
                self._init_task_scheduler(max_workers)
            
            # Validate paths
            self._validate_paths(input_paths, output_path)
            
            # Initialize
            self.progress_reporter.start_stage(ProcessingStage.INITIALIZING)
            self._log_info(f"Processing {len(input_paths)} input paths to {output_path}")
            self._log_info(f"Options: {options}")
            
            # Create output directory if it doesn't exist
            os.makedirs(output_path, exist_ok=True)
            
            # Scan input paths
            self.progress_reporter.start_stage(ProcessingStage.SCANNING)
            image_paths = self._scan_input_paths(input_paths, options.get("recursive", False))
            
            if not image_paths:
                self._log_warning("No image files found in input paths")
                return False, None
            
            self._log_info(f"Found {len(image_paths)} image files")
            
            # Check for cancellation
            if self.canceled:
                self._log_info("Operation canceled")
                return False, None
            
            # Analyze images
            self.progress_reporter.start_stage(ProcessingStage.ANALYZING)
            images = self._analyze_images(image_paths)
            
            # Check for cancellation
            if self.canceled:
                self._log_info("Operation canceled")
                return False, None
            
            # Categorize images
            self.progress_reporter.start_stage(ProcessingStage.CATEGORIZING)
            category_tree = self._categorize_images(
                images,
                options.get("similarity_threshold", 0.7),
                options.get("max_category_depth", 3),
            )
            
            # Check for cancellation
            if self.canceled:
                self._log_info("Operation canceled")
                return False, None
            
            # Organize images
            self.progress_reporter.start_stage(ProcessingStage.ORGANIZING)
            organized_images = self._organize_images(images, category_tree, output_path)
            
            # Check for cancellation
            if self.canceled:
                self._log_info("Operation canceled")
                return False, None
            
            # Generate report
            self.progress_reporter.start_stage(ProcessingStage.REPORTING)
            report = self._generate_report(
                organized_images,
                output_path,
                time.time() - start_time,
                len(image_paths),
                len(organized_images),
                len(image_paths) - len(organized_images),
                len(self.progress_reporter.errors),
                self.progress_reporter.errors,
            )
            
            # Export report
            report_format = options.get("report_format", ReportFormat.HTML)
            report_path = options.get("report_path")
            
            if isinstance(report_format, list):
                # Multiple report formats
                for fmt in report_format:
                    path = report_path.get(fmt) if isinstance(report_path, dict) else None
                    self._export_report(report, fmt, path, output_path)
            else:
                # Single report format
                self._export_report(report, report_format, report_path, output_path)
            
            # Complete
            self.progress_reporter.start_stage(ProcessingStage.COMPLETED)
            self._log_info("Processing completed successfully")
            self._log_info(f"Processed {len(organized_images)} of {len(image_paths)} images")
            
            if self.progress_reporter.errors:
                self._log_info(f"Encountered {len(self.progress_reporter.errors)} errors")
            
            return True, report
            
        except Exception as e:
            self._log_error(f"Error during processing: {e}")
            return False, None
    
    def cancel(self) -> None:
        """Cancel processing."""
        self.canceled = True
        self._log_info("Canceling operation...")
    
    def pause(self) -> None:
        """Pause processing."""
        self.paused = True
        self._log_info("Pausing operation...")
    
    def resume(self) -> None:
        """Resume processing."""
        self.paused = False
        self._log_info("Resuming operation...")
    
    def _validate_paths(self, input_paths: List[str], output_path: str) -> None:
        """
        Validate input and output paths.
        
        Args:
            input_paths: List of input file or directory paths
            output_path: Output directory path
            
        Raises:
            ValueError: If any path is invalid
        """
        # Check input paths
        for path in input_paths:
            if not os.path.exists(path):
                raise ValueError(f"Input path does not exist: {path}")
        
        # Check output path
        if os.path.exists(output_path) and not os.path.isdir(output_path):
            raise ValueError(f"Output path exists but is not a directory: {output_path}")
    
    def _scan_input_paths(self, input_paths: List[str], recursive: bool) -> List[str]:
        """
        Scan input paths for image files.
        
        Args:
            input_paths: List of input file or directory paths
            recursive: Whether to scan directories recursively
            
        Returns:
            List of image file paths
        """
        image_paths = []
        total_paths = len(input_paths)
        
        self.progress_reporter.start_progress("scan", total_paths, "Scanning input paths")
        
        for i, path in enumerate(input_paths):
            # Check for cancellation or pause
            if self.canceled:
                break
            
            while self.paused:
                time.sleep(0.1)
            
            path_obj = Path(path)
            
            if path_obj.is_file():
                if self._is_image_file(path_obj):
                    image_paths.append(str(path_obj))
            elif path_obj.is_dir():
                # Scan directory for image files
                dir_images = self._scan_directory(path_obj, recursive)
                image_paths.extend(dir_images)
            
            self.progress_reporter.update_progress("scan", i + 1)
        
        return image_paths
    
    def _scan_directory(self, directory: Path, recursive: bool) -> List[str]:
        """
        Scan a directory for image files.
        
        Args:
            directory: Directory path
            recursive: Whether to scan subdirectories
            
        Returns:
            List of image file paths
        """
        image_paths = []
        
        try:
            for item in directory.iterdir():
                # Check for cancellation or pause
                if self.canceled:
                    break
                
                while self.paused:
                    time.sleep(0.1)
                
                if item.is_file() and self._is_image_file(item):
                    image_paths.append(str(item))
                elif item.is_dir() and recursive:
                    # Recursively scan subdirectory
                    sub_images = self._scan_directory(item, recursive)
                    image_paths.extend(sub_images)
        except PermissionError:
            self._log_error(f"Permission denied: {directory}")
        except Exception as e:
            self._log_error(f"Error scanning directory {directory}: {e}")
        
        return image_paths
    
    def _is_image_file(self, path: Path) -> bool:
        """
        Check if a file is an image.
        
        Args:
            path: File path
            
        Returns:
            True if the file is an image, False otherwise
        """
        image_extensions = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".tif", ".webp"}
        return path.suffix.lower() in image_extensions
    
    def _analyze_images(self, image_paths: List[str]) -> List[Image]:
        """
        Analyze images.
        
        Args:
            image_paths: List of image file paths
            
        Returns:
            List of analyzed Image objects
        """
        total_images = len(image_paths)
        
        self.progress_reporter.start_progress("analyze", total_images, "Analyzing images")
        
        # Check if parallel processing is enabled
        if hasattr(self, "task_scheduler") and self.task_scheduler:
            # Use parallel processing
            return self._analyze_images_parallel(image_paths)
        else:
            # Use sequential processing
            return self._analyze_images_sequential(image_paths)
    
    def _analyze_images_sequential(self, image_paths: List[str]) -> List[Image]:
        """
        Analyze images sequentially.
        
        Args:
            image_paths: List of image file paths
            
        Returns:
            List of analyzed Image objects
        """
        images = []
        total_images = len(image_paths)
        
        for i, path in enumerate(image_paths):
            # Check for cancellation or pause
            if self.canceled:
                break
            
            while self.paused:
                time.sleep(0.1)
            
            try:
                # Create Image object
                image = Image(path)
                
                # Analyze image content
                self._log_info(f"Analyzing image: {path}")
                self.analysis_service.analyze_image(image)
                
                images.append(image)
                
            except Exception as e:
                self._log_error(f"Error analyzing image {path}: {e}", path)
            
            self.progress_reporter.update_progress("analyze", i + 1)
        
        return images
    
    def _analyze_images_parallel(self, image_paths: List[str]) -> List[Image]:
        """
        Analyze images in parallel.
        
        Args:
            image_paths: List of image file paths
            
        Returns:
            List of analyzed Image objects
        """
        def analyze_image(path: str) -> Optional[Image]:
            """Analyze a single image."""
            try:
                # Create Image object
                image = Image(path)
                
                # Analyze image content
                self.analysis_service.analyze_image(image)
                
                return image
                
            except Exception as e:
                self._log_error(f"Error analyzing image {path}: {e}", path)
                return None
        
        # Process images in parallel
        results = self.task_scheduler.process_batch(
            "analyze",
            analyze_image,
            image_paths,
        )
        
        # Filter out None results (failed analyses)
        return [image for image in results if image is not None]
    
    def _categorize_images(
        self,
        images: List[Image],
        similarity_threshold: float,
        max_category_depth: int,
    ) -> CategoryTree:
        """
        Categorize images.
        
        Args:
            images: List of Image objects
            similarity_threshold: Threshold for image similarity (0.0 to 1.0)
            max_category_depth: Maximum depth of category hierarchy
            
        Returns:
            CategoryTree with categorized images
        """
        total_images = len(images)
        
        self.progress_reporter.start_progress("categorize", total_images, "Categorizing images")
        
        # Create category tree
        category_tree = self.categorization_service.categorize_images(
            images,
            similarity_threshold=similarity_threshold,
            max_category_depth=max_category_depth,
            progress_callback=lambda i: self.progress_reporter.update_progress("categorize", i),
            cancel_check=lambda: self.canceled,
            pause_check=lambda: self.paused,
        )
        
        return category_tree
    
    def _organize_images(
        self,
        images: List[Image],
        category_tree: CategoryTree,
        output_path: str,
    ) -> List[Image]:
        """
        Organize images.
        
        Args:
            images: List of Image objects
            category_tree: CategoryTree with categorized images
            output_path: Output directory path
            
        Returns:
            List of organized Image objects
        """
        total_images = len(images)
        
        self.progress_reporter.start_progress("organize", total_images, "Organizing images")
        
        # Check if parallel processing is enabled
        if hasattr(self, "task_scheduler") and self.task_scheduler:
            # Use parallel processing
            return self._organize_images_parallel(images, category_tree, output_path)
        else:
            # Use sequential processing
            return self._organize_images_sequential(images, category_tree, output_path)
    
    def _organize_images_sequential(
        self,
        images: List[Image],
        category_tree: CategoryTree,
        output_path: str,
    ) -> List[Image]:
        """
        Organize images sequentially.
        
        Args:
            images: List of Image objects
            category_tree: CategoryTree with categorized images
            output_path: Output directory path
            
        Returns:
            List of organized Image objects
        """
        organized_images = []
        total_images = len(images)
        
        for i, image in enumerate(images):
            # Check for cancellation or pause
            if self.canceled:
                break
            
            while self.paused:
                time.sleep(0.1)
            
            try:
                # Get categories for image
                categories = category_tree.get_category_for_image(image.id)
                
                if not categories:
                    self._log_warning(f"No categories found for image: {image.path}")
                    continue
                
                # Use the first category (most specific)
                category = categories[0]
                
                # Get category path
                category_path = category_tree.get_category_path_names(category.id)
                
                # Create output directory
                rel_dir_path = os.path.join(*category_path) if category_path else ""
                dir_path = os.path.join(output_path, rel_dir_path)
                os.makedirs(dir_path, exist_ok=True)
                
                # Generate new filename
                new_filename = self._generate_filename(image, category)
                new_path = os.path.join(dir_path, new_filename)
                
                # Copy file
                self._log_info(f"Copying {image.path} to {new_path}")
                self.file_operations.copy_file(str(image.path), new_path)
                
                # Update image with new path
                image.new_path = Path(new_path)
                organized_images.append(image)
                
            except Exception as e:
                self._log_error(f"Error organizing image {image.path}: {e}", str(image.path))
            
            self.progress_reporter.update_progress("organize", i + 1)
        
        return organized_images
    
    def _organize_images_parallel(
        self,
        images: List[Image],
        category_tree: CategoryTree,
        output_path: str,
    ) -> List[Image]:
        """
        Organize images in parallel.
        
        Args:
            images: List of Image objects
            category_tree: CategoryTree with categorized images
            output_path: Output directory path
            
        Returns:
            List of organized Image objects
        """
        # Create a lock for directory creation
        dir_lock = threading.Lock()
        
        def organize_image(image: Image) -> Optional[Image]:
            """Organize a single image."""
            try:
                # Get categories for image
                categories = category_tree.get_category_for_image(image.id)
                
                if not categories:
                    self._log_warning(f"No categories found for image: {image.path}")
                    return None
                
                # Use the first category (most specific)
                category = categories[0]
                
                # Get category path
                category_path = category_tree.get_category_path_names(category.id)
                
                # Create output directory (with lock to avoid race conditions)
                rel_dir_path = os.path.join(*category_path) if category_path else ""
                dir_path = os.path.join(output_path, rel_dir_path)
                
                with dir_lock:
                    os.makedirs(dir_path, exist_ok=True)
                
                # Generate new filename
                new_filename = self._generate_filename(image, category)
                new_path = os.path.join(dir_path, new_filename)
                
                # Copy file
                self.file_operations.copy_file(str(image.path), new_path)
                
                # Update image with new path
                image.new_path = Path(new_path)
                return image
                
            except Exception as e:
                self._log_error(f"Error organizing image {image.path}: {e}", str(image.path))
                return None
        
        # Process images in parallel
        results = self.task_scheduler.process_batch(
            "organize",
            organize_image,
            images,
        )
        
        # Filter out None results (failed organizations)
        return [image for image in results if image is not None]
    
    def _generate_filename(self, image: Image, category: Category) -> str:
        """
        Generate a new filename for an image.
        
        Args:
            image: Image object
            category: Category object
            
        Returns:
            New filename
        """
        # Use category name and image content tags
        base_name = category.name.lower().replace(" ", "_")
        
        if image.content_tags:
            # Add top content tag
            top_tag = image.content_tags[0].lower().replace(" ", "_")
            base_name = f"{base_name}_{top_tag}"
        
        # Add unique identifier
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        
        # Add original extension
        extension = os.path.splitext(image.path)[1]
        
        return f"{base_name}_{unique_id}{extension}"
    
    def _generate_report(
        self,
        images: List[Image],
        output_path: str,
        processing_time: float,
        total_files: int,
        processed_files: int,
        skipped_files: int,
        error_count: int,
        errors: List[Dict[str, str]],
    ) -> Report:
        """
        Generate a report.
        
        Args:
            images: List of organized Image objects
            output_path: Output directory path
            processing_time: Processing time in seconds
            total_files: Total number of files
            processed_files: Number of processed files
            skipped_files: Number of skipped files
            error_count: Number of errors
            errors: List of errors
            
        Returns:
            Report object
        """
        # Create folder structure
        folder_structure = self.file_mapping_service.create_folder_structure(images, output_path)
        
        # Create file mappings
        file_mappings = self.file_mapping_service.create_file_mappings(images)
        
        # Generate report
        report = self.reporting_service.generate_report(
            folder_structure=folder_structure,
            file_mappings=file_mappings,
            processing_time=processing_time,
            total_files=total_files,
            processed_files=processed_files,
            skipped_files=skipped_files,
            error_count=error_count,
            errors=errors,
        )
        
        return report
    
    def _export_report(
        self,
        report: Report,
        format: ReportFormat,
        report_path: Optional[str],
        output_path: str,
    ) -> None:
        """
        Export a report.
        
        Args:
            report: Report object
            format: Report format
            report_path: Custom report path
            output_path: Output directory path
        """
        if report_path:
            path = report_path
        else:
            # Generate default report path
            if format == ReportFormat.TEXT:
                path = os.path.join(output_path, "report.txt")
            else:
                path = os.path.join(output_path, "report.html")
        
        self._log_info(f"Exporting report to {path}")
        self.report_export_service.export_report(report, format, path)
    
    def _log_info(self, message: str) -> None:
        """
        Log an informational message.
        
        Args:
            message: Message to log
        """
        self.progress_reporter.log_info(message)
    
    def _log_warning(self, message: str) -> None:
        """
        Log a warning message.
        
        Args:
            message: Message to log
        """
        self.progress_reporter.log_warning(message)
    
    def _log_error(self, message: str, file: Optional[str] = None) -> None:
        """
        Log an error message.
        
        Args:
            message: Message to log
            file: File that caused the error
        """
        self.progress_reporter.log_error(message, file)