"""
visualizations widget stub
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel


class \U\2isualizationsWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("visualizations - Coming Soon"))
    
    def set_datapoints(self, datapoints):
        pass
