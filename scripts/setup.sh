#!/bin/bash

echo "🌟 Setting up LEONA - Laudza's Executive One Call Away"

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install PyTorch (with CUDA support)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Install dependencies
pip install -r requirements.txt

# Download models
python scripts/download_models.py

# Setup directories
mkdir -p data/memory data/models plugins

# Initialize database
python -c "from backend.core.memory_manager import MemoryManager; import asyncio; asyncio.run(MemoryManager()._initialize_db())"

echo "✨ LEONA setup complete! Run 'python backend/main.py' to start."