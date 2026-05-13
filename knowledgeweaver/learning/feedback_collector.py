"""User feedback collection and analysis."""

from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from knowledgeweaver.storage.database import get_db_session
from knowledgeweaver.storage.models import Query
from knowledgeweaver.utils.logger import logger


class FeedbackCollector:
    """Collects and analyzes user feedback on synthesis results."""

    def __init__(self):
        """Initialize feedback collector."""
        self.logger = logger

    def submit_feedback(
        self,
        query_id: str,
        rating: int,
        feedback_text: Optional[str] = None,
    ) -> bool:
        """Submit feedback for a query result.

        Args:
            query_id: Query ID
            rating: Rating (1-5 stars)
            feedback_text: Optional feedback text

        Returns:
            True if successful, False otherwise
        """
        try:
            if not 1 <= rating <= 5:
                self.logger.warning(f"Invalid rating: {rating}")
                return False

            session = get_db_session()
            query = session.query(Query).filter_by(id=query_id).first()

            if not query:
                self.logger.warning(f"Query not found: {query_id}")
                session.close()
                return False

            query.user_rating = rating
            query.feedback = feedback_text
            session.commit()
            session.close()

            self.logger.info(
                f"Feedback submitted for query {query_id}: rating={rating}"
            )
            return True

        except Exception as e:
            self.logger.error(f"Error submitting feedback: {e}")
            return False

    def get_feedback(self, query_id: str) -> Optional[dict]:
        """Get feedback for a query.

        Args:
            query_id: Query ID

        Returns:
            Feedback dictionary or None if not found
        """
        try:
            session = get_db_session()
            query = session.query(Query).filter_by(id=query_id).first()
            session.close()

            if not query or query.user_rating is None:
                return None

            return {
                "query_id": query_id,
                "rating": query.user_rating,
                "feedback": query.feedback,
            }

        except Exception as e:
            self.logger.error(f"Error retrieving feedback: {e}")
            return None

    def get_average_rating(self, domain: Optional[str] = None) -> Optional[float]:
        """Get average rating for queries.

        Args:
            domain: Optional domain filter

        Returns:
            Average rating or None if no ratings found
        """
        try:
            session = get_db_session()
            query = session.query(Query).filter(Query.user_rating.isnot(None))

            if domain:
                query = query.filter_by(domain=domain)

            ratings = [q.user_rating for q in query.all()]
            session.close()

            if not ratings:
                return None

            return sum(ratings) / len(ratings)

        except Exception as e:
            self.logger.error(f"Error calculating average rating: {e}")
            return None

    def get_feedback_summary(self, domain: Optional[str] = None) -> dict:
        """Get feedback summary statistics.

        Args:
            domain: Optional domain filter

        Returns:
            Summary dictionary
        """
        try:
            session = get_db_session()
            query = session.query(Query).filter(Query.user_rating.isnot(None))

            if domain:
                query = query.filter_by(domain=domain)

            queries = query.all()
            session.close()

            if not queries:
                return {
                    "total_feedback": 0,
                    "average_rating": 0,
                    "rating_distribution": {},
                }

            ratings = [q.user_rating for q in queries]
            distribution = {}
            for rating in range(1, 6):
                distribution[rating] = ratings.count(rating)

            return {
                "total_feedback": len(queries),
                "average_rating": sum(ratings) / len(ratings),
                "rating_distribution": distribution,
            }

        except Exception as e:
            self.logger.error(f"Error generating feedback summary: {e}")
            return {
                "total_feedback": 0,
                "average_rating": 0,
                "rating_distribution": {},
            }

    def get_low_rated_queries(self, threshold: int = 2, limit: int = 10) -> list[dict]:
        """Get queries with low ratings.

        Args:
            threshold: Rating threshold (queries with rating <= threshold)
            limit: Maximum number to return

        Returns:
            List of low-rated queries
        """
        try:
            session = get_db_session()
            queries = (
                session.query(Query)
                .filter(Query.user_rating.isnot(None))
                .filter(Query.user_rating <= threshold)
                .order_by(Query.user_rating.asc())
                .limit(limit)
                .all()
            )
            session.close()

            return [
                {
                    "query_id": q.id,
                    "query_text": q.query_text,
                    "domain": q.domain,
                    "rating": q.user_rating,
                    "feedback": q.feedback,
                }
                for q in queries
            ]

        except Exception as e:
            self.logger.error(f"Error retrieving low-rated queries: {e}")
            return []

    def get_high_rated_queries(self, threshold: int = 4, limit: int = 10) -> list[dict]:
        """Get queries with high ratings.

        Args:
            threshold: Rating threshold (queries with rating >= threshold)
            limit: Maximum number to return

        Returns:
            List of high-rated queries
        """
        try:
            session = get_db_session()
            queries = (
                session.query(Query)
                .filter(Query.user_rating.isnot(None))
                .filter(Query.user_rating >= threshold)
                .order_by(Query.user_rating.desc())
                .limit(limit)
                .all()
            )
            session.close()

            return [
                {
                    "query_id": q.id,
                    "query_text": q.query_text,
                    "domain": q.domain,
                    "rating": q.user_rating,
                    "feedback": q.feedback,
                }
                for q in queries
            ]

        except Exception as e:
            self.logger.error(f"Error retrieving high-rated queries: {e}")
            return []

    def analyze_feedback_patterns(self, domain: Optional[str] = None) -> dict:
        """Analyze patterns in user feedback.

        Args:
            domain: Optional domain filter

        Returns:
            Analysis dictionary
        """
        try:
            session = get_db_session()
            query = session.query(Query).filter(Query.user_rating.isnot(None))

            if domain:
                query = query.filter_by(domain=domain)

            queries = query.all()
            session.close()

            if not queries:
                return {
                    "total_queries": 0,
                    "feedback_rate": 0,
                    "average_rating": 0,
                    "most_common_rating": None,
                }

            ratings = [q.user_rating for q in queries]
            rating_counts = {}
            for rating in ratings:
                rating_counts[rating] = rating_counts.get(rating, 0) + 1

            most_common = max(rating_counts, key=rating_counts.get)

            return {
                "total_queries": len(queries),
                "feedback_rate": len(queries),
                "average_rating": sum(ratings) / len(ratings),
                "most_common_rating": most_common,
                "rating_distribution": rating_counts,
            }

        except Exception as e:
            self.logger.error(f"Error analyzing feedback patterns: {e}")
            return {
                "total_queries": 0,
                "feedback_rate": 0,
                "average_rating": 0,
                "most_common_rating": None,
            }
