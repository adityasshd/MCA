from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QColor, QPen, QFont
from PyQt6.QtCore import Qt, QRectF
from src.ui.theme import COLORS

class ProgressRing(QWidget):
    """
    A circular progress indicator (donut chart style) for Mastery.
    """
    def __init__(self, value: float = 0.0, label: str = "Mastery", parent=None):
        super().__init__(parent)
        self.value = value  # 0.0 to 1.0
        self.label = label
        self.setMinimumSize(100, 100)

    def setValue(self, value: float):
        self.value = max(0.0, min(1.0, value))
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = QRectF(10, 10, self.width() - 20, self.height() - 20)
        
        # Background ring
        pen_bg = QPen(QColor(COLORS["border"]))
        pen_bg.setWidth(8)
        pen_bg.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen_bg)
        painter.drawArc(rect, 0, 360 * 16)
        
        # Foreground ring
        val_color = COLORS["danger"]
        if self.value >= 0.8:
            val_color = COLORS["success"]
        elif self.value >= 0.5:
            val_color = COLORS["warning"]
            
        pen_fg = QPen(QColor(val_color))
        pen_fg.setWidth(8)
        pen_fg.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen_fg)
        
        # Qt angles are in 1/16th of a degree, starting at 3 o'clock. 
        # We want to start at 12 o'clock (90 degrees).
        span_angle = int(-self.value * 360 * 16)
        start_angle = 90 * 16
        painter.drawArc(rect, start_angle, span_angle)
        
        # Draw Text
        painter.setPen(QColor(COLORS["text_primary"]))
        font = QFont()
        font.setPixelSize(18)
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, f"{int(self.value * 100)}%")
