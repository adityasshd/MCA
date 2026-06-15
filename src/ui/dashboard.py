from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QWidget, QGridLayout, QVBoxLayout, QLabel

from src.ui.components.custom_card import CustomCard

class Dashboard(QWidget):
    # Signals to inform MainWindow to switch views
    study_clicked = pyqtSignal()
    test_clicked = pyqtSignal()
    analytics_clicked = pyqtSignal()
    subjects_clicked = pyqtSignal()
    settings_clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        
        lbl_welcome = QLabel("Welcome to MCA AI Study Suite")
        lbl_welcome.setStyleSheet("font-size: 28px; font-weight: bold; color: white;")
        layout.addWidget(lbl_welcome, alignment=Qt.AlignmentFlag.AlignCenter)
        
        lbl_sub = QLabel("Select a module to begin")
        lbl_sub.setStyleSheet("font-size: 16px; color: #8B949E;")
        layout.addWidget(lbl_sub, alignment=Qt.AlignmentFlag.AlignCenter)
        
        layout.addSpacing(40)
        
        grid = QGridLayout()
        grid.setSpacing(30)
        
        card_study = CustomCard(
            "Study Room",
            "Browse textbooks, generate AI Study Guides, and ask the AI Tutor questions with interactive RAG retrieval.",
            ""
        )
        card_study.clicked.connect(self.study_clicked.emit)
        grid.addWidget(card_study, 0, 0)
        
        card_test = CustomCard(
            "Exam Center",
            "Generate AI exams with MCQs, True/False, and short-answers. Take tests in list or paginated view with AI feedback.",
            ""
        )
        card_test.clicked.connect(self.test_clicked.emit)
        grid.addWidget(card_test, 0, 1)
        
        card_analytics = CustomCard(
            "Analytics",
            "Track your performance over time. View exam history, score trends, and strengths/weaknesses graphs.",
            ""
        )
        card_analytics.clicked.connect(self.analytics_clicked.emit)
        grid.addWidget(card_analytics, 1, 0)
        
        card_subjects = CustomCard(
            "Subjects Manager",
            "Upload textbook PDFs, configure chapters, and view current indexing state in the RAG pipeline.",
            ""
        )
        card_subjects.clicked.connect(self.subjects_clicked.emit)
        grid.addWidget(card_subjects, 1, 1)
        
        # We can add Settings later if needed, or put it in the top bar
        
        layout.addLayout(grid)
        layout.addStretch()
