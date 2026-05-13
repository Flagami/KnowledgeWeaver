"""Error handling and recovery strategies for KnowledgeWeaver."""

import asyncio
import time
from enum import Enum
from typing import Callable, Optional, TypeVar

from knowledgeweaver.utils.errors import ResearchAgentError
from knowledgeweaver.utils.logger import logger

T = TypeVar("T")


class ErrorSeverity(str, Enum):
    """Error severity levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorRecoveryStrategy(str, Enum):
    """Error recovery strategies."""

    RETRY = "retry"
    FALLBACK = "fallback"
    SKIP = "skip"
    ABORT = "abort"


class CircuitBreakerState(str, Enum):
    """Circuit breaker states."""

    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitBreaker:
    """Circuit breaker for handling cascading failures."""

    def __init__(
        self,
        name: str,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
    ):
        """Initialize circuit breaker.

        Args:
            name: Circuit breaker name
            failure_threshold: Number of failures before opening
            recovery_timeout: Seconds before attempting recovery
        """
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0
        self.last_failure_time = None
        self.logger = logger

    async def call(self, func: Callable, *args, **kwargs):
        """Execute function with circuit breaker protection.

        Args:
            func: Function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments

        Returns:
            Function result

        Raises:
            ResearchAgentError: If circuit is open
        """
        if self.state == CircuitBreakerState.OPEN:
            if self._should_attempt_recovery():
                self.state = CircuitBreakerState.HALF_OPEN
                self.logger.info(f"Circuit breaker {self.name} attempting recovery")
            else:
                raise ResearchAgentError(
                    f"Circuit breaker {self.name} is open"
                )

        try:
            result = await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)
            self._on_success()
            return result

        except Exception as e:
            self._on_failure()
            raise

    def _on_success(self) -> None:
        """Handle successful call."""
        self.failure_count = 0
        if self.state == CircuitBreakerState.HALF_OPEN:
            self.state = CircuitBreakerState.CLOSED
            self.logger.info(f"Circuit breaker {self.name} recovered")

    def _on_failure(self) -> None:
        """Handle failed call."""
        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.failure_count >= self.failure_threshold:
            self.state = CircuitBreakerState.OPEN
            self.logger.warning(
                f"Circuit breaker {self.name} opened after {self.failure_count} failures"
            )

    def _should_attempt_recovery(self) -> bool:
        """Check if recovery should be attempted."""
        if self.last_failure_time is None:
            return True

        elapsed = time.time() - self.last_failure_time
        return elapsed >= self.recovery_timeout


class RetryStrategy:
    """Retry strategy with exponential backoff."""

    def __init__(
        self,
        max_retries: int = 3,
        initial_delay: float = 1.0,
        max_delay: float = 60.0,
        backoff_factor: float = 2.0,
    ):
        """Initialize retry strategy.

        Args:
            max_retries: Maximum number of retries
            initial_delay: Initial delay in seconds
            max_delay: Maximum delay in seconds
            backoff_factor: Exponential backoff factor
        """
        self.max_retries = max_retries
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.backoff_factor = backoff_factor
        self.logger = logger

    async def execute(
        self,
        func: Callable,
        *args,
        retryable_exceptions: tuple = (Exception,),
        **kwargs,
    ):
        """Execute function with retry logic.

        Args:
            func: Function to execute
            *args: Function arguments
            retryable_exceptions: Exceptions that trigger retry
            **kwargs: Function keyword arguments

        Returns:
            Function result

        Raises:
            Exception: If all retries fail
        """
        delay = self.initial_delay
        last_exception = None

        for attempt in range(self.max_retries + 1):
            try:
                if asyncio.iscoroutinefunction(func):
                    return await func(*args, **kwargs)
                else:
                    return func(*args, **kwargs)

            except retryable_exceptions as e:
                last_exception = e

                if attempt < self.max_retries:
                    self.logger.warning(
                        f"Attempt {attempt + 1} failed: {e}. Retrying in {delay}s..."
                    )
                    await asyncio.sleep(delay)
                    delay = min(delay * self.backoff_factor, self.max_delay)
                else:
                    self.logger.error(
                        f"All {self.max_retries + 1} attempts failed"
                    )

        raise last_exception


class ErrorHandler:
    """Centralized error handling for KnowledgeWeaver."""

    def __init__(self):
        """Initialize error handler."""
        self.logger = logger
        self.circuit_breakers = {}
        self.error_counts = {}

    def get_circuit_breaker(self, name: str) -> CircuitBreaker:
        """Get or create a circuit breaker.

        Args:
            name: Circuit breaker name

        Returns:
            Circuit breaker instance
        """
        if name not in self.circuit_breakers:
            self.circuit_breakers[name] = CircuitBreaker(name)
        return self.circuit_breakers[name]

    def classify_error(self, error: Exception) -> tuple[ErrorSeverity, ErrorRecoveryStrategy]:
        """Classify error and determine recovery strategy.

        Args:
            error: Exception to classify

        Returns:
            Tuple of (severity, recovery_strategy)
        """
        error_type = type(error).__name__

        # Network errors - retry
        if "Connection" in error_type or "Timeout" in error_type:
            return ErrorSeverity.MEDIUM, ErrorRecoveryStrategy.RETRY

        # API errors - fallback or skip
        if "API" in error_type or "HTTP" in error_type:
            return ErrorSeverity.MEDIUM, ErrorRecoveryStrategy.FALLBACK

        # Data errors - skip
        if "Data" in error_type or "Parse" in error_type:
            return ErrorSeverity.LOW, ErrorRecoveryStrategy.SKIP

        # Storage errors - abort
        if "Storage" in error_type or "Database" in error_type:
            return ErrorSeverity.HIGH, ErrorRecoveryStrategy.ABORT

        # Unknown errors - abort
        return ErrorSeverity.HIGH, ErrorRecoveryStrategy.ABORT

    def handle_error(
        self,
        error: Exception,
        context: Optional[str] = None,
    ) -> tuple[ErrorSeverity, ErrorRecoveryStrategy]:
        """Handle an error with appropriate logging and classification.

        Args:
            error: Exception to handle
            context: Optional context information

        Returns:
            Tuple of (severity, recovery_strategy)
        """
        severity, strategy = self.classify_error(error)

        # Track error counts
        error_type = type(error).__name__
        self.error_counts[error_type] = self.error_counts.get(error_type, 0) + 1

        # Log error
        log_message = f"Error: {error_type}"
        if context:
            log_message += f" (context: {context})"

        if severity == ErrorSeverity.CRITICAL:
            self.logger.critical(log_message)
        elif severity == ErrorSeverity.HIGH:
            self.logger.error(log_message)
        elif severity == ErrorSeverity.MEDIUM:
            self.logger.warning(log_message)
        else:
            self.logger.debug(log_message)

        return severity, strategy

    def get_error_summary(self) -> dict:
        """Get summary of errors encountered.

        Returns:
            Error summary dictionary
        """
        return {
            "total_errors": sum(self.error_counts.values()),
            "error_types": self.error_counts,
            "circuit_breakers": {
                name: cb.state.value
                for name, cb in self.circuit_breakers.items()
            },
        }

    def reset_error_tracking(self) -> None:
        """Reset error tracking."""
        self.error_counts.clear()
        for cb in self.circuit_breakers.values():
            cb.failure_count = 0
            cb.state = CircuitBreakerState.CLOSED


class GracefulDegradation:
    """Graceful degradation strategies when services fail."""

    @staticmethod
    def fallback_to_abstract(paper) -> Optional[str]:
        """Fallback to paper abstract when full text unavailable.

        Args:
            paper: Paper metadata

        Returns:
            Paper abstract or None
        """
        return paper.abstract if hasattr(paper, "abstract") else None

    @staticmethod
    def fallback_to_title_authors(paper) -> str:
        """Fallback to title and authors when summary unavailable.

        Args:
            paper: Paper metadata

        Returns:
            Title and authors string
        """
        title = getattr(paper, "title", "Unknown")
        authors = getattr(paper, "authors", "Unknown")
        return f"{title} by {authors}"

    @staticmethod
    def fallback_to_single_source(domain: str) -> list[str]:
        """Fallback to single source when multiple sources fail.

        Args:
            domain: Research domain

        Returns:
            List with single source
        """
        # Default fallback sources by domain
        fallback_sources = {
            "AI/ML": ["arxiv"],
            "Biology": ["pubmed"],
            "Physics": ["arxiv"],
            "Chemistry": ["crossref"],
            "Medicine": ["pubmed"],
        }
        return fallback_sources.get(domain, ["semantic_scholar"])

    @staticmethod
    def fallback_to_shallow_synthesis() -> str:
        """Fallback to shallow synthesis when deep synthesis fails.

        Returns:
            Shallow synthesis message
        """
        return "Synthesis based on available paper abstracts and metadata."
