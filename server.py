"""
FastAPI server - routes for the AI agent, ML model stats, and serves the React frontend.
"""

import logging
from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from models import QueryRequest, predictor
from agent import run_agent

logger = logging.getLogger(__name__)

app = FastAPI(title="Raft AI Agent", version="1.0.0")

# CORS for development (Vite dev server on :5173)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:8000"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
async def health():
    return {"status": "ok", "model_accuracy": predictor.accuracy}


@app.post("/api/query")
async def query(req: QueryRequest):
    """Run the LangGraph agent with a natural language query."""
    logger.info("Received query: %s", req.query)
    try:
        result = await run_agent(req.query)
        logger.info("Query completed successfully")
        return result
    except Exception as e:
        logger.error("Query failed: %s", e)
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)},
        )


@app.get("/api/stats")
async def stats():
    """Return logistic regression model stats."""
    return predictor.get_stats()


# --- Serve React Frontend ---

FRONTEND_DIR = Path(__file__).parent / "frontend" / "dist"

if FRONTEND_DIR.exists():
    app.mount("/assets", StaticFiles(directory=FRONTEND_DIR / "assets"), name="assets")

    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        """Serve React app - catch-all for client-side routing."""
        file_path = FRONTEND_DIR / full_path
        if file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(FRONTEND_DIR / "index.html")
