const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');
const https = require('https');
const { createWriteStream } = require('fs');
const { pipeline } = require('stream');
const { promisify } = require('util');
const streamPipeline = promisify(pipeline);

class PythonBundlePreparator {
  constructor() {
    this.bundleDir = path.join(__dirname, '../python-bundle');
    this.platform = process.platform;
    this.arch = process.arch;
    
    // python-build-standalone download URLs
    this.pythonVersion = '3.11.9';  // Latest stable 3.11.x
    this.buildVersion = '20240415'; // python-build-standalone release date
  }

  async preparePythonBundle() {
    console.log(' Preparing Python runtime bundle with python-build-standalone...');
    
    try {
      // Clean previous bundle
      if (fs.existsSync(this.bundleDir)) {
        fs.rmSync(this.bundleDir, { recursive: true, force: true });
      }
      fs.mkdirSync(this.bundleDir, { recursive: true });

      // Download and setup portable Python for current platform
      await this.downloadPortablePython();
      
      // Install dependencies
      await this.installDependencies();
      
      console.log('[SUCCESS] Python bundle prepared successfully');
      return true;
      
    } catch (error) {
      console.error('[ERROR]  Failed to prepare Python bundle:', error);
      return false;
    }
  }

  async downloadPortablePython() {
    console.log(` Downloading portable Python for ${this.platform}-${this.arch}...`);
    
    const downloadUrl = this.getPythonDownloadUrl();
    const fileName = path.basename(new URL(downloadUrl).pathname);
    const downloadPath = path.join(this.bundleDir, fileName);
    
    console.log(`⬇ Downloading: ${downloadUrl}`);
    await this.downloadFile(downloadUrl, downloadPath);
    
    console.log(' Extracting Python bundle...');
    await this.extractPythonBundle(downloadPath);
    
    // Clean up download file
    fs.unlinkSync(downloadPath);
    
    console.log('[SUCCESS] Portable Python setup complete');
  }

  getPythonDownloadUrl() {
    const baseUrl = `https://github.com/indygreg/python-build-standalone/releases/download/${this.buildVersion}`;
    
    // Map platform/arch to python-build-standalone naming
    let platformName, archName;
    
    switch (this.platform) {
      case 'win32':
        platformName = 'pc-windows-msvc-shared';
        archName = this.arch === 'x64' ? 'x86_64' : 'i686';
        break;
      case 'linux':
        platformName = 'unknown-linux-gnu';
        archName = this.arch === 'x64' ? 'x86_64' : this.arch === 'arm64' ? 'aarch64' : 'i686';
        break;
      case 'darwin':
        platformName = 'apple-darwin';
        archName = this.arch === 'arm64' ? 'aarch64' : 'x86_64';
        break;
      default:
        throw new Error(`Unsupported platform: ${this.platform}`);
    }
    
    const fileName = `cpython-${this.pythonVersion}+${this.buildVersion}-${archName}-${platformName}-install_only.tar.gz`;
    return `${baseUrl}/${fileName}`;
  }

  async extractPythonBundle(tarPath) {
    const extractDir = path.join(this.bundleDir, 'python');
    fs.mkdirSync(extractDir, { recursive: true });
    
    if (this.platform === 'win32') {
      // Use tar command (available in Windows 10+)
      await this.runCommand('tar', ['-xzf', tarPath, '-C', extractDir, '--strip-components=1']);
    } else {
      // Use tar command on Unix systems
      await this.runCommand('tar', ['-xzf', tarPath, '-C', extractDir, '--strip-components=1']);
    }
  }

  async installDependencies() {
    console.log(' Installing Python dependencies...');
    
    const requirementsPath = path.join(__dirname, '../../backend/requirements.txt');
    if (!fs.existsSync(requirementsPath)) {
      throw new Error('requirements.txt not found');
    }

    const pythonPath = this.getPythonExecutable();
    
    // Verify Python works
    console.log('🧪 Testing portable Python...');
    const testResult = await this.runCommand(pythonPath, ['--version']);
    console.log(`[SUCCESS] Python test: ${testResult.stdout.trim()}`);
    
    // Install pip if not present (shouldn't be needed with python-build-standalone)
    try {
      await this.runCommand(pythonPath, ['-m', 'pip', '--version']);
      console.log('[SUCCESS] pip is available');
    } catch (error) {
      console.log(' Installing pip...');
      await this.installPip(pythonPath);
    }
    
    // Install dependencies
    console.log(' Installing backend dependencies...');
    await this.runCommand(pythonPath, [
      '-m', 'pip', 'install', '-r', requirementsPath,
      '--only-binary=:all:',  // Prefer binary wheels
      '--no-cache-dir'        // Don't cache in portable environment
    ]);
    
    console.log('[SUCCESS] Dependencies installed');
  }

  async installPip(pythonPath) {
    // Download get-pip.py
    const getPipUrl = 'https://bootstrap.pypa.io/get-pip.py';
    const getPipPath = path.join(this.bundleDir, 'get-pip.py');
    
    await this.downloadFile(getPipUrl, getPipPath);
    await this.runCommand(pythonPath, [getPipPath]);
    
    // Clean up
    fs.unlinkSync(getPipPath);
    console.log('[SUCCESS] pip installed');
  }

  getPythonExecutable() {
    const pythonDir = path.join(this.bundleDir, 'python');
    
    if (this.platform === 'win32') {
      return path.join(pythonDir, 'python.exe');
    } else {
      return path.join(pythonDir, 'bin', 'python3');
    }
  }

  async downloadFile(url, destPath) {
    console.log(`⬇ Downloading ${path.basename(destPath)}...`);
    
    return new Promise((resolve, reject) => {
      const file = createWriteStream(destPath);
      
      const request = https.get(url, (response) => {
        if (response.statusCode === 302 || response.statusCode === 301) {
          // Handle redirect
          file.close();
          fs.unlinkSync(destPath);
          return this.downloadFile(response.headers.location, destPath)
            .then(resolve)
            .catch(reject);
        }
        
        if (response.statusCode !== 200) {
          file.close();
          fs.unlinkSync(destPath);
          reject(new Error(`HTTP ${response.statusCode}: ${response.statusMessage}`));
          return;
        }
        
        const totalSize = parseInt(response.headers['content-length'], 10);
        let downloadedSize = 0;
        
        response.on('data', (chunk) => {
          downloadedSize += chunk.length;
          if (totalSize) {
            const percent = Math.round((downloadedSize / totalSize) * 100);
            process.stdout.write(`\r[DATA] Progress: ${percent}% (${Math.round(downloadedSize / 1024 / 1024)}MB)`);
          }
        });
        
        streamPipeline(response, file)
          .then(() => {
            if (totalSize) process.stdout.write('\n');
            resolve();
          })
          .catch(reject);
      });
      
      request.on('error', (error) => {
        file.close();
        fs.unlinkSync(destPath);
        reject(error);
      });
    });
  }

  async runCommand(command, args, options = {}) {
    return new Promise((resolve, reject) => {
      console.log(` Running: ${command} ${args.join(' ')}`);
      
      const process = spawn(command, args, {
        stdio: 'pipe',
        ...options
      });

      let stdout = '';
      let stderr = '';

      if (process.stdout) {
        process.stdout.on('data', (data) => {
          stdout += data.toString();
        });
      }

      if (process.stderr) {
        process.stderr.on('data', (data) => {
          stderr += data.toString();
        });
      }

      process.on('close', (code) => {
        if (code === 0) {
          resolve({ stdout, stderr });
        } else {
          reject(new Error(`Command failed with code ${code}: ${stderr || stdout}`));
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
      console.log(' Python bundle preparation complete!');
      process.exit(0);
    })
    .catch((error) => {
      console.error(' Bundle preparation failed:', error);
      process.exit(1);
    });
}

module.exports = PythonBundlePreparator;
