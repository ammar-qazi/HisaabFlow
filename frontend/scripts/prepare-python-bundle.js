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
    
    const pythonDir = path.join(this.bundleDir, 'python');
    fs.mkdirSync(pythonDir, { recursive: true });
    
    // First create a venv with copies (not symlinks)
    console.log('🔧 Creating Python virtual environment...');
    await this.runCommand('python3', ['-m', 'venv', '--copies', pythonDir]);
    
    // Now make it truly self-contained by copying shared libraries
    await this.makePythonSelfContained(pythonDir);
    
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
    
    const pythonDir = path.join(this.bundleDir, 'python');
    fs.mkdirSync(pythonDir, { recursive: true });
    
    // Create a minimal Python installation using venv
    console.log('🔧 Creating Python virtual environment...');
    await this.runCommand('python3', ['-m', 'venv', '--copies', pythonDir]);
    
    // Make it self-contained for macOS
    await this.makeMacPythonSelfContained(pythonDir);
    
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

  async makePythonSelfContained(pythonDir) {
    console.log('🔗 Making Python self-contained with shared libraries...');
    
    const pythonBin = path.join(pythonDir, 'bin', 'python3');
    const libDir = path.join(pythonDir, 'lib');
    
    try {
      // Find Python shared library dependencies using ldd
      console.log('🔍 Analyzing Python dependencies...');
      const { stdout } = await this.runCommand('ldd', [pythonBin]);
      
      // Parse ldd output to find libpython and other essential libraries
      const dependencies = this.parseLddOutput(stdout);
      console.log(`🔍 Found ${dependencies.length} dependencies`);
      
      // Copy essential shared libraries to bundle
      for (const dep of dependencies) {
        if (this.isEssentialLibrary(dep.name)) {
          const destPath = path.join(libDir, dep.name);
          console.log(`📋 Copying ${dep.name} from ${dep.path}`);
          
          // Create lib directory if it doesn't exist
          if (!fs.existsSync(libDir)) {
            fs.mkdirSync(libDir, { recursive: true });
          }
          
          // Copy the library
          fs.copyFileSync(dep.path, destPath);
          
          // Make it executable
          fs.chmodSync(destPath, 0o755);
        }
      }
      
      // Update Python binary to look in bundle lib directory
      await this.setPythonRPath(pythonBin, libDir);
      
      console.log('✅ Python made self-contained');
      
    } catch (error) {
      console.warn('⚠️ Failed to make Python fully self-contained:', error.message);
      console.warn('⚠️ Python may work if target system has compatible libraries');
    }
  }

  async makeMacPythonSelfContained(pythonDir) {
    console.log('🔗 Making macOS Python self-contained...');
    
    const pythonBin = path.join(pythonDir, 'bin', 'python3');
    const libDir = path.join(pythonDir, 'lib');
    
    try {
      // Find Python shared library dependencies using otool (macOS equivalent of ldd)
      console.log('🔍 Analyzing Python dependencies...');
      const { stdout } = await this.runCommand('otool', ['-L', pythonBin]);
      
      // Parse otool output to find Python framework and libraries
      const dependencies = this.parseOtoolOutput(stdout);
      console.log(`🔍 Found ${dependencies.length} dependencies`);
      
      // Copy essential shared libraries/frameworks to bundle
      for (const dep of dependencies) {
        if (this.isMacEssentialLibrary(dep.path)) {
          const libName = path.basename(dep.path);
          const destPath = path.join(libDir, libName);
          console.log(`📋 Copying ${libName} from ${dep.path}`);
          
          // Create lib directory if it doesn't exist
          if (!fs.existsSync(libDir)) {
            fs.mkdirSync(libDir, { recursive: true });
          }
          
          // Copy the library
          if (fs.existsSync(dep.path)) {
            fs.copyFileSync(dep.path, destPath);
            fs.chmodSync(destPath, 0o755);
          }
        }
      }
      
      // Update Python binary to look in bundle lib directory using install_name_tool
      await this.setMacPythonRPath(pythonBin, libDir);
      
      console.log('✅ macOS Python made self-contained');
      
    } catch (error) {
      console.warn('⚠️ Failed to make macOS Python fully self-contained:', error.message);
      console.warn('⚠️ Python may work if target system has compatible libraries');
    }
  }

  parseOtoolOutput(otoolOutput) {
    const dependencies = [];
    const lines = otoolOutput.split('\n');
    
    for (const line of lines) {
      const trimmed = line.trim();
      if (!trimmed || trimmed.includes('is not an object file')) continue;
      
      // Parse lines like: /usr/lib/libpython3.11.dylib (compatibility version...)
      const match = trimmed.match(/^\s*([^\s]+)\s+\(/);
      if (match) {
        dependencies.push({
          path: match[1]
        });
      }
    }
    
    return dependencies;
  }

  isMacEssentialLibrary(libPath) {
    // Only copy Python-specific libraries and essential runtime libraries
    const essentialPatterns = [
      '/Python.framework',     // Python framework
      'libpython',            // Python runtime
      'libssl',               // SSL support
      'libcrypto'             // Crypto support
    ];
    
    return essentialPatterns.some(pattern => libPath.includes(pattern));
  }

  async setMacPythonRPath(pythonBin, libDir) {
    try {
      console.log('🔧 Setting install_name for macOS Python executable...');
      
      // Use install_name_tool to set library search paths
      await this.runCommand('install_name_tool', ['-add_rpath', '@executable_path/../lib', pythonBin]);
      
      console.log('✅ macOS RPATH set successfully');
    } catch (error) {
      console.warn('⚠️ Could not set RPATH on macOS:', error.message);
      console.warn('⚠️ Creating DYLD_LIBRARY_PATH wrapper instead...');
      await this.createMacPythonWrapper(pythonBin, libDir);
    }
  }

  async createMacPythonWrapper(pythonBin, libDir) {
    // Create a wrapper script that sets DYLD_LIBRARY_PATH
    const wrapperPath = pythonBin + '_real';
    const wrapperScript = `#!/bin/bash
export DYLD_LIBRARY_PATH="${libDir}:\${DYLD_LIBRARY_PATH}"
exec "${wrapperPath}" "$@"
`;
    
    // Rename original python to python_real
    fs.renameSync(pythonBin, wrapperPath);
    
    // Create wrapper script
    fs.writeFileSync(pythonBin, wrapperScript);
    fs.chmodSync(pythonBin, 0o755);
    
    console.log('✅ Created DYLD_LIBRARY_PATH wrapper script');
  }

  parseLddOutput(lddOutput) {
    const dependencies = [];
    const lines = lddOutput.split('\n');
    
    for (const line of lines) {
      const trimmed = line.trim();
      if (!trimmed || trimmed.includes('not a dynamic executable')) continue;
      
      // Parse lines like: libpython3.11.so.1.0 => /usr/lib/x86_64-linux-gnu/libpython3.11.so.1.0 (0x...)
      const match = trimmed.match(/([^\s]+)\s*=>\s*([^\s]+)/);
      if (match) {
        dependencies.push({
          name: match[1],
          path: match[2]
        });
      }
    }
    
    return dependencies;
  }

  isEssentialLibrary(libName) {
    // Only copy Python-specific libraries and essential runtime libraries
    const essentialPrefixes = [
      'libpython',          // Python runtime
      'libssl',             // SSL support (needed for pip/https)
      'libcrypto',          // Crypto support
    ];
    
    return essentialPrefixes.some(prefix => libName.startsWith(prefix));
  }

  async setPythonRPath(pythonBin, libDir) {
    try {
      console.log('🔧 Setting RPATH for Python executable...');
      
      // Use patchelf to set RPATH so Python looks in bundle lib directory
      await this.runCommand('patchelf', ['--set-rpath', `$ORIGIN/../lib:${libDir}`, pythonBin]);
      
      console.log('✅ RPATH set successfully');
    } catch (error) {
      console.warn('⚠️ patchelf not available, trying chrpath...');
      
      try {
        // Fallback to chrpath
        await this.runCommand('chrpath', ['-r', `$ORIGIN/../lib:${libDir}`, pythonBin]);
        console.log('✅ RPATH set with chrpath');
      } catch (error2) {
        console.warn('⚠️ Could not set RPATH (patchelf/chrpath not available)');
        console.warn('⚠️ Creating LD_LIBRARY_PATH wrapper instead...');
        await this.createPythonWrapper(pythonBin, libDir);
      }
    }
  }

  async createPythonWrapper(pythonBin, libDir) {
    // Create a wrapper script that sets LD_LIBRARY_PATH
    const wrapperPath = pythonBin + '_real';
    const wrapperScript = `#!/bin/bash
export LD_LIBRARY_PATH="${libDir}:\${LD_LIBRARY_PATH}"
exec "${wrapperPath}" "$@"
`;
    
    // Rename original python to python_real
    fs.renameSync(pythonBin, wrapperPath);
    
    // Create wrapper script
    fs.writeFileSync(pythonBin, wrapperScript);
    fs.chmodSync(pythonBin, 0o755);
    
    console.log('✅ Created LD_LIBRARY_PATH wrapper script');
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
