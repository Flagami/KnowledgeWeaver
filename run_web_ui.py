"""Run the KnowledgeWeaver Web UI."""

import os
import sys
import uvicorn
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

if __name__ == "__main__":
    print("🚀 Starting KnowledgeWeaver Web UI...")
    print("📍 Open your browser at: http://localhost:8000")
    print("⌨️  Press Ctrl+C to stop the server\n")

    uvicorn.run(
        "knowledgeweaver.ui.web.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
