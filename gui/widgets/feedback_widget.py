"""
feedback_widget widget stub
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel


class \U\2eedback\U\2idgetWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("feedback_widget - Coming Soon"))
    
    def set_datapoints(self, datapoints):
        pass
