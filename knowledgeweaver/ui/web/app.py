"""Web UI backend for KnowledgeWeaver using FastAPI."""

import asyncio
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from knowledgeweaver.core.synthesis_pipeline import SynthesisPipeline
from knowledgeweaver.core.query_manager import Query, QueryManager
from knowledgeweaver.learning.preference_tracker import PreferenceTracker
from knowledgeweaver.learning.feedback_collector import FeedbackCollector
from knowledgeweaver.learning.preference_updater import PreferenceUpdater
from knowledgeweaver.utils.logger import logger

# Initialize FastAPI app
app = FastAPI(
    title="KnowledgeWeaver",
    description="Intelligent Research Synthesis System",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
pipeline = SynthesisPipeline()
query_manager = QueryManager(max_concurrent=4)
preference_tracker = PreferenceTracker()
feedback_collector = FeedbackCollector()
preference_updater = PreferenceUpdater()

# Store for tracking background tasks
background_tasks_store = {}


# Pydantic models
class QueryRequest(BaseModel):
    """Request model for submitting a query."""
    query_text: str
    domain: str
    depth: str = "medium"


class FeedbackRequest(BaseModel):
    """Request model for submitting feedback."""
    query_id: str
    rating: int
    feedback_text: Optional[str] = None


class PreferenceRequest(BaseModel):
    """Request model for updating preferences."""
    domain: str
    depth_level: Optional[str] = None
    paper_type: Optional[str] = None


# Health check endpoint
@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }


# Query endpoints
@app.post("/api/queries")
async def submit_query(request: QueryRequest, background_tasks: BackgroundTasks):
    """Submit a new research query."""
    try:
        # Validate input
        if not request.query_text or len(request.query_text.strip()) == 0:
            raise HTTPException(status_code=400, detail="Query text cannot be empty")

        if request.depth not in ["shallow", "medium", "deep"]:
            raise HTTPException(status_code=400, detail="Invalid depth level")

        # Create query
        query = Query(
            query_text=request.query_text,
            domain=request.domain
        )

        # Process in background
        background_tasks.add_task(
            process_query,
            query,
            request.depth
        )

        return {
            "query_id": query.id,
            "status": "submitted",
            "message": "Query submitted for processing"
        }

    except Exception as e:
        logger.error(f"Error submitting query: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/queries/{query_id}")
async def get_query_status(query_id: str):
    """Get the status of a query."""
    try:
        # This would normally query the database
        # For now, return a mock response
        return {
            "query_id": query_id,
            "status": "completed",
            "result_path": f"./outputs/query_{query_id}.html"
        }
    except Exception as e:
        logger.error(f"Error getting query status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/queries")
async def list_queries():
    """List all queries."""
    try:
        stats = query_manager.get_stats()
        return {
            "total": stats.get("total", 0),
            "completed": stats.get("completed", 0),
            "pending": stats.get("pending", 0),
            "active": stats.get("active", 0)
        }
    except Exception as e:
        logger.error(f"Error listing queries: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Feedback endpoints
@app.post("/api/feedback")
async def submit_feedback(request: FeedbackRequest):
    """Submit feedback for a query."""
    try:
        if not 1 <= request.rating <= 5:
            raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")

        feedback_collector.submit_feedback(
            request.query_id,
            rating=request.rating,
            feedback_text=request.feedback_text
        )

        return {
            "status": "success",
            "message": "Feedback submitted successfully"
        }
    except Exception as e:
        logger.error(f"Error submitting feedback: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/feedback/{domain}")
async def get_feedback_analysis(domain: str):
    """Get feedback analysis for a domain."""
    try:
        analysis = feedback_collector.analyze_feedback_patterns(domain)
        return analysis
    except Exception as e:
        logger.error(f"Error getting feedback analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Preference endpoints
@app.get("/api/preferences/{domain}")
async def get_preferences(domain: str):
    """Get preferences for a domain."""
    try:
        prefs = preference_tracker.get_preferences(domain)
        return prefs
    except Exception as e:
        logger.error(f"Error getting preferences: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/preferences")
async def update_preferences(request: PreferenceRequest):
    """Update preferences for a domain."""
    try:
        preference_tracker.set_preferences(
            request.domain,
            depth_level=request.depth_level,
            paper_type=request.paper_type
        )

        return {
            "status": "success",
            "message": "Preferences updated successfully"
        }
    except Exception as e:
        logger.error(f"Error updating preferences: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Learning endpoints
@app.get("/api/learning/{domain}")
async def get_learning_summary(domain: str):
    """Get learning summary for a domain."""
    try:
        summary = preference_updater.get_learning_summary(domain)
        return summary
    except Exception as e:
        logger.error(f"Error getting learning summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/suggestions/{domain}")
async def get_suggestions(domain: str):
    """Get improvement suggestions for a domain."""
    try:
        suggestions = preference_updater.suggest_improvements(domain)
        return {"suggestions": suggestions}
    except Exception as e:
        logger.error(f"Error getting suggestions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Helper function to process query in background
async def process_query(query: Query, depth: str):
    """Process a query in the background."""
    try:
        logger.info(f"Processing query: {query.query_text}")
        result_path = await pipeline.process(query, depth=depth)
        logger.info(f"Query processed: {result_path}")
    except Exception as e:
        logger.error(f"Error processing query: {e}")


# Serve static files
@app.get("/")
async def root():
    """Serve the main HTML page."""
    return FileResponse("knowledgeweaver/ui/web/index.html")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
