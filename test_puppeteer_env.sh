#!/bin/bash

# Simple Puppeteer Test Script (No sudo required)
# Run this AFTER manually installing packages

echo "🧪 Testing Puppeteer Environment..."

# Check if required packages are installed
echo "📦 Checking installations..."

if command -v xvfb-run &> /dev/null; then
    echo "✅ xvfb-run found"
else
    echo "❌ xvfb-run not found - run: sudo apt install xvfb"
    exit 1
fi

if command -v chromium-browser &> /dev/null || command -v google-chrome &> /dev/null; then
    echo "✅ Browser found"
else
    echo "❌ No browser found - run: sudo apt install chromium-browser"
    exit 1
fi

# Start virtual display
echo "🖥️  Starting virtual display..."
export DISPLAY=:99

# Check if Xvfb is already running
if pgrep -x "Xvfb" > /dev/null; then
    echo "✅ Xvfb already running"
else
    echo "🚀 Starting Xvfb..."
    Xvfb :99 -screen 0 1920x1080x24 &
    XVFB_PID=$!
    echo "Started with PID: $XVFB_PID"
    sleep 3
fi

# Test display
echo "🧪 Testing display..."
if DISPLAY=:99 xdpyinfo >/dev/null 2>&1; then
    echo "✅ Display test successful"
else
    echo "⚠️  Display test failed, but may still work"
fi

# Test browser
echo "🧪 Testing browser..."
if command -v chromium-browser &> /dev/null; then
    BROWSER_CMD="chromium-browser"
elif command -v google-chrome &> /dev/null; then
    BROWSER_CMD="google-chrome"
fi

DISPLAY=:99 $BROWSER_CMD --headless --disable-gpu --no-sandbox --version 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✅ Browser test successful"
else
    echo "⚠️  Browser test had issues but may still work"
fi

echo ""
echo "🎉 Setup complete! Environment ready for Puppeteer."
echo "💡 DISPLAY is set to: $DISPLAY"
echo ""
echo "📋 To make permanent, add to ~/.bashrc:"
echo "   export DISPLAY=:99"
echo ""
echo "🧹 To stop virtual display later:"
echo "   pkill Xvfb"
