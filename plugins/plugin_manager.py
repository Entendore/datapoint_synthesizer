"""
Plugin system for extensibility
"""

import os
from typing import Dict, List


class PluginBase:
    """Base class for plugins."""
    
    name: str = "Base Plugin"
    description: str = "Base plugin class"
    version: str = "1.0.0"
    author: str = "Unknown"
    
    def initialize(self, context: Dict):
        pass
    
    def execute(self, datapoints: List[Dict], params: Dict) -> List[Dict]:
        return datapoints
    
    def cleanup(self):
        pass


class PluginManager:
    """Manages plugins."""
    
    def __init__(self):
        self.plugins: Dict[str, PluginBase] = {}
        self.plugin_dir = "plugins"
        os.makedirs(self.plugin_dir, exist_ok=True)
    
    def load_plugin(self, plugin_class: type):
        plugin = plugin_class()
        self.plugins[plugin.name] = plugin
        return plugin
    
    def unload_plugin(self, name: str):
        if name in self.plugins:
            self.plugins[name].cleanup()
            del self.plugins[name]
    
    def execute_plugin(self, name: str, datapoints: List[Dict], params: Dict) -> List[Dict]:
        if name not in self.plugins:
            raise ValueError(f"Plugin not found: {name}")
        
        return self.plugins[name].execute(datapoints, params)
    
    def list_plugins(self) -> List[str]:
        return list(self.plugins.keys())


# Built-in plugins
class UppercasePlugin(PluginBase):
    name = "Uppercase"
    description = "Converts all string fields to uppercase"
    
    def execute(self, datapoints: List[Dict], params: Dict) -> List[Dict]:
        for dp in datapoints:
            for k, v in dp.items():
                if isinstance(v, str):
                    dp[k] = v.upper()
        return datapoints


class AddTimestampPlugin(PluginBase):
    name = "Add Timestamp"
    description = "Adds a timestamp field to each datapoint"
    
    def execute(self, datapoints: List[Dict], params: Dict) -> List[Dict]:
        from datetime import datetime
        for dp in datapoints:
            dp['timestamp'] = datetime.now().isoformat()
        return datapoints


class FilterByLengthPlugin(PluginBase):
    name = "Filter by Length"
    description = "Filters datapoints by text length"
    
    def execute(self, datapoints: List[Dict], params: Dict) -> List[Dict]:
        field = params.get('field', 'text')
        min_length = params.get('min_length', 0)
        max_length = params.get('max_length', float('inf'))
        
        filtered = []
        for dp in datapoints:
            if field in dp:
                text = str(dp[field])
                if min_length <= len(text) <= max_length:
                    filtered.append(dp)
        
        return filtered
