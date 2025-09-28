# ============================================
# FIXED LEONA WINDOWS SETUP
# File: quick_setup.py
# ============================================
"""
Fixed Windows setup for LEONA
Run: python quick_setup.py
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    print("""
    ╔════════════════════════════════════════════╗
    ║        LEONA Quick Setup (Windows)         ║
    ║      Laudza's Executive One Call Away      ║
    ╚════════════════════════════════════════════╝
    """)
    
    # Step 1: Create fixed requirements.txt
    print("📝 Creating fixed requirements.txt...")
    
    requirements = """# Core - Essential packages only
fastapi==0.104.1
uvicorn[standard]==0.24.0
pyyaml==6.0.1
aiofiles==23.2.1

# Optional - Add these later if needed
# llama-cpp-python==0.2.20
# pyttsx3==2.90
# SpeechRecognition==3.10.0
"""
    
    with open("requirements_minimal.txt", "w") as f:
        f.write(requirements)
    
    print("   ✅ Created requirements_minimal.txt")
    
    # Step 2: Install minimal requirements
    print("\n📦 Installing essential packages...")
    python_exe = sys.executable
    
    try:
        subprocess.run([python_exe, "-m", "pip", "install", "--upgrade", "pip"], check=True)
        subprocess.run([python_exe, "-m", "pip", "install", "-r", "requirements_minimal.txt"], check=True)
        print("   ✅ Essential packages installed")
    except:
        print("   ⚠️ Some packages failed. Continuing...")
    
    # Step 3: Create directories
    print("\n📁 Creating directories...")
    for dir_path in ["backend", "frontend", "data/memory", "data/models", "scripts"]:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
    print("   ✅ Directories created")
    
    # Step 4: Create simple LEONA server
    print("\n🔧 Creating LEONA server...")
    
    main_py = '''"""
LEONA - Minimal Server for Windows
"""
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
import uvicorn

app = FastAPI(title="LEONA", version="1.0.0")

@app.get("/", response_class=HTMLResponse)
async def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>LEONA - Always One Call Away</title>
        <meta charset="UTF-8">
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: 'Segoe UI', system-ui, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                min-height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
            }
            .container {
                text-align: center;
                padding: 3rem;
                background: rgba(255,255,255,0.1);
                border-radius: 30px;
                backdrop-filter: blur(10px);
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                max-width: 600px;
                animation: fadeIn 1s ease-out;
            }
            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(20px); }
                to { opacity: 1; transform: translateY(0); }
            }
            h1 {
                font-size: 4rem;
                margin-bottom: 0.5rem;
                text-shadow: 2px 2px 10px rgba(0,0,0,0.3);
                background: linear-gradient(to right, #fff, #e0e0ff);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            }
            .tagline {
                font-size: 1.3rem;
                opacity: 0.9;
                margin-bottom: 2rem;
            }
            .status {
                display: inline-block;
                padding: 0.8rem 2rem;
                background: rgba(0,255,100,0.2);
                border: 1px solid rgba(0,255,100,0.4);
                border-radius: 50px;
                margin: 1rem 0;
                animation: pulse 2s infinite;
            }
            @keyframes pulse {
                0%, 100% { transform: scale(1); }
                50% { transform: scale(1.02); }
            }
            .chat-container {
                margin-top: 2rem;
                padding: 1.5rem;
                background: rgba(255,255,255,0.05);
                border-radius: 20px;
            }
            #chat-input {
                width: 100%;
                padding: 1rem;
                border: none;
                border-radius: 50px;
                background: rgba(255,255,255,0.2);
                color: white;
                font-size: 1rem;
                outline: none;
                transition: all 0.3s;
            }
            #chat-input:focus {
                background: rgba(255,255,255,0.3);
                transform: translateY(-2px);
            }
            #chat-input::placeholder {
                color: rgba(255,255,255,0.6);
            }
            #response {
                margin-top: 1.5rem;
                padding: 1rem;
                background: rgba(255,255,255,0.1);
                border-radius: 15px;
                min-height: 60px;
                display: none;
                animation: slideIn 0.3s ease-out;
            }
            @keyframes slideIn {
                from { opacity: 0; transform: translateX(-20px); }
                to { opacity: 1; transform: translateX(0); }
            }
            .features {
                display: flex;
                gap: 1rem;
                margin-top: 2rem;
                flex-wrap: wrap;
                justify-content: center;
            }
            .feature {
                padding: 0.5rem 1rem;
                background: rgba(255,255,255,0.1);
                border-radius: 20px;
                font-size: 0.9rem;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>LEONA</h1>
            <p class="tagline">Always One Call Away ✨</p>
            <div class="status">🟢 System Online</div>
            
            <div class="chat-container">
                <input type="text" id="chat-input" placeholder="Ask me anything..." 
                       onkeypress="if(event.key==='Enter') sendMessage()">
                <div id="response"></div>
            </div>
            
            <div class="features">
                <span class="feature">🧠 AI Assistant</span>
                <span class="feature">🎤 Voice Ready</span>
                <span class="feature">📅 Scheduler</span>
                <span class="feature">📁 File Manager</span>
                <span class="feature">🏠 Smart Home</span>
            </div>
        </div>
        
        <script>
            async function sendMessage() {
                const input = document.getElementById('chat-input');
                const responseDiv = document.getElementById('response');
                const message = input.value.trim();
                
                if (!message) return;
                
                responseDiv.style.display = 'block';
                responseDiv.innerHTML = '💭 Thinking...';
                
                try {
                    const response = await fetch('/api/chat', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({message: message})
                    });
                    const data = await response.json();
                    responseDiv.innerHTML = '✨ ' + data.response;
                } catch (error) {
                    responseDiv.innerHTML = '❌ Connection error. Please try again.';
                }
                
                input.value = '';
            }
            
            // Add welcome message
            setTimeout(() => {
                document.getElementById('response').style.display = 'block';
                document.getElementById('response').innerHTML = 
                    "👋 Hello! I'm LEONA, your AI assistant. I'm currently running in basic mode. " +
                    "To unlock my full capabilities, install an AI model using the setup instructions.";
            }, 1000);
        </script>
    </body>
    </html>
    """

@app.post("/api/chat")
async def chat(request: Request):
    try:
        data = await request.json()
        message = data.get("message", "")
        
        # Basic responses without AI model
        responses = {
            "hello": "Hello! I'm LEONA, your executive assistant. How can I help you today?",
            "help": "I can help with scheduling, file management, web searches, and more. Install an AI model to unlock my full capabilities!",
            "time": f"The current time is: {__import__('datetime').datetime.now().strftime('%I:%M %p')}",
            "date": f"Today is: {__import__('datetime').datetime.now().strftime('%A, %B %d, %Y')}",
        }
        
        # Check for keywords
        message_lower = message.lower()
        for key, response in responses.items():
            if key in message_lower:
                return {"response": response}
        
        # Default response
        return {
            "response": f"I heard you say: '{message}'. Once you install an AI model, I'll be able to provide much more intelligent responses. For now, try asking about the time, date, or say hello!"
        }
    except Exception as e:
        return {"response": f"Error processing request: {str(e)}"}

@app.get("/api/status")
async def status():
    return {
        "status": "online",
        "version": "1.0.0",
        "model": "No model loaded (basic mode)",
        "tagline": "Always One Call Away"
    }

if __name__ == "__main__":
    print("\\n🌟 Starting LEONA on http://localhost:8000")
    print("✨ Always One Call Away\\n")
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="error")
'''
    
    with open("backend/main.py", "w", encoding='utf-8') as f:
        f.write(main_py)
    
    print("   ✅ LEONA server created")
    
    # Step 5: Create simple start script
    print("\n📜 Creating launch script...")
    
    start_script = f'''@echo off
echo.
echo ======================================
echo         Starting LEONA
echo     Always One Call Away
echo ======================================
echo.

"{sys.executable}" backend\\main.py
pause
'''
    
    with open("start_leona.bat", "w") as f:
        f.write(start_script)
    
    print("   ✅ Created start_leona.bat")
    
    # Step 6: Create PowerShell version
    ps_script = f'''Write-Host ""
Write-Host "======================================" -ForegroundColor Cyan
Write-Host "         Starting LEONA" -ForegroundColor White
Write-Host "     Always One Call Away" -ForegroundColor Gray  
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

& "{sys.executable}" backend\\main.py
'''
    
    with open("start_leona.ps1", "w") as f:
        f.write(ps_script)
    
    print("   ✅ Created start_leona.ps1")
    
    # Success!
    print("""
    ╔════════════════════════════════════════════╗
    ║         ✅ LEONA Setup Complete!           ║
    ╚════════════════════════════════════════════╝
    
    🚀 To start LEONA, run ONE of these:
    
       1. Double-click: start_leona.bat
       2. PowerShell:   .\\start_leona.ps1
       3. Direct:       python backend\\main.py
    
    🌐 Then open your browser to:
       http://localhost:8000
    
    💡 Next Steps:
       - Install AI model for full capabilities
       - Add more features as needed
    
    ✨ LEONA - Always One Call Away
    """)

if __name__ == "__main__":
    main()