"""Configuration management for KnowledgeWeaver.

Loads configuration from environment variables and .env files using pydantic.
"""

from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application configuration loaded from environment variables and .env files."""

    # Claude API Configuration
    anthropic_api_key: str
    llm_model: str = "claude-opus-4-7"

    # Research APIs (Optional)
    semantic_scholar_api_key: Optional[str] = None
    crossref_email: Optional[str] = None

    # System Configuration
    concurrent_queries: int = 8
    query_timeout_seconds: int = 300
    log_level: str = "INFO"

    # Storage
    database_path: str = "./knowledgeweaver.db"
    output_dir: str = "./outputs"

    # Development
    debug: bool = False

    class Config:
        """Pydantic configuration."""

        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

    def __init__(self, **data):
        """Initialize settings and create output directory if needed."""
        super().__init__(**data)
        # Create output directory if it doesn't exist
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)


# Global settings instance
settings = Settings()
