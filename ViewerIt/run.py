#!/usr/bin/env python3
"""
ViewerIt Unified Launcher
==========================
A single-command launcher that starts ViewerIt services with UI selection.

Usage:
    python run.py                    # Start all services (Backend + React + Streamlit)
    python run.py --ui react         # Start Backend + React only
    python run.py --ui streamlit     # Start Backend + Streamlit only
    python run.py --check            # Check system prerequisites only
    python run.py --install          # Install dependencies only
"""

import os
import sys
import subprocess
import signal
import time
import socket
import shutil
import threading
import queue
import argparse
import webbrowser
from pathlib import Path
from datetime import datetime

# =============================================================================
# CONFIGURATION
# =============================================================================

PROJECT_ROOT = Path(__file__).parent.resolve()
BACKEND_DIR = PROJECT_ROOT / "backend"
FRONTEND_DIR = PROJECT_ROOT / "frontend"
STREAMLIT_DIR = PROJECT_ROOT / "streamlit_app"
VENV_DIR = PROJECT_ROOT / "venv"

# Service ports
BACKEND_PORT = 8000
FRONTEND_PORT = 5173
STREAMLIT_PORT = 8501

# Minimum versions
MIN_PYTHON_VERSION = (3, 10)
MIN_NODE_VERSION = 18

# UI Mode options
UI_MODES = ["all", "react", "streamlit"]

# =============================================================================
# COLORS AND FORMATTING
# =============================================================================

class Colors:
    """ANSI color codes for terminal output."""
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    
    # Service colors
    BACKEND = "\033[96m"    # Cyan
    FRONTEND = "\033[95m"   # Magenta
    STREAMLIT = "\033[93m"  # Yellow
    LAUNCHER = "\033[92m"   # Green
    ERROR = "\033[91m"      # Red
    WARNING = "\033[93m"    # Yellow
    INFO = "\033[94m"       # Blue
    SUCCESS = "\033[92m"    # Green

def print_banner():
    """Print the ViewerIt ASCII banner."""
    # Use ASCII-safe banner for better Windows compatibility
    banner = f"""
{Colors.BACKEND} __      ___                      ___ _   {Colors.RESET}
{Colors.BACKEND} \\ \\    / (_)                    |_ _| |  {Colors.RESET}
{Colors.FRONTEND}  \\ \\  / / _  _____      _____ _ _| || |_ {Colors.RESET}
{Colors.FRONTEND}   \\ \\/ / | |/ _ \\ \\ /\\ / / _ \\ '__| || __|{Colors.RESET}
{Colors.STREAMLIT}    \\  /  | |  __/\\ V  V /  __/ |  | || |_ {Colors.RESET}
{Colors.STREAMLIT}     \\/   |_|\\___| \\_/\\_/ \\___|_| |___\\__|{Colors.RESET}

{Colors.DIM}  Cyberpunk eDiscovery Data Comparator - Unified Launcher{Colors.RESET}
"""
    try:
        print(banner)
    except UnicodeEncodeError:
        # Fallback for terminals that can't handle special characters
        print(f"\n{Colors.BACKEND}ViewerIt{Colors.RESET}")
        print(f"{Colors.DIM}Cyberpunk eDiscovery Data Comparator - Unified Launcher{Colors.RESET}\n")

def log(message: str, service: str = "LAUNCHER", level: str = "INFO"):
    """Print a formatted log message."""
    colors = {
        "BACKEND": Colors.BACKEND,
        "FRONTEND": Colors.FRONTEND,
        "STREAMLIT": Colors.STREAMLIT,
        "LAUNCHER": Colors.LAUNCHER,
    }
    level_colors = {
        "INFO": Colors.INFO,
        "SUCCESS": Colors.SUCCESS,
        "WARNING": Colors.WARNING,
        "ERROR": Colors.ERROR,
    }
    
    timestamp = datetime.now().strftime("%H:%M:%S")
    service_color = colors.get(service, Colors.INFO)
    level_color = level_colors.get(level, Colors.INFO)
    
    prefix = f"{Colors.DIM}[{timestamp}]{Colors.RESET} {service_color}[{service:^10}]{Colors.RESET}"
    print(f"{prefix} {message}")

def log_error(message: str, service: str = "LAUNCHER"):
    """Print an error message."""
    log(f"{Colors.ERROR}{message}{Colors.RESET}", service, "ERROR")

def log_success(message: str, service: str = "LAUNCHER"):
    """Print a success message."""
    log(f"{Colors.SUCCESS}{message}{Colors.RESET}", service, "SUCCESS")

def log_warning(message: str, service: str = "LAUNCHER"):
    """Print a warning message."""
    log(f"{Colors.WARNING}{message}{Colors.RESET}", service, "WARNING")

# =============================================================================
# SYSTEM CHECKS
# =============================================================================

def check_python_version() -> bool:
    """Check if Python version meets minimum requirements."""
    current = sys.version_info[:2]
    if current >= MIN_PYTHON_VERSION:
        log_success(f"Python {current[0]}.{current[1]} [OK]")
        return True
    else:
        log_error(f"Python {current[0]}.{current[1]} found, need {MIN_PYTHON_VERSION[0]}.{MIN_PYTHON_VERSION[1]}+")
        return False

def check_node_version() -> bool:
    """Check if Node.js is installed and meets minimum version."""
    try:
        result = subprocess.run(
            ["node", "--version"],
            capture_output=True, text=True, timeout=10
        )
        version_str = result.stdout.strip().lstrip('v')
        major_version = int(version_str.split('.')[0])
        
        if major_version >= MIN_NODE_VERSION:
            log_success(f"Node.js v{version_str} [OK]")
            return True
        else:
            log_error(f"Node.js v{version_str} found, need v{MIN_NODE_VERSION}+")
            return False
    except FileNotFoundError:
        log_error("Node.js not found. Install from https://nodejs.org")
        return False
    except Exception as e:
        log_error(f"Error checking Node.js: {e}")
        return False

def check_npm() -> bool:
    """Check if npm is available."""
    try:
        # Use npm.cmd on Windows
        npm_cmd = "npm.cmd" if sys.platform == "win32" else "npm"
        result = subprocess.run(
            [npm_cmd, "--version"],
            capture_output=True, text=True, timeout=10,
            shell=(sys.platform == "win32")  # Use shell on Windows
        )
        if result.returncode == 0:
            version = result.stdout.strip()
            log_success(f"npm v{version} [OK]")
            return True
        else:
            log_error("npm not found")
            return False
    except FileNotFoundError:
        log_error("npm not found")
        return False
    except Exception as e:
        log_error(f"Error checking npm: {e}")
        return False

def check_port_available(port: int) -> bool:
    """Check if a port is available."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(("127.0.0.1", port))
            return True
        except socket.error:
            return False

def check_ports(ui_mode: str = "all") -> dict:
    """Check if required ports are available based on UI mode."""
    ports = {
        "Backend (8000)": BACKEND_PORT,
    }
    
    if ui_mode in ["all", "react"]:
        ports["Frontend (5173)"] = FRONTEND_PORT
    if ui_mode in ["all", "streamlit"]:
        ports["Streamlit (8501)"] = STREAMLIT_PORT
    
    results = {}
    for name, port in ports.items():
        available = check_port_available(port)
        results[name] = available
        if available:
            log_success(f"Port {port} available [OK]")
        else:
            log_warning(f"Port {port} in use - {name} may fail to start")
    
    return results

def check_ollama() -> bool:
    """Check if Ollama is running (optional for AI features)."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            s.connect(("127.0.0.1", 11434))
            log_success("Ollama running [OK] (AI features available)")
            return True
    except (socket.error, socket.timeout):
        log_warning("Ollama not running - AI features will be limited")
        return False

def run_system_checks(ui_mode: str = "all") -> bool:
    """Run all system prerequisite checks."""
    print(f"\n{Colors.BOLD}System Prerequisites Check{Colors.RESET}")
    print("=" * 50)
    
    checks = []
    checks.append(("Python", check_python_version()))
    
    # Only check Node.js/npm if React UI is needed
    if ui_mode in ["all", "react"]:
        checks.append(("Node.js", check_node_version()))
        checks.append(("npm", check_npm()))
    
    print()
    check_ports(ui_mode)
    print()
    check_ollama()
    
    # Check critical requirements
    critical_names = ["Python"]
    if ui_mode in ["all", "react"]:
        critical_names.extend(["Node.js", "npm"])
    
    critical_passed = all(passed for name, passed in checks if name in critical_names)
    
    print()
    if critical_passed:
        log_success("All critical prerequisites met!")
    else:
        log_error("Some critical prerequisites are missing. Please install them first.")
    
    return critical_passed

# =============================================================================
# ENVIRONMENT SETUP
# =============================================================================

def setup_venv() -> bool:
    """Create Python virtual environment if it doesn't exist."""
    if VENV_DIR.exists():
        log_success("Virtual environment exists [OK]")
        return True
    
    log("Creating virtual environment...")
    try:
        subprocess.run(
            [sys.executable, "-m", "venv", str(VENV_DIR)],
            check=True, capture_output=True
        )
        log_success("Virtual environment created [OK]")
        return True
    except subprocess.CalledProcessError as e:
        log_error(f"Failed to create venv: {e}")
        return False

def get_venv_python() -> str:
    """Get the path to the virtual environment's Python executable."""
    if sys.platform == "win32":
        return str(VENV_DIR / "Scripts" / "python.exe")
    return str(VENV_DIR / "bin" / "python")

def get_venv_pip() -> str:
    """Get the path to the virtual environment's pip executable."""
    if sys.platform == "win32":
        return str(VENV_DIR / "Scripts" / "pip.exe")
    return str(VENV_DIR / "bin" / "pip")

def install_python_deps() -> bool:
    """Install Python dependencies."""
    requirements_file = PROJECT_ROOT / "requirements.txt"
    
    if not requirements_file.exists():
        log_error("requirements.txt not found")
        return False
    
    log("Installing Python dependencies...")
    try:
        subprocess.run(
            [get_venv_pip(), "install", "-r", str(requirements_file), "-q"],
            check=True, capture_output=True
        )
        log_success("Python dependencies installed [OK]")
        return True
    except subprocess.CalledProcessError as e:
        log_error(f"Failed to install Python deps: {e.stderr.decode() if e.stderr else e}")
        return False

def install_npm_deps() -> bool:
    """Install npm dependencies for the frontend."""
    node_modules = FRONTEND_DIR / "node_modules"
    package_lock = FRONTEND_DIR / "package-lock.json"
    
    # Check if node_modules exists and has content
    if node_modules.exists() and any(node_modules.iterdir()):
        # Quick validation: check if key packages exist
        vite_pkg = node_modules / "vite"
        react_pkg = node_modules / "react"
        if vite_pkg.exists() and react_pkg.exists():
            log_success("npm dependencies already installed [OK]")
            return True
        else:
            log_warning("node_modules incomplete, reinstalling...")
    
    log("Installing npm dependencies (this may take a minute)...")
    try:
        # Use npm.cmd on Windows
        npm_cmd = "npm.cmd" if sys.platform == "win32" else "npm"
        
        # Use npm ci if package-lock exists for faster, more reliable installs
        install_cmd = "ci" if package_lock.exists() else "install"
        
        result = subprocess.run(
            [npm_cmd, install_cmd],
            cwd=str(FRONTEND_DIR),
            capture_output=True,
            text=True,
            shell=(sys.platform == "win32"),
            timeout=300  # 5 minute timeout
        )
        
        if result.returncode != 0:
            log_error(f"npm {install_cmd} failed: {result.stderr}")
            return False
            
        log_success("npm dependencies installed [OK]")
        return True
    except subprocess.TimeoutExpired:
        log_error("npm install timed out after 5 minutes")
        return False
    except subprocess.CalledProcessError as e:
        log_error(f"Failed to install npm deps: {e.stderr if e.stderr else e}")
        return False
    except Exception as e:
        log_error(f"Error installing npm deps: {e}")
        return False

def setup_environment(ui_mode: str = "all") -> bool:
    """Set up the complete environment."""
    print(f"\n{Colors.BOLD}Environment Setup{Colors.RESET}")
    print("=" * 50)
    
    if not setup_venv():
        return False
    
    if not install_python_deps():
        return False
    
    # Only install npm deps if React UI is needed
    if ui_mode in ["all", "react"]:
        if not install_npm_deps():
            return False
    
    print()
    log_success("Environment setup complete!")
    return True

# =============================================================================
# SERVICE MANAGEMENT
# =============================================================================

class ServiceManager:
    """Manages the lifecycle of ViewerIt services."""
    
    def __init__(self, ui_mode: str = "all"):
        self.ui_mode = ui_mode
        self.processes: dict[str, subprocess.Popen] = {}
        self.output_queue = queue.Queue()
        self.running = False
        self.output_threads: list[threading.Thread] = []
    
    def _stream_output(self, process: subprocess.Popen, service_name: str, stream):
        """Stream output from a process to the queue."""
        try:
            for line in iter(stream.readline, ''):
                if not self.running:
                    break
                if line.strip():
                    self.output_queue.put((service_name, line.strip()))
        except Exception:
            pass
    
    def _print_output(self):
        """Print output from the queue."""
        while self.running or not self.output_queue.empty():
            try:
                service, message = self.output_queue.get(timeout=0.1)
                log(message, service)
            except queue.Empty:
                continue
    
    def start_backend(self) -> bool:
        """Start the FastAPI backend server."""
        log("Starting Backend server...", "BACKEND")
        
        try:
            env = os.environ.copy()
            # Ensure Python output is unbuffered for real-time logs
            env["PYTHONUNBUFFERED"] = "1"
            
            process = subprocess.Popen(
                [get_venv_python(), "-m", "uvicorn", "main:app", 
                 "--host", "0.0.0.0", "--port", str(BACKEND_PORT), "--reload"],
                cwd=str(BACKEND_DIR),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                env=env
            )
            self.processes["BACKEND"] = process
            
            # Start output streaming thread
            thread = threading.Thread(
                target=self._stream_output,
                args=(process, "BACKEND", process.stdout),
                daemon=True
            )
            thread.start()
            self.output_threads.append(thread)
            
            return True
        except Exception as e:
            log_error(f"Failed to start backend: {e}", "BACKEND")
            return False
    
    def start_frontend(self) -> bool:
        """Start the Vite frontend server."""
        log("Starting React Frontend...", "FRONTEND")
        
        try:
            env = os.environ.copy()
            # Force color output and disable interactive prompts
            env["FORCE_COLOR"] = "1"
            env["CI"] = "true"
            
            # Use npm.cmd on Windows with shell=True
            npm_cmd = "npm.cmd" if sys.platform == "win32" else "npm"
            
            # Add --host flag to make frontend accessible on network
            process = subprocess.Popen(
                [npm_cmd, "run", "dev", "--", "--host"],
                cwd=str(FRONTEND_DIR),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                shell=(sys.platform == "win32"),
                env=env
            )
            self.processes["FRONTEND"] = process
            
            # Start output streaming thread
            thread = threading.Thread(
                target=self._stream_output,
                args=(process, "FRONTEND", process.stdout),
                daemon=True
            )
            thread.start()
            self.output_threads.append(thread)
            
            return True
        except Exception as e:
            log_error(f"Failed to start frontend: {e}", "FRONTEND")
            return False
    
    def start_streamlit(self) -> bool:
        """Start the Streamlit dashboard."""
        log("Starting Streamlit dashboard...", "STREAMLIT")
        
        try:
            env = os.environ.copy()
            # Ensure Python output is unbuffered for real-time logs
            env["PYTHONUNBUFFERED"] = "1"
            
            process = subprocess.Popen(
                [get_venv_python(), "-m", "streamlit", "run",
                 str(STREAMLIT_DIR / "viz_report.py"),
                 "--server.port", str(STREAMLIT_PORT),
                 "--server.headless", "true",
                 "--browser.gatherUsageStats", "false"],
                cwd=str(PROJECT_ROOT),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                env=env
            )
            self.processes["STREAMLIT"] = process
            
            # Start output streaming thread
            thread = threading.Thread(
                target=self._stream_output,
                args=(process, "STREAMLIT", process.stdout),
                daemon=True
            )
            thread.start()
            self.output_threads.append(thread)
            
            return True
        except Exception as e:
            log_error(f"Failed to start streamlit: {e}", "STREAMLIT")
            return False
    
    def start_services(self) -> bool:
        """Start services based on UI mode."""
        self.running = True
        
        # Start output printer thread
        printer_thread = threading.Thread(target=self._print_output, daemon=True)
        printer_thread.start()
        
        # Always start backend
        if not self.start_backend():
            return False
        time.sleep(2)  # Wait for backend to initialize
        
        # Start UI services based on mode
        if self.ui_mode == "all":
            if not self.start_streamlit():
                return False
            time.sleep(1)
            if not self.start_frontend():
                return False
        elif self.ui_mode == "react":
            if not self.start_frontend():
                return False
        elif self.ui_mode == "streamlit":
            if not self.start_streamlit():
                return False
        
        return True
    
    def stop_all(self):
        """Stop all services gracefully."""
        self.running = False
        log("Shutting down services...")
        
        for name, process in self.processes.items():
            if process and process.poll() is None:
                log(f"Stopping {name}...", name)
                try:
                    if sys.platform == "win32":
                        process.terminate()
                    else:
                        process.send_signal(signal.SIGTERM)
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                except Exception:
                    pass
        
        log_success("All services stopped.")
    
    def wait(self):
        """Wait for all services to exit or for interrupt."""
        try:
            while self.running:
                # Check if any process has died
                for name, process in list(self.processes.items()):
                    if process.poll() is not None:
                        log_error(f"{name} exited unexpectedly with code {process.returncode}", name)
                        self.running = False
                        break
                time.sleep(1)
        except KeyboardInterrupt:
            print()
            log("Received interrupt signal...")
        finally:
            self.stop_all()

# =============================================================================
# MAIN
# =============================================================================

def print_service_urls(ui_mode: str, open_browser: bool = False):
    """Print the URLs for running services."""
    frontend_url = f"http://localhost:{FRONTEND_PORT}"
    backend_url = f"http://localhost:{BACKEND_PORT}"
    streamlit_url = f"http://localhost:{STREAMLIT_PORT}"
    docs_url = f"http://localhost:{BACKEND_PORT}/docs"
    
    try:
        print(f"\n{Colors.BOLD}+-----------------------------------------------------------+{Colors.RESET}")
        print(f"{Colors.BOLD}|{Colors.RESET}                   {Colors.SUCCESS}Services Started!{Colors.RESET}                       {Colors.BOLD}|{Colors.RESET}")
        print(f"{Colors.BOLD}+-----------------------------------------------------------+{Colors.RESET}")
        print(f"{Colors.BOLD}|{Colors.RESET}                                                           {Colors.BOLD}|{Colors.RESET}")
        
        if ui_mode in ["all", "react"]:
            print(f"{Colors.BOLD}|{Colors.RESET}  {Colors.FRONTEND}> React UI:{Colors.RESET}   {frontend_url}                   {Colors.BOLD}|{Colors.RESET}")
        if ui_mode in ["all", "streamlit"]:
            print(f"{Colors.BOLD}|{Colors.RESET}  {Colors.STREAMLIT}> Streamlit:{Colors.RESET}  {streamlit_url}                    {Colors.BOLD}|{Colors.RESET}")
        
        print(f"{Colors.BOLD}|{Colors.RESET}  {Colors.BACKEND}> Backend:{Colors.RESET}    {backend_url}                    {Colors.BOLD}|{Colors.RESET}")
        print(f"{Colors.BOLD}|{Colors.RESET}  {Colors.INFO}> API Docs:{Colors.RESET}   {docs_url}                {Colors.BOLD}|{Colors.RESET}")
        print(f"{Colors.BOLD}|{Colors.RESET}                                                           {Colors.BOLD}|{Colors.RESET}")
        print(f"{Colors.BOLD}|{Colors.RESET}  {Colors.DIM}Press Ctrl+C to stop all services{Colors.RESET}                     {Colors.BOLD}|{Colors.RESET}")
        print(f"{Colors.BOLD}|{Colors.RESET}                                                           {Colors.BOLD}|{Colors.RESET}")
        print(f"{Colors.BOLD}+-----------------------------------------------------------+{Colors.RESET}")
        
        # Show UI mode info
        if ui_mode == "react":
            print(f"\n{Colors.INFO}UI Mode: React only (Streamlit disabled){Colors.RESET}")
        elif ui_mode == "streamlit":
            print(f"\n{Colors.INFO}UI Mode: Streamlit only (React disabled){Colors.RESET}")
        else:
            print(f"\n{Colors.INFO}UI Mode: All (React + Streamlit as separate apps){Colors.RESET}")
        
        print()
        
    except UnicodeEncodeError:
        # Fallback for problematic terminals
        print(f"\n{Colors.SUCCESS}Services Started!{Colors.RESET}")
        if ui_mode in ["all", "react"]:
            print(f"  {Colors.FRONTEND}React UI:{Colors.RESET}   {frontend_url}")
        if ui_mode in ["all", "streamlit"]:
            print(f"  {Colors.STREAMLIT}Streamlit:{Colors.RESET}  {streamlit_url}")
        print(f"  {Colors.BACKEND}Backend:{Colors.RESET}    {backend_url}")
        print(f"  {Colors.INFO}API Docs:{Colors.RESET}   {docs_url}")
        print(f"\n  {Colors.DIM}Press Ctrl+C to stop all services{Colors.RESET}\n")
    
    # Open browser if requested
    if open_browser:
        time.sleep(1)
        if ui_mode == "streamlit":
            webbrowser.open(streamlit_url)
        else:
            webbrowser.open(frontend_url)

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="ViewerIt Unified Launcher",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run.py                    Start all services (Backend + React + Streamlit)
  python run.py --ui react         Start Backend + React UI only
  python run.py --ui streamlit     Start Backend + Streamlit UI only
  python run.py --check            Check system prerequisites only
  python run.py --install          Install dependencies only
  python run.py --open             Open browser after startup
        """
    )
    parser.add_argument("--check", action="store_true", help="Check prerequisites only")
    parser.add_argument("--install", action="store_true", help="Install dependencies only")
    parser.add_argument("--skip-checks", action="store_true", help="Skip prerequisite checks")
    parser.add_argument("--ui", choices=UI_MODES, default="all", 
                        help="UI mode: 'all' (both), 'react' (React only), 'streamlit' (Streamlit only)")
    parser.add_argument("--open", action="store_true", help="Open browser after startup")
    
    args = parser.parse_args()
    
    # Enable ANSI colors on Windows
    if sys.platform == "win32":
        os.system("")  # Enables ANSI escape sequences on Windows 10+
    
    print_banner()
    
    # Show selected UI mode
    print(f"{Colors.INFO}Selected UI Mode: {Colors.BOLD}{args.ui.upper()}{Colors.RESET}")
    
    # Check only mode
    if args.check:
        success = run_system_checks(args.ui)
        sys.exit(0 if success else 1)
    
    # Run checks unless skipped
    if not args.skip_checks:
        if not run_system_checks(args.ui):
            log_error("Prerequisites check failed. Use --skip-checks to bypass.")
            sys.exit(1)
    
    # Setup environment
    if not setup_environment(args.ui):
        log_error("Environment setup failed.")
        sys.exit(1)
    
    # Install only mode
    if args.install:
        log_success("Dependencies installed successfully!")
        sys.exit(0)
    
    # Start services
    print(f"\n{Colors.BOLD}Starting Services ({args.ui.upper()} mode){Colors.RESET}")
    print("=" * 50)
    
    manager = ServiceManager(ui_mode=args.ui)
    
    # Handle signals
    def signal_handler(sig, frame):
        manager.stop_all()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    if not manager.start_services():
        log_error("Failed to start one or more services")
        manager.stop_all()
        sys.exit(1)
    
    # Wait a moment for services to initialize
    time.sleep(3)
    
    print_service_urls(args.ui, open_browser=args.open)
    
    # Wait for services
    manager.wait()

if __name__ == "__main__":
    main()
