"""Preference updater that learns from user feedback."""

from typing import Optional

from knowledgeweaver.learning.feedback_collector import FeedbackCollector
from knowledgeweaver.learning.preference_tracker import PreferenceTracker
from knowledgeweaver.utils.logger import logger


class PreferenceUpdater:
    """Updates user preferences based on feedback and behavior patterns."""

    # Thresholds for preference adjustments
    RATING_THRESHOLD_HIGH = 4  # Ratings >= 4 are considered positive
    RATING_THRESHOLD_LOW = 2  # Ratings <= 2 are considered negative
    MIN_FEEDBACK_SAMPLES = 3  # Minimum feedback samples to make adjustments

    def __init__(self):
        """Initialize preference updater."""
        self.logger = logger
        self.preference_tracker = PreferenceTracker()
        self.feedback_collector = FeedbackCollector()

    def update_preferences_from_feedback(self, domain: str) -> bool:
        """Update preferences for a domain based on feedback.

        Args:
            domain: Research domain

        Returns:
            True if preferences were updated, False otherwise
        """
        try:
            # Get feedback analysis
            analysis = self.feedback_collector.analyze_feedback_patterns(domain)

            if analysis["feedback_rate"] < self.MIN_FEEDBACK_SAMPLES:
                self.logger.debug(
                    f"Not enough feedback samples for {domain}: {analysis['feedback_rate']}"
                )
                return False

            # Get current preferences
            current_prefs = self.preference_tracker.get_preferences(domain)

            # Analyze and update depth preference
            new_depth = self._recommend_depth(analysis, current_prefs)
            if new_depth != current_prefs["depth_level"]:
                self.preference_tracker.update_depth_preference(domain, new_depth)
                self.logger.info(
                    f"Updated depth preference for {domain}: {current_prefs['depth_level']} → {new_depth}"
                )

            # Analyze and update paper type preference
            new_paper_type = self._recommend_paper_type(analysis, current_prefs)
            if new_paper_type != current_prefs["paper_type"]:
                self.preference_tracker.update_paper_type_preference(domain, new_paper_type)
                self.logger.info(
                    f"Updated paper type preference for {domain}: {current_prefs['paper_type']} → {new_paper_type}"
                )

            return True

        except Exception as e:
            self.logger.error(f"Error updating preferences: {e}")
            return False

    def _recommend_depth(self, analysis: dict, current_prefs: dict) -> str:
        """Recommend depth preference based on feedback.

        Args:
            analysis: Feedback analysis
            current_prefs: Current preferences

        Returns:
            Recommended depth level
        """
        avg_rating = analysis.get("average_rating", 0)
        current_depth = current_prefs.get("depth_level", "medium")

        # If average rating is high, user likes current depth
        if avg_rating >= self.RATING_THRESHOLD_HIGH:
            return current_depth

        # If average rating is low, try different depth
        if avg_rating <= self.RATING_THRESHOLD_LOW:
            if current_depth == "shallow":
                return "medium"
            elif current_depth == "medium":
                return "deep"
            else:  # deep
                return "medium"

        # If rating is neutral, keep current
        return current_depth

    def _recommend_paper_type(self, analysis: dict, current_prefs: dict) -> str:
        """Recommend paper type preference based on feedback.

        Args:
            analysis: Feedback analysis
            current_prefs: Current preferences

        Returns:
            Recommended paper type
        """
        avg_rating = analysis.get("average_rating", 0)
        current_type = current_prefs.get("paper_type", "research")

        # If average rating is high, user likes current paper type
        if avg_rating >= self.RATING_THRESHOLD_HIGH:
            return current_type

        # If average rating is low, try different paper type
        if avg_rating <= self.RATING_THRESHOLD_LOW:
            if current_type == "research":
                return "review"
            elif current_type == "review":
                return "preprint"
            else:  # preprint
                return "research"

        # If rating is neutral, keep current
        return current_type

    def get_learning_summary(self, domain: str) -> dict:
        """Get learning summary for a domain.

        Args:
            domain: Research domain

        Returns:
            Learning summary dictionary
        """
        try:
            analysis = self.feedback_collector.analyze_feedback_patterns(domain)
            current_prefs = self.preference_tracker.get_preferences(domain)

            return {
                "domain": domain,
                "current_preferences": current_prefs,
                "feedback_analysis": analysis,
                "recommended_depth": self._recommend_depth(analysis, current_prefs),
                "recommended_paper_type": self._recommend_paper_type(
                    analysis, current_prefs
                ),
            }

        except Exception as e:
            self.logger.error(f"Error generating learning summary: {e}")
            return {
                "domain": domain,
                "error": str(e),
            }

    def get_all_learning_summaries(self) -> list[dict]:
        """Get learning summaries for all domains.

        Returns:
            List of learning summary dictionaries
        """
        try:
            all_prefs = self.preference_tracker.get_all_preferences()
            summaries = []

            for pref in all_prefs:
                domain = pref["domain"]
                summary = self.get_learning_summary(domain)
                summaries.append(summary)

            return summaries

        except Exception as e:
            self.logger.error(f"Error generating all learning summaries: {e}")
            return []

    def suggest_improvements(self, domain: str) -> list[str]:
        """Suggest improvements based on feedback patterns.

        Args:
            domain: Research domain

        Returns:
            List of improvement suggestions
        """
        try:
            suggestions = []
            analysis = self.feedback_collector.analyze_feedback_patterns(domain)

            if analysis["feedback_rate"] == 0:
                suggestions.append("No feedback collected yet. Submit queries to enable learning.")
                return suggestions

            avg_rating = analysis.get("average_rating", 0)

            # Suggest based on average rating
            if avg_rating < 2:
                suggestions.append(
                    "Average rating is low. Consider adjusting synthesis depth or paper type."
                )
            elif avg_rating < 3:
                suggestions.append(
                    "Average rating is below neutral. Try different preferences."
                )
            elif avg_rating >= 4:
                suggestions.append("Great! Current preferences are working well.")

            # Suggest based on rating distribution
            distribution = analysis.get("rating_distribution", {})
            if distribution.get(1, 0) > distribution.get(5, 0):
                suggestions.append("More 1-star ratings than 5-star. Consider changing approach.")
            elif distribution.get(5, 0) > distribution.get(1, 0):
                suggestions.append("Excellent! More 5-star ratings than 1-star.")

            # Suggest based on feedback volume
            if analysis["feedback_rate"] < 5:
                suggestions.append(
                    f"Collect more feedback ({analysis['feedback_rate']}/5 samples) for better learning."
                )

            return suggestions

        except Exception as e:
            self.logger.error(f"Error generating suggestions: {e}")
            return ["Unable to generate suggestions at this time."]
