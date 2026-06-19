from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QPushButton,
    QLabel,
    QFrame,
    QSpacerItem,
    QSizePolicy
)

class SidebarButton(QPushButton):
    def __init__(self, text, icon_text="", parent=None):
        super().__init__(text, parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setCheckable(True)
        # Using emoji/text for icon temporarily if no real icon
        self.icon_text = icon_text
        
        self.setStyleSheet("""
            QPushButton {
                text-align: left;
                padding: 12px 20px;
                border: none;
                border-radius: 8px;
                color: #94A3B8;
                font-size: 15px;
                font-weight: bold;
                background-color: transparent;
                margin: 2px 10px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.05);
                color: #F8FAFC;
            }
            QPushButton:checked {
                background-color: rgba(59, 130, 246, 0.15);
                color: #3B82F6;
                border-left: 4px solid #3B82F6;
            }
        """)

class Sidebar(QWidget):
    # Signals for navigation
    nav_clicked = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("Sidebar")
        self.setFixedWidth(260)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 20, 0, 20)
        layout.setSpacing(8)
        
        # Logo/Brand Area
        brand_layout = QVBoxLayout()
        brand_layout.setContentsMargins(20, 0, 20, 20)
        lbl_logo = QLabel("🎓 MCA AI Study")
        lbl_logo.setStyleSheet("font-size: 20px; font-weight: bold; color: #F8FAFC;")
        brand_layout.addWidget(lbl_logo)
        
        layout.addLayout(brand_layout)
        
        # Navigation Buttons
        self.buttons = []
        
        nav_items = [
            ("Dashboard", 0),
            ("Study Room", 1),
            ("Exam Center", 2),
            ("Analytics", 3),
            ("Subjects", 4),
        ]
        
        for text, index in nav_items:
            btn = SidebarButton(text)
            btn.clicked.connect(lambda checked, idx=index: self._on_nav_clicked(idx))
            self.buttons.append(btn)
            layout.addWidget(btn)
            
        layout.addStretch()
        
        # Settings at bottom
        self.btn_settings = SidebarButton("Settings")
        self.btn_settings.clicked.connect(lambda: self._on_nav_clicked(5))
        self.buttons.append(self.btn_settings)
        layout.addWidget(self.btn_settings)
        
        # Select first by default
        self.set_active(0)

    def _on_nav_clicked(self, index: int):
        self.set_active(index)
        self.nav_clicked.emit(index)
        
    def set_active(self, index: int):
        # Update checked state
        for idx, btn in enumerate(self.buttons):
            # Buttons match the indices 0..4 for main, and 5 for settings. 
            # In our list `self.buttons`, the indices map perfectly if they are in order.
            btn.setChecked(idx == index)
