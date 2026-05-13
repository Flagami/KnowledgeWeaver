"""Unit tests for Phase 4: TUI Interface components."""

import pytest

from knowledgeweaver.core.query_manager import Query, QueryManager, QueryStatus
from knowledgeweaver.core.synthesis_pipeline import SynthesisPipeline


class TestQueryStatus:
    """Test query status enumeration."""

    def test_query_status_values(self):
        """Test query status values."""
        assert QueryStatus.PENDING.value == "pending"
        assert QueryStatus.PROCESSING.value == "processing"
        assert QueryStatus.COMPLETED.value == "completed"
        assert QueryStatus.FAILED.value == "failed"
        assert QueryStatus.CANCELLED.value == "cancelled"


class TestQuery:
    """Test Query data structure."""

    def test_query_creation(self):
        """Test creating a query."""
        query = Query(query_text="test query", domain="AI/ML")
        assert query.query_text == "test query"
        assert query.domain == "AI/ML"
        assert query.status == QueryStatus.PENDING
        assert query.query_id is not None

    def test_query_unique_ids(self):
        """Test that queries have unique IDs."""
        q1 = Query(query_text="query 1")
        q2 = Query(query_text="query 2")
        assert q1.query_id != q2.query_id


class TestQueryManager:
    """Test query manager."""

    @pytest.fixture
    def manager(self):
        """Create query manager."""
        return QueryManager(max_concurrent=4)

    @pytest.mark.asyncio
    async def test_submit_query(self, manager):
        """Test submitting a query."""
        query = await manager.submit_query("test query", domain="AI/ML")
        assert query.query_text == "test query"
        assert query.domain == "AI/ML"
        assert query.status == QueryStatus.PENDING

    @pytest.mark.asyncio
    async def test_get_next_query(self, manager):
        """Test getting next query from queue."""
        await manager.submit_query("query 1")
        await manager.submit_query("query 2")

        next_query = await manager.get_next_query()
        assert next_query is not None
        assert next_query.query_text == "query 1"

    @pytest.mark.asyncio
    async def test_start_processing(self, manager):
        """Test starting query processing."""
        query = await manager.submit_query("test query")
        await manager.start_processing(query)

        assert query.status == QueryStatus.PROCESSING
        assert query.started_at is not None
        assert query.query_id in manager.active_queries

    @pytest.mark.asyncio
    async def test_complete_query(self, manager):
        """Test completing a query."""
        query = await manager.submit_query("test query")
        await manager.start_processing(query)
        await manager.complete_query(query, result_path="/path/to/result.html")

        assert query.status == QueryStatus.COMPLETED
        assert query.completed_at is not None
        assert query.result_path == "/path/to/result.html"
        assert query.processing_time_seconds > 0

    @pytest.mark.asyncio
    async def test_fail_query(self, manager):
        """Test failing a query."""
        query = await manager.submit_query("test query")
        await manager.start_processing(query)
        await manager.fail_query(query, "Test error")

        assert query.status == QueryStatus.FAILED
        assert query.error_message == "Test error"
        assert query.completed_at is not None

    @pytest.mark.asyncio
    async def test_cancel_query(self, manager):
        """Test cancelling a query."""
        query = await manager.submit_query("test query")
        cancelled = await manager.cancel_query(query.query_id)

        assert cancelled is True
        assert query.status == QueryStatus.CANCELLED

    @pytest.mark.asyncio
    async def test_get_query_status(self, manager):
        """Test getting query status."""
        query = await manager.submit_query("test query")
        status = manager.get_query_status(query.query_id)

        assert status == QueryStatus.PENDING

    @pytest.mark.asyncio
    async def test_get_query(self, manager):
        """Test getting a query by ID."""
        query = await manager.submit_query("test query")
        retrieved = manager.get_query(query.query_id)

        assert retrieved is not None
        assert retrieved.query_id == query.query_id

    @pytest.mark.asyncio
    async def test_get_active_queries(self, manager):
        """Test getting active queries."""
        query = await manager.submit_query("test query")
        await manager.start_processing(query)

        active = manager.get_active_queries()
        assert len(active) == 1
        assert active[0].query_id == query.query_id

    @pytest.mark.asyncio
    async def test_get_pending_queries(self, manager):
        """Test getting pending queries."""
        await manager.submit_query("query 1")
        await manager.submit_query("query 2")

        pending = manager.get_pending_queries()
        assert len(pending) == 2

    @pytest.mark.asyncio
    async def test_get_completed_queries(self, manager):
        """Test getting completed queries."""
        query = await manager.submit_query("test query")
        await manager.start_processing(query)
        await manager.complete_query(query)

        completed = manager.get_completed_queries()
        assert len(completed) == 1

    @pytest.mark.asyncio
    async def test_get_stats(self, manager):
        """Test getting manager statistics."""
        await manager.submit_query("query 1")
        await manager.submit_query("query 2")

        stats = manager.get_stats()
        assert stats["pending"] == 2
        assert stats["active"] == 0
        assert stats["completed"] == 0
        assert stats["max_concurrent"] == 4


class TestSynthesisPipeline:
    """Test synthesis pipeline."""

    @pytest.fixture
    def pipeline(self):
        """Create synthesis pipeline."""
        return SynthesisPipeline()

    def test_pipeline_initialization(self, pipeline):
        """Test pipeline initialization."""
        assert pipeline.domain_detector is not None
        assert pipeline.source_registry is not None
        assert pipeline.paper_fetcher is not None
        assert pipeline.paper_summarizer is not None
        assert pipeline.paper_synthesizer is not None
        assert pipeline.insight_generator is not None
        assert pipeline.html_generator is not None

    def test_pipeline_sources_registered(self, pipeline):
        """Test that sources are registered."""
        all_sources = pipeline.source_registry.get_all_sources()
        assert len(all_sources) > 0
        assert "AI/ML" in all_sources or "Biology" in all_sources

    def test_get_source(self, pipeline):
        """Test getting a source."""
        source = pipeline._get_source("arxiv")
        assert source is not None
        assert source.name == "arxiv"

    def test_get_nonexistent_source(self, pipeline):
        """Test getting a nonexistent source."""
        source = pipeline._get_source("nonexistent")
        assert source is None
