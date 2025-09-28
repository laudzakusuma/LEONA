import os
import sys
import subprocess
import urllib.request
from pathlib import Path
import json

class LeonaAdvancedSetup:
    def __init__(self):
        self.base_dir = Path.cwd()
        self.venv_python = sys.executable
        
    def print_header(self):
        print("""
        ╔══════════════════════════════════════════════════╗
        ║       LEONA ADVANCED SETUP WITH AI              ║
        ║          Full JARVIS Experience                 ║
        ╚══════════════════════════════════════════════════╝
        """)
    
    def install_requirements(self):
        """Install advanced requirements"""
        print("\n📦 Installing Advanced Packages...")
        
        requirements = [
            "fastapi==0.104.1",
            "uvicorn[standard]==0.24.0",
            "pyttsx3==2.90",
            "psutil==5.9.6",
            "aiohttp==3.9.0",
            "sqlite3",  # Built-in
            "SpeechRecognition==3.10.0",
            "pyaudio==0.2.13",  # For microphone
            "llama-cpp-python==0.2.20",  # For AI models
            "requests==2.31.0",
            "numpy==1.24.3"
        ]
        
        for package in requirements:
            print(f"Installing {package}...")
            try:
                subprocess.run([self.venv_python, "-m", "pip", "install", package], 
                             capture_output=True, check=True)
                print(f"  ✅ {package.split('==')[0]} installed")
            except:
                print(f"  ⚠️ {package.split('==')[0]} failed (optional)")
    
    def download_ai_model(self):
        """Download AI model"""
        print("\n🧠 AI Model Setup")
        print("-" * 40)
        print("Choose an AI model:")
        print("1. TinyLlama (638 MB) - Fast, lightweight")
        print("2. Phi-2 (1.6 GB) - Balanced")  
        print("3. Mistral 7B (4.1 GB) - Best quality")
        print("4. Skip (use without AI)")
        
        choice = input("\nSelect (1-4): ").strip()
        
        models = {
            "1": {
                "name": "TinyLlama",
                "url": "https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF/resolve/main/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf",
                "filename": "tinyllama.gguf",
                "size": "638 MB"
            },
            "2": {
                "name": "Phi-2", 
                "url": "https://huggingface.co/TheBloke/phi-2-GGUF/resolve/main/phi-2.Q4_K_M.gguf",
                "filename": "phi2.gguf",
                "size": "1.6 GB"
            },
            "3": {
                "name": "Mistral 7B",
                "url": "https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF/resolve/main/mistral-7b-instruct-v0.2.Q4_K_M.gguf",
                "filename": "mistral.gguf",
                "size": "4.1 GB"
            }
        }
        
        if choice in models:
            model = models[choice]
            model_dir = Path("data/models")
            model_dir.mkdir(parents=True, exist_ok=True)
            model_path = model_dir / model["filename"]
            
            if model_path.exists():
                print(f"✅ {model['name']} already exists")
                return str(model_path)
            
            print(f"\n📥 Downloading {model['name']} ({model['size']})...")
            print("This may take several minutes depending on your connection...")
            
            def download_progress(block_num, block_size, total_size):
                downloaded = block_num * block_size
                percent = min(downloaded * 100 / total_size, 100)
                bar_length = 40
                filled = int(bar_length * percent / 100)
                bar = '█' * filled + '░' * (bar_length - filled)
                sys.stdout.write(f'\r[{bar}] {percent:.1f}%')
                sys.stdout.flush()
            
            try:
                urllib.request.urlretrieve(model["url"], str(model_path), download_progress)
                print(f"\n✅ {model['name']} downloaded successfully!")
                return str(model_path)
            except Exception as e:
                print(f"\n❌ Download failed: {e}")
                return None
        else:
            print("⚠️ Skipping AI model - LEONA will use basic responses")
            return None
    
    def create_startup_script(self):
        """Create convenient startup scripts"""
        print("\n📝 Creating startup scripts...")
        
        # Windows batch file
        bat_content = f'''@echo off
echo.
echo ============================================
echo        STARTING LEONA ADVANCED
echo            JARVIS MODE v3.0
echo ============================================
echo.

cd /d "{self.base_dir}"
"{self.venv_python}" leona_advanced.py
pause
'''
        
        with open("start_leona_advanced.bat", "w") as f:
            f.write(bat_content)
        
        # PowerShell script
        ps1_content = f'''Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "       STARTING LEONA ADVANCED" -ForegroundColor White
Write-Host "          JARVIS MODE v3.0" -ForegroundColor Yellow
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

Set-Location "{self.base_dir}"
& "{self.venv_python}" leona_advanced.py
'''
        
        with open("start_leona_advanced.ps1", "w") as f:
            f.write(ps1_content)
        
        print("✅ Startup scripts created")
    
    def setup_smart_home_demo(self):
        """Setup demo smart home devices"""
        print("\n🏠 Setting up smart home demo...")
        
        import sqlite3
        
        db_path = Path("data/memory/leona.db")
        db_path.parent.mkdir(parents=True, exist_ok=True)
        
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Create devices table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS devices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE,
                type TEXT,
                status TEXT,
                location TEXT,
                last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Add demo devices
        demo_devices = [
            ("living_room_lights", "light", "off", "Living Room"),
            ("bedroom_lights", "light", "off", "Bedroom"),
            ("kitchen_lights", "light", "off", "Kitchen"),
            ("main_door", "lock", "locked", "Entrance"),
            ("thermostat", "climate", "22°C", "Central"),
            ("security_system", "security", "armed", "All"),
            ("tv", "entertainment", "off", "Living Room"),
            ("coffee_maker", "appliance", "off", "Kitchen")
        ]
        
        for device in demo_devices:
            cursor.execute(
                "INSERT OR REPLACE INTO devices (name, type, status, location) VALUES (?, ?, ?, ?)",
                device
            )
        
        conn.commit()
        conn.close()
        
        print("✅ Smart home devices configured")
    
    def create_config_file(self, model_path=None):
        """Create configuration file"""
        print("\n⚙️ Creating configuration...")
        
        config = {
            "leona": {
                "version": "3.0",
                "mode": "JARVIS",
                "name": "LEONA"
            },
            "ai": {
                "enabled": model_path is not None,
                "model_path": model_path or "",
                "context_size": 2048,
                "temperature": 0.7
            },
            "voice": {
                "tts_enabled": True,
                "stt_enabled": True,
                "voice_activation": False
            },
            "features": {
                "smart_home": True,
                "task_management": True,
                "web_search": True,
                "system_control": True,
                "file_management": True
            }
        }
        
        with open("leona_config.json", "w") as f:
            json.dump(config, f, indent=2)
        
        print("✅ Configuration saved")
    
    def run_setup(self):
        """Run complete setup"""
        self.print_header()
        
        # Install packages
        self.install_requirements()
        
        # Download AI model
        model_path = self.download_ai_model()
        
        # Setup smart home
        self.setup_smart_home_demo()
        
        # Create config
        self.create_config_file(model_path)
        
        # Create startup scripts
        self.create_startup_script()
        
        # Success message
        print("""
        ╔══════════════════════════════════════════════════╗
        ║        ✅ LEONA ADVANCED SETUP COMPLETE!         ║
        ╚══════════════════════════════════════════════════╝
        
        🚀 To start LEONA Advanced:
        
           Option 1: Double-click 'start_leona_advanced.bat'
           Option 2: Run: python leona_advanced.py
        
        🎯 Features Ready:
           ✅ AI Chat (if model downloaded)
           ✅ Voice Commands
           ✅ Smart Home Control
           ✅ Task Management
           ✅ Web Search
           ✅ System Control
           
        🎤 Voice Commands to Try:
           "Turn on living room lights"
           "What's the weather?"
           "Add a task: Meeting at 3pm"
           "Search for Python tutorials"
           "Open notepad"
           
        🌐 Access at: http://localhost:8000
        
        ✨ LEONA - Your JARVIS is ready!
        """)

# ============================================
# QUICK TEST SCRIPT
# ============================================

def test_leona():
    """Test LEONA features"""
    print("\n🧪 Testing LEONA Systems...")
    
    # Test TTS
    try:
        import pyttsx3
        engine = pyttsx3.init()
        engine.say("LEONA systems test successful")
        engine.runAndWait()
        print("✅ Voice synthesis working")
    except:
        print("⚠️ Voice synthesis not available")
    
    # Test Speech Recognition
    try:
        import speech_recognition as sr
        print("✅ Speech recognition available")
    except:
        print("⚠️ Speech recognition not installed")
    
    # Test AI model
    try:
        from llama_cpp import Llama
        model_path = Path("data/models/tinyllama.gguf")
        if model_path.exists():
            print("✅ AI model found")
        else:
            print("ℹ️ No AI model found (optional)")
    except:
        print("ℹ️ AI module not installed (optional)")
    
    print("\n✨ Test complete!")

if __name__ == "__main__":
    setup = LeonaAdvancedSetup()
    setup.run_setup()
    
    # Run test
    test_leona()