# Puppeteer Integration Guide

## Why Puppeteer Might Be Needed
- **Web Scraping**: Download bank statements directly from bank websites
- **PDF Processing**: Convert online statements to processable formats
- **Authentication**: Handle bank login flows automatically
- **Dynamic Content**: Extract data from JavaScript-heavy banking portals

## Implementation Requirements

### 1. Node.js Setup
```bash
# Install Node.js if not present
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Verify installation
node --version
npm --version
```

### 2. Puppeteer Installation
```bash
# In your project root
npm init -y
npm install puppeteer

# For system Chrome usage
npm install puppeteer-core
```

### 3. System Dependencies
```bash
# Required for headless Chrome
sudo apt-get update
sudo apt-get install -y \
    gconf-service libasound2 libatk1.0-0 libcairo2 libcups2 \
    libfontconfig1 libgdk-pixbuf2.0-0 libgtk-3-0 libnspr4 \
    libpango-1.0-0 libxrandr2 libxss1 libxtst6 ca-certificates \
    fonts-liberation libappindicator1 libnss3 lsb-release \
    xdg-utils wget chromium-browser
```

### 4. Integration with Python Backend

#### Option A: Node.js Service
Create a separate Node.js service that Python calls:

```javascript
// puppeteer_service.js
const puppeteer = require('puppeteer');
const express = require('express');
const app = express();

app.use(express.json());

app.post('/scrape-bank', async (req, res) => {
    const { bankUrl, credentials } = req.body;
    
    const browser = await puppeteer.launch({
        headless: true,
        args: ['--no-sandbox', '--disable-setuid-sandbox']
    });
    
    try {
        const page = await browser.newPage();
        await page.goto(bankUrl);
        
        // Bank-specific scraping logic here
        const statements = await page.evaluate(() => {
            // Extract statement data
        });
        
        res.json({ success: true, data: statements });
    } catch (error) {
        res.json({ success: false, error: error.message });
    } finally {
        await browser.close();
    }
});

app.listen(3001, () => console.log('Puppeteer service running on port 3001'));
```

#### Option B: Python Subprocess
```python
# backend/scrapers/puppeteer_wrapper.py
import subprocess
import json
import tempfile
import os

class PuppeteerScraper:
    def __init__(self):
        self.script_path = os.path.join(os.path.dirname(__file__), 'scraper.js')
    
    def scrape_bank_statements(self, bank_url, credentials):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({'url': bank_url, 'credentials': credentials}, f)
            config_file = f.name
        
        try:
            result = subprocess.run([
                'node', self.script_path, config_file
            ], capture_output=True, text=True, timeout=120)
            
            if result.returncode == 0:
                return json.loads(result.stdout)
            else:
                raise Exception(f"Puppeteer error: {result.stderr}")
        finally:
            os.unlink(config_file)
```

### 5. Project Structure Updates
```
bank_statement_parser/
├── backend/
│   ├── scrapers/          # NEW: Web scraping modules
│   │   ├── __init__.py
│   │   ├── puppeteer_wrapper.py
│   │   ├── bank_scrapers/
│   │   │   ├── nayapay_scraper.js
│   │   │   └── wise_scraper.js
│   │   └── scraper_base.js
├── frontend/
├── node_modules/          # NEW: Node.js dependencies
├── package.json           # NEW: Node.js project config
└── puppeteer_service.js   # NEW: Puppeteer service
```

### 6. Configuration Updates

Add to your backend configuration:
```python
# configs/scraper_config.py
PUPPETEER_CONFIG = {
    'headless': True,
    'timeout': 30000,
    'viewport': {'width': 1920, 'height': 1080},
    'user_agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
    'service_url': 'http://localhost:3001'
}

BANK_SCRAPERS = {
    'nayapay': {
        'login_url': 'https://nayapay.com/login',
        'statements_url': 'https://nayapay.com/statements',
        'selectors': {
            'username': '#username',
            'password': '#password',
            'login_button': '.login-btn',
            'download_link': '.download-csv'
        }
    },
    'wise': {
        'login_url': 'https://wise.com/login',
        'statements_url': 'https://wise.com/statements',
        '