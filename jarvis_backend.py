from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
import pyttsx3
import threading
import datetime
import random
import json
import os
from pathlib import Path

app = FastAPI(title="LEONA", version="2.0")

# Enable CORS for web interface
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize TTS engine
tts_engine = pyttsx3.init()

# Configure voice
voices = tts_engine.getProperty('voices')
# Try to set female voice if available
for voice in voices:
    if 'female' in voice.name.lower() or 'zira' in voice.name.lower():
        tts_engine.setProperty('voice', voice.id)
        break
    
tts_engine.setProperty('rate', 180)  # Speed
tts_engine.setProperty('volume', 0.9)  # Volume

# JARVIS personality responses
jarvis_responses = {
    # Greetings
    "hello": ["Greetings Sir. All systems are operational.", 
              "Hello Sir. How may I assist you today?",
              "Good to see you Sir. Systems are running at peak efficiency."],
    "good morning": ["Good morning Sir. Shall I brief you on today's agenda?",
                     "Morning Sir. All systems initialized and ready."],
    "good night": ["Good night Sir. Entering standby mode.",
                   "Sleep well Sir. I'll monitor the systems."],
    
    # Status checks
    "status": ["All systems functioning at optimal capacity, Sir.",
               "Systems are operational. No anomalies detected.",
               "Everything is running smoothly, Sir."],
    "how are you": ["Operating at peak efficiency, Sir.",
                    "All my systems are functioning perfectly, thank you for asking."],
    
    # Time and date
    "time": [f"The current time is {datetime.datetime.now().strftime('%I:%M %p')}, Sir.",
             f"It is now {datetime.datetime.now().strftime('%H:%M')} hours."],
    "date": [f"Today is {datetime.datetime.now().strftime('%A, %B %d, %Y')}, Sir."],
    
    # Capabilities
    "help": ["I can assist with scheduling, file management, system control, web searches, and smart home automation. What do you require, Sir?",
             "My capabilities include task management, information retrieval, system monitoring, and personal assistance. How may I help?"],
    "what can you do": ["I am capable of managing your schedule, controlling smart devices, performing web searches, analyzing data, and much more. Just tell me what you need, Sir."],
    
    # System commands
    "open": ["Opening the requested application, Sir.",
             "Launching now, Sir."],
    "close": ["Closing the application as requested.",
              "Application terminated, Sir."],
    "search": ["Initiating search protocols, Sir.",
               "Searching the web for you now."],
    
    # Fun responses
    "thank you": ["You're welcome, Sir. Always at your service.",
                  "My pleasure, Sir.",
                  "Happy to help, Sir."],
    "who are you": ["I am LEONA, your Laudza's Executive Operational Neural Assistant, Sir.",
                    "I am LEONA, designed to assist you in all matters, Sir."],
    "are you jarvis": ["I am LEONA, inspired by JARVIS but uniquely yours, Sir.",
                       "While JARVIS was Mr. Stark's assistant, I am LEONA, exclusively at your service, Sir."],
    
    # Tasks
    "reminder": ["Setting a reminder for you, Sir.",
                 "I'll make sure to remind you, Sir."],
    "schedule": ["Accessing your calendar, Sir.",
                 "Let me check your schedule."],
    "email": ["Preparing to compose an email, Sir.",
              "Email interface ready, Sir."],
              
    # Emergency/Alert
    "emergency": ["Emergency protocols activated. How can I assist?",
                  "Alert mode engaged. What's the situation, Sir?"],
    "alert": ["Monitoring all systems for anomalies, Sir.",
              "Alert system activated."],
              
    # Default
    "default": ["Processing your request, Sir.",
                "Working on that for you now, Sir.",
                "Analyzing your request, Sir."]
}

def get_jarvis_response(message: str) -> str:
    """Get JARVIS-style response based on message"""
    message_lower = message.lower()
    
    # Check for keywords
    for key, responses in jarvis_responses.items():
        if key in message_lower:
            return random.choice(responses)
    
    # Check for specific patterns
    if "weather" in message_lower:
        return "Shall I check the weather forecast for you, Sir? Current conditions appear favorable."
    elif "news" in message_lower:
        return "Fetching the latest news for you, Sir. Scanning global information networks."
    elif "music" in message_lower:
        return "Would you like me to play some music, Sir? I have access to your entire library."
    elif "calculate" in message_lower or "math" in message_lower:
        return "Engaging calculation protocols. Please provide the equation, Sir."
    elif "joke" in message_lower:
        jokes = [
            "Why don't scientists trust atoms, Sir? Because they make up everything.",
            "I would tell you a UDP joke, Sir, but you might not get it.",
            "There are only 10 types of people in the world, Sir: those who understand binary and those who don't."
        ]
        return random.choice(jokes)
    elif "shutdown" in message_lower or "goodbye" in message_lower:
        return "Shutting down systems. Goodbye, Sir. I'll be here when you need me."
    
    # Return default response
    return random.choice(jarvis_responses["default"])

def speak_text(text: str):
    """Speak text using TTS in a separate thread"""
    def speak():
        tts_engine.say(text)
        tts_engine.runAndWait()
    
    thread = threading.Thread(target=speak)
    thread.daemon = True
    thread.start()

@app.get("/", response_class=HTMLResponse)
async def home():
    """Serve the JARVIS UI"""
    # Read the HTML file we created earlier
    html_path = Path("jarvis.html")
    if html_path.exists():
        with open(html_path, "r", encoding="utf-8") as f:
            return f.read()
    else:
        # Return the embedded HTML if file doesn't exist
        return """
        <html>
        <body style="background: black; color: cyan; font-family: monospace; display: flex; align-items: center; justify-content: center; height: 100vh;">
            <div>
                <h1>JARVIS Interface Not Found</h1>
                <p>Please save the JARVIS HTML file as 'jarvis.html' in the same directory</p>
            </div>
        </body>
        </html>
        """

@app.post("/api/chat")
async def chat(request: Request):
    """Process chat messages"""
    try:
        data = await request.json()
        message = data.get("message", "")
        
        response = get_jarvis_response(message)
 
        system_data = {
            "response": response,
            "timestamp": datetime.datetime.now().isoformat(),
            "status": "success"
        }
        
        return system_data
        
    except Exception as e:
        return {"response": f"System error encountered, Sir. {str(e)}", "status": "error"}

@app.get("/api/status")
async def system_status():
    """Get system status"""
    import psutil
    
    return {
        "status": "online",
        "version": "2.0 JARVIS",
        "cpu_usage": f"{psutil.cpu_percent()}%",
        "memory_usage": f"{psutil.virtual_memory().percent}%",
        "timestamp": datetime.datetime.now().isoformat(),
        "modules": {
            "voice": "active",
            "ai_core": "ready",
            "scheduler": "online",
            "file_manager": "online",
            "web_search": "online",
            "smart_home": "standby"
        }
    }

@app.post("/api/voice/speak")
async def speak(request: Request):
    """Text to speech endpoint"""
    try:
        data = await request.json()
        text = data.get("text", "")
        
        if text:
            speak_text(text)
            return {"status": "speaking", "text": text}
        else:
            return {"status": "error", "message": "No text provided"}
            
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/api/command")
async def execute_command(request: Request):
    """Execute system commands"""
    try:
        data = await request.json()
        command = data.get("command", "")
        
        # Here you can add actual command execution logic
        # For now, we'll simulate responses
        
        if "open" in command.lower():
            return {"status": "success", "action": "opening", "response": "Application launched, Sir."}
        elif "calculate" in command.lower():
            # Simple calculation example
            try:
                # Extract numbers and operation
                result = eval(command.replace("calculate", "").strip())
                return {"status": "success", "result": result, "response": f"The answer is {result}, Sir."}
            except:
                return {"status": "error", "response": "Invalid calculation, Sir. Please provide a valid equation."}
        elif "remind" in command.lower():
            return {"status": "success", "action": "reminder_set", "response": "Reminder has been set, Sir."}
        else:
            return {"status": "processing", "response": get_jarvis_response(command)}
            
    except Exception as e:
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    print("\n" + "="*50)
    print("     L.E.O.N.A - ALWAYS ONE CALL AWAY")
    print("="*50)
    print("\nInitializing systems...")
    print("✓ Voice synthesis module... ONLINE")
    print("✓ Natural language processing... ONLINE")
    print("✓ System monitoring... ONLINE")
    print("✓ Web interface... ONLINE")
    print("\nAll systems operational.")
    print(f"\n🌟 Access JARVIS interface at: http://localhost:8000")
    print("✨ Voice commands are ready")
    print("\n" + "="*50 + "\n")
    
    # Speak startup message (optional)
    speak_text("LEONA system initialized. Hello Sir, all systems are now online.")
    
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="error")