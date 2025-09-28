# ============================================
# LEONA SMART LAUNCHER WITH PORT MANAGEMENT
# File: leona_launcher.py
# ============================================

import os
import sys
import psutil
import socket
import subprocess
import time
from pathlib import Path

class LeonaLauncher:
    def __init__(self):
        self.default_port = 8000
        self.available_ports = [8000, 8001, 8080, 8888, 3000, 5000]
        
    def print_banner(self):
        print("""
        ╔══════════════════════════════════════════════════╗
        ║           LEONA LAUNCHER & MANAGER               ║
        ║         Intelligent Process Management           ║
        ╚══════════════════════════════════════════════════╝
        """)
    
    def find_process_on_port(self, port):
        """Find process using specific port"""
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                for conn in proc.connections():
                    if conn.laddr.port == port:
                        return proc
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return None
    
    def is_port_available(self, port):
        """Check if port is available"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('127.0.0.1', port))
                return True
        except:
            return False
    
    def kill_process_on_port(self, port):
        """Kill process using specific port"""
        proc = self.find_process_on_port(port)
        if proc:
            try:
                proc.terminate()
                time.sleep(2)
                if proc.is_running():
                    proc.kill()
                return True
            except:
                return False
        return False
    
    def find_available_port(self):
        """Find first available port"""
        for port in self.available_ports:
            if self.is_port_available(port):
                return port
        # If all predefined ports are busy, find a random one
        for port in range(8100, 9000):
            if self.is_port_available(port):
                return port
        return None
    
    def list_leona_processes(self):
        """List all LEONA related processes"""
        leona_processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = ' '.join(proc.info['cmdline'] or [])
                if any(keyword in cmdline.lower() for keyword in ['leona', 'jarvis', 'uvicorn']):
                    leona_processes.append({
                        'pid': proc.info['pid'],
                        'name': proc.info['name'],
                        'cmdline': cmdline[:100]
                    })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return leona_processes
    
    def manage_processes(self):
        """Manage LEONA processes"""
        print("\n📊 Current LEONA Processes:")
        print("-" * 50)
        
        processes = self.list_leona_processes()
        
        if not processes:
            print("No LEONA processes running")
            return
        
        for i, proc in enumerate(processes, 1):
            print(f"{i}. PID: {proc['pid']} - {proc['name']}")
            print(f"   Command: {proc['cmdline']}")
        
        print("\nOptions:")
        print("1. Kill all LEONA processes")
        print("2. Kill specific process by PID")
        print("3. Continue without killing")
        
        choice = input("\nSelect option (1-3): ").strip()
        
        if choice == "1":
            for proc in processes:
                try:
                    psutil.Process(proc['pid']).terminate()
                    print(f"Terminated PID {proc['pid']}")
                except:
                    pass
            time.sleep(2)
        elif choice == "2":
            pid = input("Enter PID to kill: ").strip()
            try:
                psutil.Process(int(pid)).terminate()
                print(f"Terminated PID {pid}")
                time.sleep(2)
            except:
                print("Failed to terminate process")
    
    def launch_leona(self, mode="advanced"):
        """Launch LEONA with available port"""
        print("\n🚀 Launching LEONA...")
        
        # Check port 8000
        if not self.is_port_available(8000):
            print(f"⚠️ Port 8000 is busy")
            
            print("\nOptions:")
            print("1. Kill process on port 8000 and use it")
            print("2. Use different port")
            print("3. Exit")
            
            choice = input("\nSelect (1-3): ").strip()
            
            if choice == "1":
                print("Killing process on port 8000...")
                if self.kill_process_on_port(8000):
                    print("✅ Port 8000 freed")
                    port = 8000
                else:
                    print("❌ Failed to free port 8000")
                    port = self.find_available_port()
            elif choice == "2":
                port = self.find_available_port()
            else:
                return
        else:
            port = 8000
        
        if not port:
            print("❌ No available ports found")
            return
        
        print(f"✅ Using port {port}")
        
        # Determine which file to launch
        if mode == "advanced":
            if Path("leona_advanced.py").exists():
                launch_file = "leona_advanced.py"
            else:
                print("leona_advanced.py not found, trying jarvis_backend.py")
                launch_file = "jarvis_backend.py"
        else:
            launch_file = "jarvis_backend.py"
        
        if not Path(launch_file).exists():
            print(f"❌ {launch_file} not found")
            return
        
        # Modify the launch command to use the selected port
        print(f"Starting {launch_file} on port {port}...")
        
        # Create temporary launch file with custom port
        temp_launcher = f"""
import sys
sys.path.insert(0, '.')
import uvicorn

# Import the app from the target file
if "{launch_file}" == "leona_advanced.py":
    from leona_advanced import app
else:
    from jarvis_backend import app

if __name__ == "__main__":
    print("\\n🌟 LEONA Starting on port {port}")
    uvicorn.run(app, host="127.0.0.1", port={port}, log_level="info")
"""
        
        with open("temp_launcher.py", "w") as f:
            f.write(temp_launcher)
        
        # Launch
        subprocess.Popen([sys.executable, "temp_launcher.py"])
        
        time.sleep(3)
        print(f"\n✨ LEONA should be running at: http://localhost:{port}")
        
        # Open browser
        import webbrowser
        webbrowser.open(f"http://localhost:{port}")
    
    def status_check(self):
        """Check LEONA status"""
        print("\n📊 LEONA Status Check")
        print("-" * 50)
        
        # Check ports
        for port in self.available_ports:
            if self.is_port_available(port):
                print(f"Port {port}: ✅ Available")
            else:
                proc = self.find_process_on_port(port)
                if proc:
                    print(f"Port {port}: ❌ Used by {proc.name()} (PID: {proc.pid})")
                else:
                    print(f"Port {port}: ❌ In use")
        
        # Check processes
        processes = self.list_leona_processes()
        print(f"\nLEONA Processes: {len(processes)}")
        
        # Check system resources
        print(f"\nSystem Resources:")
        print(f"CPU Usage: {psutil.cpu_percent()}%")
        print(f"Memory: {psutil.virtual_memory().percent}%")
        
    def main_menu(self):
        """Main menu"""
        self.print_banner()
        
        while True:
            print("\n" + "="*50)
            print("LEONA LAUNCHER MENU")
            print("="*50)
            print("1. Launch LEONA Advanced (with AI)")
            print("2. Launch LEONA JARVIS (basic)")
            print("3. Manage running processes")
            print("4. Status check")
            print("5. Quick launch (auto-select port)")
            print("6. Exit")
            
            choice = input("\nSelect option (1-6): ").strip()
            
            if choice == "1":
                self.launch_leona("advanced")
            elif choice == "2":
                self.launch_leona("jarvis")
            elif choice == "3":
                self.manage_processes()
            elif choice == "4":
                self.status_check()
            elif choice == "5":
                # Quick launch - automatically handle port
                port = self.find_available_port()
                if port:
                    print(f"Quick launching on port {port}...")
                    self.launch_leona("advanced")
                else:
                    print("No ports available")
            elif choice == "6":
                print("\n👋 Goodbye!")
                break
            else:
                print("Invalid option")

# ============================================
# QUICK FIX SCRIPT
# ============================================

def quick_fix():
    """Quick fix for port issues"""
    print("\n🔧 LEONA Quick Fix")
    print("-" * 40)
    
    # Kill all Python processes on port 8000
    for proc in psutil.process_iter():
        try:
            for conn in proc.connections():
                if conn.laddr.port == 8000:
                    print(f"Found {proc.name()} on port 8000")
                    proc.terminate()
                    print("✅ Terminated")
                    time.sleep(2)
                    break
        except:
            continue
    
    print("\n✅ Port 8000 should be free now")
    print("You can now run: python leona_advanced.py")

# ============================================
# WINDOWS SPECIFIC PORT KILLER
# ============================================

def kill_port_windows(port):
    """Kill process on port (Windows specific)"""
    try:
        # Find PID using netstat
        result = subprocess.run(
            f'netstat -ano | findstr :{port}',
            shell=True,
            capture_output=True,
            text=True
        )
        
        lines = result.stdout.strip().split('\n')
        for line in lines:
            if f':{port}' in line and 'LISTENING' in line:
                parts = line.split()
                pid = parts[-1]
                
                # Kill the process
                subprocess.run(f'taskkill /F /PID {pid}', shell=True)
                print(f"✅ Killed process {pid} on port {port}")
                return True
    except Exception as e:
        print(f"Error: {e}")
    return False

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "fix":
            quick_fix()
        elif sys.argv[1] == "kill" and len(sys.argv) > 2:
            port = int(sys.argv[2])
            kill_port_windows(port)
        else:
            print("Usage:")
            print("  python leona_launcher.py       - Open menu")
            print("  python leona_launcher.py fix   - Quick fix port 8000")
            print("  python leona_launcher.py kill 8000  - Kill specific port")
    else:
        launcher = LeonaLauncher()
        launcher.main_menu()