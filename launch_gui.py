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
        self.script_dir = Path(__file__).parent.absolute()
        
        self.setup_style()
        self.setup_ui()
        
    def setup_style(self):
        """Setup modern UI styling"""
        style = ttk.Style()
        
        # Configure colors
        self.colors = {
            'primary': '#2196F3', 'success': '#4CAF50', 'warning': '#FF9800',
            'danger': '#F44336', 'dark': '#212121', 'light': '#F5F5F5'
        }
        
        # Configure button styles
        style.configure('Start.TButton', foreground='white', background=self.colors['success'])
        style.configure('Stop.TButton', foreground='white', background=self.colors['danger'])
        style.configure('Open.TButton', foreground='white', background=self.colors['primary'])
        
    def setup_ui(self):
        """Create the user interface"""
        main_frame = self._create_main_frame()
        self._create_title_section(main_frame)
        self._create_status_section(main_frame)
        self._create_control_buttons(main_frame)
        self._create_links_section(main_frame)
        self._create_log_section(main_frame)
        self._log_initial_messages()
        
    def _create_main_frame(self):
        """Create and configure the main frame"""
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        return main_frame
        
    def _create_title_section(self, parent):
        """Create the title section"""
        title_label = ttk.Label(parent, text="🏦 Bank Statement Parser", 
                               font=('Arial', 18, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
    def _create_status_section(self, parent):
        """Create the status indicators section"""
        status_frame = ttk.LabelFrame(parent, text="Application Status", padding="10")
        status_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        status_frame.columnconfigure(1, weight=1)
        
        for i, (name, attr) in enumerate([("Backend:", "backend_status"), ("Frontend:", "frontend_status")]):
            ttk.Label(status_frame, text=name).grid(row=i, column=0, sticky=tk.W)
            status_label = ttk.Label(status_frame, text="●", foreground=self.colors['danger'])
            status_label.grid(row=i, column=1, sticky=tk.W)
            setattr(self, attr, status_label)
        
    def _create_control_buttons(self, parent):
        """Create the control buttons section"""
        buttons_frame = ttk.Frame(parent)
        buttons_frame.grid(row=2, column=0, columnspan=3, pady=10)
        
        buttons = [
            ("🚀 Start Application", self.start_application, 'Start.TButton', 'start_button', 'normal'),
            ("🛑 Stop Application", self.stop_application, 'Stop.TButton', 'stop_button', 'disabled'),
            ("🌐 Open in Browser", self.open_browser, 'Open.TButton', 'open_button', 'disabled')
        ]
        
        for text, command, style, attr, state in buttons:
            button = ttk.Button(buttons_frame, text=text, command=command, style=style, state=state)
            button.pack(side=tk.LEFT, padx=5)
            setattr(self, attr, button)
        
    def _create_links_section(self, parent):
        """Create the quick links section"""
        links_frame = ttk.LabelFrame(parent, text="Quick Links", padding="10")
        links_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        links_text = ("• Frontend Application: http://localhost:3000\n"
                     "• Backend API: http://127.0.0.1:8000\n"
                     "• API Documentation: http://127.0.0.1:8000/docs")
        ttk.Label(links_frame, text=links_text, justify=tk.LEFT).pack(anchor=tk.W)
        
    def _create_log_section(self, parent):
        """Create the log section"""
        log_frame = ttk.LabelFrame(parent, text="Application Log", padding="10")
        log_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        parent.rowconfigure(4, weight=1)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=10, width=70)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
    def _log_initial_messages(self):
        """Log initial startup messages"""
        self.log("🏦 Bank Statement Parser Launcher Ready")
        self.log("📁 Working directory: " + str(self.script_dir))
        
    def log(self, message):
        """Add message to log with timestamp"""
        timestamp = time.strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.root.update()
        
    def check_requirements(self):
        """Check if all requirements are met"""
        issues = []
        
        # Check system requirements
        for name, command in [("Python", [sys.executable, '--version']), 
                              ("Node.js", ['node', '--version'])]:
            try:
                result = subprocess.run(command, capture_output=True, text=True)
                if result.returncode == 0:
                    self.log(f"✅ {name}: {result.stdout.strip()}")
                else:
                    issues.append(f"{name} not found")
            except Exception:
                issues.append(f"{name} not accessible" if name == "Python" else f"{name} not found")
            
        # Check directories
        for name, path in [("Backend", self.script_dir / 'backend'), 
                          ("Frontend", self.script_dir / 'frontend')]:
            if path.exists():
                self.log(f"✅ {name} directory found")
            else:
                issues.append(f"{name} directory not found")
            
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
        threading.Thread(target=self._start_services, daemon=True).start()
        
    def _start_services(self):
        """Start backend and frontend services"""
        try:
            if self._start_backend() and self._start_frontend():
                self._finalize_startup()
            else:
                self.stop_application()
        except Exception as e:
            self.log(f"❌ Error starting application: {e}")
            self.stop_application()
            
    def _start_backend(self):
        """Start the backend service"""
        self.log("🔧 Starting backend server...")
        venv_python = self._get_venv_python(self.script_dir / 'backend')
        if not venv_python:
            return False
            
        self.backend_process = subprocess.Popen(
            [str(venv_python), 'main.py'], cwd=self.script_dir / 'backend',
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
        )
        
        time.sleep(3)
        success = self.backend_process.poll() is None
        self.log("✅ Backend started successfully" if success else "❌ Backend failed to start")
        if success:
            self._update_status("backend", "success")
        return success
    
    def _start_frontend(self):
        """Start the frontend service"""
        self.log("🎨 Starting frontend application...")
        npm_cmd = self._get_npm_command()
        if not npm_cmd:
            return False
            
        self.frontend_process = subprocess.Popen(
            [npm_cmd, 'start'], cwd=self.script_dir / 'frontend',
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
        )
        
        time.sleep(5)
        success = self.frontend_process.poll() is None
        self.log("✅ Frontend started successfully" if success else "❌ Frontend failed to start")
        if success:
            self._update_status("frontend", "success")
        return success
    
    def _get_venv_python(self, backend_dir):
        """Get the virtual environment Python executable path"""
        venv_python = (backend_dir / 'venv' / 'Scripts' / 'python.exe' if os.name == 'nt' 
                      else backend_dir / 'venv' / 'bin' / 'python')
            
        if not venv_python.exists():
            self.log("❌ Virtual environment not found!")
            self.log("   Please run: python3 -m venv venv in backend directory")
            return None
        return venv_python
    
    def _get_npm_command(self):
        """Get available npm command (npm or yarn)"""
        for cmd in ['npm', 'yarn']:
            try:
                subprocess.run([cmd, '--version'], capture_output=True, check=True)
                return cmd
            except (subprocess.CalledProcessError, FileNotFoundError):
                continue
        self.log("❌ Neither npm nor yarn found!")
        return None
    
    def _update_status(self, service, status):
        """Update service status indicator"""
        color = self.colors['success'] if status == 'success' else self.colors['danger']
        text = "● Running" if status == 'success' else "● Stopped"
        getattr(self, f"{service}_status").config(text=text, foreground=color)
    
    def _finalize_startup(self):
        """Finalize startup: enable buttons and open browser"""
        self.is_running = True
        self.stop_button.config(state='normal')
        self.open_button.config(state='normal')
        self.root.after(2000, self.open_browser)  # Auto-open browser after 2 seconds
        
    def stop_application(self):
        """Stop both backend and frontend"""
        self.log("🛑 Stopping application...")
        
        # Stop processes and update status
        for name, process, status_widget in [
            ("backend", self.backend_process, self.backend_status),
            ("frontend", self.frontend_process, self.frontend_status)
        ]:
            if process:
                process.terminate()
                setattr(self, f"{name}_process", None)
                status_widget.config(text="● Stopped", foreground=self.colors['danger'])
        
        # Reset UI state
        self.is_running = False
        for button, state in [(self.start_button, 'normal'), (self.stop_button, 'disabled'), (self.open_button, 'disabled')]:
            button.config(state=state)
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
    BankParserLauncher().run()
