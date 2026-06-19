from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt

class PremiumCard(QFrame):
    """
    A premium card container with a title, description, and dynamic content area.
    Provides hover effects via QSS in theme.py.
    """
    def __init__(self, title: str, description: str = "", parent=None):
        super().__init__(parent)
        self.setProperty("class", "CardPanel")
        
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(20, 20, 20, 20)
        self._layout.setSpacing(12)
        
        self.title_label = QLabel(title)
        self.title_label.setProperty("class", "CardTitle")
        self._layout.addWidget(self.title_label)
        
        if description:
            self.desc_label = QLabel(description)
            self.desc_label.setProperty("class", "MetaText")
            self.desc_label.setWordWrap(True)
            self._layout.addWidget(self.desc_label)
            
        self.content_layout = QVBoxLayout()
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self._layout.addLayout(self.content_layout)
        
    def add_widget(self, widget):
        self.content_layout.addWidget(widget)
        
    def add_layout(self, layout):
        self.content_layout.addLayout(layout)
