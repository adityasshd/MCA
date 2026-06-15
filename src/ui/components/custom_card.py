from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QEnterEvent, QMouseEvent
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGraphicsDropShadowEffect

class CustomCard(QWidget):
    clicked = pyqtSignal()

    def __init__(self, title: str, description: str, icon: str = "", parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setObjectName("CustomCard")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)
        
        lbl_icon = QLabel(icon)
        lbl_icon.setStyleSheet('font-family: "Noto Color Emoji", "Apple Color Emoji", "Segoe UI Emoji", "Twemoji", sans-serif; font-size: 36px; background: transparent; border: none;')
        if not icon:
            lbl_icon.hide()
        
        lbl_title = QLabel(title)
        lbl_title.setStyleSheet("font-size: 20px; font-weight: bold; color: #E6EDF3; background: transparent; border: none;")
        
        lbl_desc = QLabel(description)
        lbl_desc.setWordWrap(True)
        lbl_desc.setStyleSheet("font-size: 14px; color: #8B949E; background: transparent; border: none; line-height: 1.5;")
        
        layout.addWidget(lbl_icon)
        layout.addWidget(lbl_title)
        layout.addWidget(lbl_desc)
        layout.addStretch()

        # Shadow effect
        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(20)
        self.shadow.setXOffset(0)
        self.shadow.setYOffset(4)
        self.shadow.setColor(QColor(0, 0, 0, 100))
        self.setGraphicsEffect(self.shadow)

        self.setStyleSheet("""
            QWidget#CustomCard {
                background-color: #161B22;
                border-radius: 16px;
                border: 1px solid #30363D;
            }
            QWidget#CustomCard:hover {
                border: 1px solid #58A6FF;
                background-color: #1C2128;
            }
        """)

    def enterEvent(self, event: QEnterEvent) -> None:
        self.shadow.setBlurRadius(30)
        self.shadow.setYOffset(8)
        self.shadow.setColor(QColor(0, 0, 0, 150))
        super().enterEvent(event)

    def leaveEvent(self, event) -> None:
        self.shadow.setBlurRadius(20)
        self.shadow.setYOffset(4)
        self.shadow.setColor(QColor(0, 0, 0, 100))
        super().leaveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
        super().mouseReleaseEvent(event)
