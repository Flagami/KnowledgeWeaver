# KnowledgeWeaver Deployment Guide

Complete guide for deploying KnowledgeWeaver locally or using Docker.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Local Deployment](#local-deployment)
3. [Docker Deployment](#docker-deployment)
4. [Environment Configuration](#environment-configuration)
5. [Running the Application](#running-the-application)
6. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### System Requirements

- **Python**: 3.9 or higher (for local deployment)
- **Docker**: Latest version (for Docker deployment)
- **Memory**: Minimum 2GB RAM (4GB+ recommended)
- **Disk Space**: 5GB for dependencies and cache
- **Network**: Internet access for API calls

### Required API Keys

- **Anthropic API Key** — For Claude AI integration
  - Get it from: https://console.anthropic.com/
  - Required for all synthesis operations

### Optional API Keys

- **arXiv API** — No key required (public API)
- **PubMed API** — No key required (public API)
- **Semantic Scholar API** — No key required (public API)
- **CrossRef API** — No key required (public API)

---

## Local Deployment

### Step 1: Clone Repository

```bash
git clone https://github.com/Flagami/KnowledgeWeaver.git
cd KnowledgeWeaver
```

### Step 2: Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Install web UI dependencies (optional)
pip install -r requirements-web.txt
```

### Step 4: Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your settings
nano .env  # or use your preferred editor
```

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

### Step 5: Initialize Database

```bash
# Create database and tables
python -c "from knowledgeweaver.storage.database import init_database; init_database()"
```

### Step 6: Run Application

Choose one of the following methods:

#### Option A: Run Web UI (Recommended)

```bash
# Start the web UI server
python run_web_ui.py

# Open your browser at: http://localhost:8000
```

#### Option B: Run Python API

```bash
# Create a Python script to use the API
cat > run_synthesis.py << 'EOF'
import asyncio
from knowledgeweaver.core.synthesis_pipeline import SynthesisPipeline
from knowledgeweaver.core.query_manager import Query

async def main():
    pipeline = SynthesisPipeline()
    query = Query(
        query_text="machine learning applications in healthcare",
        domain="AI/ML"
    )
    result_path = await pipeline.process(query, depth="medium")
    print(f"✅ Report saved to: {result_path}")

asyncio.run(main())
EOF

# Run the script
python run_synthesis.py
```

#### Option C: Run TUI (Terminal User Interface)

```bash
# Run the TUI application
python test_tui_simple.py
```

---

## Docker Deployment

### Step 1: Build Docker Image

```bash
# Build the Docker image
docker build -t knowledgeweaver:latest .
```

### Step 2: Create Docker Compose File

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  knowledgeweaver:
    build: .
    container_name: knowledgeweaver
    environment:
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - ANTHROPIC_BASE_URL=https://api.anthropic.com
      - ANTHROPIC_MODEL=claude-opus-4-7
      - CONCURRENT_QUERIES=8
      - LOG_LEVEL=INFO
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
      start_period: 40s
```

### Step 3: Create .env File for Docker

```bash
# Create .env file with your API key
cat > .env << 'EOF'
ANTHROPIC_API_KEY=sk-ant-your-actual-api-key-here
ANTHROPIC_BASE_URL=https://api.anthropic.com
ANTHROPIC_MODEL=claude-opus-4-7
CONCURRENT_QUERIES=8
QUERY_TIMEOUT_SECONDS=300
LOG_LEVEL=INFO
DATABASE_PATH=/app/data/knowledgeweaver.db
OUTPUT_DIR=/app/output
DEBUG=false
EOF
```

### Step 4: Run with Docker Compose

```bash
# Start the container
docker-compose up -d

# View logs
docker-compose logs -f knowledgeweaver

# Stop the container
docker-compose down
```

### Step 5: Access the Application

```bash
# Open your browser at: http://localhost:8000
```

### Step 6: Verify Docker Deployment

```bash
# Check container status
docker ps | grep knowledgeweaver

# Check container logs
docker logs knowledgeweaver

# Run tests inside container
docker-compose exec knowledgeweaver pytest tests/unit/ -v

# Access container shell
docker-compose exec knowledgeweaver bash
```

---

## Environment Configuration

### Required Variables

- `ANTHROPIC_API_KEY` — Your Anthropic API key (required)
- `ANTHROPIC_BASE_URL` — Anthropic API endpoint (default: https://api.anthropic.com)
- `ANTHROPIC_MODEL` — Claude model to use (default: claude-opus-4-7)

### Optional Variables

- `CONCURRENT_QUERIES` — Maximum concurrent queries (default: 8)
- `QUERY_TIMEOUT_SECONDS` — Query timeout in seconds (default: 300)
- `LOG_LEVEL` — Logging level (default: INFO)
- `DATABASE_PATH` — SQLite database path (default: ./knowledgeweaver.db)
- `OUTPUT_DIR` — Output directory for reports (default: ./outputs)
- `DEBUG` — Enable debug mode (default: false)

### Production Configuration

For production deployments, use:

```env
# Security
LOG_LEVEL=WARNING
CONCURRENT_QUERIES=4
QUERY_TIMEOUT_SECONDS=600

# Performance
CACHE_TTL_SECONDS=7200
PAPER_CACHE_DAYS=60
```

---

## Running the Application

### Web UI (Recommended)

The Web UI provides a user-friendly interface for non-technical users.

```bash
# Start the web UI
python run_web_ui.py

# Open browser at: http://localhost:8000
```

**Features:**
- Beautiful, responsive interface
- Query submission form
- Real-time statistics
- Result display with star ratings
- Feedback collection

### Python API

The Python API is for developers and advanced users.

```python
import asyncio
from knowledgeweaver.core.synthesis_pipeline import SynthesisPipeline
from knowledgeweaver.core.query_manager import Query

async def main():
    pipeline = SynthesisPipeline()
    query = Query(query_text="your topic", domain="AI/ML")
    result = await pipeline.process(query, depth="medium")
    print(f"Result: {result}")

asyncio.run(main())
```

### TUI (Terminal User Interface)

The TUI is for terminal enthusiasts.

```bash
# Run the TUI test
python test_tui_simple.py
```

---

## Troubleshooting

### Issue 1: "ANTHROPIC_API_KEY not found"

**Solution:**
```bash
# Check if .env file exists
ls -la .env

# Check if API key is set
grep ANTHROPIC_API_KEY .env

# If not set, edit the file
nano .env
# Add: ANTHROPIC_API_KEY=sk-ant-your-key-here
```

### Issue 2: "Connection refused" or "API timeout"

**Solution:**
```bash
# Check internet connection
ping api.anthropic.com

# Increase timeout in .env
QUERY_TIMEOUT_SECONDS=600

# Reduce concurrent queries
CONCURRENT_QUERIES=2
```

### Issue 3: "Database is locked"

**Solution:**
```bash
# Remove the database file
rm knowledgeweaver.db

# Reinitialize
python -c "from knowledgeweaver.storage.database import init_database; init_database()"
```

### Issue 4: "ModuleNotFoundError: No module named 'knowledgeweaver'"

**Solution:**
```bash
# Make sure virtual environment is activated
source venv/bin/activate  # or source .venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt

# Verify installation
python -c "import knowledgeweaver; print('OK')"
```

### Issue 5: Docker container won't start

**Solution:**
```bash
# Check Docker logs
docker-compose logs knowledgeweaver

# Rebuild the image
docker-compose build --no-cache

# Start again
docker-compose up -d
```

### Issue 6: "Port 8000 already in use"

**Solution:**
```bash
# Find process using port 8000
lsof -i :8000

# Kill the process
kill -9 <PID>

# Or use a different port in docker-compose.yml
ports:
  - "8001:8000"
```

### Issue 7: Memory issues or slow performance

**Solution:**
```bash
# Reduce concurrent queries in .env
CONCURRENT_QUERIES=2

# Use shallow depth for faster processing
# In your script: depth="shallow"

# Clear cache
rm -rf outputs/paper_cache

# Monitor memory usage
top -p $(pgrep -f knowledgeweaver)
```

---

## Useful Commands

### Local Deployment

```bash
# Activate virtual environment
source venv/bin/activate

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

# Run tests
pytest tests/unit/ -v
```

### Docker Deployment

```bash
# Build image
docker build -t knowledgeweaver:latest .

# Start container
docker-compose up -d

# Stop container
docker-compose down

# View logs
docker-compose logs -f

# Execute command in container
docker-compose exec knowledgeweaver bash

# Remove image
docker rmi knowledgeweaver:latest

# Remove all containers and volumes
docker-compose down -v
```

---

## Next Steps

1. **Choose deployment method** — Local or Docker
2. **Configure environment** — Add your API key
3. **Run the application** — Use Web UI, Python API, or TUI
4. **Submit queries** — Start researching
5. **Provide feedback** — Help the system learn

---

## Support & Resources

- 📖 [Main README](./README.md)
- 🖥️ [Local Mac Deployment Guide](./LOCAL_DEPLOYMENT_MAC.md)
- 🐛 [Issue Tracker](https://github.com/Flagami/KnowledgeWeaver/issues)
- 💬 [Discussions](https://github.com/Flagami/KnowledgeWeaver/discussions)

---

**Happy researching! 🧠**
