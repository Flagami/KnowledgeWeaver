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
            qid = query.query_id[:8]
            self.logger.info(
                f"[{qid}] Pipeline start | query='{query.query_text[:80]}' | depth={depth}"
            )

            # Step 1: Detect domain
            step_start = time.time()
            self.logger.info(
                f"[{qid}] Step 1/7 — Domain detection | query='{query.query_text[:80]}'"
            )
            _progress("Detecting research domain...")
            domain_result = self.domain_detector.detect(query.query_text)
            query.domain = domain_result.domain
            self.logger.info(
                f"[{qid}] Domain detected: '{domain_result.domain}'"
                f" | sources={domain_result.sources}"
                f" | t={time.time()-step_start:.2f}s"
            )

            # Step 2: Search for papers concurrently across all sources
            step_start = time.time()
            source_count = len(domain_result.sources)
            self.logger.info(
                f"[{qid}] Step 2/7 — Searching {source_count} sources"
                f" | query='{query.query_text[:80]}'"
            )
            _progress(f"Searching papers across {source_count} sources concurrently...")
            papers = await self._search_papers(query.query_text, domain_result.sources, qid)
            self.logger.info(
                f"[{qid}] Step 2/7 — Total: {len(papers)} unique papers after dedup"
                f" | t={time.time()-step_start:.2f}s"
            )
            if not papers:
                raise ResearchAgentError("No papers found")

            # Step 3: Fetch and extract text concurrently
            step_start = time.time()
            papers_to_fetch = papers[:10]
            self.logger.info(
                f"[{qid}] Step 3/7 — Fetching content for {len(papers_to_fetch)} papers"
            )
            _progress(f"Found {len(papers)} papers. Fetching content...")
            for p in papers_to_fetch:
                self.logger.debug(
                    f"[{qid}] Fetching: '{p.title[:60]}' | source={p.source} | url={p.url}"
                )
            fetch_tasks = [self.paper_fetcher.fetch(p) for p in papers_to_fetch]
            fetch_results = await asyncio.gather(*fetch_tasks, return_exceptions=True)
            papers_with_text = []
            for i, result in enumerate(fetch_results):
                paper = papers_to_fetch[i]
                if isinstance(result, Exception):
                    self.logger.warning(
                        f"[{qid}] Fetch FAILED: '{paper.title[:60]}'"
                        f" | reason={type(result).__name__}: {result}"
                    )
                elif result:
                    papers_with_text.append((paper, result))
                    self.logger.debug(
                        f"[{qid}] Fetch OK: '{paper.title[:60]}'"
                        f" | chars={len(result)}"
                    )
                else:
                    self.logger.warning(
                        f"[{qid}] Fetch returned empty: '{paper.title[:60]}'"
                    )
            self.logger.info(
                f"[{qid}] Step 3/7 — Fetched {len(papers_with_text)}/{len(papers_to_fetch)} papers"
                f" | t={time.time()-step_start:.2f}s"
            )

            if not papers_with_text:
                raise ResearchAgentError("Could not extract text from papers")

            # Step 4: Summarize papers concurrently
            step_start = time.time()
            self.logger.info(
                f"[{qid}] Step 4/7 — Summarizing {len(papers_with_text)} papers"
                f" | depth={depth}"
            )
            _progress(
                f"Extracted text from {len(papers_with_text)} papers. Summarizing..."
            )
            for paper, _ in papers_with_text:
                self.logger.debug(
                    f"[{qid}] Summarizing: '{paper.title[:60]}'"
                )
            summarize_tasks = [
                self.paper_summarizer.summarize(paper, text, depth=depth)
                for paper, text in papers_with_text
            ]
            summarize_results = await asyncio.gather(
                *summarize_tasks, return_exceptions=True
            )
            summaries = []
            for i, result in enumerate(summarize_results):
                paper = papers_with_text[i][0]
                if isinstance(result, Exception):
                    self.logger.warning(
                        f"[{qid}] Summarize FAILED: '{paper.title[:60]}'"
                        f" | reason={type(result).__name__}: {result}"
                    )
                else:
                    summaries.append(result)
                    self.logger.debug(
                        f"[{qid}] Summarize OK: '{paper.title[:60]}'"
                    )
            self.logger.info(
                f"[{qid}] Step 4/7 — Summarized {len(summaries)}/{len(papers_with_text)} papers"
                f" | t={time.time()-step_start:.2f}s"
            )

            if not summaries:
                raise ResearchAgentError("Could not summarize papers")

            # Step 5: Synthesize findings
            step_start = time.time()
            self.logger.info(
                f"[{qid}] Step 5/7 — Synthesizing {len(summaries)} summaries"
                f" | depth={depth}"
            )
            _progress(
                f"Summarized {len(summaries)} papers. Synthesizing findings..."
            )
            synthesis = await self.paper_synthesizer.synthesize(summaries, depth=depth)
            self.logger.info(
                f"[{qid}] Step 5/7 — Synthesis complete"
                f" | output_chars={len(synthesis.synthesis)}"
                f" | connections={len(synthesis.connections)}"
                f" | citations={len(synthesis.citations)}"
                f" | t={time.time()-step_start:.2f}s"
            )

            # Step 6: Generate insights
            step_start = time.time()
            self.logger.info(f"[{qid}] Step 6/7 — Generating insights")
            _progress("Generating insights...")
            insights = await self.insight_generator.generate(synthesis, query.query_text)
            self.logger.info(
                f"[{qid}] Step 6/7 — Insights generated"
                f" | insights={len(insights.insights)}"
                f" | future_directions={len(insights.future_directions)}"
                f" | open_questions={len(insights.open_questions)}"
                f" | t={time.time()-step_start:.2f}s"
            )

            # Step 7: Generate HTML report
            step_start = time.time()
            self.logger.info(f"[{qid}] Step 7/7 — Building HTML report")
            _progress("Building HTML report...")
            html_path = self.html_generator.generate(
                query=query.query_text,
                synthesis=synthesis,
                insights=insights,
                domain=query.domain,
                query_id=query.query_id,
            )
            import os
            file_size = os.path.getsize(html_path) if html_path and os.path.exists(html_path) else 0
            self.logger.info(
                f"[{qid}] Step 7/7 — HTML report generated"
                f" | path={html_path}"
                f" | size={file_size} bytes"
                f" | t={time.time()-step_start:.2f}s"
            )

            total_time = time.time() - start_time
            self.logger.info(f"[{qid}] Pipeline completed | total_time={total_time:.2f}s")

            return html_path

        except Exception as e:
            self.logger.exception(f"[{query.query_id[:8]}] Pipeline failed: {e}")
            raise

    async def _search_papers(self, query: str, sources: list[str], qid: str = "") -> list:
        """Search for papers across multiple sources concurrently.

        Args:
            query: Search query
            sources: List of source names to search
            qid: Short query ID prefix for log messages

        Returns:
            Deduplicated list of papers from all sources
        """
        prefix = f"[{qid}] Step 2/7" if qid else "Step 2/7"

        source_instances = []
        for source_name in sources:
            source = self._get_source(source_name)
            if source:
                source_instances.append((source_name, source))
            else:
                self.logger.warning(f"{prefix} — Source not found: {source_name}")

        async def _search_one(name: str, src) -> list:
            self.logger.debug(f"{prefix} — Searching source: {name}")
            try:
                results = await src.search(query, limit=5)
                self.logger.info(f"{prefix} — {name}: {len(results)} papers found")
                return results
            except Exception as exc:
                self.logger.warning(
                    f"{prefix} — {name}: ERROR {type(exc).__name__}: {exc}"
                )
                raise

        tasks = [_search_one(name, src) for name, src in source_instances]
        gathered = await asyncio.gather(*tasks, return_exceptions=True)

        all_papers = []
        for (name, _), item in zip(source_instances, gathered):
            if isinstance(item, Exception):
                self.logger.warning(
                    f"{prefix} — {name}: skipped due to error: {item}"
                )
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
