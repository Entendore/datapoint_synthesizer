"""
Main GUI window
"""

import sys
import json
from typing import Dict, List

from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                               QHBoxLayout, QStackedWidget, QListWidget, QLabel,
                               QPushButton, QTextEdit, QStatusBar, QMenuBar, QMenu,
                               QToolBar, QProgressBar, QAction, QShortcut, QMessageBox)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QKeySequence

from .theme_manager import ThemeManager
from .session_manager import SessionManager
from .widgets.example_manager import ExampleManagerWidget
from .widgets.generation_config import GenerationConfigWidget
from .widgets.output_viewer import EnhancedOutputViewerWidget


class SynthesizerMainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🧬 Datapoint Synthesizer v3 - Complete")
        self.resize(1600, 1000)
        
        self.synthesizer = None
        self.session_manager = SessionManager()
        self.current_datapoints: List[Dict] = []
        
        self._init_ui()
        self._init_menu()
        self._init_toolbar()
        self._init_statusbar()
        self._init_shortcuts()
        
        self._load_default_examples()
    
    def _init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        
        sidebar = QWidget()
        sidebar.setMaximumWidth(220)
        sidebar_layout = QVBoxLayout(sidebar)
        
        self.nav_list = QListWidget()
        self.nav_list.addItems([
            "📝 Examples",
            "⚙️ Generation",
            "📤 Output",
        ])
        self.nav_list.currentRowChanged.connect(self._on_nav_changed)
        sidebar_layout.addWidget(self.nav_list)
        
        main_layout.addWidget(sidebar)
        
        self.content_stack = QStackedWidget()
        
        self.example_manager = ExampleManagerWidget()
        self.example_manager.examples_changed.connect(self._on_examples_changed)
        self.content_stack.addWidget(self.example_manager)
        
        self.gen_config = GenerationConfigWidget()
        self.gen_config.config_changed.connect(self._on_config_changed)
        self.content_stack.addWidget(self.gen_config)
        
        self.output_viewer = EnhancedOutputViewerWidget()
        self.content_stack.addWidget(self.output_viewer)
        
        main_layout.addWidget(self.content_stack, 1)
        
        preview_widget = QWidget()
        preview_widget.setMaximumWidth(400)
        preview_layout = QVBoxLayout(preview_widget)
        
        preview_layout.addWidget(QLabel("👁️ Live Preview"))
        self.preview_view = QTextEdit()
        self.preview_view.setReadOnly(True)
        self.preview_view.setFont(QFont("Consolas", 10))
        preview_layout.addWidget(self.preview_view)
        
        main_layout.addWidget(preview_widget)
        
        self.nav_list.setCurrentRow(0)
    
    def _init_menu(self):
        menubar = self.menuBar()
        
        file_menu = menubar.addMenu("📁 File")
        
        load_action = QAction("📂 Load Examples...", self)
        load_action.setShortcut("Ctrl+O")
        load_action.triggered.connect(self.example_manager.load_from_file)
        file_menu.addAction(load_action)
        
        save_action = QAction("💾 Save Generated Data", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(lambda: self.output_viewer._export("jsonl"))
        file_menu.addAction(save_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("❌ Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        gen_menu = menubar.addMenu("🔄 Generate")
        
        generate_action = QAction("🔄 Generate Datapoints", self)
        generate_action.setShortcut("Ctrl+G")
        generate_action.triggered.connect(self._generate)
        gen_menu.addAction(generate_action)
    
    def _init_toolbar(self):
        toolbar = QToolBar("Main Toolbar")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)
        
        toolbar.addAction("📂 Load").triggered.connect(self.example_manager.load_from_file)
        toolbar.addSeparator()
        toolbar.addAction("🔄 Generate").triggered.connect(self._generate)
    
    def _init_statusbar(self):
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumWidth(200)
        self.progress_bar.setVisible(False)
        self.status_bar.addPermanentWidget(self.progress_bar)
        
        self.status_bar.showMessage("Ready - Load examples to begin")
    
    def _init_shortcuts(self):
        QShortcut(QKeySequence("Ctrl+G"), self).activated.connect(self._generate)
    
    def _load_default_examples(self):
        defaults = [
            {"question": "What is the capital of France?", "answer": "Paris", "difficulty": "easy"},
            {"question": "What is the capital of Japan?", "answer": "Tokyo", "difficulty": "medium"},
            {"question": "What is the capital of Germany?", "answer": "Berlin", "difficulty": "hard"},
        ]
        self.example_manager.set_examples(defaults)
    
    def _on_nav_changed(self, row: int):
        self.content_stack.setCurrentIndex(row)
    
    def _on_examples_changed(self):
        self.status_bar.showMessage(f"{len(self.example_manager.get_examples())} examples loaded")
    
    def _get_synthesizer(self):
        if self.synthesizer is None:
            try:
                from core.synthesizer import DatapointSynthesizerV3
                from core.strategies import Strategy
                self.synthesizer = DatapointSynthesizerV3()
            except ImportError as e:
                QMessageBox.critical(self, "Import Error", str(e))
                return None
        return self.synthesizer
    
    def _on_config_changed(self, config: Dict):
        action = config.get("action", "generate")
        self.gen_config.clear_pending_action()
        
        if action == "generate":
            self._generate()
    
    def _generate(self):
        examples = self.example_manager.get_examples()
        if not examples:
            QMessageBox.warning(self, "No Examples", "Please add examples first")
            return
        
        synth = self._get_synthesizer()
        if not synth:
            return
        
        config = self.gen_config.get_config()
        
        try:
            if not synth.examples:
                synth.set_examples(examples)
            
            self.status_bar.showMessage("🔄 Generating...")
            self.progress_bar.setVisible(True)
            self.progress_bar.setRange(0, 0)
            
            QApplication.processEvents()
            
            generated = synth.synthesize(
                n=config["count"],
                ensure_novelty=config["novelty"],
                validate=config["validate"],
                add_explanations=config["explanations"],
                conditions=config.get("conditions")
            )
            
            self.progress_bar.setVisible(False)
            self.current_datapoints = generated
            
            self.output_viewer.set_datapoints(generated)
            
            if generated:
                self.preview_view.setPlainText(json.dumps(generated[0], indent=2))
            
            self.status_bar.showMessage(f"✓ Generated {len(generated)} datapoints")
            self.nav_list.setCurrentRow(2)
            
        except Exception as e:
            self.progress_bar.setVisible(False)
            QMessageBox.critical(self, "Error", str(e))
