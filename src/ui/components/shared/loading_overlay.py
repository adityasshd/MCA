from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtGui import QPainter, QColor

class LoadingOverlay(QWidget):
    """
    A semi-transparent loading overlay that intercepts events 
    and displays an animated text message.
    """
    def __init__(self, parent=None, text="Loading..."):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
        # We need to catch all events when active to prevent interaction
        self.hide()
        
        self.base_text = text
        self.dots = 0
        
        self._init_ui()
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._animate_dots)
        self.timer.setInterval(500)
        
    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.lbl_text = QLabel(self.base_text)
        self.lbl_text.setStyleSheet("""
            color: white; 
            font-size: 20px; 
            font-weight: bold;
            background-color: rgba(11, 16, 32, 0.8);
            padding: 20px 40px;
            border-radius: 12px;
            border: 1px solid rgba(255, 255, 255, 0.1);
        """)
        self.lbl_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(self.lbl_text)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(0, 0, 0, 150))
        
    def show_loading(self, text: str | None = None):
        if text:
            self.base_text = text
            
        self.dots = 0
        self.lbl_text.setText(self.base_text)
        self.timer.start()
        
        if self.parent():
            self.resize(self.parent().size())
            self.raise_()
            
        self.show()
        
    def update_text(self, text: str):
        self.base_text = text
        self.lbl_text.setText(f"{self.base_text}{'.' * self.dots}")
        
    def hide_loading(self):
        self.timer.stop()
        self.hide()
        
    def _animate_dots(self):
        self.dots = (self.dots + 1) % 4
        self.lbl_text.setText(f"{self.base_text}{'.' * self.dots}")

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Keep centered if parent resizes
        if self.parent():
            self.resize(self.parent().size())
