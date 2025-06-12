#!/bin/bash

# Test Puppeteer Environment with Firefox
echo "🧪 Testing Puppeteer Environment with Firefox..."

# Check if Xvfb is installed
if ! command -v xvfb-run &> /dev/null; then
    echo "❌ Xvfb not installed. Run: sudo apt install -y xvfb"
    exit 1
fi

echo "✅ Xvfb found"

# Check Firefox
if ! command -v firefox &> /dev/null; then
    echo "❌ Firefox not found"
    exit 1
fi

echo "✅ Firefox found: $(firefox --version)"

# Set display
export DISPLAY=:99

# Start Xvfb if not running
if ! pgrep -x "Xvfb" > /dev/null; then
    echo "🖥️  Starting virtual display..."
    Xvfb :99 -screen 0 1920x1080x24 &
    XVFB_PID=$!
    echo "Started Xvfb with PID: $XVFB_PID"
    sleep 3
else
    echo "✅ Xvfb already running"
fi

# Test display
echo "🧪 Testing virtual display..."
if xdpyinfo -display :99 >/dev/null 2>&1; then
    echo "✅ Virtual display working"
else
    echo "⚠️  Display test had issues but continuing..."
fi

# Test Firefox headless mode
echo "🧪 Testing Firefox headless mode..."
TEST_FILE="/tmp/puppeteer_test_$(date +%s).png"

if DISPLAY=:99 timeout 30s firefox --headless --screenshot="$TEST_FILE" "https://example.com" >/dev/null 2>&1; then
    if [ -f "$TEST_FILE" ]; then
        echo "✅ Firefox headless test successful! Screenshot saved to: $TEST_FILE"
        echo "📄 Screenshot size: $(du -h "$TEST_FILE" | cut -f1)"
        rm "$TEST_FILE"
    else
        echo "⚠️  Firefox ran but no screenshot created"
    fi
else
    echo "⚠️  Firefox test had issues but may still work with Puppeteer"
fi

echo ""
echo "🎉 Environment test complete!"
echo "💡 DISPLAY set to: $DISPLAY"
echo ""
echo "📋 If all tests passed, Puppeteer MCP should now work!"
echo ""
echo "🧹 To stop virtual display:"
echo "   pkill Xvfb"
echo ""
