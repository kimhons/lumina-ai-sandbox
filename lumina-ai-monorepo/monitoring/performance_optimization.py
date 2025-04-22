"""
Performance Optimization System for Lumina AI

This module provides tools and utilities for analyzing and optimizing the performance
of Lumina AI components, including automated performance testing, bottleneck detection,
resource optimization, caching, and query optimization.
"""

import logging
import time
import os
import json
import threading
import statistics
from typing import Dict, List, Any, Optional, Union, Callable
from datetime import datetime
import hashlib
import random
import concurrent.futures

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PerformanceProfiler:
    """
    Profiles the performance of code blocks and functions.
    """
    
    def __init__(self, service_name: str):
        """
        Initialize the performance profiler.
        
        Args:
            service_name: Name of the service being profiled
        """
        self.service_name = service_name
        self.profiles = {}
        self._lock = threading.Lock()
        logger.info(f"Initialized PerformanceProfiler for service {service_name}")
    
    def profile(self, name: str):
        """
        Context manager for profiling a code block.
        
        Args:
            name: Name of the profile
            
        Returns:
            Context manager for profiling
        """
        class ProfilerContext:
            def __init__(self, profiler, name):
                self.profiler = profiler
                self.name = name
                self.start_time = None
                self.cpu_start = None
                self.memory_start = None
            
            def __enter__(self):
                self.start_time = time.time()
                try:
                    import psutil
                    process = psutil.Process(os.getpid())
                    self.cpu_start = process.cpu_percent()
                    self.memory_start = process.memory_info().rss
                except ImportError:
                    logger.warning("psutil not available, CPU and memory profiling disabled")
                return self
            
            def __exit__(self, exc_type, exc_val, exc_tb):
                duration = time.time() - self.start_time
                
                profile_data = {
                    "duration": duration,
                    "timestamp": datetime.utcnow().isoformat(),
                    "error": exc_type is not None
                }
                
                try:
                    import psutil
                    process = psutil.Process(os.getpid())
                    profile_data["cpu_percent"] = process.cpu_percent()
                    profile_data["memory_current"] = process.memory_info().rss
                    if self.memory_start:
                        profile_data["memory_delta"] = profile_data["memory_current"] - self.memory_start
                except ImportError:
                    pass
                
                with self.profiler._lock:
                    if self.name not in self.profiler.profiles:
                        self.profiler.profiles[self.name] = []
                    self.profiler.profiles[self.name].append(profile_data)
                
                logger.debug(f"Profile {self.name}: {duration:.6f}s")
                
                # Don't suppress exceptions
                return False
        
        return ProfilerContext(self, name)
    
    def profile_function(self, func):
        """
        Decorator for profiling a function.
        
        Args:
            func: Function to profile
            
        Returns:
            Wrapped function with profiling
        """
        def wrapper(*args, **kwargs):
            with self.profile(func.__name__):
                return func(*args, **kwargs)
        return wrapper
    
    def get_profile_data(self, name: Optional[str] = None) -> Dict[str, Any]:
        """
        Get profile data for a specific profile or all profiles.
        
        Args:
            name: Optional name of the profile to get data for
            
        Returns:
            Dictionary containing profile data
        """
        with self._lock:
            if name:
                if name not in self.profiles:
                    return {"name": name, "samples": []}
                
                samples = self.profiles[name]
                
                # Calculate statistics
                durations = [sample["duration"] for sample in samples]
                stats = {
                    "name": name,
                    "samples": samples,
                    "count": len(samples),
                    "min_duration": min(durations),
                    "max_duration": max(durations),
                    "avg_duration": sum(durations) / len(durations),
                    "median_duration": statistics.median(durations),
                    "p90_duration": sorted(durations)[int(len(durations) * 0.9)],
                    "p95_duration": sorted(durations)[int(len(durations) * 0.95)],
                    "p99_duration": sorted(durations)[int(len(durations) * 0.99)]
                }
                
                # Add memory stats if available
                if "memory_delta" in samples[0]:
                    memory_deltas = [sample["memory_delta"] for sample in samples]
                    stats["avg_memory_delta"] = sum(memory_deltas) / len(memory_deltas)
                
                return stats
            else:
                # Get stats for all profiles
                result = {}
                for profile_name in self.profiles:
                    result[profile_name] = self.get_profile_data(profile_name)
                return result
    
    def reset_profiles(self) -> None:
        """Reset all profile data."""
        with self._lock:
            self.profiles = {}
        logger.info(f"Profiles reset for service {self.service_name}")


class CachingService:
    """
    Provides caching capabilities for improving performance.
    """
    
    def __init__(self, cache_name: str, max_size: int = 1000, ttl_seconds: int = 3600):
        """
        Initialize the caching service.
        
        Args:
            cache_name: Name of the cache
            max_size: Maximum number of items in the cache
            ttl_seconds: Default time-to-live for cache items in seconds
        """
        self.cache_name = cache_name
        self.max_size = max_size
        self.default_ttl = ttl_seconds
        self.cache = {}
        self.expiry = {}
        self.access_count = {}
        self._lock = threading.Lock()
        logger.info(f"Initialized CachingService {cache_name} with max size {max_size}, TTL {ttl_seconds}s")
    
    def _generate_key(self, key_data: Any) -> str:
        """
        Generate a cache key from the data.
        
        Args:
            key_data: Data to generate key from
            
        Returns:
            Cache key string
        """
        if isinstance(key_data, str):
            serialized = key_data
        else:
            try:
                serialized = json.dumps(key_data, sort_keys=True)
            except (TypeError, ValueError):
                serialized = str(key_data)
        
        return f"{self.cache_name}:{hashlib.md5(serialized.encode()).hexdigest()}"
    
    def get(self, key_data: Any) -> Optional[Any]:
        """
        Get an item from the cache.
        
        Args:
            key_data: Key data to look up
            
        Returns:
            Cached value or None if not found or expired
        """
        key = self._generate_key(key_data)
        
        with self._lock:
            # Check if key exists and is not expired
            if key in self.cache:
                if key in self.expiry and self.expiry[key] < time.time():
                    # Expired
                    del self.cache[key]
                    del self.expiry[key]
                    if key in self.access_count:
                        del self.access_count[key]
                    logger.debug(f"Cache {self.cache_name}: Key {key} expired")
                    return None
                
                # Update access count
                self.access_count[key] = self.access_count.get(key, 0) + 1
                logger.debug(f"Cache {self.cache_name}: Hit for key {key}")
                return self.cache[key]
            
            logger.debug(f"Cache {self.cache_name}: Miss for key {key}")
            return None
    
    def set(self, key_data: Any, value: Any, ttl_seconds: Optional[int] = None) -> None:
        """
        Set an item in the cache.
        
        Args:
            key_data: Key data to store under
            value: Value to store
            ttl_seconds: Optional custom TTL in seconds
        """
        key = self._generate_key(key_data)
        
        with self._lock:
            # Check if we need to evict items
            if len(self.cache) >= self.max_size and key not in self.cache:
                self._evict_item()
            
            # Store the item
            self.cache[key] = value
            
            # Set expiry
            ttl = ttl_seconds if ttl_seconds is not None else self.default_ttl
            if ttl > 0:
                self.expiry[key] = time.time() + ttl
            
            # Initialize access count
            self.access_count[key] = 0
        
        logger.debug(f"Cache {self.cache_name}: Set key {key} with TTL {ttl}s")
    
    def _evict_item(self) -> None:
        """Evict an item from the cache based on access count."""
        # Find the least recently accessed item
        min_access = float('inf')
        min_key = None
        
        for key in self.cache:
            access = self.access_count.get(key, 0)
            if access < min_access:
                min_access = access
                min_key = key
        
        if min_key:
            del self.cache[min_key]
            if min_key in self.expiry:
                del self.expiry[min_key]
            if min_key in self.access_count:
                del self.access_count[min_key]
            
            logger.debug(f"Cache {self.cache_name}: Evicted key {min_key}")
    
    def invalidate(self, key_data: Optional[Any] = None) -> None:
        """
        Invalidate a specific item or the entire cache.
        
        Args:
            key_data: Optional key data to invalidate, or None to invalidate all
        """
        with self._lock:
            if key_data is None:
                # Invalidate all
                self.cache = {}
                self.expiry = {}
                self.access_count = {}
                logger.info(f"Cache {self.cache_name}: Invalidated all items")
            else:
                # Invalidate specific key
                key = self._generate_key(key_data)
                if key in self.cache:
                    del self.cache[key]
                    if key in self.expiry:
                        del self.expiry[key]
                    if key in self.access_count:
                        del self.access_count[key]
                    logger.debug(f"Cache {self.cache_name}: Invalidated key {key}")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary containing cache statistics
        """
        with self._lock:
            # Count expired items
            now = time.time()
            expired = sum(1 for exp in self.expiry.values() if exp < now)
            
            return {
                "name": self.cache_name,
                "size": len(self.cache),
                "max_size": self.max_size,
                "expired": expired,
                "active": len(self.cache) - expired,
                "ttl": self.default_ttl
            }


class ResourceMonitor:
    """
    Monitors system resource usage for performance optimization.
    """
    
    def __init__(self, service_name: str, sampling_interval: float = 5.0):
        """
        Initialize the resource monitor.
        
        Args:
            service_name: Name of the service being monitored
            sampling_interval: Interval between resource samples in seconds
        """
        self.service_name = service_name
        self.sampling_interval = sampling_interval
        self.samples = []
        self.running = False
        self.sample_thread = None
        self._lock = threading.Lock()
        
        # Check if psutil is available
        try:
            import psutil
            self.psutil_available = True
        except ImportError:
            self.psutil_available = False
            logger.warning("psutil not available, resource monitoring will be limited")
        
        logger.info(f"Initialized ResourceMonitor for service {service_name}")
    
    def start_monitoring(self) -> None:
        """Start resource monitoring in a background thread."""
        if self.running:
            logger.warning("Resource monitoring already running")
            return
        
        self.running = True
        self.sample_thread = threading.Thread(target=self._sampling_loop)
        self.sample_thread.daemon = True
        self.sample_thread.start()
        
        logger.info(f"Started resource monitoring for service {self.service_name}")
    
    def stop_monitoring(self) -> None:
        """Stop resource monitoring."""
        self.running = False
        if self.sample_thread:
            self.sample_thread.join(timeout=2.0)
            self.sample_thread = None
        
        logger.info(f"Stopped resource monitoring for service {self.service_name}")
    
    def _sampling_loop(self) -> None:
        """Background thread for sampling resource usage."""
        while self.running:
            try:
                sample = self._collect_sample()
                
                with self._lock:
                    self.samples.append(sample)
                    
                    # Limit the number of samples to prevent memory issues
                    if len(self.samples) > 1000:
                        self.samples = self.samples[-1000:]
            except Exception as e:
                logger.error(f"Error collecting resource sample: {str(e)}")
            
            time.sleep(self.sampling_interval)
    
    def _collect_sample(self) -> Dict[str, Any]:
        """
        Collect a resource usage sample.
        
        Returns:
            Dictionary containing resource usage data
        """
        sample = {
            "timestamp": datetime.utcnow().isoformat(),
            "service": self.service_name
        }
        
        if self.psutil_available:
            import psutil
            
            # Process-specific metrics
            process = psutil.Process(os.getpid())
            sample["process"] = {
                "cpu_percent": process.cpu_percent(),
                "memory_rss": process.memory_info().rss,
                "memory_vms": process.memory_info().vms,
                "threads": process.num_threads(),
                "open_files": len(process.open_files()),
                "connections": len(process.connections())
            }
            
            # System-wide metrics
            sample["system"] = {
                "cpu_percent": psutil.cpu_percent(),
                "memory_percent": psutil.virtual_memory().percent,
                "swap_percent": psutil.swap_memory().percent,
                "disk_usage": {path: psutil.disk_usage(path).percent for path in ["/", "/home"]}
            }
            
            # Network metrics
            net_io = psutil.net_io_counters()
            sample["network"] = {
                "bytes_sent": net_io.bytes_sent,
                "bytes_recv": net_io.bytes_recv,
                "packets_sent": net_io.packets_sent,
                "packets_recv": net_io.packets_recv
            }
        else:
            # Fallback to basic metrics
            sample["process"] = {
                "threads": threading.active_count()
            }
        
        return sample
    
    def get_resource_usage(self, window_seconds: Optional[float] = None) -> Dict[str, Any]:
        """
        Get resource usage statistics.
        
        Args:
            window_seconds: Optional time window to limit samples
            
        Returns:
            Dictionary containing resource usage statistics
        """
        with self._lock:
            if not self.samples:
                return {"service": self.service_name, "samples": 0}
            
            # Filter samples by time window if specified
            if window_seconds:
                cutoff_time = datetime.utcnow().timestamp() - window_seconds
                filtered_samples = [
                    s for s in self.samples 
                    if datetime.fromisoformat(s["timestamp"]).timestamp() >= cutoff_time
                ]
            else:
                filtered_samples = self.samples
            
            if not filtered_samples:
                return {"service": self.service_name, "samples": 0}
            
            # Calculate statistics
            stats = {
                "service": self.service_name,
                "samples": len(filtered_samples),
                "start_time": filtered_samples[0]["timestamp"],
                "end_time": filtered_samples[-1]["timestamp"]
            }
            
            if self.psutil_available and "process" in filtered_samples[0]:
                # Process CPU stats
                cpu_values = [s["process"]["cpu_percent"] for s in filtered_samples]
                stats["process_cpu"] = {
                    "min": min(cpu_values),
                    "max": max(cpu_values),
                    "avg": sum(cpu_values) / len(cpu_values)
                }
                
                # Process memory stats
                memory_values = [s["process"]["memory_rss"] for s in filtered_samples]
                stats["process_memory"] = {
                    "min": min(memory_values),
                    "max": max(memory_values),
                    "avg": sum(memory_values) / len(memory_values),
                    "current": filtered_samples[-1]["process"]["memory_rss"]
                }
                
                # System CPU stats
                sys_cpu_values = [s["system"]["cpu_percent"] for s in filtered_samples]
                stats["system_cpu"] = {
                    "min": min(sys_cpu_values),
                    "max": max(sys_cpu_values),
                    "avg": sum(sys_cpu_values) / len(sys_cpu_values)
                }
                
                # System memory stats
                sys_memory_values = [s["system"]["memory_percent"] for s in filtered_samples]
                stats["system_memory"] = {
                    "min": min(sys_memory_values),
                    "max": max(sys_memory_values),
                    "avg": sum(sys_memory_values) / len(sys_memory_values)
                }
            
            return stats


class PerformanceTester:
    """
    Runs performance tests to identify bottlenecks and optimization opportunities.
    """
    
    def __init__(self, service_name: str):
        """
        Initialize the performance tester.
        
        Args:
            service_name: Name of the service being tested
        """
        self.service_name = service_name
        self.test_results = {}
        self._lock = threading.Lock()
        logger.info(f"Initialized PerformanceTester for service {service_name}")
    
    def run_load_test(self, test_name: str, test_function: Callable, 
                     concurrency: int = 10, iterations: int = 100,
                     ramp_up_seconds: float = 1.0) -> Dict[str, Any]:
        """
        Run a load test with concurrent requests.
        
        Args:
            test_name: Name of the test
            test_function: Function to test (should take no arguments)
            concurrency: Number of concurrent executions
            iterations: Total number of iterations to run
            ramp_up_seconds: Time to ramp up to full concurrency
            
        Returns:
            Dictionary containing test results
        """
        logger.info(f"Starting load test {test_name} with concurrency {concurrency}, iterations {iterations}")
        
        results = []
        errors = []
        start_time = time.time()
        
        # Create a thread pool
        with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as executor:
            # Submit tasks with a ramp-up period
            futures = []
            for i in range(iterations):
                # Calculate delay for ramp-up
                if ramp_up_seconds > 0 and i < concurrency:
                    delay = (i / concurrency) * ramp_up_seconds
                    time.sleep(delay / concurrency)
                
                futures.append(executor.submit(self._run_test_iteration, test_function, i))
            
            # Collect results
            for future in concurrent.futures.as_completed(futures):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    errors.append(str(e))
        
        end_time = time.time()
        total_duration = end_time - start_time
        
        # Calculate statistics
        durations = [r["duration"] for r in results]
        
        test_result = {
            "name": test_name,
            "timestamp": datetime.utcnow().isoformat(),
            "concurrency": concurrency,
            "iterations": iterations,
            "completed": len(results),
            "errors": len(errors),
            "total_duration": total_duration,
            "throughput": len(results) / total_duration,
            "min_duration": min(durations) if durations else 0,
            "max_duration": max(durations) if durations else 0,
            "avg_duration": sum(durations) / len(durations) if durations else 0,
            "median_duration": statistics.median(durations) if durations else 0,
            "p90_duration": sorted(durations)[int(len(durations) * 0.9)] if len(durations) > 10 else 0,
            "p95_duration": sorted(durations)[int(len(durations) * 0.95)] if len(durations) > 20 else 0,
            "p99_duration": sorted(durations)[int(len(durations) * 0.99)] if len(durations) > 100 else 0,
            "error_details": errors[:10]  # Limit to first 10 errors
        }
        
        with self._lock:
            self.test_results[test_name] = test_result
        
        logger.info(f"Completed load test {test_name}: throughput={test_result['throughput']:.2f} req/s, avg={test_result['avg_duration']:.6f}s")
        return test_result
    
    def _run_test_iteration(self, test_function: Callable, iteration: int) -> Dict[str, Any]:
        """
        Run a single test iteration.
        
        Args:
            test_function: Function to test
            iteration: Iteration number
            
        Returns:
            Dictionary containing iteration results
        """
        start_time = time.time()
        
        try:
            result = test_function()
            success = True
            error = None
        except Exception as e:
            result = None
            success = False
            error = str(e)
        
        end_time = time.time()
        duration = end_time - start_time
        
        return {
            "iteration": iteration,
            "duration": duration,
            "success": success,
            "error": error,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def run_stress_test(self, test_name: str, test_function: Callable,
                       start_concurrency: int = 1, max_concurrency: int = 100,
                       step_size: int = 5, iterations_per_step: int = 50,
                       target_response_time: float = 1.0) -> Dict[str, Any]:
        """
        Run a stress test to find the maximum concurrency while maintaining response time.
        
        Args:
            test_name: Name of the test
            test_function: Function to test (should take no arguments)
            start_concurrency: Starting concurrency level
            max_concurrency: Maximum concurrency level
            step_size: How much to increase concurrency each step
            iterations_per_step: How many iterations to run at each concurrency level
            target_response_time: Target response time in seconds
            
        Returns:
            Dictionary containing test results
        """
        logger.info(f"Starting stress test {test_name} with max concurrency {max_concurrency}")
        
        step_results = []
        optimal_concurrency = start_concurrency
        exceeded_target = False
        
        # Test increasing concurrency levels
        concurrency = start_concurrency
        while concurrency <= max_concurrency and not exceeded_target:
            # Run a load test at this concurrency level
            result = self.run_load_test(
                f"{test_name}_c{concurrency}",
                test_function,
                concurrency=concurrency,
                iterations=iterations_per_step
            )
            
            step_results.append({
                "concurrency": concurrency,
                "throughput": result["throughput"],
                "avg_duration": result["avg_duration"],
                "p95_duration": result["p95_duration"]
            })
            
            # Check if we've exceeded the target response time
            if result["p95_duration"] > target_response_time:
                exceeded_target = True
                logger.info(f"Stress test {test_name} exceeded target response time at concurrency {concurrency}")
            else:
                optimal_concurrency = concurrency
                concurrency += step_size
        
        # Calculate the optimal throughput
        optimal_result = next((r for r in step_results if r["concurrency"] == optimal_concurrency), None)
        optimal_throughput = optimal_result["throughput"] if optimal_result else 0
        
        stress_result = {
            "name": test_name,
            "timestamp": datetime.utcnow().isoformat(),
            "optimal_concurrency": optimal_concurrency,
            "optimal_throughput": optimal_throughput,
            "target_response_time": target_response_time,
            "steps": step_results
        }
        
        with self._lock:
            self.test_results[f"{test_name}_stress"] = stress_result
        
        logger.info(f"Completed stress test {test_name}: optimal_concurrency={optimal_concurrency}, throughput={optimal_throughput:.2f} req/s")
        return stress_result
    
    def get_test_results(self, test_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Get test results.
        
        Args:
            test_name: Optional name of the test to get results for
            
        Returns:
            Dictionary containing test results
        """
        with self._lock:
            if test_name:
                return self.test_results.get(test_name, {"name": test_name, "error": "Test not found"})
            else:
                return dict(self.test_results)


class QueryOptimizer:
    """
    Analyzes and optimizes database and API queries.
    """
    
    def __init__(self, service_name: str):
        """
        Initialize the query optimizer.
        
        Args:
            service_name: Name of the service
        """
        self.service_name = service_name
        self.query_stats = {}
        self._lock = threading.Lock()
        logger.info(f"Initialized QueryOptimizer for service {service_name}")
    
    def record_query(self, query_type: str, query_id: str, query_text: str, 
                    duration: float, result_size: int) -> None:
        """
        Record a query execution for analysis.
        
        Args:
            query_type: Type of query (e.g., SQL, GraphQL, API)
            query_id: Identifier for the query
            query_text: Text of the query
            duration: Execution duration in seconds
            result_size: Size of the result (rows, items, bytes)
        """
        with self._lock:
            key = f"{query_type}:{query_id}"
            
            if key not in self.query_stats:
                self.query_stats[key] = {
                    "type": query_type,
                    "id": query_id,
                    "text": query_text,
                    "executions": 0,
                    "total_duration": 0,
                    "min_duration": float('inf'),
                    "max_duration": 0,
                    "total_result_size": 0,
                    "samples": []
                }
            
            stats = self.query_stats[key]
            stats["executions"] += 1
            stats["total_duration"] += duration
            stats["min_duration"] = min(stats["min_duration"], duration)
            stats["max_duration"] = max(stats["max_duration"], duration)
            stats["total_result_size"] += result_size
            
            # Add sample, keeping only the last 100
            stats["samples"].append({
                "timestamp": datetime.utcnow().isoformat(),
                "duration": duration,
                "result_size": result_size
            })
            
            if len(stats["samples"]) > 100:
                stats["samples"] = stats["samples"][-100:]
        
        logger.debug(f"Recorded {query_type} query {query_id}: {duration:.6f}s, {result_size} items")
    
    def analyze_query(self, query_type: str, query_id: str) -> Dict[str, Any]:
        """
        Analyze a specific query for optimization opportunities.
        
        Args:
            query_type: Type of query
            query_id: Identifier for the query
            
        Returns:
            Dictionary containing analysis results
        """
        key = f"{query_type}:{query_id}"
        
        with self._lock:
            if key not in self.query_stats:
                return {"error": "Query not found"}
            
            stats = self.query_stats[key]
        
        # Calculate statistics
        avg_duration = stats["total_duration"] / stats["executions"]
        avg_result_size = stats["total_result_size"] / stats["executions"]
        
        # Calculate duration per result item
        if avg_result_size > 0:
            duration_per_item = avg_duration / avg_result_size
        else:
            duration_per_item = avg_duration
        
        # Look for patterns in the query text
        optimization_suggestions = []
        
        if query_type == "SQL":
            # SQL-specific optimizations
            query_text = stats["text"].lower()
            
            if "select *" in query_text:
                optimization_suggestions.append("Use specific column names instead of SELECT *")
            
            if "where" not in query_text and "limit" not in query_text:
                optimization_suggestions.append("Add WHERE clause or LIMIT to restrict results")
            
            if "join" in query_text and "index" not in query_text:
                optimization_suggestions.append("Ensure joined columns are indexed")
            
            if "order by" in query_text and "limit" not in query_text:
                optimization_suggestions.append("Add LIMIT clause when using ORDER BY")
            
            if "group by" in query_text and "having" not in query_text:
                optimization_suggestions.append("Consider adding HAVING clause to filter groups")
        
        elif query_type == "GraphQL":
            # GraphQL-specific optimizations
            query_text = stats["text"].lower()
            
            if avg_result_size > 100:
                optimization_suggestions.append("Use pagination to limit result size")
            
            if "fragment" not in query_text and len(query_text) > 200:
                optimization_suggestions.append("Use fragments to organize complex queries")
            
            if query_text.count("{") > 3:
                optimization_suggestions.append("Consider splitting deeply nested queries")
        
        elif query_type == "API":
            # API-specific optimizations
            if avg_result_size > 100:
                optimization_suggestions.append("Use pagination parameters to limit result size")
            
            if duration_per_item > 0.01:
                optimization_suggestions.append("Response time per item is high, consider optimizing backend processing")
        
        # Performance classification
        if avg_duration < 0.01:
            performance_class = "Excellent"
        elif avg_duration < 0.1:
            performance_class = "Good"
        elif avg_duration < 0.5:
            performance_class = "Fair"
        elif avg_duration < 1.0:
            performance_class = "Poor"
        else:
            performance_class = "Critical"
        
        analysis = {
            "type": query_type,
            "id": query_id,
            "text": stats["text"],
            "executions": stats["executions"],
            "avg_duration": avg_duration,
            "min_duration": stats["min_duration"],
            "max_duration": stats["max_duration"],
            "avg_result_size": avg_result_size,
            "duration_per_item": duration_per_item,
            "performance_class": performance_class,
            "optimization_suggestions": optimization_suggestions
        }
        
        logger.info(f"Analyzed {query_type} query {query_id}: {performance_class}, {len(optimization_suggestions)} suggestions")
        return analysis
    
    def get_slowest_queries(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get the slowest queries by average duration.
        
        Args:
            limit: Maximum number of queries to return
            
        Returns:
            List of query statistics
        """
        with self._lock:
            # Calculate average duration for each query
            query_avgs = [
                {
                    "type": stats["type"],
                    "id": stats["id"],
                    "text": stats["text"],
                    "avg_duration": stats["total_duration"] / stats["executions"],
                    "executions": stats["executions"]
                }
                for key, stats in self.query_stats.items()
            ]
        
        # Sort by average duration (descending)
        sorted_queries = sorted(query_avgs, key=lambda q: q["avg_duration"], reverse=True)
        
        return sorted_queries[:limit]
    
    def get_most_frequent_queries(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get the most frequently executed queries.
        
        Args:
            limit: Maximum number of queries to return
            
        Returns:
            List of query statistics
        """
        with self._lock:
            # Extract execution count for each query
            query_freqs = [
                {
                    "type": stats["type"],
                    "id": stats["id"],
                    "text": stats["text"],
                    "executions": stats["executions"],
                    "avg_duration": stats["total_duration"] / stats["executions"]
                }
                for key, stats in self.query_stats.items()
            ]
        
        # Sort by execution count (descending)
        sorted_queries = sorted(query_freqs, key=lambda q: q["executions"], reverse=True)
        
        return sorted_queries[:limit]


class PerformanceOptimizationSystem:
    """
    Main class that integrates all performance optimization components.
    """
    
    def __init__(self, service_name: str):
        """
        Initialize the performance optimization system.
        
        Args:
            service_name: Name of the service
        """
        self.service_name = service_name
        
        # Initialize components
        self.profiler = PerformanceProfiler(service_name)
        self.cache = CachingService(f"{service_name}_cache")
        self.resource_monitor = ResourceMonitor(service_name)
        self.tester = PerformanceTester(service_name)
        self.query_optimizer = QueryOptimizer(service_name)
        
        logger.info(f"Initialized PerformanceOptimizationSystem for service {service_name}")
    
    def start_monitoring(self) -> None:
        """Start resource monitoring."""
        self.resource_monitor.start_monitoring()
    
    def stop_monitoring(self) -> None:
        """Stop resource monitoring."""
        self.resource_monitor.stop_monitoring()
    
    def profile_operation(self, name: str):
        """
        Context manager for profiling an operation.
        
        Args:
            name: Name of the operation
            
        Returns:
            Context manager for profiling
        """
        return self.profiler.profile(name)
    
    def cached_operation(self, operation_func, key_func=None, ttl_seconds=None):
        """
        Decorator for caching operation results.
        
        Args:
            operation_func: Function to cache results for
            key_func: Optional function to generate cache key from args
            ttl_seconds: Optional TTL for cache entries
            
        Returns:
            Decorated function with caching
        """
        def wrapper(*args, **kwargs):
            # Generate cache key
            if key_func:
                key = key_func(*args, **kwargs)
            else:
                # Default key generation
                key = {
                    "func": operation_func.__name__,
                    "args": [str(arg) for arg in args],
                    "kwargs": {k: str(v) for k, v in kwargs.items()}
                }
            
            # Check cache
            cached_result = self.cache.get(key)
            if cached_result is not None:
                return cached_result
            
            # Execute operation
            with self.profile_operation(f"cached_{operation_func.__name__}"):
                result = operation_func(*args, **kwargs)
            
            # Cache result
            self.cache.set(key, result, ttl_seconds)
            
            return result
        
        return wrapper
    
    def optimize_query(self, query_type: str, query_id: str, query_text: str):
        """
        Decorator for optimizing and tracking queries.
        
        Args:
            query_type: Type of query
            query_id: Identifier for the query
            query_text: Text of the query
            
        Returns:
            Decorated function with query optimization
        """
        def decorator(query_func):
            def wrapper(*args, **kwargs):
                start_time = time.time()
                
                try:
                    result = query_func(*args, **kwargs)
                    
                    # Determine result size
                    if isinstance(result, list):
                        result_size = len(result)
                    elif isinstance(result, dict):
                        result_size = len(result)
                    else:
                        result_size = 1
                    
                    duration = time.time() - start_time
                    
                    # Record query execution
                    self.query_optimizer.record_query(
                        query_type, query_id, query_text, duration, result_size
                    )
                    
                    return result
                except Exception as e:
                    # Record failed query
                    duration = time.time() - start_time
                    self.query_optimizer.record_query(
                        query_type, query_id, query_text, duration, 0
                    )
                    raise
            
            return wrapper
        
        return decorator
    
    def get_optimization_recommendations(self) -> Dict[str, Any]:
        """
        Get comprehensive performance optimization recommendations.
        
        Returns:
            Dictionary containing optimization recommendations
        """
        recommendations = {
            "service": self.service_name,
            "timestamp": datetime.utcnow().isoformat(),
            "profile_recommendations": [],
            "resource_recommendations": [],
            "query_recommendations": [],
            "caching_recommendations": []
        }
        
        # Profile-based recommendations
        profile_data = self.profiler.get_profile_data()
        slow_operations = []
        
        for name, data in profile_data.items():
            if data["avg_duration"] > 0.1:  # Operations taking more than 100ms
                slow_operations.append({
                    "name": name,
                    "avg_duration": data["avg_duration"],
                    "count": data["count"]
                })
        
        if slow_operations:
            recommendations["profile_recommendations"].append({
                "type": "slow_operations",
                "operations": slow_operations,
                "suggestion": "Optimize these slow operations to improve overall performance"
            })
        
        # Resource-based recommendations
        resource_data = self.resource_monitor.get_resource_usage(window_seconds=300)
        
        if "process_cpu" in resource_data and resource_data["process_cpu"]["avg"] > 70:
            recommendations["resource_recommendations"].append({
                "type": "high_cpu_usage",
                "value": resource_data["process_cpu"]["avg"],
                "suggestion": "CPU usage is high, consider optimizing CPU-intensive operations or scaling horizontally"
            })
        
        if "process_memory" in resource_data:
            memory_growth = (resource_data["process_memory"]["max"] - resource_data["process_memory"]["min"]) / resource_data["process_memory"]["min"] * 100
            
            if memory_growth > 20:
                recommendations["resource_recommendations"].append({
                    "type": "memory_growth",
                    "value": memory_growth,
                    "suggestion": "Memory usage is growing significantly, check for memory leaks or excessive caching"
                })
        
        # Query-based recommendations
        slow_queries = self.query_optimizer.get_slowest_queries(5)
        
        for query in slow_queries:
            if query["avg_duration"] > 0.2:  # Queries taking more than 200ms
                analysis = self.query_optimizer.analyze_query(query["type"], query["id"])
                
                recommendations["query_recommendations"].append({
                    "type": "slow_query",
                    "query_type": query["type"],
                    "query_id": query["id"],
                    "avg_duration": query["avg_duration"],
                    "suggestions": analysis.get("optimization_suggestions", [])
                })
        
        # Caching recommendations
        cache_stats = self.cache.get_stats()
        
        if cache_stats["size"] > 0.8 * cache_stats["max_size"]:
            recommendations["caching_recommendations"].append({
                "type": "cache_size",
                "value": cache_stats["size"],
                "max_size": cache_stats["max_size"],
                "suggestion": "Cache is nearing capacity, consider increasing max size or reducing TTL"
            })
        
        return recommendations


# Example usage
if __name__ == "__main__":
    # Initialize performance optimization system
    perf_system = PerformanceOptimizationSystem("example-service")
    
    # Start resource monitoring
    perf_system.start_monitoring()
    
    # Example of profiling an operation
    with perf_system.profile_operation("example_operation"):
        # Simulate some work
        time.sleep(0.1)
    
    # Example of a cached operation
    @perf_system.cached_operation
    def expensive_calculation(x, y):
        # Simulate expensive calculation
        time.sleep(0.2)
        return x * y
    
    # Call the cached function multiple times
    result1 = expensive_calculation(5, 10)
    result2 = expensive_calculation(5, 10)  # Should be cached
    
    # Example of query optimization
    @perf_system.optimize_query("SQL", "get_users", "SELECT * FROM users WHERE active = true")
    def get_users():
        # Simulate database query
        time.sleep(0.15)
        return [{"id": i, "name": f"User {i}"} for i in range(10)]
    
    # Call the query function
    users = get_users()
    
    # Example of performance testing
    def test_function():
        # Function to test
        time.sleep(0.01 + random.random() * 0.02)
        return {"status": "success"}
    
    # Run a load test
    perf_system.tester.run_load_test("example_test", test_function, concurrency=5, iterations=20)
    
    # Get optimization recommendations
    recommendations = perf_system.get_optimization_recommendations()
    print(json.dumps(recommendations, indent=2))
    
    # Stop resource monitoring
    perf_system.stop_monitoring()
