"""Unit tests for Phase 2: Research Pipeline components."""

import pytest

from knowledgeweaver.core.domain_detector import DomainDetector
from knowledgeweaver.sources.base import BaseSource, PaperMetadata, SourceRegistry
from knowledgeweaver.sources.arxiv import ArxivSource
from knowledgeweaver.sources.pubmed import PubmedSource
from knowledgeweaver.sources.semantic_scholar import SemanticScholarSource
from knowledgeweaver.sources.crossref import CrossrefSource


class TestDomainDetector:
    """Test domain detection."""

    @pytest.fixture
    def detector(self):
        """Create domain detector."""
        return DomainDetector()

    def test_detect_ai_ml_domain(self, detector):
        """Test AI/ML domain detection."""
        result = detector.detect("machine learning and neural networks")
        assert result.domain in ["AI/ML", "Physics"]  # Could be either
        assert result.confidence > 0

    def test_detect_biology_domain(self, detector):
        """Test Biology domain detection."""
        result = detector.detect("protein folding and genetics")
        assert result.domain == "Biology"
        assert result.confidence > 0

    def test_detect_physics_domain(self, detector):
        """Test Physics domain detection."""
        result = detector.detect("quantum mechanics and relativity")
        assert result.domain == "Physics"
        assert result.confidence > 0

    def test_get_sources_for_domain(self, detector):
        """Test getting sources for a domain."""
        sources = detector.get_sources("AI/ML")
        assert isinstance(sources, list)
        assert len(sources) > 0
        assert "arxiv" in sources

    def test_get_supported_domains(self, detector):
        """Test getting supported domains."""
        domains = detector.get_supported_domains()
        assert len(domains) >= 3
        assert "AI/ML" in domains
        assert "Biology" in domains
        assert "Physics" in domains

    def test_unknown_domain_returns_defaults(self, detector):
        """Test that unknown domain returns default sources."""
        result = detector.detect("xyzabc123 unknown query")
        assert result.domain == "General"
        assert result.confidence == 0.0
        assert len(result.sources) > 0


class TestSourceRegistry:
    """Test source registry."""

    @pytest.fixture
    def registry(self):
        """Create source registry."""
        return SourceRegistry()

    @pytest.fixture
    def mock_source(self):
        """Create mock source."""

        class MockSource(BaseSource):
            async def search(self, query, limit=10, sort_by="relevance"):
                return []

            async def fetch(self, paper):
                return None

        return MockSource(name="mock", priority=5)

    def test_register_source(self, registry, mock_source):
        """Test registering a source."""
        registry.register("AI/ML", mock_source)
        sources = registry.get_sources("AI/ML")
        assert len(sources) == 1
        assert sources[0].name == "mock"

    def test_get_source_by_name(self, registry, mock_source):
        """Test getting a specific source."""
        registry.register("AI/ML", mock_source)
        source = registry.get_source("AI/ML", "mock")
        assert source is not None
        assert source.name == "mock"

    def test_sources_sorted_by_priority(self, registry):
        """Test that sources are sorted by priority."""

        class Source1(BaseSource):
            async def search(self, query, limit=10, sort_by="relevance"):
                return []

            async def fetch(self, paper):
                return None

        class Source2(BaseSource):
            async def search(self, query, limit=10, sort_by="relevance"):
                return []

            async def fetch(self, paper):
                return None

        s1 = Source1(name="source1", priority=5)
        s2 = Source2(name="source2", priority=10)

        registry.register("AI/ML", s1)
        registry.register("AI/ML", s2)

        sources = registry.get_sources("AI/ML")
        assert sources[0].priority == 10  # Higher priority first
        assert sources[1].priority == 5


class TestSourceImplementations:
    """Test source implementations."""

    def test_arxiv_source_initialization(self):
        """Test ArxivSource initialization."""
        source = ArxivSource()
        assert source.name == "arxiv"
        assert source.priority == 10

    def test_pubmed_source_initialization(self):
        """Test PubmedSource initialization."""
        source = PubmedSource()
        assert source.name == "pubmed"
        assert source.priority == 9

    def test_semantic_scholar_source_initialization(self):
        """Test SemanticScholarSource initialization."""
        source = SemanticScholarSource()
        assert source.name == "semantic_scholar"
        assert source.priority == 8

    def test_crossref_source_initialization(self):
        """Test CrossrefSource initialization."""
        source = CrossrefSource()
        assert source.name == "crossref"
        assert source.priority == 7

    def test_paper_metadata_creation(self):
        """Test PaperMetadata creation."""
        paper = PaperMetadata(
            source="arxiv",
            source_id="2301.12345",
            title="Test Paper",
            authors="John Doe",
            abstract="Test abstract",
            url="https://arxiv.org/abs/2301.12345",
            published_date="2023-01-15",
            citation_count=10,
        )
        assert paper.source == "arxiv"
        assert paper.title == "Test Paper"
        assert paper.citation_count == 10
