#!/usr/bin/env python3
"""
Bank Statement Parser - GUI Launcher
A simple graphical interface to start and manage the application
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import subprocess
import threading
import os
import sys
import time
import webbrowser
import signal
from pathlib import Path

class BankParserLauncher:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🏦 Bank Statement Parser")
        self.root.geometry("600x500")
        self.root.resizable(True, True)
        
        # Process tracking
        self.backend_process = None
        self.frontend_process = None
        self.is_running = False
        
        # Get script directory
        self.script_dir = Path(__file__).parent.absolute()
        
        self.setup_style()
        self.setup_ui()
        
    def setup_style(self):
        """Setup modern UI styling"""
        style = ttk.Style()
        
        # Configure colors
        self.colors = {
            'primary': '#2196F3',
            'success': '#4CAF50', 
            'warning': '#FF9800',
            'danger': '#F44336',
            'dark': '#212121',
            'light': '#F5F5F5'
        }
        
        # Configure button styles
        style.configure('Start.TButton', foreground='white', background=self.colors['success'])
        style.configure('Stop.TButton', foreground='white', background=self.colors['danger'])
        style.configure('Open.TButton', foreground='white', background=self.colors['primary'])
        
    def setup_ui(self):
        """Create the user interface"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="🏦 Bank Statement Parser", 
                               font=('Arial', 18, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Status frame
        status_frame = ttk.LabelFrame(main_frame, text="Application Status", padding="10")
        status_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        status_frame.columnconfigure(1, weight=1)
        
        # Status indicators
        ttk.Label(status_frame, text="Backend:").grid(row=0, column=0, sticky=tk.W)
        self.backend_status = ttk.Label(status_frame, text="●", foreground=self.colors['danger'])
        self.backend_status.grid(row=0, column=1, sticky=tk.W)
        
        ttk.Label(status_frame, text="Frontend:").grid(row=1, column=0, sticky=tk.W)
        self.frontend_status = ttk.Label(status_frame, text="●", foreground=self.colors['danger'])
        self.frontend_status.grid(row=1, column=1, sticky=tk.W)
        
        # Control buttons frame
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.grid(row=2, column=0, columnspan=3, pady=10)
        
        # Control buttons
        self.start_button = ttk.Button(buttons_frame, text="🚀 Start Application", 
                                      command=self.start_application, style='Start.TButton')
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = ttk.Button(buttons_frame, text="🛑 Stop Application", 
                                     command=self.stop_application, style='Stop.TButton', 
                                     state='disabled')
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        self.open_button = ttk.Button(buttons_frame, text="🌐 Open in Browser", 
                                     command=self.open_browser, style='Open.TButton',
                                     state='disabled')
        self.open_button.pack(side=tk.LEFT, padx=5)
        
        # Quick links frame
        links_frame = ttk.LabelFrame(main_frame, text="Quick Links", padding="10")
        links_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        links_text = "• Frontend Application: http://localhost:3000\n"
        links_text += "• Backend API: http://127.0.0.1:8000\n"
        links_text += "• API Documentation: http://127.0.0.1:8000/docs"
        
        ttk.Label(links_frame, text=links_text, justify=tk.LEFT).pack(anchor=tk.W)
        
        # Log frame
        log_frame = ttk.LabelFrame(main_frame, text="Application Log", padding="10")
        log_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(4, weight=1)
        
        # Log text area
        self.log_text = scrolledtext.ScrolledText(log_frame, height=10, width=70)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Initial log message
        self.log("🏦 Bank Statement Parser Launcher Ready")
        self.log("📁 Working directory: " + str(self.script_dir))
        
    def log(self, message):
        """Add message to log with timestamp"""
        timestamp = time.strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}\n"
        self.log_text.insert(tk.END, log_message)
        self.log_text.see(tk.END)
        self.root.update()
        
    def check_requirements(self):
        """Check if all requirements are met"""
        issues = []
        
        # Check Python
        try:
            result = subprocess.run([sys.executable, '--version'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                self.log(f"✅ Python: {result.stdout.strip()}")
            else:
                issues.append("Python not found")
        except Exception:
            issues.append("Python not accessible")
            
        # Check Node.js
        try:
            result = subprocess.run(['node', '--version'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                self.log(f"✅ Node.js: {result.stdout.strip()}")
            else:
                issues.append("Node.js not found")
        except Exception:
            issues.append("Node.js not found")
            
        # Check directories
        backend_dir = self.script_dir / 'backend'
        frontend_dir = self.script_dir / 'frontend'
        
        if not backend_dir.exists():
            issues.append("Backend directory not found")
        else:
            self.log("✅ Backend directory found")
            
        if not frontend_dir.exists():
            issues.append("Frontend directory not found")
        else:
            self.log("✅ Frontend directory found")
            
        return issues
        
    def start_application(self):
        """Start both backend and frontend"""
        if self.is_running:
            return
            
        self.log("🔍 Checking requirements...")
        issues = self.check_requirements()
        
        if issues:
            error_msg = "❌ Requirements not met:\n" + "\n".join(f"• {issue}" for issue in issues)
            self.log(error_msg)
            messagebox.showerror("Requirements Error", error_msg)
            return
            
        self.log("🚀 Starting application...")
        self.start_button.config(state='disabled')
        
        # Start in separate thread to avoid blocking UI
        threading.Thread(target=self._start_services, daemon=True).start()
        
    def _start_services(self):
        """Start backend and frontend services"""
        try:
            # Start backend
            self.log("🔧 Starting backend server...")
            backend_dir = self.script_dir / 'backend'
            
            # Activate venv and start backend
            if os.name == 'nt':  # Windows
                venv_python = backend_dir / 'venv' / 'Scripts' / 'python.exe'
            else:  # Linux/Mac
                venv_python = backend_dir / 'venv' / 'bin' / 'python'
                
            if not venv_python.exists():
                self.log("❌ Virtual environment not found!")
                self.log("   Please run: python3 -m venv venv in backend directory")
                return
                
            self.backend_process = subprocess.Popen(
                [str(venv_python), 'main.py'],
                cwd=backend_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )
            
            # Wait for backend to start
            time.sleep(3)
            if self.backend_process.poll() is None:
                self.log("✅ Backend started successfully")
                self.backend_status.config(text="● Running", foreground=self.colors['success'])
            else:
                self.log("❌ Backend failed to start")
                return
                
            # Start frontend
            self.log("🎨 Starting frontend application...")
            frontend_dir = self.script_dir / 'frontend'
            
            # Check for npm or yarn
            npm_cmd = 'npm'
            try:
                subprocess.run([npm_cmd, '--version'], capture_output=True, check=True)
            except (subprocess.CalledProcessError, FileNotFoundError):
                try:
                    npm_cmd = 'yarn'
                    subprocess.run([npm_cmd, '--version'], capture_output=True, check=True)
                except (subprocess.CalledProcessError, FileNotFoundError):
                    self.log("❌ Neither npm nor yarn found!")
                    return
                    
            self.frontend_process = subprocess.Popen(
                [npm_cmd, 'start'],
                cwd=frontend_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )
            
            # Wait for frontend to start
            time.sleep(5)
            if self.frontend_process.poll() is None:
                self.log("✅ Frontend started successfully")
                self.frontend_status.config(text="● Running", foreground=self.colors['success'])
                
                # Enable buttons
                self.root.after(0, self._enable_running_buttons)
                
                # Auto-open browser
                time.sleep(2)
                self.root.after(0, self.open_browser)
                
            else:
                self.log("❌ Frontend failed to start")
                self.stop_application()
                
        except Exception as e:
            self.log(f"❌ Error starting application: {e}")
            self.stop_application()
            
    def _enable_running_buttons(self):
        """Enable buttons when application is running"""
        self.is_running = True
        self.stop_button.config(state='normal')
        self.open_button.config(state='normal')
        
    def stop_application(self):
        """Stop both backend and frontend"""
        self.log("🛑 Stopping application...")
        
        if self.backend_process:
            self.backend_process.terminate()
            self.backend_process = None
            self.backend_status.config(text="● Stopped", foreground=self.colors['danger'])
            
        if self.frontend_process:
            self.frontend_process.terminate()
            self.frontend_process = None
            self.frontend_status.config(text="● Stopped", foreground=self.colors['danger'])
            
        self.is_running = False
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')
        self.open_button.config(state='disabled')
        
        self.log("✅ Application stopped")
        
    def open_browser(self):
        """Open the application in browser"""
        self.log("🌐 Opening application in browser...")
        webbrowser.open('http://localhost:3000')
        
    def on_closing(self):
        """Handle window close event"""
        if self.is_running:
            if messagebox.askokcancel("Quit", "Stop the application and quit?"):
                self.stop_application()
                self.root.destroy()
        else:
            self.root.destroy()
            
    def run(self):
        """Start the GUI application"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()

if __name__ == "__main__":
    app = BankParserLauncher()
    app.run()
