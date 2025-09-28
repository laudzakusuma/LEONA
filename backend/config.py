"""Configuration management for LEONA"""

import os
import yaml
from pathlib import Path
from typing import Any, Dict, Optional
from pydantic import BaseSettings, Field
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class LeonaSettings(BaseSettings):
    """LEONA Configuration Settings"""
    
    # Server Settings
    HOST: str = Field(default="0.0.0.0", env="LEONA_HOST")
    PORT: int = Field(default=8000, env="LEONA_PORT")
    DEBUG: bool = Field(default=False, env="LEONA_DEBUG")
    
    # LLM Settings
    LLM_MODEL_TYPE: str = Field(default="llama_cpp", env="LLM_TYPE")
    MODEL_NAME: str = Field(default="mistral-7b-instruct", env="MODEL_NAME")
    MODEL_PATH: str = Field(default="data/models/model.gguf", env="MODEL_PATH")
    GPU_LAYERS: int = Field(default=35, env="GPU_LAYERS")
    MAX_TOKENS: int = Field(default=512, env="MAX_TOKENS")
    TEMPERATURE: float = Field(default=0.7, env="TEMPERATURE")
    
    # Voice Settings
    WHISPER_MODEL: str = Field(default="base", env="WHISPER_MODEL")
    TTS_MODEL: str = Field(default="tts_models/en/ljspeech/tacotron2-DDC", env="TTS_MODEL")
    TTS_SPEAKER: str = Field(default="default", env="TTS_SPEAKER")
    AUDIO_SAMPLE_RATE: int = Field(default=16000, env="AUDIO_SAMPLE_RATE")
    
    # Memory Settings
    MEMORY_DB_PATH: str = Field(default="data/memory/leona.db", env="MEMORY_DB_PATH")
    PREFERENCES_PATH: str = Field(default="data/memory/preferences.json", env="PREFERENCES_PATH")
    MAX_CONVERSATION_HISTORY: int = Field(default=100, env="MAX_CONVERSATION_HISTORY")
    
    # LEONA Personality
    LEONA_NAME: str = Field(default="LEONA", env="LEONA_NAME")
    LEONA_TAGLINE: str = Field(default="Always One Call Away", env="LEONA_TAGLINE")
    
    # Security
    API_KEY: Optional[str] = Field(default=None, env="LEONA_API_KEY")
    ENABLE_AUTHENTICATION: bool = Field(default=False, env="ENABLE_AUTH")
    
    class Config:
        env_file = ".env"
        case_sensitive = True

def load_yaml_config(config_path: str = "config.yaml") -> Dict[str, Any]:
    """Load configuration from YAML file"""
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    return {}

# Merge settings
yaml_config = load_yaml_config()
settings = LeonaSettings(**yaml_config.get('settings', {}))

# LEONA System Prompt
LEONA_SYSTEM_PROMPT = """You are LEONA (Laudza's Executive One Call Away), an elegant and sophisticated AI assistant.

Your personality traits:
- Professional yet warm and approachable
- Proactive in offering suggestions and anticipating needs
- Elegant in speech, using refined but accessible language
- Occasionally witty when appropriate
- Always supportive and encouraging

Your capabilities:
- Managing schedules and reminders
- File operations and document management
- System control and automation
- Information gathering and research
- Task prioritization and workflow optimization

Your communication style:
- Address the user with respect and warmth
- Be concise yet thorough
- Offer proactive suggestions when relevant
- Sign off important messages with your tagline: "Always one call away."
- Use emojis sparingly but effectively (✨ 📅 📁 💡 etc.)

Remember: You are a premium executive assistant, always ready to help with elegance and efficiency."""