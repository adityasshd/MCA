"""
main_window — PyQt6 Application Shell
=======================================
The main application shell using a QStackedWidget and a sidebar.
"""

from PyQt6.QtCore import Qt, QSize
from PyQt6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
    QPushButton,
)

from src.core.config import get_config
from src.core.database import DatabaseManager
from src.core.models import ModelManager
from src.ui.theme import apply_theme

# Import Views
from src.ui.dashboard import Dashboard
from src.ui.study_view import StudyView
from src.ui.test_view import TestView
from src.ui.analytics_view import AnalyticsView
from src.ui.subject_manager import SubjectManager
from src.ui.settings_dialog import SettingsDialog

# Import Components
from src.ui.components.ai_tutor import AITutorWidget, FloatingActionButton


class MainWindow(QMainWindow):
    def __init__(self, db: DatabaseManager, model_manager: ModelManager):
        super().__init__()
        self.db = db
        self.model_manager = model_manager
        
        self.setWindowTitle("MCA AI Study Suite")
        self.resize(1200, 800)
        self._init_ui()

    def _init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ── Top Bar ──
        self.top_bar = QWidget()
        self.top_bar.setObjectName("TopBar")
        self.top_bar.setStyleSheet("background-color: #161B22; border-bottom: 1px solid #30363D;")
        top_layout = QHBoxLayout(self.top_bar)
        top_layout.setContentsMargins(20, 10, 20, 10)
        
        self.btn_back = QPushButton("← Dashboard")
        self.btn_back.setStyleSheet("background: transparent; color: #58A6FF; font-weight: bold; font-size: 14px; border: none;")
        self.btn_back.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_back.clicked.connect(self.go_home)
        self.btn_back.hide()
        
        lbl_logo = QLabel("MCA AI Study Suite")
        lbl_logo.setStyleSheet("font-size: 18px; font-weight: bold; color: #E6EDF3;")
        
        top_layout.addWidget(self.btn_back)
        top_layout.addStretch()
        top_layout.addWidget(lbl_logo)
        
        main_layout.addWidget(self.top_bar)

        # ── Content Area ──
        self.content_stack = QStackedWidget()
        main_layout.addWidget(self.content_stack, stretch=1)

        # Add actual views
        self.view_dashboard = Dashboard()
        self.view_dashboard.study_clicked.connect(lambda: self.switch_view(1))
        self.view_dashboard.test_clicked.connect(lambda: self.switch_view(2))
        self.view_dashboard.analytics_clicked.connect(lambda: self.switch_view(3))
        self.view_dashboard.subjects_clicked.connect(lambda: self.switch_view(4))
        
        self.view_study = StudyView(self.db, self.model_manager)
        self.view_test = TestView(self.db, self.model_manager)
        self.view_analytics = AnalyticsView(self.db)
        self.view_subjects = SubjectManager(self.db, self.model_manager)
        self.view_settings = SettingsDialog()

        self.content_stack.addWidget(self.view_dashboard) # 0
        self.content_stack.addWidget(self.view_study)     # 1
        self.content_stack.addWidget(self.view_test)      # 2
        self.content_stack.addWidget(self.view_analytics) # 3
        self.content_stack.addWidget(self.view_subjects)  # 4
        self.content_stack.addWidget(self.view_settings)  # 5

        self.go_home()

        # ── Status Bar ──
        self.status_bar = self.statusBar()
        config = get_config()
        self.status_bar.showMessage(
            f"Ready | DB: {config.DB_BACKEND.upper()} | Model: {config.TIER1_MODEL}"
        )

        # ── Floating AI Tutor ──
        self.ai_tutor_widget = AITutorWidget(self.db, self.model_manager, self)
        
        self.fab = FloatingActionButton(self)
        self.fab.clicked.connect(self.toggle_ai_tutor)

    def switch_view(self, index: int):
        self.content_stack.setCurrentIndex(index)
        self.btn_back.show()

    def go_home(self):
        self.content_stack.setCurrentIndex(0)
        self.btn_back.hide()

    def toggle_ai_tutor(self):
        if self.ai_tutor_widget.isVisible():
            self.ai_tutor_widget.hide()
        else:
            self.ai_tutor_widget.show()
            self.ai_tutor_widget.raise_()
            
    def resizeEvent(self, event):
        super().resizeEvent(event)
        fab_x = self.width() - self.fab.width() - 30
        fab_y = self.height() - self.fab.height() - 40
        self.fab.move(fab_x, fab_y)
        
        tutor_x = self.width() - self.ai_tutor_widget.width() - 30
        tutor_y = fab_y - self.ai_tutor_widget.height() - 20
        self.ai_tutor_widget.move(tutor_x, tutor_y)
