"""
Serve the built React app from the same origin as the API.
"""
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse


def register_frontend(app: FastAPI, build_dir: Path) -> None:
    """
    Serve files from build_dir, and index.html for any other non-API path so
    client-side routes work on reload. Call after the API routers are added.
    """
    build_dir = build_dir.resolve()
    index = build_dir / "index.html"

    @app.get("/{path:path}", include_in_schema=False)
    async def frontend(path: str):
        if path == "api" or path.startswith("api/"):
            raise HTTPException(status_code=404, detail="Not Found")
        candidate = (build_dir / path).resolve()
        if path and candidate.is_file() and candidate.is_relative_to(build_dir):
            return FileResponse(candidate)
        return FileResponse(index)
