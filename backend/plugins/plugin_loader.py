"""Dynamic plugin loader for LEONA"""

import importlib
import os
from pathlib import Path
from typing import Dict, Any, List

class PluginLoader:
    """Load and manage LEONA plugins"""
    
    def __init__(self, plugin_dir: str = "plugins"):
        self.plugin_dir = Path(plugin_dir)
        self.loaded_plugins = {}
        
    def discover_plugins(self) -> List[str]:
        """Discover available plugins"""
        plugins = []
        
        if not self.plugin_dir.exists():
            return plugins
        
        for item in self.plugin_dir.iterdir():
            if item.is_dir() and (item / "__init__.py").exists():
                plugins.append(item.name)
            elif item.is_file() and item.suffix == ".py" and item.name != "__init__.py":
                plugins.append(item.stem)
        
        return plugins
    
    def load_plugin(self, plugin_name: str) -> bool:
        """Load a specific plugin"""
        try:
            # Import the plugin module
            module = importlib.import_module(f"plugins.{plugin_name}")
            
            # Get the register function
            if hasattr(module, 'register'):
                plugin_class = module.register()
                self.loaded_plugins[plugin_name] = plugin_class()
                print(f"✅ Loaded plugin: {plugin_name}")
                return True
            else:
                print(f"❌ Plugin {plugin_name} missing register function")
                return False
                
        except Exception as e:
            print(f"❌ Failed to load plugin {plugin_name}: {e}")
            return False
    
    def load_all_plugins(self):
        """Load all discovered plugins"""
        plugins = self.discover_plugins()
        
        for plugin in plugins:
            self.load_plugin(plugin)
    
    def get_plugin(self, plugin_name: str):
        """Get a loaded plugin instance"""
        return self.loaded_plugins.get(plugin_name)
    
    def list_loaded_plugins(self) -> List[str]:
        """List all loaded plugins"""
        return list(self.loaded_plugins.keys())
    
    def execute_plugin(self, plugin_name: str, method: str, *args, **kwargs):
        """Execute a plugin method"""
        plugin = self.get_plugin(plugin_name)
        
        if not plugin:
            return f"Plugin {plugin_name} not loaded"
        
        if hasattr(plugin, method):
            return getattr(plugin, method)(*args, **kwargs)
        else:
            return f"Plugin {plugin_name} doesn't have method {method}"