#!/bin/bash
# Stop virtual display

if [ -f .xvfb_pid ]; then
    XVFB_PID=$(cat .xvfb_pid)
    if kill -0 $XVFB_PID 2>/dev/null; then
        echo "🛑 Stopping virtual display (PID: $XVFB_PID)..."
        kill $XVFB_PID
        rm .xvfb_pid
        echo "✅ Virtual display stopped"
    else
        echo "ℹ️  Virtual display not running"
        rm -f .xvfb_pid
    fi
else
    echo "ℹ️  No virtual display PID file found"
fi

# Also kill any remaining Xvfb processes
pkill -f "Xvfb :99" 2>/dev/null || true
