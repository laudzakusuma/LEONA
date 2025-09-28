"""
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
    print("\n🌟 Starting LEONA on http://localhost:8000")
    print("✨ Always One Call Away\n")
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="error")
