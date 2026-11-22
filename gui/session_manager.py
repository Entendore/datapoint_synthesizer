"""
Session management with undo/redo
"""

import pickle
from typing import Dict, List, Optional
from datetime import datetime
from dataclasses import dataclass, field
from collections import deque

from PySide6.QtCore import QTimer


@dataclass
class SessionState:
    examples: List[Dict]
    generated_data: List[Dict]
    config: Dict
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    notes: str = ""


class SessionManager:
    """Manages session state with undo/redo and auto-save."""
    
    def __init__(self, max_history: int = 50):
        self.undo_stack: deque = deque(maxlen=max_history)
        self.redo_stack: deque = deque(maxlen=max_history)
        self.current_state: Optional[SessionState] = None
        self.auto_save_path: Optional[str] = None
        self.auto_save_timer = QTimer()
        self.auto_save_timer.timeout.connect(self._auto_save)
    
    def save_state(self, examples: List[Dict], generated: List[Dict], config: Dict):
        if self.current_state:
            self.undo_stack.append(self.current_state)
            self.redo_stack.clear()
        
        self.current_state = SessionState(
            examples=examples.copy(),
            generated_data=generated.copy(),
            config=config.copy()
        )
    
    def undo(self) -> Optional[SessionState]:
        if not self.undo_stack:
            return None
        
        if self.current_state:
            self.redo_stack.append(self.current_state)
        
        self.current_state = self.undo_stack.pop()
        return self.current_state
    
    def redo(self) -> Optional[SessionState]:
        if not self.redo_stack:
            return None
        
        if self.current_state:
            self.undo_stack.append(self.current_state)
        
        self.current_state = self.redo_stack.pop()
        return self.current_state
    
    def save_session(self, path: str):
        session_data = {
            "version": "2.0",
            "current_state": self.current_state,
            "undo_stack": list(self.undo_stack),
            "redo_stack": list(self.redo_stack),
            "saved_at": datetime.now().isoformat()
        }
        
        with open(path, 'wb') as f:
            pickle.dump(session_data, f)
    
    def load_session(self, path: str) -> bool:
        try:
            with open(path, 'rb') as f:
                session_data = pickle.load(f)
            
            self.current_state = session_data["current_state"]
            self.undo_stack = deque(session_data["undo_stack"], maxlen=50)
            self.redo_stack = deque(session_data["redo_stack"], maxlen=50)
            return True
        except Exception:
            return False
    
    def enable_auto_save(self, path: str, interval_ms: int = 60000):
        self.auto_save_path = path
        self.auto_save_timer.start(interval_ms)
    
    def _auto_save(self):
        if self.auto_save_path and self.current_state:
            try:
                self.save_session(self.auto_save_path + ".autosave")
            except Exception:
                pass
