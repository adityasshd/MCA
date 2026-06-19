from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QMouseEvent
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QProgressBar, QHBoxLayout

class UnitCard(QWidget):
    clicked = pyqtSignal()

    def __init__(self, title: str, num_topics: int, estimated_time: str = "30 min", progress: int = 0, parent=None):
        super().__init__(parent)
        self.setProperty("class", "CardPanel")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        
        lbl_title = QLabel(title)
        lbl_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #F8FAFC;")
        lbl_title.setWordWrap(True)
        layout.addWidget(lbl_title)
        
        meta_layout = QHBoxLayout()
        lbl_meta = QLabel(f"{num_topics} Topics • {estimated_time}")
        lbl_meta.setStyleSheet("color: #94A3B8; font-size: 13px;")
        meta_layout.addWidget(lbl_meta)
        meta_layout.addStretch()
        
        # Badge for completion
        if progress == 100:
            lbl_badge = QLabel("✓")
            lbl_badge.setStyleSheet("color: #22C55E; font-weight: bold; font-size: 14px;")
            meta_layout.addWidget(lbl_badge)
            
        layout.addLayout(meta_layout)
        
        layout.addSpacing(10)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(progress)
        self.progress_bar.setFixedHeight(4)
        self.progress_bar.setTextVisible(False)
        layout.addWidget(self.progress_bar)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
        super().mouseReleaseEvent(event)
