"""
Global configuration for the Datapoint Synthesizer
"""

from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Any
import json
import os


@dataclass
class Config:
    """Application configuration."""
    
    # Paths
    base_dir: Path = Path("datasets")
    templates_dir: Path = Path("templates")
    plugins_dir: Path = Path("plugins")
    sessions_dir: Path = Path("sessions")
    
    # Generation defaults
    default_strategy: str = "balanced"
    default_count: int = 10
    default_temperature: float = 1.0
    novelty_threshold: float = 0.85
    
    # Feature toggles
    enable_novelty_detection: bool = True
    enable_validation: bool = True
    enable_coherence: bool = True
    enable_explanations: bool = False
    enable_auto_save: bool = True
    auto_save_interval_ms: int = 60000
    
    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    
    # UI
    theme: str = "dark"
    window_width: int = 1600
    window_height: int = 1000
    
    # Performance
    max_workers: int = 4
    batch_size: int = 100
    max_history: int = 50
    
    @classmethod
    def load(cls, path: str = "config.json") -> "Config":
        if not os.path.exists(path):
            return cls()
        
        with open(path, 'r') as f:
            data = json.load(f)
        
        config = cls()
        for key, value in data.items():
            if hasattr(config, key):
                if key.endswith("_dir"):
                    setattr(config, key, Path(value))
                else:
                    setattr(config, key, value)
        
        return config
    
    def save(self, path: str = "config.json"):
        data = {
            "base_dir": str(self.base_dir),
            "templates_dir": str(self.templates_dir),
            "plugins_dir": str(self.plugins_dir),
            "sessions_dir": str(self.sessions_dir),
            "default_strategy": self.default_strategy,
            "default_count": self.default_count,
            "default_temperature": self.default_temperature,
            "novelty_threshold": self.novelty_threshold,
            "enable_novelty_detection": self.enable_novelty_detection,
            "enable_validation": self.enable_validation,
            "enable_coherence": self.enable_coherence,
            "enable_explanations": self.enable_explanations,
            "enable_auto_save": self.enable_auto_save,
            "auto_save_interval_ms": self.auto_save_interval_ms,
            "api_host": self.api_host,
            "api_port": self.api_port,
            "theme": self.theme,
            "window_width": self.window_width,
            "window_height": self.window_height,
            "max_workers": self.max_workers,
            "batch_size": self.batch_size,
            "max_history": self.max_history,
        }
        
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)


CONFIG = Config.load()


def get_config() -> Config:
    return CONFIG
