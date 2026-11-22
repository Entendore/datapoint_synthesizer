"""
template_library widget stub
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel


class \U\2emplate\U\2ibraryWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("template_library - Coming Soon"))
    
    def set_datapoints(self, datapoints):
        pass
