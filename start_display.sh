#!/bin/bash
# Start virtual display for Puppeteer

# Check if display is already running
if pgrep -x "Xvfb" > /dev/null; then
    echo "✅ Virtual display already running"
    export DISPLAY=:99
    exit 0
fi

# Start Xvfb on display :99
echo "🖥️  Starting virtual display..."
Xvfb :99 -screen 0 1920x1080x24 &
XVFB_PID=$!

# Wait a moment for Xvfb to start
sleep 2

# Set DISPLAY environment variable
export DISPLAY=:99

# Save PID for cleanup
echo $XVFB_PID > .xvfb_pid

echo "✅ Virtual display started on DISPLAY=:99"
echo "📝 Xvfb PID: $XVFB_PID saved to .xvfb_pid"
