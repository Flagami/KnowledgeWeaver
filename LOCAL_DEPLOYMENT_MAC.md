# KnowledgeWeaver - Local Deployment Guide for macOS

Complete guide for deploying and using KnowledgeWeaver on your local Mac computer.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Running the Application](#running-the-application)
5. [Using KnowledgeWeaver](#using-knowledgeweaver)
6. [Troubleshooting](#troubleshooting)
7. [Advanced Usage](#advanced-usage)

---

## Prerequisites

### System Requirements

- **macOS**: 10.14 or later (Intel or Apple Silicon)
- **Python**: 3.9 or higher
- **Memory**: 4GB RAM minimum (8GB+ recommended)
- **Disk Space**: 5GB for dependencies and cache
- **Internet**: Required for API calls

### Check Your System

```bash
# Check macOS version
sw_vers

# Check Python version
python3 --version

# Check if you have Homebrew (optional but recommended)
brew --version
```

### Required API Keys

1. **Anthropic API Key** (Required)
   - Get it from: https://console.anthropic.com/
   - Sign up for an account
   - Create an API key in the dashboard
   - Keep it safe - you'll need it for configuration

---

## Installation

### Option 1: Recommended Installation with `uv` (Fastest)

`uv` is a blazingly fast Python package installer written in Rust. It's the recommended way to install KnowledgeWeaver.

#### Step 1: Install `uv`

```bash
# Install uv using curl
curl -LsSf https://astral.sh/uv/install.sh | sh

# Verify installation
uv --version
```

#### Step 2: Clone the Repository

```bash
# Clone the repository
git clone https://github.com/Flagami/KnowledgeWeaver.git
cd KnowledgeWeaver

# Verify you're in the right directory
pwd  # Should show: /path/to/KnowledgeWeaver
```

#### Step 3: Create Virtual Environment with `uv`

```bash
# Create virtual environment
uv venv

# Activate virtual environment
source .venv/bin/activate

# Verify activation (you should see (.venv) in your prompt)
which python
```

#### Step 4: Install Dependencies with `uv`

```bash
# Install all dependencies
uv pip install -r requirements.txt

# Verify installation
python -c "import knowledgeweaver; print('✓ Installation successful!')"
```

### Option 2: Alternative Installation with pip

If you prefer using the standard pip package manager:

```bash
# Clone the repository
git clone https://github.com/Flagami/KnowledgeWeaver.git
cd KnowledgeWeaver

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Verify installation
python -c "import knowledgeweaver; print('✓ Installation successful!')"
```

### Option 3: Using Homebrew (If you prefer Homebrew)

```bash
# Install Python with Homebrew (if not already installed)
brew install python@3.11

# Create virtual environment
python3.11 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

---

## Configuration

### Step 1: Create Environment File

```bash
# Copy the example environment file
cp .env.example .env

# Open the file in your preferred editor
nano .env
# or
vim .env
# or
open -a "Visual Studio Code" .env
```

### Step 2: Configure Environment Variables

Edit `.env` and add your Anthropic API key:

```env
# Claude API Configuration (REQUIRED)
ANTHROPIC_API_KEY=sk-ant-your-actual-api-key-here
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

### Step 3: Verify Configuration

```bash
# Test that configuration loads correctly
python -c "from knowledgeweaver.config import settings; print(f'✓ Config loaded: Model={settings.anthropic_model}')"
```

---

## Running the Application

### Important Note About the TUI

The TUI (Terminal User Interface) application requires interactive terminal support. On macOS, it may not display properly in all terminal emulators. We recommend using the **Python API** instead for local development.

### Method 1: Using the Python API (Recommended for Local Development)

Create a Python script to use KnowledgeWeaver:

#### Step 1: Create a Script

```bash
# Create a new Python script
cat > run_synthesis.py << 'EOF'
"""Example script to run KnowledgeWeaver synthesis."""

import asyncio
from knowledgeweaver.core.synthesis_pipeline import SynthesisPipeline
from knowledgeweaver.core.query_manager import Query

async def main():
    """Run a research synthesis query."""
    
    # Initialize the pipeline
    print("🚀 Initializing KnowledgeWeaver...")
    pipeline = SynthesisPipeline()
    
    # Create a query
    query = Query(
        query_text="machine learning applications in healthcare",
        domain="AI/ML"
    )
    
    print(f"\n📚 Processing query: {query.query_text}")
    print(f"🔍 Domain: {query.domain}")
    
    # Process the query
    try:
        result_path = await pipeline.process(query, depth="medium")
        print(f"\n✅ Synthesis complete!")
        print(f"📄 Report saved to: {result_path}")
        
        # Open the report in your browser
        import webbrowser
        webbrowser.open(f"file://{result_path}")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
EOF

# Run the script
python run_synthesis.py
```

#### Step 2: Customize the Query

Edit `run_synthesis.py` to change the query:

```python
# Change the query text
query = Query(
    query_text="quantum computing algorithms",  # Your research topic
    domain="Physics"  # Your research domain
)

# Change the depth level
result_path = await pipeline.process(query, depth="deep")  # shallow, medium, or deep
```

### Method 2: Interactive Python Shell

```bash
# Start Python interactive shell
python

# Then run these commands:
>>> import asyncio
>>> from knowledgeweaver.core.synthesis_pipeline import SynthesisPipeline
>>> from knowledgeweaver.core.query_manager import Query
>>> 
>>> async def test():
...     pipeline = SynthesisPipeline()
...     query = Query(query_text="AI research", domain="AI/ML")
...     result = await pipeline.process(query, depth="medium")
...     print(f"Result: {result}")
... 
>>> asyncio.run(test())
```

### Method 3: Using the Query Manager Directly

```bash
# Create a script to use the query manager
cat > query_example.py << 'EOF'
"""Example using the query manager."""

import asyncio
from knowledgeweaver.core.query_manager import QueryManager

async def main():
    manager = QueryManager(max_concurrent=4)
    
    # Submit a query
    query = await manager.submit_query(
        "deep learning neural networks",
        domain="AI/ML"
    )
    
    print(f"Query submitted: {query.query_id}")
    print(f"Status: {query.status}")
    
    # Get statistics
    stats = manager.get_stats()
    print(f"Stats: {stats}")

asyncio.run(main())
EOF

python query_example.py
```

---

## Using KnowledgeWeaver

### Basic Workflow

1. **Create a Query** — Define your research topic and domain
2. **Process** — Let KnowledgeWeaver search and synthesize
3. **Review Results** — Open the generated HTML report
4. **Provide Feedback** — Rate the results to improve future queries

### Example: Complete Workflow

```python
"""Complete example workflow."""

import asyncio
from knowledgeweaver.core.synthesis_pipeline import SynthesisPipeline
from knowledgeweaver.core.query_manager import Query
from knowledgeweaver.learning.feedback_collector import FeedbackCollector
from knowledgeweaver.learning.preference_tracker import PreferenceTracker

async def complete_workflow():
    # Initialize components
    pipeline = SynthesisPipeline()
    feedback_collector = FeedbackCollector()
    preference_tracker = PreferenceTracker()
    
    # Get user preferences
    prefs = preference_tracker.get_preferences("AI/ML")
    print(f"Current preferences: {prefs}")
    
    # Create and process query
    query = Query(
        query_text="transformer models in NLP",
        domain="AI/ML"
    )
    
    print(f"Processing: {query.query_text}")
    result_path = await pipeline.process(query, depth=prefs["depth_level"])
    print(f"Report: {result_path}")
    
    # Simulate user feedback
    feedback_collector.submit_feedback(
        query.id,
        rating=5,
        feedback_text="Excellent synthesis!"
    )
    
    # Get feedback analysis
    analysis = feedback_collector.analyze_feedback_patterns("AI/ML")
    print(f"Feedback analysis: {analysis}")

asyncio.run(complete_workflow())
```

---

## Troubleshooting

### Issue 1: "ModuleNotFoundError: No module named 'knowledgeweaver'"

**Solution:**
```bash
# Make sure virtual environment is activated
source .venv/bin/activate  # or source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt

# Verify installation
python -c "import knowledgeweaver; print('OK')"
```

### Issue 2: "ANTHROPIC_API_KEY not found"

**Solution:**
```bash
# Check if .env file exists
ls -la .env

# Check if API key is set
grep ANTHROPIC_API_KEY .env

# If not set, edit the file
nano .env
# Add: ANTHROPIC_API_KEY=sk-ant-your-key-here

# Verify it's loaded
python -c "from knowledgeweaver.config import settings; print(settings.anthropic_api_key[:10])"
```

### Issue 3: "Connection refused" or "API timeout"

**Solution:**
```bash
# Check internet connection
ping api.anthropic.com

# Increase timeout
# Edit .env and change:
QUERY_TIMEOUT_SECONDS=600  # Increase from 300

# Reduce concurrent queries
CONCURRENT_QUERIES=2  # Reduce from 8
```

### Issue 4: "Database is locked"

**Solution:**
```bash
# Remove the database file
rm knowledgeweaver.db

# Reinitialize
python -c "from knowledgeweaver.storage.database import init_database; init_database()"
```

### Issue 5: "TUI application doesn't display"

**Solution:**
Use the Python API instead (see "Using KnowledgeWeaver" section above). The TUI requires specific terminal support that may not work on all macOS terminal emulators.

```bash
# Instead of:
python -m knowledgeweaver.ui.app

# Use:
python run_synthesis.py  # See examples above
```

### Issue 6: "Memory issues or slow performance"

**Solution:**
```bash
# Reduce concurrent queries
CONCURRENT_QUERIES=2

# Use shallow depth
# In your script: depth="shallow"

# Clear cache
rm -rf outputs/paper_cache

# Monitor memory usage
top -p $(pgrep -f knowledgeweaver)
```

---

## Advanced Usage

### Custom Configuration

```python
"""Use custom configuration."""

from knowledgeweaver.config import Settings

# Create custom settings
custom_settings = Settings(
    anthropic_api_key="your-key",
    anthropic_model="claude-opus-4-7",
    concurrent_queries=4,
    query_timeout_seconds=600,
    log_level="DEBUG"
)
```

### Batch Processing Multiple Queries

```python
"""Process multiple queries in batch."""

import asyncio
from knowledgeweaver.core.query_manager import QueryManager
from knowledgeweaver.core.query_manager import Query

async def batch_process():
    manager = QueryManager(max_concurrent=4)
    
    queries = [
        ("machine learning", "AI/ML"),
        ("protein folding", "Biology"),
        ("quantum computing", "Physics"),
    ]
    
    for query_text, domain in queries:
        query = await manager.submit_query(query_text, domain=domain)
        print(f"Submitted: {query.query_id}")
    
    # Wait for all to complete
    while manager.get_pending_queries():
        await asyncio.sleep(5)
    
    # Get results
    completed = manager.get_completed_queries()
    print(f"Completed: {len(completed)} queries")

asyncio.run(batch_process())
```

### Monitoring Performance

```python
"""Monitor performance metrics."""

from knowledgeweaver.core.performance import performance_monitor, PerformanceTuner

# Get performance statistics
stats = performance_monitor.get_all_stats()
print(f"Performance stats: {stats}")

# Get recommendations
tuner = PerformanceTuner(performance_monitor)
recommendations = tuner.get_recommendations()
for rec in recommendations:
    print(f"- {rec}")

# Get bottlenecks
bottlenecks = tuner.get_bottlenecks()
for operation, total_time in bottlenecks:
    print(f"{operation}: {total_time:.2f}s")
```

### Analyzing Feedback

```python
"""Analyze user feedback patterns."""

from knowledgeweaver.learning.feedback_collector import FeedbackCollector
from knowledgeweaver.learning.preference_updater import PreferenceUpdater

collector = FeedbackCollector()
updater = PreferenceUpdater()

# Get feedback summary
summary = collector.get_feedback_summary("AI/ML")
print(f"Feedback summary: {summary}")

# Get learning summary
learning = updater.get_learning_summary("AI/ML")
print(f"Learning summary: {learning}")

# Get improvement suggestions
suggestions = updater.suggest_improvements("AI/ML")
for suggestion in suggestions:
    print(f"- {suggestion}")
```

---

## Running Tests

```bash
# Run all tests
pytest tests/unit/ -v

# Run specific test file
pytest tests/unit/test_phase1_foundation.py -v

# Run with coverage
pytest tests/ --cov=knowledgeweaver --cov-report=html

# View coverage report
open htmlcov/index.html
```

---

## Useful Commands

```bash
# Activate virtual environment
source .venv/bin/activate

# Deactivate virtual environment
deactivate

# Check installed packages
pip list

# Update dependencies
pip install --upgrade -r requirements.txt

# View logs
tail -f logs/knowledgeweaver.log

# Clear cache
rm -rf outputs/paper_cache

# Reset database
rm knowledgeweaver.db

# Check configuration
python -c "from knowledgeweaver.config import settings; print(settings)"
```

---

## Next Steps

1. **Run your first query** — Use the examples above to process a research topic
2. **Explore the outputs** — Check the generated HTML reports in the `outputs/` directory
3. **Provide feedback** — Rate the results to help the system learn
4. **Customize settings** — Adjust configuration for your needs
5. **Check documentation** — See README.md and DEPLOYMENT.md for more info

---

## Support & Resources

- 📖 [Main README](./README.md)
- 🚀 [Deployment Guide](./DEPLOYMENT.md)
- 🐛 [Issue Tracker](https://github.com/Flagami/KnowledgeWeaver/issues)
- 💬 [Discussions](https://github.com/Flagami/KnowledgeWeaver/discussions)

---

**Happy researching! 🧠**
