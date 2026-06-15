"""
settings_dialog — App Configuration
====================================
A basic settings view showing current configuration.
"""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QFormLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)

from src.core.config import get_config


class SettingsDialog(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        
        lbl_title = QLabel("Settings & Configuration")
        lbl_title.setProperty("class", "HeaderLabel")
        layout.addWidget(lbl_title)
        
        form_layout = QFormLayout()
        
        config = get_config()
        
        # We just show current config read from .env
        form_layout.addRow("Database Backend:", QLabel(config.DB_BACKEND))
        form_layout.addRow("Fast Model (Tier 1):", QLabel(f"{config.TIER1_PROVIDER} / {config.TIER1_MODEL}"))
        form_layout.addRow("Reasoning Model (Tier 2):", QLabel(f"{config.TIER2_PROVIDER} / {config.TIER2_MODEL}"))
        form_layout.addRow("Embedding Provider:", QLabel(config.EMBEDDING_PROVIDER))
        
        layout.addLayout(form_layout)
        layout.addStretch()
