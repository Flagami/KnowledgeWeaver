"""Synthesis pipeline orchestrator."""

import time
from typing import Optional

from knowledgeweaver.core.domain_detector import DomainDetector
from knowledgeweaver.core.query_manager import Query, QueryManager
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
        self.query_manager = QueryManager()

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
    ) -> Optional[str]:
        """Process a query through the complete pipeline.

        Args:
            query: Query to process
            depth: Synthesis depth ('shallow', 'medium', 'deep')

        Returns:
            Path to generated HTML report or None on failure
        """
        start_time = time.time()

        try:
            self.logger.info(f"Starting pipeline for query: {query.query_text}")

            # Step 1: Detect domain
            self.logger.debug("Step 1: Detecting domain")
            domain_result = self.domain_detector.detect(query.query_text)
            query.domain = domain_result.domain
            self.logger.info(f"Detected domain: {domain_result.domain}")

            # Step 2: Search for papers
            self.logger.debug("Step 2: Searching for papers")
            papers = await self._search_papers(query.query_text, domain_result.sources)
            if not papers:
                raise ResearchAgentError("No papers found")
            self.logger.info(f"Found {len(papers)} papers")

            # Step 3: Fetch and extract text
            self.logger.debug("Step 3: Fetching and extracting text")
            papers_with_text = []
            for paper in papers[:10]:  # Limit to top 10 papers
                text = await self.paper_fetcher.fetch(paper)
                if text:
                    papers_with_text.append((paper, text))

            if not papers_with_text:
                raise ResearchAgentError("Could not extract text from papers")
            self.logger.info(f"Extracted text from {len(papers_with_text)} papers")

            # Step 4: Summarize papers
            self.logger.debug("Step 4: Summarizing papers")
            summaries = []
            for paper, text in papers_with_text:
                try:
                    summary = await self.paper_summarizer.summarize(
                        paper, text, depth=depth
                    )
                    summaries.append(summary)
                except Exception as e:
                    self.logger.warning(f"Failed to summarize paper: {e}")
                    continue

            if not summaries:
                raise ResearchAgentError("Could not summarize papers")
            self.logger.info(f"Summarized {len(summaries)} papers")

            # Step 5: Synthesize findings
            self.logger.debug("Step 5: Synthesizing findings")
            synthesis = await self.paper_synthesizer.synthesize(summaries, depth=depth)
            self.logger.info("Synthesis complete")

            # Step 6: Generate insights
            self.logger.debug("Step 6: Generating insights")
            insights = await self.insight_generator.generate(synthesis, query.query_text)
            self.logger.info("Insights generated")

            # Step 7: Generate HTML
            self.logger.debug("Step 7: Generating HTML report")
            html_path = self.html_generator.generate(
                query=query.query_text,
                synthesis=synthesis,
                insights=insights,
                domain=query.domain,
            )
            self.logger.info(f"HTML report generated: {html_path}")

            # Calculate processing time
            processing_time = time.time() - start_time
            self.logger.info(f"Pipeline completed in {processing_time:.2f}s")

            return html_path

        except Exception as e:
            self.logger.error(f"Pipeline failed: {e}")
            raise

    async def _search_papers(self, query: str, sources: list[str]) -> list:
        """Search for papers across multiple sources.

        Args:
            query: Search query
            sources: List of source names to search

        Returns:
            List of papers from all sources
        """
        all_papers = []

        for source_name in sources:
            try:
                self.logger.debug(f"Searching {source_name}")
                source = self._get_source(source_name)
                if not source:
                    self.logger.warning(f"Source not found: {source_name}")
                    continue

                papers = await source.search(query, limit=5)
                all_papers.extend(papers)
                self.logger.debug(f"Found {len(papers)} papers from {source_name}")

            except Exception as e:
                self.logger.warning(f"Error searching {source_name}: {e}")
                continue

        # Remove duplicates by title
        seen_titles = set()
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
        # Try to find in registry
        for domain_sources in self.source_registry.get_all_sources().values():
            for source in domain_sources:
                if source.name == source_name:
                    return source
        return None

    def __repr__(self) -> str:
        return f"<SynthesisPipeline(sources={len(self.source_registry.get_all_sources())})>"
