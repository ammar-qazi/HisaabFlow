@echo off
title Bank Statement Parser Launcher

echo 🏦 Bank Statement Parser - Starting Application...
echo ==================================================

cd /d "%~dp0"

echo 🔍 Checking requirements...

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    python3 --version >nul 2>&1
    if errorlevel 1 (
        echo ❌ Python not found! Please install Python 3
        pause
        exit /b 1
    ) else (
        set PYTHON_CMD=python3
    )
) else (
    set PYTHON_CMD=python
)

echo ✅ Python found

:: Check Node.js
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js not found! Please install Node.js
    pause
    exit /b 1
)

echo ✅ Node.js found

:: Function to kill processes on ports
echo 🧹 Cleaning up any existing processes...
for /f "tokens=5" %%a in ('netstat -aon ^| find ":8000" ^| find "LISTENING"') do taskkill /F /PID %%a >nul 2>&1
for /f "tokens=5" %%a in ('netstat -aon ^| find ":3000" ^| find "LISTENING"') do taskkill /F /PID %%a >nul 2>&1

:: Start backend
echo 🚀 Starting Backend Server...
cd backend

if not exist "venv" (
    echo ❌ Virtual environment not found!
    echo    Please run: python -m venv venv
    pause
    exit /b 1
)

call venv\Scripts\activate.bat
start "Backend" /min cmd /c "%PYTHON_CMD% main.py"

echo    Backend starting on http://127.0.0.1:8000
echo    Waiting for backend to initialize...
timeout /t 3 /nobreak >nul

cd ..

:: Start frontend
echo 🎨 Starting Frontend Application...
cd frontend

if not exist "node_modules" (
    echo 📦 Installing frontend dependencies...
    npm install
)

echo    Frontend starting on http://localhost:3000
start "Frontend" /min cmd /c "npm start"

echo    Waiting for frontend to initialize...
timeout /t 5 /nobreak >nul

cd ..

:: Open browser
echo 🌐 Opening application in browser...
timeout /t 2 /nobreak >nul
start http://localhost:3000

echo.
echo 🎯 Application is running!
echo    📡 Backend API: http://127.0.0.1:8000
echo    🎨 Frontend:    http://localhost:3000
echo    📋 API Docs:    http://127.0.0.1:8000/docs
echo.
echo Press any key to stop the application...
pause >nul

echo 🛑 Stopping application...
for /f "tokens=5" %%a in ('netstat -aon ^| find ":8000" ^| find "LISTENING"') do taskkill /F /PID %%a >nul 2>&1
for /f "tokens=5" %%a in ('netstat -aon ^| find ":3000" ^| find "LISTENING"') do taskkill /F /PID %%a >nul 2>&1

echo ✅ Application stopped successfully!
echo    Thank you for using Bank Statement Parser! 🏦
pause
