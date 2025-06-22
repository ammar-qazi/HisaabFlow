const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');
const https = require('https');
const { createWriteStream, createReadStream } = require('fs');
const { pipeline } = require('stream');
const { promisify } = require('util');
const streamPipeline = promisify(pipeline);

class PythonBundlePreparator {
  constructor() {
    this.bundleDir = path.join(__dirname, '../python-bundle');
    this.platform = process.platform;
    this.arch = process.arch;
  }

  async preparePythonBundle() {
    console.log('🐍 Preparing Python runtime bundle...');
    
    try {
      // Clean previous bundle
      if (fs.existsSync(this.bundleDir)) {
        fs.rmSync(this.bundleDir, { recursive: true, force: true });
      }
      fs.mkdirSync(this.bundleDir, { recursive: true });

      // Download and setup Python for current platform
      await this.setupPython();
      
      // Install dependencies
      await this.installDependencies();
      
      console.log('✅ Python bundle prepared successfully');
      return true;
      
    } catch (error) {
      console.error('❌ Failed to prepare Python bundle:', error);
      return false;
    }
  }

  async setupPython() {
    if (this.platform === 'linux') {
      await this.setupLinuxPython();
    } else if (this.platform === 'win32') {
      await this.setupWindowsPython();
    } else if (this.platform === 'darwin') {
      await this.setupMacPython();
    }
  }

  async setupLinuxPython() {
    console.log('📦 Setting up Python for Linux...');
    
    // Use system Python to create a relocatable installation
    const pythonDir = path.join(this.bundleDir, 'python');
    fs.mkdirSync(pythonDir, { recursive: true });
    
    // Create a minimal Python installation using venv
    await this.runCommand('python3', ['-m', 'venv', '--copies', pythonDir]);
    
    // Verify installation
    const pythonBin = path.join(pythonDir, 'bin', 'python3');
    if (!fs.existsSync(pythonBin)) {
      throw new Error('Failed to create Python installation');
    }
    
    console.log('✅ Linux Python setup complete');
  }

  async setupWindowsPython() {
    console.log('📦 Setting up Python for Windows...');
    
    // Download Python embeddable zip
    const pythonVersion = '3.11.8';
    const archSuffix = this.arch === 'x64' ? 'amd64' : 'win32';
    const zipUrl = `https://www.python.org/ftp/python/${pythonVersion}/python-${pythonVersion}-embed-${archSuffix}.zip`;
    const zipPath = path.join(this.bundleDir, 'python-embed.zip');
    
    await this.downloadFile(zipUrl, zipPath);
    await this.extractZip(zipPath, path.join(this.bundleDir, 'python'));
    
    // Download and install pip
    await this.setupWindowsPip();
    
    console.log('✅ Windows Python setup complete');
  }

  async setupMacPython() {
    console.log('📦 Setting up Python for macOS...');
    
    // Use system Python to create a relocatable installation
    const pythonDir = path.join(this.bundleDir, 'python');
    fs.mkdirSync(pythonDir, { recursive: true });
    
    // Create a minimal Python installation using venv
    await this.runCommand('python3', ['-m', 'venv', '--copies', pythonDir]);
    
    console.log('✅ macOS Python setup complete');
  }

  async setupWindowsPip() {
    // Download get-pip.py
    const getPipUrl = 'https://bootstrap.pypa.io/get-pip.py';
    const getPipPath = path.join(this.bundleDir, 'get-pip.py');
    
    await this.downloadFile(getPipUrl, getPipPath);
    
    // Install pip
    const pythonExe = path.join(this.bundleDir, 'python', 'python.exe');
    await this.runCommand(pythonExe, [getPipPath]);
    
    // Clean up get-pip.py
    require('fs').unlinkSync(getPipPath);
    
    // Enable site-packages by creating/modifying pth file
    const pthContent = 'import site; site.main()';
    const pthPath = path.join(this.bundleDir, 'python', 'python312._pth');
    if (require('fs').existsSync(pthPath)) {
      let content = require('fs').readFileSync(pthPath, 'utf8');
      if (!content.includes('import site')) {
        content += '\nimport site';
        require('fs').writeFileSync(pthPath, content);
      }
    }
  }

  async installDependencies() {
    console.log('📦 Installing Python dependencies...');
    
    const requirementsPath = path.join(__dirname, '../../backend/requirements.txt');
    if (!fs.existsSync(requirementsPath)) {
      throw new Error('requirements.txt not found');
    }

    const pythonPath = this.getPythonExecutable();
    
    // Install dependencies
    await this.runCommand(pythonPath, [
      '-m', 'pip', 'install', '-r', requirementsPath,
      '--only-binary=:all:'  // Prefer binary wheels for faster installation
    ]);
    
    console.log('✅ Dependencies installed');
  }

  getPythonExecutable() {
    if (this.platform === 'win32') {
      return path.join(this.bundleDir, 'python', 'python.exe');
    } else {
      return path.join(this.bundleDir, 'python', 'bin', 'python3');
    }
  }

  async downloadFile(url, destPath) {
    console.log(`⬇️ Downloading ${url}...`);
    
    return new Promise((resolve, reject) => {
      const file = createWriteStream(destPath);
      
      https.get(url, (response) => {
        if (response.statusCode === 302 || response.statusCode === 301) {
          // Handle redirect
          return this.downloadFile(response.headers.location, destPath)
            .then(resolve)
            .catch(reject);
        }
        
        if (response.statusCode !== 200) {
          reject(new Error(`HTTP ${response.statusCode}: ${response.statusMessage}`));
          return;
        }
        
        streamPipeline(response, file)
          .then(resolve)
          .catch(reject);
      }).on('error', reject);
    });
  }

  async extractZip(zipPath, destDir) {
    // Simple zip extraction for Node.js
    const AdmZip = require('adm-zip');
    const zip = new AdmZip(zipPath);
    zip.extractAllTo(destDir, true);
    
    // Clean up zip file
    require('fs').unlinkSync(zipPath);
  }

  async runCommand(command, args, options = {}) {
    return new Promise((resolve, reject) => {
      console.log(`🔧 Running: ${command} ${args.join(' ')}`);
      
      const process = spawn(command, args, {
        stdio: 'pipe',
        ...options
      });

      let stdout = '';
      let stderr = '';

      process.stdout.on('data', (data) => {
        stdout += data.toString();
      });

      process.stderr.on('data', (data) => {
        stderr += data.toString();
      });

      process.on('close', (code) => {
        if (code === 0) {
          resolve({ stdout, stderr });
        } else {
          reject(new Error(`Command failed with code ${code}: ${stderr}`));
        }
      });

      process.on('error', reject);
    });
  }
}

// CLI usage
if (require.main === module) {
  const preparator = new PythonBundlePreparator();
  preparator.preparePythonBundle()
    .then(() => {
      console.log('🎉 Python bundle preparation complete!');
      process.exit(0);
    })
    .catch((error) => {
      console.error('💥 Bundle preparation failed:', error);
      process.exit(1);
    });
}

module.exports = PythonBundlePreparator;
