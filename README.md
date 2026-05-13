# KnowledgeWeaver

A TUI-based AI agent dialogue research system that transforms user questions into expert-level summaries backed by highly cited papers and articles from authoritative sources.

## Vision

KnowledgeWeaver automates the research synthesis process. Users input keywords or questions via a simple terminal interface, and the system:

1. **Searches** multiple authoritative sources concurrently (arXiv, PubMed, Semantic Scholar, CrossRef)
2. **Fetches & Extracts** key findings from papers
3. **Synthesizes** findings across papers using Claude AI
4. **Generates** interactive HTML reports with citations
5. **Learns** from user feedback to improve future queries

## Features

- 🔍 **Multi-Domain Support** — AI/ML, Biology, Physics, and more
- ⚡ **Concurrent Processing** — Handle 8 parallel queries simultaneously
- 🧠 **Deep Synthesis** — Extract → Summarize → Synthesize → Generate Insights
- 🎨 **Interactive HTML** — Expandable sections, concept links, related papers, citations
- 📚 **Self-Evolving** — User preferences improve synthesis quality over time
- 🎛️ **Configurable** — Choose your base model via `LLM_MODEL` environment variable
- 💾 **Local-First** — SQLite storage, no cloud required for MVP

## Quick Start

### Prerequisites

- Python 3.11+
- Anthropic API key

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/knowledgeweaver.git
cd knowledgeweaver

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"

# Copy environment template
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

### Usage

```bash
# Run the TUI application
python -m knowledgeweaver

# Run with custom model
LLM_MODEL=claude-sonnet-4-6 python -m knowledgeweaver

# Generate HTML report (manual)
python -m knowledgeweaver generate-html --query "quantum computing" --output report.html
```

## Development

### Running Tests

```bash
# Run all tests with coverage
pytest tests/ -v --cov=knowledgeweaver

# Run specific test suite
pytest tests/unit/ -v
pytest tests/integration/ -v
```

### Code Quality

```bash
# Format code
black knowledgeweaver/ tests/

# Lint
ruff check knowledgeweaver/ --fix

# Type checking
mypy knowledgeweaver/
```

## Project Structure

```
knowledgeweaver/
├── core/              # Query management, domain detection, pipeline orchestration
├── sources/           # Research source integrations (arXiv, PubMed, etc.)
├── processing/        # Fetching, extraction, summarization, synthesis
├── storage/           # Database models and ORM
├── ui/                # TUI interface (textual)
├── output/            # HTML generation and templates
├── learning/          # User preference tracking and feedback
└── utils/             # Logging, errors, helpers

tests/
├── unit/              # Unit tests for individual components
├── integration/       # Integration tests for pipelines
└── fixtures/          # Test data and mocks
```

## Documentation

- [SPEC.md](SPEC.md) — Complete specification and design decisions
- [PLAN.md](PLAN.md) — Implementation plan with task breakdown
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) — System architecture deep-dive (coming soon)
- [docs/API.md](docs/API.md) — Internal API reference (coming soon)

## Roadmap

### MVP (Phase 1-6)
- ✅ Multi-domain research aggregation
- ✅ Concurrent query processing (8 parallel)
- ✅ Deep synthesis pipeline
- ✅ Interactive HTML output
- ✅ User preference learning
- ✅ TUI interface

### v2 (Post-MVP)
- PostgreSQL migration for multi-user support
- Advanced HTML visualizations (concept graphs, network diagrams)
- Redis caching layer
- REST/GraphQL API server
- Cloud deployment

### v3+
- Multi-language support
- ML-based preference learning
- Collaborative research features
- Citation export (BibTeX, RIS)
- Mobile app

## Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

MIT License — see LICENSE file for details

## Support

- 📖 Read the [SPEC.md](SPEC.md) for detailed requirements
- 📋 Check [PLAN.md](PLAN.md) for implementation roadmap
- 🐛 Report issues on GitHub
- 💬 Discuss ideas in GitHub Discussions

---

Built with ❤️ using Claude AI and Python
