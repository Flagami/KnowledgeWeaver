"""arXiv research source integration."""

import re
from datetime import datetime
from typing import Optional

import httpx

from knowledgeweaver.sources.base import BaseSource, PaperMetadata
from knowledgeweaver.utils.errors import SourceError


class ArxivSource(BaseSource):
    """arXiv research paper source."""

    BASE_URL = "http://export.arxiv.org/api/query"

    def __init__(self):
        """Initialize arXiv source."""
        super().__init__(name="arxiv", priority=10)
        self.client = httpx.AsyncClient(timeout=30.0)

    async def search(
        self,
        query: str,
        limit: int = 10,
        sort_by: str = "relevance",
    ) -> list[PaperMetadata]:
        """Search arXiv for papers.

        Args:
            query: Search query
            limit: Maximum number of results
            sort_by: Sort order ('relevance', 'date')

        Returns:
            List of paper metadata
        """
        try:
            # Build arXiv query
            arxiv_query = f"search_query=all:{query}&start=0&max_results={limit}"
            if sort_by == "date":
                arxiv_query += "&sortBy=submittedDate&sortOrder=descending"
            else:
                arxiv_query += "&sortBy=relevance"

            self.logger.debug(f"arXiv search | query='{query}' | limit={limit} | sort={sort_by}")
            response = await self.client.get(f"{self.BASE_URL}?{arxiv_query}")
            self.logger.debug(f"arXiv HTTP {response.status_code} | query='{query}'")
            response.raise_for_status()

            papers = self._parse_arxiv_response(response.text)
            self.logger.info(f"arXiv: {len(papers)} papers found | query='{query}'")
            return papers

        except httpx.HTTPError as e:
            self.logger.error(f"arXiv API error | query='{query}' | {type(e).__name__}: {e}")
            raise SourceError(f"arXiv search failed: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error searching arXiv | query='{query}' | {type(e).__name__}: {e}")
            raise SourceError(f"Unexpected error: {e}")

    async def fetch(self, paper: PaperMetadata) -> Optional[str]:
        """Fetch paper from arXiv (returns abstract as we can't fetch full PDF easily).

        Args:
            paper: Paper metadata

        Returns:
            Paper abstract or None
        """
        return paper.abstract

    def _parse_arxiv_response(self, xml_response: str) -> list[PaperMetadata]:
        """Parse arXiv API XML response.

        Args:
            xml_response: XML response from arXiv API

        Returns:
            List of paper metadata
        """
        papers = []

        # Simple XML parsing (avoiding external dependencies)
        entries = re.findall(r"<entry>(.*?)</entry>", xml_response, re.DOTALL)

        for entry in entries:
            try:
                # Extract fields using regex
                title_match = re.search(r"<title>(.*?)</title>", entry)
                authors_match = re.findall(r"<author>.*?<name>(.*?)</name>", entry)
                summary_match = re.search(r"<summary>(.*?)</summary>", entry, re.DOTALL)
                id_match = re.search(r"<id>(.*?)</id>", entry)
                published_match = re.search(r"<published>(.*?)</published>", entry)

                if not all([title_match, id_match, published_match]):
                    self.logger.debug("arXiv entry skipped: missing required fields")
                    continue

                title = title_match.group(1).strip()
                authors = ", ".join(author.strip() for author in authors_match)
                abstract = summary_match.group(1).strip() if summary_match else ""
                arxiv_id = id_match.group(1).strip().split("/abs/")[-1]
                published_date = published_match.group(1).split("T")[0]

                paper = PaperMetadata(
                    source="arxiv",
                    source_id=arxiv_id,
                    title=title,
                    authors=authors,
                    abstract=abstract,
                    url=f"https://arxiv.org/abs/{arxiv_id}",
                    published_date=published_date,
                    citation_count=0,  # arXiv doesn't provide citation count
                )
                papers.append(paper)

            except Exception as e:
                self.logger.warning(f"arXiv entry parse error: {type(e).__name__}: {e}")
                continue

        return papers
