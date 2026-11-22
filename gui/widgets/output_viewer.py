"""
Output viewer widget
"""

import json
from typing import List, Dict

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
                               QTextEdit, QLabel, QPushButton, QTableWidget,
                               QTableWidgetItem, QHeaderView, QFileDialog,
                               QMessageBox, QLineEdit, QComboBox)
from PySide6.QtGui import QFont


class EnhancedOutputViewerWidget(QWidget):
    """Enhanced output viewer with search, filter, bookmarks."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.datapoints: List[Dict] = []
        self.filtered_datapoints: List[Dict] = []
        self._init_ui()
    
    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        search_bar = QHBoxLayout()
        
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("🔍 Search datapoints...")
        self.search_box.textChanged.connect(self._apply_filter)
        search_bar.addWidget(self.search_box)
        
        self.filter_field_combo = QComboBox()
        self.filter_field_combo.setEditable(True)
        self.filter_field_combo.setPlaceholderText("Field")
        search_bar.addWidget(self.filter_field_combo)
        
        self.filter_value_box = QLineEdit()
        self.filter_value_box.setPlaceholderText("Value")
        self.filter_value_box.textChanged.connect(self._apply_filter)
        search_bar.addWidget(self.filter_value_box)
        
        self.clear_filter_btn = QPushButton("✕ Clear")
        self.clear_filter_btn.clicked.connect(self._clear_filter)
        search_bar.addWidget(self.clear_filter_btn)
        
        layout.addLayout(search_bar)
        
        self.tabs = QTabWidget()
        
        json_widget = QWidget()
        json_layout = QVBoxLayout(json_widget)
        json_layout.setContentsMargins(0, 0, 0, 0)
        
        self.json_view = QTextEdit()
        self.json_view.setReadOnly(True)
        self.json_view.setFont(QFont("Consolas", 11))
        json_layout.addWidget(self.json_view)
        
        self.tabs.addTab(json_widget, "📄 JSON")
        
        table_widget = QWidget()
        table_layout = QVBoxLayout(table_widget)
        table_layout.setContentsMargins(0, 0, 0, 0)
        
        self.table_view = QTableWidget()
        self.table_view.setSelectionBehavior(QTableWidget.SelectRows)
        table_layout.addWidget(self.table_view)
        
        self.tabs.addTab(table_widget, "📊 Table")
        
        layout.addWidget(self.tabs)
        
        export_layout = QHBoxLayout()
        
        self.export_jsonl_btn = QPushButton("💾 JSONL")
        self.export_jsonl_btn.clicked.connect(lambda: self._export("jsonl"))
        export_layout.addWidget(self.export_jsonl_btn)
        
        self.export_json_btn = QPushButton("💾 JSON")
        self.export_json_btn.clicked.connect(lambda: self._export("json"))
        export_layout.addWidget(self.export_json_btn)
        
        self.export_csv_btn = QPushButton("💾 CSV")
        self.export_csv_btn.clicked.connect(lambda: self._export("csv"))
        export_layout.addWidget(self.export_csv_btn)
        
        export_layout.addStretch()
        
        self.copy_btn = QPushButton("📋 Copy")
        self.copy_btn.clicked.connect(self._copy_to_clipboard)
        export_layout.addWidget(self.copy_btn)
        
        layout.addLayout(export_layout)
        
        self.status_label = QLabel("0 datapoints")
        layout.addWidget(self.status_label)
    
    def set_datapoints(self, datapoints: List[Dict]):
        self.datapoints = datapoints
        self.filtered_datapoints = datapoints.copy()
        self._update_field_combo()
        self._update_views()
    
    def _update_field_combo(self):
        self.filter_field_combo.clear()
        
        all_fields = set()
        for dp in self.datapoints:
            all_fields.update(k for k in dp.keys() if not k.startswith('_'))
        
        self.filter_field_combo.addItems(sorted(all_fields))
    
    def _apply_filter(self):
        search_text = self.search_box.text().lower()
        field_name = self.filter_field_combo.currentText()
        field_value = self.filter_value_box.text().lower()
        
        filtered = []
        for dp in self.datapoints:
            if search_text:
                dp_text = json.dumps(dp).lower()
                if search_text not in dp_text:
                    continue
            
            if field_name and field_value:
                if field_name not in dp:
                    continue
                
                dp_val = str(dp[field_name]).lower()
                if field_value not in dp_val:
                    continue
            
            filtered.append(dp)
        
        self.filtered_datapoints = filtered
        self._update_views()
    
    def _clear_filter(self):
        self.search_box.clear()
        self.filter_field_combo.setCurrentIndex(-1)
        self.filter_value_box.clear()
        self.filtered_datapoints = self.datapoints.copy()
        self._update_views()
    
    def _update_views(self):
        self._update_json_view()
        self._update_table_view()
        self.status_label.setText(f"{len(self.filtered_datapoints)} / {len(self.datapoints)} datapoints")
    
    def _update_json_view(self):
        preview = self.filtered_datapoints[:50]
        text = json.dumps(preview, indent=2, ensure_ascii=False)
        if len(self.filtered_datapoints) > 50:
            text += f"\n\n... and {len(self.filtered_datapoints) - 50} more"
        self.json_view.setPlainText(text)
    
    def _update_table_view(self):
        if not self.filtered_datapoints:
            self.table_view.clear()
            return
        
        all_fields = set()
        for dp in self.filtered_datapoints:
            all_fields.update(k for k in dp.keys() if not k.startswith('_'))
        all_fields = sorted(all_fields)
        
        self.table_view.setColumnCount(len(all_fields))
        self.table_view.setHorizontalHeaderLabels(all_fields)
        self.table_view.setRowCount(min(500, len(self.filtered_datapoints)))
        
        for i, dp in enumerate(self.filtered_datapoints[:500]):
            for j, field in enumerate(all_fields):
                value = dp.get(field)
                if isinstance(value, (dict, list)):
                    text = json.dumps(value)
                else:
                    text = str(value) if value is not None else ""
                self.table_view.setItem(i, j, QTableWidgetItem(text))
        
        self.table_view.resizeColumnsToContents()
    
    def _export(self, format_type: str):
        if not self.filtered_datapoints:
            QMessageBox.warning(self, "No Data", "Nothing to export")
            return
        
        filters = {
            "jsonl": "JSONL Files (*.jsonl)",
            "json": "JSON Files (*.json)",
            "csv": "CSV Files (*.csv)"
        }
        
        path, _ = QFileDialog.getSaveFileName(
            self, f"Export as {format_type.upper()}", "", filters[format_type]
        )
        if not path:
            return
        
        try:
            if format_type == "jsonl":
                with open(path, 'w', encoding='utf-8') as f:
                    for dp in self.filtered_datapoints:
                        f.write(json.dumps(dp, ensure_ascii=False) + '\n')
            elif format_type == "json":
                with open(path, 'w', encoding='utf-8') as f:
                    json.dump(self.filtered_datapoints, f, indent=2, ensure_ascii=False)
            elif format_type == "csv":
                import pandas as pd
                df = pd.json_normalize(self.filtered_datapoints)
                df.to_csv(path, index=False)
            
            QMessageBox.information(self, "Exported", f"Saved to {path}")
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Export failed: {e}")
    
    def _copy_to_clipboard(self):
        from PySide6.QtWidgets import QApplication
        text = json.dumps(self.filtered_datapoints[:50], indent=2)
        QApplication.clipboard().setText(text)
        QMessageBox.information(self, "Copied", "First 50 datapoints copied")
