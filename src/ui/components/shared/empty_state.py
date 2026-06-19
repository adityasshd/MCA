from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt
from src.ui.theme import COLORS

class EmptyState(QWidget):
    """
    A placeholder for empty lists or unselected states.
    """
    def __init__(self, title: str, message: str, parent=None):
        super().__init__(parent)
        
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(8)
        
        icon_label = QLabel("🎯")
        icon_label.setStyleSheet("font-size: 48px;")
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        title_label = QLabel(title)
        title_label.setProperty("class", "SectionTitle")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        msg_label = QLabel(message)
        msg_label.setProperty("class", "BodyText")
        msg_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        msg_label.setWordWrap(True)
        msg_label.setMaximumWidth(300)
        
        layout.addWidget(icon_label)
        layout.addWidget(title_label)
        layout.addWidget(msg_label)
