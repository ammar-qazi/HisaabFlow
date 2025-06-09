#!/usr/bin/env python3
"""
Bank Statement Parser - Clean Configuration-Based Backend
Lightweight entry point with modular API components
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import sys

# Add paths for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'api'))

# Import modular API routers directly (avoiding problematic __init__.py)
try:
    from api.config_endpoints import config_router
    from api.file_endpoints import file_router  
    from api.parse_endpoints import parse_router
    from api.transform_endpoints import transform_router
    from api.middleware import setup_logging_middleware
    ROUTERS_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Router import failed: {e}")
    print("🔄 Using minimal endpoints instead...")
    ROUTERS_AVAILABLE = False
    config_router = None
    file_router = None
    parse_router = None
    transform_router = None
    setup_logging_middleware = None

# Initialize FastAPI app
app = FastAPI(
    title="Bank Statement Parser API - Configuration Based", 
    version="3.0.0",
    description="Modular configuration-based CSV parser for Cashew"
)

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup logging middleware
if ROUTERS_AVAILABLE and setup_logging_middleware:
    setup_logging_middleware(app)
else:
    # Basic logging middleware fallback
    @app.middleware("http")
    async def log_requests(request, call_next):
        print(f"🔍 {request.method} {request.url}")
        response = await call_next(request)
        print(f"📤 Response: {response.status_code}")
        return response

# Register API routers if available
if ROUTERS_AVAILABLE:
    app.include_router(config_router, prefix="/api/v3", tags=["configs"])
    app.include_router(file_router, tags=["files"])
    app.include_router(parse_router, tags=["parsing"])
    app.include_router(transform_router, tags=["transformation"])
else:
    print("⚠️  No API routers available - using minimal endpoints only")

@app.get("/")
async def root():
    return {
        "message": "Bank Statement Parser API - Configuration Based",
        "version": "3.0.0",
        "architecture": "Modular API endpoints",
        "features": [
            "Configuration-based bank rules",
            "No template system", 
            "Clean modular architecture",
            "Under 300-line main.py",
            f"Routers available: {ROUTERS_AVAILABLE}"
        ]
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "3.0.0"}

# All routers loaded successfully - no fallback endpoints needed
if not ROUTERS_AVAILABLE:
    print("⚠️  Routers not available - this should not happen after import fixes")
else:
    print("✅ All API routers loaded successfully - complete functionality available")

# Exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    print(f"❌ Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal server error: {str(exc)}"}
    )

if __name__ == "__main__":
    import uvicorn
    print("\n🌟 Starting Modular Configuration-Based FastAPI Server...")
    print("   📡 Backend: http://127.0.0.1:8000")
    print("   📋 API docs: http://127.0.0.1:8000/docs")
    print("   ⚙️  Architecture: Modular API routers")
    print("   📏 Main file: Under 300 lines")
    print("   ⏹️  Press Ctrl+C to stop")
    print("")
    
    try:
        uvicorn.run(
            "main:app",
            host="127.0.0.1",
            port=8000,
            reload=True,
            log_level="info"
        )
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
