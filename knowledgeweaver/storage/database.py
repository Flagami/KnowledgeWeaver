"""Database initialization and management."""

from knowledgeweaver.config import settings
from knowledgeweaver.storage.models import DatabaseManager

# Global database manager instance
db_manager = DatabaseManager(database_path=settings.database_path)


def init_database() -> None:
    """Initialize the database with all tables."""
    db_manager.init_db()


def get_db_session():
    """Get a new database session."""
    return db_manager.get_session()
