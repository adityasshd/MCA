from PyQt6.QtWidgets import QLabel
from PyQt6.QtCore import Qt
from src.ui.theme import COLORS

class Badge(QLabel):
    """
    A small rounded badge for status (Success, Warning, Danger, Info).
    """
    def __init__(self, text: str, status: str = "info", parent=None):
        super().__init__(text, parent)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        bg_color = {
            "success": f"{COLORS['success']}20",
            "warning": f"{COLORS['warning']}20",
            "danger": f"{COLORS['danger']}20",
            "info": f"{COLORS['primary']}20"
        }.get(status, f"{COLORS['primary']}20")
        
        text_color = {
            "success": COLORS["success"],
            "warning": COLORS["warning"],
            "danger": COLORS["danger"],
            "info": COLORS["primary"]
        }.get(status, COLORS["primary"])
        
        self.setStyleSheet(f"""
            QLabel {{
                background-color: {bg_color};
                color: {text_color};
                border-radius: 6px;
                padding: 4px 8px;
                font-size: 11px;
                font-weight: bold;
            }}
        """)
