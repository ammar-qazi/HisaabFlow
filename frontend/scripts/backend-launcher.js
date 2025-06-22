const { spawn } = require('child_process');
const path = require('path');
const os = require('os');

class BackendLauncher {
  constructor() {
    this.backendProcess = null;
    this.isRunning = false;
    this.port = 8000;
  }

  async startBackend() {
    console.log('🚀 Starting HisaabFlow backend...');
    
    try {
      const backendPath = this.getBackendPath();
      
      // Ensure virtual environment exists and get Python path
      const pythonPath = await this.ensureVenv();
      
      console.log(`📂 Backend path: ${backendPath}`);
      console.log(`🐍 Python path: ${pythonPath}`);
      
      // Start FastAPI server using uvicorn
      this.backendProcess = spawn(pythonPath, [
        '-m', 'uvicorn',
        'main:app',
        '--host', '127.0.0.1',
        '--port', this.port.toString(),
        '--log-level', 'info'
      ], {
        cwd: backendPath,
        env: { ...process.env, PYTHONPATH: backendPath }
      });

      this.setupProcessHandlers();
      
      // Wait for backend to be ready
      await this.waitForBackend();
      this.isRunning = true;
      
      console.log('✅ Backend started successfully');
      return true;
      
    } catch (error) {
      console.error('❌ Failed to start backend:', error);
      return false;
    }
  }

  setupProcessHandlers() {
    this.backendProcess.stdout.on('data', (data) => {
      console.log(`🔧 Backend: ${data.toString().trim()}`);
    });

    this.backendProcess.stderr.on('data', (data) => {
      console.error(`⚠️ Backend error: ${data.toString().trim()}`);
    });

    this.backendProcess.on('close', (code) => {
      console.log(`🔄 Backend process exited with code ${code}`);
      this.isRunning = false;
    });
  }

  async waitForBackend(maxAttempts = 30) {
    const axios = require('axios');
    
    for (let i = 0; i < maxAttempts; i++) {
      try {
        await axios.get(`http://127.0.0.1:${this.port}/health`);
        return true;
      } catch (error) {
        console.log(`⏳ Waiting for backend... (${i + 1}/${maxAttempts})`);
        await new Promise(resolve => setTimeout(resolve, 1000));
      }
    }
    throw new Error('Backend failed to start within timeout');
  }

  getBackendPath() {
    const isDev = require('electron-is-dev');
    
    if (isDev) {
      // Development: backend folder in project root
      return path.join(__dirname, '../../backend');
    } else {
      // Production: backend in extraResources
      return path.join(process.resourcesPath, 'backend');
    }
  }

  getVenvPath() {
    return path.join(os.homedir(), '.hisaabflow', 'venv');
  }

  getVenvPython() {
    const venvPath = this.getVenvPath();
    return process.platform === 'win32' 
      ? path.join(venvPath, 'Scripts', 'python.exe')
      : path.join(venvPath, 'bin', 'python3');
  }

  async ensureVenv() {
    const venvPath = this.getVenvPath();
    
    if (!require('fs').existsSync(venvPath)) {
      console.log('📦 Creating HisaabFlow virtual environment...');
      await this.createVenv();
      console.log('📦 Installing dependencies...');
      await this.installDependencies();
    }
    
    return this.getVenvPython();
  }

  async createVenv() {
    const venvPath = this.getVenvPath();
    
    return new Promise((resolve, reject) => {
      const create = spawn('python3', ['-m', 'venv', venvPath], { stdio: 'pipe' });
      
      create.on('close', (code) => {
        if (code === 0) {
          console.log('✅ Virtual environment created');
          resolve();
        } else {
          reject(new Error('Failed to create virtual environment'));
        }
      });
    });
  }

  async installDependencies() {
    const venvPython = this.getVenvPython();
    
    return new Promise((resolve, reject) => {
      const install = spawn(venvPython, ['-m', 'pip', 'install', 
        'fastapi', 'uvicorn', 'pydantic', 'python-multipart',
        '--only-binary=pandas', 'pandas'
      ], { stdio: 'pipe' });
      
      install.on('close', (code) => {
        if (code === 0) {
          console.log('✅ Dependencies installed successfully');
          resolve();
        } else {
          console.warn('⚠️ Some dependencies failed, trying core only...');
          this.installCoreDependencies().then(resolve).catch(reject);
        }
      });
    });
  }

  async installCoreDependencies() {
    const venvPython = this.getVenvPython();
    
    return new Promise((resolve, reject) => {
      const install = spawn(venvPython, ['-m', 'pip', 'install', 
        'fastapi', 'uvicorn', 'pydantic', 'python-multipart'
      ], { stdio: 'pipe' });
      
      install.on('close', (code) => {
        if (code === 0) {
          console.log('✅ Core dependencies installed');
          resolve();
        } else {
          reject(new Error('Failed to install core dependencies'));
        }
      });
    });
  }

  getPythonPath() {
    const isDev = require('electron-is-dev');
    
    if (isDev) {
      // Development: try virtual environment first, then system Python
      const backendPath = this.getBackendPath();
      const venvPath = path.join(backendPath, 'venv');
      
      if (process.platform === 'win32') {
        const venvPython = path.join(venvPath, 'Scripts', 'python.exe');
        if (require('fs').existsSync(venvPython)) {
          return venvPython;
        }
        return 'python';
      } else {
        const venvPython = path.join(venvPath, 'bin', 'python3');
        if (require('fs').existsSync(venvPython)) {
          return venvPython;
        }
        return 'python3';
      }
    } else {
      // Production: use system Python (user must have Python + deps installed)
      return process.platform === 'win32' ? 'python' : 'python3';
    }
  }

  stopBackend() {
    if (this.backendProcess && this.isRunning) {
      console.log('🛑 Stopping backend...');
      this.backendProcess.kill();
      this.isRunning = false;
    }
  }

  getBackendUrl() {
    return `http://127.0.0.1:${this.port}`;
  }
}

module.exports = BackendLauncher;
