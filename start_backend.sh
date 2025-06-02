#!/bin/bash

echo "🚀 Starting Bank Statement Parser"
echo "================================="

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 is not installed"
    exit 1
fi

echo "✅ Python3 found"

# Navigate to backend directory
cd backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "🔧 Creating Python virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "❌ Failed to create virtual environment"
        echo "   Installing python3-venv..."
        sudo apt update && sudo apt install -y python3-venv python3-full
        python3 -m venv venv
    fi
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip

echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

echo "🧪 Testing CSV parser..."
python test_parser.py

if [ $? -eq 0 ]; then
    echo "✅ Backend test passed!"
    echo "🚀 Starting FastAPI server..."
    echo "   Backend will be available at: http://127.0.0.1:8000"
    echo "   Press Ctrl+C to stop"
    echo ""
    python main.py
else
    echo "❌ Backend test failed!"
    exit 1
fi
