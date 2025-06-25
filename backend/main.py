#!/usr/bin/env python3
"""
Bank Statement Parser - Clean Configuration-Based Backend
Lightweight entry point with modular API components
"""
from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import sys
 
# Add project root to path for consistent absolute imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
 
# Import modular API routers directly using absolute paths
try:
    from backend.api.config_endpoints import config_router
    from backend.api.file_endpoints import file_router
    from backend.api.parse_endpoints import parse_router
    from backend.api.transform_endpoints import transform_router
    from backend.api.middleware import setup_logging_middleware
    ROUTERS_AVAILABLE = True
except ImportError as e:
    print(f"[WARNING]  Router import failed: {e}")
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
    description="Modular configuration-based CSV parser for HisaabFlow"
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
        print(f" {request.method} {request.url}")
        response = await call_next(request)
        print(f"[OUT] Response: {response.status_code}")
        return response

# Register API routers if available
if ROUTERS_AVAILABLE:
    v1_router = APIRouter()
    v1_router.include_router(file_router, tags=["files"])
    v1_router.include_router(parse_router, tags=["parsing"])
    v1_router.include_router(transform_router, tags=["transformation"])
    v1_router.include_router(config_router, tags=["configs"])
    
    app.include_router(v1_router, prefix="/api/v1")
    
    # Add direct preview route for frontend compatibility
    app.include_router(parse_router, prefix="", tags=["preview"])
    
    # Add v3 compatibility routes for legacy frontend
    app.include_router(config_router, prefix="/api/v3", tags=["legacy-v3"])
else:
    print("[WARNING]  No API routers available - using minimal endpoints only")

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
    print("[WARNING]  Routers not available - this should not happen after import fixes")
else:
    print("[SUCCESS] All API routers loaded successfully - complete functionality available")

# Exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    print(f"[ERROR]  Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal server error: {str(exc)}"}
    )

if __name__ == "__main__":
    import uvicorn
    
    print("\n Starting HisaabFlow Configuration-Based FastAPI Server...")
    print("    Backend: http://127.0.0.1:8000")
    print("    API docs: http://127.0.0.1:8000/docs")
    print("   ️  Architecture: Modular API routers")
    print("    Main file: Under 300 lines")
    print("   Mode: Nuitka compiled executable")
    print("   ⏹️  Press Ctrl+C to stop")
    print("")
    
    # Parse command line arguments for executable compatibility
    host = "127.0.0.1"
    port = 8000
    
    for i, arg in enumerate(sys.argv):
        if arg == "--host" and i + 1 < len(sys.argv):
            host = sys.argv[i + 1]
        elif arg == "--port" and i + 1 < len(sys.argv):
            port = int(sys.argv[i + 1])
    
    try:
        uvicorn.run(
            "main:app",
            host=host,
            port=port,
            reload=False,  # Disable reload for compiled executable
            log_level="info"
        )
    except Exception as e:
        print(f"[ERROR]  Failed to start server: {e}")
        sys.exit(1)