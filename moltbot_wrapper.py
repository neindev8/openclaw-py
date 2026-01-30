#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Moltbot Wrapper - FULLY AUTOCONFIGURABLE
Automatically installs Node.js, pnpm, dependencies, and runs Moltbot.
"""

import os
import sys
import subprocess
import shutil
import urllib.request
import tempfile
import zipfile
import re
import time
from pathlib import Path
from typing import Optional, Tuple

# ============================================================================
# Configuration
# ============================================================================

MOLTBOT_DIR = Path(__file__).parent.resolve()
MIN_NODE_VERSION = (22, 12, 0)

# Node.js download URLs (Windows x64)
NODE_VERSION = "22.13.0"
NODE_URL = f"https://nodejs.org/dist/v{NODE_VERSION}/node-v{NODE_VERSION}-win-x64.zip"
NODE_INSTALL_DIR = MOLTBOT_DIR / "node_portable"

# ============================================================================
# Unicode & Environment Setup
# ============================================================================

def setup_environment():
    """Configure environment for proper Unicode handling on Windows."""
    os.environ["PYTHONIOENCODING"] = "utf-8"
    os.environ["PYTHONUTF8"] = "1"
    os.environ["FORCE_COLOR"] = "1"
    os.environ["NO_COLOR"] = ""
    
    if sys.platform == "win32":
        try:
            subprocess.run(["chcp", "65001"], shell=True, capture_output=True)
        except:
            pass
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
        except:
            pass

def add_node_to_path():
    """Add Node.js and npm to PATH."""
    # Add portable Node.js if exists
    node_bin = NODE_INSTALL_DIR / f"node-v{NODE_VERSION}-win-x64"
    if node_bin.exists():
        os.environ["PATH"] = str(node_bin) + os.pathsep + os.environ.get("PATH", "")
    
    # Find where node.exe is and add that directory (for npm)
    node_path = shutil.which("node")
    if node_path:
        node_dir = Path(node_path).parent
        if str(node_dir) not in os.environ.get("PATH", ""):
            os.environ["PATH"] = str(node_dir) + os.pathsep + os.environ.get("PATH", "")
    
    # Add npm global bin
    npm_global = Path.home() / "AppData" / "Roaming" / "npm"
    if npm_global.exists():
        os.environ["PATH"] = str(npm_global) + os.pathsep + os.environ["PATH"]
    
    # Also check Program Files for Node.js
    program_files = [
        Path(os.environ.get("ProgramFiles", "C:\\Program Files")) / "nodejs",
        Path(os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)")) / "nodejs",
        Path.home() / "AppData" / "Local" / "Programs" / "nodejs",
    ]
    for pf in program_files:
        if pf.exists() and (pf / "npm.cmd").exists():
            os.environ["PATH"] = str(pf) + os.pathsep + os.environ["PATH"]
            break

# ============================================================================
# Utilities
# ============================================================================

class Colors:
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    CYAN = "\033[96m"
    BLUE = "\033[94m"
    RESET = "\033[0m"
    BOLD = "\033[1m"

def print_header():
    print(f"\n{Colors.CYAN}{'='*60}")
    print(f"  🦞 MOLTBOT WRAPPER - Fully Autoconfigurable")
    print(f"{'='*60}{Colors.RESET}")
    print(f"  Project: {MOLTBOT_DIR}")
    print(f"{Colors.CYAN}{'='*60}{Colors.RESET}\n")

def print_status(message: str, status: str = "INFO"):
    symbols = {"INFO": "ℹ", "OK": "✓", "WARN": "⚠", "ERROR": "✗", "WAIT": "⏳"}
    colors = {"INFO": Colors.BLUE, "OK": Colors.GREEN, "WARN": Colors.YELLOW, 
              "ERROR": Colors.RED, "WAIT": Colors.CYAN}
    color = colors.get(status, Colors.BLUE)
    symbol = symbols.get(status, "•")
    print(f"  {color}[{symbol}] {message}{Colors.RESET}")

def print_progress(current: int, total: int, prefix: str = ""):
    bar_len = 40
    filled = int(bar_len * current / total)
    bar = "█" * filled + "░" * (bar_len - filled)
    pct = current / total * 100
    print(f"\r  {prefix} [{bar}] {pct:.1f}%", end="", flush=True)
    if current >= total:
        print()

def get_node_dir() -> Optional[Path]:
    """Get the directory containing node.exe."""
    # Check PATH
    node = shutil.which("node") or shutil.which("node.exe")
    if node:
        return Path(node).parent
    
    # Check common paths
    common = [
        Path(os.environ.get("ProgramFiles", "C:\\Program Files")) / "nodejs",
        Path.home() / "AppData" / "Local" / "Programs" / "nodejs",
        Path(os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)")) / "nodejs",
    ]
    for p in common:
        if (p / "node.exe").exists():
            return p
    
    # Check portable
    node_bin = NODE_INSTALL_DIR / f"node-v{NODE_VERSION}-win-x64"
    if (node_bin / "node.exe").exists():
        return node_bin
    
    return None

def get_full_path() -> str:
    """Build a complete PATH with Node.js and pnpm."""
    paths = []
    
    # Node.js
    node_dir = get_node_dir()
    if node_dir:
        paths.append(str(node_dir))
    
    # npm global (where pnpm is usually installed)
    npm_global = Path.home() / "AppData" / "Roaming" / "npm"
    if npm_global.exists():
        paths.append(str(npm_global))
    
    # pnpm home
    pnpm_home = Path.home() / "AppData" / "Local" / "pnpm"
    if pnpm_home.exists():
        paths.append(str(pnpm_home))
    
    # Add original PATH
    paths.append(os.environ.get("PATH", ""))
    
    return os.pathsep.join(paths)

def run_command(cmd: list, cwd: Optional[Path] = None, capture: bool = False,
                shell: bool = False, show_output: bool = True) -> Tuple[int, str, str]:
    """Run a command and return (returncode, stdout, stderr)."""
    # Build environment with proper PATH
    env = os.environ.copy()
    env["PATH"] = get_full_path()
    
    try:
        if show_output and not capture:
            result = subprocess.run(
                cmd, cwd=cwd or MOLTBOT_DIR, shell=shell,
                encoding="utf-8", errors="replace", env=env
            )
            return result.returncode, "", ""
        else:
            result = subprocess.run(
                cmd, cwd=cwd or MOLTBOT_DIR, capture_output=True,
                text=True, shell=shell, encoding="utf-8", 
                errors="replace", env=env
            )
            return result.returncode, result.stdout or "", result.stderr or ""
    except FileNotFoundError:
        return -1, "", f"Command not found: {cmd[0]}"
    except Exception as e:
        return -1, "", str(e)

def check_command_exists(cmd: str) -> bool:
    return shutil.which(cmd) is not None

def parse_version(version_str: str) -> Tuple[int, ...]:
    match = re.search(r'(\d+)\.(\d+)\.(\d+)', version_str)
    if match:
        return tuple(int(x) for x in match.groups())
    return (0, 0, 0)

# ============================================================================
# Download Utilities
# ============================================================================

def download_file(url: str, dest: Path, desc: str = "Downloading") -> bool:
    """Download a file with progress bar."""
    try:
        print_status(f"{desc}...", "WAIT")
        
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        
        with urllib.request.urlopen(req, timeout=60) as response:
            total = int(response.headers.get("Content-Length", 0))
            downloaded = 0
            chunk_size = 8192
            
            with open(dest, "wb") as f:
                while True:
                    chunk = response.read(chunk_size)
                    if not chunk:
                        break
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total > 0:
                        print_progress(downloaded, total, desc)
        
        print_status(f"{desc} complete!", "OK")
        return True
        
    except Exception as e:
        print_status(f"Download failed: {e}", "ERROR")
        return False

# ============================================================================
# Node.js Installation
# ============================================================================

def check_node_version() -> Tuple[bool, str]:
    """Check if Node.js is installed and meets minimum version."""
    if not check_command_exists("node"):
        return False, "Node.js not found"
    
    code, stdout, _ = run_command(["node", "--version"], capture=True)
    if code != 0:
        return False, "Failed to get Node.js version"
    
    version = parse_version(stdout.strip())
    if version < MIN_NODE_VERSION:
        return False, f"Node.js {stdout.strip()} < v{'.'.join(map(str, MIN_NODE_VERSION))}"
    
    return True, f"Node.js {stdout.strip()}"

def install_node_portable() -> bool:
    """Download and install Node.js portable version."""
    print_status(f"Installing Node.js v{NODE_VERSION} (portable)...", "INFO")
    
    NODE_INSTALL_DIR.mkdir(parents=True, exist_ok=True)
    zip_path = NODE_INSTALL_DIR / "node.zip"
    
    # Download
    if not download_file(NODE_URL, zip_path, "Downloading Node.js"):
        return False
    
    # Extract
    print_status("Extracting Node.js...", "WAIT")
    try:
        with zipfile.ZipFile(zip_path, 'r') as zf:
            zf.extractall(NODE_INSTALL_DIR)
        zip_path.unlink()  # Delete zip
        print_status("Node.js extracted!", "OK")
    except Exception as e:
        print_status(f"Extract failed: {e}", "ERROR")
        return False
    
    # Add to PATH
    add_node_to_path()
    
    # Verify
    code, stdout, _ = run_command(["node", "--version"], capture=True)
    if code == 0:
        print_status(f"Node.js {stdout.strip()} installed successfully!", "OK")
        return True
    
    print_status("Node.js installation verification failed", "ERROR")
    return False

def install_node_winget() -> bool:
    """Try to install Node.js via winget."""
    if not check_command_exists("winget"):
        return False
    
    print_status("Installing Node.js via winget...", "WAIT")
    code, _, _ = run_command(
        ["winget", "install", "-e", "--id", "OpenJS.NodeJS.LTS", 
         "--accept-source-agreements", "--accept-package-agreements"],
        capture=True
    )
    
    if code == 0:
        print_status("Node.js installed via winget!", "OK")
        print_status("You may need to restart the terminal for PATH changes", "WARN")
        return True
    return False

def ensure_node_installed() -> bool:
    """Ensure Node.js is installed, installing if necessary."""
    ok, msg = check_node_version()
    if ok:
        print_status(msg, "OK")
        return True
    
    print_status(msg, "WARN")
    print_status("Attempting to install Node.js automatically...", "INFO")
    
    # Try winget first (cleaner system install)
    if install_node_winget():
        # Refresh PATH and check again
        time.sleep(2)
        ok, msg = check_node_version()
        if ok:
            return True
    
    # Fallback to portable install
    print_status("Using portable Node.js installation...", "INFO")
    if install_node_portable():
        return True
    
    print_status("Failed to install Node.js automatically!", "ERROR")
    print_status("Please install Node.js 22+ manually from https://nodejs.org", "INFO")
    return False

# ============================================================================
# pnpm Installation
# ============================================================================

def check_pnpm() -> Tuple[bool, str]:
    """Check if pnpm is installed."""
    pnpm = shutil.which("pnpm") or shutil.which("pnpm.cmd")
    if not pnpm:
        # Check in npm global
        npm_global = Path.home() / "AppData" / "Roaming" / "npm"
        pnpm_cmd = npm_global / "pnpm.cmd"
        if pnpm_cmd.exists():
            os.environ["PATH"] = str(npm_global) + os.pathsep + os.environ.get("PATH", "")
            pnpm = str(pnpm_cmd)
    
    if not pnpm:
        # Check pnpm home
        pnpm_home = Path.home() / "AppData" / "Local" / "pnpm"
        pnpm_cmd = pnpm_home / "pnpm.cmd"
        if pnpm_cmd.exists():
            os.environ["PATH"] = str(pnpm_home) + os.pathsep + os.environ.get("PATH", "")
            pnpm = str(pnpm_cmd)
    
    if not pnpm:
        return False, "pnpm not found"
    
    code, stdout, _ = run_command([pnpm, "--version"], capture=True)
    if code != 0:
        return False, "Failed to get pnpm version"
    return True, f"pnpm {stdout.strip()}"

def find_npm() -> Optional[str]:
    """Find npm executable."""
    # Check if npm is in PATH
    npm = shutil.which("npm")
    if npm:
        return npm
    
    # Check npm.cmd on Windows
    npm_cmd = shutil.which("npm.cmd")
    if npm_cmd:
        return npm_cmd
    
    # Find node and look for npm in same directory
    node_path = shutil.which("node")
    if node_path:
        node_dir = Path(node_path).parent
        for npm_name in ["npm.cmd", "npm.exe", "npm"]:
            npm_path = node_dir / npm_name
            if npm_path.exists():
                return str(npm_path)
    
    # Check common installation paths
    common_paths = [
        Path(os.environ.get("ProgramFiles", "C:\\Program Files")) / "nodejs",
        Path.home() / "AppData" / "Local" / "Programs" / "nodejs",
        Path(os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)")) / "nodejs",
    ]
    for path in common_paths:
        npm_cmd = path / "npm.cmd"
        if npm_cmd.exists():
            # Also add to PATH for future use
            os.environ["PATH"] = str(path) + os.pathsep + os.environ.get("PATH", "")
            return str(npm_cmd)
    
    return None

def install_pnpm() -> bool:
    """Install pnpm via npm."""
    print_status("Installing pnpm...", "WAIT")
    
    npm_path = find_npm()
    if not npm_path:
        print_status("npm not found! Trying to find Node.js installation...", "WARN")
        
        # Try to reinstall/fix Node.js
        if install_node_portable():
            add_node_to_path()
            npm_path = find_npm()
    
    if npm_path:
        print_status(f"Found npm at: {npm_path}", "INFO")
        code, stdout, stderr = run_command([npm_path, "install", "-g", "pnpm"], capture=True)
        if code == 0:
            # Refresh PATH
            add_node_to_path()
            ok, msg = check_pnpm()
            if ok:
                print_status(msg, "OK")
                return True
        else:
            print_status(f"npm install failed: {stderr}", "WARN")
    
    # Try corepack as fallback
    print_status("Trying corepack...", "INFO")
    corepack = shutil.which("corepack") or shutil.which("corepack.cmd")
    if corepack:
        run_command([corepack, "enable"], capture=True)
        code, _, _ = run_command([corepack, "prepare", "pnpm@latest", "--activate"], capture=True)
        if code == 0:
            ok, msg = check_pnpm()
            if ok:
                print_status(msg, "OK")
                return True
    
    # Last resort: download pnpm directly
    print_status("Trying direct pnpm installation...", "INFO")
    code, _, _ = run_command(
        ["powershell", "-Command", "iwr https://get.pnpm.io/install.ps1 -useb | iex"],
        capture=True, shell=True
    )
    if code == 0:
        add_node_to_path()
        ok, msg = check_pnpm()
        if ok:
            print_status(msg, "OK")
            return True
    
    print_status("Failed to install pnpm", "ERROR")
    return False

def ensure_pnpm_installed() -> bool:
    ok, msg = check_pnpm()
    if ok:
        print_status(msg, "OK")
        return True
    
    print_status(msg, "WARN")
    return install_pnpm()

# ============================================================================
# Project Setup
# ============================================================================

def check_dependencies_installed() -> bool:
    return (MOLTBOT_DIR / "node_modules").exists()

def get_pnpm_path() -> Optional[str]:
    """Get the full path to pnpm executable."""
    # Check PATH first
    pnpm = shutil.which("pnpm") or shutil.which("pnpm.cmd")
    if pnpm:
        return pnpm
    
    # Check npm global (most common on Windows)
    npm_global = Path.home() / "AppData" / "Roaming" / "npm" / "pnpm.cmd"
    if npm_global.exists():
        return str(npm_global)
    
    # Check pnpm home
    pnpm_home = Path.home() / "AppData" / "Local" / "pnpm" / "pnpm.cmd"
    if pnpm_home.exists():
        return str(pnpm_home)
    
    return None

def install_dependencies() -> bool:
    print_status("Installing project dependencies...", "INFO")
    print_status("This may take several minutes on first run!", "WARN")
    print()
    
    pnpm = get_pnpm_path()
    if not pnpm:
        print_status("pnpm not found!", "ERROR")
        return False
    
    print_status(f"Using pnpm: {pnpm}", "INFO")
    print()
    
    # Run with output visible
    code, stdout, stderr = run_command([pnpm, "install"], cwd=MOLTBOT_DIR, capture=False)
    
    if code != 0:
        print_status(f"pnpm install failed with code {code}", "ERROR")
        if stderr:
            print(f"\n  Error details:\n{stderr}\n")
        return False
    
    print_status("Dependencies installed!", "OK")
    return True

def get_node_path() -> Optional[str]:
    """Get the full path to node executable."""
    node_dir = get_node_dir()
    if node_dir:
        node_exe = node_dir / "node.exe"
        if node_exe.exists():
            return str(node_exe)
    return shutil.which("node") or shutil.which("node.exe")

def build_project() -> bool:
    print_status("Building project...", "INFO")
    print()
    
    pnpm = get_pnpm_path()
    if not pnpm:
        print_status("pnpm not found!", "ERROR")
        return False
    
    node = get_node_path()
    if not node:
        print_status("node not found!", "ERROR")
        return False
    
    # First, run the A2UI bundle using Python script (Windows compatible)
    bundle_script = MOLTBOT_DIR / "scripts" / "bundle-a2ui.py"
    if bundle_script.exists():
        print_status("Bundling A2UI (Windows mode)...", "INFO")
        code, _, stderr = run_command(["python", str(bundle_script)], capture=False)
        if code != 0:
            print_status("A2UI bundling failed, continuing anyway...", "WARN")
    
    # Run TypeScript compilation
    print_status("Compiling TypeScript...", "INFO")
    code, _, stderr = run_command([pnpm, "exec", "tsc", "-p", "tsconfig.json"], cwd=MOLTBOT_DIR)
    if code != 0:
        print_status(f"TypeScript compilation failed", "ERROR")
        return False
    
    # Run post-build scripts using node directly (avoid bash)
    post_scripts = [
        [node, "--import", "tsx", "scripts/canvas-a2ui-copy.ts"],
        [node, "--import", "tsx", "scripts/copy-hook-metadata.ts"],
        [node, "--import", "tsx", "scripts/write-build-info.ts"],
    ]
    
    for script_cmd in post_scripts:
        script_name = script_cmd[-1]
        script_path = MOLTBOT_DIR / script_name
        if script_path.exists():
            print_status(f"Running {script_name}...", "INFO")
            code, _, _ = run_command(script_cmd, cwd=MOLTBOT_DIR, capture=False)
            if code != 0:
                print_status(f"{script_name} failed, continuing...", "WARN")
    
    print_status("Build complete!", "OK")
    return True

def build_ui() -> bool:
    print_status("Building UI...", "INFO")
    
    pnpm = get_pnpm_path()
    if not pnpm:
        return False
    
    code, _, _ = run_command([pnpm, "ui:build"], cwd=MOLTBOT_DIR)
    if code != 0:
        print_status("UI build failed (may be optional)", "WARN")
        return False
    print_status("UI built!", "OK")
    return True

# ============================================================================
# Moltbot Commands
# ============================================================================

def run_moltbot(args: list) -> bool:
    pnpm = get_pnpm_path()
    if not pnpm:
        print_status("pnpm not found!", "ERROR")
        return False
    
    cmd = [pnpm, "moltbot"] + args
    print_status(f"Running: pnpm moltbot {' '.join(args)}", "INFO")
    print(f"\n{'-'*60}\n")
    code, _, _ = run_command(cmd, cwd=MOLTBOT_DIR)
    print(f"\n{'-'*60}")
    return code == 0

# ============================================================================
# Menu
# ============================================================================

def show_menu():
    print(f"\n{Colors.CYAN}{'='*60}")
    print("  MAIN MENU")
    print(f"{'='*60}{Colors.RESET}")
    print(f"""
  {Colors.GREEN}[1]{Colors.RESET} Onboard          - Setup wizard (run this first!)
  {Colors.GREEN}[2]{Colors.RESET} Gateway          - Start gateway server
  {Colors.GREEN}[3]{Colors.RESET} TUI              - Terminal UI
  {Colors.GREEN}[4]{Colors.RESET} Doctor           - Run diagnostics
  {Colors.GREEN}[5]{Colors.RESET} Dev Mode         - Development mode
  {Colors.GREEN}[6]{Colors.RESET} Custom Command   - Run any moltbot command
  
  {Colors.YELLOW}[R]{Colors.RESET} Reinstall Deps   - Reinstall all dependencies
  {Colors.YELLOW}[B]{Colors.RESET} Rebuild          - Rebuild project
  
  {Colors.RED}[Q]{Colors.RESET} Quit
""")
    print(f"{Colors.CYAN}{'='*60}{Colors.RESET}")

def handle_menu(choice: str) -> bool:
    choice = choice.strip().upper()
    
    if choice == "Q":
        return False
    elif choice == "1":
        run_moltbot(["onboard"])
    elif choice == "2":
        run_moltbot(["gateway", "--verbose"])
    elif choice == "3":
        run_moltbot(["tui"])
    elif choice == "4":
        run_moltbot(["doctor"])
    elif choice == "5":
        pnpm = get_pnpm_path()
        if pnpm:
            run_command([pnpm, "dev"], cwd=MOLTBOT_DIR)
    elif choice == "6":
        print("\n  Enter arguments (e.g., 'agent --message \"Hello\"'):")
        args = input("  > moltbot ").strip()
        if args:
            run_moltbot(args.split())
    elif choice == "R":
        shutil.rmtree(MOLTBOT_DIR / "node_modules", ignore_errors=True)
        install_dependencies()
    elif choice == "B":
        build_project()
    else:
        print_status(f"Unknown option: {choice}", "WARN")
    
    input(f"\n  {Colors.CYAN}Press Enter to continue...{Colors.RESET}")
    return True

# ============================================================================
# Main
# ============================================================================

def full_setup() -> bool:
    """Run full setup: Node.js, pnpm, dependencies, build."""
    print_status("Starting full auto-setup...", "INFO")
    print()
    
    # 1. Node.js
    if not ensure_node_installed():
        return False
    
    # Refresh PATH after Node.js install
    add_node_to_path()
    
    # 2. pnpm
    if not ensure_pnpm_installed():
        return False
    
    # Refresh PATH after pnpm install
    add_node_to_path()
    
    # 3. Dependencies
    if not check_dependencies_installed():
        print()
        if not install_dependencies():
            return False
        print()
        if not build_project():
            return False
    else:
        print_status("Dependencies already installed", "OK")
        
        # Check if dist exists
        if not (MOLTBOT_DIR / "dist").exists():
            print_status("Building project...", "INFO")
            if not build_project():
                return False
    
    print()
    print_status("Setup complete! Ready to run.", "OK")
    return True

def main():
    setup_environment()
    add_node_to_path()
    os.chdir(MOLTBOT_DIR)
    
    print_header()
    
    if not full_setup():
        print()
        print_status("Setup failed. Please check errors above.", "ERROR")
        input("\n  Press Enter to exit...")
        return 1
    
    # Check for auto-onboard flag
    if "--auto-onboard" in sys.argv:
        print()
        print_status("Running onboard wizard automatically...", "INFO")
        run_moltbot(["onboard"])
        return 0
    
    # Check for direct command
    if len(sys.argv) > 1 and sys.argv[1] != "--auto-onboard":
        return 0 if run_moltbot(sys.argv[1:]) else 1
    
    # Menu loop
    running = True
    while running:
        show_menu()
        choice = input("  Select option: ")
        running = handle_menu(choice)
    
    print(f"\n  {Colors.CYAN}Goodbye! 🦞{Colors.RESET}\n")
    return 0

if __name__ == "__main__":
    sys.exit(main())
