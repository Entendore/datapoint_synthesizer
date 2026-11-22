"""
Example manager widget
"""

import json
from typing import List, Dict

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QListWidget,
                               QListWidgetItem, QTextEdit, QPushButton, QLabel,
                               QSplitter, QFileDialog, QMessageBox)
from PySide6.QtCore import Signal
from PySide6.QtGui import QFont


class ExampleManagerWidget(QWidget):
    """Widget for managing example datapoints."""
    
    examples_changed = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.examples: List[Dict] = []
        self.current_idx = -1
        self._init_ui()
    
    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        toolbar = QHBoxLayout()
        
        self.add_btn = QPushButton("➕ Add Example")
        self.add_btn.clicked.connect(self.add_example)
        toolbar.addWidget(self.add_btn)
        
        self.remove_btn = QPushButton("🗑️ Remove")
        self.remove_btn.clicked.connect(self.remove_example)
        toolbar.addWidget(self.remove_btn)
        
        self.load_btn = QPushButton("📂 Load JSON")
        self.load_btn.clicked.connect(self.load_from_file)
        toolbar.addWidget(self.load_btn)
        
        self.clear_btn = QPushButton("🧹 Clear All")
        self.clear_btn.clicked.connect(self.clear_all)
        toolbar.addWidget(self.clear_btn)
        
        toolbar.addStretch()
        layout.addLayout(toolbar)
        
        splitter = QSplitter()
        
        list_widget = QWidget()
        list_layout = QVBoxLayout(list_widget)
        list_layout.setContentsMargins(0, 0, 0, 0)
        
        self.example_list = QListWidget()
        self.example_list.currentRowChanged.connect(self._on_selection_changed)
        list_layout.addWidget(self.example_list)
        
        splitter.addWidget(list_widget)
        
        editor_widget = QWidget()
        editor_layout = QVBoxLayout(editor_widget)
        editor_layout.setContentsMargins(0, 0, 0, 0)
        
        self.editor = QTextEdit()
        self.editor.setPlaceholderText("Select an example to edit, or add a new one...")
        self.editor.setFont(QFont("Consolas", 11))
        self.editor.textChanged.connect(self._on_editor_changed)
        editor_layout.addWidget(self.editor)
        
        splitter.addWidget(editor_widget)
        splitter.setSizes([250, 750])
        
        layout.addWidget(splitter)
        
        self.status_label = QLabel("0 examples loaded")
        layout.addWidget(self.status_label)
    
    def add_example(self, example: Dict = None):
        if example is None:
            example = {"field1": "value1", "field2": 42}
        
        self.examples.append(example)
        self.example_list.addItem(f"Example {len(self.examples)}: {self._preview(example)}")
        self.example_list.setCurrentRow(len(self.examples) - 1)
        self._update_status()
        self.examples_changed.emit()
    
    def remove_example(self):
        row = self.example_list.currentRow()
        if row >= 0:
            self.examples.pop(row)
            self.example_list.takeItem(row)
            self._update_status()
            self.examples_changed.emit()
    
    def clear_all(self):
        self.examples.clear()
        self.example_list.clear()
        self.editor.clear()
        self._update_status()
        self.examples_changed.emit()
    
    def load_from_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Load Examples", "", "JSON Files (*.json);;JSONL Files (*.jsonl)"
        )
        if not path:
            return
        
        try:
            with open(path, 'r') as f:
                if path.endswith('.jsonl'):
                    data = [json.loads(line) for line in f if line.strip()]
                else:
                    data = json.load(f)
                    if isinstance(data, dict):
                        data = [data]
            
            for ex in data:
                self.add_example(ex)
            
            QMessageBox.information(self, "Loaded", f"Loaded {len(data)} examples")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load: {e}")
    
    def _on_selection_changed(self, row: int):
        self.current_idx = row
        if 0 <= row < len(self.examples):
            self.editor.setPlainText(json.dumps(self.examples[row], indent=2))
    
    def _on_editor_changed(self):
        if self.current_idx < 0:
            return
        try:
            new_value = json.loads(self.editor.toPlainText())
            self.examples[self.current_idx] = new_value
            self.example_list.item(self.current_idx).setText(
                f"Example {self.current_idx + 1}: {self._preview(new_value)}"
            )
            self.examples_changed.emit()
        except json.JSONDecodeError:
            pass
    
    def _preview(self, example: Dict) -> str:
        keys = list(example.keys())[:2]
        preview = ", ".join(f"{k}={example[k]}" for k in keys if k in example)
        return preview[:50] + ("..." if len(preview) > 50 else "")
    
    def _update_status(self):
        self.status_label.setText(f"{len(self.examples)} examples loaded")
    
    def get_examples(self) -> List[Dict]:
        return self.examples.copy()
    
    def set_examples(self, examples: List[Dict]):
        self.clear_all()
        for ex in examples:
            self.add_example(ex)
