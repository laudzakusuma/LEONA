import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from llama_cpp import Llama
import asyncio
from typing import Optional, List, Dict
from config import settings

class LLMEngine:
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.model_type = settings.LLM_MODEL_TYPE
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
    async def initialize(self):
        """Load the local LLM model"""
        if self.model_type == "llama_cpp":
            # Using llama.cpp for efficient inference
            self.model = Llama(
                model_path=settings.MODEL_PATH,
                n_gpu_layers=settings.GPU_LAYERS if self.device == "cuda" else 0,
                n_ctx=4096,
                n_threads=8,
                verbose=False
            )
        else:
            # Using HuggingFace transformers
            self.tokenizer = AutoTokenizer.from_pretrained(settings.MODEL_NAME)
            self.model = AutoModelForCausalLM.from_pretrained(
                settings.MODEL_NAME,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                device_map="auto"
            )
    
    async def generate(self, 
                       prompt: str, 
                       system_prompt: str = None,
                       max_tokens: int = 512,
                       temperature: float = 0.7) -> str:
        """Generate response from the LLM"""
        
        # LEONA's personality system prompt
        if not system_prompt:
            system_prompt = """You are LEONA (Laudza's Executive One Call Away), an elegant and professional AI assistant.
            You are supportive, proactive, and occasionally witty. You speak with warmth and sophistication.
            Your responses are concise yet complete. You anticipate needs and offer helpful suggestions.
            Your tagline is 'Always One Call Away.'"""
        
        if self.model_type == "llama_cpp":
            response = self.model(
                f"System: {system_prompt}\nUser: {prompt}\nLEONA:",
                max_tokens=max_tokens,
                temperature=temperature,
                stop=["User:", "\n\n"]
            )
            return response['choices'][0]['text'].strip()
        else:
            # HuggingFace generation
            full_prompt = f"{system_prompt}\n\nUser: {prompt}\nAssistant:"
            inputs = self.tokenizer(full_prompt, return_tensors="pt").to(self.device)
            
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=max_tokens,
                    temperature=temperature,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id
                )
            
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            return response.split("Assistant:")[-1].strip()
    
    def is_ready(self) -> bool:
        return self.model is not None
    
    async def cleanup(self):
        """Cleanup resources"""
        if self.model:
            del self.model
            torch.cuda.empty_cache()