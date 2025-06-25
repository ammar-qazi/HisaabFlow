#!/bin/bash

# HisaabFlow Desktop App Startup Script
# Handles both development and production scenarios

echo "[START] Starting HisaabFlow Desktop App..."

# Check if we're in development mode
if [ -f "../backend/main.py" ]; then
    echo " Development mode detected"
    echo " Backend path: ../backend"
    
    # Check if Python is available
    if command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
    elif command -v python &> /dev/null; then
        PYTHON_CMD="python"
    else
        echo "[ERROR]  Python not found! Please install Python 3.9+"
        echo "   Visit: https://www.python.org/downloads/"
        exit 1
    fi
    
    echo " Python command: $PYTHON_CMD"
    
    # Check if backend dependencies are installed
    if [ ! -d "../backend/venv" ]; then
        echo " Setting up Python virtual environment..."
        cd ../backend
        $PYTHON_CMD -m venv venv
        source venv/bin/activate
        pip install -r requirements.txt
        cd ../frontend
        echo "[SUCCESS] Backend dependencies installed"
    fi
    
    echo " Development setup complete"
    echo " Starting Electron app..."
    npm run electron-dev
    
else
    echo " Production mode - backend should be bundled"
    echo " Starting Electron app..."
    npm run electron
fi
