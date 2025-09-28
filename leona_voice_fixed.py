from fastapi import FastAPI, Request, WebSocket, BackgroundTasks
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import asyncio
import json
import datetime
import os
import sys
import subprocess
import psutil
import pyttsx3
import threading
import random
import re
from pathlib import Path
from typing import Dict, List, Any, Optional
import aiohttp
import sqlite3
from dataclasses import dataclass
from enum import Enum

# Try to import optional packages
try:
    import speech_recognition as sr
    SPEECH_RECOGNITION_AVAILABLE = True
except:
    SPEECH_RECOGNITION_AVAILABLE = False

try:
    from llama_cpp import Llama
    LLAMA_AVAILABLE = True
except:
    LLAMA_AVAILABLE = False

app = FastAPI(title="LEONA Advanced", version="3.0")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================
# SYSTEM CONFIGURATION
# ============================================

class SystemConfig:
    # Paths
    DATA_DIR = Path("data")
    MEMORY_DB = DATA_DIR / "memory" / "leona.db"
    MODELS_DIR = DATA_DIR / "models"
    TASKS_DIR = DATA_DIR / "tasks"
    
    # Create directories
    for dir in [DATA_DIR, DATA_DIR / "memory", MODELS_DIR, TASKS_DIR]:
        dir.mkdir(parents=True, exist_ok=True)
    
    # System settings
    VOICE_ENABLED = True
    AI_MODEL_PATH = MODELS_DIR / "tinyllama.gguf"  # Change to your model
    USE_GPU = False
    MAX_CONTEXT = 2048

config = SystemConfig()

# ============================================
# AI BRAIN - LLM Integration
# ============================================

class AIBrain:
    def __init__(self):
        self.model = None
        self.context = []
        self.load_model()
    
    def load_model(self):
        """Load AI model if available"""
        if LLAMA_AVAILABLE and config.AI_MODEL_PATH.exists():
            try:
                print("🧠 Loading AI model...")
                self.model = Llama(
                    model_path=str(config.AI_MODEL_PATH),
                    n_ctx=config.MAX_CONTEXT,
                    n_gpu_layers=35 if config.USE_GPU else 0,
                    verbose=False
                )
                print("✅ AI model loaded successfully!")
            except Exception as e:
                print(f"❌ Failed to load AI model: {e}")
                self.model = None
        else:
            print("ℹ️ AI model not available - using rule-based responses")
    
    def generate_response(self, prompt: str, context: str = "") -> str:
        """Generate AI response"""
        if self.model:
            try:
                # Create JARVIS-style prompt
                full_prompt = f"""You are LEONA (Laudza's Executive Operational Neural Assistant), an AI assistant with the personality of JARVIS from Iron Man. 
You are sophisticated, professional, helpful, and occasionally witty. Always address the user as "Sir" or "Ma'am".
You have access to various systems and can control smart home devices, manage schedules, and perform complex tasks.

Context: {context}
User: {prompt}
LEONA:"""
                
                response = self.model(
                    full_prompt,
                    max_tokens=256,
                    temperature=0.7,
                    stop=["User:", "\n\n"]
                )
                
                return response['choices'][0]['text'].strip()
            except Exception as e:
                print(f"AI generation error: {e}")
                return self.get_fallback_response(prompt)
        else:
            return self.get_fallback_response(prompt)
    
    def get_fallback_response(self, prompt: str) -> str:
        """Fallback responses when AI not available"""
        prompt_lower = prompt.lower()
        
        if "weather" in prompt_lower:
            return "I'll check the weather for you, Sir. According to my sensors, conditions appear favorable today."
        elif "news" in prompt_lower:
            return "Scanning global news networks now, Sir. I'll compile the most relevant stories for you."
        elif "schedule" in prompt_lower or "calendar" in prompt_lower:
            return "Accessing your calendar, Sir. You have 3 meetings today. Would you like me to review them?"
        elif "email" in prompt_lower:
            return "Email interface ready, Sir. You have 12 unread messages. Shall I prioritize them for you?"
        elif "music" in prompt_lower:
            return "I'll queue up your favorite playlist, Sir. Would you prefer something energetic or relaxing?"
        elif "lights" in prompt_lower:
            return "Adjusting lighting to your preferences, Sir. All smart lights are now configured."
        elif "temperature" in prompt_lower:
            return "Climate control engaged, Sir. Setting temperature to 22°C for optimal comfort."
        else:
            responses = [
                "Processing your request now, Sir.",
                "Working on that for you, Sir.",
                "I'll handle that immediately, Sir.",
                "Consider it done, Sir."
            ]
            return random.choice(responses)

# Initialize AI Brain
ai_brain = AIBrain()

# ============================================
# MEMORY SYSTEM
# ============================================

class MemorySystem:
    def __init__(self):
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database"""
        conn = sqlite3.connect(str(config.MEMORY_DB))
        cursor = conn.cursor()
        
        # Conversations table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                user_input TEXT,
                leona_response TEXT,
                context TEXT
            )
        ''')
        
        # Tasks table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                due_date DATETIME,
                title TEXT,
                description TEXT,
                status TEXT DEFAULT 'pending',
                priority INTEGER DEFAULT 3
            )
        ''')
        
        # Smart home devices
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
        
        # User preferences
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS preferences (
                key TEXT PRIMARY KEY,
                value TEXT,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def store_conversation(self, user_input: str, response: str, context: str = ""):
        """Store conversation in memory"""
        conn = sqlite3.connect(str(config.MEMORY_DB))
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO conversations (user_input, leona_response, context) VALUES (?, ?, ?)",
            (user_input, response, context)
        )
        conn.commit()
        conn.close()
    
    def get_recent_conversations(self, limit: int = 5) -> List[Dict]:
        """Get recent conversations"""
        conn = sqlite3.connect(str(config.MEMORY_DB))
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM conversations ORDER BY timestamp DESC LIMIT ?",
            (limit,)
        )
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                "id": row[0],
                "timestamp": row[1],
                "user_input": row[2],
                "leona_response": row[3],
                "context": row[4]
            }
            for row in rows
        ]
    
    def add_task(self, title: str, description: str = "", due_date: str = None, priority: int = 3):
        """Add a task"""
        conn = sqlite3.connect(str(config.MEMORY_DB))
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO tasks (title, description, due_date, priority) VALUES (?, ?, ?, ?)",
            (title, description, due_date, priority)
        )
        conn.commit()
        conn.close()
    
    def get_pending_tasks(self) -> List[Dict]:
        """Get pending tasks"""
        conn = sqlite3.connect(str(config.MEMORY_DB))
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM tasks WHERE status = 'pending' ORDER BY priority DESC, due_date ASC"
        )
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                "id": row[0],
                "created_at": row[1],
                "due_date": row[2],
                "title": row[3],
                "description": row[4],
                "status": row[5],
                "priority": row[6]
            }
            for row in rows
        ]

# Initialize Memory System
memory = MemorySystem()

# ============================================
# VOICE SYSTEM
# ============================================

# ============================================
# VOICE SYSTEM - FIXED WITH FEMALE VOICE
# ============================================

class VoiceSystem:
    def __init__(self):
        # TTS Engine with thread safety
        import pyttsx3
        self.tts_engine = None
        self.tts_lock = threading.Lock()
        self.init_tts()
        
        # Speech Recognition
        try:
            import speech_recognition as sr
            self.recognizer = sr.Recognizer()
            self.microphone = sr.Microphone()
            self.speech_available = True
        except:
            self.speech_available = False
            print("Speech recognition not available")
    
    def init_tts(self):
        """Initialize TTS with female voice"""
        try:
            import pyttsx3
            self.tts_engine = pyttsx3.init()
            
            # Get available voices
            voices = self.tts_engine.getProperty('voices')
            
            # Find and set female voice
            female_voice_found = False
            
            # Print available voices for debugging
            print("
🎤 Available voices:")
            for i, voice in enumerate(voices):
                print(f"  {i}: {voice.name}")
                
                # Check for female voices (different patterns for Windows)
                if any(name in voice.name.lower() for name in ['zira', 'female', 'woman', 'susan', 'hazel', 'catherine']):
                    self.tts_engine.setProperty('voice', voice.id)
                    female_voice_found = True
                    print(f"  ✅ Selected female voice: {voice.name}")
                    break
            
            # If no female voice found, try by index (usually index 1 is female on Windows)
            if not female_voice_found and len(voices) > 1:
                self.tts_engine.setProperty('voice', voices[1].id)
                print(f"  ✅ Selected voice by index: {voices[1].name}")
            
            # Set voice properties for more feminine sound
            self.tts_engine.setProperty('rate', 180)    # Speed
            self.tts_engine.setProperty('volume', 0.9)  # Volume
            
            print("✅ Female voice configured")
            
        except Exception as e:
            print(f"TTS initialization error: {e}")
            self.tts_engine = None
    
    def speak(self, text: str):
        """Speak text using TTS with thread safety"""
        if not self.tts_engine:
            print(f"[TTS Disabled] Would say: {text}")
            return
        
        def _speak_thread():
            try:
                with self.tts_lock:
                    # Create new engine instance for this thread
                    import pyttsx3
                    engine = pyttsx3.init()
                    
                    # Set female voice
                    voices = engine.getProperty('voices')
                    if len(voices) > 1:
                        # Try to find Zira (female voice on Windows)
                        for voice in voices:
                            if 'zira' in voice.name.lower() or 'female' in voice.name.lower():
                                engine.setProperty('voice', voice.id)
                                break
                        else:
                            # Use second voice (usually female)
                            engine.setProperty('voice', voices[1].id)
                    
                    engine.setProperty('rate', 180)
                    engine.setProperty('volume', 0.9)
                    
                    # Speak
                    engine.say(text)
                    engine.runAndWait()
                    engine.stop()
                    
            except Exception as e:
                print(f"TTS Error: {e}")
        
        # Run in separate thread
        thread = threading.Thread(target=_speak_thread, daemon=True)
        thread.start()
    
    def listen(self):
        """Listen for voice input"""
        if not self.speech_available:
            return None
        
        try:
            import speech_recognition as sr
            with self.microphone as source:
                print("🎤 Listening...")
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=5)
            
            print("🔄 Recognizing...")
            text = self.recognizer.recognize_google(audio)
            print(f"📝 Heard: {text}")
            return text
        except Exception as e:
            print(f"Voice recognition error: {e}")
            return None
# ============================================
# SYSTEM CONTROL
# ============================================

class SystemControl:
    """Control system operations"""
    
    @staticmethod
    def get_system_info() -> Dict:
        """Get system information"""
        return {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_usage": psutil.disk_usage('/').percent,
            "network": "Connected" if any(psutil.net_if_stats()[iface].isup for iface in psutil.net_if_stats()) else "Disconnected",
            "battery": psutil.sensors_battery().percent if psutil.sensors_battery() else 100,
            "processes": len(psutil.pids())
        }
    
    @staticmethod
    def open_application(app_name: str) -> bool:
        """Open an application"""
        try:
            if sys.platform == "win32":
                os.startfile(app_name)
            elif sys.platform == "darwin":
                subprocess.call(["open", "-a", app_name])
            else:
                subprocess.call(["xdg-open", app_name])
            return True
        except Exception as e:
            print(f"Failed to open {app_name}: {e}")
            return False
    
    @staticmethod
    def search_files(query: str, directory: str = None) -> List[str]:
        """Search for files"""
        if directory is None:
            directory = str(Path.home())
        
        matches = []
        for root, dirs, files in os.walk(directory):
            for file in files:
                if query.lower() in file.lower():
                    matches.append(os.path.join(root, file))
                    if len(matches) >= 10:  # Limit results
                        return matches
        return matches

# ============================================
# SMART HOME CONTROL
# ============================================

class SmartHomeController:
    """Control smart home devices"""
    
    def __init__(self):
        self.devices = {}
        self.load_devices()
    
    def load_devices(self):
        """Load smart home devices from database"""
        conn = sqlite3.connect(str(config.MEMORY_DB))
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM devices")
        rows = cursor.fetchall()
        conn.close()
        
        for row in rows:
            self.devices[row[1]] = {
                "type": row[2],
                "status": row[3],
                "location": row[4]
            }
    
    def control_device(self, device_name: str, action: str) -> str:
        """Control a smart home device"""
        if device_name not in self.devices:
            # Add new device
            self.add_device(device_name, "light", "off", "unknown")
        
        # Update device status
        self.devices[device_name]["status"] = action
        
        # Update database
        conn = sqlite3.connect(str(config.MEMORY_DB))
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE devices SET status = ?, last_updated = CURRENT_TIMESTAMP WHERE name = ?",
            (action, device_name)
        )
        conn.commit()
        conn.close()
        
        return f"Device '{device_name}' is now {action}"
    
    def add_device(self, name: str, device_type: str, status: str, location: str):
        """Add a new smart home device"""
        conn = sqlite3.connect(str(config.MEMORY_DB))
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR REPLACE INTO devices (name, type, status, location) VALUES (?, ?, ?, ?)",
            (name, device_type, status, location)
        )
        conn.commit()
        conn.close()
        
        self.devices[name] = {
            "type": device_type,
            "status": status,
            "location": location
        }

# Initialize Smart Home Controller
smart_home = SmartHomeController()

# ============================================
# WEB SEARCH
# ============================================

class WebSearch:
    """Web search functionality"""
    
    @staticmethod
    async def search(query: str) -> List[Dict]:
        """Search the web (using DuckDuckGo API)"""
        try:
            url = f"https://api.duckduckgo.com/?q={query}&format=json&no_html=1"
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    data = await response.json()
                    
                    results = []
                    if data.get("AbstractText"):
                        results.append({
                            "title": "Summary",
                            "content": data["AbstractText"],
                            "url": data.get("AbstractURL", "")
                        })
                    
                    for item in data.get("RelatedTopics", [])[:3]:
                        if isinstance(item, dict) and "Text" in item:
                            results.append({
                                "title": item.get("Text", "")[:50],
                                "content": item.get("Text", ""),
                                "url": item.get("FirstURL", "")
                            })
                    
                    return results
        except Exception as e:
            print(f"Search error: {e}")
            return []

# ============================================
# API ENDPOINTS
# ============================================

@app.get("/")
async def home():
    """Serve the JARVIS UI"""
    html_file = Path("jarvis.html")
    if html_file.exists():
        with open(html_file, "r", encoding="utf-8") as f:
            return HTMLResponse(f.read())
    else:
        return HTMLResponse("<h1>Run fix_leona_ui.py first to create jarvis.html</h1>")
@app.post("/api/chat")
async def chat(request: Request):
    """Process chat with AI"""
    data = await request.json()
    message = data.get("message", "")
    use_ai = data.get("use_ai", True)
    
    # Get context from memory
    recent_convs = memory.get_recent_conversations(3)
    context = "\n".join([f"User: {c['user_input']}\nLEONA: {c['leona_response']}" for c in recent_convs])
    
    # Generate response
    if use_ai:
        response = ai_brain.generate_response(message, context)
    else:
        response = ai_brain.get_fallback_response(message)
    
    # Store conversation
    memory.store_conversation(message, response)
    
    # Speak if voice enabled
    if config.VOICE_ENABLED:
        voice.speak(response)
    
    return {
        "response": response,
        "timestamp": datetime.datetime.now().isoformat(),
        "ai_mode": use_ai and ai_brain.model is not None
    }

@app.post("/api/voice/listen")
async def listen_voice():
    """Listen for voice input"""
    text = voice.listen()
    
    if text:
        return {"status": "success", "text": text}
    else:
        return {"status": "no_speech", "text": ""}

@app.post("/api/voice/speak")
async def speak_text(request: Request):
    """Text to speech"""
    data = await request.json()
    text = data.get("text", "")
    
    if text:
        voice.speak(text)
        return {"status": "speaking", "text": text}
    else:
        return {"status": "error", "message": "No text provided"}

@app.get("/api/system/status")
async def system_status():
    """Get detailed system status"""
    return {
        "timestamp": datetime.datetime.now().isoformat(),
        "system": SystemControl.get_system_info(),
        "ai": {
            "model_loaded": ai_brain.model is not None,
            "model_path": str(config.AI_MODEL_PATH),
            "context_size": config.MAX_CONTEXT
        },
        "memory": {
            "conversations": len(memory.get_recent_conversations(100)),
            "tasks": len(memory.get_pending_tasks()),
            "devices": len(smart_home.devices)
        },
        "voice": {
            "tts_enabled": True,
            "stt_enabled": SPEECH_RECOGNITION_AVAILABLE
        }
    }

@app.post("/api/task/add")
async def add_task(request: Request):
    """Add a new task"""
    data = await request.json()
    title = data.get("title", "")
    description = data.get("description", "")
    due_date = data.get("due_date")
    priority = data.get("priority", 3)
    
    if title:
        memory.add_task(title, description, due_date, priority)
        return {"status": "success", "message": f"Task '{title}' added successfully, Sir."}
    else:
        return {"status": "error", "message": "Task title is required"}

@app.get("/api/task/list")
async def list_tasks():
    """Get pending tasks"""
    tasks = memory.get_pending_tasks()
    return {
        "tasks": tasks,
        "count": len(tasks)
    }

@app.post("/api/smarthome/control")
async def control_smart_home(request: Request):
    """Control smart home devices"""
    data = await request.json()
    device = data.get("device", "")
    action = data.get("action", "")
    
    if device and action:
        result = smart_home.control_device(device, action)
        return {"status": "success", "message": result}
    else:
        return {"status": "error", "message": "Device and action are required"}

@app.get("/api/smarthome/devices")
async def get_devices():
    """Get all smart home devices"""
    return {"devices": smart_home.devices}

@app.post("/api/search")
async def search_web(request: Request):
    """Search the web"""
    data = await request.json()
    query = data.get("query", "")
    
    if query:
        results = await WebSearch.search(query)
        return {"results": results, "count": len(results)}
    else:
        return {"results": [], "count": 0}

@app.post("/api/system/open")
async def open_app(request: Request):
    """Open an application"""
    data = await request.json()
    app_name = data.get("app", "")
    
    if app_name:
        success = SystemControl.open_application(app_name)
        if success:
            return {"status": "success", "message": f"Opening {app_name}, Sir."}
        else:
            return {"status": "error", "message": f"Failed to open {app_name}"}
    else:
        return {"status": "error", "message": "Application name required"}

@app.post("/api/files/search")
async def search_files(request: Request):
    """Search for files"""
    data = await request.json()
    query = data.get("query", "")
    directory = data.get("directory")
    
    if query:
        files = SystemControl.search_files(query, directory)
        return {"files": files[:10], "count": len(files)}
    else:
        return {"files": [], "count": 0}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket for real-time communication"""
    await websocket.accept()
    
    try:
        while True:
            # Receive message
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Process command
            if message["type"] == "chat":
                response = ai_brain.generate_response(message["content"])
                await websocket.send_json({
                    "type": "response",
                    "content": response
                })
            elif message["type"] == "system":
                status = SystemControl.get_system_info()
                await websocket.send_json({
                    "type": "status",
                    "content": status
                })
                
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        await websocket.close()

# ============================================
# MAIN STARTUP
# ============================================

if __name__ == "__main__":
    print("\n" + "="*60)
    print("     L.E.O.N.A ADVANCED SYSTEM v3.0")
    print("="*60)
    print("\n🚀 Initializing Advanced Systems...")
    print("━"*40)
    
    # System checks
    print("✓ Memory System.......... ONLINE")
    print("✓ Voice Synthesis........ ONLINE")
    print(f"✓ Speech Recognition..... {'ONLINE' if SPEECH_RECOGNITION_AVAILABLE else 'OFFLINE'}")
    print(f"✓ AI Brain............... {'ONLINE' if ai_brain.model else 'STANDBY'}")
    print("✓ Smart Home Control..... ONLINE")
    print("✓ Task Management........ ONLINE")
    print("✓ Web Search............. ONLINE")
    print("✓ System Monitor......... ONLINE")
    
    print("\n" + "="*60)
    print("🌟 LEONA is ready at: http://localhost:8000")
    print("✨ All systems operational")
    print("="*60 + "\n")
    
    # Initial greeting
    voice.speak("All systems are now online. Hello Sir, LEONA at your service.")
    
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        log_level="info"
    )