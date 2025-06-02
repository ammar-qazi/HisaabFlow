#!/bin/bash

echo "🎨 Starting Frontend (Electron + React)"
echo "======================================="

# Check if Node.js is available
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed"
    echo "   Please install Node.js 14+ from https://nodejs.org"
    exit 1
fi

echo "✅ Node.js found: $(node --version)"

# Navigate to frontend directory
cd frontend

echo "📦 Installing Node.js dependencies..."
npm install

echo "🚀 Starting Electron development environment..."
echo "   This will start both React dev server and Electron app"
echo "   React dev server: http://localhost:3000"
echo "   Make sure backend is running at: http://127.0.0.1:8000"
echo ""
echo "   Press Ctrl+C to stop"
echo ""

npm run electron-dev
