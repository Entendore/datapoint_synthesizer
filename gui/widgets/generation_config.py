"""
Generation configuration widget
"""

import json
from typing import Dict

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
                               QFormLayout, QComboBox, QSpinBox, QCheckBox,
                               QPushButton, QTextEdit, QLabel)
from PySide6.QtCore import Signal


class GenerationConfigWidget(QWidget):
    """Configuration panel for generation parameters."""
    
    config_changed = Signal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._pending_action = "generate"
        self._init_ui()
    
    def _init_ui(self):
        layout = QVBoxLayout(self)
        
        strategy_group = QGroupBox("🎯 Generation Strategy")
        strategy_layout = QFormLayout()
        
        self.strategy_combo = QComboBox()
        self.strategy_combo.addItems(["conservative", "balanced", "creative", "adversarial"])
        self.strategy_combo.setCurrentText("balanced")
        self.strategy_combo.currentTextChanged.connect(self._emit_config)
        strategy_layout.addRow("Strategy:", self.strategy_combo)
        
        self.n_spin = QSpinBox()
        self.n_spin.setRange(1, 10000)
        self.n_spin.setValue(10)
        self.n_spin.valueChanged.connect(self._emit_config)
        strategy_layout.addRow("Count:", self.n_spin)
        
        strategy_group.setLayout(strategy_layout)
        layout.addWidget(strategy_group)
        
        options_group = QGroupBox("⚙️ Options")
        options_layout = QVBoxLayout()
        
        self.novelty_check = QCheckBox("🔍 Enable novelty detection")
        self.novelty_check.setChecked(True)
        self.novelty_check.stateChanged.connect(self._emit_config)
        options_layout.addWidget(self.novelty_check)
        
        self.validate_check = QCheckBox("✓ Validate against schema")
        self.validate_check.setChecked(True)
        self.validate_check.stateChanged.connect(self._emit_config)
        options_layout.addWidget(self.validate_check)
        
        self.explain_check = QCheckBox("💡 Add explanations")
        self.explain_check.setChecked(False)
        self.explain_check.stateChanged.connect(self._emit_config)
        options_layout.addWidget(self.explain_check)
        
        self.coherence_check = QCheckBox("🔗 Ensure semantic coherence")
        self.coherence_check.setChecked(True)
        self.coherence_check.stateChanged.connect(self._emit_config)
        options_layout.addWidget(self.coherence_check)
        
        options_group.setLayout(options_layout)
        layout.addWidget(options_group)
        
        cond_group = QGroupBox("🎛️ Conditional Generation")
        cond_layout = QVBoxLayout()
        
        self.use_conditions_check = QCheckBox("Apply conditions")
        self.use_conditions_check.setChecked(False)
        cond_layout.addWidget(self.use_conditions_check)
        
        self.conditions_editor = QTextEdit()
        self.conditions_editor.setPlaceholderText(
            '{"difficulty": "hard"}\n{"reward": {"min": 0.5, "max": 1.0}}'
        )
        self.conditions_editor.setMaximumHeight(80)
        cond_layout.addWidget(self.conditions_editor)
        
        cond_group.setLayout(cond_layout)
        layout.addWidget(cond_group)
        
        self.generate_btn = QPushButton("🔄 GENERATE DATAPOINTS")
        self.generate_btn.setMinimumHeight(50)
        self.generate_btn.clicked.connect(lambda: self._emit_action("generate"))
        layout.addWidget(self.generate_btn)
        
        layout.addStretch()
    
    def _emit_config(self):
        self.config_changed.emit(self.get_config())
    
    def _emit_action(self, action: str):
        self._pending_action = action
        self.config_changed.emit(self.get_config())
    
    def get_config(self) -> Dict:
        conditions = None
        if self.use_conditions_check.isChecked():
            try:
                conditions = json.loads(self.conditions_editor.toPlainText())
            except json.JSONDecodeError:
                pass
        
        return {
            "strategy": self.strategy_combo.currentText(),
            "count": self.n_spin.value(),
            "novelty": self.novelty_check.isChecked(),
            "validate": self.validate_check.isChecked(),
            "explanations": self.explain_check.isChecked(),
            "coherence": self.coherence_check.isChecked(),
            "conditions": conditions,
            "action": self._pending_action
        }
    
    def clear_pending_action(self):
        self._pending_action = "generate"
