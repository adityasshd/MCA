from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from src.ui.theme import COLORS

class KPIWidget(QWidget):
    """
    A specialized compact widget for displaying a single metric.
    E.g., [ 5.2h ]
          Study Time
    """
    def __init__(self, value: str, label: str, parent=None):
        super().__init__(parent)
        self.setProperty("class", "CardPanel")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(4)
        
        self.val_label = QLabel(value)
        self.val_label.setStyleSheet(f"font-size: 24px; font-weight: bold; color: {COLORS['primary']};")
        
        self.title_label = QLabel(label)
        self.title_label.setProperty("class", "MetaText")
        
        layout.addWidget(self.val_label)
        layout.addWidget(self.title_label)

    def set_value(self, value: str):
        self.val_label.setText(value)
