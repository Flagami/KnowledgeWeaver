"""Keyword recommender for word cloud UI based on query history."""

import re
from collections import defaultdict
from datetime import datetime, timezone
from typing import Optional

from knowledgeweaver.storage.database import get_db_session
from knowledgeweaver.storage.models import Query
from knowledgeweaver.utils.logger import logger

STOP_WORDS = {
    # Common English
    "the", "and", "for", "are", "but", "not", "you", "all", "can", "had",
    "her", "was", "one", "our", "out", "day", "get", "has", "him", "his",
    "how", "its", "may", "now", "old", "see", "two", "who", "did", "let",
    "put", "say", "she", "too", "use", "that", "this", "with", "have",
    "from", "they", "will", "been", "more", "when", "what", "your", "said",
    "each", "which", "their", "time", "about", "would", "there", "could",
    "other", "into", "than", "then", "some", "these", "also", "just",
    "like", "over", "such", "very", "well", "were", "here", "only",
    # Research-specific noise
    "research", "study", "paper", "analysis", "using", "based", "new",
    "recent", "review", "approach", "method", "methods", "results",
    "data", "model", "models", "system", "systems", "work", "works",
    "show", "shows", "propose", "proposed", "present", "presented",
    "demonstrate", "demonstrates", "evaluate", "evaluated", "performance",
    "novel", "existing", "current", "previous", "different", "various",
    "large", "small", "high", "low", "first", "second", "third",
    "however", "therefore", "thus", "hence", "while", "although",
    "between", "through", "across", "within", "without", "toward",
}

SEED_KEYWORDS = [
    {"word": "machine learning", "weight": 8, "count": 0},
    {"word": "CRISPR", "weight": 7, "count": 0},
    {"word": "quantum computing", "weight": 9, "count": 0},
    {"word": "neural networks", "weight": 8, "count": 0},
    {"word": "climate change", "weight": 7, "count": 0},
    {"word": "protein folding", "weight": 6, "count": 0},
    {"word": "dark matter", "weight": 7, "count": 0},
    {"word": "gene therapy", "weight": 6, "count": 0},
    {"word": "transformer architecture", "weight": 9, "count": 0},
    {"word": "immunotherapy", "weight": 6, "count": 0},
    {"word": "reinforcement learning", "weight": 8, "count": 0},
    {"word": "nanotechnology", "weight": 5, "count": 0},
    {"word": "exoplanets", "weight": 6, "count": 0},
    {"word": "microbiome", "weight": 5, "count": 0},
    {"word": "superconductivity", "weight": 6, "count": 0},
    {"word": "diffusion models", "weight": 8, "count": 0},
    {"word": "epigenetics", "weight": 5, "count": 0},
    {"word": "gravitational waves", "weight": 7, "count": 0},
    {"word": "large language models", "weight": 10, "count": 0},
    {"word": "stem cells", "weight": 5, "count": 0},
]


class KeywordRecommender:
    """Extracts keyword recommendations from query history for a word cloud UI."""

    def get_recommendations(self, limit: int = 40) -> list[dict]:
        """Return keyword recommendations derived from completed query history.

        Each entry has the shape: {"word": str, "weight": int (1-10), "count": int}.
        Falls back to seed keywords when no history is available.

        Args:
            limit: Maximum number of keywords to return.

        Returns:
            List of keyword dicts sorted by weight descending.
        """
        try:
            return self._recommendations_from_db(limit)
        except Exception as exc:
            logger.warning(f"KeywordRecommender DB error, using seeds: {exc}")
            return SEED_KEYWORDS[:limit]

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _recommendations_from_db(self, limit: int) -> list[dict]:
        """Query the DB and compute weighted keyword frequencies."""
        session = get_db_session()
        try:
            queries = (
                session.query(Query)
                .filter(Query.status == "completed")
                .all()
            )
        finally:
            session.close()

        if not queries:
            return SEED_KEYWORDS[:limit]

        now = datetime.now(timezone.utc)
        raw_scores: dict[str, float] = defaultdict(float)
        counts: dict[str, int] = defaultdict(int)

        for q in queries:
            recency_weight = self._recency_weight(q.created_at, now)
            rating_weight = self._rating_weight(q.user_rating)
            combined = recency_weight * rating_weight

            for token in self._tokenize(q.query_text):
                raw_scores[token] += combined
                counts[token] += 1

        if not raw_scores:
            return SEED_KEYWORDS[:limit]

        # Sort by score, take top `limit`
        top = sorted(raw_scores.items(), key=lambda kv: kv[1], reverse=True)[:limit]

        # Normalise scores to 1-10
        max_score = top[0][1] if top else 1.0
        min_score = top[-1][1] if top else 0.0
        score_range = max_score - min_score or 1.0

        result = []
        for word, score in top:
            normalised = 1 + round(9 * (score - min_score) / score_range)
            result.append({"word": word, "weight": normalised, "count": counts[word]})

        return result

    @staticmethod
    def _tokenize(text: Optional[str]) -> list[str]:
        """Extract lowercase alphabetic tokens (3+ chars) excluding stop words."""
        if not text:
            return []
        tokens = re.findall(r'\b[a-zA-Z][a-zA-Z]{2,}\b', text)
        return [t.lower() for t in tokens if t.lower() not in STOP_WORDS]

    @staticmethod
    def _recency_weight(created_at: Optional[datetime], now: datetime) -> float:
        """Return a recency multiplier based on how old the query is."""
        if created_at is None:
            return 1.0
        # Ensure both datetimes are timezone-aware for comparison
        if created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=timezone.utc)
        age_days = (now - created_at).days
        if age_days <= 7:
            return 2.0
        if age_days <= 30:
            return 1.5
        return 1.0

    @staticmethod
    def _rating_weight(user_rating: Optional[float]) -> float:
        """Return a rating multiplier; unrated queries default to 1.0."""
        if user_rating is None:
            return 1.0
        return user_rating / 3.0
