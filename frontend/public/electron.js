const { app, BrowserWindow, dialog, ipcMain } = require('electron');
const path = require('path');
const fs = require('fs');
const os = require('os');
const isDev = require('electron-is-dev');
const BackendLauncher = require('../scripts/backend-launcher');

let mainWindow;
let backendLauncher;

// Setup user directory with configs and sample data
async function setupUserDirectory() {
  const userDir = path.join(os.homedir(), 'HisaabFlow');
  const configsDir = path.join(userDir, 'configs');
  const sampleDataDir = path.join(userDir, 'sample_data');
  
  // Create directories if they don't exist
  if (!fs.existsSync(userDir)) {
    fs.mkdirSync(userDir, { recursive: true });
    console.log(' Created user directory:', userDir);
  }
  
  if (!fs.existsSync(configsDir)) {
    fs.mkdirSync(configsDir, { recursive: true });
    console.log(' Created configs directory:', configsDir);
  }
  
  if (!fs.existsSync(sampleDataDir)) {
    fs.mkdirSync(sampleDataDir, { recursive: true });
    console.log(' Created sample_data directory:', sampleDataDir);
  }
  
  // Copy configs from app bundle (first run only - preserve user modifications)
  const appConfigsPath = isDev 
    ? path.join(__dirname, '../../configs')
    : path.join(process.resourcesPath, 'configs');
    
  if (fs.existsSync(appConfigsPath)) {
    const configFiles = fs.readdirSync(appConfigsPath).filter(f => f.endsWith('.conf'));
    for (const configFile of configFiles) {
      const sourcePath = path.join(appConfigsPath, configFile);
      const destPath = path.join(configsDir, configFile);
      
      // Only copy if user doesn't already have this config (preserve modifications)
      if (!fs.existsSync(destPath)) {
        fs.copyFileSync(sourcePath, destPath);
        console.log(' Copied config:', configFile);
      }
    }
  }
  
  // Copy sample data from app bundle (first run only)
  const appSampleDataPath = isDev 
    ? path.join(__dirname, '../../sample_data')
    : path.join(process.resourcesPath, 'sample_data');
    
  if (fs.existsSync(appSampleDataPath)) {
    const sampleFiles = fs.readdirSync(appSampleDataPath);
    for (const sampleFile of sampleFiles) {
      const sourcePath = path.join(appSampleDataPath, sampleFile);
      const destPath = path.join(sampleDataDir, sampleFile);
      
      // Only copy if file doesn't exist (preserve user modifications)
      if (!fs.existsSync(destPath) && fs.statSync(sourcePath).isFile()) {
        fs.copyFileSync(sourcePath, destPath);
        console.log(' Copied sample data:', sampleFile);
      }
    }
  }
  
  // Create README for user
  const readmePath = path.join(userDir, 'README.md');
  if (!fs.existsSync(readmePath)) {
    const readmeContent = `# HisaabFlow User Directory

Welcome to your HisaabFlow configuration directory!

##  Directory Structure

- **configs/**: Bank configuration files (.conf)
- **sample_data/**: Sample CSV files for testing

##  Customizing Configurations

Edit the .conf files in the configs/ directory to customize:
- Bank detection patterns
- Column mappings  
- Categorization rules
- Data cleaning settings

##  Sample Data

Use the sample CSV files to test the application with different bank formats.

## [START] Getting Started

1. Place your bank CSV files anywhere
2. Open HisaabFlow
3. Upload and parse your statements
4. Customize configs as needed

Your modifications will be preserved across app updates.
`;
    fs.writeFileSync(readmePath, readmeContent);
    console.log(' Created user README');
  }
  
  return userDir;
}

async function createWindow() {
  // Setup user directory first
  const userDir = await setupUserDirectory();
  
  // Initialize backend launcher with user directory
  backendLauncher = new BackendLauncher(userDir);
  
  // Start backend before creating window
  console.log(' Initializing HisaabFlow...');
  const backendStarted = await backendLauncher.startBackend();
  
  if (!backendStarted) {
    console.error('[ERROR]  Failed to start backend - app may not work correctly');
  }

  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    title: 'HisaabFlow',
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
      enableRemoteModule: true
    }
  });

  mainWindow.loadURL(
    isDev
      ? 'http://localhost:3000'
      : `file://${path.join(__dirname, '../build/index.html')}`
  );

  if (isDev) {
    mainWindow.webContents.openDevTools();
  }

  // Track if we're in shutdown process
  let isShuttingDown = false;
  
  mainWindow.on('closed', () => {
    console.log('🪟 Main window closed');
    mainWindow = null;
  });
  
  // Handle window close event to ensure clean shutdown
  mainWindow.on('close', async (event) => {
    if (isShuttingDown) {
      console.log('[CLEANUP] Already shutting down, allowing close');
      return; // Allow the close to proceed
    }
    
    console.log('[CLEANUP] Window closing, ensuring backend cleanup...');
    
    if (backendLauncher && backendLauncher.isBackendRunning()) {
      // Prevent window from closing immediately
      event.preventDefault();
      isShuttingDown = true;
      
      console.log('[CLEANUP] Stopping backend before window close...');
      try {
        await backendLauncher.stopBackend();
        console.log('[CLEANUP] Backend stopped successfully, closing window');
      } catch (error) {
        console.error('[WARNING] Backend shutdown error:', error);
      }
      
      // Now actually close the window
      isShuttingDown = false;
      mainWindow.close(); // Use close() instead of destroy() to trigger normal close flow
    }
  });
  
  // Provide backend URL to frontend
  mainWindow.webContents.on('dom-ready', () => {
    mainWindow.webContents.executeJavaScript(`
      window.BACKEND_URL = '${backendLauncher.getBackendUrl()}';
      console.log(' Backend URL configured:', window.BACKEND_URL);
    `);
  });
}

app.on('ready', createWindow);

app.on('window-all-closed', async () => {
  console.log('[CLEANUP] All windows closed, cleaning up...');
  
  // Stop backend when app closes
  if (backendLauncher && backendLauncher.isBackendRunning()) {
    console.log('[CLEANUP] Stopping backend process...');
    try {
      await backendLauncher.stopBackend();
      console.log('[SUCCESS] Backend cleanup completed');
    } catch (error) {
      console.error('[WARNING] Backend cleanup error:', error);
      // Force emergency cleanup if normal shutdown failed
      if (backendLauncher.emergencyCleanup) {
        try {
          await backendLauncher.emergencyCleanup();
          console.log('[SUCCESS] Emergency cleanup completed');
        } catch (emergencyError) {
          console.error('[ERROR] Emergency cleanup failed:', emergencyError);
        }
      }
    }
  }
  
  if (process.platform !== 'darwin') {
    console.log('[CLEANUP] Quitting application...');
    app.quit();
  }
});

app.on('activate', () => {
  if (mainWindow === null) {
    createWindow();
  }
});

// Handle file dialog
ipcMain.handle('show-open-dialog', async () => {
  const result = await dialog.showOpenDialog(mainWindow, {
    properties: ['openFile'],
    filters: [
      { name: 'CSV Files', extensions: ['csv'] },
      { name: 'All Files', extensions: ['*'] }
    ]
  });
  return result;
});

// Handle save dialog
ipcMain.handle('show-save-dialog', async (event, options) => {
  const result = await dialog.showSaveDialog(mainWindow, options);
  return result;
});

// Process cleanup handlers for proper shutdown
process.on('SIGINT', async () => {
  console.log('[SIGNAL] Received SIGINT, cleaning up...');
  await cleanup();
  process.exit(0);
});

process.on('SIGTERM', async () => {
  console.log('[SIGNAL] Received SIGTERM, cleaning up...');
  await cleanup();
  process.exit(0);
});

// Note: 'exit' event cannot be async, so we use app lifecycle events instead
process.on('beforeExit', async () => {
  console.log('[SIGNAL] Process before exit, final cleanup...');
  await cleanup();
});

async function cleanup() {
  if (backendLauncher && backendLauncher.isRunning) {
    console.log('[CLEANUP] Final backend cleanup...');
    try {
      await backendLauncher.stopBackend();
      console.log('[SUCCESS] Final cleanup completed');
    } catch (error) {
      console.error('[WARNING] Final cleanup error:', error);
      
      // Emergency cleanup only if normal shutdown failed
      console.log('[EMERGENCY] Attempting emergency process cleanup...');
      
      // Use the launcher's emergency cleanup method first
      if (backendLauncher.emergencyCleanup) {
        try {
          await backendLauncher.emergencyCleanup();
          console.log('[SUCCESS] Emergency cleanup via launcher completed');
          return; // Exit early if successful
        } catch (emergencyError) {
          console.error('[WARNING] Launcher emergency cleanup failed:', emergencyError);
        }
      }
      
      if (process.platform === 'win32') {
        // Windows: Try to kill by process name as last resort
        const { spawn } = require('child_process');
        try {
          console.log('[EMERGENCY] Windows: Killing hisaabflow-backend.exe processes...');
          const killBackend = spawn('taskkill', ['/f', '/im', 'hisaabflow-backend.exe'], { 
            stdio: 'ignore',
            detached: true 
          });
          
          killBackend.on('close', (code) => {
            console.log(`[EMERGENCY] taskkill hisaabflow-backend exit code: ${code}`);
          });
          
          // Also kill any Python processes running uvicorn
          console.log('[EMERGENCY] Windows: Killing Python uvicorn processes...');
          const killPython = spawn('wmic', [
            'process', 'where', 
            'name="python.exe" and commandline like "%uvicorn%" and commandline like "%main:app%"', 
            'delete'
          ], { 
            stdio: 'ignore',
            detached: true 
          });
          
          killPython.on('close', (code) => {
            console.log(`[EMERGENCY] wmic Python cleanup exit code: ${code}`);
          });
          
        } catch (emergencyError) {
          console.error('[WARNING] Emergency cleanup failed:', emergencyError.message);
        }
      } else {
        // Unix: Kill process group containing our backend processes
        const { spawn } = require('child_process');
        try {
          spawn('pkill', ['-f', 'hisaabflow-backend'], { stdio: 'ignore' });
          spawn('pkill', ['-f', 'uvicorn.*main:app'], { stdio: 'ignore' });
        } catch (emergencyError) {
          console.error('[WARNING] Emergency cleanup failed:', emergencyError.message);
        }
      }
    }
  }
}