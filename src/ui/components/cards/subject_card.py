from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QEnterEvent, QMouseEvent
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QProgressBar, QHBoxLayout

class SubjectCard(QWidget):
    clicked = pyqtSignal()

    def __init__(self, title: str, num_units: int, progress: int = 0, last_accessed: str = "Never", parent=None):
        super().__init__(parent)
        self.setProperty("class", "CardPanel")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        lbl_title = QLabel(title)
        lbl_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #F8FAFC;")
        lbl_title.setWordWrap(True)
        layout.addWidget(lbl_title)
        
        # Meta info
        meta_layout = QHBoxLayout()
        lbl_units = QLabel(f"{num_units} Units")
        lbl_units.setStyleSheet("color: #94A3B8; font-size: 13px;")
        
        lbl_accessed = QLabel(f"Last accessed: {last_accessed}")
        lbl_accessed.setStyleSheet("color: #94A3B8; font-size: 13px;")
        
        meta_layout.addWidget(lbl_units)
        meta_layout.addStretch()
        meta_layout.addWidget(lbl_accessed)
        layout.addLayout(meta_layout)
        
        layout.addSpacing(15)
        
        # Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(progress)
        self.progress_bar.setFixedHeight(6)
        self.progress_bar.setTextVisible(False)
        layout.addWidget(self.progress_bar)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
        super().mouseReleaseEvent(event)
