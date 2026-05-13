"""Base source interface and registry for research sources."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

from knowledgeweaver.utils.logger import logger


@dataclass
class PaperMetadata:
    """Metadata for a research paper."""

    source: str
    source_id: str
    title: str
    authors: str
    abstract: str
    url: str
    published_date: str
    citation_count: int = 0


class BaseSource(ABC):
    """Abstract base class for research sources."""

    def __init__(self, name: str, priority: int = 0):
        """Initialize source.

        Args:
            name: Source name (e.g., 'arxiv', 'pubmed')
            priority: Priority weight (higher = more important)
        """
        self.name = name
        self.priority = priority
        self.logger = logger

    @abstractmethod
    async def search(
        self,
        query: str,
        limit: int = 10,
        sort_by: str = "relevance",
    ) -> list[PaperMetadata]:
        """Search for papers in this source.

        Args:
            query: Search query
            limit: Maximum number of results
            sort_by: Sort order ('relevance', 'date', 'citations')

        Returns:
            List of paper metadata
        """
        pass

    @abstractmethod
    async def fetch(self, paper: PaperMetadata) -> Optional[str]:
        """Fetch full text of a paper.

        Args:
            paper: Paper metadata

        Returns:
            Full text content or None if unavailable
        """
        pass

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(name={self.name}, priority={self.priority})>"


class SourceRegistry:
    """Registry mapping domains to research sources."""

    def __init__(self):
        """Initialize source registry."""
        self.sources: dict[str, list[BaseSource]] = {}
        self.logger = logger

    def register(self, domain: str, source: BaseSource) -> None:
        """Register a source for a domain.

        Args:
            domain: Domain name
            source: Source instance
        """
        if domain not in self.sources:
            self.sources[domain] = []

        self.sources[domain].append(source)
        # Sort by priority (highest first)
        self.sources[domain].sort(key=lambda s: s.priority, reverse=True)

        self.logger.debug(f"Registered {source.name} for domain {domain}")

    def get_sources(self, domain: str) -> list[BaseSource]:
        """Get sources for a domain, sorted by priority.

        Args:
            domain: Domain name

        Returns:
            List of sources in priority order
        """
        return self.sources.get(domain, [])

    def get_source(self, domain: str, source_name: str) -> Optional[BaseSource]:
        """Get a specific source for a domain.

        Args:
            domain: Domain name
            source_name: Source name

        Returns:
            Source instance or None if not found
        """
        sources = self.get_sources(domain)
        for source in sources:
            if source.name == source_name:
                return source
        return None

    def get_all_sources(self) -> dict[str, list[BaseSource]]:
        """Get all registered sources.

        Returns:
            Dictionary mapping domains to source lists
        """
        return self.sources

    def __repr__(self) -> str:
        total_sources = sum(len(sources) for sources in self.sources.values())
        return f"<SourceRegistry(domains={len(self.sources)}, sources={total_sources})>"


# Global registry instance
source_registry = SourceRegistry()
