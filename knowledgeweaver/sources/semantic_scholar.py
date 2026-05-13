"""Semantic Scholar research source integration."""

from typing import Optional

import httpx

from knowledgeweaver.sources.base import BaseSource, PaperMetadata
from knowledgeweaver.utils.errors import SourceError


class SemanticScholarSource(BaseSource):
    """Semantic Scholar research paper source."""

    BASE_URL = "https://api.semanticscholar.org/graph/v1/paper/search"

    def __init__(self):
        """Initialize Semantic Scholar source."""
        super().__init__(name="semantic_scholar", priority=8)
        self.client = httpx.AsyncClient(timeout=30.0)

    async def search(
        self,
        query: str,
        limit: int = 10,
        sort_by: str = "relevance",
    ) -> list[PaperMetadata]:
        """Search Semantic Scholar for papers.

        Args:
            query: Search query
            limit: Maximum number of results
            sort_by: Sort order ('relevance', 'date')

        Returns:
            List of paper metadata
        """
        try:
            params = {
                "query": query,
                "limit": limit,
                "fields": "paperId,title,authors,abstract,url,publicationDate,citationCount",
            }

            if sort_by == "date":
                params["sort"] = "publication_date:desc"
            else:
                params["sort"] = "relevance"

            response = await self.client.get(self.BASE_URL, params=params)
            response.raise_for_status()

            data = response.json()
            papers = self._parse_semantic_scholar_response(data)
            self.logger.info(
                f"Found {len(papers)} papers on Semantic Scholar for query: {query}"
            )
            return papers

        except httpx.HTTPError as e:
            self.logger.error(f"Semantic Scholar API error: {e}")
            raise SourceError(f"Semantic Scholar search failed: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error searching Semantic Scholar: {e}")
            raise SourceError(f"Unexpected error: {e}")

    async def fetch(self, paper: PaperMetadata) -> Optional[str]:
        """Fetch paper from Semantic Scholar (returns abstract).

        Args:
            paper: Paper metadata

        Returns:
            Paper abstract or None
        """
        return paper.abstract

    def _parse_semantic_scholar_response(self, data: dict) -> list[PaperMetadata]:
        """Parse Semantic Scholar API response.

        Args:
            data: JSON response from Semantic Scholar API

        Returns:
            List of paper metadata
        """
        papers = []

        for paper_data in data.get("data", []):
            try:
                title = paper_data.get("title", "")
                authors = ", ".join(
                    [author.get("name", "") for author in paper_data.get("authors", [])]
                )
                abstract = paper_data.get("abstract", "")
                url = paper_data.get("url", "")
                published_date = paper_data.get("publicationDate", "")
                citation_count = paper_data.get("citationCount", 0)
                paper_id = paper_data.get("paperId", "")

                if not title or not paper_id:
                    continue

                paper = PaperMetadata(
                    source="semantic_scholar",
                    source_id=paper_id,
                    title=title,
                    authors=authors,
                    abstract=abstract,
                    url=url or f"https://www.semanticscholar.org/paper/{paper_id}",
                    published_date=published_date,
                    citation_count=citation_count,
                )
                papers.append(paper)

            except Exception as e:
                self.logger.debug(f"Error parsing Semantic Scholar paper: {e}")
                continue

        return papers
