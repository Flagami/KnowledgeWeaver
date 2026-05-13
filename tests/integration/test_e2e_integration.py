"""End-to-end integration tests for the complete KnowledgeWeaver system."""

import asyncio
import tempfile
from pathlib import Path

import pytest

from knowledgeweaver.core.domain_detector import DomainDetector
from knowledgeweaver.core.query_manager import Query, QueryManager
from knowledgeweaver.core.synthesis_pipeline import SynthesisPipeline
from knowledgeweaver.learning.feedback_collector import FeedbackCollector
from knowledgeweaver.learning.preference_tracker import PreferenceTracker
from knowledgeweaver.learning.preference_updater import PreferenceUpdater
from knowledgeweaver.output.html_generator import HTMLGenerator
from knowledgeweaver.processing.insight_generator import GeneratedInsights
from knowledgeweaver.processing.synthesizer import SynthesisResult
from knowledgeweaver.storage.database import init_database
from knowledgeweaver.utils.logger import logger


class TestEndToEndWorkflow:
    """Test complete end-to-end workflows."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup for each test."""
        init_database()
        yield

    def test_domain_detection_workflow(self):
        """Test domain detection workflow."""
        detector = DomainDetector()

        # Test AI/ML query
        result = detector.detect("machine learning and neural networks")
        assert result.domain in ["AI/ML", "Physics"]
        assert result.confidence > 0
        assert len(result.sources) > 0

        # Test Biology query
        result = detector.detect("protein folding and genetics")
        assert result.domain == "Biology"
        assert len(result.sources) > 0

    @pytest.mark.asyncio
    async def test_query_manager_workflow(self):
        """Test query manager workflow."""
        manager = QueryManager(max_concurrent=2)

        # Submit queries
        q1 = await manager.submit_query("query 1", domain="AI/ML")
        q2 = await manager.submit_query("query 2", domain="Biology")

        # Check pending
        pending = manager.get_pending_queries()
        assert len(pending) == 2

        # Process first query
        next_q = await manager.get_next_query()
        assert next_q is not None
        await manager.start_processing(next_q)
        await manager.complete_query(next_q, result_path="/path/to/result.html")

        # Check stats
        stats = manager.get_stats()
        assert stats["completed"] == 1
        assert stats["pending"] == 1

    def test_preference_workflow(self):
        """Test preference tracking workflow."""
        tracker = PreferenceTracker()

        # Get default preferences
        prefs = tracker.get_preferences("AI/ML")
        assert prefs["depth_level"] == "medium"

        # Update preferences
        tracker.set_preferences("AI/ML", depth_level="deep")
        updated_prefs = tracker.get_preferences("AI/ML")
        assert updated_prefs["depth_level"] == "deep"

    def test_feedback_workflow(self):
        """Test feedback collection workflow."""
        collector = FeedbackCollector()

        # Get initial summary
        summary = collector.get_feedback_summary()
        assert summary["total_feedback"] == 0

        # Get analysis
        analysis = collector.analyze_feedback_patterns()
        assert analysis["total_queries"] == 0

    def test_preference_learning_workflow(self):
        """Test preference learning workflow."""
        updater = PreferenceUpdater()

        # Get learning summary
        summary = updater.get_learning_summary("AI/ML")
        assert "domain" in summary
        assert "current_preferences" in summary

        # Get suggestions
        suggestions = updater.suggest_improvements("AI/ML")
        assert isinstance(suggestions, list)

    def test_html_generation_workflow(self):
        """Test HTML generation workflow."""
        generator = HTMLGenerator()

        # Create sample synthesis
        synthesis = SynthesisResult(
            synthesis="Test synthesis",
            insights=["Insight 1", "Insight 2"],
            connections=["Connection 1"],
            citations=["Citation 1"],
        )

        # Create sample insights
        insights = GeneratedInsights(
            insights=["Insight 1"],
            future_directions=["Direction 1"],
            open_questions=["Question 1"],
        )

        # Generate HTML
        html_path = generator.generate(
            query="test query",
            synthesis=synthesis,
            insights=insights,
            domain="AI/ML",
        )

        # Verify HTML was created
        assert Path(html_path).exists()
        assert html_path.endswith(".html")

        # Verify HTML content
        with open(html_path, "r") as f:
            content = f.read()
            assert "test query" in content
            assert "AI/ML" in content
            assert "Insight 1" in content


class TestSystemIntegration:
    """Test system-level integration."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup for each test."""
        init_database()
        yield

    def test_pipeline_initialization(self):
        """Test pipeline initialization."""
        pipeline = SynthesisPipeline()

        assert pipeline.domain_detector is not None
        assert pipeline.source_registry is not None
        assert pipeline.paper_fetcher is not None
        assert pipeline.paper_summarizer is not None
        assert pipeline.paper_synthesizer is not None
        assert pipeline.insight_generator is not None
        assert pipeline.html_generator is not None
        assert pipeline.query_manager is not None

    def test_source_registration(self):
        """Test that all sources are registered."""
        pipeline = SynthesisPipeline()

        all_sources = pipeline.source_registry.get_all_sources()
        assert len(all_sources) > 0

        # Check specific sources
        arxiv = pipeline._get_source("arxiv")
        assert arxiv is not None
        assert arxiv.name == "arxiv"

        pubmed = pipeline._get_source("pubmed")
        assert pubmed is not None
        assert pubmed.name == "pubmed"

    def test_concurrent_query_handling(self):
        """Test handling of concurrent queries."""
        manager = QueryManager(max_concurrent=4)

        # Submit multiple queries
        queries = []
        for i in range(6):
            q = asyncio.run(manager.submit_query(f"query {i}"))
            queries.append(q)

        # Verify all submitted
        assert len(manager.get_pending_queries()) == 6

        # Process some
        for i in range(3):
            q = asyncio.run(manager.get_next_query())
            asyncio.run(manager.start_processing(q))

        # Check active
        active = manager.get_active_queries()
        assert len(active) == 3

    def test_error_recovery(self):
        """Test error recovery in workflows."""
        manager = QueryManager()

        # Create and fail a query
        asyncio.run(
            manager.submit_query("test query")
        )
        q = asyncio.run(manager.get_next_query())
        asyncio.run(manager.start_processing(q))
        asyncio.run(manager.fail_query(q, "Test error"))

        # Verify it's marked as failed
        assert q.status.value == "failed"
        assert q.error_message == "Test error"

        # Verify it's in completed queries
        completed = manager.get_completed_queries()
        assert len(completed) > 0


class TestDataPersistence:
    """Test data persistence across operations."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup for each test."""
        init_database()
        yield

    def test_preference_persistence(self):
        """Test that preferences persist."""
        tracker1 = PreferenceTracker()
        tracker1.set_preferences("TestDomain", depth_level="deep")

        # Create new tracker instance
        tracker2 = PreferenceTracker()
        prefs = tracker2.get_preferences("TestDomain")

        assert prefs["depth_level"] == "deep"

    def test_multiple_domain_preferences(self):
        """Test managing preferences for multiple domains."""
        tracker = PreferenceTracker()

        # Set preferences for multiple domains
        tracker.set_preferences("Domain1", depth_level="shallow")
        tracker.set_preferences("Domain2", depth_level="deep")
        tracker.set_preferences("Domain3", paper_type="review")

        # Retrieve all
        all_prefs = tracker.get_all_preferences()
        assert len(all_prefs) >= 3

        # Verify each
        d1 = tracker.get_preferences("Domain1")
        assert d1["depth_level"] == "shallow"

        d2 = tracker.get_preferences("Domain2")
        assert d2["depth_level"] == "deep"

        d3 = tracker.get_preferences("Domain3")
        assert d3["paper_type"] == "review"
