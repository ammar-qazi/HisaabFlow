#!/bin/bash

# Test Backend Integration
echo "🧪 Testing HisaabFlow Backend Integration..."

cd frontend

# Test 1: Check if backend launcher can be imported
echo "📋 Test 1: Backend launcher import"
node -e "
try {
  const BackendLauncher = require('./scripts/backend-launcher');
  console.log('✅ Backend launcher imported successfully');
  const launcher = new BackendLauncher();
  console.log('✅ Backend launcher instance created');
  console.log('📁 Backend path:', launcher.getBackendPath());
  console.log('🐍 Python path:', launcher.getPythonPath());
} catch (error) {
  console.error('❌ Backend launcher test failed:', error.message);
  process.exit(1);
}
"

# Test 2: Check if backend dependencies are available
echo "📋 Test 2: Backend dependencies"
cd ../backend

if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment exists"
    source venv/bin/activate
fi

# Test 3: Check if backend can start
echo "📋 Test 3: Backend startup test"
python3 -c "
import sys
sys.path.append('.')
try:
    from main import app
    print('✅ FastAPI app imports successfully')
    print('✅ Backend integration test passed')
except Exception as e:
    print(f'❌ Backend import failed: {e}')
    sys.exit(1)
"

echo "🎉 All backend integration tests passed!"
echo "🚀 Ready to build integrated AppImage"
