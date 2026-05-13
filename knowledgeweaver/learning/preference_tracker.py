"""User preference tracking and management."""

from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from knowledgeweaver.storage.database import get_db_session
from knowledgeweaver.storage.models import UserPreferences
from knowledgeweaver.utils.logger import logger


class PreferenceTracker:
    """Tracks and manages user preferences."""

    # Default preferences for new users
    DEFAULT_PREFERENCES = {
        "paper_type": "research",  # research, review, preprint
        "depth_level": "medium",  # shallow, medium, deep
        "output_format": "html",  # html, markdown
    }

    def __init__(self):
        """Initialize preference tracker."""
        self.logger = logger

    def get_preferences(self, domain: str) -> dict:
        """Get user preferences for a domain.

        Args:
            domain: Research domain

        Returns:
            Preferences dictionary
        """
        try:
            session = get_db_session()
            prefs = session.query(UserPreferences).filter_by(domain=domain).first()
            session.close()

            if prefs:
                self.logger.debug(f"Retrieved preferences for domain: {domain}")
                return {
                    "domain": prefs.domain,
                    "paper_type": prefs.paper_type,
                    "depth_level": prefs.depth_level,
                    "output_format": prefs.output_format,
                }

            # Return defaults for new domain
            self.logger.debug(f"No preferences found for domain: {domain}, using defaults")
            return {
                "domain": domain,
                **self.DEFAULT_PREFERENCES,
            }

        except Exception as e:
            self.logger.error(f"Error retrieving preferences: {e}")
            return {
                "domain": domain,
                **self.DEFAULT_PREFERENCES,
            }

    def set_preferences(
        self,
        domain: str,
        paper_type: Optional[str] = None,
        depth_level: Optional[str] = None,
        output_format: Optional[str] = None,
    ) -> bool:
        """Set user preferences for a domain.

        Args:
            domain: Research domain
            paper_type: Paper type preference
            depth_level: Synthesis depth preference
            output_format: Output format preference

        Returns:
            True if successful, False otherwise
        """
        try:
            session = get_db_session()

            # Get or create preferences
            prefs = session.query(UserPreferences).filter_by(domain=domain).first()
            if not prefs:
                prefs = UserPreferences(domain=domain)
                session.add(prefs)

            # Update fields
            if paper_type:
                prefs.paper_type = paper_type
            if depth_level:
                prefs.depth_level = depth_level
            if output_format:
                prefs.output_format = output_format

            prefs.updated_at = datetime.utcnow()
            session.commit()
            session.close()

            self.logger.info(f"Updated preferences for domain: {domain}")
            return True

        except Exception as e:
            self.logger.error(f"Error setting preferences: {e}")
            return False

    def update_depth_preference(self, domain: str, new_depth: str) -> bool:
        """Update depth preference for a domain.

        Args:
            domain: Research domain
            new_depth: New depth level

        Returns:
            True if successful, False otherwise
        """
        return self.set_preferences(domain, depth_level=new_depth)

    def update_paper_type_preference(self, domain: str, new_type: str) -> bool:
        """Update paper type preference for a domain.

        Args:
            domain: Research domain
            new_type: New paper type

        Returns:
            True if successful, False otherwise
        """
        return self.set_preferences(domain, paper_type=new_type)

    def get_all_preferences(self) -> list[dict]:
        """Get all user preferences.

        Returns:
            List of preference dictionaries
        """
        try:
            session = get_db_session()
            all_prefs = session.query(UserPreferences).all()
            session.close()

            return [
                {
                    "domain": p.domain,
                    "paper_type": p.paper_type,
                    "depth_level": p.depth_level,
                    "output_format": p.output_format,
                }
                for p in all_prefs
            ]

        except Exception as e:
            self.logger.error(f"Error retrieving all preferences: {e}")
            return []

    def reset_preferences(self, domain: str) -> bool:
        """Reset preferences to defaults for a domain.

        Args:
            domain: Research domain

        Returns:
            True if successful, False otherwise
        """
        return self.set_preferences(
            domain,
            paper_type=self.DEFAULT_PREFERENCES["paper_type"],
            depth_level=self.DEFAULT_PREFERENCES["depth_level"],
            output_format=self.DEFAULT_PREFERENCES["output_format"],
        )
