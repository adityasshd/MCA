from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QFrame
)

class TopBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("TopBar")
        self.setFixedHeight(70)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 10, 20, 10)
        
        # Page Title (dynamically updated)
        self.lbl_title = QLabel("Dashboard")
        self.lbl_title.setProperty("class", "PageTitle")
        layout.addWidget(self.lbl_title)
        
        layout.addStretch()
        
        # Search Bar
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search syllabus...")
        self.search_bar.setFixedWidth(250)
        self.search_bar.setStyleSheet("""
            QLineEdit {
                background-color: #1A2333;
                border: 1px solid rgba(255,255,255,0.08);
                border-radius: 18px;
                padding: 8px 16px;
                color: #F8FAFC;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 1px solid #3B82F6;
            }
        """)
        layout.addWidget(self.search_bar)
        
        layout.addSpacing(20)
        
        # AI Status Indicator
        self.lbl_ai_status = QLabel("● AI Ready")
        self.lbl_ai_status.setStyleSheet("color: #22C55E; font-weight: bold; font-size: 14px;")
        layout.addWidget(self.lbl_ai_status)

    def set_title(self, title: str):
        self.lbl_title.setText(title)
