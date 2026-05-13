"""Database models for KnowledgeWeaver using SQLAlchemy ORM."""

from datetime import datetime
from typing import Optional

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text, create_engine
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

Base = declarative_base()


class UserPreferences(Base):
    """User preferences for research queries."""

    __tablename__ = "user_preferences"

    id = Column(Integer, primary_key=True)
    domain = Column(String(100), nullable=False, unique=True)
    paper_type = Column(String(50), default="research")  # research, review, preprint
    depth_level = Column(String(20), default="medium")  # shallow, medium, deep
    output_format = Column(String(20), default="html")  # html, markdown
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    queries = relationship("Query", back_populates="preferences")

    def __repr__(self) -> str:
        return f"<UserPreferences(domain={self.domain}, depth={self.depth_level})>"


class Query(Base):
    """Research query and its results."""

    __tablename__ = "queries"

    id = Column(Integer, primary_key=True)
    query_text = Column(Text, nullable=False)
    domain = Column(String(100), nullable=False)
    preferences_id = Column(Integer, ForeignKey("user_preferences.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String(20), default="pending")  # pending, processing, completed, failed
    result_path = Column(String(255))  # Path to HTML output
    user_rating = Column(Integer)  # 1-5 stars
    feedback = Column(Text)  # User feedback text
    processing_time_seconds = Column(Float)  # Time taken to process

    # Relationships
    papers = relationship("Paper", back_populates="query", cascade="all, delete-orphan")
    preferences = relationship("UserPreferences", back_populates="queries")

    def __repr__(self) -> str:
        return f"<Query(id={self.id}, query={self.query_text[:50]}, status={self.status})>"


class Paper(Base):
    """Research paper from a source."""

    __tablename__ = "papers"

    id = Column(Integer, primary_key=True)
    query_id = Column(Integer, ForeignKey("queries.id"), nullable=False)
    source = Column(String(50), nullable=False)  # arxiv, pubmed, semantic_scholar, crossref
    source_id = Column(String(255), nullable=False)  # Unique ID from source
    title = Column(Text, nullable=False)
    authors = Column(Text)  # Comma-separated authors
    abstract = Column(Text)
    url = Column(String(500))
    published_date = Column(String(20))  # ISO format date
    citation_count = Column(Integer, default=0)
    fetched_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    query = relationship("Query", back_populates="papers")

    def __repr__(self) -> str:
        return f"<Paper(source={self.source}, title={self.title[:50]})>"


class DatabaseManager:
    """Manages database initialization and session creation."""

    def __init__(self, database_path: str = "./knowledgeweaver.db"):
        """Initialize database manager.

        Args:
            database_path: Path to SQLite database file
        """
        self.database_path = database_path
        self.engine = create_engine(f"sqlite:///{database_path}", echo=False)
        self.SessionLocal = sessionmaker(bind=self.engine)

    def init_db(self) -> None:
        """Create all tables in the database."""
        Base.metadata.create_all(self.engine)

    def get_session(self):
        """Get a new database session."""
        return self.SessionLocal()

    def close(self) -> None:
        """Close database connections."""
        self.engine.dispose()
