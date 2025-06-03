# 🏦 Bank Statement Parser - Easy Launchers

Three convenient ways to start the Bank Statement Parser application without managing terminal commands!

## 🚀 Quick Start Options

### Option 1: Bash Script (Linux/Mac) - Recommended
```bash
./start_app.sh
```
- **Features**: Automatic setup, port cleanup, error handling
- **Best for**: Linux and Mac users who want a simple terminal-based launcher
- **Requirements**: Bash shell (standard on Linux/Mac)

### Option 2: Python GUI Launcher (Cross-Platform) - Most User-Friendly
```bash
python3 launch_gui.py
# or double-click launch_gui.py in file manager
```
- **Features**: 
  - Beautiful graphical interface
  - Real-time status indicators
  - Built-in log viewer
  - One-click start/stop
  - Auto-opens browser
  - System requirements checker
- **Best for**: Users who prefer graphical interfaces
- **Requirements**: Python 3 with tkinter (usually included)

### Option 3: Windows Batch File (Windows)
```cmd
start_app.bat
# or double-click start_app.bat in file explorer
```
- **Features**: Windows-optimized, automatic dependency checking
- **Best for**: Windows users who want a simple double-click solution
- **Requirements**: Windows command prompt

## 📋 What Each Launcher Does

All launchers automatically:
1. ✅ **Check Requirements** - Verify Python 3, Node.js, and dependencies
2. ✅ **Clean Ports** - Stop any existing processes on ports 3000/8000
3. ✅ **Start Backend** - Activate virtual environment and start FastAPI server
4. ✅ **Start Frontend** - Install dependencies (if needed) and start React app
5. ✅ **Open Browser** - Automatically open http://localhost:3000
6. ✅ **Easy Shutdown** - Simple stop mechanism with cleanup

## 🎯 Application URLs

Once started, access these URLs:
- **Frontend Application**: http://localhost:3000
- **Backend API**: http://127.0.0.1:8000  
- **API Documentation**: http://127.0.0.1:8000/docs

## 🔧 Troubleshooting

### Common Issues:

**"Virtual environment not found"**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# or venv\Scripts\activate.bat  # Windows
pip install -r requirements.txt
```

**"Node modules not found"**
```bash
cd frontend
npm install
```

**"Port already in use"**
- The launchers automatically clean up ports
- If issues persist, manually kill processes: `sudo lsof -ti :3000,:8000 | xargs kill -9`

**Python GUI launcher won't start**
```bash
# Install tkinter if missing (Ubuntu/Debian)
sudo apt-get install python3-tk

# Or use pip
pip install tk
```

## 🌟 Recommended Usage

1. **First-time users**: Use `launch_gui.py` for the best experience
2. **Developers**: Use `start_app.sh` for quick terminal-based startup
3. **Windows users**: Use `start_app.bat` for native Windows experience

## 📁 File Structure

```
bank_statement_parser/
├── start_app.sh       # Bash launcher (Linux/Mac)
├── launch_gui.py      # Python GUI launcher (Cross-platform)
├── start_app.bat      # Windows batch launcher
├── backend/           # FastAPI backend
├── frontend/          # React frontend
└── templates/         # Bank templates (NayaPay, Transferwise)
```

## 🎉 Features Supported

- **Multi-Bank Support**: NayaPay and Transferwise templates
- **Smart Categorization**: Automatic transaction categorization
- **Description Cleaning**: Clean, readable transaction descriptions
- **Robust CSV Parsing**: Handles various CSV formats and edge cases
- **Template System**: Easy to add new bank templates
- **Export to Cashew**: Perfect integration with Cashew finance app

---

**Choose your preferred launcher and start processing bank statements with one click! 🚀**