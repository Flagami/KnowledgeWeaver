# KnowledgeWeaver 🧠

**Intelligent Research Synthesis System** — Automatically search, analyze, and synthesize research papers using Claude AI.

---

## 🎯 The Problem You're Solving

**Drowning in research papers?** Researchers and knowledge workers face a critical challenge: the exponential growth of academic literature makes it impossible to stay current. You spend hours:

- 🔍 **Searching** across fragmented databases with inconsistent results
- 📚 **Reading** dozens of papers to find relevant insights
- 🤔 **Synthesizing** findings manually across multiple sources
- 📝 **Extracting** key insights and connections by hand
- 🔄 **Repeating** the same research process for similar queries

**Result?** Wasted time, missed connections, and incomplete understanding of your research domain.

## ✨ The KnowledgeWeaver Solution

**Meet your AI research assistant.** KnowledgeWeaver combines **multi-agent AI orchestration** with **intelligent synthesis** to transform how you discover and understand research:

### 🤖 AI-Powered Agent Architecture

KnowledgeWeaver deploys a sophisticated **multi-agent system** that works together seamlessly:

1. **Domain Detection Agent** — Intelligently identifies your research domain and selects optimal sources
2. **Search Agents** (4 specialized agents) — Simultaneously query arXiv, PubMed, Semantic Scholar, and CrossRef for comprehensive coverage
3. **Paper Analysis Agent** — Extracts and caches paper content with intelligent text extraction
4. **Summarization Agent** — Uses Claude to create concise, accurate paper summaries
5. **Synthesis Agent** — Intelligently combines findings across papers to identify patterns and connections
6. **Insight Generation Agent** — Generates actionable insights and identifies future research directions
7. **Learning Agent** — Adapts to your preferences based on feedback, continuously improving results

### 🚀 Unique AI Capabilities

- **Concurrent Multi-Source Search** — Query 4 research databases simultaneously for comprehensive coverage
- **Claude-Powered Synthesis** — Uses advanced Claude AI to understand context and generate meaningful insights
- **Adaptive Learning** — Learns from your feedback to personalize results and improve recommendations
- **Intelligent Fallbacks** — Gracefully handles API failures with circuit breakers and automatic degradation
- **Interactive Intelligence** — Beautiful HTML reports with expandable sections, citations, and 1-5 star feedback

### 💡 Real-World Impact

- ⏱️ **Save 80% of research time** — From hours of manual work to minutes of AI-powered synthesis
- 🎯 **Discover hidden connections** — Find relationships between papers you'd never find manually
- 📈 **Stay current** — Automatically synthesize the latest research in your domain
- 🧠 **Deeper understanding** — Get actionable insights, not just summaries
- 🔄 **Continuous improvement** — System learns from your feedback to get smarter over time

---

## Overview

KnowledgeWeaver is a comprehensive research synthesis platform that:

- 🔍 **Searches** multiple research databases (arXiv, PubMed, Semantic Scholar, CrossRef)
- 📄 **Fetches** and extracts text from research papers
- 🤖 **Synthesizes** findings using Claude AI
- 💡 **Generates** actionable insights and future research directions
- 📊 **Creates** interactive HTML reports
- 🎯 **Learns** from user feedback to improve recommendations
- ⚡ **Handles** concurrent queries with intelligent concurrency control

## Quick Start

### Installation (Recommended: Using `uv`)

The fastest way to get started is using [uv](https://github.com/astral-sh/uv), a blazingly fast Python package installer:

```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone the repository
git clone https://github.com/yourusername/KnowledgeWeaver.git
cd KnowledgeWeaver

# Create virtual environment and install dependencies with uv
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys
```

### Installation (Alternative: Using pip)

```bash
# Clone the repository
git clone https://github.com/yourusername/KnowledgeWeaver.git
cd KnowledgeWeaver

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys
```

### Configuration

Create a `.env` file with:

```env
# Claude API Configuration (Required)
ANTHROPIC_API_KEY=sk-ant-your-api-key-here
ANTHROPIC_BASE_URL=https://api.anthropic.com
ANTHROPIC_MODEL=claude-opus-4-7

# Research APIs (Optional)
SEMANTIC_SCHOLAR_API_KEY=
CROSSREF_EMAIL=your-email@example.com

# System Configuration
CONCURRENT_QUERIES=8
QUERY_TIMEOUT_SECONDS=300
LOG_LEVEL=INFO

# Storage
DATABASE_PATH=./knowledgeweaver.db
OUTPUT_DIR=./outputs

# Development
DEBUG=false
```

**Configuration Variables:**
- `ANTHROPIC_API_KEY` — Your Anthropic API key (required)
- `ANTHROPIC_BASE_URL` — Anthropic API endpoint (default: https://api.anthropic.com)
- `ANTHROPIC_MODEL` — Claude model to use (default: claude-opus-4-7)
- `CONCURRENT_QUERIES` — Maximum concurrent queries (default: 8)
- `QUERY_TIMEOUT_SECONDS` — Query timeout in seconds (default: 300)
- `LOG_LEVEL` — Logging level (default: INFO)
- `DATABASE_PATH` — SQLite database path (default: ./knowledgeweaver.db)
- `OUTPUT_DIR` — Output directory for reports (default: ./outputs)

### Basic Usage

```python
from knowledgeweaver.core.synthesis_pipeline import SynthesisPipeline
from knowledgeweaver.core.query_manager import Query

# Initialize pipeline
pipeline = SynthesisPipeline()

# Create a query
query = Query(query_text="quantum computing applications", domain="Physics")

# Process the query
result_path = await pipeline.process(query, depth="medium")
print(f"Report generated: {result_path}")
```

## Architecture

### Phase 1: Foundation
- **Configuration Management** — Environment-based settings with pydantic
- **Database Layer** — SQLAlchemy ORM with SQLite
- **Logging System** — Structured logging with file rotation
- **Error Handling** — Custom exception hierarchy

### Phase 2: Research Pipeline
- **Domain Detection** — Identifies research domain from queries
- **Source Registry** — Manages research sources with priority weighting
- **Search Agents** — Integrates arXiv, PubMed, Semantic Scholar, CrossRef
- **Paper Fetcher** — Downloads and caches papers with text extraction
- **Key Findings Extractor** — Uses Claude to extract structured findings

### Phase 3: Synthesis & Output
- **Paper Summarizer** — Summarizes individual papers with Claude
- **Cross-Reference Synthesizer** — Synthesizes findings across papers
- **Insight Generator** — Generates high-level insights and future directions
- **HTML Generator** — Creates interactive, responsive HTML reports

### Phase 4: TUI Interface
- **Query Manager** — Manages query queue with concurrency control
- **Synthesis Pipeline Orchestrator** — Coordinates all pipeline steps
- **TUI Application** — Terminal user interface using textual framework

### Phase 5: User Learning
- **Preference Tracker** — Manages user preferences by domain
- **Feedback Collector** — Collects and analyzes user ratings
- **Preference Updater** — Learns from feedback to improve recommendations

### Phase 6: Integration & Testing
- **End-to-End Tests** — Integration tests for complete workflows
- **Error Handling & Recovery** — Circuit breakers and retry logic
- **Performance Optimization** — Caching and performance monitoring
- **Documentation** — Comprehensive guides and API documentation

## Features

### 🔍 Multi-Source Search
- **arXiv** — AI/ML and physics papers
- **PubMed** — Biomedical literature
- **Semantic Scholar** — Multi-domain with citation counts
- **CrossRef** — Comprehensive DOI database

### 🤖 Claude-Powered Analysis
- Intelligent paper summarization
- Cross-paper synthesis
- Insight generation
- Configurable depth (shallow/medium/deep)

### 📊 Interactive Reports
- Expandable sections
- Citation tracking
- Related papers sidebar
- 1-5 star rating widget
- Responsive design (mobile-friendly)

### 🎯 Adaptive Learning
- Tracks user preferences by domain
- Analyzes feedback patterns
- Recommends preference adjustments
- Generates improvement suggestions

### ⚡ Performance
- Concurrent query processing (default: 8 parallel)
- Paper text caching (30-day TTL)
- Circuit breaker pattern for API failures
- Exponential backoff retry logic

## API Reference

### Query Manager

```python
from knowledgeweaver.core.query_manager import QueryManager

manager = QueryManager(max_concurrent=8)

# Submit query
query = await manager.submit_query("machine learning", domain="AI/ML")

# Get status
status = manager.get_query_status(query.query_id)

# Get statistics
stats = manager.get_stats()
```

### Synthesis Pipeline

```python
from knowledgeweaver.core.synthesis_pipeline import SynthesisPipeline

pipeline = SynthesisPipeline()

# Process query
result_path = await pipeline.process(query, depth="medium")
```

### Preference Tracking

```python
from knowledgeweaver.learning.preference_tracker import PreferenceTracker

tracker = PreferenceTracker()

# Get preferences
prefs = tracker.get_preferences("AI/ML")

# Update preferences
tracker.set_preferences("AI/ML", depth_level="deep")
```

### Feedback Collection

```python
from knowledgeweaver.learning.feedback_collector import FeedbackCollector

collector = FeedbackCollector()

# Submit feedback
collector.submit_feedback(query_id, rating=5, feedback_text="Great synthesis!")

# Get analysis
analysis = collector.analyze_feedback_patterns("AI/ML")
```

## Testing

### Run All Tests

```bash
pytest tests/unit/ -v
pytest tests/integration/ -v
```

### Run Specific Test Suite

```bash
# Phase 1 tests
pytest tests/unit/test_phase1_foundation.py -v

# Phase 2 tests
pytest tests/unit/test_phase2_research_pipeline.py -v

# Integration tests
pytest tests/integration/test_e2e_integration.py -v
```

### Test Coverage

```bash
pytest tests/ --cov=knowledgeweaver --cov-report=html
```

## Performance

### Benchmarks

- **Domain Detection**: ~10ms
- **Paper Search**: ~2-5s per source
- **Text Extraction**: ~500ms per paper
- **Paper Summarization**: ~3-5s per paper
- **Synthesis**: ~5-10s for 5 papers
- **HTML Generation**: ~500ms

### Optimization Tips

1. **Enable Caching** — Paper text is cached for 30 days
2. **Adjust Concurrency** — Set `CONCURRENT_QUERIES` based on system resources
3. **Use Shallow Depth** — Faster synthesis with less detail
4. **Batch Queries** — Process multiple queries concurrently

## Error Handling

### Circuit Breaker Pattern

Automatically opens circuit after 5 consecutive failures, attempts recovery after 60 seconds.

```python
from knowledgeweaver.core.error_handler import CircuitBreaker

cb = CircuitBreaker(name="arxiv", failure_threshold=5)
result = await cb.call(search_function, query)
```

### Retry Logic

Exponential backoff with configurable max retries.

```python
from knowledgeweaver.core.error_handler import RetryStrategy

retry = RetryStrategy(max_retries=3, initial_delay=1.0)
result = await retry.execute(function, *args)
```

### Graceful Degradation

Automatically falls back to simpler strategies when services fail:
- Falls back to abstract when full text unavailable
- Uses single source when multiple sources fail
- Uses shallow synthesis when deep synthesis fails

## Troubleshooting

### API Rate Limits

If you hit rate limits:
1. Reduce `CONCURRENT_QUERIES` in `.env`
2. Increase `QUERY_TIMEOUT_SECONDS`
3. Use `depth="shallow"` for faster processing

### Memory Issues

If experiencing high memory usage:
1. Reduce `CONCURRENT_QUERIES`
2. Clear paper cache: `rm -rf output/paper_cache`
3. Limit papers per query in pipeline

### Database Errors

If database is locked:
1. Ensure only one instance is running
2. Delete `knowledgeweaver.db` to reset
3. Check file permissions on database directory

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## License

MIT License — See LICENSE file for details

## Citation

If you use KnowledgeWeaver in your research, please cite:

```bibtex
@software{knowledgeweaver2024,
  title={KnowledgeWeaver: Intelligent Research Synthesis System},
  author={Your Name},
  year={2024},
  url={https://github.com/yourusername/KnowledgeWeaver}
}
```

## Support

- 📖 [Documentation](./docs/)
- 🐛 [Issue Tracker](https://github.com/yourusername/KnowledgeWeaver/issues)
- 💬 [Discussions](https://github.com/yourusername/KnowledgeWeaver/discussions)

---

**Built with ❤️ using Claude AI**
