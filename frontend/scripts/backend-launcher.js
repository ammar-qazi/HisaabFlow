const { spawn } = require('child_process');
const path = require('path');
const os = require('os');

class BackendLauncher {
  constructor(userDir = null) {
    this.backendProcess = null;
    this.isRunning = false;
    this.port = 8000;
    this.userDir = userDir;
  }

  getBackendExecutable() {
    const isDev = require('electron-is-dev');
    
    if (isDev) {
      // Development: still use Python approach for easier debugging
      return null;
    } else {
      // Production: use compiled executable for ALL platforms
      const execName = process.platform === 'win32' 
        ? 'hisaabflow-backend.exe' 
        : 'hisaabflow-backend';
      return path.join(process.resourcesPath, execName);
    }
  }

  async startCompiledBackend(exePath) {
    console.log('Using compiled backend executable');
    console.log(` Executable path: ${exePath}`);
    
    try {
      // Set up environment with user configs directory and UTF-8 support
      const env = { ...process.env };
      
      // Force UTF-8 encoding for cross-platform compatibility
      env.PYTHONUTF8 = '1';
      env.PYTHONIOENCODING = 'utf-8';
      
      if (this.userDir) {
        env.HISAABFLOW_USER_DIR = this.userDir;
        env.HISAABFLOW_CONFIG_DIR = path.join(this.userDir, 'configs');
        console.log(` Using user configs: ${env.HISAABFLOW_CONFIG_DIR}`);
      }
      
      // Start the compiled executable
      this.backendProcess = spawn(exePath, [], {
        env: env,
        stdio: 'pipe'
      });

      this.setupProcessHandlers();
      
      // Wait for backend to be ready
      await this.waitForBackend();
      this.isRunning = true;
      
      console.log('[SUCCESS] Compiled backend started successfully');
      return true;
      
    } catch (error) {
      console.error('[ERROR]  Failed to start compiled backend:', error);
      return false;
    }
  }

  async startBackend() {
    console.log('[START] Starting HisaabFlow backend...');
    console.log(' DEBUG: Platform:', process.platform);
    console.log(' DEBUG: resourcesPath:', process.resourcesPath);
    console.log(' DEBUG: __dirname:', __dirname);
    
    // Check for compiled executable first (ALL platforms in production)
    const backendExe = this.getBackendExecutable();
    
    if (backendExe && require('fs').existsSync(backendExe)) {
      return this.startCompiledBackend(backendExe);
    } else {
      // Fall back to Python approach (development only)
      return this.startPythonBackend();
    }
  }

  async startPythonBackend() {
    console.log(' Using Python backend approach (development mode)');
    
    try {
      const backendPath = this.getBackendPath();
      console.log(` Backend path: ${backendPath}`);
      console.log(` Backend exists: ${require('fs').existsSync(backendPath)}`);
      
      if (require('fs').existsSync(backendPath)) {
        const backendFiles = require('fs').readdirSync(backendPath);
        console.log(` Backend files: ${backendFiles.join(', ')}`);
      }
      
      // Ensure virtual environment exists and get Python path
      const pythonPath = await this.ensureVenv();
      console.log(` Python path: ${pythonPath}`);
      console.log(` Python exists: ${require('fs').existsSync(pythonPath)}`);
      
      // Test Python execution
      console.log('🧪 Testing Python execution...');
      const testResult = await this.testPython(pythonPath);
      console.log(`🧪 Python test result: ${testResult}`);
      
      // Start FastAPI server using uvicorn
      // Set up environment with user configs directory and UTF-8 support
      const env = { 
        ...process.env, 
        PYTHONPATH: backendPath,
        // Force UTF-8 encoding for cross-platform compatibility
        PYTHONUTF8: '1',
        PYTHONIOENCODING: 'utf-8'
      };
      
      if (this.userDir) {
        env.HISAABFLOW_USER_DIR = this.userDir;
        env.HISAABFLOW_CONFIG_DIR = path.join(this.userDir, 'configs');
        console.log(` Using user configs: ${env.HISAABFLOW_CONFIG_DIR}`);
      }
      
      this.backendProcess = spawn(pythonPath, [
        '-m', 'uvicorn',
        'main:app',
        '--host', '127.0.0.1',
        '--port', this.port.toString(),
        '--log-level', 'info'
      ], {
        cwd: backendPath,
        env: env
      });

      this.setupProcessHandlers();
      
      // Wait for backend to be ready
      await this.waitForBackend();
      this.isRunning = true;
      
      console.log('[SUCCESS] Python backend started successfully');
      return true;
      
    } catch (error) {
      console.error('[ERROR]  Failed to start Python backend:', error);
      return false;
    }
  }

  setupProcessHandlers() {
    this.backendProcess.stdout.on('data', (data) => {
      console.log(` Backend: ${data.toString().trim()}`);
    });

    this.backendProcess.stderr.on('data', (data) => {
      console.error(`[WARNING] Backend error: ${data.toString().trim()}`);
    });

    this.backendProcess.on('close', (code) => {
      console.log(` Backend process exited with code ${code}`);
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
      // Production: backend in extraResources (fallback for development)
      return path.join(process.resourcesPath, 'backend');
    }
  }

  getBundledPythonPath() {
    const isDev = require('electron-is-dev');
    console.log(` isDev: ${isDev}`);
    
    if (isDev) {
      // Development: check for local python bundle first
      const localBundle = path.join(__dirname, '../python-bundle/python');
      if (require('fs').existsSync(localBundle)) {
        const pythonExe = process.platform === 'win32' 
          ? path.join(localBundle, 'python.exe')
          : path.join(localBundle, 'bin', 'python3');
        console.log(` Dev bundle Python: ${pythonExe}`);
        return pythonExe;
      }
      return null; // Fall back to system Python in development
    } else {
      // Production: use bundled python-build-standalone Python (not used with Nuitka)
      const bundlePath = path.join(process.resourcesPath, 'python-bundle/python');
      console.log(` Production bundle path: ${bundlePath}`);
      
      const pythonExe = process.platform === 'win32' 
        ? path.join(bundlePath, 'python.exe')
        : path.join(bundlePath, 'bin', 'python3');
      console.log(` Production Python executable: ${pythonExe}`);
      return pythonExe;
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
    // First check if we have bundled Python
    const bundledPython = this.getBundledPythonPath();
    console.log(` Bundled Python path: ${bundledPython}`);
    
    if (bundledPython && require('fs').existsSync(bundledPython)) {
      console.log('[SUCCESS] Using bundled Python runtime');
      return bundledPython;
    } else {
      console.log(`[WARNING] Bundled Python not found at: ${bundledPython}`);
      if (bundledPython) {
        const bundleDir = require('path').dirname(bundledPython);
        console.log(` Bundle directory exists: ${require('fs').existsSync(bundleDir)}`);
        if (require('fs').existsSync(bundleDir)) {
          const bundleFiles = require('fs').readdirSync(bundleDir);
          console.log(` Files in bundle dir: ${bundleFiles.join(', ')}`);
        }
      }
    }
    
    // Fall back to virtual environment approach (for development)
    console.log('[WARNING] Bundled Python not found, using virtual environment...');
    const venvPath = this.getVenvPath();
    
    if (!require('fs').existsSync(venvPath)) {
      console.log(' Creating HisaabFlow virtual environment...');
      await this.createVenv();
      console.log(' Installing dependencies...');
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
          console.log('[SUCCESS] Virtual environment created');
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
          console.log('[SUCCESS] Dependencies installed successfully');
          resolve();
        } else {
          console.warn('[WARNING] Some dependencies failed, trying core only...');
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
          console.log('[SUCCESS] Core dependencies installed');
          resolve();
        } else {
          reject(new Error('Failed to install core dependencies'));
        }
      });
    });
  }

  stopBackend() {
    if (this.backendProcess && this.isRunning) {
      console.log(' Stopping backend...');
      
      try {
        // Try graceful shutdown first
        this.backendProcess.kill('SIGTERM');
        
        // Force kill after timeout
        setTimeout(() => {
          if (this.backendProcess && this.isRunning) {
            console.log(' Force killing backend process...');
            this.backendProcess.kill('SIGKILL');
          }
        }, 3000); // 3 second timeout
        
      } catch (error) {
        console.error('[WARNING] Error stopping backend:', error.message);
      }
      
      this.isRunning = false;
      console.log('[SUCCESS] Backend shutdown initiated');
    }
  }

  async testPython(pythonPath) {
    try {
      const { spawn } = require('child_process');
      return new Promise((resolve) => {
        const test = spawn(pythonPath, ['--version'], { stdio: 'pipe' });
        let output = '';
        
        test.stdout.on('data', (data) => {
          output += data.toString();
        });
        
        test.stderr.on('data', (data) => {
          output += data.toString();
        });
        
        test.on('close', (code) => {
          resolve(`Exit code: ${code}, Output: ${output.trim()}`);
        });
        
        test.on('error', (error) => {
          resolve(`Error: ${error.message}`);
        });
      });
    } catch (error) {
      return `Exception: ${error.message}`;
    }
  }

  getBackendUrl() {
    return `http://127.0.0.1:${this.port}`;
  }
}

module.exports = BackendLauncher;