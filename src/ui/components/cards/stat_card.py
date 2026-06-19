from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QEnterEvent, QMouseEvent
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel

class StatCard(QWidget):
    def __init__(self, title: str, value: str, parent=None):
        super().__init__(parent)
        self.setProperty("class", "CardPanel")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        lbl_title = QLabel(title)
        lbl_title.setStyleSheet("color: #94A3B8; font-size: 14px; font-weight: bold;")
        
        lbl_value = QLabel(value)
        lbl_value.setStyleSheet("color: #F8FAFC; font-size: 32px; font-weight: bold;")
        
        layout.addWidget(lbl_title)
        layout.addWidget(lbl_value)
        layout.addStretch()

    def update_value(self, new_value: str):
        # Update the value label if needed dynamically
        self.layout().itemAt(1).widget().setText(new_value)
