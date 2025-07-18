"""
Unit tests for the parallel processing utilities.
"""

import concurrent.futures
import threading
import time
from unittest.mock import MagicMock, patch

import pytest

from photo_organizer.parallel import TaskScheduler, WorkerPool


def square(x):
    """Square a number."""
    return x * x


def slow_square(x):
    """Square a number with a delay."""
    time.sleep(0.01)
    return x * x


def failing_function(x):
    """Function that raises an exception."""
    raise ValueError(f"Error processing {x}")


class TestWorkerPool:
    """Tests for the WorkerPool class."""

    def test_init(self) -> None:
        """Test initializing a WorkerPool object."""
        pool = WorkerPool(max_workers=2, name="TestPool")
        
        assert pool.max_workers == 2
        assert pool.name == "TestPool"
        assert pool.progress_callback is None
        assert pool.executor is None
        assert pool.futures == []
        assert pool.results == []
        assert pool.errors == []
        assert not pool.canceled
        assert not pool.paused

    def test_map(self) -> None:
        """Test mapping a function over items."""
        pool = WorkerPool(max_workers=2)
        
        results = pool.map(square, [1, 2, 3, 4, 5])
        
        assert sorted(results) == [1, 4, 9, 16, 25]
        assert len(pool.futures) == 5
        assert len(pool.results) == 5
        assert pool.errors == []

    def test_map_with_progress(self) -> None:
        """Test mapping with progress callback."""
        progress_callback = MagicMock()
        pool = WorkerPool(max_workers=2, progress_callback=progress_callback)
        
        pool.map(slow_square, [1, 2, 3, 4, 5])
        
        assert progress_callback.call_count == 5
        progress_callback.assert_any_call(1, 5)
        progress_callback.assert_any_call(2, 5)
        progress_callback.assert_any_call(3, 5)
        progress_callback.assert_any_call(4, 5)
        progress_callback.assert_any_call(5, 5)

    def test_map_with_errors(self) -> None:
        """Test mapping with errors."""
        pool = WorkerPool(max_workers=2)
        
        results = pool.map(failing_function, [1, 2, 3])
        
        assert results == []
        assert len(pool.errors) == 3
        assert all(isinstance(error[1], ValueError) for error in pool.errors)

    def test_cancel(self) -> None:
        """Test canceling tasks."""
        pool = WorkerPool(max_workers=2)
        
        # Start a thread to cancel after a short delay
        def cancel_thread():
            time.sleep(0.02)
            pool.cancel()
        
        thread = threading.Thread(target=cancel_thread)
        thread.start()
        
        # Map a slow function
        results = pool.map(slow_square, [1, 2, 3, 4, 5])
        
        # Wait for the cancel thread to finish
        thread.join()
        
        # Check that not all items were processed
        assert len(results) < 5
        assert pool.canceled

    def test_pause_resume(self) -> None:
        """Test pausing and resuming tasks."""
        pool = WorkerPool(max_workers=1)
        
        # Start a thread to pause and resume after short delays
        def pause_resume_thread():
            time.sleep(0.01)
            pool.pause()
            time.sleep(0.02)
            pool.resume()
        
        thread = threading.Thread(target=pause_resume_thread)
        thread.start()
        
        # Map a slow function
        start_time = time.time()
        results = pool.map(slow_square, [1, 2, 3])
        elapsed_time = time.time() - start_time
        
        # Wait for the pause/resume thread to finish
        thread.join()
        
        # Check that all items were processed
        assert sorted(results) == [1, 4, 9]
        
        # Check that the processing took longer due to the pause
        assert elapsed_time > 0.03


class TestTaskScheduler:
    """Tests for the TaskScheduler class."""

    def test_init(self) -> None:
        """Test initializing a TaskScheduler object."""
        scheduler = TaskScheduler(max_workers=2)
        
        assert scheduler.max_workers == 2
        assert scheduler.progress_callback is None
        assert scheduler.cancel_check is None
        assert scheduler.pause_check is None
        assert scheduler.worker_pools == {}

    def test_process_batch(self) -> None:
        """Test processing a batch of items."""
        scheduler = TaskScheduler(max_workers=2)
        
        results = scheduler.process_batch("test", square, [1, 2, 3, 4, 5])
        
        assert sorted(results) == [1, 4, 9, 16, 25]
        assert "test" in scheduler.worker_pools
        assert len(scheduler.worker_pools["test"].results) == 5

    def test_process_batch_with_progress(self) -> None:
        """Test processing a batch with progress callback."""
        progress_callback = MagicMock()
        scheduler = TaskScheduler(max_workers=2, progress_callback=progress_callback)
        
        scheduler.process_batch("test", slow_square, [1, 2, 3, 4, 5])
        
        assert progress_callback.call_count == 5
        progress_callback.assert_any_call("test", 1, 5)
        progress_callback.assert_any_call("test", 2, 5)
        progress_callback.assert_any_call("test", 3, 5)
        progress_callback.assert_any_call("test", 4, 5)
        progress_callback.assert_any_call("test", 5, 5)

    def test_process_batch_with_cancel_check(self) -> None:
        """Test processing a batch with cancel check."""
        # Create a cancel check that returns True after 2 items
        cancel_check = MagicMock()
        cancel_check.side_effect = [False, False, True]
        
        scheduler = TaskScheduler(max_workers=1, cancel_check=cancel_check)
        
        results = scheduler.process_batch("test", slow_square, [1, 2, 3, 4, 5])
        
        # Check that not all items were processed
        assert len(results) < 5
        assert scheduler.worker_pools["test"].canceled

    def test_process_batch_with_pause_check(self) -> None:
        """Test processing a batch with pause check."""
        # Create a pause check that returns True for a short time
        pause_check = MagicMock()
        pause_check.side_effect = [False, True, True, False, False]
        
        scheduler = TaskScheduler(max_workers=1, pause_check=pause_check)
        
        # Process a batch
        start_time = time.time()
        results = scheduler.process_batch("test", slow_square, [1, 2, 3])
        elapsed_time = time.time() - start_time
        
        # Check that all items were processed
        assert sorted(results) == [1, 4, 9]
        
        # Check that the pause check was called
        assert pause_check.call_count >= 3

    def test_cancel_all(self) -> None:
        """Test canceling all worker pools."""
        scheduler = TaskScheduler(max_workers=2)
        
        # Create two worker pools
        pool1 = MagicMock()
        pool2 = MagicMock()
        scheduler.worker_pools = {"pool1": pool1, "pool2": pool2}
        
        # Cancel all
        scheduler.cancel_all()
        
        # Check that both pools were canceled
        pool1.cancel.assert_called_once()
        pool2.cancel.assert_called_once()

    def test_pause_all(self) -> None:
        """Test pausing all worker pools."""
        scheduler = TaskScheduler(max_workers=2)
        
        # Create two worker pools
        pool1 = MagicMock()
        pool2 = MagicMock()
        scheduler.worker_pools = {"pool1": pool1, "pool2": pool2}
        
        # Pause all
        scheduler.pause_all()
        
        # Check that both pools were paused
        pool1.pause.assert_called_once()
        pool2.pause.assert_called_once()

    def test_resume_all(self) -> None:
        """Test resuming all worker pools."""
        scheduler = TaskScheduler(max_workers=2)
        
        # Create two worker pools
        pool1 = MagicMock()
        pool2 = MagicMock()
        scheduler.worker_pools = {"pool1": pool1, "pool2": pool2}
        
        # Resume all
        scheduler.resume_all()
        
        # Check that both pools were resumed
        pool1.resume.assert_called_once()
        pool2.resume.assert_called_once()