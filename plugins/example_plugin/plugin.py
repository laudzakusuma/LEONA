from typing import Dict, Any

class WeatherPlugin:
    """Example plugin for weather information"""
    
    def __init__(self, config: Dict[str, Any]):
        self.name = "weather"
        self.config = config
        
    async def execute(self, query: str) -> str:
        """Get weather information"""
        # Implementation here
        return f"Weather plugin processing: {query}"
    
    def get_capabilities(self) -> Dict[str, str]:
        return {
            "weather": "Get current weather",
            "forecast": "Get weather forecast"
        }

# Plugin registration
def register():
    return WeatherPlugin