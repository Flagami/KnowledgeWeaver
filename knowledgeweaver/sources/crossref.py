"""CrossRef research source integration."""

from typing import Optional

import httpx

from knowledgeweaver.sources.base import BaseSource, PaperMetadata
from knowledgeweaver.utils.errors import SourceError


class CrossrefSource(BaseSource):
    """CrossRef research paper source."""

    BASE_URL = "https://api.crossref.org/v1/works"

    def __init__(self):
        """Initialize CrossRef source."""
        super().__init__(name="crossref", priority=7)
        self.client = httpx.AsyncClient(timeout=30.0)

    async def search(
        self,
        query: str,
        limit: int = 10,
        sort_by: str = "relevance",
    ) -> list[PaperMetadata]:
        """Search CrossRef for papers.

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
                "rows": limit,
                "select": "DOI,title,author,abstract,published-online,is-referenced-by-count",
            }

            if sort_by == "date":
                params["sort"] = "published"
                params["order"] = "desc"
            else:
                params["sort"] = "relevance"

            self.logger.debug(f"CrossRef search | query='{query}' | limit={limit}")
            response = await self.client.get(self.BASE_URL, params=params)
            self.logger.debug(f"CrossRef HTTP {response.status_code} | query='{query}'")
            response.raise_for_status()

            data = response.json()
            papers = self._parse_crossref_response(data)
            self.logger.info(f"CrossRef: {len(papers)} papers found | query='{query}'")
            return papers

        except httpx.HTTPError as e:
            self.logger.error(f"CrossRef API error | query='{query}' | {type(e).__name__}: {e}")
            raise SourceError(f"CrossRef search failed: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error searching CrossRef | query='{query}' | {type(e).__name__}: {e}")
            raise SourceError(f"Unexpected error: {e}")

    async def fetch(self, paper: PaperMetadata) -> Optional[str]:
        """Fetch paper from CrossRef (returns abstract).

        Args:
            paper: Paper metadata

        Returns:
            Paper abstract or None
        """
        return paper.abstract

    def _parse_crossref_response(self, data: dict) -> list[PaperMetadata]:
        """Parse CrossRef API response.

        Args:
            data: JSON response from CrossRef API

        Returns:
            List of paper metadata
        """
        papers = []

        for item in data.get("message", {}).get("items", []):
            try:
                title = item.get("title", [""])[0] if item.get("title") else ""
                authors = ", ".join(
                    [
                        f"{author.get('given', '')} {author.get('family', '')}"
                        for author in item.get("author", [])[:5]
                    ]
                ).strip()

                abstract = item.get("abstract", "")
                doi = item.get("DOI", "")
                published_date = ""

                # Try to get publication date
                if item.get("published-online"):
                    date_parts = item["published-online"].get("date-parts", [[]])[0]
                    if date_parts:
                        published_date = f"{date_parts[0]:04d}-{date_parts[1]:02d}-{date_parts[2]:02d}" if len(date_parts) >= 3 else f"{date_parts[0]:04d}-{date_parts[1]:02d}-01" if len(date_parts) >= 2 else f"{date_parts[0]:04d}-01-01"

                citation_count = item.get("is-referenced-by-count", 0)

                if not title or not doi:
                    continue

                paper = PaperMetadata(
                    source="crossref",
                    source_id=doi,
                    title=title,
                    authors=authors,
                    abstract=abstract,
                    url=f"https://doi.org/{doi}",
                    published_date=published_date,
                    citation_count=citation_count,
                )
                papers.append(paper)

            except Exception as e:
                self.logger.debug(f"Error parsing CrossRef paper: {e}")
                continue

        return papers
