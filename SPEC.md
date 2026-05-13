# Spec: ResearchAgent — TUI-Based AI Research Synthesis System

## Objective

**What we're building:**
A fully automated research synthesis system that transforms user questions into expert-level summaries backed by highly cited papers and articles. Users input keywords or questions via a TUI interface, the system searches multiple authoritative sources concurrently, synthesizes findings across papers, and outputs interactive HTML visualizations with citations.

**Target users:**
- Researchers exploring new domains
- Students learning complex topics
- Professionals needing quick domain overviews
- Anyone seeking credible, synthesized knowledge

**Success looks like:**
- User enters "quantum computing applications" → system returns a structured HTML report with key findings, citations, and interactive concept relationships within 2-3 minutes
- System handles 8 concurrent queries without degradation
- User ratings improve synthesis quality over time (self-evolving mechanism)
- HTML output is readable, interactive, and citable

**Acceptance Criteria:**
- MVP supports ≥3 domains (AI/ML, Biology, Physics)
- Synthesis pipeline completes end-to-end: search → fetch → extract → summarize → synthesize → generate HTML
- User preferences persist and influence future queries
- Configurable base model via `LLM_MODEL` environment variable
- Concurrent query handling (8 parallel default)
- Complete synthesis before output (batch processing, not streaming)

---

## Tech Stack

| Component | Choice | Rationale |
|-----------|--------|-----------|
| Language | Python 3.11+ | Claude SDK native, fastest MVP |
| TUI Framework | `textual` | Async-friendly, modern, better UX than `rich` |
| Async Runtime | `asyncio` | Python native, no extra runtime |
| Storage | SQLite (MVP) → PostgreSQL (v2) | Local first, scalable later |
| LLM Integration | Anthropic Claude SDK | Configurable model, prompt caching support |
| HTTP Client | `httpx` | Async, connection pooling |
| HTML Generation | Jinja2 + custom CSS | Templated, interactive output |
| Testing | `pytest` + `pytest-asyncio` | Standard Python testing |
| Config Management | `pydantic` + `.env` files | Type-safe, environment-aware |

**Key Dependencies (MVP):**
```
anthropic>=0.28.0
textual>=0.50.0
httpx>=0.25.0
pydantic>=2.0.0
pydantic-settings>=2.0.0
jinja2>=3.1.0
pytest>=7.4.0
pytest-asyncio>=0.21.0
python-dotenv>=1.0.0
```

---

## Commands

```bash
# Development
python -m pip install -e ".[dev]"

# Run the TUI application
python -m researchagent

# Run with custom model
LLM_MODEL=claude-sonnet-4-6 python -m researchagent

# Run tests
pytest tests/ -v --cov=researchagent

# Run tests with async support
pytest tests/ -v --asyncio-mode=auto

# Lint and format
ruff check researchagent/ --fix
black researchagent/ tests/

# Type checking
mypy researchagent/

# Build HTML output (manual)
python -m researchagent.cli generate-html --query "quantum computing" --output report.html
```

---

## Project Structure

```
researchagent/
├── __main__.py                 # Entry point for TUI
├── __init__.py
├── config.py                   # Configuration schema (pydantic)
├── cli.py                      # CLI commands (generate-html, export-prefs, etc.)
│
├── core/
│   ├── __init__.py
│   ├── query_manager.py        # Query queue, concurrency control (8 parallel)
│   ├── domain_detector.py      # Auto-detect domain from query
│   └── synthesis_pipeline.py   # Main pipeline orchestrator
│
├── sources/
│   ├── __init__.py
│   ├── base.py                 # Abstract source interface
│   ├── arxiv.py                # arXiv API integration
│   ├── pubmed.py               # PubMed API integration
│   ├── semantic_scholar.py     # Semantic Scholar API
│   ├── crossref.py             # CrossRef API
│   ├── google_scholar.py       # Google Scholar scraper (fallback)
│   └── source_registry.py      # Domain → sources mapping
│
├── processing/
│   ├── __init__.py
│   ├── fetcher.py              # Download papers, extract text
│   ├── extractor.py            # Extract key findings from papers
│   ├── summarizer.py           # Summarize individual papers (Claude)
│   ├── synthesizer.py          # Cross-reference & synthesize (Claude)
│   └── insight_generator.py    # Generate insights & conclusions
│
├── storage/
│   ├── __init__.py
│   ├── database.py             # SQLite ORM (sqlalchemy)
│   ├── models.py               # Query history, user preferences, results
│   └── migrations/             # Alembic migrations (future)
│
├── ui/
│   ├── __init__.py
│   ├── app.py                  # Main TUI application (textual)
│   ├── screens/
│   │   ├── home.py             # Home screen (input query)
│   │   ├── processing.py       # Processing status screen
│   │   ├── results.py          # Results display screen
│   │   └── history.py          # Query history screen
│   ├── widgets/
│   │   ├── query_input.py      # Query input widget
│   │   ├── status_panel.py     # Status/progress panel
│   │   └── result_viewer.py    # Result viewer widget
│   └── styles.css              # TUI styling
│
├── output/
│   ├── __init__.py
│   ├── html_generator.py       # Generate interactive HTML
│   ├── templates/
│   │   ├── base.html           # Base template
│   │   ├── report.html         # Report template
│   │   └── styles.css          # HTML styling
│   └── assets/
│       └── interactive.js      # Client-side interactivity
│
├── learning/
│   ├── __init__.py
│   ├── preference_tracker.py   # Track user preferences
│   ├── feedback_collector.py   # Collect ratings/feedback
│   └── preference_updater.py   # Update future queries based on feedback
│
└── utils/
    ├── __init__.py
    ├── logger.py               # Logging setup
    ├── errors.py               # Custom exceptions
    └── helpers.py              # Utility functions

tests/
├── __init__.py
├── unit/
│   ├── test_domain_detector.py
│   ├── test_query_manager.py
│   ├── test_synthesizer.py
│   └── test_preference_tracker.py
├── integration/
│   ├── test_pipeline_end_to_end.py
│   ├── test_source_integration.py
│   └── test_storage.py
└── fixtures/
    ├── sample_papers.py
    └── mock_responses.py

docs/
├── README.md                   # Getting started
├── ARCHITECTURE.md             # System design deep-dive
├── API.md                      # Internal API reference
├── SOURCES.md                  # Research source documentation
└── FUTURE.md                   # v2+ roadmap

pyproject.toml                  # Project metadata, dependencies
.env.example                    # Environment variables template
.gitignore
```

---

## Code Style

**Python conventions:**
- Type hints on all functions: `def fetch_papers(query: str, limit: int = 10) -> list[Paper]:`
- Async functions prefixed with `async def`, called with `await`
- Docstrings: Google style, one-liner for simple functions
- Constants: `UPPERCASE_WITH_UNDERSCORES`
- Private methods: `_leading_underscore`
- Classes: `PascalCase`, functions: `snake_case`

**Example — Good style:**

```python
from typing import Optional
from anthropic import Anthropic

class PaperSynthesizer:
    """Synthesizes findings across multiple papers using Claude."""
    
    def __init__(self, model: str = "claude-opus-4-7"):
        self.client = Anthropic()
        self.model = model
    
    async def synthesize(
        self,
        papers: list[Paper],
        user_preferences: Optional[UserPreferences] = None,
    ) -> SynthesisResult:
        """Synthesize findings across papers, respecting user preferences.
        
        Args:
            papers: List of papers to synthesize
            user_preferences: User's depth/format preferences
            
        Returns:
            SynthesisResult with insights and citations
        """
        prompt = self._build_synthesis_prompt(papers, user_preferences)
        
        response = await self.client.messages.create(
            model=self.model,
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}],
        )
        
        return self._parse_response(response)
    
    def _build_synthesis_prompt(
        self,
        papers: list[Paper],
        preferences: Optional[UserPreferences],
    ) -> str:
        """Build synthesis prompt with user preferences."""
        depth = preferences.depth_level if preferences else "medium"
        return f"Synthesize these papers at {depth} depth: {papers}"
```

**Error handling:**
```python
class ResearchAgentError(Exception):
    """Base exception for ResearchAgent."""
    pass

class SourceError(ResearchAgentError):
    """Raised when a research source fails."""
    pass

class SynthesisError(ResearchAgentError):
    """Raised when synthesis pipeline fails."""
    pass

# Usage
try:
    papers = await fetch_papers(query)
except SourceError as e:
    logger.warning(f"Source failed, trying fallback: {e}")
    papers = await fetch_papers_fallback(query)
```

---

## Testing Strategy

**Framework:** `pytest` + `pytest-asyncio` for async tests

**Test Levels:**

| Level | Framework | Location | Coverage Target |
|-------|-----------|----------|-----------------|
| Unit | pytest | `tests/unit/` | Core logic (domain detection, preference tracking) |
| Integration | pytest | `tests/integration/` | Pipeline end-to-end, source APIs, storage |
| E2E | Manual + TUI automation | `tests/e2e/` | Full user flow (query → HTML output) |

**Test Structure:**

```python
# tests/unit/test_synthesizer.py
import pytest
from researchagent.processing.synthesizer import PaperSynthesizer
from tests.fixtures import sample_papers

@pytest.mark.asyncio
async def test_synthesizer_respects_user_depth_preference():
    """Synthesizer should adjust output depth based on user preference."""
    synthesizer = PaperSynthesizer()
    papers = sample_papers()
    
    result = await synthesizer.synthesize(
        papers,
        user_preferences=UserPreferences(depth_level="deep"),
    )
    
    assert len(result.insights) >= 5  # Deep synthesis has more insights
    assert result.citation_count >= len(papers)

@pytest.mark.asyncio
async def test_synthesizer_handles_empty_papers():
    """Synthesizer should gracefully handle empty paper list."""
    synthesizer = PaperSynthesizer()
    
    with pytest.raises(ValueError, match="No papers to synthesize"):
        await synthesizer.synthesize([])
```

**Coverage expectations:**
- Unit tests: ≥80% coverage
- Integration tests: ≥60% coverage
- E2E: Manual verification of key flows

**Running tests:**
```bash
pytest tests/ -v --cov=researchagent --cov-report=html
```

---

## Boundaries

### Always Do
- ✅ Validate user input (query length, special characters)
- ✅ Log all API calls and errors (for debugging)
- ✅ Handle source failures gracefully (try next source)
- ✅ Persist user preferences to database
- ✅ Run tests before committing
- ✅ Type-hint all functions
- ✅ Use async/await for I/O operations

### Ask First
- ❓ Adding new research sources (requires API integration, testing)
- ❓ Changing database schema (affects stored preferences)
- ❓ Modifying synthesis prompt (affects output quality)
- ❓ Adding new dependencies (bloat, security review)
- ❓ Changing concurrency limits (performance implications)
- ❓ Modifying HTML output format (user experience impact)

### Never Do
- ❌ Commit API keys or secrets (use `.env` files)
- ❌ Store user queries without consent (privacy)
- ❌ Modify vendor code or dependencies directly
- ❌ Skip error handling for "it won't happen" cases
- ❌ Remove failing tests without approval
- ❌ Hardcode configuration values (use config.py)
- ❌ Make blocking I/O calls (use async)

---

## Configuration Schema

**Environment Variables (.env):**
```bash
# Claude API
ANTHROPIC_API_KEY=sk-ant-...
LLM_MODEL=claude-opus-4-7  # Configurable base model

# Research APIs
SEMANTIC_SCHOLAR_API_KEY=optional
CROSSREF_EMAIL=your-email@example.com

# System
CONCURRENT_QUERIES=8
QUERY_TIMEOUT_SECONDS=300
LOG_LEVEL=INFO
DATABASE_PATH=./researchagent.db
OUTPUT_DIR=./outputs
```

**Config Schema (pydantic):**
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application configuration."""
    
    anthropic_api_key: str
    llm_model: str = "claude-opus-4-7"
    
    concurrent_queries: int = 8
    query_timeout_seconds: int = 300
    
    semantic_scholar_api_key: Optional[str] = None
    crossref_email: Optional[str] = None
    
    database_path: str = "./researchagent.db"
    output_dir: str = "./outputs"
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
```

---

## Database Schema

**User Preferences:**
```sql
CREATE TABLE user_preferences (
    id INTEGER PRIMARY KEY,
    domain TEXT NOT NULL,
    paper_type TEXT,  -- "research", "review", "preprint"
    depth_level TEXT,  -- "shallow", "medium", "deep"
    output_format TEXT,  -- "html", "markdown"
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Query History:**
```sql
CREATE TABLE queries (
    id INTEGER PRIMARY KEY,
    query_text TEXT NOT NULL,
    domain TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status TEXT,  -- "pending", "processing", "completed", "failed"
    result_path TEXT,  -- Path to HTML output
    user_rating INTEGER,  -- 1-5 stars
    feedback TEXT,  -- User feedback
    processing_time_seconds FLOAT
);
```

**Papers Cache:**
```sql
CREATE TABLE papers (
    id INTEGER PRIMARY KEY,
    query_id INTEGER,
    source TEXT,  -- "arxiv", "pubmed", etc.
    source_id TEXT UNIQUE,
    title TEXT,
    authors TEXT,
    abstract TEXT,
    url TEXT,
    published_date DATE,
    citation_count INTEGER,
    fetched_at TIMESTAMP,
    FOREIGN KEY (query_id) REFERENCES queries(id)
);
```

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    TUI Interface (textual)                   │
│  Input: Keywords/Questions | Output: Processing Status      │
└────────────────┬────────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────────┐
│              Query Manager & Concurrency Control             │
│  (Queue, 8 parallel limit, domain detection)                │
└────────────────┬────────────────────────────────────────────┘
                 │
    ┌────────────┼────────────┐
    │            │            │
┌───▼──┐  ┌─────▼────┐  ┌────▼────┐
│Search│  │ Fetch &  │  │Synthesis│
│Agent │  │ Extract  │  │ Agent   │
│      │  │          │  │         │
│ • arXiv│ • PDF     │  │ • Cross-│
│ • Pub- │   parsing │  │   ref   │
│   Med  │ • Text    │  │ • Synth │
│ • Sem. │   extract │  │ • Claude│
│   Sch. │          │  │         │
└──────┘  └──────────┘  └────────┘
    │            │            │
    └────────────┼────────────┘
                 │
         ┌───────▼────────┐
         │ HTML Generator │
         │ & Formatter    │
         └────────────────┘
                 │
         ┌───────▼────────┐
         │ User Preference│
         │ Learning       │
         └────────────────┘
                 │
         ┌───────▼────────┐
         │ SQLite Storage │
         │ (Preferences,  │
         │  History)      │
         └────────────────┘
```

**Data Flow:**
1. User enters query in TUI
2. Query Manager detects domain, creates queue entry
3. Search Agent queries multiple sources concurrently
4. Fetch & Extract processes papers in parallel
5. Synthesis Agent synthesizes findings (Claude)
6. HTML Generator creates interactive output
7. User rates result → Preference Learning updates model
8. Next query uses updated preferences

---

## MVP Scope (Phase 1)

**In Scope:**
- ✅ Multi-domain support (AI/ML, Biology, Physics)
- ✅ Concurrent query handling (8 parallel)
- ✅ Deep synthesis pipeline (extract → summarize → synthesize → insights)
- ✅ Interactive HTML output (expandable sections, citations, related concepts)
- ✅ User preference learning (rating-based feedback)
- ✅ Configurable base model (LLM_MODEL env var)
- ✅ TUI interface (query input, status, history)
- ✅ Batch processing (complete synthesis before output)

**Out of Scope (v2+):**
- ❌ Cloud deployment / multi-user
- ❌ Real-time streaming results
- ❌ Advanced visualization (concept graphs, network diagrams)
- ❌ Multi-language support
- ❌ Mobile app
- ❌ Collaborative features
- ❌ Advanced caching / indexing

---

## Future Upgrade Paths

**v2 (Post-MVP):**
- PostgreSQL migration (multi-user support)
- Advanced HTML (concept graphs, related papers)
- Caching layer (Redis) for repeated queries
- API server (REST/GraphQL) for programmatic access
- User accounts & cloud sync

**v3:**
- Multi-language support
- Advanced preference learning (ML-based ranking)
- Collaborative research (shared queries, annotations)
- Citation export (BibTeX, RIS)
- Integration with reference managers (Zotero, Mendeley)

**v4+:**
- Mobile app (iOS/Android)
- Real-time collaboration
- Custom domain training
- Advanced visualization (interactive concept maps)

---

## Error Handling & Resilience

**Source Failures:**
- If one source fails, try next source in priority order
- Log failure, continue with available sources
- Graceful degradation: fewer papers → still synthesize

**API Rate Limits:**
- Implement exponential backoff (1s → 2s → 4s)
- Queue requests if rate-limited
- Cache results to reduce API calls

**Synthesis Failures:**
- If Claude API fails, retry with exponential backoff
- If synthesis fails, return raw paper summaries
- Log error, notify user

**Database Failures:**
- Use in-memory cache as fallback
- Persist cache to disk on shutdown
- Warn user if preferences not saved

**Timeout Handling:**
- Query timeout: 300 seconds default (configurable)
- Individual source timeout: 30 seconds
- Synthesis timeout: 60 seconds
- Return partial results if timeout

---

## Success Criteria

**Functional:**
- [ ] User can input query via TUI
- [ ] System searches ≥3 sources concurrently
- [ ] Synthesis pipeline completes end-to-end
- [ ] HTML output is interactive and readable
- [ ] User ratings persist and influence future queries
- [ ] Configurable model via LLM_MODEL env var
- [ ] 8 concurrent queries handled without degradation

**Non-Functional:**
- [ ] Synthesis completes within 3 minutes (typical)
- [ ] HTML output loads in <2 seconds
- [ ] Unit test coverage ≥80%
- [ ] Integration test coverage ≥60%
- [ ] No hardcoded secrets in code
- [ ] Graceful error handling for all failure modes

**User Experience:**
- [ ] TUI is responsive and intuitive
- [ ] Status updates show progress
- [ ] Results are easy to understand and cite
- [ ] User preferences improve synthesis quality over time

---

## Decisions on Open Questions

1. **Source Priority:** ✅ Weight sources by domain (e.g., arXiv for CS, PubMed for Biology)
   - Domain detector maps query → domain → source priority list
   - Example: "quantum computing" → CS domain → [arXiv, Semantic Scholar, Google Scholar, CrossRef]

2. **Synthesis Depth:** ✅ User preferences adjust Claude's synthesis prompt
   - Shallow: Key findings only, 1-2 paragraphs per topic
   - Medium: Balanced findings + context, 3-4 paragraphs per topic
   - Deep: Comprehensive analysis, 5+ paragraphs, includes limitations & future work

3. **HTML Interactivity:** ✅ Expandable sections, concept links, related papers
   - Expandable sections for each finding (click to expand/collapse)
   - Concept links (hover to show definition, click to search)
   - Related papers sidebar (papers cited in synthesis)
   - Citation tooltips (hover to see full citation)

4. **Feedback Collection:** ✅ Collect ratings at the end of HTML output
   - 1-5 star rating widget at bottom of HTML
   - Optional text feedback field
   - "Submit" button saves to database
   - Confirmation message after submission

5. **Caching Strategy:** ✅ Cache by source
   - Key: `{source}:{source_id}` (e.g., `arxiv:2301.12345`)
   - Prevents duplicate fetches across queries
   - Expires after 30 days (configurable)

6. **Error Recovery:** ✅ Retry with simpler prompt
   - First attempt: Full synthesis prompt with depth preference
   - If fails: Retry with simplified prompt (no depth preference)
   - If fails again: Return raw paper summaries with error message

---

## Next Steps

1. **Review & Approve:** Confirm this spec aligns with your vision
2. **Clarify Open Questions:** Answer the questions above
3. **Create Implementation Plan:** Break into phases and tasks
4. **Begin Phase 1:** Start with core pipeline (search → fetch → synthesize)
