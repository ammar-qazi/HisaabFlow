# Puppeteer Display Fix - Manual Installation Guide

## The Problem
Puppeteer fails with: `Missing X server or $DISPLAY`

## Quick Solution (Run these commands manually)

### 1. Install Required Packages
```bash
# Install Xvfb (Virtual display server)
sudo apt update
sudo apt install -y xvfb

# Install browser dependencies
sudo apt install -y \
    gconf-service libasound2 libatk1.0-0 libcairo2 libcups2 \
    libfontconfig1 libgdk-pixbuf2.0-0 libgtk-3-0 libnspr4 \
    libpango-1.0-0 libxrandr2 libxss1 libxtst6 ca-certificates \
    fonts-liberation libappindicator1 libnss3 lsb-release \
    xdg-utils wget chromium-browser
```

### 2. Start Virtual Display
```bash
# Start Xvfb in background
Xvfb :99 -screen 0 1920x1080x24 &

# Set display environment variable
export DISPLAY=:99
```

### 3. Test Puppeteer
After running the above commands, test Puppeteer with:

## Alternative: Headless Mode Configuration

If you prefer not to install display server, configure Puppeteer with proper headless mode:

### Option A: Environment Variable Method
```bash
# Set these environment variables
export DISPLAY=:99
export PUPPETEER_EXECUTABLE_PATH=/usr/bin/chromium-browser
export PUPPETEER_ARGS="--no-sandbox --disable-setuid-sandbox --disable-dev-shm-usage"
```

### Option B: Direct Configuration
When using Claude's Puppeteer MCP, it should automatically use headless mode, but the display error suggests the underlying browser still needs a display server.

## Automated Startup Integration

Add to your project's startup scripts:

### Update start_app.sh
```bash
#!/bin/bash

# Start virtual display if not running
if ! pgrep -x "Xvfb" > /dev/null; then
    echo "Starting virtual display for Puppeteer..."
    Xvfb :99 -screen 0 1920x1080x24 &
    export DISPLAY=:99
    sleep 2
fi

# Your existing startup commands
./start_backend.sh &
./start_frontend.sh &
```

### Add to .bashrc (Optional - Permanent)
```bash
# Add to ~/.bashrc for permanent display setup
if [ -z "$DISPLAY" ]; then
    export DISPLAY=:99
fi
```

## Testing Commands

After installation, test with these commands:

```bash
# 1. Check if Xvfb is installed
which xvfb-run

# 2. Test virtual display
DISPLAY=:99 xdpyinfo

# 3. Test browser launch
DISPLAY=:99 chromium-browser --headless --version

# 4. Start display manually
Xvfb :99 -screen 0 1920x1080x24 &
export DISPLAY=:99
```

## Troubleshooting

### If you get "command not found" for xvfb-run:
```bash
sudo apt install xvfb
```

### If Chromium is missing:
```bash
sudo apt install chromium-browser
# OR for Google Chrome:
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
sudo sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'
sudo apt update
sudo apt install google-chrome-stable
```

### If display issues persist:
```bash
# Kill existing Xvfb processes
pkill Xvfb
# Restart with different display number
Xvfb :100 -screen 0 1920x1080x24 &
export DISPLAY=:100
```

## For Your Bank Statement Parser

Once this is working, you can use Puppeteer for:
- **Bank login automation**: Automatically log into bank portals
- **Statement downloads**: Download CSV/PDF statements automatically  
- **Multi-bank processing**: Scrape data from multiple bank websites
- **Scheduled updates**: Automatically update statements daily/weekly

The key is getting the display environment working first, then Puppeteer MCP will function properly.
