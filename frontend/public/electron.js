const { app, BrowserWindow, dialog, ipcMain } = require('electron');
const path = require('path');
const isDev = require('electron-is-dev');
const BackendLauncher = require('../scripts/backend-launcher');

let mainWindow;
let backendLauncher;

async function createWindow() {
  // Initialize backend launcher
  backendLauncher = new BackendLauncher();
  
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
    mainWindow = null;
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
  // Stop backend when app closes
  if (backendLauncher) {
    backendLauncher.stopBackend();
  }
  
  if (process.platform !== 'darwin') {
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