"""Synthesis pipeline orchestrator."""

import asyncio
import time
from typing import Callable, Optional

from knowledgeweaver.core.domain_detector import DomainDetector
from knowledgeweaver.core.query_manager import Query
from knowledgeweaver.output.html_generator import HTMLGenerator
from knowledgeweaver.processing.extractor import KeyFindingsExtractor
from knowledgeweaver.processing.fetcher import PaperFetcher
from knowledgeweaver.processing.insight_generator import InsightGenerator
from knowledgeweaver.processing.summarizer import PaperSummarizer
from knowledgeweaver.processing.synthesizer import PaperSynthesizer
from knowledgeweaver.sources.arxiv import ArxivSource
from knowledgeweaver.sources.base import SourceRegistry
from knowledgeweaver.sources.crossref import CrossrefSource
from knowledgeweaver.sources.pubmed import PubmedSource
from knowledgeweaver.sources.semantic_scholar import SemanticScholarSource
from knowledgeweaver.utils.errors import ResearchAgentError
from knowledgeweaver.utils.logger import logger


class SynthesisPipeline:
    """Orchestrates the complete synthesis pipeline."""

    def __init__(self):
        """Initialize synthesis pipeline."""
        self.logger = logger
        self.domain_detector = DomainDetector()
        self.source_registry = SourceRegistry()
        self.paper_fetcher = PaperFetcher()
        self.paper_summarizer = PaperSummarizer()
        self.paper_synthesizer = PaperSynthesizer()
        self.insight_generator = InsightGenerator()
        self.html_generator = HTMLGenerator()

        # Register sources
        self._register_sources()

    def _register_sources(self) -> None:
        """Register all research sources."""
        sources = {
            "AI/ML": [ArxivSource(), SemanticScholarSource(), CrossrefSource()],
            "Biology": [PubmedSource(), CrossrefSource(), SemanticScholarSource()],
            "Physics": [ArxivSource(), CrossrefSource(), SemanticScholarSource()],
            "Chemistry": [CrossrefSource(), SemanticScholarSource(), ArxivSource()],
            "Medicine": [PubmedSource(), CrossrefSource(), SemanticScholarSource()],
        }

        for domain, domain_sources in sources.items():
            for source in domain_sources:
                self.source_registry.register(domain, source)

        self.logger.info("Registered all research sources")

    async def process(
        self,
        query: Query,
        depth: str = "medium",
        on_progress: Optional[Callable[[str], None]] = None,
    ) -> Optional[str]:
        """Process a query through the complete pipeline.

        Args:
            query: Query to process
            depth: Synthesis depth ('shallow', 'medium', 'deep')
            on_progress: Optional callback invoked with a status message at each step

        Returns:
            Path to generated HTML report or None on failure
        """
        start_time = time.time()

        def _progress(msg: str) -> None:
            self.logger.info(msg)
            if on_progress is not None:
                on_progress(msg)

        try:
            self.logger.info(f"Starting pipeline for query: {query.query_text}")

            # Step 1: Detect domain
            _progress("Detecting research domain...")
            domain_result = self.domain_detector.detect(query.query_text)
            query.domain = domain_result.domain
            self.logger.info(f"Detected domain: {domain_result.domain}")

            # Step 2: Search for papers concurrently across all sources
            source_count = len(domain_result.sources)
            _progress(f"Searching papers across {source_count} sources concurrently...")
            papers = await self._search_papers(query.query_text, domain_result.sources)
            if not papers:
                raise ResearchAgentError("No papers found")

            # Step 3: Fetch and extract text concurrently
            _progress(f"Found {len(papers)} papers. Fetching content...")
            fetch_tasks = [self.paper_fetcher.fetch(p) for p in papers[:10]]
            fetch_results = await asyncio.gather(*fetch_tasks, return_exceptions=True)
            papers_with_text = [
                (papers[i], result)
                for i, result in enumerate(fetch_results)
                if not isinstance(result, Exception) and result
            ]

            if not papers_with_text:
                raise ResearchAgentError("Could not extract text from papers")

            # Step 4: Summarize papers concurrently
            _progress(
                f"Extracted text from {len(papers_with_text)} papers. Summarizing..."
            )
            summarize_tasks = [
                self.paper_summarizer.summarize(paper, text, depth=depth)
                for paper, text in papers_with_text
            ]
            summarize_results = await asyncio.gather(
                *summarize_tasks, return_exceptions=True
            )
            summaries = [r for r in summarize_results if not isinstance(r, Exception)]

            if not summaries:
                raise ResearchAgentError("Could not summarize papers")

            # Step 5: Synthesize findings
            _progress(
                f"Summarized {len(summaries)} papers. Synthesizing findings..."
            )
            synthesis = await self.paper_synthesizer.synthesize(summaries, depth=depth)
            self.logger.info("Synthesis complete")

            # Step 6: Generate insights
            _progress("Generating insights...")
            insights = await self.insight_generator.generate(synthesis, query.query_text)
            self.logger.info("Insights generated")

            # Step 7: Generate HTML report
            _progress("Building HTML report...")
            html_path = self.html_generator.generate(
                query=query.query_text,
                synthesis=synthesis,
                insights=insights,
                domain=query.domain,
                query_id=query.query_id,
            )
            self.logger.info(f"HTML report generated: {html_path}")

            processing_time = time.time() - start_time
            self.logger.info(f"Pipeline completed in {processing_time:.2f}s")

            return html_path

        except Exception as e:
            self.logger.error(f"Pipeline failed: {e}")
            raise

    async def _search_papers(self, query: str, sources: list[str]) -> list:
        """Search for papers across multiple sources concurrently.

        Args:
            query: Search query
            sources: List of source names to search

        Returns:
            Deduplicated list of papers from all sources
        """
        source_instances = []
        for source_name in sources:
            source = self._get_source(source_name)
            if source:
                source_instances.append((source_name, source))
            else:
                self.logger.warning(f"Source not found: {source_name}")

        async def _search_one(name: str, src) -> list:
            self.logger.debug(f"Searching {name}")
            results = await src.search(query, limit=5)
            self.logger.debug(f"Found {len(results)} papers from {name}")
            return results

        tasks = [_search_one(name, src) for name, src in source_instances]
        gathered = await asyncio.gather(*tasks, return_exceptions=True)

        all_papers = []
        for item in gathered:
            if isinstance(item, Exception):
                self.logger.warning(f"Error during concurrent search: {item}")
            else:
                all_papers.extend(item)

        # Remove duplicates by title
        seen_titles: set[str] = set()
        unique_papers = []
        for paper in all_papers:
            if paper.title not in seen_titles:
                seen_titles.add(paper.title)
                unique_papers.append(paper)

        return unique_papers

    def _get_source(self, source_name: str):
        """Get a source by name.

        Args:
            source_name: Source name

        Returns:
            Source instance or None
        """
        for domain_sources in self.source_registry.get_all_sources().values():
            for source in domain_sources:
                if source.name == source_name:
                    return source
        return None

    def __repr__(self) -> str:
        return f"<SynthesisPipeline(sources={len(self.source_registry.get_all_sources())})>"
