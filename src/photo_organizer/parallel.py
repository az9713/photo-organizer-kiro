"""
Parallel processing utilities for the Photo Organizer application.
"""

import concurrent.futures
import threading
import time
from typing import Any, Callable, Dict, List, Optional, TypeVar, Union

T = TypeVar("T")
U = TypeVar("U")


class WorkerPool:
    """Pool of worker threads for parallel processing."""
    
    def __init__(
        self,
        max_workers: int = 4,
        name: str = "WorkerPool",
        progress_callback: Optional[Callable[[int, int], None]] = None,
    ) -> None:
        """
        Initialize a worker pool.
        
        Args:
            max_workers: Maximum number of worker threads
            name: Name of the worker pool
            progress_callback: Callback for progress updates
        """
        self.max_workers = max_workers
        self.name = name
        self.progress_callback = progress_callback
        
        self.executor = None
        self.futures = []
        self.results = []
        self.errors = []
        
        self.canceled = False
        self.paused = False
        self.pause_condition = threading.Condition()
    
    def map(
        self,
        func: Callable[[T], U],
        items: List[T],
        timeout: Optional[float] = None,
    ) -> List[U]:
        """
        Apply a function to each item in parallel.
        
        Args:
            func: Function to apply
            items: Items to process
            timeout: Timeout in seconds
            
        Returns:
            List of results
        """
        self.canceled = False
        self.paused = False
        self.futures = []
        self.results = []
        self.errors = []
        
        total_items = len(items)
        processed_items = 0
        
        # Create wrapped function that handles pausing
        def wrapped_func(item: T) -> Optional[U]:
            # Check for cancellation
            if self.canceled:
                return None
            
            # Check for pause
            with self.pause_condition:
                while self.paused and not self.canceled:
                    self.pause_condition.wait()
            
            # Process item
            try:
                return func(item)
            except Exception as e:
                self.errors.append((item, e))
                return None
        
        # Create thread pool
        with concurrent.futures.ThreadPoolExecutor(
            max_workers=self.max_workers,
            thread_name_prefix=self.name,
        ) as executor:
            self.executor = executor
            
            # Submit all tasks
            for item in items:
                if self.canceled:
                    break
                
                future = executor.submit(wrapped_func, item)
                self.futures.append(future)
            
            # Wait for tasks to complete
            for i, future in enumerate(concurrent.futures.as_completed(self.futures)):
                if self.canceled:
                    break
                
                result = future.result()
                if result is not None:
                    self.results.append(result)
                
                processed_items += 1
                
                # Update progress
                if self.progress_callback:
                    self.progress_callback(processed_items, total_items)
        
        return self.results
    
    def cancel(self) -> None:
        """Cancel all tasks."""
        self.canceled = True
        
        # Wake up paused threads
        with self.pause_condition:
            self.paused = False
            self.pause_condition.notify_all()
        
        # Cancel futures
        if self.executor:
            self.executor.shutdown(wait=False)
            
            for future in self.futures:
                future.cancel()
    
    def pause(self) -> None:
        """Pause all tasks."""
        with self.pause_condition:
            self.paused = True
    
    def resume(self) -> None:
        """Resume all tasks."""
        with self.pause_condition:
            self.paused = False
            self.pause_condition.notify_all()


class TaskScheduler:
    """Scheduler for processing tasks."""
    
    def __init__(
        self,
        max_workers: int = 4,
        progress_callback: Optional[Callable[[str, int, int], None]] = None,
        cancel_check: Optional[Callable[[], bool]] = None,
        pause_check: Optional[Callable[[], bool]] = None,
    ) -> None:
        """
        Initialize a task scheduler.
        
        Args:
            max_workers: Maximum number of worker threads
            progress_callback: Callback for progress updates
            cancel_check: Function to check if processing should be canceled
            pause_check: Function to check if processing should be paused
        """
        self.max_workers = max_workers
        self.progress_callback = progress_callback
        self.cancel_check = cancel_check
        self.pause_check = pause_check
        
        self.worker_pools: Dict[str, WorkerPool] = {}
    
    def process_batch(
        self,
        name: str,
        func: Callable[[T], U],
        items: List[T],
        timeout: Optional[float] = None,
    ) -> List[U]:
        """
        Process a batch of items in parallel.
        
        Args:
            name: Name of the batch
            func: Function to apply to each item
            items: Items to process
            timeout: Timeout in seconds
            
        Returns:
            List of results
        """
        # Create progress callback
        def progress_callback(processed: int, total: int) -> None:
            if self.progress_callback:
                self.progress_callback(name, processed, total)
        
        # Create or get worker pool
        if name not in self.worker_pools:
            self.worker_pools[name] = WorkerPool(
                max_workers=self.max_workers,
                name=name,
                progress_callback=progress_callback,
            )
        
        worker_pool = self.worker_pools[name]
        
        # Start a thread to check for cancellation and pausing
        if self.cancel_check or self.pause_check:
            def monitor_thread() -> None:
                while not worker_pool.canceled:
                    # Check for cancellation
                    if self.cancel_check and self.cancel_check():
                        worker_pool.cancel()
                        break
                    
                    # Check for pausing
                    if self.pause_check:
                        paused = self.pause_check()
                        if paused and not worker_pool.paused:
                            worker_pool.pause()
                        elif not paused and worker_pool.paused:
                            worker_pool.resume()
                    
                    time.sleep(0.1)
            
            monitor = threading.Thread(target=monitor_thread, daemon=True)
            monitor.start()
        
        # Process items
        return worker_pool.map(func, items, timeout)
    
    def cancel_all(self) -> None:
        """Cancel all worker pools."""
        for worker_pool in self.worker_pools.values():
            worker_pool.cancel()
    
    def pause_all(self) -> None:
        """Pause all worker pools."""
        for worker_pool in self.worker_pools.values():
            worker_pool.pause()
    
    def resume_all(self) -> None:
        """Resume all worker pools."""
        for worker_pool in self.worker_pools.values():
            worker_pool.resume()