"""Web UI backend for KnowledgeWeaver using FastAPI."""

import asyncio
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from knowledgeweaver.core.synthesis_pipeline import SynthesisPipeline
from knowledgeweaver.core.query_manager import Query
from knowledgeweaver.learning.keyword_recommender import KeywordRecommender
from knowledgeweaver.learning.feedback_collector import FeedbackCollector
from knowledgeweaver.config import settings
from knowledgeweaver.utils.logger import logger

# ---------------------------------------------------------------------------
# Global in-memory stores
# ---------------------------------------------------------------------------

# query_id -> dict with keys: query_id, query_text, domain, status,
#   created_at (ISO str), started_at, completed_at, result_path (filename only),
#   error_message, progress_message, processing_time, user_rating, feedback_text
queries_store: dict[str, dict] = {}

# query_id -> list of progress message strings
progress_store: dict[str, list[str]] = {}

# Semaphore to cap concurrent pipeline runs
_pipeline_semaphore = asyncio.Semaphore(4)

# ---------------------------------------------------------------------------
# Module-level singletons
# ---------------------------------------------------------------------------

pipeline = SynthesisPipeline()
feedback_collector = FeedbackCollector()

# ---------------------------------------------------------------------------
# Seed keywords returned when the recommender DB is not yet available
# ---------------------------------------------------------------------------

_SEED_KEYWORDS = [
    {"word": "machine learning", "weight": 10, "count": 0},
    {"word": "deep learning", "weight": 9, "count": 0},
    {"word": "neural networks", "weight": 9, "count": 0},
    {"word": "natural language processing", "weight": 8, "count": 0},
    {"word": "computer vision", "weight": 8, "count": 0},
]

# ---------------------------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------------------------

app = FastAPI(
    title="KnowledgeWeaver",
    description="Intelligent Research Synthesis System",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Pydantic request models
# ---------------------------------------------------------------------------


class QueryRequest(BaseModel):
    query_text: str
    depth: str = "medium"


class FeedbackRequest(BaseModel):
    query_id: str
    rating: int
    feedback_text: str = ""

# ---------------------------------------------------------------------------
# Background pipeline runner
# ---------------------------------------------------------------------------


async def run_pipeline(query_id: str, query_text: str, depth: str) -> None:
    """Run the synthesis pipeline for a query, updating queries_store."""
    async with _pipeline_semaphore:
        started_at = datetime.utcnow()
        queries_store[query_id]["status"] = "processing"
        queries_store[query_id]["started_at"] = started_at.isoformat()
        progress_store.setdefault(query_id, [])

        def on_progress(message: str) -> None:
            progress_store[query_id].append(message)
            queries_store[query_id]["progress_message"] = message
            logger.debug(f"[{query_id[:8]}] {message}")

        try:
            query = Query(
                query_id=query_id,
                query_text=query_text,
            )
            result = await pipeline.process(
                query, depth=depth, on_progress=on_progress
            )
            completed_at = datetime.utcnow()
            processing_time = (completed_at - started_at).total_seconds()
            queries_store[query_id].update(
                {
                    "status": "completed",
                    "result_path": Path(result).name if result else None,
                    "completed_at": completed_at.isoformat(),
                    "processing_time": processing_time,
                    "domain": getattr(query, "domain", ""),
                }
            )
            logger.info(
                f"Query {query_id[:8]} completed in {processing_time:.1f}s"
            )
        except Exception as exc:
            queries_store[query_id].update(
                {
                    "status": "failed",
                    "error_message": str(exc),
                    "completed_at": datetime.utcnow().isoformat(),
                }
            )
            logger.error(f"Query {query_id[:8]} failed: {exc}")

# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@app.post("/api/queries")
async def submit_query(request: QueryRequest, background_tasks: BackgroundTasks):
    """Submit a new research query."""
    if not request.query_text or not request.query_text.strip():
        raise HTTPException(status_code=400, detail="query_text cannot be empty")

    from uuid import uuid4
    query_id = str(uuid4())
    now = datetime.utcnow().isoformat()

    queries_store[query_id] = {
        "query_id": query_id,
        "query_text": request.query_text.strip(),
        "domain": "",
        "status": "pending",
        "created_at": now,
        "started_at": None,
        "completed_at": None,
        "result_path": None,
        "error_message": None,
        "progress_message": None,
        "processing_time": None,
        "user_rating": None,
        "feedback_text": "",
    }
    progress_store[query_id] = []

    background_tasks.add_task(run_pipeline, query_id, request.query_text.strip(), request.depth)
    return {"query_id": query_id, "status": "pending"}


@app.get("/api/queries")
async def list_queries():
    """Return all queries sorted by created_at descending."""
    rows = sorted(
        queries_store.values(),
        key=lambda q: q.get("created_at") or "",
        reverse=True,
    )
    return [
        {
            "query_id": q["query_id"],
            "query_text": q["query_text"],
            "domain": q.get("domain", ""),
            "status": q["status"],
            "created_at": q.get("created_at"),
            "completed_at": q.get("completed_at"),
            "result_path": q.get("result_path"),
            "progress_message": q.get("progress_message"),
        }
        for q in rows
    ]


@app.get("/api/queries/{query_id}")
async def get_query(query_id: str):
    """Return a single query by ID."""
    entry = queries_store.get(query_id)
    if entry is None:
        raise HTTPException(status_code=404, detail="Query not found")
    return entry


@app.get("/api/queries/{query_id}/progress")
async def get_query_progress(query_id: str):
    """Return progress messages for a query."""
    if query_id not in queries_store:
        raise HTTPException(status_code=404, detail="Query not found")
    return {"messages": progress_store.get(query_id, [])}


@app.get("/api/recommendations")
async def get_recommendations():
    """Return keyword recommendations for the word cloud."""
    try:
        recommender = KeywordRecommender()
        keywords = recommender.get_recommendations(limit=40)
        return {"keywords": keywords}
    except Exception as exc:
        logger.warning(f"KeywordRecommender unavailable, returning seeds: {exc}")
        return {"keywords": _SEED_KEYWORDS}


@app.post("/api/feedback")
async def submit_feedback(request: FeedbackRequest):
    """Record user feedback for a completed query."""
    if request.query_id not in queries_store:
        raise HTTPException(status_code=404, detail="Query not found")
    if not 1 <= request.rating <= 5:
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")

    queries_store[request.query_id]["user_rating"] = request.rating
    queries_store[request.query_id]["feedback_text"] = request.feedback_text

    try:
        feedback_collector.submit_feedback(
            request.query_id,
            rating=request.rating,
            feedback_text=request.feedback_text,
        )
    except Exception as exc:
        logger.warning(f"FeedbackCollector.submit_feedback failed: {exc}")

    return {"status": "ok"}


@app.get("/outputs/{filename}")
async def serve_output(filename: str):
    """Serve a generated HTML report from the outputs directory."""
    # Prevent path traversal
    if ".." in filename or "/" in filename or "\\" in filename:
        raise HTTPException(status_code=400, detail="Invalid filename")

    output_path = Path(settings.output_dir) / filename
    if not output_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(str(output_path))


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    active = sum(
        1 for q in queries_store.values() if q["status"] == "processing"
    )
    return {
        "status": "healthy",
        "active_queries": active,
        "total_queries": len(queries_store),
    }


@app.get("/")
async def root():
    """Serve the main web UI."""
    index = Path(__file__).parent / "index.html"
    return FileResponse(str(index))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
