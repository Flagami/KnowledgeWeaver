"""Paper fetching and text extraction."""

import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

import httpx
import pdfplumber

from knowledgeweaver.config import settings
from knowledgeweaver.sources.base import PaperMetadata
from knowledgeweaver.utils.errors import FetchError
from knowledgeweaver.utils.logger import logger


class PaperFetcher:
    """Fetches and extracts text from research papers."""

    CACHE_DIR = Path(settings.output_dir) / "paper_cache"
    CACHE_EXPIRY_DAYS = 30

    def __init__(self):
        """Initialize paper fetcher."""
        self.logger = logger
        self.client = httpx.AsyncClient(timeout=60.0)
        self.CACHE_DIR.mkdir(parents=True, exist_ok=True)

    async def fetch(self, paper: PaperMetadata) -> Optional[str]:
        """Fetch and extract text from a paper.

        Args:
            paper: Paper metadata

        Returns:
            Extracted text or None if unavailable
        """
        paper_id = f"{paper.source}:{paper.source_id}"
        try:
            # Check cache first
            cached_text = self._get_cached_text(paper)
            if cached_text:
                self.logger.debug(
                    f"Cache HIT: {paper_id} | chars={len(cached_text)}"
                )
                return cached_text

            self.logger.debug(f"Cache MISS: {paper_id}")

            # Try to fetch from URL
            if paper.url:
                self.logger.debug(f"Fetching URL: {paper.url} | paper={paper_id}")
                text = await self._fetch_from_url(paper.url)
                if text:
                    self._cache_text(paper, text)
                    self.logger.debug(
                        f"Fetch OK: {paper_id} | chars={len(text)}"
                    )
                    return text
                else:
                    self.logger.warning(
                        f"Fetch returned no text: {paper_id} | url={paper.url}"
                    )

            # Fallback to abstract
            if paper.abstract:
                self.logger.debug(
                    f"Using abstract fallback: {paper_id} | chars={len(paper.abstract)}"
                )
                return paper.abstract

            self.logger.warning(f"No text available for: {paper_id}")
            return None

        except Exception as e:
            self.logger.error(
                f"Error fetching paper {paper_id}: {type(e).__name__}: {e}"
            )
            return None

    async def _fetch_from_url(self, url: str) -> Optional[str]:
        """Fetch content from URL.

        Args:
            url: Paper URL

        Returns:
            Extracted text or None
        """
        try:
            response = await self.client.get(url, follow_redirects=True)
            self.logger.debug(
                f"HTTP {response.status_code} for URL: {url}"
            )
            response.raise_for_status()

            content_type = response.headers.get("content-type", "").lower()

            # Handle PDF
            if "pdf" in content_type or url.endswith(".pdf"):
                text = self._extract_pdf_text(response.content)
                if text:
                    self.logger.debug(
                        f"PDF extracted: {len(text)} chars | url={url}"
                    )
                else:
                    self.logger.warning(f"PDF extraction returned no text | url={url}")
                return text

            # Handle HTML
            if "html" in content_type or "text" in content_type:
                text = self._extract_html_text(response.text)
                if text:
                    self.logger.debug(
                        f"HTML extracted: {len(text)} chars | url={url}"
                    )
                else:
                    self.logger.warning(f"HTML extraction returned no text | url={url}")
                return text

            self.logger.warning(
                f"Unhandled content-type '{content_type}' | url={url}"
            )
            return None

        except httpx.TimeoutException as e:
            self.logger.warning(f"Timeout fetching URL: {url} | {e}")
            return None
        except httpx.ConnectError as e:
            self.logger.warning(f"Connection error fetching URL: {url} | {e}")
            return None
        except httpx.HTTPStatusError as e:
            self.logger.warning(
                f"HTTP {e.response.status_code} error fetching URL: {url} | {e}"
            )
            return None
        except httpx.HTTPError as e:
            self.logger.debug(f"HTTP error fetching {url}: {e}")
            return None
        except Exception as e:
            self.logger.debug(f"Error fetching from {url}: {e}")
            return None

    def _extract_pdf_text(self, pdf_content: bytes) -> Optional[str]:
        """Extract text from PDF content.

        Args:
            pdf_content: PDF file content

        Returns:
            Extracted text or None
        """
        try:
            with pdfplumber.open(pdf_content) as pdf:
                text = ""
                for page in pdf.pages[:10]:  # Limit to first 10 pages
                    text += page.extract_text() or ""
                result = text.strip() if text else None
                if result:
                    self.logger.debug(f"PDF extraction OK | pages={len(pdf.pages)} | chars={len(result)}")
                else:
                    self.logger.warning("PDF extraction produced no text")
                return result

        except Exception as e:
            self.logger.warning(f"PDF extraction failed: {type(e).__name__}: {e}")
            return None

    def _extract_html_text(self, html_content: str) -> Optional[str]:
        """Extract text from HTML content.

        Args:
            html_content: HTML content

        Returns:
            Extracted text or None
        """
        try:
            # Simple HTML text extraction (remove tags)
            import re

            # Remove script and style elements
            html = re.sub(r"<script[^>]*>.*?</script>", "", html_content, flags=re.DOTALL)
            html = re.sub(r"<style[^>]*>.*?</style>", "", html, flags=re.DOTALL)

            # Remove HTML tags
            text = re.sub(r"<[^>]+>", "", html)

            # Clean up whitespace
            text = re.sub(r"\s+", " ", text).strip()

            return text if text else None

        except Exception as e:
            self.logger.debug(f"Error extracting HTML text: {e}")
            return None

    def _get_cache_key(self, paper: PaperMetadata) -> str:
        """Get cache key for a paper.

        Args:
            paper: Paper metadata

        Returns:
            Cache key
        """
        key = f"{paper.source}:{paper.source_id}"
        return hashlib.md5(key.encode()).hexdigest()

    def _get_cached_text(self, paper: PaperMetadata) -> Optional[str]:
        """Get cached text for a paper.

        Args:
            paper: Paper metadata

        Returns:
            Cached text or None if not found or expired
        """
        cache_key = self._get_cache_key(paper)
        cache_file = self.CACHE_DIR / f"{cache_key}.txt"

        if not cache_file.exists():
            return None

        # Check if cache is expired
        file_age = datetime.now() - datetime.fromtimestamp(cache_file.stat().st_mtime)
        if file_age > timedelta(days=self.CACHE_EXPIRY_DAYS):
            cache_file.unlink()
            return None

        try:
            return cache_file.read_text(encoding="utf-8")
        except Exception as e:
            self.logger.debug(f"Error reading cache file: {e}")
            return None

    def _cache_text(self, paper: PaperMetadata, text: str) -> None:
        """Cache text for a paper.

        Args:
            paper: Paper metadata
            text: Text to cache
        """
        try:
            cache_key = self._get_cache_key(paper)
            cache_file = self.CACHE_DIR / f"{cache_key}.txt"
            cache_file.write_text(text, encoding="utf-8")
        except Exception as e:
            self.logger.debug(f"Error caching text: {e}")
