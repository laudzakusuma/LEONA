from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from core.llm_engine import LLMEngine
from core.memory_manager import MemoryManager

class BaseAgent(ABC):
    """Base class for all LEONA agents"""
    
    def __init__(self, llm: LLMEngine, memory: MemoryManager):
        self.llm = llm
        self.memory = memory
        self.name = self.__class__.__name__
        
    @abstractmethod
    async def execute(self, user_input: str, parameters: Dict[str, Any] = None) -> str:
        """Execute the agent's primary function"""
        pass
    
    async def get_context(self, user_input: str) -> str:
        """Get relevant context from memory"""
        return await self.memory.get_context(user_input)
    
    async def store_action(self, action: str, result: str):
        """Store agent action in memory"""
        await self.memory.store_conversation(
            f"[{self.name}] {action}",
            result,
            context=f"agent_action"
        )