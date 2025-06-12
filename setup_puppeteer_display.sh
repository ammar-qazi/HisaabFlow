#!/bin/bash

# Puppeteer Display Environment Setup Script
# Fixes: Missing X server or $DISPLAY error

echo "🚀 Setting up Puppeteer display environment..."

# 1. Install Xvfb (Virtual Framebuffer X11 server)
echo "📦 Installing Xvfb and dependencies..."
sudo apt update
sudo apt install -y xvfb

# 2. Install additional browser dependencies
echo "📦 Installing browser dependencies..."
sudo apt install -y \
    gconf-service \
    libasound2 \
    libatk1.0-0 \
    libcairo2 \
    libcups2 \
    libfontconfig1 \
    libgdk-pixbuf2.0-0 \
    libgtk-3-0 \
    libnspr4 \
    libpango-1.0-0 \
    libxrandr2 \
    libxss1 \
    libxtst6 \
    ca-certificates \
    fonts-liberation \
    libappindicator1 \
    libnss3 \
    lsb-release \
    xdg-utils \
    wget

# 3. Install Chrome/Chromium if not present
if ! command -v google-chrome &> /dev/null && ! command -v chromium-browser &> /dev/null; then
    echo "📦 Installing Chromium browser..."
    sudo apt install -y chromium-browser
fi

# 4. Test Xvfb installation
echo "🧪 Testing Xvfb installation..."
if command -v xvfb-run &> /dev/null; then
    echo "✅ Xvfb installed successfully"
else
    echo "❌ Xvfb installation failed"
    exit 1
fi

# 5. Create display startup script
echo "📝 Creating display startup script..."
cat > start_display.sh << 'EOF'
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
EOF

chmod +x start_display.sh

# 6. Create display cleanup script
echo "📝 Creating display cleanup script..."
cat > stop_display.sh << 'EOF'
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
EOF

chmod +x stop_display.sh

# 7. Test the setup
echo "🧪 Testing virtual display setup..."
./start_display.sh

# Test if DISPLAY is working
if DISPLAY=:99 xdpyinfo >/dev/null 2>&1; then
    echo "✅ Virtual display test successful!"
else
    echo "⚠️  Virtual display test failed, but may still work with browsers"
fi

echo ""
echo "🎉 Puppeteer display setup complete!"
echo ""
echo "📋 Next steps:"
echo "   1. Run './start_display.sh' before using Puppeteer"
echo "   2. Set DISPLAY=:99 in your environment"
echo "   3. Run './stop_display.sh' when done"
echo ""
echo "🔧 For permanent setup, add to your .bashrc:"
echo "   export DISPLAY=:99"
echo ""
