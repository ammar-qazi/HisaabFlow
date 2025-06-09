#!/bin/bash

# Test script to verify the venv path fix
echo "🧪 Testing venv path fix..."

# Get the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "📁 Current directory: $(pwd)"
echo "🔍 Checking for venv locations..."

# Check root venv
if [ -d "venv" ]; then
    echo "✅ Found venv in root directory: $(pwd)/venv"
    echo "   Python executable: $(ls -la venv/bin/python* | head -1)"
else
    echo "❌ No venv in root directory"
fi

# Check backend venv  
if [ -d "backend/venv" ]; then
    echo "✅ Found venv in backend directory: $(pwd)/backend/venv"
    echo "   Python executable: $(ls -la backend/venv/bin/python* | head -1)"
else
    echo "❌ No venv in backend directory"
fi

# Test activation of root venv
echo ""
echo "🧪 Testing root venv activation..."
if [ -d "venv" ]; then
    source venv/bin/activate
    if python -c "import fastapi" 2>/dev/null; then
        echo "✅ Root venv works: FastAPI is available"
        echo "   Python version: $(python --version)"
        echo "   Python path: $(which python)"
    else
        echo "⚠️  Root venv activated but FastAPI not installed"
        echo "   Python version: $(python --version)"
        echo "   Available packages: $(pip list | head -5)"
    fi
    deactivate
else
    echo "❌ Cannot test - no root venv found"
fi

echo ""
echo "🎯 Recommended configuration:"
echo "   ✅ Use root venv: $(pwd)/venv"
echo "   ✅ Backend dir: $(pwd)/backend"
echo "   ✅ Requirements: $(pwd)/backend/requirements.txt"
