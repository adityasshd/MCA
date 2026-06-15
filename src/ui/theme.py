"""
theme — PyQt6 Styling and QSS
==============================
Applies qdarktheme and custom QSS overrides to match the dark aesthetic.
"""

import qdarktheme
from PyQt6.QtGui import QColor, QFont
from PyQt6.QtWidgets import QApplication

# ── Color Palette ────────────────────────────────────────────────────────

COLORS = {
    "bg_primary": "#0D1117",
    "bg_surface": "#161B22",
    "bg_elevated": "#1C2128",
    "accent_blue": "#58A6FF",
    "accent_orange": "#F78166",
    "accent_green": "#3FB950",
    "accent_purple": "#BC8CFF",
    "text_primary": "#C9D1D9",
    "text_muted": "#8B949E",
    "border": "#30363D",
}


def get_color(name: str) -> QColor:
    return QColor(COLORS.get(name, "#FFFFFF"))


# ── Custom QSS Overrides ──────────────────────────────────────────────────

CUSTOM_QSS = f"""
* {{
    font-family: "Inter", "Segoe UI", "Ubuntu", "Helvetica Neue", sans-serif;
}}

/* Global Backgrounds */
QMainWindow, QDialog, QStackedWidget {{
    background-color: {COLORS["bg_primary"]};
}}

/* Top Bar */
QWidget#TopBar {{
    background-color: {COLORS["bg_surface"]};
    border-bottom: 1px solid {COLORS["border"]};
}}

/* Cards and Panels */
QFrame.CardPanel {{
    background-color: {COLORS["bg_surface"]};
    border: 1px solid {COLORS["border"]};
    border-radius: 12px;
}}

/* Markdown Browser */
QTextBrowser {{
    background-color: {COLORS["bg_surface"]};
    border: none;
    font-size: 14px;
    line-height: 1.6;
    padding: 10px;
}}

/* Progress Bars */
QProgressBar {{
    background-color: {COLORS["bg_elevated"]};
    border: 1px solid {COLORS["border"]};
    border-radius: 4px;
    text-align: center;
    color: {COLORS["text_primary"]};
}}
QProgressBar::chunk {{
    background-color: {COLORS["accent_green"]};
    border-radius: 3px;
}}

/* Labels */
QLabel.HeaderLabel {{
    font-size: 22px;
    font-weight: bold;
    color: {COLORS["text_primary"]};
}}
QLabel.SubheaderLabel {{
    font-size: 15px;
    color: {COLORS["text_muted"]};
}}
"""

def apply_theme(app: QApplication) -> None:
    """Apply the global dark theme and custom QSS to the application."""
    app.setStyle("Fusion")
    
    # Setup base dark theme with our primary color
    qdarktheme.setup_theme(
        theme="dark",
        custom_colors={
            "[dark]": {
                "primary": COLORS["accent_blue"],
            }
        }
    )
    
    # Append our custom QSS overrides
    app.setStyleSheet(app.styleSheet() + "\n" + CUSTOM_QSS)

    # Use a robust cross-platform fallback for the base font
    font = QFont()
    font.setFamilies(["Segoe UI", "Ubuntu", "Helvetica Neue", "Inter", "sans-serif"])
    font.setPointSize(10)
    font.setStyleHint(QFont.StyleHint.SansSerif)
    app.setFont(font)
