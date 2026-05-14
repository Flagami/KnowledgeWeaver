"""PubMed research source integration."""

import re
from typing import Optional

import httpx

from knowledgeweaver.sources.base import BaseSource, PaperMetadata
from knowledgeweaver.utils.errors import SourceError


class PubmedSource(BaseSource):
    """PubMed research paper source."""

    BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"

    def __init__(self):
        """Initialize PubMed source."""
        super().__init__(name="pubmed", priority=9)
        self.client = httpx.AsyncClient(timeout=30.0)

    async def search(
        self,
        query: str,
        limit: int = 10,
        sort_by: str = "relevance",
    ) -> list[PaperMetadata]:
        """Search PubMed for papers.

        Args:
            query: Search query
            limit: Maximum number of results
            sort_by: Sort order ('relevance', 'date')

        Returns:
            List of paper metadata
        """
        try:
            # First, search for PMIDs
            search_url = f"{self.BASE_URL}/esearch.fcgi"
            search_params = {
                "db": "pubmed",
                "term": query,
                "retmax": limit,
                "rettype": "json",
            }

            if sort_by == "date":
                search_params["sort"] = "date"

            self.logger.debug(f"PubMed search | query='{query}' | limit={limit}")
            response = await self.client.get(search_url, params=search_params)
            self.logger.debug(f"PubMed HTTP {response.status_code} | query='{query}'")
            response.raise_for_status()

            search_data = response.json()
            pmids = search_data.get("esearchresult", {}).get("idlist", [])

            if not pmids:
                self.logger.info(f"PubMed: 0 papers found | query='{query}'")
                return []

            self.logger.debug(f"PubMed: {len(pmids)} PMIDs found, fetching details")
            # Fetch details for each PMID
            papers = await self._fetch_paper_details(pmids)
            self.logger.info(f"PubMed: {len(papers)} papers found | query='{query}'")
            return papers

        except httpx.HTTPError as e:
            self.logger.error(f"PubMed API error | query='{query}' | {type(e).__name__}: {e}")
            raise SourceError(f"PubMed search failed: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error searching PubMed | query='{query}' | {type(e).__name__}: {e}")
            raise SourceError(f"Unexpected error: {e}")

    async def fetch(self, paper: PaperMetadata) -> Optional[str]:
        """Fetch paper from PubMed (returns abstract).

        Args:
            paper: Paper metadata

        Returns:
            Paper abstract or None
        """
        return paper.abstract

    async def _fetch_paper_details(self, pmids: list[str]) -> list[PaperMetadata]:
        """Fetch detailed information for papers.

        Args:
            pmids: List of PubMed IDs

        Returns:
            List of paper metadata
        """
        papers = []

        try:
            fetch_url = f"{self.BASE_URL}/efetch.fcgi"
            fetch_params = {
                "db": "pubmed",
                "id": ",".join(pmids),
                "rettype": "json",
            }

            response = await self.client.get(fetch_url, params=fetch_params)
            response.raise_for_status()

            data = response.json()
            articles = data.get("result", {}).get("uids", [])

            for uid in articles:
                if uid == "uids":
                    continue

                article = data.get("result", {}).get(uid, {})
                if not article:
                    continue

                try:
                    title = article.get("title", "")
                    authors = ", ".join(
                        [
                            f"{a.get('name', '')}"
                            for a in article.get("authors", [])[:5]
                        ]
                    )
                    abstract = article.get("abstract", "")
                    published_date = article.get("pubdate", "")[:10]

                    paper = PaperMetadata(
                        source="pubmed",
                        source_id=uid,
                        title=title,
                        authors=authors,
                        abstract=abstract,
                        url=f"https://pubmed.ncbi.nlm.nih.gov/{uid}/",
                        published_date=published_date,
                        citation_count=0,
                    )
                    papers.append(paper)

                except Exception as e:
                    self.logger.debug(f"Error parsing PubMed article {uid}: {e}")
                    continue

        except Exception as e:
            self.logger.error(f"Error fetching PubMed details: {e}")

        return papers
