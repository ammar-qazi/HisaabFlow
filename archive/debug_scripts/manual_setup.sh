#!/bin/bash

echo "🔧 Manual Setup Instructions"
echo "============================"
echo ""

echo "If the automatic script fails, follow these manual steps:"
echo ""

echo "1. 🐍 Setup Python Backend:"
echo "   cd backend"
echo "   python3 -m venv venv"
echo "   source venv/bin/activate"
echo "   pip install --upgrade pip"
echo "   pip install pandas fastapi uvicorn python-multipart pydantic"
echo "   python test_parser.py"
echo "   python main.py"
echo ""

echo "2. 🎨 Setup Frontend (in another terminal):"
echo "   cd frontend"
echo "   npm install"
echo "   npm run electron-dev"
echo ""

echo "3. 🧪 Test the Application:"
echo "   - Backend should be running at: http://127.0.0.1:8000"
echo "   - Frontend desktop app should open automatically"
echo "   - Upload the nayapay_statement.csv file to test"
echo ""

echo "4. 📦 If you don't have Node.js:"
echo "   sudo apt update"
echo "   sudo apt install nodejs npm"
echo "   node --version  # Should be 14+"
echo ""

echo "5. 🐍 If you don't have python3-venv:"
echo "   sudo apt update"
echo "   sudo apt install python3-venv python3-full python3-pip"
echo ""

echo "6. ⚡ Quick test without virtual environment (risky):"
echo "   pip install --break-system-packages pandas fastapi uvicorn"
echo "   # Not recommended but works if you're okay with system packages"
echo ""

echo "💡 Troubleshooting:"
echo "   - Make sure both backend (port 8000) and frontend (port 3000) aren't blocked"
echo "   - Check Python version: python3 --version (should be 3.8+)"
echo "   - Check Node version: node --version (should be 14+)"
echo "   - If Electron fails to start, try: npm install electron --save-dev"
