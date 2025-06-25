"""
Middleware setup for logging and request handling
"""
from fastapi import Request

def setup_logging_middleware(app):
    """Setup logging middleware for the FastAPI app"""
    
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        print(f" {request.method} {request.url} - Origin: {request.headers.get('origin', 'None')}")
        response = await call_next(request)
        print(f"Response: {response.status_code}")
        return response
