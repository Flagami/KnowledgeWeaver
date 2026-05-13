"""Query management and concurrency control."""

import asyncio
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import uuid4

from knowledgeweaver.config import settings
from knowledgeweaver.utils.logger import logger


class QueryStatus(str, Enum):
    """Query status enumeration."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class Query:
    """Represents a research query."""

    query_id: str = field(default_factory=lambda: str(uuid4()))
    query_text: str = ""
    domain: str = ""
    status: QueryStatus = QueryStatus.PENDING
    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result_path: Optional[str] = None
    error_message: Optional[str] = None
    processing_time_seconds: float = 0.0

    def __repr__(self) -> str:
        return f"<Query(id={self.query_id[:8]}, text={self.query_text[:30]}, status={self.status})>"


class QueryManager:
    """Manages query queue and concurrency control."""

    def __init__(self, max_concurrent: int = settings.concurrent_queries):
        """Initialize query manager.

        Args:
            max_concurrent: Maximum concurrent queries (default: from config)
        """
        self.max_concurrent = max_concurrent
        self.query_queue: list[Query] = []
        self.active_queries: dict[str, Query] = {}
        self.completed_queries: dict[str, Query] = {}
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.logger = logger

    async def submit_query(self, query_text: str, domain: str = "") -> Query:
        """Submit a new query to the queue.

        Args:
            query_text: Query text
            domain: Research domain (optional)

        Returns:
            Query object
        """
        query = Query(query_text=query_text, domain=domain)
        self.query_queue.append(query)
        self.logger.info(f"Query submitted: {query.query_id} - {query_text[:50]}")
        return query

    async def get_next_query(self) -> Optional[Query]:
        """Get next query from queue.

        Returns:
            Next query or None if queue is empty
        """
        if self.query_queue:
            query = self.query_queue.pop(0)
            return query
        return None

    async def start_processing(self, query: Query) -> None:
        """Mark query as processing.

        Args:
            query: Query to process
        """
        query.status = QueryStatus.PROCESSING
        query.started_at = datetime.utcnow()
        self.active_queries[query.query_id] = query
        self.logger.debug(f"Processing started: {query.query_id}")

    async def complete_query(
        self,
        query: Query,
        result_path: Optional[str] = None,
    ) -> None:
        """Mark query as completed.

        Args:
            query: Query to complete
            result_path: Path to result file
        """
        query.status = QueryStatus.COMPLETED
        query.completed_at = datetime.utcnow()
        query.result_path = result_path

        if query.started_at:
            query.processing_time_seconds = (
                query.completed_at - query.started_at
            ).total_seconds()

        self.active_queries.pop(query.query_id, None)
        self.completed_queries[query.query_id] = query
        self.logger.info(
            f"Query completed: {query.query_id} ({query.processing_time_seconds:.2f}s)"
        )

    async def fail_query(self, query: Query, error_message: str) -> None:
        """Mark query as failed.

        Args:
            query: Query that failed
            error_message: Error message
        """
        query.status = QueryStatus.FAILED
        query.completed_at = datetime.utcnow()
        query.error_message = error_message

        if query.started_at:
            query.processing_time_seconds = (
                query.completed_at - query.started_at
            ).total_seconds()

        self.active_queries.pop(query.query_id, None)
        self.completed_queries[query.query_id] = query
        self.logger.error(f"Query failed: {query.query_id} - {error_message}")

    async def cancel_query(self, query_id: str) -> bool:
        """Cancel a query.

        Args:
            query_id: Query ID to cancel

        Returns:
            True if cancelled, False if not found or already completed
        """
        # Check if in queue
        for i, query in enumerate(self.query_queue):
            if query.query_id == query_id:
                query.status = QueryStatus.CANCELLED
                self.query_queue.pop(i)
                self.logger.info(f"Query cancelled: {query_id}")
                return True

        # Check if active
        if query_id in self.active_queries:
            query = self.active_queries[query_id]
            query.status = QueryStatus.CANCELLED
            self.active_queries.pop(query_id)
            self.logger.info(f"Query cancelled: {query_id}")
            return True

        return False

    def get_query_status(self, query_id: str) -> Optional[QueryStatus]:
        """Get status of a query.

        Args:
            query_id: Query ID

        Returns:
            Query status or None if not found
        """
        # Check queue
        for query in self.query_queue:
            if query.query_id == query_id:
                return query.status

        # Check active
        if query_id in self.active_queries:
            return self.active_queries[query_id].status

        # Check completed
        if query_id in self.completed_queries:
            return self.completed_queries[query_id].status

        return None

    def get_query(self, query_id: str) -> Optional[Query]:
        """Get a query by ID.

        Args:
            query_id: Query ID

        Returns:
            Query or None if not found
        """
        # Check queue
        for query in self.query_queue:
            if query.query_id == query_id:
                return query

        # Check active
        if query_id in self.active_queries:
            return self.active_queries[query_id]

        # Check completed
        if query_id in self.completed_queries:
            return self.completed_queries[query_id]

        return None

    def get_active_queries(self) -> list[Query]:
        """Get all active queries.

        Returns:
            List of active queries
        """
        return list(self.active_queries.values())

    def get_pending_queries(self) -> list[Query]:
        """Get all pending queries.

        Returns:
            List of pending queries
        """
        return self.query_queue.copy()

    def get_completed_queries(self, limit: int = 10) -> list[Query]:
        """Get completed queries.

        Args:
            limit: Maximum number to return

        Returns:
            List of completed queries (most recent first)
        """
        queries = list(self.completed_queries.values())
        queries.sort(key=lambda q: q.completed_at or datetime.utcnow(), reverse=True)
        return queries[:limit]

    def get_stats(self) -> dict:
        """Get query manager statistics.

        Returns:
            Statistics dictionary
        """
        return {
            "pending": len(self.query_queue),
            "active": len(self.active_queries),
            "completed": len(self.completed_queries),
            "max_concurrent": self.max_concurrent,
        }

    async def acquire_slot(self):
        """Acquire a concurrency slot.

        Returns:
            Context manager for the slot
        """
        return self.semaphore

    def __repr__(self) -> str:
        stats = self.get_stats()
        return f"<QueryManager(pending={stats['pending']}, active={stats['active']}, completed={stats['completed']})>"
