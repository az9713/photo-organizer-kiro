"""
Performance benchmarks for the Photo Organizer application.
"""

import os
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import pytest

from photo_organizer.core import ApplicationCore
from photo_organizer.ui.cli_progress import CLIProgressReporter
from tests.integration.test_dataset import test_dataset


# Skip these tests by default as they are resource-intensive
# Run with pytest -m performance_benchmarks to include them
pytestmark = pytest.mark.performance_benchmarks


class TestPerformanceBenchmarks:
    """Performance benchmarks for the Photo Organizer application."""
    
    @pytest.fixture
    def large_dataset(self, test_dataset: Tuple[Path, Dict[str, List[Path]]]) -> Tuple[Path, List[Path]]:
        """Create a large dataset by duplicating the test dataset."""
        base_dir, dataset = test_dataset
        large_dir = base_dir / "large"
        large_dir.mkdir()
        
        # Get all image paths
        all_images = []
        for category, images in dataset.items():
            all_images.extend(images)
        
        # Duplicate images to create a larger dataset
        large_images = []
        for i in range(10):  # Create 10 copies
            for image in all_images:
                new_path = large_dir / f"{i}_{image.name}"
                shutil.copy(image, new_path)
                large_images.append(new_path)
        
        return large_dir, large_images
    
    def test_worker_count_scaling(self, large_dataset: Tuple[Path, List[Path]]) -> None:
        """Test scaling with different numbers of worker threads."""
        large_dir, large_images = large_dataset
        
        # Test with different numbers of workers
        worker_counts = [1, 2, 4, 8]
        times = []
        
        for workers in worker_counts:
            output_dir = large_dir / f"output_{workers}"
            output_dir.mkdir()
            
            # Measure processing time
            time_taken = self._measure_processing_time(
                large_images,
                output_dir,
                workers=workers,
            )
            
            times.append(time_taken)
            
            print(f"\nWorkers: {workers}, Time: {time_taken:.2f}s")
        
        # Print scaling results
        print("\nScaling results:")
        for i, workers in enumerate(worker_counts):
            speedup = times[0] / times[i]
            efficiency = speedup / workers
            print(f"Workers: {workers}, Time: {times[i]:.2f}s, Speedup: {speedup:.2f}x, Efficiency: {efficiency:.2f}")
    
    def test_batch_size_impact(self, large_dataset: Tuple[Path, List[Path]]) -> None:
        """Test the impact of batch size on performance."""
        large_dir, large_images = large_dataset
        
        # Test with different batch sizes
        batch_sizes = [10, 50, 100, 500]
        times = []
        
        for batch_size in batch_sizes:
            output_dir = large_dir / f"output_batch_{batch_size}"
            output_dir.mkdir()
            
            # Measure processing time
            time_taken = self._measure_processing_time(
                large_images,
                output_dir,
                batch_size=batch_size,
            )
            
            times.append(time_taken)
            
            print(f"\nBatch size: {batch_size}, Time: {time_taken:.2f}s")
        
        # Print batch size results
        print("\nBatch size results:")
        for i, batch_size in enumerate(batch_sizes):
            print(f"Batch size: {batch_size}, Time: {times[i]:.2f}s")
    
    def test_memory_profile(self, large_dataset: Tuple[Path, List[Path]]) -> None:
        """Test memory usage profile during processing."""
        large_dir, large_images = large_dataset
        output_dir = large_dir / "output_memory"
        output_dir.mkdir()
        
        # Create a memory profiler
        import tracemalloc
        
        # Start tracking memory allocations
        tracemalloc.start()
        
        # Process images
        reporter = CLIProgressReporter(verbose=0, quiet=True)
        app_core = ApplicationCore(reporter, parallel_processing=True, max_workers=4)
        
        app_core.process_images(
            [str(path) for path in large_images],
            str(output_dir),
            {
                "recursive": False,
                "parallel_processing": True,
                "max_workers": 4,
                "similarity_threshold": 0.7,
                "max_category_depth": 3,
            },
        )
        
        # Get memory snapshot
        snapshot = tracemalloc.take_snapshot()
        
        # Stop tracking
        tracemalloc.stop()
        
        # Print top memory consumers
        print("\nTop 10 memory consumers:")
        top_stats = snapshot.statistics("lineno")
        for stat in top_stats[:10]:
            print(f"{stat.count} allocations: {stat.size / 1024 / 1024:.1f} MB")
            for line in stat.traceback.format():
                print(f"    {line}")
    
    def test_bottleneck_identification(self, large_dataset: Tuple[Path, List[Path]]) -> None:
        """Test to identify performance bottlenecks."""
        large_dir, large_images = large_dataset
        output_dir = large_dir / "output_bottleneck"
        output_dir.mkdir()
        
        # Create a profiler
        import cProfile
        import pstats
        import io
        
        # Profile the processing
        profiler = cProfile.Profile()
        profiler.enable()
        
        # Process images
        reporter = CLIProgressReporter(verbose=0, quiet=True)
        app_core = ApplicationCore(reporter, parallel_processing=True, max_workers=4)
        
        app_core.process_images(
            [str(path) for path in large_images[:100]],  # Use a subset for profiling
            str(output_dir),
            {
                "recursive": False,
                "parallel_processing": True,
                "max_workers": 4,
                "similarity_threshold": 0.7,
                "max_category_depth": 3,
            },
        )
        
        profiler.disable()
        
        # Print profiling results
        s = io.StringIO()
        ps = pstats.Stats(profiler, stream=s).sort_stats("cumulative")
        ps.print_stats(20)  # Print top 20 functions by cumulative time
        
        print("\nProfiling results:")
        print(s.getvalue())
    
    def _measure_processing_time(
        self,
        images: List[Path],
        output_dir: Path,
        workers: int = 4,
        batch_size: int = 100,
    ) -> float:
        """
        Measure the time it takes to process a list of images.
        
        Args:
            images: List of image paths
            output_dir: Output directory
            workers: Number of worker threads
            batch_size: Batch size for processing
            
        Returns:
            Processing time in seconds
        """
        output_dir.mkdir(exist_ok=True)
        
        # Create a progress reporter
        reporter = CLIProgressReporter(verbose=0, quiet=True)
        
        # Create an application core
        app_core = ApplicationCore(
            reporter,
            parallel_processing=True,
            max_workers=workers,
        )
        
        # Measure processing time
        start_time = time.time()
        
        # Process images in batches
        for i in range(0, len(images), batch_size):
            batch = images[i:i+batch_size]
            
            app_core.process_images(
                [str(path) for path in batch],
                str(output_dir),
                {
                    "recursive": False,
                    "parallel_processing": True,
                    "max_workers": workers,
                    "similarity_threshold": 0.7,
                    "max_category_depth": 3,
                },
            )
        
        end_time = time.time()
        
        return end_time - start_time