"""Unit tests for Phase 6: Integration & Testing components."""

import pytest

from knowledgeweaver.core.error_handler import (
    CircuitBreaker,
    CircuitBreakerState,
    ErrorHandler,
    ErrorRecoveryStrategy,
    ErrorSeverity,
    GracefulDegradation,
    RetryStrategy,
)
from knowledgeweaver.core.performance import (
    CacheManager,
    PerformanceMonitor,
    PerformanceTuner,
)


class TestCircuitBreaker:
    """Test circuit breaker."""

    @pytest.fixture
    def breaker(self):
        """Create circuit breaker."""
        return CircuitBreaker(name="test", failure_threshold=3)

    @pytest.mark.asyncio
    async def test_circuit_breaker_closed_state(self, breaker):
        """Test circuit breaker in closed state."""
        assert breaker.state == CircuitBreakerState.CLOSED

    @pytest.mark.asyncio
    async def test_circuit_breaker_opens_after_failures(self, breaker):
        """Test circuit breaker opens after threshold failures."""
        async def failing_func():
            raise Exception("Test error")

        # Trigger failures
        for _ in range(3):
            try:
                await breaker.call(failing_func)
            except Exception:
                pass

        assert breaker.state == CircuitBreakerState.OPEN

    @pytest.mark.asyncio
    async def test_circuit_breaker_rejects_calls_when_open(self, breaker):
        """Test circuit breaker rejects calls when open."""
        async def failing_func():
            raise Exception("Test error")

        # Open the circuit
        for _ in range(3):
            try:
                await breaker.call(failing_func)
            except Exception:
                pass

        # Try to call when open
        with pytest.raises(Exception):
            await breaker.call(failing_func)


class TestRetryStrategy:
    """Test retry strategy."""

    @pytest.fixture
    def retry(self):
        """Create retry strategy."""
        return RetryStrategy(max_retries=2, initial_delay=0.1)

    @pytest.mark.asyncio
    async def test_retry_succeeds_on_first_attempt(self, retry):
        """Test retry succeeds on first attempt."""
        async def success_func():
            return "success"

        result = await retry.execute(success_func)
        assert result == "success"

    @pytest.mark.asyncio
    async def test_retry_succeeds_after_failures(self, retry):
        """Test retry succeeds after failures."""
        call_count = 0

        async def eventually_succeeds():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise Exception("Not yet")
            return "success"

        result = await retry.execute(eventually_succeeds)
        assert result == "success"
        assert call_count == 3


class TestErrorHandler:
    """Test error handler."""

    @pytest.fixture
    def handler(self):
        """Create error handler."""
        return ErrorHandler()

    def test_classify_connection_error(self, handler):
        """Test classifying connection error."""
        error = ConnectionError("Connection failed")
        severity, strategy = handler.classify_error(error)

        assert severity == ErrorSeverity.MEDIUM
        assert strategy == ErrorRecoveryStrategy.RETRY

    def test_classify_timeout_error(self, handler):
        """Test classifying timeout error."""
        error = TimeoutError("Request timed out")
        severity, strategy = handler.classify_error(error)

        assert severity == ErrorSeverity.MEDIUM
        assert strategy == ErrorRecoveryStrategy.RETRY

    def test_get_circuit_breaker(self, handler):
        """Test getting circuit breaker."""
        cb1 = handler.get_circuit_breaker("test")
        cb2 = handler.get_circuit_breaker("test")

        assert cb1 is cb2

    def test_get_error_summary(self, handler):
        """Test getting error summary."""
        summary = handler.get_error_summary()

        assert "total_errors" in summary
        assert "error_types" in summary
        assert "circuit_breakers" in summary


class TestPerformanceMonitor:
    """Test performance monitor."""

    @pytest.fixture
    def monitor(self):
        """Create performance monitor."""
        return PerformanceMonitor()

    def test_timer_tracking(self, monitor):
        """Test timer tracking."""
        import time

        monitor.start_timer("test_op")
        time.sleep(0.1)
        elapsed = monitor.end_timer("test_op")

        assert elapsed >= 0.1

    def test_get_average_time(self, monitor):
        """Test getting average time."""
        import time

        for _ in range(3):
            monitor.start_timer("test_op")
            time.sleep(0.05)
            monitor.end_timer("test_op")

        avg = monitor.get_average_time("test_op")
        assert avg is not None
        assert avg >= 0.05

    def test_get_stats(self, monitor):
        """Test getting statistics."""
        import time

        for _ in range(3):
            monitor.start_timer("test_op")
            time.sleep(0.01)
            monitor.end_timer("test_op")

        stats = monitor.get_stats("test_op")
        assert stats["count"] == 3
        assert stats["average"] > 0

    def test_reset_metrics(self, monitor):
        """Test resetting metrics."""
        monitor.start_timer("test_op")
        monitor.end_timer("test_op")

        monitor.reset_metrics()
        assert monitor.get_average_time("test_op") is None


class TestCacheManager:
    """Test cache manager."""

    @pytest.fixture
    def cache(self):
        """Create cache manager."""
        return CacheManager(ttl_seconds=10)

    def test_cache_set_and_get(self, cache):
        """Test setting and getting cache."""
        cache.set("key1", "value1")
        value = cache.get("key1")

        assert value == "value1"

    def test_cache_miss(self, cache):
        """Test cache miss."""
        value = cache.get("nonexistent")
        assert value is None

    def test_cache_expiration(self):
        """Test cache expiration."""
        cache = CacheManager(ttl_seconds=0.1)
        cache.set("key1", "value1")

        import time
        time.sleep(0.2)

        value = cache.get("key1")
        assert value is None

    def test_cache_clear(self, cache):
        """Test clearing cache."""
        cache.set("key1", "value1")
        cache.set("key2", "value2")

        cache.clear()

        assert cache.get("key1") is None
        assert cache.get("key2") is None

    def test_cache_stats(self, cache):
        """Test cache statistics."""
        cache.set("key1", "value1")
        stats = cache.get_stats()

        assert stats["entries"] == 1
        assert stats["ttl_seconds"] == 10


class TestPerformanceTuner:
    """Test performance tuner."""

    @pytest.fixture
    def tuner(self):
        """Create performance tuner."""
        monitor = PerformanceMonitor()
        return PerformanceTuner(monitor)

    def test_get_recommendations(self, tuner):
        """Test getting recommendations."""
        recommendations = tuner.get_recommendations()
        assert isinstance(recommendations, list)

    def test_get_bottlenecks(self, tuner):
        """Test getting bottlenecks."""
        bottlenecks = tuner.get_bottlenecks()
        assert isinstance(bottlenecks, list)


class TestGracefulDegradation:
    """Test graceful degradation strategies."""

    def test_fallback_to_abstract(self):
        """Test fallback to abstract."""
        class MockPaper:
            abstract = "Test abstract"

        paper = MockPaper()
        result = GracefulDegradation.fallback_to_abstract(paper)

        assert result == "Test abstract"

    def test_fallback_to_title_authors(self):
        """Test fallback to title and authors."""
        class MockPaper:
            title = "Test Title"
            authors = "John Doe"

        paper = MockPaper()
        result = GracefulDegradation.fallback_to_title_authors(paper)

        assert "Test Title" in result
        assert "John Doe" in result

    def test_fallback_to_single_source(self):
        """Test fallback to single source."""
        sources = GracefulDegradation.fallback_to_single_source("AI/ML")
        assert len(sources) == 1
        assert sources[0] == "arxiv"

    def test_fallback_to_shallow_synthesis(self):
        """Test fallback to shallow synthesis."""
        result = GracefulDegradation.fallback_to_shallow_synthesis()
        assert isinstance(result, str)
        assert len(result) > 0
