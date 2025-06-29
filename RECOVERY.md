# HisaabFlow Emergency Recovery Procedures

This document provides step-by-step emergency recovery procedures for HisaabFlow when refactoring goes wrong.

## 🚨 When to Use Emergency Recovery

- API endpoints stop responding
- Frontend-backend communication broken
- Desktop app won't start
- Configuration loading fails
- Any critical functionality is broken after changes

## ⚡ Quick Recovery (< 2 minutes)

### Automatic Rollback
If you used the `--rollback-on-failure` flag with integration tests:
```bash
./test_all_integration.sh --rollback-on-failure
# Automatically rolls back if any test fails
```

### Manual Git Rollback
```bash
# 1. Immediately rollback to previous commit
git reset --hard HEAD~1

# 2. Verify rollback worked
git log --oneline -1

# 3. Test system functionality
./test_api_coverage.sh
```

## 🔧 Standard Recovery (< 5 minutes)

### Step 1: Stop All Processes
```bash
# Kill any running backend processes
pkill -f "python.*main.py"
pkill -f "uvicorn"
pkill -f "hisaabflow-backend"

# Kill any running frontend processes  
pkill -f "electron"
pkill -f "npm.*start"

# Clean up ports
sudo lsof -ti :8000 | xargs kill -9 2>/dev/null || true
sudo lsof -ti :3000 | xargs kill -9 2>/dev/null || true
```

### Step 2: Git Recovery
```bash
# Check current status
git status
git log --oneline -5

# Option A: Rollback to previous commit
git reset --hard HEAD~1

# Option B: Rollback to specific known good commit
git reset --hard <last_known_good_commit_sha>

# Option C: Rollback to main branch
git checkout main
git reset --hard origin/main
```

### Step 3: Clean Environment
```bash
# Clear any temporary files
rm -rf /tmp/hisaabflow_*
rm -rf backend/__pycache__
rm -rf backend/*/__pycache__

# Reset virtual environment if needed
cd backend
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cd ..
```

### Step 4: Verify Recovery
```bash
# Test backend startup
cd backend
source venv/bin/activate
python3 main.py &
cd ..

# Wait and test
sleep 5
curl -s http://127.0.0.1:8000/health

# Run integration tests
./test_api_coverage.sh
```

### Step 5: Restart Application
```bash
# Stop test backend
pkill -f "python.*main.py"

# Start full application
./start_app.sh
```

## 🔍 Recovery Verification Checklist

After recovery, verify these components work:

- [ ] Backend starts without errors: `curl http://127.0.0.1:8000/health`
- [ ] Configuration loading works: `curl http://127.0.0.1:8000/api/v1/configs`
- [ ] File upload works: Test with sample CSV
- [ ] Desktop app launches: `./start_app.sh`
- [ ] Complete integration test: `./test_all_integration.sh`

## 🎯 Common Recovery Scenarios

### Scenario 1: "Backend won't start"
**Symptoms**: `python main.py` fails, import errors
**Recovery**:
```bash
# 1. Check for import path issues
cd /path/to/HisaabFlow
source backend/venv/bin/activate
python3 backend/main.py  # Note: run from project root

# 2. If still failing, rollback
git reset --hard HEAD~1
```

### Scenario 2: "API endpoints return 500 errors"
**Symptoms**: Backend starts but API calls fail
**Recovery**:
```bash
# 1. Check recent config changes
git diff HEAD~1 configs/

# 2. Rollback config changes
git checkout HEAD~1 -- configs/

# 3. Restart backend
pkill -f "python.*main.py"
source backend/venv/bin/activate
python3 backend/main.py &
```

### Scenario 3: "Frontend can't connect to backend"
**Symptoms**: Frontend loads but can't communicate with backend
**Recovery**:
```bash
# 1. Check if backend is actually running
curl http://127.0.0.1:8000/health

# 2. If backend is up, check frontend URL configuration
grep -r "127.0.0.1:8000\|localhost:8000" frontend/src/

# 3. Rollback frontend changes
git checkout HEAD~1 -- frontend/src/
```

### Scenario 4: "Configuration system broken"
**Symptoms**: Config loading fails, bank detection doesn't work
**Recovery**:
```bash
# 1. Backup current configs
cp -r configs/ configs_backup/

# 2. Restore from git
git checkout HEAD~1 -- configs/

# 3. Test config loading
curl http://127.0.0.1:8000/api/v1/configs
```

### Scenario 5: "Desktop app won't launch"
**Symptoms**: Electron app crashes or won't start
**Recovery**:
```bash
# 1. Check if backend launcher is the issue
cd frontend
npm run electron-dev

# 2. Check for node_modules corruption
rm -rf node_modules package-lock.json
npm install

# 3. If still failing, rollback frontend
git checkout HEAD~1 -- frontend/
```

## 🛡️ Prevention Strategies

### Before Making Changes
1. **Always commit working state first**:
   ```bash
   git add .
   git commit -m "Working state before refactoring"
   ```

2. **Run full integration tests**:
   ```bash
   ./test_all_integration.sh
   ```

3. **Use feature branches**:
   ```bash
   git checkout -b feature/my-refactoring
   ```

### During Refactoring
1. **Use automated rollback**:
   ```bash
   ./test_all_integration.sh --rollback-on-failure
   ```

2. **Make small, incremental changes**
3. **Test after each logical change**
4. **Commit frequently with good messages**

### Emergency Contacts
- **Git Recovery**: All commands documented above
- **System Requirements**: Check `CLAUDE.md` for environment setup
- **Integration Tests**: Use `./test_all_integration.sh` for verification

## 📞 Last Resort: Complete Reset

If all else fails, complete project reset:

```bash
# 1. Backup any important changes
cp -r configs/ ~/backup_configs/
cp TASKS.md ~/backup_tasks.md

# 2. Reset to known good state
git checkout main
git reset --hard origin/main
git clean -fxd

# 3. Reinstall dependencies
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cd ../frontend
npm install
cd ..

# 4. Test system
./start_app.sh
```

---

**Recovery Time Targets:**
- ⚡ Quick Recovery: < 2 minutes
- 🔧 Standard Recovery: < 5 minutes  
- 📞 Complete Reset: < 15 minutes

**Remember**: It's better to rollback quickly and retry than to spend hours debugging a broken state!