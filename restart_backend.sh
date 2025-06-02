#!/bin/bash

echo "🔧 Backend Troubleshooting & Restart"
echo "====================================="

cd backend

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Check if FastAPI is installed
echo "📦 Checking dependencies..."
python -c "import fastapi, uvicorn, pandas; print('✅ All dependencies found')" || {
    echo "❌ Missing dependencies, installing..."
    pip install fastapi uvicorn pandas python-multipart pydantic
}

# Kill any existing process on port 8000
echo "🧹 Cleaning up port 8000..."
pkill -f "python.*main.py" || true
pkill -f "uvicorn.*main:app" || true

# Wait a moment
sleep 2

# Check if port is free
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null ; then
    echo "⚠️  Port 8000 is still in use"
    echo "Processes using port 8000:"
    lsof -i :8000
    echo ""
    echo "Kill them with: kill -9 $(lsof -t -i:8000)"
    exit 1
fi

echo "✅ Port 8000 is free"

# Start server with alternative method
echo "🚀 Starting FastAPI server..."
echo "   📡 Will be available at: http://127.0.0.1:8000"
echo "   📋 API docs at: http://127.0.0.1:8000/docs"
echo ""

# Try multiple startup methods
echo "Trying method 1: uvicorn command..."
uvicorn main:app --host 127.0.0.1 --port 8000 --reload || {
    echo "❌ Method 1 failed, trying method 2: python script..."
    python main.py || {
        echo "❌ Method 2 failed, trying method 3: direct python..."
        python -c "
import uvicorn
from main import app
print('Starting with direct Python call...')
uvicorn.run(app, host='127.0.0.1', port=8000)
        "
    }
}
