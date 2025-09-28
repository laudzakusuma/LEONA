import asyncio
from typing import List, Dict, Any
from agents.base_agent import BaseAgent
from agents.scheduler_agent import SchedulerAgent
from agents.file_agent import FileAgent
from agents.system_agent import SystemAgent
from agents.web_agent import WebAgent
from core.llm_engine import LLMEngine
from core.memory_manager import MemoryManager

class AgentOrchestrator:
    def __init__(self):
        self.llm = LLMEngine()
        self.memory = MemoryManager()
        self.agents: Dict[str, BaseAgent] = {}
        self._initialize_agents()
        
    def _initialize_agents(self):
        """Initialize all available agents"""
        self.agents = {
            "scheduler": SchedulerAgent(self.llm, self.memory),
            "file": FileAgent(self.llm, self.memory),
            "system": SystemAgent(self.llm, self.memory),
            "web": WebAgent(self.llm, self.memory),
        }
    
    async def process_input(self, user_input: str) -> str:
        """Process user input and orchestrate agents"""
        
        # Analyze intent
        intent = await self._analyze_intent(user_input)
        
        # Route to appropriate agent(s)
        if intent["primary_agent"]:
            agent = self.agents.get(intent["primary_agent"])
            if agent:
                result = await agent.execute(user_input, intent["parameters"])
                
                # Check for proactive suggestions
                suggestions = await self._generate_suggestions(user_input, result)
                
                if suggestions:
                    result += f"\n\n💡 By the way, {suggestions}"
                
                return result
        
        # Default to general conversation
        response = await self.llm.generate(user_input)
        
        # Add LEONA's signature touch
        if not response.endswith("."):
            response += "."
        response += " Always one call away."
        
        return response
    
    async def _analyze_intent(self, user_input: str) -> Dict[str, Any]:
        """Analyze user intent to determine which agent to use"""
        
        prompt = f"""Analyze this request and determine which agent should handle it:
        User: {user_input}
        
        Available agents:
        - scheduler: calendar, reminders, scheduling
        - file: file operations, document management
        - system: system commands, app launching
        - web: web browsing, information gathering
        
        Respond with the agent name and any parameters in JSON format."""
        
        response = await self.llm.generate(prompt)
        
        # Parse response (simplified - use proper JSON parsing in production)
        try:
            import json
            return json.loads(response)
        except:
            return {"primary_agent": None, "parameters": {}}
    
    async def _generate_suggestions(self, user_input: str, result: str) -> str:
        """Generate proactive suggestions based on context"""
        
        # Check memory for patterns
        context = await self.memory.get_context(user_input)
        
        prompt = f"""Based on this interaction:
        User: {user_input}
        Response: {result}
        Context: {context}
        
        As LEONA, provide a brief, helpful proactive suggestion if relevant.
        Be elegant and concise. Return empty string if no suggestion needed."""
        
        suggestion = await self.llm.generate(prompt, max_tokens=100)
        return suggestion.strip()
    
    async def create_sub_agent(self, task: str) -> BaseAgent:
        """Create a sub-agent for specific tasks"""
        # Dynamic agent creation for complex workflows
        pass