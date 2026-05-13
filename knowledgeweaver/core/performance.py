"""Performance optimization and monitoring for KnowledgeWeaver."""

import time
from datetime import datetime, timedelta
from functools import wraps
from typing import Any, Callable, Dict, Optional

from knowledgeweaver.utils.logger import logger


class PerformanceMonitor:
    """Monitors and tracks performance metrics."""

    def __init__(self):
        """Initialize performance monitor."""
        self.logger = logger
        self.metrics: Dict[str, list] = {}
        self.start_times: Dict[str, float] = {}

    def start_timer(self, operation: str) -> None:
        """Start timing an operation.

        Args:
            operation: Operation name
        """
        self.start_times[operation] = time.time()

    def end_timer(self, operation: str) -> float:
        """End timing an operation and record metric.

        Args:
            operation: Operation name

        Returns:
            Elapsed time in seconds
        """
        if operation not in self.start_times:
            self.logger.warning(f"Timer not started for {operation}")
            return 0.0

        elapsed = time.time() - self.start_times[operation]
        del self.start_times[operation]

        if operation not in self.metrics:
            self.metrics[operation] = []

        self.metrics[operation].append(elapsed)
        return elapsed

    def get_average_time(self, operation: str) -> Optional[float]:
        """Get average execution time for an operation.

        Args:
            operation: Operation name

        Returns:
            Average time in seconds or None
        """
        if operation not in self.metrics or not self.metrics[operation]:
            return None

        times = self.metrics[operation]
        return sum(times) / len(times)

    def get_stats(self, operation: str) -> Optional[dict]:
        """Get statistics for an operation.

        Args:
            operation: Operation name

        Returns:
            Statistics dictionary or None
        """
        if operation not in self.metrics or not self.metrics[operation]:
            return None

        times = self.metrics[operation]
        return {
            "count": len(times),
            "total": sum(times),
            "average": sum(times) / len(times),
            "min": min(times),
            "max": max(times),
        }

    def get_all_stats(self) -> dict:
        """Get statistics for all operations.

        Returns:
            Dictionary of all statistics
        """
        stats = {}
        for operation in self.metrics:
            op_stats = self.get_stats(operation)
            if op_stats:
                stats[operation] = op_stats
        return stats

    def reset_metrics(self) -> None:
        """Reset all metrics."""
        self.metrics.clear()
        self.start_times.clear()


class CacheManager:
    """Manages caching for expensive operations."""

    def __init__(self, ttl_seconds: int = 3600):
        """Initialize cache manager.

        Args:
            ttl_seconds: Time-to-live for cache entries
        """
        self.ttl_seconds = ttl_seconds
        self.cache: Dict[str, tuple[Any, float]] = {}
        self.logger = logger

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if expired/not found
        """
        if key not in self.cache:
            return None

        value, timestamp = self.cache[key]
        elapsed = time.time() - timestamp

        if elapsed > self.ttl_seconds:
            del self.cache[key]
            self.logger.debug(f"Cache expired for key: {key}")
            return None

        self.logger.debug(f"Cache hit for key: {key}")
        return value

    def set(self, key: str, value: Any) -> None:
        """Set value in cache.

        Args:
            key: Cache key
            value: Value to cache
        """
        self.cache[key] = (value, time.time())
        self.logger.debug(f"Cache set for key: {key}")

    def clear(self) -> None:
        """Clear all cache entries."""
        self.cache.clear()
        self.logger.debug("Cache cleared")

    def get_stats(self) -> dict:
        """Get cache statistics.

        Returns:
            Cache statistics
        """
        return {
            "entries": len(self.cache),
            "ttl_seconds": self.ttl_seconds,
        }


def cached(ttl_seconds: int = 3600):
    """Decorator for caching function results.

    Args:
        ttl_seconds: Time-to-live for cache entries

    Returns:
        Decorator function
    """
    cache = CacheManager(ttl_seconds=ttl_seconds)

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key from function name and arguments
            cache_key = f"{func.__name__}:{str(args)}:{str(kwargs)}"

            # Try to get from cache
            cached_value = cache.get(cache_key)
            if cached_value is not None:
                return cached_value

            # Execute function and cache result
            result = func(*args, **kwargs)
            cache.set(cache_key, result)
            return result

        return wrapper

    return decorator


def timed(monitor: Optional[PerformanceMonitor] = None):
    """Decorator for timing function execution.

    Args:
        monitor: Optional performance monitor instance

    Returns:
        Decorator function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            perf_monitor = monitor or PerformanceMonitor()
            operation = func.__name__

            perf_monitor.start_timer(operation)
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                elapsed = perf_monitor.end_timer(operation)
                logger.debug(f"{operation} took {elapsed:.3f}s")

        return wrapper

    return decorator


class QueryOptimizer:
    """Optimizes database queries."""

    @staticmethod
    def optimize_paper_query(session, domain: Optional[str] = None):
        """Optimize paper query with eager loading.

        Args:
            session: Database session
            domain: Optional domain filter

        Returns:
            Optimized query
        """
        from knowledgeweaver.storage.models import Paper, Query

        query = session.query(Paper)

        if domain:
            query = query.join(Query).filter(Query.domain == domain)

        return query

    @staticmethod
    def optimize_preference_query(session, domain: Optional[str] = None):
        """Optimize preference query.

        Args:
            session: Database session
            domain: Optional domain filter

        Returns:
            Optimized query
        """
        from knowledgeweaver.storage.models import UserPreferences

        query = session.query(UserPreferences)

        if domain:
            query = query.filter(UserPreferences.domain == domain)

        return query


class PerformanceTuner:
    """Provides performance tuning recommendations."""

    def __init__(self, monitor: PerformanceMonitor):
        """Initialize performance tuner.

        Args:
            monitor: Performance monitor instance
        """
        self.monitor = monitor
        self.logger = logger

    def get_recommendations(self) -> list[str]:
        """Get performance tuning recommendations.

        Returns:
            List of recommendations
        """
        recommendations = []
        stats = self.monitor.get_all_stats()

        for operation, op_stats in stats.items():
            avg_time = op_stats["average"]

            # Recommend caching for slow operations
            if avg_time > 5.0:
                recommendations.append(
                    f"Consider caching results for {operation} (avg: {avg_time:.2f}s)"
                )

            # Recommend optimization for very slow operations
            if avg_time > 10.0:
                recommendations.append(
                    f"Optimize {operation} - taking {avg_time:.2f}s on average"
                )

            # Recommend parallelization for frequently called operations
            if op_stats["count"] > 100 and avg_time > 1.0:
                recommendations.append(
                    f"Consider parallelizing {operation} (called {op_stats['count']} times)"
                )

        if not recommendations:
            recommendations.append("Performance is good! No immediate optimizations needed.")

        return recommendations

    def get_bottlenecks(self) -> list[tuple[str, float]]:
        """Get performance bottlenecks.

        Returns:
            List of (operation, total_time) tuples sorted by total time
        """
        stats = self.monitor.get_all_stats()
        bottlenecks = [
            (operation, op_stats["total"])
            for operation, op_stats in stats.items()
        ]
        bottlenecks.sort(key=lambda x: x[1], reverse=True)
        return bottlenecks


# Global performance monitor instance
performance_monitor = PerformanceMonitor()
