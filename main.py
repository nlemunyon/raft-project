"""
Entry point - starts both the dummy customer API and the FastAPI server.

Usage:
    python main.py
"""

import os
import sys
import signal
import logging
import subprocess
import time
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


def main():
    # Check for API key
    if not os.getenv("OPENROUTER_API_KEY"):
        logger.error("OPENROUTER_API_KEY not found in environment.")
        logger.error("Create a .env file with: OPENROUTER_API_KEY=sk-or-...")
        sys.exit(1)

    # Check for frontend build
    frontend_dist = Path(__file__).parent / "frontend" / "dist"
    if not frontend_dist.exists():
        logger.warning("frontend/dist/ not found. UI will not be served.")
        logger.warning("To build: cd frontend && npm install && npm run build")

    # Start dummy API as subprocess
    logger.info("Starting dummy customer API on port 5001...")
    dummy_proc = subprocess.Popen(
        [sys.executable, "dummy_customer_api.py"],
        cwd=Path(__file__).parent,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    # Give it a moment to start
    time.sleep(1)

    if dummy_proc.poll() is not None:
        logger.error("Dummy API failed to start.")
        sys.exit(1)

    logger.info("Dummy API running on http://localhost:5001")

    # Handle cleanup
    def cleanup(signum=None, frame=None):
        logger.info("Shutting down...")
        dummy_proc.terminate()
        try:
            dummy_proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            dummy_proc.kill()
        sys.exit(0)

    signal.signal(signal.SIGINT, cleanup)
    signal.signal(signal.SIGTERM, cleanup)

    # Start FastAPI
    logger.info("Starting FastAPI server on port 8000...")
    logger.info("=" * 50)
    logger.info("  Raft AI Agent is running!")
    logger.info("  API:  http://localhost:8000/api/query")
    if frontend_dist.exists():
        logger.info("  UI:   http://localhost:8000")
    logger.info("  Docs: http://localhost:8000/docs")
    logger.info("=" * 50)

    try:
        import uvicorn
        uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=False)
    finally:
        cleanup()


if __name__ == "__main__":
    main()
