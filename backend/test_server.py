#!/usr/bin/env python3

# Minimal test server to verify FastAPI works
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"status": "working", "message": "Test server is running"}

@app.get("/test")
def test():
    return {"test": "success", "backend": "connected"}

if __name__ == "__main__":
    import uvicorn
    print("🧪 Starting minimal test server on port 8000...")
    uvicorn.run("test_server:app", host="127.0.0.1", port=8000, reload=True)
