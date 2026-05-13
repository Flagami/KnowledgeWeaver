# KnowledgeWeaver Deployment Guide

Complete guide for deploying KnowledgeWeaver in various environments.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Local Deployment](#local-deployment)
3. [Docker Deployment](#docker-deployment)
4. [Cloud Deployment](#cloud-deployment)
5. [Environment Configuration](#environment-configuration)
6. [Database Setup](#database-setup)
7. [Monitoring & Logging](#monitoring--logging)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### System Requirements

- **Python**: 3.9 or higher
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
git clone https://github.com/yourusername/KnowledgeWeaver.git
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
```

### Step 4: Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your settings
nano .env  # or use your preferred editor
```

### Step 5: Initialize Database

```bash
# Create database and tables
python -c "from knowledgeweaver.storage.database import init_database; init_database()"
```

### Step 6: Run Application

```bash
# Run TUI application
python -m knowledgeweaver.ui.app

# Or run as Python module
python -c "from knowledgeweaver.core.synthesis_pipeline import SynthesisPipeline; print('Ready to use!')"
```

### Step 7: Verify Installation

```bash
# Run tests to verify everything works
pytest tests/unit/ -v
pytest tests/integration/ -v
```

---

## Docker Deployment

### Step 1: Create Dockerfile

Create `Dockerfile` in project root:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create output directory
RUN mkdir -p output

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV LOG_LEVEL=INFO

# Run application
CMD ["python", "-m", "knowledgeweaver.ui.app"]
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
      - LLM_MODEL=claude-opus-4-7
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
      test: ["CMD", "python", "-c", "import knowledgeweaver; print('healthy')"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
```

### Step 3: Build and Run

```bash
# Build Docker image
docker build -t knowledgeweaver:latest .

# Run with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f knowledgeweaver

# Stop container
docker-compose down
```

### Step 4: Verify Docker Deployment

```bash
# Check container status
docker ps | grep knowledgeweaver

# Run tests inside container
docker-compose exec knowledgeweaver pytest tests/unit/ -v

# Access container shell
docker-compose exec knowledgeweaver bash
```

---

## Cloud Deployment

### AWS Deployment (EC2)

#### Step 1: Launch EC2 Instance

```bash
# Using AWS CLI
aws ec2 run-instances \
  --image-id ami-0c55b159cbfafe1f0 \
  --instance-type t3.medium \
  --key-name your-key-pair \
  --security-groups default
```

#### Step 2: Connect and Setup

```bash
# SSH into instance
ssh -i your-key.pem ec2-user@your-instance-ip

# Update system
sudo yum update -y

# Install Python and dependencies
sudo yum install -y python3 python3-pip git

# Clone repository
git clone https://github.com/yourusername/KnowledgeWeaver.git
cd KnowledgeWeaver

# Follow local deployment steps
```

#### Step 3: Configure for Production

```bash
# Create systemd service file
sudo nano /etc/systemd/system/knowledgeweaver.service
```

Add:

```ini
[Unit]
Description=KnowledgeWeaver Research Synthesis
After=network.target

[Service]
Type=simple
User=ec2-user
WorkingDirectory=/home/ec2-user/KnowledgeWeaver
Environment="PATH=/home/ec2-user/KnowledgeWeaver/venv/bin"
Environment="ANTHROPIC_API_KEY=your_api_key"
ExecStart=/home/ec2-user/KnowledgeWeaver/venv/bin/python -m knowledgeweaver.ui.app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable knowledgeweaver
sudo systemctl start knowledgeweaver

# Check status
sudo systemctl status knowledgeweaver
```

### Heroku Deployment

#### Step 1: Create Heroku App

```bash
# Install Heroku CLI
# https://devcenter.heroku.com/articles/heroku-cli

# Login to Heroku
heroku login

# Create app
heroku create knowledgeweaver-app

# Add buildpack
heroku buildpacks:add heroku/python
```

#### Step 2: Create Procfile

Create `Procfile`:

```
web: python -m knowledgeweaver.ui.app
worker: python -m knowledgeweaver.core.synthesis_pipeline
```

#### Step 3: Set Environment Variables

```bash
# Set API key
heroku config:set ANTHROPIC_API_KEY=your_api_key

# Set other variables
heroku config:set LLM_MODEL=claude-opus-4-7
heroku config:set CONCURRENT_QUERIES=4
heroku config:set LOG_LEVEL=INFO
```

#### Step 4: Deploy

```bash
# Deploy to Heroku
git push heroku main

# View logs
heroku logs --tail

# Scale dynos
heroku ps:scale web=1 worker=1
```

### Google Cloud Run Deployment

#### Step 1: Create Cloud Run Service

```bash
# Set project
gcloud config set project YOUR_PROJECT_ID

# Build and push to Container Registry
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/knowledgeweaver

# Deploy to Cloud Run
gcloud run deploy knowledgeweaver \
  --image gcr.io/YOUR_PROJECT_ID/knowledgeweaver \
  --platform managed \
  --region us-central1 \
  --memory 2Gi \
  --timeout 3600 \
  --set-env-vars ANTHROPIC_API_KEY=your_api_key
```

#### Step 2: Configure Cloud Storage

```bash
# Create bucket for output
gsutil mb gs://knowledgeweaver-output

# Update environment variable
gcloud run services update knowledgeweaver \
  --set-env-vars OUTPUT_DIR=/tmp/output
```

---

## Environment Configuration

### Required Environment Variables

```env
# Claude API Configuration
ANTHROPIC_API_KEY=sk-ant-...          # Your Anthropic API key
LLM_MODEL=claude-opus-4-7             # Claude model to use

# Application Configuration
CONCURRENT_QUERIES=8                  # Max concurrent queries
QUERY_TIMEOUT_SECONDS=300             # Query timeout in seconds
LOG_LEVEL=INFO                        # Logging level

# Storage Configuration
DATABASE_PATH=./knowledgeweaver.db    # Database file path
OUTPUT_DIR=./output                   # Output directory for reports
```

### Optional Environment Variables

```env
# Performance Tuning
CACHE_TTL_SECONDS=3600                # Cache time-to-live
PAPER_CACHE_DAYS=30                   # Paper cache expiry

# API Configuration
ARXIV_API_TIMEOUT=30                  # arXiv API timeout
PUBMED_API_TIMEOUT=30                 # PubMed API timeout
SEMANTIC_SCHOLAR_TIMEOUT=30           # Semantic Scholar timeout
CROSSREF_TIMEOUT=30                   # CrossRef timeout

# Monitoring
ENABLE_METRICS=true                   # Enable performance metrics
METRICS_PORT=9090                     # Metrics port
```

### Production Configuration

For production deployments, use:

```env
# Security
LOG_LEVEL=WARNING                     # Reduce log verbosity
CONCURRENT_QUERIES=4                  # Conservative concurrency
QUERY_TIMEOUT_SECONDS=600             # Longer timeout for stability

# Performance
CACHE_TTL_SECONDS=7200                # Longer cache TTL
PAPER_CACHE_DAYS=60                   # Longer paper cache

# Monitoring
ENABLE_METRICS=true
METRICS_PORT=9090
```

---

## Database Setup

### SQLite (Default)

```bash
# Database is automatically created at DATABASE_PATH
# Default: ./knowledgeweaver.db

# Backup database
cp knowledgeweaver.db knowledgeweaver.db.backup

# Restore database
cp knowledgeweaver.db.backup knowledgeweaver.db
```

### PostgreSQL (Production)

#### Step 1: Install PostgreSQL

```bash
# macOS
brew install postgresql

# Ubuntu/Debian
sudo apt-get install postgresql postgresql-contrib

# Start PostgreSQL
sudo systemctl start postgresql
```

#### Step 2: Create Database

```bash
# Create database
createdb knowledgeweaver

# Create user
createuser knowledgeweaver_user

# Set password
psql -c "ALTER USER knowledgeweaver_user WITH PASSWORD 'secure_password';"

# Grant privileges
psql -c "GRANT ALL PRIVILEGES ON DATABASE knowledgeweaver TO knowledgeweaver_user;"
```

#### Step 3: Update Configuration

Update `.env`:

```env
DATABASE_URL=postgresql://knowledgeweaver_user:secure_password@localhost:5432/knowledgeweaver
```

#### Step 4: Run Migrations

```bash
# Alembic migrations (if using)
alembic upgrade head
```

---

## Monitoring & Logging

### Application Logging

```bash
# View logs
tail -f logs/knowledgeweaver.log

# Filter logs by level
grep "ERROR" logs/knowledgeweaver.log
grep "WARNING" logs/knowledgeweaver.log

# Rotate logs
logrotate -f /etc/logrotate.d/knowledgeweaver
```

### Performance Monitoring

```python
from knowledgeweaver.core.performance import performance_monitor

# Get performance statistics
stats = performance_monitor.get_all_stats()
print(stats)

# Get bottlenecks
bottlenecks = performance_monitor.get_bottlenecks()
for operation, total_time in bottlenecks:
    print(f"{operation}: {total_time:.2f}s")
```

### Health Checks

```bash
# Check application health
curl http://localhost:8000/health

# Check database
python -c "from knowledgeweaver.storage.database import get_db_session; session = get_db_session(); print('Database OK')"

# Check API connectivity
python -c "from anthropic import Anthropic; client = Anthropic(); print('API OK')"
```

### Monitoring Tools

#### Prometheus Integration

```python
from prometheus_client import Counter, Histogram, start_http_server

# Start metrics server
start_http_server(9090)

# Create metrics
query_counter = Counter('queries_total', 'Total queries')
synthesis_time = Histogram('synthesis_seconds', 'Synthesis time')
```

#### ELK Stack Integration

```python
from pythonjsonlogger import jsonlogger
import logging

# Configure JSON logging for ELK
logger = logging.getLogger()
handler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter()
handler.setFormatter(formatter)
logger.addHandler(handler)
```

---

## Troubleshooting

### Common Issues

#### Issue: API Key Not Found

```bash
# Check environment variable
echo $ANTHROPIC_API_KEY

# Set API key
export ANTHROPIC_API_KEY=your_api_key

# Verify
python -c "import os; print(os.getenv('ANTHROPIC_API_KEY'))"
```

#### Issue: Database Locked

```bash
# Check for running processes
lsof | grep knowledgeweaver.db

# Kill process if needed
kill -9 <PID>

# Reset database
rm knowledgeweaver.db
python -c "from knowledgeweaver.storage.database import init_database; init_database()"
```

#### Issue: Memory Issues

```bash
# Monitor memory usage
top -p $(pgrep -f knowledgeweaver)

# Reduce concurrent queries
export CONCURRENT_QUERIES=2

# Clear cache
rm -rf output/paper_cache
```

#### Issue: Slow Performance

```bash
# Check performance metrics
python -c "from knowledgeweaver.core.performance import performance_monitor; print(performance_monitor.get_all_stats())"

# Get recommendations
from knowledgeweaver.core.performance import PerformanceTuner
tuner = PerformanceTuner(performance_monitor)
print(tuner.get_recommendations())
```

### Debug Mode

```bash
# Enable debug logging
export LOG_LEVEL=DEBUG

# Run with verbose output
python -m knowledgeweaver.ui.app --verbose

# Run tests with output
pytest tests/ -v -s
```

### Performance Optimization

```bash
# Enable caching
export CACHE_TTL_SECONDS=7200

# Increase paper cache
export PAPER_CACHE_DAYS=60

# Optimize database
python -c "from knowledgeweaver.storage.database import optimize_database; optimize_database()"
```

---

## Scaling Considerations

### Horizontal Scaling

```bash
# Run multiple instances with load balancer
# Instance 1
export INSTANCE_ID=1
python -m knowledgeweaver.ui.app

# Instance 2
export INSTANCE_ID=2
python -m knowledgeweaver.ui.app

# Use nginx for load balancing
# See nginx.conf example below
```

### Vertical Scaling

```bash
# Increase resources
export CONCURRENT_QUERIES=16
export CACHE_TTL_SECONDS=14400

# Use PostgreSQL instead of SQLite
export DATABASE_URL=postgresql://...
```

### Database Optimization

```bash
# Create indexes
CREATE INDEX idx_query_domain ON query(domain);
CREATE INDEX idx_paper_source ON paper(source);
CREATE INDEX idx_preferences_domain ON user_preferences(domain);

# Analyze query performance
EXPLAIN ANALYZE SELECT * FROM query WHERE domain = 'AI/ML';
```

---

## Backup & Recovery

### Backup Strategy

```bash
# Daily backup
0 2 * * * /usr/local/bin/backup-knowledgeweaver.sh

# Create backup script
cat > /usr/local/bin/backup-knowledgeweaver.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/backups/knowledgeweaver"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR
cp /app/knowledgeweaver.db $BACKUP_DIR/knowledgeweaver_$DATE.db
tar -czf $BACKUP_DIR/output_$DATE.tar.gz /app/output
# Keep only last 30 days
find $BACKUP_DIR -mtime +30 -delete
EOF

chmod +x /usr/local/bin/backup-knowledgeweaver.sh
```

### Recovery Procedure

```bash
# Restore from backup
cp /backups/knowledgeweaver/knowledgeweaver_20240101_020000.db ./knowledgeweaver.db

# Restore output files
tar -xzf /backups/knowledgeweaver/output_20240101_020000.tar.gz

# Verify restoration
python -c "from knowledgeweaver.storage.database import get_db_session; session = get_db_session(); print('Database restored')"
```

---

## Security Considerations

### API Key Management

```bash
# Use environment variables (not in code)
export ANTHROPIC_API_KEY=sk-ant-...

# Use secrets manager (production)
# AWS Secrets Manager
aws secretsmanager get-secret-value --secret-id knowledgeweaver/api-key

# HashiCorp Vault
vault kv get secret/knowledgeweaver/api-key
```

### Network Security

```bash
# Use HTTPS only
# Configure SSL certificate
# Use firewall rules to restrict access

# Example nginx configuration
server {
    listen 443 ssl;
    ssl_certificate /etc/ssl/certs/knowledgeweaver.crt;
    ssl_certificate_key /etc/ssl/private/knowledgeweaver.key;
    
    location / {
        proxy_pass http://localhost:8000;
    }
}
```

### Database Security

```bash
# Use strong passwords
# Enable authentication
# Restrict network access
# Use encrypted connections

# PostgreSQL example
psql -U knowledgeweaver_user -h localhost -d knowledgeweaver
```

---

## Support & Resources

- 📖 [Main README](./README.md)
- 🐛 [Issue Tracker](https://github.com/yourusername/KnowledgeWeaver/issues)
- 💬 [Discussions](https://github.com/yourusername/KnowledgeWeaver/discussions)
- 📧 Email: support@knowledgeweaver.dev

---

**Last Updated**: 2024
**Version**: 1.0
