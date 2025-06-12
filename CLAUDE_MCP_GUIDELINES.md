# Claude MCP Tool Usage Guidelines for Bank Statement Parser

## ✅ PUPPETEER MCP SETUP & USAGE

### **Puppeteer MCP Status: ✅ WORKING (Including Localhost)**

**Setup Complete**: Virtual display (Xvfb) + Firefox successfully configured  
**Environment**: DISPLAY=:99 with Xvfb running  
**Browser**: Firefox 139.0.1 in headless mode  

### **Required Parameters for Puppeteer MCP:**
```javascript
// Always use these parameters for Puppeteer MCP calls:
{
  "allowDangerous": true,
  "launchOptions": {
    "headless": true,
    "args": ["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"]
  }
}
```

### **✅ LOCALHOST TESTING NOW ENABLED!**

**Benefits of Localhost Puppeteer Testing:**
- 🎯 **Visual Debugging**: See exactly what's happening in the frontend
- 🔍 **End-to-End Testing**: Test complete upload → processing → display workflow  
- 🐛 **UI Bug Detection**: Spot frontend issues not visible in logs
- 🔗 **Integration Testing**: Verify frontend-backend communication visually
- 👤 **User Experience**: See how the actual UI behaves during processing

### **Your App URLs (Safe for Testing):**
- ✅ **Frontend**: http://localhost:3000 (React + Electron)
- ✅ **Backend API**: http://127.0.0.1:8000 (FastAPI endpoints)
- ✅ **Backend Docs**: http://127.0.0.1:8000/docs (API documentation)

### **Best Practices for Localhost Testing:**

#### **1. Development Server Safety:**
```bash
# Before Puppeteer testing, ensure servers are stable:
./start_backend.sh &    # Start backend first
./start_frontend.sh &   # Then frontend
sleep 10               # Wait for startup

# Test endpoints are responsive:
curl http://127.0.0.1:8000/health
curl http://localhost:3000
```

#### **2. Strategic Testing Approach:**
- **Use for visual verification**, not primary debugging
- **Test critical user flows**: Upload → Preview → Process → Export
- **Verify UI state changes** during processing
- **Check error handling** displays properly
- **Monitor progress indicators** and loading states

#### **3. Cleanup After Testing:**
```bash
# If browser processes interfere with development:
pkill -f "puppeteer\|chrome\|firefox.*headless"

# Restart development servers if needed:
./restart_backend.sh
```

### **Specific Testing Use Cases:**

#### **File Upload Flow Testing:**
- Navigate to frontend, upload CSV files
- Verify bank detection displays correctly  
- Check preview shows proper column mapping
- Monitor processing progress indicators

#### **Multi-Bank Processing:**
- Upload multiple bank CSV files
- Verify each bank detected correctly in UI
- Check combined processing results display
- Test export functionality

#### **Error Handling Verification:**
- Upload invalid files, see error messages
- Test network errors during processing
- Verify user feedback for failed operations

### **External Website Automation:**
- ✅ **Bank Portal Automation**: Login and download statements from bank websites
- ✅ **External Website Testing**: Test public websites and capture screenshots  
- ✅ **Web Scraping**: Extract data from bank portals and financial sites
- ✅ **Form Automation**: Fill out external web forms automatically
- ✅ **Screenshot Documentation**: Capture web interfaces for documentation

## ✅ PREFERRED ALTERNATIVES FOR VALIDATION

### **Instead of Puppeteer MCP, Use:**

#### **1. Direct File System Operations**
```bash
# Check if frontend is running
curl -f http://localhost:3000 > /dev/null 2>&1 && echo "Frontend running" || echo "Frontend not running"

# Test backend endpoints
curl -X POST http://localhost:8000/api/parse -H "Content-Type: application/json" -d '{"test": "data"}'
```

#### **2. Log File Analysis**
```python
# Add to project code for debugging
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Instead of browser testing, add comprehensive logging
logger.debug(f"Processing bank: {bank_name}")
logger.debug(f"Row count: {len(transactions)}")
logger.debug(f"Sample transaction: {transactions[0] if transactions else 'None'}")
```

#### **3. JSON Response Validation**
```python
# Test API responses directly
import requests
import json

def test_parse_endpoint():
    with open('sample_data/test.csv', 'rb') as f:
        response = requests.post('http://localhost:8000/api/parse', 
                               files={'file': f})
    print(json.dumps(response.json(), indent=2))
```

#### **4. File System Verification**
```python
# Verify file processing results
def verify_processing_results():
    output_dir = "/path/to/output"
    files = os.listdir(output_dir)
    for file in files:
        print(f"Generated: {file} - Size: {os.path.getsize(os.path.join(output_dir, file))} bytes")
```

## 🛠️ LOCAL DEVELOPMENT SETUP DOCUMENTATION

### **Current Project Ports (For Claude's Reference):**
- **Backend**: http://localhost:8000 (FastAPI/Flask)
- **Frontend**: http://localhost:3000 (React/Vue development server)
- **Database**: localhost:5432 (PostgreSQL) or localhost:27017 (MongoDB)

### **Critical Files in Active Development:**
- `/backend/api/parse_endpoints.py` - Main API endpoints
- `/frontend/src/components/` - React components
- `/configs/*.conf` - Bank configuration files
- `/memory/project_status.md` - Project state tracking

### **Development Processes to Avoid Interfering With:**
- **File Watching**: Frontend development server file watchers
- **Hot Reloading**: Backend auto-restart on file changes
- **Database Connections**: Active DB connections during development
- **Log File Writing**: Continuous logging to debug files

## 🔧 DEBUGGING ALTERNATIVES

### **Instead of Browser Automation, Use:**

#### **1. Enhanced Logging**
```python
# Add debugging prints directly in code
print(f"DEBUG: Bank detected as {bank_name} with confidence {confidence}")
print(f"DEBUG: Processing {len(rows)} rows starting from row {start_row}")
print(f"DEBUG: Column mapping: {column_mapping}")
```

#### **2. Temporary Debug Endpoints**
```python
# Add temporary debug routes to backend
@app.route('/debug/bank-detection', methods=['POST'])
def debug_bank_detection():
    # Return detailed detection results
    pass

@app.route('/debug/parsing-state', methods=['GET'])
def debug_parsing_state():
    # Return current parsing state
    pass
```

#### **3. File-Based Testing**
```python
# Create test output files instead of browser testing
def create_debug_output(data, filename):
    debug_dir = "debug_outputs"
    os.makedirs(debug_dir, exist_ok=True)
    with open(f"{debug_dir}/{filename}", 'w') as f:
        json.dump(data, f, indent=2)
```

#### **4. Command Line Validation**
```bash
# Test backend functionality via command line
python -c "
from backend.bank_detection.bank_detector import BankDetector
detector = BankDetector()
result = detector.detect_bank('sample_data/nayapay_feb.csv')
print(f'Bank: {result.bank_name}, Confidence: {result.confidence}')
"
```

## 📋 WHEN TO USE OTHER MCP TOOLS

### **Safe MCP Tools for This Project:**
- ✅ **File Operations**: read_file, write_file, edit_file, list_directory
- ✅ **Code Search**: search_files, search_code
- ✅ **Shell Commands**: execute_command (for system operations)
- ✅ **Web Search**: For documentation and troubleshooting (external sites only)

### **MCP Tools to Avoid:**
- 🚫 **Puppeteer Tools**: puppeteer_navigate, puppeteer_screenshot, puppeteer_click, etc.
- 🚫 **Web Fetch**: For localhost URLs (use curl or requests instead)

## 🧹 CLEANUP PROCEDURES

### **If Puppeteer Processes Are Running:**
```bash
# Kill any stuck browser processes
pkill -f chromium
pkill -f chrome
pkill -f "node.*puppeteer"

# Check for stuck processes
ps aux | grep -E "(chromium|chrome|puppeteer)"

# Free up any locked files
lsof | grep chrome
```

### **Reset Development Environment:**
```bash
# Restart development servers
./restart_backend.sh
./start_frontend.sh

# Clear any temporary files
rm -rf /tmp/chrome_*
rm -rf /tmp/puppeteer_*
```

## 🎯 PROJECT-SPECIFIC INSTRUCTIONS FOR CLAUDE

### **For Bank Statement Parser Development:**
1. **Never use Puppeteer MCP** - Use file operations and direct API testing instead
2. **Focus on backend logic** - Test bank detection and parsing through file operations
3. **Use logging extensively** - Add debug prints instead of browser inspection
4. **Test with sample files** - Use existing CSV files in `/sample_data/` directory
5. **Verify through file outputs** - Check generated files rather than UI testing

### **For Frontend Issues:**
1. **Check log files** first: `frontend.log`, `backend.log`
2. **Use API testing** via curl or direct Python requests
3. **Examine file outputs** in debug directories
4. **Never automate the browser** - Work with the running development server via APIs

### **Emergency Recovery:**
If browser processes are interfering:
1. Kill all browser processes: `pkill -f chrome`
2. Restart development servers: `./restart_backend.sh`
3. Clear temporary files: `rm -rf /tmp/chrome_*`
4. Continue with file-based debugging only

---

**Summary**: Avoid Puppeteer MCP entirely for local development. Use file operations, logging, and direct API testing instead. This prevents resource conflicts and ensures smooth development workflow.
