# HisaabFlow - Development Commands & Workflows

## Essential Commands

### Project Startup
```bash
# One-command setup and launch (recommended)
./start_app.sh

# Manual startup (alternative)
# Backend (in backend/ directory):
source venv/bin/activate
python main.py

# Frontend (in frontend/ directory):
npm start  # or yarn start
```

### Development Environment Setup
```bash
# Backend virtual environment
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Frontend dependencies
cd frontend
npm install  # or yarn install
```

### File Operations
```bash
# File listing and navigation
ls -la                    # List all files
find . -name "*.py"       # Find Python files
find . -name "*.js"       # Find JavaScript files
grep -r "pattern" .       # Search for text patterns
```

### Git Operations
```bash
git log --oneline -10     # Recent commits
git status               # Working directory status
git add .                # Stage changes
git commit -m "message"  # Commit changes
```

### Process Management
```bash
# Check port usage
lsof -i :8000            # Backend port
lsof -i :3000            # Frontend port

# Kill processes
lsof -ti :8000 | xargs kill -9  # Kill backend
lsof -ti :3000 | xargs kill -9  # Kill frontend
```

## Development Workflow

### Code Modification Process
1. **Read existing code** before making changes
2. **Check file sizes** in CODEBASE_MAP.md (keep under 200 lines)
3. **Use inline debugging** (console.log, print statements)
4. **Test immediately** with live reload
5. **Update documentation** if needed

### Configuration Management
- **Bank configs**: Located in `configs/` directory
- **App config**: `configs/app.conf` (created from template)
- **Sample data**: `sample_data/` directory for testing

### Debugging Approach
- **No separate test files** - Use inline validation only
- **Backend debugging**: print() statements in Python code
- **Frontend debugging**: console.log() in JavaScript
- **Live testing**: Use running application for immediate feedback