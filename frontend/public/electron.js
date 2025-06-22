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
    console.log('📁 Created user directory:', userDir);
  }
  
  if (!fs.existsSync(configsDir)) {
    fs.mkdirSync(configsDir, { recursive: true });
    console.log('📁 Created configs directory:', configsDir);
  }
  
  if (!fs.existsSync(sampleDataDir)) {
    fs.mkdirSync(sampleDataDir, { recursive: true });
    console.log('📁 Created sample_data directory:', sampleDataDir);
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
        console.log('📋 Copied config:', configFile);
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
        console.log('📄 Copied sample data:', sampleFile);
      }
    }
  }
  
  // Create README for user
  const readmePath = path.join(userDir, 'README.md');
  if (!fs.existsSync(readmePath)) {
    const readmeContent = `# HisaabFlow User Directory

Welcome to your HisaabFlow configuration directory!

## 📁 Directory Structure

- **configs/**: Bank configuration files (.conf)
- **sample_data/**: Sample CSV files for testing

## 🔧 Customizing Configurations

Edit the .conf files in the configs/ directory to customize:
- Bank detection patterns
- Column mappings  
- Categorization rules
- Data cleaning settings

## 📄 Sample Data

Use the sample CSV files to test the application with different bank formats.

## 🚀 Getting Started

1. Place your bank CSV files anywhere
2. Open HisaabFlow
3. Upload and parse your statements
4. Customize configs as needed

Your modifications will be preserved across app updates.
`;
    fs.writeFileSync(readmePath, readmeContent);
    console.log('📚 Created user README');
  }
  
  return userDir;
}

async function createWindow() {
  // Setup user directory first
  const userDir = await setupUserDirectory();
  
  // Initialize backend launcher with user directory
  backendLauncher = new BackendLauncher(userDir);
  
  // Start backend before creating window
  console.log('🔄 Initializing HisaabFlow...');
  const backendStarted = await backendLauncher.startBackend();
  
  if (!backendStarted) {
    console.error('❌ Failed to start backend - app may not work correctly');
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

  mainWindow.on('closed', () => {
    console.log('🪟 Main window closed');
    mainWindow = null;
  });
  
  // Handle window close event to ensure clean shutdown
  mainWindow.on('close', (event) => {
    console.log('🔄 Window closing, ensuring backend cleanup...');
    
    if (backendLauncher && backendLauncher.isRunning) {
      console.log('🛑 Stopping backend before window close...');
      backendLauncher.stopBackend();
    }
  });
  
  // Provide backend URL to frontend
  mainWindow.webContents.on('dom-ready', () => {
    mainWindow.webContents.executeJavaScript(`
      window.BACKEND_URL = '${backendLauncher.getBackendUrl()}';
      console.log('🔗 Backend URL configured:', window.BACKEND_URL);
    `);
  });
}

app.on('ready', createWindow);

app.on('window-all-closed', () => {
  console.log('🔄 All windows closed, cleaning up...');
  
  // Stop backend when app closes
  if (backendLauncher) {
    console.log('🛑 Stopping backend process...');
    backendLauncher.stopBackend();
  }
  
  if (process.platform !== 'darwin') {
    console.log('🚪 Quitting application...');
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
process.on('SIGINT', () => {
  console.log('🔄 Received SIGINT, cleaning up...');
  cleanup();
});

process.on('SIGTERM', () => {
  console.log('🔄 Received SIGTERM, cleaning up...');
  cleanup();
});

process.on('exit', () => {
  console.log('🔄 Process exiting, final cleanup...');
  cleanup();
});

function cleanup() {
  if (backendLauncher && backendLauncher.isRunning) {
    console.log('🛑 Final backend cleanup...');
    backendLauncher.stopBackend();
  }
}