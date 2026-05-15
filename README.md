# KnowledgeWeaver

**Intelligent Research Synthesis System** — Search, analyze, and synthesize research papers using Claude AI, served through a web interface.

---

## What it does

KnowledgeWeaver takes a research topic, queries multiple academic databases concurrently, summarizes the papers with Claude, and synthesizes the findings into an interactive HTML report. You interact with it through a browser-based UI.

**Research sources:**
- arXiv — preprints in physics, math, CS, and more
- PubMed — biomedical literature
- Semantic Scholar — multi-domain with citation counts
- CrossRef — comprehensive DOI database

**Pipeline stages:**
1. Domain detection — identifies the research domain from your query
2. Concurrent search — queries all four sources in parallel
3. Paper fetching — downloads and caches paper text
4. Summarization — Claude summarizes each paper
5. Synthesis — Claude identifies patterns and connections across papers
6. Insight generation — produces actionable insights and future directions
7. HTML report — generates an interactive report with citations and ratings

---

## Quick start

### Prerequisites

- Python 3.11+
- An [Anthropic API key](https://console.anthropic.com/)

### Install with uv (recommended)

[uv](https://github.com/astral-sh/uv) is the fastest way to get started:

```bash
# Install uv if you don't have it
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone the repo
git clone https://github.com/Flagami/KnowledgeWeaver.git
cd KnowledgeWeaver

# Create virtual environment and install dependencies
uv venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
uv pip install -e ".[dev]"
```

### Install with pip

```bash
git clone https://github.com/Flagami/KnowledgeWeaver.git
cd KnowledgeWeaver

python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

### Configure

Copy the example env file and add your API key:

```bash
cp .env.example .env
```

Edit `.env`:

```env
# Required
ANTHROPIC_API_KEY=sk-ant-your-key-here

# Optional — defaults shown
ANTHROPIC_MODEL=claude-opus-4-7
CONCURRENT_QUERIES=8
QUERY_TIMEOUT_SECONDS=300
LOG_LEVEL=INFO
DATABASE_PATH=./knowledgeweaver.db
OUTPUT_DIR=./outputs
CROSSREF_EMAIL=your-email@example.com
```

### Run

```bash
python run_web_ui.py
```

Open `http://localhost:8000` in your browser. Enter a research topic and click Explore.

---

## Deployment

### Local

```bash
# Activate your virtual environment, then:
python run_web_ui.py
# → http://localhost:8000
```

### Docker

Create a `docker-compose.yml`:

```yaml
version: '3.8'
services:
  knowledgeweaver:
    build: .
    environment:
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - ANTHROPIC_MODEL=claude-opus-4-7
      - DATABASE_PATH=/app/data/knowledgeweaver.db
      - OUTPUT_DIR=/app/output
    volumes:
      - ./data:/app/data
      - ./output:/app/output
      - ./logs:/app/logs
    ports:
      - "8000:8000"
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

```bash
# Start
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

---

## Architecture

### Core pipeline (`knowledgeweaver/core/`)
- `synthesis_pipeline.py` — orchestrates the full research workflow
- `query_manager.py` — manages query queue with concurrency control
- `domain_detector.py` — identifies research domain from query text
- `error_handler.py` — circuit breaker and retry logic

### Research sources (`knowledgeweaver/sources/`)
- `arxiv.py`, `pubmed.py`, `semantic_scholar.py`, `crossref.py` — source adapters

### Processing (`knowledgeweaver/processing/`)
- `fetcher.py` — downloads and caches paper text (30-day TTL)
- `extractor.py` — extracts text from PDFs
- `summarizer.py` — Claude-powered paper summarization
- `synthesizer.py` — cross-paper synthesis
- `insight_generator.py` — high-level insights and future directions

### Output (`knowledgeweaver/output/`)
- `html_generator.py` — generates interactive HTML reports with citations and ratings

### Learning (`knowledgeweaver/learning/`)
- `preference_tracker.py` — stores user preferences by domain
- `feedback_collector.py` — collects and analyzes star ratings
- `preference_updater.py` — adjusts recommendations based on feedback

### Web UI (`knowledgeweaver/ui/`)
- FastAPI backend serving a single-page interface at `http://localhost:8000`
- Editorial aesthetic: warm ivory palette, serif typography, gold accents
- Real-time research status with animated topic bubble cloud
- Research library with status badges and gold processing indicator
- Toast notifications for research events

---

## Python API

You can also drive the pipeline directly from Python:

```python
import asyncio
from knowledgeweaver.core.synthesis_pipeline import SynthesisPipeline
from knowledgeweaver.core.query_manager import Query

async def main():
    pipeline = SynthesisPipeline()
    query = Query(query_text="quantum computing applications", domain="Physics")
    result_path = await pipeline.process(query, depth="medium")
    print(f"Report: {result_path}")

asyncio.run(main())
```

Depth options: `shallow` (fast), `medium` (default), `deep` (thorough).

---

## Testing

```bash
# Run all tests (requires pytest-cov)
pytest tests/

# Run without coverage
pytest tests/ --override-ini="addopts="

# Unit tests only
pytest tests/unit/ --override-ini="addopts=" -v

# Integration tests
pytest tests/integration/ --override-ini="addopts=" -v
```

---

## Troubleshooting

**`ANTHROPIC_API_KEY not found`** — check that `.env` exists and contains your key.

**Port 8000 in use** — find and kill the process: `lsof -i :8000`, then `kill -9 <PID>`.

**Database locked** — ensure only one instance is running. Delete `knowledgeweaver.db` to reset.

**API rate limits** — reduce `CONCURRENT_QUERIES` in `.env` or switch to `depth="shallow"`.

**`ModuleNotFoundError: No module named 'knowledgeweaver'`** — activate your virtual environment and run `pip install -e .`.

---

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## License

MIT — see LICENSE for details.
