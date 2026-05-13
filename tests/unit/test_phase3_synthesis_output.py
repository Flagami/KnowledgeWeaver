"""Unit tests for Phase 3: Synthesis & Output components."""

import pytest

from knowledgeweaver.output.html_generator import HTMLGenerator
from knowledgeweaver.processing.insight_generator import GeneratedInsights
from knowledgeweaver.processing.summarizer import PaperSummary
from knowledgeweaver.processing.synthesizer import SynthesisResult
from knowledgeweaver.sources.base import PaperMetadata


class TestPaperSummary:
    """Test paper summary data structure."""

    def test_paper_summary_creation(self):
        """Test creating a paper summary."""
        summary = PaperSummary(
            title="Test Paper",
            authors="John Doe",
            summary="This is a test summary",
            key_points=["Point 1", "Point 2"],
            citations=["Citation 1"],
        )
        assert summary.title == "Test Paper"
        assert len(summary.key_points) == 2


class TestSynthesisResult:
    """Test synthesis result data structure."""

    def test_synthesis_result_creation(self):
        """Test creating a synthesis result."""
        result = SynthesisResult(
            synthesis="Synthesis text",
            insights=["Insight 1", "Insight 2"],
            connections=["Connection 1"],
            citations=["Citation 1"],
        )
        assert result.synthesis == "Synthesis text"
        assert len(result.insights) == 2


class TestGeneratedInsights:
    """Test generated insights data structure."""

    def test_generated_insights_creation(self):
        """Test creating generated insights."""
        insights = GeneratedInsights(
            insights=["Insight 1"],
            future_directions=["Direction 1"],
            open_questions=["Question 1"],
        )
        assert len(insights.insights) == 1
        assert len(insights.future_directions) == 1
        assert len(insights.open_questions) == 1


class TestHTMLGenerator:
    """Test HTML generation."""

    @pytest.fixture
    def generator(self):
        """Create HTML generator."""
        return HTMLGenerator()

    @pytest.fixture
    def sample_synthesis(self):
        """Create sample synthesis result."""
        return SynthesisResult(
            synthesis="This is a test synthesis of multiple papers.",
            insights=["Key insight 1", "Key insight 2"],
            connections=["Papers A and B both discuss X"],
            citations=["Smith et al. 2023", "Jones et al. 2022"],
        )

    @pytest.fixture
    def sample_insights(self):
        """Create sample insights."""
        return GeneratedInsights(
            insights=["Actionable insight 1", "Actionable insight 2"],
            future_directions=["Research direction 1"],
            open_questions=["What about X?"],
        )

    def test_html_generation(self, generator, sample_synthesis, sample_insights):
        """Test HTML generation."""
        html_path = generator.generate(
            query="test query",
            synthesis=sample_synthesis,
            insights=sample_insights,
            domain="AI/ML",
        )
        assert html_path is not None
        assert html_path.endswith(".html")

    def test_generated_html_contains_content(self, generator, sample_synthesis, sample_insights):
        """Test that generated HTML contains expected content."""
        html_path = generator.generate(
            query="machine learning",
            synthesis=sample_synthesis,
            insights=sample_insights,
            domain="AI/ML",
        )

        # Read the generated HTML
        with open(html_path, "r") as f:
            html_content = f.read()

        # Check for key content
        assert "machine learning" in html_content
        assert "AI/ML" in html_content
        assert "Key Insights" in html_content
        assert "Synthesis" in html_content

    def test_html_contains_rating_widget(self, generator, sample_synthesis, sample_insights):
        """Test that HTML contains rating widget."""
        html_path = generator.generate(
            query="test",
            synthesis=sample_synthesis,
            insights=sample_insights,
        )

        with open(html_path, "r") as f:
            html_content = f.read()

        assert "rating-widget" in html_content
        assert "Was this helpful?" in html_content
        assert "Submit Rating" in html_content

    def test_html_contains_javascript(self, generator, sample_synthesis, sample_insights):
        """Test that HTML contains JavaScript for interactivity."""
        html_path = generator.generate(
            query="test",
            synthesis=sample_synthesis,
            insights=sample_insights,
        )

        with open(html_path, "r") as f:
            html_content = f.read()

        assert "toggleSection" in html_content
        assert "submitRating" in html_content
        assert "currentRating" in html_content

    def test_html_is_responsive(self, generator, sample_synthesis, sample_insights):
        """Test that HTML includes responsive design."""
        html_path = generator.generate(
            query="test",
            synthesis=sample_synthesis,
            insights=sample_insights,
        )

        with open(html_path, "r") as f:
            html_content = f.read()

        assert "viewport" in html_content
        assert "@media" in html_content
        assert "max-width: 768px" in html_content
