# Implementation Plan: ResearchAgent

## Overview

ResearchAgent is a TUI-based AI research synthesis system that transforms user questions into expert-level summaries backed by highly cited papers. The MVP will support multi-domain research aggregation, concurrent query processing (8 parallel), deep synthesis pipeline, interactive HTML output, and user preference learning.

**Timeline:** MVP in phases, starting with core infrastructure → research pipeline → synthesis → TUI → learning → integration.

---

## Architecture Decisions

1. **Vertical Slicing:** Build complete feature paths (query → synthesis → output) rather than horizontal layers (all search, then all synthesis, then all output)
2. **Async-First:** All I/O operations use `asyncio` for concurrent query handling
3. **Domain-Weighted Sources:** Query domain detection maps to prioritized source lists
4. **Preference-Driven Synthesis:** User preferences adjust Claude's synthesis prompt depth
5. **Graceful Degradation:** If one source fails, continue with others; if synthesis fails, retry with simpler prompt
6. **Local-First Storage:** SQLite for MVP (migrate to PostgreSQL in v2)
7. **Configurable Model:** LLM_MODEL environment variable controls base model

---

## Dependency Graph

```
┌─────────────────────────────────────────────────────────────┐
│ Phase 1: Foundation (Core Infrastructure)                   │
│ - Project setup, config, database, logging                  │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ Phase 2: Research Pipeline (Search & Fetch)                 │
│ - Domain detector, source registry, search agents           │
│ - Paper fetcher, key findings extractor                     │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ Phase 3: Synthesis & Output (Claude Integration)            │
│ - Summarizer, synthesizer, insight generator                │
│ - HTML generator, interactive templates                     │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ Phase 4: TUI Interface (User Interaction)                   │
│ - Query input, processing status, results display           │
│ - History, main app orchestration                           │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ Phase 5: User Learning (Preferences & Feedback)             │
│ - Preference tracker, feedback collector, updater           │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ Phase 6: Integration & Testing (End-to-End)                 │
│ - E2E tests, error handling, performance tuning             │
└─────────────────────────────────────────────────────────────┘
```

---

## Task List

### Phase 1: Foundation (Core Infrastructure)

#### Task 1.1: Project Setup & Configuration
**Description:** Initialize project structure, dependencies, and configuration system. Set up pyproject.toml, .env.example, and pydantic-based configuration.

**Acceptance criteria:**
- [ ] `pyproject.toml` defines all dependencies with pinned versions
- [ ] `.env.example` documents all required environment variables
- [ ] `config.py` uses pydantic to validate and load configuration
- [ ] `LLM_MODEL` environment variable controls base model (default: claude-opus-4-7)
- [ ] Project structure matches SPEC.md layout
- [ ] `python -m pip install -e ".[dev]"` succeeds

**Verification:**
- [ ] Run: `python -c "from researchagent.config import settings; print(settings.llm_model)"`
- [ ] Verify: `LLM_MODEL=claude-sonnet-4-6 python -c "from researchagent.config import settings; print(settings.llm_model)"` outputs `claude-sonnet-4-6`
- [ ] Check: All files in correct directories per SPEC.md

**Dependencies:** None

**Files likely touched:**
- `pyproject.toml`
- `.env.example`
- `researchagent/__init__.py`
- `researchagent/config.py`
- `.gitignore`

**Estimated scope:** Small (1-2 files)

---

#### Task 1.2: Database Schema & ORM Setup
**Description:** Create SQLite database schema for user preferences, query history, and papers cache. Set up SQLAlchemy ORM models.

**Acceptance criteria:**
- [ ] SQLite database initializes on first run
- [ ] `UserPreferences` model stores domain, paper_type, depth_level, output_format
- [ ] `Query` model stores query_text, domain, status, result_path, user_rating, feedback
- [ ] `Paper` model stores source, source_id, title, authors, abstract, url, published_date, citation_count
- [ ] Database migrations work (Alembic setup)
- [ ] Models have proper relationships (Query → Papers)

**Verification:**
- [ ] Run: `python -c "from researchagent.storage.models import Base; Base.metadata.create_all()"`
- [ ] Check: SQLite file created at configured path
- [ ] Verify: All tables exist with correct columns

**Dependencies:** Task 1.1

**Files likely touched:**
- `researchagent/storage/database.py`
- `researchagent/storage/models.py`
- `researchagent/storage/migrations/` (Alembic)

**Estimated scope:** Medium (3-5 files)

---

#### Task 1.3: Logging & Error Handling Setup
**Description:** Configure structured logging and define custom exception hierarchy for the system.

**Acceptance criteria:**
- [ ] Logging configured with file and console handlers
- [ ] Log level configurable via environment variable
- [ ] Custom exceptions defined: `ResearchAgentError`, `SourceError`, `SynthesisError`, `StorageError`
- [ ] All exceptions inherit from `ResearchAgentError`
- [ ] Logging includes timestamps, levels, and module names

**Verification:**
- [ ] Run: `python -c "from researchagent.utils.logger import logger; logger.info('test')"` outputs to console
- [ ] Check: Log file created at configured path
- [ ] Verify: Custom exceptions can be imported and raised

**Dependencies:** Task 1.1

**Files likely touched:**
- `researchagent/utils/logger.py`
- `researchagent/utils/errors.py`

**Estimated scope:** Small (1-2 files)

---

### Checkpoint: Foundation Complete
- [ ] All tests pass: `pytest tests/unit/test_config.py tests/unit/test_database.py -v`
- [ ] Project builds without errors
- [ ] Configuration loads correctly with environment variables
- [ ] Database schema initializes
- [ ] Logging works end-to-end

---

### Phase 2: Research Pipeline (Search & Fetch)

#### Task 2.1: Domain Detector
**Description:** Implement domain detection from user queries. Map detected domain to prioritized source list.

**Acceptance criteria:**
- [ ] `DomainDetector` class detects domain from query text
- [ ] Supports ≥3 domains: AI/ML, Biology, Physics
- [ ] Returns domain name and confidence score
- [ ] Maps domain → source priority list (e.g., AI/ML → [arXiv, Semantic Scholar, CrossRef])
- [ ] Handles unknown domains gracefully (default to general sources)

**Verification:**
- [ ] Test: `detector.detect("quantum computing")` returns `("AI/ML", 0.95)`
- [ ] Test: `detector.detect("protein folding")` returns `("Biology", 0.90)`
- [ ] Test: `detector.get_sources("AI/ML")` returns `["arxiv", "semantic_scholar", "crossref"]`

**Dependencies:** Task 1.1

**Files likely touched:**
- `researchagent/core/domain_detector.py`
- `tests/unit/test_domain_detector.py`

**Estimated scope:** Small (1-2 files)

---

#### Task 2.2: Source Registry & Base Source Interface
**Description:** Create abstract source interface and registry mapping domains to source implementations.

**Acceptance criteria:**
- [ ] `BaseSource` abstract class defines interface: `search()`, `fetch()`, `parse()`
- [ ] `SourceRegistry` maps domain → list of source instances
- [ ] Registry is configurable (can add/remove sources)
- [ ] Each source has priority weight for ranking results

**Verification:**
- [ ] Test: `registry.get_sources("AI/ML")` returns list of source instances
- [ ] Test: Sources have correct priority order
- [ ] Verify: All sources implement required methods

**Dependencies:** Task 2.1

**Files likely touched:**
- `researchagent/sources/base.py`
- `researchagent/sources/source_registry.py`
- `tests/unit/test_source_registry.py`

**Estimated scope:** Small (1-2 files)

---

#### Task 2.3: Search Agents (arXiv, PubMed, Semantic Scholar, CrossRef)
**Description:** Implement search agents for each research source. Each agent queries its API and returns standardized paper metadata.

**Acceptance criteria:**
- [ ] `ArxivSource` queries arXiv API, returns papers with title, authors, abstract, URL, date
- [ ] `PubmedSource` queries PubMed API, returns papers with same metadata
- [ ] `SemanticScholarSource` queries Semantic Scholar API, includes citation count
- [ ] `CrossrefSource` queries CrossRef API, includes DOI and publication date
- [ ] All sources handle API errors gracefully (retry, fallback)
- [ ] Results ranked by recency and citation count
- [ ] Concurrent requests within rate limits

**Verification:**
- [ ] Test: `arxiv_source.search("quantum computing", limit=5)` returns 5 papers
- [ ] Test: Results include all required fields (title, authors, abstract, url, date, citation_count)
- [ ] Test: API errors don't crash (logged and handled)
- [ ] Verify: Citation count present in Semantic Scholar results

**Dependencies:** Task 2.2

**Files likely touched:**
- `researchagent/sources/arxiv.py`
- `researchagent/sources/pubmed.py`
- `researchagent/sources/semantic_scholar.py`
- `researchagent/sources/crossref.py`
- `tests/integration/test_source_integration.py`

**Estimated scope:** Large (5+ files)

---

#### Task 2.4: Paper Fetcher & Text Extractor
**Description:** Download papers from URLs and extract text content. Handle PDFs, HTML, and plain text.

**Acceptance criteria:**
- [ ] `PaperFetcher` downloads papers from URLs
- [ ] Extracts text from PDFs using `pdfplumber` or similar
- [ ] Handles HTML pages (extract main content)
- [ ] Caches downloaded papers by source ID (key: `{source}:{source_id}`)
- [ ] Cache expires after 30 days
- [ ] Handles download failures gracefully (log, continue)

**Verification:**
- [ ] Test: `fetcher.fetch(paper_url)` returns extracted text
- [ ] Test: PDF extraction works correctly
- [ ] Test: Cache prevents duplicate downloads
- [ ] Verify: Failed downloads logged but don't crash

**Dependencies:** Task 2.3

**Files likely touched:**
- `researchagent/processing/fetcher.py`
- `researchagent/storage/cache.py`
- `tests/integration/test_fetcher.py`

**Estimated scope:** Medium (3-5 files)

---

#### Task 2.5: Key Findings Extractor
**Description:** Extract key findings, methodology, and conclusions from paper text using Claude.

**Acceptance criteria:**
- [ ] `KeyFindingsExtractor` uses Claude to extract structured findings
- [ ] Returns: key_findings (list), methodology (str), conclusions (str), limitations (str)
- [ ] Respects user depth preference (shallow/medium/deep)
- [ ] Handles extraction failures gracefully (return raw abstract)

**Verification:**
- [ ] Test: `extractor.extract(paper_text, depth="medium")` returns structured findings
- [ ] Test: Shallow extraction is shorter than deep extraction
- [ ] Test: Failures return fallback (raw abstract)

**Dependencies:** Task 2.4, Task 1.1 (config for Claude API)

**Files likely touched:**
- `researchagent/processing/extractor.py`
- `tests/unit/test_extractor.py`

**Estimated scope:** Small (1-2 files)

---

### Checkpoint: Research Pipeline Complete
- [ ] All tests pass: `pytest tests/unit/test_domain_detector.py tests/integration/test_source_integration.py -v`
- [ ] Domain detection works for ≥3 domains
- [ ] Search agents return papers from all sources
- [ ] Paper fetcher downloads and caches papers
- [ ] Key findings extraction works end-to-end

---

### Phase 3: Synthesis & Output (Claude Integration)

#### Task 3.1: Paper Summarizer
**Description:** Summarize individual papers using Claude. Respect user depth preferences.

**Acceptance criteria:**
- [ ] `PaperSummarizer` uses Claude to summarize papers
- [ ] Respects depth preference: shallow (1-2 paragraphs), medium (3-4), deep (5+)
- [ ] Returns: summary (str), key_points (list), citations (list)
- [ ] Handles summarization failures gracefully

**Verification:**
- [ ] Test: `summarizer.summarize(paper, depth="medium")` returns summary
- [ ] Test: Shallow summary is shorter than deep summary
- [ ] Test: Key points extracted correctly

**Dependencies:** Task 2.5, Task 1.1

**Files likely touched:**
- `researchagent/processing/summarizer.py`
- `tests/unit/test_summarizer.py`

**Estimated scope:** Small (1-2 files)

---

#### Task 3.2: Cross-Reference Synthesizer
**Description:** Synthesize findings across multiple papers using Claude. Generate insights and connections.

**Acceptance criteria:**
- [ ] `PaperSynthesizer` takes list of paper summaries and synthesizes
- [ ] Returns: synthesis (str), insights (list), connections (list), citations (list)
- [ ] Respects user depth preference
- [ ] Includes citations to source papers
- [ ] Handles synthesis failures with retry logic (simple prompt on failure)

**Verification:**
- [ ] Test: `synthesizer.synthesize(papers, depth="medium")` returns synthesis
- [ ] Test: Synthesis includes insights and connections
- [ ] Test: Citations reference source papers
- [ ] Test: Retry logic works on failure

**Dependencies:** Task 3.1, Task 1.1

**Files likely touched:**
- `researchagent/processing/synthesizer.py`
- `tests/unit/test_synthesizer.py`

**Estimated scope:** Medium (3-5 files)

---

#### Task 3.3: Insight Generator
**Description:** Generate high-level insights and conclusions from synthesis. Identify future research directions.

**Acceptance criteria:**
- [ ] `InsightGenerator` uses Claude to generate insights
- [ ] Returns: insights (list), future_directions (list), open_questions (list)
- [ ] Insights are actionable and specific
- [ ] Respects user depth preference

**Verification:**
- [ ] Test: `generator.generate(synthesis)` returns insights
- [ ] Test: Insights are specific and actionable
- [ ] Test: Future directions identified

**Dependencies:** Task 3.2

**Files likely touched:**
- `researchagent/processing/insight_generator.py`
- `tests/unit/test_insight_generator.py`

**Estimated scope:** Small (1-2 files)

---

#### Task 3.4: HTML Generator & Templates
**Description:** Generate interactive HTML output from synthesis results. Include expandable sections, concept links, related papers, citation tooltips.

**Acceptance criteria:**
- [ ] `HTMLGenerator` creates interactive HTML from synthesis results
- [ ] Includes: title, abstract, key findings (expandable), synthesis, insights, citations
- [ ] Interactive elements: expandable sections, concept links, related papers sidebar
- [ ] Citation tooltips on hover
- [ ] Rating widget at bottom (1-5 stars + feedback field)
- [ ] Responsive design (mobile-friendly)
- [ ] Embedded CSS/JS (no external dependencies)

**Verification:**
- [ ] Test: `generator.generate(synthesis_result)` returns valid HTML
- [ ] Check: HTML includes all required sections
- [ ] Verify: Interactive elements work (test with browser)
- [ ] Check: Rating widget present at bottom

**Dependencies:** Task 3.3

**Files likely touched:**
- `researchagent/output/html_generator.py`
- `researchagent/output/templates/base.html`
- `researchagent/output/templates/report.html`
- `researchagent/output/assets/interactive.js`
- `researchagent/output/assets/styles.css`
- `tests/unit/test_html_generator.py`

**Estimated scope:** Large (5+ files)

---

### Checkpoint: Synthesis & Output Complete
- [ ] All tests pass: `pytest tests/unit/test_synthesizer.py tests/unit/test_html_generator.py -v`
- [ ] Synthesis pipeline works end-to-end
- [ ] HTML output is interactive and readable
- [ ] Rating widget present and functional

---

### Phase 4: TUI Interface (User Interaction)

#### Task 4.1: Query Manager & Concurrency Control
**Description:** Implement query queue and concurrency control. Handle 8 parallel queries with proper state management.

**Acceptance criteria:**
- [ ] `QueryManager` maintains queue of pending queries
- [ ] Limits concurrent queries to configurable max (default: 8)
- [ ] Tracks query status: pending, processing, completed, failed
- [ ] Supports cancellation of queries
- [ ] Handles query timeouts (default: 300 seconds)

**Verification:**
- [ ] Test: `manager.submit_query(query)` adds to queue
- [ ] Test: Max 8 queries process concurrently
- [ ] Test: Query status updates correctly
- [ ] Test: Timeout cancels query after 300 seconds

**Dependencies:** Task 1.2, Task 2.1

**Files likely touched:**
- `researchagent/core/query_manager.py`
- `tests/unit/test_query_manager.py`

**Estimated scope:** Medium (3-5 files)

---

#### Task 4.2: Synthesis Pipeline Orchestrator
**Description:** Orchestrate full pipeline: domain detection → search → fetch → extract → summarize → synthesize → generate HTML.

**Acceptance criteria:**
- [ ] `SynthesisPipeline` orchestrates all steps
- [ ] Handles errors gracefully (retry, fallback)
- [ ] Respects user preferences (depth, format)
- [ ] Returns complete synthesis result with HTML
- [ ] Logs all steps for debugging

**Verification:**
- [ ] Test: `pipeline.process(query, user_preferences)` returns synthesis result
- [ ] Test: All pipeline steps execute in order
- [ ] Test: Errors handled gracefully
- [ ] Verify: HTML output generated

**Dependencies:** Task 2.5, Task 3.4, Task 4.1

**Files likely touched:**
- `researchagent/core/synthesis_pipeline.py`
- `tests/integration/test_pipeline_end_to_end.py`

**Estimated scope:** Medium (3-5 files)

---

#### Task 4.3: TUI Application (textual)
**Description:** Build main TUI application using textual framework. Implement screens for query input, processing status, results display, and history.

**Acceptance criteria:**
- [ ] Main app screen with query input field
- [ ] Processing status screen showing progress
- [ ] Results display screen showing HTML output
- [ ] History screen showing past queries
- [ ] Navigation between screens
- [ ] Responsive to terminal size changes
- [ ] Keyboard shortcuts for common actions

**Verification:**
- [ ] Run: `python -m researchagent` starts TUI
- [ ] Test: Query input works
- [ ] Test: Status updates during processing
- [ ] Test: Results display correctly
- [ ] Test: History shows past queries

**Dependencies:** Task 4.2

**Files likely touched:**
- `researchagent/ui/app.py`
- `researchagent/ui/screens/home.py`
- `researchagent/ui/screens/processing.py`
- `researchagent/ui/screens/results.py`
- `researchagent/ui/screens/history.py`
- `researchagent/ui/widgets/query_input.py`
- `researchagent/ui/widgets/status_panel.py`
- `researchagent/ui/widgets/result_viewer.py`
- `tests/unit/test_ui_app.py`

**Estimated scope:** Large (5+ files)

---

### Checkpoint: TUI Interface Complete
- [ ] All tests pass: `pytest tests/unit/test_ui_app.py -v`
- [ ] TUI application starts and responds to input
- [ ] Query input works
- [ ] Processing status displays
- [ ] Results display correctly

---

### Phase 5: User Learning (Preferences & Feedback)

#### Task 5.1: User Preference Tracker
**Description:** Track and persist user preferences. Update preferences based on query history and feedback.

**Acceptance criteria:**
- [ ] `PreferenceTracker` stores user preferences in database
- [ ] Tracks: domain, paper_type, depth_level, output_format
- [ ] Updates preferences based on query history
- [ ] Retrieves preferences for future queries
- [ ] Handles new users (default preferences)

**Verification:**
- [ ] Test: `tracker.get_preferences(domain)` returns user preferences
- [ ] Test: Preferences persist across sessions
- [ ] Test: New users get default preferences

**Dependencies:** Task 1.2

**Files likely touched:**
- `researchagent/learning/preference_tracker.py`
- `tests/unit/test_preference_tracker.py`

**Estimated scope:** Small (1-2 files)

---

#### Task 5.2: Feedback Collector
**Description:** Collect user ratings and feedback from HTML output. Store in database.

**Acceptance criteria:**
- [ ] `FeedbackCollector` receives rating (1-5 stars) and optional text feedback
- [ ] Stores feedback in database linked to query
- [ ] Validates rating range (1-5)
- [ ] Handles feedback submission from HTML widget

**Verification:**
- [ ] Test: `collector.submit_feedback(query_id, rating=4, text="helpful")` stores feedback
- [ ] Test: Feedback persists in database
- [ ] Test: Invalid ratings rejected

**Dependencies:** Task 1.2, Task 3.4

**Files likely touched:**
- `researchagent/learning/feedback_collector.py`
- `tests/unit/test_feedback_collector.py`

**Estimated scope:** Small (1-2 files)

---

#### Task 5.3: Preference Updater
**Description:** Update user preferences based on feedback. Improve future queries based on ratings.

**Acceptance criteria:**
- [ ] `PreferenceUpdater` analyzes feedback patterns
- [ ] Adjusts depth_level based on ratings (high ratings → increase depth)
- [ ] Adjusts paper_type based on ratings (high ratings → prefer that type)
- [ ] Updates preferences in database
- [ ] Applies updated preferences to future queries

**Verification:**
- [ ] Test: High ratings increase depth preference
- [ ] Test: Low ratings decrease depth preference
- [ ] Test: Updated preferences applied to next query

**Dependencies:** Task 5.1, Task 5.2

**Files likely touched:**
- `researchagent/learning/preference_updater.py`
- `tests/unit/test_preference_updater.py`

**Estimated scope:** Small (1-2 files)

---

### Checkpoint: User Learning Complete
- [ ] All tests pass: `pytest tests/unit/test_preference_tracker.py tests/unit/test_feedback_collector.py -v`
- [ ] Preferences persist and update
- [ ] Feedback collection works
- [ ] Preferences influence future queries

---

### Phase 6: Integration & Testing (End-to-End)

#### Task 6.1: End-to-End Integration Tests
**Description:** Test complete user flow from query input to HTML output with feedback.

**Acceptance criteria:**
- [ ] E2E test: User enters query → system searches → fetches → synthesizes → outputs HTML
- [ ] E2E test: User rates result → preferences update
- [ ] E2E test: Next query uses updated preferences
- [ ] E2E test: Concurrent queries handled correctly
- [ ] E2E test: Error handling works (source failure, synthesis failure)

**Verification:**
- [ ] Run: `pytest tests/integration/test_pipeline_end_to_end.py -v`
- [ ] All E2E tests pass
- [ ] Coverage ≥60%

**Dependencies:** All previous tasks

**Files likely touched:**
- `tests/integration/test_pipeline_end_to_end.py`
- `tests/integration/test_concurrent_queries.py`
- `tests/integration/test_error_handling.py`

**Estimated scope:** Medium (3-5 files)

---

#### Task 6.2: Error Handling & Resilience Tests
**Description:** Test error handling for all failure modes: source failures, API errors, synthesis failures, timeouts.

**Acceptance criteria:**
- [ ] Test: Source failure → try next source
- [ ] Test: API rate limit → exponential backoff
- [ ] Test: Synthesis failure → retry with simpler prompt
- [ ] Test: Query timeout → return partial results
- [ ] Test: Database failure → use in-memory cache
- [ ] All errors logged appropriately

**Verification:**
- [ ] Run: `pytest tests/integration/test_error_handling.py -v`
- [ ] All error handling tests pass
- [ ] Errors logged correctly

**Dependencies:** All previous tasks

**Files likely touched:**
- `tests/integration/test_error_handling.py`

**Estimated scope:** Medium (3-5 files)

---

#### Task 6.3: Performance & Load Testing
**Description:** Test system performance under load. Verify 8 concurrent queries handled without degradation.

**Acceptance criteria:**
- [ ] Test: 8 concurrent queries complete within 3 minutes
- [ ] Test: HTML output loads in <2 seconds
- [ ] Test: Memory usage stays within limits
- [ ] Test: No query starvation (all queries eventually complete)

**Verification:**
- [ ] Run: `pytest tests/integration/test_performance.py -v`
- [ ] All performance tests pass
- [ ] Load test results documented

**Dependencies:** All previous tasks

**Files likely touched:**
- `tests/integration/test_performance.py`

**Estimated scope:** Medium (3-5 files)

---

#### Task 6.4: Documentation & CLI Commands
**Description:** Write documentation and implement CLI commands for manual operations.

**Acceptance criteria:**
- [ ] README.md with getting started guide
- [ ] ARCHITECTURE.md with system design
- [ ] API.md with internal API reference
- [ ] CLI command: `generate-html --query "..." --output report.html`
- [ ] CLI command: `export-preferences --output prefs.json`
- [ ] CLI command: `clear-cache`

**Verification:**
- [ ] Run: `python -m researchagent --help` shows available commands
- [ ] Test: `python -m researchagent generate-html --query "test" --output test.html` works
- [ ] Check: Documentation is complete and accurate

**Dependencies:** All previous tasks

**Files likely touched:**
- `README.md`
- `docs/ARCHITECTURE.md`
- `docs/API.md`
- `researchagent/cli.py`

**Estimated scope:** Medium (3-5 files)

---

### Final Checkpoint: MVP Complete
- [ ] All tests pass: `pytest tests/ -v --cov=researchagent`
- [ ] Coverage ≥80% for unit tests, ≥60% for integration tests
- [ ] TUI application works end-to-end
- [ ] HTML output is interactive and readable
- [ ] User preferences persist and improve synthesis
- [ ] Documentation complete
- [ ] No hardcoded secrets in code
- [ ] All error modes handled gracefully

---

## Parallelization Opportunities

**Can run in parallel (independent):**
- Task 2.3 (Search agents) — each source is independent
- Task 3.1 & 3.2 & 3.3 — can develop simultaneously with mock data
- Task 4.3 (TUI screens) — different screens can be built in parallel
- Task 5.1 & 5.2 & 5.3 — preference learning components are independent
- Task 6.1 & 6.2 & 6.3 — different test suites can run in parallel

**Must be sequential:**
- Phase 1 → Phase 2 (foundation required)
- Phase 2 → Phase 3 (pipeline required)
- Phase 3 → Phase 4 (synthesis required)
- Phase 4 → Phase 5 (TUI required for feedback collection)
- Phase 5 → Phase 6 (all components required for integration)

---

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| API rate limits from research sources | High | Implement exponential backoff, caching, request queuing |
| Claude API failures during synthesis | High | Retry with simpler prompt, return raw summaries as fallback |
| Large PDF parsing failures | Medium | Use multiple PDF libraries, fallback to abstract extraction |
| TUI responsiveness with 8 concurrent queries | Medium | Use asyncio properly, offload I/O to background tasks |
| User preference learning not improving quality | Medium | Start with simple heuristics, add ML later if needed |
| Database schema changes needed mid-development | Medium | Use Alembic migrations, test schema changes early |
| HTML output too large (performance) | Low | Lazy-load sections, compress CSS/JS, pagination |

---

## Next Steps

1. **Review & Approve:** Confirm this plan aligns with your vision
2. **Start Phase 1:** Begin with project setup and configuration
3. **Parallel Development:** Once foundation is solid, parallelize where possible
4. **Checkpoint Reviews:** Review after each checkpoint before proceeding
5. **Iterate:** Adjust plan based on learnings during implementation

---

## Success Metrics

**By end of MVP:**
- ✅ User can input query via TUI
- ✅ System searches ≥3 sources concurrently
- ✅ Synthesis pipeline completes end-to-end
- ✅ HTML output is interactive and readable
- ✅ User ratings persist and influence future queries
- ✅ Configurable model via LLM_MODEL env var
- ✅ 8 concurrent queries handled without degradation
- ✅ Synthesis completes within 3 minutes (typical)
- ✅ Unit test coverage ≥80%
- ✅ Integration test coverage ≥60%
