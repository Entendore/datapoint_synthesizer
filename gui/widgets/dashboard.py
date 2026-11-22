"""
dashboard widget stub
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel


class \U\2ashboardWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("dashboard - Coming Soon"))
    
    def set_datapoints(self, datapoints):
        pass
