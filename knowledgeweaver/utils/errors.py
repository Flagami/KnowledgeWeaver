"""Custom exceptions for KnowledgeWeaver."""


class ResearchAgentError(Exception):
    """Base exception for all KnowledgeWeaver errors."""

    pass


class SourceError(ResearchAgentError):
    """Raised when a research source fails."""

    pass


class SynthesisError(ResearchAgentError):
    """Raised when synthesis pipeline fails."""

    pass


class StorageError(ResearchAgentError):
    """Raised when database operations fail."""

    pass


class ConfigError(ResearchAgentError):
    """Raised when configuration is invalid."""

    pass


class FetchError(ResearchAgentError):
    """Raised when paper fetching fails."""

    pass


class ExtractionError(ResearchAgentError):
    """Raised when key findings extraction fails."""

    pass
