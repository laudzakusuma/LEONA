#!/bin/bash

# LEONA Quick Start - Get running in 5 minutes
# Run: bash leona_quickstart.sh

set -e

echo "╔══════════════════════════════════════════╗"
echo "║       LEONA - Quick Start Installer      ║"
echo "║    Laudza's Executive One Call Away      ║"
echo "╚══════════════════════════════════════════╝"
echo ""

# Check Python version
if ! python3 --version | grep -E "3\.(9|1[0-9])" > /dev/null; then
    echo "❌ Python 3.9+ required. Please install Python 3.9 or higher."
    exit 1
fi

# Create project directory
PROJECT_DIR="$HOME/leona"
echo "📁 Creating LEONA in $PROJECT_DIR..."
mkdir -p "$PROJECT_DIR"
cd "$PROJECT_DIR"

# Create virtual environment
echo "🐍 Setting up Python environment..."
python3 -m venv venv
source venv/bin/activate

# Create minimal requirements.txt
cat > requirements.txt << 'EOF'
# Core
fastapi==0.104.1
uvicorn[standard]==0.24.0
websockets==12.0
aiosqlite==0.19.0
pydantic==2.5.0

# LLM - Using llama-cpp for efficiency
llama-cpp-python==0.2.20

# Voice
openai-whisper==20231117
TTS==0.20.2

# Utilities
python-dotenv==1.0.0
pyyaml==6.0.1
requests==2.31.0
EOF

echo "📦 Installing dependencies (this may take a few minutes)..."
pip install --upgrade pip
pip install -r requirements.txt

# Create directory structure
echo "🏗️ Creating project structure..."
mkdir -p backend/{core,agents,models,utils} frontend data/{memory,models} plugins scripts

# Create config.yaml
cat > config.yaml << 'EOF'
leona:
  name: "LEONA"
  tagline: "Always One Call Away"
  
llm:
  model_type: "llama_cpp"
  model_path: "data/models/model.gguf"
  
voice:
  whisper_model: "base"
  tts_model: "tts_models/en/ljspeech/tacotron2-DDC"
  
memory:
  db_path: "data/memory/leona.db"
  
server:
  host: "0.0.0.0"
  port: 8000
EOF

# Create simplified main.py
cat > backend/main.py << 'EOF'
from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
import asyncio
import yaml

# Load config
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

app = FastAPI(title="LEONA", version="1.0.0")

@app.get("/")
async def root():
    return HTMLResponse("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>LEONA</title>
        <style>
            body { 
                font-family: 'Segoe UI', system-ui, sans-serif; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white; 
                display: flex; 
                justify-content: center; 
                align-items: center; 
                height: 100vh; 
                margin: 0;
            }
            .container { 
                text-align: center; 
                padding: 40px;
                background: rgba(255,255,255,0.1);
                border-radius: 20px;
                backdrop-filter: blur(10px);
            }
            h1 { 
                font-size: 4em; 
                margin: 0;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            }
            .tagline { 
                font-size: 1.5em; 
                opacity: 0.9; 
                margin-top: 10px;
            }
            .status { 
                margin-top: 30px; 
                padding: 15px 30px; 
                background: rgba(0,255,0,0.2); 
                border-radius: 30px;
                display: inline-block;
            }
            .instructions {
                margin-top: 40px;
                padding: 20px;
                background: rgba(0,0,0,0.2);
                border-radius: 10px;
                text-align: left;
                max-width: 600px;
                margin-left: auto;
                margin-right: auto;
            }
            code {
                background: rgba(0,0,0,0.3);
                padding: 2px 6px;
                border-radius: 4px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>LEONA</h1>
            <p class="tagline">Laudza's Executive One Call Away</p>
            <div class="status">✨ System Online</div>
            
            <div class="instructions">
                <h3>🚀 Getting Started</h3>
                <p>Welcome to LEONA! Your AI assistant is ready.</p>
                
                <h4>Next Steps:</h4>
                <ol>
                    <li>Download a model: <code>bash download_model.sh</code></li>
                    <li>Test the API: <a href="/docs" style="color: white;">API Docs</a></li>
                    <li>Connect via WebSocket for voice chat</li>
                </ol>
                
                <p style="margin-top: 20px; opacity: 0.8;">
                    💡 Check the full documentation in the project folder for advanced features.
                </p>
            </div>
        </div>
    </body>
    </html>
    """)

@app.get("/api/status")
async def status():
    return {
        "status": "online",
        "name": config['leona']['name'],
        "tagline": config['leona']['tagline']
    }

@app.post("/api/chat")
async def chat(message: str):
    # Simplified response for demo
    return {
        "response": f"I understand you said: '{message}'. Once you install a model, I'll be able to provide intelligent responses. Always one call away."
    }

if __name__ == "__main__":
    import uvicorn
    print(f"🌟 Starting LEONA on http://localhost:{config['server']['port']}")
    print(f"✨ {config['leona']['tagline']}")
    uvicorn.run(app, host=config['server']['host'], port=config['server']['port'])
EOF

# Create model download script
cat > download_model.sh << 'EOF'
#!/bin/bash

echo "📥 LEONA Model Downloader"
echo ""
echo "Choose a model to download:"
echo "1) Mistral 7B (Recommended - 4.1GB)"
echo "2) LLaMA 2 7B (4.1GB)"
echo "3) Phi-2 (1.6GB - Smaller, faster)"
echo "4) TinyLLaMA (638MB - Minimal resources)"
echo ""
read -p "Enter choice (1-4): " choice

MODEL_DIR="data/models"
mkdir -p "$MODEL_DIR"

case $choice in
    1)
        echo "Downloading Mistral 7B..."
        wget -O "$MODEL_DIR/model.gguf" "https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF/resolve/main/mistral-7b-instruct-v0.2.Q4_K_M.gguf"
        ;;
    2)
        echo "Downloading LLaMA 2 7B..."
        wget -O "$MODEL_DIR/model.gguf" "https://huggingface.co/TheBloke/Llama-2-7B-Chat-GGUF/resolve/main/llama-2-7b-chat.Q4_K_M.gguf"
        ;;
    3)
        echo "Downloading Phi-2..."
        wget -O "$MODEL_DIR/model.gguf" "https://huggingface.co/TheBloke/phi-2-GGUF/resolve/main/phi-2.Q4_K_M.gguf"
        ;;
    4)
        echo "Downloading TinyLLaMA..."
        wget -O "$MODEL_DIR/model.gguf" "https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF/resolve/main/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf"
        ;;
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac

echo "✅ Model downloaded successfully!"
EOF

chmod +x download_model.sh

# Create start script
cat > start_leona.sh << 'EOF'
#!/bin/bash

source venv/bin/activate
echo "🌟 Starting LEONA..."
python backend/main.py
EOF

chmod +x start_leona.sh

# Final setup
echo ""
echo "╔══════════════════════════════════════════╗"
echo "║        ✅ LEONA Setup Complete!          ║"
echo "╚══════════════════════════════════════════╝"
echo ""
echo "📍 Installation location: $PROJECT_DIR"
echo ""
echo "🚀 To start LEONA:"
echo "   1. cd $PROJECT_DIR"
echo "   2. ./download_model.sh  (download an AI model)"
echo "   3. ./start_leona.sh     (start LEONA)"
echo ""
echo "🌐 Then open: http://localhost:8000"
echo ""
echo "💡 For the full implementation with all agents and features,"
echo "   refer to the complete development plan."
echo ""
echo "✨ LEONA - Always One Call Away"