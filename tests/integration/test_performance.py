"""
Performance tests for the Photo Organizer application.
"""

import time
from pathlib import Path
from typing import Dict, List, Tuple

import pytest

from photo_organizer.core import ApplicationCore
from photo_organizer.ui.cli_progress import CLIProgressReporter
from tests.integration.test_dataset import test_dataset


class TestPerformance:
    """Performance tests for the Photo Organizer application."""
    
    def test_sequential_vs_parallel(self, test_dataset: Tuple[Path, Dict[str, List[Path]]]) -> None:
        """Test sequential vs parallel processing performance."""
        base_dir, dataset = test_dataset
        output_dir = base_dir / "output"
        output_dir.mkdir()
        
        # Get all image paths
        all_images = []
        for category, images in dataset.items():
            all_images.extend(images)
        
        # Process sequentially
        sequential_time = self._measure_processing_time(
            all_images,
            output_dir / "sequential",
            parallel=False,
        )
        
        # Process in parallel
        parallel_time = self._measure_processing_time(
            all_images,
            output_dir / "parallel",
            parallel=True,
        )
        
        # Check that parallel processing is faster (or at least not much slower)
        # This is a very simple check and might not always be true for small datasets
        assert parallel_time <= sequential_time * 1.5, \
            f"Parallel processing ({parallel_time:.2f}s) should not be much slower than sequential processing ({sequential_time:.2f}s)"
        
        # Print performance comparison
        print(f"\nPerformance comparison:")
        print(f"Sequential: {sequential_time:.2f}s")
        print(f"Parallel: {parallel_time:.2f}s")
        print(f"Speedup: {sequential_time / parallel_time:.2f}x")
    
    def test_memory_usage(self, test_dataset: Tuple[Path, Dict[str, List[Path]]]) -> None:
        """Test memory usage during processing."""
        base_dir, dataset = test_dataset
        output_dir = base_dir / "output"
        output_dir.mkdir()
        
        # Get all image paths
        all_images = []
        for category, images in dataset.items():
            all_images.extend(images)
        
        # Measure memory usage
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        
        # Get initial memory usage
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Process images
        reporter = CLIProgressReporter(verbose=0, quiet=True)
        app_core = ApplicationCore(reporter)
        
        app_core.process_images(
            [str(path) for path in all_images],
            str(output_dir),
            {
                "recursive": False,
                "parallel_processing": True,
                "max_workers": 4,
                "similarity_threshold": 0.7,
                "max_category_depth": 3,
            },
        )
        
        # Get final memory usage
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Print memory usage
        print(f"\nMemory usage:")
        print(f"Initial: {initial_memory:.2f} MB")
        print(f"Final: {final_memory:.2f} MB")
        print(f"Difference: {final_memory - initial_memory:.2f} MB")
    
    def _measure_processing_time(
        self,
        images: List[Path],
        output_dir: Path,
        parallel: bool = False,
    ) -> float:
        """
        Measure the time it takes to process a list of images.
        
        Args:
            images: List of image paths
            output_dir: Output directory
            parallel: Whether to use parallel processing
            
        Returns:
            Processing time in seconds
        """
        output_dir.mkdir(exist_ok=True)
        
        # Create a progress reporter
        reporter = CLIProgressReporter(verbose=0, quiet=True)
        
        # Create an application core
        app_core = ApplicationCore(
            reporter,
            parallel_processing=parallel,
            max_workers=4,
        )
        
        # Measure processing time
        start_time = time.time()
        
        app_core.process_images(
            [str(path) for path in images],
            str(output_dir),
            {
                "recursive": False,
                "parallel_processing": parallel,
                "max_workers": 4,
                "similarity_threshold": 0.7,
                "max_category_depth": 3,
            },
        )
        
        end_time = time.time()
        
        return end_time - start_time