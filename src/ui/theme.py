"""
theme — PyQt6 Styling and QSS
==============================
Applies modern, premium dark aesthetic and provides utility functions.
"""

import re
import qdarktheme
from PyQt6.QtGui import QColor, QFont
from PyQt6.QtWidgets import QApplication

# ── Color Palette ────────────────────────────────────────────────────────

COLORS = {
    "bg_primary": "#0A0F1C",
    "bg_surface": "#111827",
    "bg_elevated": "#172033",
    "bg_surface_light": "#1F2937",
    "primary": "#4F8CFF",
    "primary_hover": "#6CA3FF",
    "success": "#22C55E",
    "warning": "#F59E0B",
    "danger": "#EF4444",
    "text_primary": "#F8FAFC",
    "text_secondary": "#94A3B8",
    "border": "#273449",
}


def get_color(name: str) -> QColor:
    c = COLORS.get(name, "#FFFFFF")
    if c.startswith("rgba"):
        # Parse rgba string if necessary, though QColor supports many formats
        return QColor(c)
    return QColor(c)


def format_title_case(text: str) -> str:
    """
    Converts messy strings like 'ANALYTICAL_SKILLS-I' 
    into 'Analytical Skills I'.
    """
    if not text:
        return ""
    # Replace underscores and hyphens with spaces
    text = text.replace("_", " ").replace("-", " ")
    
    # Identify roman numerals at the end
    words = text.split()
    formatted_words = []
    
    roman_numerals = {"I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X"}
    
    for word in words:
        if word.upper() in roman_numerals:
            formatted_words.append(word.upper())
        elif word.lower() == "and":
            formatted_words.append("&")
        else:
            formatted_words.append(word.capitalize())
            
    return " ".join(formatted_words)


# ── Custom QSS Overrides ──────────────────────────────────────────────────

CUSTOM_QSS = f"""
* {{
    font-family: "Inter", "Roboto", "Segoe UI", "Helvetica Neue", sans-serif;
}}

/* Global Backgrounds */
QMainWindow, QDialog, QStackedWidget {{
    background-color: {COLORS["bg_primary"]};
}}

/* Top Bar and Sidebar */
QWidget#TopBar {{
    background-color: {COLORS["bg_primary"]};
    border-bottom: 1px solid {COLORS["border"]};
}}

QWidget#Sidebar {{
    background-color: {COLORS["bg_surface"]};
    border-right: 1px solid {COLORS["border"]};
}}

/* Cards and Panels */
QFrame.CardPanel, QWidget.CardPanel {{
    background-color: {COLORS["bg_elevated"]};
    border: 1px solid {COLORS["border"]};
    border-radius: 16px;
}}
QFrame.CardPanel:hover, QWidget.CardPanel:hover {{
    border: 1px solid {COLORS["primary"]};
    background-color: {COLORS["bg_surface_light"]};
}}

/* Markdown Browser */
QTextBrowser {{
    background-color: {COLORS["bg_primary"]};
    color: {COLORS["text_primary"]};
    border: none;
    font-size: 16px;
    line-height: 1.8;
    padding: 20px;
}}

/* Scrollbars */
QScrollBar:vertical {{
    border: none;
    background: transparent;
    width: 8px;
    margin: 0px 0px 0px 0px;
}}
QScrollBar::handle:vertical {{
    background: #334155;
    min-height: 20px;
    border-radius: 4px;
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    border: none;
    background: none;
}}

/* Progress Bars */
QProgressBar {{
    background-color: {COLORS["bg_elevated"]};
    border: 1px solid {COLORS["border"]};
    border-radius: 4px;
    text-align: center;
    color: {COLORS["text_primary"]};
    font-size: 12px;
}}
QProgressBar::chunk {{
    background-color: {COLORS["success"]};
    border-radius: 3px;
}}

/* Labels */
QLabel.LargeTitle {{
    font-size: 36px;
    font-weight: bold;
    color: {COLORS["text_primary"]};
}}
QLabel.PageTitle {{
    font-size: 32px;
    font-weight: bold;
    color: {COLORS["text_primary"]};
}}
QLabel.SectionTitle {{
    font-size: 24px;
    font-weight: bold;
    color: {COLORS["text_primary"]};
}}
QLabel.CardTitle {{
    font-size: 18px;
    font-weight: 600;
    color: {COLORS["text_primary"]};
}}
QLabel.BodyText {{
    font-size: 14px;
    color: {COLORS["text_secondary"]};
}}
QLabel.MetaText {{
    font-size: 12px;
    color: {COLORS["text_secondary"]};
}}

/* Buttons */
QPushButton.PrimaryButton {{
    background-color: {COLORS["primary"]};
    color: white;
    font-weight: 600;
    border-radius: 8px;
    padding: 10px 16px;
    border: none;
}}
QPushButton.PrimaryButton:hover {{
    background-color: {COLORS["primary_hover"]};
}}
QPushButton.SecondaryButton {{
    background-color: {COLORS["bg_elevated"]};
    color: {COLORS["text_primary"]};
    font-weight: bold;
    border-radius: 8px;
    padding: 10px 16px;
    border: 1px solid {COLORS["border"]};
}}
QPushButton.SecondaryButton:hover {{
    background-color: #334155;
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
                "primary": COLORS["primary"],
                "background": COLORS["bg_primary"],
                "border": COLORS["border"],
            }
        }
    )
    
    # Append our custom QSS overrides
    app.setStyleSheet(app.styleSheet() + "\n" + CUSTOM_QSS)

    # Use a robust cross-platform fallback for the base font
    font = QFont()
    font.setFamilies(["Inter", "Roboto", "Segoe UI", "Helvetica Neue", "sans-serif"])
    font.setPointSize(11)
    font.setStyleHint(QFont.StyleHint.SansSerif)
    app.setFont(font)
