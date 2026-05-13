"""Unit tests for Phase 5: User Learning components."""

import pytest

from knowledgeweaver.learning.feedback_collector import FeedbackCollector
from knowledgeweaver.learning.preference_tracker import PreferenceTracker
from knowledgeweaver.learning.preference_updater import PreferenceUpdater


class TestPreferenceTracker:
    """Test preference tracker."""

    @pytest.fixture
    def tracker(self):
        """Create preference tracker."""
        return PreferenceTracker()

    def test_get_default_preferences(self, tracker):
        """Test getting default preferences for new domain."""
        prefs = tracker.get_preferences("NewDomain")
        assert prefs["domain"] == "NewDomain"
        assert prefs["paper_type"] == "research"
        assert prefs["depth_level"] == "medium"
        assert prefs["output_format"] == "html"

    def test_set_preferences(self, tracker):
        """Test setting preferences."""
        success = tracker.set_preferences(
            "AI/ML",
            paper_type="review",
            depth_level="deep",
        )
        assert success is True

    def test_update_depth_preference(self, tracker):
        """Test updating depth preference."""
        success = tracker.update_depth_preference("AI/ML", "shallow")
        assert success is True

    def test_update_paper_type_preference(self, tracker):
        """Test updating paper type preference."""
        success = tracker.update_paper_type_preference("AI/ML", "preprint")
        assert success is True

    def test_get_all_preferences(self, tracker):
        """Test getting all preferences."""
        tracker.set_preferences("Domain1", depth_level="shallow")
        tracker.set_preferences("Domain2", depth_level="deep")

        all_prefs = tracker.get_all_preferences()
        assert len(all_prefs) >= 2

    def test_reset_preferences(self, tracker):
        """Test resetting preferences to defaults."""
        tracker.set_preferences("AI/ML", depth_level="deep")
        success = tracker.reset_preferences("AI/ML")
        assert success is True

        prefs = tracker.get_preferences("AI/ML")
        assert prefs["depth_level"] == "medium"


class TestFeedbackCollector:
    """Test feedback collector."""

    @pytest.fixture
    def collector(self):
        """Create feedback collector."""
        return FeedbackCollector()

    def test_get_average_rating_no_feedback(self, collector):
        """Test average rating with no feedback."""
        avg = collector.get_average_rating()
        assert avg is None or avg >= 0

    def test_get_feedback_summary(self, collector):
        """Test feedback summary."""
        summary = collector.get_feedback_summary()
        assert "total_feedback" in summary
        assert "average_rating" in summary
        assert "rating_distribution" in summary

    def test_get_low_rated_queries(self, collector):
        """Test getting low-rated queries."""
        queries = collector.get_low_rated_queries()
        assert isinstance(queries, list)

    def test_get_high_rated_queries(self, collector):
        """Test getting high-rated queries."""
        queries = collector.get_high_rated_queries()
        assert isinstance(queries, list)

    def test_analyze_feedback_patterns(self, collector):
        """Test analyzing feedback patterns."""
        analysis = collector.analyze_feedback_patterns()
        assert "total_queries" in analysis
        assert "feedback_rate" in analysis
        assert "average_rating" in analysis


class TestPreferenceUpdater:
    """Test preference updater."""

    @pytest.fixture
    def updater(self):
        """Create preference updater."""
        return PreferenceUpdater()

    def test_recommend_depth_high_rating(self, updater):
        """Test depth recommendation with high rating."""
        analysis = {
            "average_rating": 4.5,
            "feedback_rate": 5,
        }
        current_prefs = {"depth_level": "medium"}

        depth = updater._recommend_depth(analysis, current_prefs)
        assert depth == "medium"  # Keep current if rating is high

    def test_recommend_depth_low_rating(self, updater):
        """Test depth recommendation with low rating."""
        analysis = {
            "average_rating": 1.5,
            "feedback_rate": 5,
        }
        current_prefs = {"depth_level": "medium"}

        depth = updater._recommend_depth(analysis, current_prefs)
        assert depth in ["shallow", "deep"]  # Change if rating is low

    def test_recommend_paper_type_high_rating(self, updater):
        """Test paper type recommendation with high rating."""
        analysis = {
            "average_rating": 4.5,
            "feedback_rate": 5,
        }
        current_prefs = {"paper_type": "research"}

        paper_type = updater._recommend_paper_type(analysis, current_prefs)
        assert paper_type == "research"  # Keep current if rating is high

    def test_recommend_paper_type_low_rating(self, updater):
        """Test paper type recommendation with low rating."""
        analysis = {
            "average_rating": 1.5,
            "feedback_rate": 5,
        }
        current_prefs = {"paper_type": "research"}

        paper_type = updater._recommend_paper_type(analysis, current_prefs)
        assert paper_type in ["review", "preprint"]  # Change if rating is low

    def test_get_learning_summary(self, updater):
        """Test getting learning summary."""
        summary = updater.get_learning_summary("AI/ML")
        assert "domain" in summary
        assert "current_preferences" in summary
        assert "feedback_analysis" in summary

    def test_get_all_learning_summaries(self, updater):
        """Test getting all learning summaries."""
        summaries = updater.get_all_learning_summaries()
        assert isinstance(summaries, list)

    def test_suggest_improvements(self, updater):
        """Test suggesting improvements."""
        suggestions = updater.suggest_improvements("AI/ML")
        assert isinstance(suggestions, list)
        assert len(suggestions) > 0
