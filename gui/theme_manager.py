"""
Theme management for the GUI
"""

from PySide6.QtWidgets import QApplication


class ThemeManager:
    """Manages dark/light themes with QSS styling."""
    
    DARK_THEME = """
    QMainWindow, QWidget { background-color: #1e1e2e; color: #cdd6f4; }
    QGroupBox { 
        background-color: #313244; border: 1px solid #45475a; 
        border-radius: 8px; margin-top: 12px; padding-top: 16px;
        font-weight: bold; color: #89b4fa;
    }
    QGroupBox::title { subcontrol-origin: margin; left: 12px; padding: 0 6px; }
    QPushButton { 
        background-color: #89b4fa; color: #1e1e2e; border: none;
        padding: 8px 16px; border-radius: 6px; font-weight: bold;
    }
    QPushButton:hover { background-color: #b4befe; }
    QPushButton:pressed { background-color: #74c7ec; }
    QPushButton:disabled { background-color: #45475a; color: #6c7086; }
    QLineEdit, QTextEdit, QSpinBox, QDoubleSpinBox, QComboBox {
        background-color: #313244; color: #cdd6f4; border: 1px solid #45475a;
        border-radius: 4px; padding: 6px; selection-background-color: #89b4fa;
    }
    QLineEdit:focus, QTextEdit:focus { border: 1px solid #89b4fa; }
    QTabWidget::pane { border: 1px solid #45475a; border-radius: 4px; }
    QTabBar::tab { 
        background-color: #313244; color: #a6adc8; padding: 8px 16px;
        border-top-left-radius: 4px; border-top-right-radius: 4px;
        margin-right: 2px;
    }
    QTabBar::tab:selected { background-color: #45475a; color: #89b4fa; font-weight: bold; }
    QTreeWidget, QListWidget, QTableWidget {
        background-color: #313244; border: 1px solid #45475a; border-radius: 4px;
    }
    QTreeWidget::item:selected, QListWidget::item:selected { 
        background-color: #45475a; color: #89b4fa; 
    }
    QHeaderView::section { 
        background-color: #45475a; color: #cdd6f4; padding: 6px;
        border: none; border-right: 1px solid #313244;
    }
    QScrollBar:vertical { background: #1e1e2e; width: 10px; }
    QScrollBar::handle:vertical { background: #45475a; border-radius: 5px; min-height: 20px; }
    QMenuBar { background-color: #181825; color: #cdd6f4; }
    QMenuBar::item:selected { background-color: #313244; }
    QMenu { background-color: #313244; color: #cdd6f4; border: 1px solid #45475a; }
    QMenu::item:selected { background-color: #45475a; }
    QStatusBar { background-color: #181825; color: #a6adc8; }
    QProgressBar { 
        border: 1px solid #45475a; border-radius: 4px; text-align: center;
        background-color: #313244; color: #cdd6f4;
    }
    QProgressBar::chunk { background-color: #a6e3a1; border-radius: 3px; }
    QSplitter::handle { background-color: #45475a; }
    """
    
    LIGHT_THEME = """
    QMainWindow, QWidget { background-color: #eff1f5; color: #4c4f69; }
    QGroupBox { 
        background-color: #ffffff; border: 1px solid #ccd0da; 
        border-radius: 8px; margin-top: 12px; padding-top: 16px;
        font-weight: bold; color: #1e66f5;
    }
    QPushButton { 
        background-color: #1e66f5; color: #ffffff; border: none;
        padding: 8px 16px; border-radius: 6px; font-weight: bold;
    }
    QPushButton:hover { background-color: #2a6ef5; }
    QLineEdit, QTextEdit, QSpinBox, QDoubleSpinBox, QComboBox {
        background-color: #ffffff; color: #4c4f69; border: 1px solid #ccd0da;
        border-radius: 4px; padding: 6px;
    }
    QTabBar::tab:selected { background-color: #ffffff; color: #1e66f5; font-weight: bold; }
    QTreeWidget::item:selected { background-color: #ccd0da; color: #1e66f5; }
    QProgressBar::chunk { background-color: #40a02b; }
    """
    
    @staticmethod
    def apply_theme(app: QApplication, theme: str = "dark"):
        if theme == "dark":
            app.setStyleSheet(ThemeManager.DARK_THEME)
        else:
            app.setStyleSheet(ThemeManager.LIGHT_THEME)
