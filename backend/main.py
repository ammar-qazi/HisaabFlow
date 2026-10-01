#!/usr/bin/env python3
"""
Bank Statement Parser - Clean Configuration-Based Backend
Lightweight entry point with modular API components
"""
from fastapi import FastAPI, APIRouter
from fastapi.responses import JSONResponse
import os
import sys
from pathlib import Path
 
# Add project root to path for consistent absolute imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import response models after path setup
from backend.logging_config import configure_logging
configure_logging()

from backend.api.models import HealthResponse
 
# A failed import here should stop startup, not serve an API without routes
from backend.api.config_endpoints import config_router
from backend.api.file_endpoints import file_router
from backend.api.parse_endpoints import parse_router
from backend.api.transform_endpoints import transform_router
from backend.api.unknown_bank_endpoints import unknown_bank_router
from backend.api.middleware import setup_logging_middleware
from backend.api.frontend import register_frontend
import logging

logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Bank Statement Parser API - Configuration Based", 
    version="3.0.0",
    description="Modular configuration-based CSV parser for HisaabFlow"
)

# No CORS: the UI is served from this app (Docker) or reaches it through the
# CRA dev server's proxy, so the browser always sees one origin.
setup_logging_middleware(app)

v1_router = APIRouter()
v1_router.include_router(file_router, tags=["files"])
v1_router.include_router(parse_router, tags=["parsing"])
v1_router.include_router(transform_router, tags=["transformation"])
v1_router.include_router(config_router, tags=["configs"])
v1_router.include_router(unknown_bank_router, tags=["unknown-bank"])
app.include_router(v1_router, prefix="/api/v1")

@app.get("/health", response_model=HealthResponse)
async def health_check():
    return {"status": "healthy", "version": "3.0.0"}

# The built React app, when present (the Docker image always has it).
# Registered last so its catch-all route doesn't shadow the API.
FRONTEND_DIR = Path(os.environ.get("HISAABFLOW_FRONTEND_DIR", Path(project_root) / "frontend" / "build"))
if (FRONTEND_DIR / "index.html").is_file():
    register_frontend(app, FRONTEND_DIR)

# Exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.exception("Unhandled exception")
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal server error: {str(exc)}"}
    )

if __name__ == "__main__":
    # Local run without Docker: python backend/main.py
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
