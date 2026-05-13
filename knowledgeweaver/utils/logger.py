"""Logging configuration for KnowledgeWeaver."""

import logging
import logging.handlers
from pathlib import Path

from knowledgeweaver.config import settings


def setup_logging() -> logging.Logger:
    """Set up logging configuration for the application.

    Returns:
        Configured logger instance
    """
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    # Create logger
    logger = logging.getLogger("knowledgeweaver")
    logger.setLevel(getattr(logging, settings.log_level))

    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()

    # Create formatters
    detailed_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    simple_formatter = logging.Formatter(
        "%(levelname)s - %(message)s",
    )

    # Console handler (simple format)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, settings.log_level))
    console_handler.setFormatter(simple_formatter)
    logger.addHandler(console_handler)

    # File handler (detailed format)
    file_handler = logging.handlers.RotatingFileHandler(
        log_dir / "knowledgeweaver.log",
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(detailed_formatter)
    logger.addHandler(file_handler)

    return logger


# Global logger instance
logger = setup_logging()
