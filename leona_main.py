"""
LEONA - API Version (DeepSeek/Gemini)
Fast, reliable, no local model needed
"""

import os
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(title="LEONA", version="2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# Initialize AI providers
AI_PROVIDER = os.getenv("AI_PROVIDER", "gemini")
ai_ready = False

print("\n" + "="*60)
print("        LEONA - API Version")
print("="*60 + "\n")

# Setup DeepSeek
deepseek_client = None
if AI_PROVIDER == "deepseek":
    try:
        from openai import OpenAI
        api_key = os.getenv("DEEPSEEK_API_KEY")
        if api_key and api_key != "your_deepseek_key_here":
            deepseek_client = OpenAI(
                api_key=api_key,
                base_url="https://api.deepseek.com"
            )
            ai_ready = True
            print("✅ DeepSeek API connected")
            print("   Model: deepseek-chat")
        else:
            print("⚠️  DeepSeek API key not set")
    except Exception as e:
        print(f"⚠️  DeepSeek error: {e}")

# Setup Gemini
gemini_model = None
if AI_PROVIDER == "gemini":
    try:
        import google.generativeai as genai
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key and api_key != "your_gemini_key_here":
            genai.configure(api_key=api_key)
            gemini_model = genai.GenerativeModel('gemini-2.0-flash-exp')
            ai_ready = True
            print("✅ Gemini API connected")
            print("   Model: gemini-pro")
        else:
            print("⚠️  Gemini API key not set")
    except Exception as e:
        print(f"⚠️  Gemini error: {e}")

if not ai_ready:
    print("\n⚠️  No API configured. Please set API keys in .env file\n")

@app.get("/", response_class=HTMLResponse)
async def home():
    return """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LEONA - Always One Call Away</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', system-ui, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }
        .header {
            text-align: center;
            padding: 40px 20px;
            background: rgba(0,0,0,0.2);
        }
        h1 {
            font-size: 4em;
            margin-bottom: 10px;
            text-shadow: 0 0 20px rgba(255,255,255,0.3);
        }
        .status {
            display: inline-block;
            padding: 10px 20px;
            background: rgba(0,255,100,0.2);
            border: 1px solid rgba(0,255,100,0.5);
            border-radius: 20px;
            margin-top: 20px;
        }
        .chat-container {
            flex: 1;
            max-width: 1000px;
            width: 100%;
            margin: 0 auto;
            padding: 20px;
            display: flex;
            flex-direction: column;
        }
        #messages {
            flex: 1;
            background: rgba(0,0,0,0.2);
            border-radius: 20px;
            padding: 20px;
            margin-bottom: 20px;
            overflow-y: auto;
            min-height: 400px;
        }
        .message {
            margin: 15px 0;
            padding: 15px 20px;
            border-radius: 15px;
            animation: fadeIn 0.3s;
            line-height: 1.6;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .user-message {
            background: rgba(102, 126, 234, 0.4);
            margin-left: 20%;
            border-left: 4px solid #667eea;
        }
        .leona-message {
            background: rgba(236, 72, 153, 0.4);
            margin-right: 20%;
            border-left: 4px solid #ec4899;
        }
        .input-area {
            display: flex;
            gap: 10px;
            background: rgba(0,0,0,0.2);
            padding: 20px;
            border-radius: 20px;
        }
        input {
            flex: 1;
            padding: 15px 20px;
            border: none;
            border-radius: 10px;
            background: rgba(255,255,255,0.2);
            color: white;
            font-size: 16px;
        }
        input::placeholder { color: rgba(255,255,255,0.7); }
        input:focus { outline: none; background: rgba(255,255,255,0.3); }
        button {
            padding: 15px 30px;
            border: none;
            border-radius: 10px;
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            font-weight: bold;
            cursor: pointer;
            transition: transform 0.2s;
        }
        button:hover { transform: scale(1.05); }
        button:disabled { opacity: 0.5; cursor: not-allowed; }
    </style>
</head>
<body>
    <div class="header">
        <h1>L.E.O.N.A</h1>
        <p style="font-size: 1.2em; opacity: 0.9;">Always One Call Away</p>
        <div class="status" id="status">Loading...</div>
    </div>
    
    <div class="chat-container">
        <div id="messages">
            <div class="message leona-message">
                <strong>LEONA:</strong> Hello! I'm LEONA, your AI assistant. How can I help you today?
            </div>
        </div>
        
        <div class="input-area">
            <input type="text" id="input" placeholder="Ask me anything..." 
                   onkeypress="if(event.key==='Enter') sendMessage()">
            <button onclick="sendMessage()" id="send-btn">Send</button>
        </div>
    </div>
    
    <script>
        async function sendMessage() {
            const input = document.getElementById('input');
            const messages = document.getElementById('messages');
            const sendBtn = document.getElementById('send-btn');
            const message = input.value.trim();
            
            if (!message) return;
            
            messages.innerHTML += `<div class="message user-message"><strong>You:</strong> ${message}</div>`;
            
            const thinkingDiv = document.createElement('div');
            thinkingDiv.className = 'message leona-message';
            thinkingDiv.innerHTML = '<strong>LEONA:</strong> <em>Thinking...</em>';
            thinkingDiv.id = 'thinking';
            messages.appendChild(thinkingDiv);
            
            input.value = '';
            sendBtn.disabled = true;
            messages.scrollTop = messages.scrollHeight;
            
            try {
                const response = await fetch('/api/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({message})
                });
                
                const data = await response.json();
                document.getElementById('thinking').remove();
                messages.innerHTML += `<div class="message leona-message"><strong>LEONA:</strong> ${data.response}</div>`;
                
            } catch (error) {
                document.getElementById('thinking').remove();
                messages.innerHTML += `<div class="message leona-message"><strong>Error:</strong> Connection failed</div>`;
            }
            
            sendBtn.disabled = false;
            messages.scrollTop = messages.scrollHeight;
        }
        
        async function checkStatus() {
            try {
                const response = await fetch('/api/status');
                const data = await response.json();
                document.getElementById('status').innerHTML = 
                    data.ai_ready ? `AI Ready (${data.provider})` : 'Setup Required';
            } catch (e) {}
        }
        
        checkStatus();
        document.getElementById('input').focus();
    </script>
</body>
</html>
    """

@app.post("/api/chat")
async def chat(request: Request):
    data = await request.json()
    message = data.get("message", "")
    
    if not ai_ready:
        return {"response": "API not configured. Please set API key in .env file", "status": "error"}
    
    try:
        # DeepSeek
        if AI_PROVIDER == "deepseek" and deepseek_client:
            response = deepseek_client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": "You are LEONA, an elegant and helpful AI assistant. Be concise, clear, and professional."},
                    {"role": "user", "content": message}
                ],
                max_tokens=512,
                temperature=0.7
            )
            answer = response.choices[0].message.content
        
        # Gemini
        elif AI_PROVIDER == "gemini" and gemini_model:
            prompt = f"""You are LEONA, an elegant AI assistant. Be helpful and concise.

User: {message}"""
            response = gemini_model.generate_content(prompt)
            answer = response.text
        
        else:
            answer = "AI provider not configured"
        
        return {"response": answer, "status": "success"}
        
    except Exception as e:
        return {"response": f"Error: {str(e)}", "status": "error"}

@app.get("/api/status")
async def status():
    return {
        "ai_ready": ai_ready,
        "provider": AI_PROVIDER
    }

if __name__ == "__main__":
    print("="*60)
    print("🌐 Server: http://localhost:8000")
    print("="*60 + "\n")
    
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="error")