"""
Request logging middleware
"""
import logging

from fastapi import Request

logger = logging.getLogger(__name__)


def setup_logging_middleware(app):
    """Log method, path and status code for each request"""

    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        response = await call_next(request)
        logger.info("%s %s -> %s", request.method, request.url.path, response.status_code)
        return response
