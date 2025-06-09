#!/bin/bash

# Bank Statement Parser - Easy Launcher
# This script starts both backend and frontend automatically

echo "🏦 Bank Statement Parser - Starting Application..."
echo "=================================================="

# Get the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to find Python 3
find_python() {
    for cmd in python3 python python3.11 python3.10 python3.9; do
        if command_exists "$cmd"; then
            if "$cmd" --version 2>&1 | grep -q "Python 3"; then
                echo "$cmd"
                return 0
            fi
        fi
    done
    return 1
}

# Function to check if port is in use
port_in_use() {
    lsof -i :$1 >/dev/null 2>&1
}

# Function to kill processes on specific ports
cleanup_ports() {
    echo "🧹 Cleaning up any existing processes..."
    if port_in_use 8000; then
        echo "   Stopping backend on port 8000..."
        lsof -ti :8000 | xargs kill -9 2>/dev/null || true
    fi
    if port_in_use 3000; then
        echo "   Stopping frontend on port 3000..."
        lsof -ti :3000 | xargs kill -9 2>/dev/null || true
    fi
    sleep 2
}

# Function to start backend
start_backend() {
    echo "🚀 Starting Backend Server..."
    
    # Check if virtual environment exists in root directory
    if [ ! -d "venv" ]; then
        echo "❌ Virtual environment not found in root directory!"
        echo "   Please run: python3 -m venv venv && source venv/bin/activate && pip install -r backend/requirements.txt"
        exit 1
    fi
    
    # Activate virtual environment from root directory
    source venv/bin/activate
    
    # Check if requirements are installed
    if ! python -c "import fastapi" 2>/dev/null; then
        echo "📦 Installing backend dependencies..."
        pip install -r backend/requirements.txt
    fi
    
    # Change to backend directory and start server
    cd backend
    echo "   Backend starting on http://127.0.0.1:8000"
    echo "   Using modular configuration-based system (v3.0.0)"
    echo "   Main file: main.py (clean modular version - 94 lines)"
    python main.py &
    BACKEND_PID=$!
    cd ..
    
    # Wait for backend to start
    echo "   Waiting for backend to initialize..."
    sleep 3
    
    # Check if backend started successfully
    if ! port_in_use 8000; then
        echo "❌ Backend failed to start!"
        exit 1
    fi
    echo "✅ Backend running successfully!"
}

# Function to start frontend
start_frontend() {
    echo "🎨 Starting Frontend Application..."
    cd frontend
    
    # Check if node_modules exists
    if [ ! -d "node_modules" ]; then
        echo "📦 Installing frontend dependencies..."
        if command_exists npm; then
            npm install
        elif command_exists yarn; then
            yarn install
        else
            echo "❌ Neither npm nor yarn found!"
            echo "   Please install Node.js: https://nodejs.org/"
            exit 1
        fi
    fi
    
    echo "   Frontend starting on http://localhost:3000"
    if command_exists npm; then
        npm start &
    elif command_exists yarn; then
        yarn start &
    fi
    FRONTEND_PID=$!
    cd ..
    
    # Wait for frontend to start
    echo "   Waiting for frontend to initialize..."
    sleep 5
    
    echo "✅ Frontend running successfully!"
}

# Function to open browser
open_browser() {
    echo "🌐 Opening application in browser..."
    sleep 2
    
    if command_exists xdg-open; then
        xdg-open http://localhost:3000 2>/dev/null
    elif command_exists open; then
        open http://localhost:3000 2>/dev/null
    elif command_exists start; then
        start http://localhost:3000 2>/dev/null
    else
        echo "   Please open http://localhost:3000 in your browser"
    fi
}

# Function to wait for user input to stop
wait_for_stop() {
    echo ""
    echo "🎯 Application is running!"
    echo "   📡 Backend API: http://127.0.0.1:8000"
    echo "   🎨 Frontend:    http://localhost:3000"
    echo "   📋 API Docs:    http://127.0.0.1:8000/docs"
    echo ""
    echo "Press [CTRL+C] or [Enter] to stop the application..."
    
    # Set up trap to handle Ctrl+C
    trap 'echo; echo "🛑 Stopping application..."; cleanup_and_exit' INT
    
    # Wait for user input
    read -r
    cleanup_and_exit
}

# Function to clean up and exit
cleanup_and_exit() {
    echo "🧹 Shutting down servers..."
    
    # Kill backend and frontend processes
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null || true
    fi
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null || true
    fi
    
    # Clean up ports
    cleanup_ports
    
    echo "✅ Application stopped successfully!"
    echo "   Thank you for using Bank Statement Parser! 🏦"
    exit 0
}

# Main execution
main() {
    # Check system requirements
    echo "🔍 Checking system requirements..."
    
    PYTHON_CMD=$(find_python)
    if [ $? -ne 0 ]; then
        echo "❌ Python 3 not found!"
        echo "   Please install Python 3: https://python.org/"
        exit 1
    fi
    echo "   ✅ Python found: $PYTHON_CMD"
    
    if command_exists node; then
        echo "   ✅ Node.js found: $(node --version)"
    else
        echo "❌ Node.js not found!"
        echo "   Please install Node.js: https://nodejs.org/"
        exit 1
    fi
    
    if command_exists npm || command_exists yarn; then
        echo "   ✅ Package manager found"
    else
        echo "❌ npm or yarn not found!"
        exit 1
    fi
    
    echo ""
    
    # Clean up any existing processes
    cleanup_ports
    
    # Start services
    start_backend
    start_frontend
    open_browser
    wait_for_stop
}

# Run main function
main