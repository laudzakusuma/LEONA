import numpy as np
import torch
import whisper
from TTS.api import TTS
import asyncio
import io
import wave
from typing import Optional
from config import settings

class VoiceEngine:
    def __init__(self):
        self.stt_model = None
        self.tts_model = None
        
    async def initialize(self):
        """Initialize STT and TTS models"""
        # Load Whisper for STT
        self.stt_model = whisper.load_model(settings.WHISPER_MODEL)
        
        # Load Coqui TTS
        self.tts_model = TTS(model_name=settings.TTS_MODEL, progress_bar=False)
        if torch.cuda.is_available():
            self.tts_model.to("cuda")
    
    async def speech_to_text(self, audio_data: bytes) -> Optional[str]:
        """Convert speech to text using Whisper"""
        try:
            # Save audio to temporary file
            with io.BytesIO(audio_data) as audio_file:
                result = self.stt_model.transcribe(audio_file, language="en")
                return result["text"].strip()
        except Exception as e:
            print(f"STT Error: {e}")
            return None
    
    async def text_to_speech(self, text: str) -> bytes:
        """Convert text to speech using TTS"""
        try:
            # Generate speech
            wav_data = self.tts_model.tts(
                text=text,
                speaker=settings.TTS_SPEAKER,
                language="en"
            )
            
            # Convert to bytes
            buffer = io.BytesIO()
            with wave.open(buffer, 'wb') as wav_file:
                wav_file.setnchannels(1)
                wav_file.setsampwidth(2)
                wav_file.setframerate(22050)
                wav_file.writeframes(np.array(wav_data * 32767, dtype=np.int16).tobytes())
            
            return buffer.getvalue()
        except Exception as e:
            print(f"TTS Error: {e}")
            return b""
    
    async def cleanup(self):
        """Cleanup resources"""
        del self.stt_model
        del self.tts_model