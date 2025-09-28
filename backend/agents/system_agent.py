import subprocess
import platform
import os
from typing import Dict, Any
from agents.base_agent import BaseAgent

class SystemAgent(BaseAgent):
    """Agent for system-level operations"""
    
    def __init__(self, llm, memory):
        super().__init__(llm, memory)
        self.os_type = platform.system()
        
    async def execute(self, user_input: str, parameters: Dict[str, Any] = None) -> str:
        """Execute system commands"""
        
        # Parse command from user input
        command = await self._parse_command(user_input)
        
        if command["action"] == "open_app":
            return await self._open_application(command["target"])
        elif command["action"] == "search_files":
            return await self._search_files(command["query"])
        elif command["action"] == "run_script":
            return await self._run_script(command["script"])
        else:
            return "I understand you want to interact with the system, but I need more specific instructions."
    
    async def _parse_command(self, user_input: str) -> Dict[str, str]:
        """Parse system command from natural language"""
        prompt = f"""Parse this system command request:
        User: {user_input}
        
        Determine the action (open_app, search_files, run_script) and target.
        Respond in JSON format."""
        
        response = await self.llm.generate(prompt)
        # Parse JSON response
        try:
            import json
            return json.loads(response)
        except:
            return {"action": "unknown", "target": ""}
    
    async def _open_application(self, app_name: str) -> str:
        """Open an application"""
        try:
            if self.os_type == "Windows":
                subprocess.Popen(f"start {app_name}", shell=True)
            elif self.os_type == "Darwin":  # macOS
                subprocess.Popen(f"open -a {app_name}", shell=True)
            else:  # Linux
                subprocess.Popen(app_name, shell=True)
            
            return f"I've opened {app_name} for you. Is there anything specific you'd like me to help with?"
        except Exception as e:
            return f"I encountered an issue opening {app_name}. Let me try an alternative approach."
    
    async def _search_files(self, query: str) -> str:
        """Search for files on the system"""
        try:
            # Simple file search implementation
            home_dir = os.path.expanduser("~")
            matches = []
            
            for root, dirs, files in os.walk(home_dir):
                for file in files:
                    if query.lower() in file.lower():
                        matches.append(os.path.join(root, file))
                        if len(matches) >= 5:  # Limit results
                            break
                if len(matches) >= 5:
                    break
            
            if matches:
                result = f"I found {len(matches)} files matching '{query}':\n"
                for match in matches:
                    result += f"  • {match}\n"
                return result
            else:
                return f"I couldn't find any files matching '{query}'. Would you like me to search in a specific directory?"
        except Exception as e:
            return f"I encountered an issue while searching. Could you provide more specific details?"
    
    async def _run_script(self, script_path: str) -> str:
        """Run a script safely"""
        # Security check - only run from approved directories
        approved_dirs = [os.path.expanduser("~/leona_scripts")]
        
        if not any(script_path.startswith(d) for d in approved_dirs):
            return "For security reasons, I can only run scripts from approved directories."
        
        try:
            result = subprocess.run(
                script_path,
                capture_output=True,
                text=True,
                timeout=30
            )
            return f"Script executed successfully. Output:\n{result.stdout}"
        except subprocess.TimeoutExpired:
            return "The script took too long to execute. I've stopped it for safety."
        except Exception as e:
            return f"I couldn't run the script. Please check if it exists and has proper permissions."