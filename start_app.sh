#!/bin/bash

# Bank Statement Parser - One-Command Launcher
# This script handles complete setup and starts both backend and frontend automatically

echo " Bank Statement Parser - One-Command Setup & Launch"
echo "====================================================="

# Get the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to find Python 3
find_python() {
    for cmd in python3 python python3.11 python3.10 python3.9; do
        if command_exists "$cmd"; then
            if "$cmd" --version 2>&1 | grep -q "Python 3"; then
                echo "$cmd"
                return 0
            fi
        fi
    done
    return 1
}

# Function to check if port is in use
port_in_use() {
    lsof -i :$1 >/dev/null 2>&1
}

# Function to kill processes on specific ports
cleanup_ports() {
    echo "🧹 Cleaning up any existing processes..."
    if port_in_use 8000; then
        echo "   Stopping backend on port 8000..."
        lsof -ti :8000 | xargs kill -9 2>/dev/null || true
    fi
    if port_in_use 3000; then
        echo "   Stopping frontend on port 3000..."
        lsof -ti :3000 | xargs kill -9 2>/dev/null || true
    fi
    sleep 2
}

# Function to setup configuration files
setup_configuration() {
    echo " Setting up configuration files..."
    
    # Check if app.conf exists
    if [ ! -f "configs/app.conf" ]; then
        if [ -f "configs/app.conf.template" ]; then
            echo "   Creating configs/app.conf from template..."
            cp configs/app.conf.template configs/app.conf
            echo "   [WARNING]  Please edit configs/app.conf to set your actual name for transfer detection"
        else
            echo "   [ERROR]  configs/app.conf.template not found!"
            echo "   Creating basic app.conf..."
            mkdir -p configs
            cat > configs/app.conf << EOF
[general]
date_tolerance_hours = 72
user_name = Your Name Here

[transfer_detection]
confidence_threshold = 0.7

[transfer_categorization]
default_pair_category = Balance Correction
EOF
        fi
    else
        echo "   [SUCCESS] configs/app.conf already exists"
    fi
}

# Function to setup Python virtual environment
setup_python_env() {
    echo " Setting up Python environment..."
    
    # Check if virtual environment exists in backend directory
    if [ ! -d "backend/venv" ]; then
        echo "   Creating Python virtual environment..."
        cd backend
        $PYTHON_CMD -m venv venv
        if [ $? -ne 0 ]; then
            echo "   [ERROR]  Failed to create virtual environment!"
            echo "   Please ensure Python 3 and venv module are properly installed"
            exit 1
        fi
        cd ..
        echo "   [SUCCESS] Virtual environment created successfully"
    else
        echo "   [SUCCESS] Virtual environment already exists"
    fi
}
# Function to start backend
start_backend() {
    echo "[START] Starting Backend Server..."
    
    # Activate virtual environment from backend directory
    source backend/venv/bin/activate
    
    # Check if requirements are installed
    if ! $PYTHON_CMD -c "import fastapi" 2>/dev/null; then
        echo " Installing backend dependencies..."
        # Make sure we're using the virtual environment's pip
        $PYTHON_CMD -m pip install -r backend/requirements.txt
        if [ $? -ne 0 ]; then
            echo "   [ERROR]  Failed to install backend dependencies!"
            exit 1
        fi
    fi
    
    # Change to backend directory and start server
    cd backend
    echo "   Backend starting on http://127.0.0.1:8000"
    echo "   Using modular configuration-based system"
    $PYTHON_CMD main.py &
    BACKEND_PID=$!
    cd ..
    
    # Wait for backend to start
    echo "   Waiting for backend to initialize..."
    sleep 3
    
    # Check if backend started successfully
    if ! port_in_use 8000; then
        echo "[ERROR]  Backend failed to start!"
        exit 1
    fi
    echo "[SUCCESS] Backend running successfully!"
}

# Function to start frontend (Electron desktop app)
start_frontend() {
    echo " Starting Frontend Application (Desktop)..."
    cd frontend
    
    # Check if node_modules exists
    if [ ! -d "node_modules" ]; then
        echo " Installing frontend dependencies..."
        if command_exists npm; then
            npm install
        elif command_exists yarn; then
            yarn install
        else
            echo "[ERROR]  Neither npm nor yarn found!"
            echo "   Please install Node.js: https://nodejs.org/"
            exit 1
        fi
    fi
    
    echo "   Launching Electron desktop application..."
    echo "   React dev server will start on http://localhost:3000 (internal)"
    if command_exists npm; then
        npm run electron-dev &
    elif command_exists yarn; then
        yarn run electron-dev &
    fi
    FRONTEND_PID=$!
    cd ..
    
    # Wait for frontend to start
    echo "   Waiting for Electron app to initialize..."
    sleep 8
    
    echo "[SUCCESS] Electron desktop app running successfully!"
}

# Function to handle desktop app launch (no browser needed)
handle_desktop_launch() {
    echo "️  Desktop application launched successfully!"
    echo "   Note: App will open in a separate desktop window"
    echo "   (No browser window needed for desktop mode)"
}

# Function to wait for user input to stop
wait_for_stop() {
    echo ""
    echo "Application is running!"
    echo "    Backend API: http://127.0.0.1:8000"
    echo "   ️  Desktop App: Running in separate window"
    echo "    API Docs:    http://127.0.0.1:8000/docs"
    echo ""
    echo "Press [CTRL+C] or [Enter] to stop the application..."
    
    # Set up trap to handle Ctrl+C
    trap 'echo; echo " Stopping application..."; cleanup_and_exit' INT
    
    # Wait for user input
    read -r
    cleanup_and_exit
}

# Function to clean up and exit
cleanup_and_exit() {
    echo "🧹 Shutting down servers..."
    
    # Kill backend and frontend processes
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null || true
    fi
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null || true
    fi
    
    # Clean up ports
    cleanup_ports
    
    echo "[SUCCESS] Application stopped successfully!"
    echo ""
    echo " To run again, simply execute: ./start_app.sh"
    echo "   Thank you for using Bank Statement Parser! "
    exit 0
}

# Main execution
main() {
    # Check system requirements
    echo " Checking system requirements..."
    
    PYTHON_CMD=$(find_python)
    if [ $? -ne 0 ]; then
        echo "[ERROR]  Python 3 not found!"
        echo "   Please install Python 3: https://python.org/"
        exit 1
    fi
    echo "   [SUCCESS] Python found: $PYTHON_CMD"
    
    if command_exists node; then
        echo "   [SUCCESS] Node.js found: $(node --version)"
    else
        echo "[ERROR]  Node.js not found!"
        echo "   Please install Node.js: https://nodejs.org/"
        exit 1
    fi
    
    if command_exists npm || command_exists yarn; then
        echo "   [SUCCESS] Package manager found"
    else
        echo "[ERROR]  npm or yarn not found!"
        exit 1
    fi
    
    echo ""
    
    # Setup configuration files
    setup_configuration
    
    # Setup Python environment
    setup_python_env
    
    # Clean up any existing processes
    cleanup_ports
    
    # Start services
    start_backend
    start_frontend
    handle_desktop_launch
    wait_for_stop
}

# Run main function
main