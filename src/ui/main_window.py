"""
main_window — PyQt6 Application Shell
=======================================
The main application shell using a Sidebar, Topbar, and persistent AI Chat Panel.
"""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QMainWindow,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
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
from src.ui.infinite_practice_view import InfinitePracticeView
from src.services.practice_service import PracticeService

# Import Components
from src.ui.components.navigation.sidebar import Sidebar
from src.ui.components.navigation.topbar import TopBar
from src.ui.components.chat.ai_chat_panel import AIChatPanel

class MainWindow(QMainWindow):
    def __init__(self, db: DatabaseManager, model_manager: ModelManager):
        super().__init__()
        self.db = db
        self.model_manager = model_manager
        
        self.setWindowTitle("MCA AI Study Suite")
        self.resize(1400, 900)
        self._init_ui()

    def _init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main Horizontal Layout: Sidebar | Center Area | AI Chat
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ── Sidebar ──
        self.sidebar = Sidebar()
        self.sidebar.nav_clicked.connect(self.switch_view)
        main_layout.addWidget(self.sidebar)

        # ── Center Area ──
        self.center_widget = QWidget()
        center_layout = QVBoxLayout(self.center_widget)
        center_layout.setContentsMargins(0, 0, 0, 0)
        center_layout.setSpacing(0)
        
        self.top_bar = TopBar()
        center_layout.addWidget(self.top_bar)
        
        self.content_stack = QStackedWidget()
        center_layout.addWidget(self.content_stack, stretch=1)
        
        main_layout.addWidget(self.center_widget, stretch=1)

        # ── Persistent AI Chat Panel ──
        self.ai_chat_panel = AIChatPanel(self.db, self.model_manager, self)
        # We will keep it hidden by default until they enter the study room, or keep it visible?
        # Let's keep it hidden initially except in Study/Exam modes, or just hide by default.
        self.ai_chat_panel.hide()
        main_layout.addWidget(self.ai_chat_panel)

        # Add actual views
        self.view_dashboard = Dashboard(self.db)
        self.view_dashboard.study_clicked.connect(lambda: self.switch_view(1))
        self.view_dashboard.test_clicked.connect(lambda: self.switch_view(2))
        self.view_dashboard.analytics_clicked.connect(lambda: self.switch_view(3))
        self.view_dashboard.subjects_clicked.connect(lambda: self.switch_view(4))
        self.view_dashboard.practice_clicked.connect(self._launch_practice)
        
        self.view_study = StudyView(self.db, self.model_manager, self.ai_chat_panel)
        self.view_test = TestView(self.db, self.model_manager)
        self.view_analytics = AnalyticsView(self.db, self.model_manager)
        self.view_subjects = SubjectManager(self.db, self.model_manager)
        self.view_settings = SettingsDialog(self.db)
        
        practice_service = PracticeService(self.db, self.view_study.agent)
        self.view_practice = InfinitePracticeView(practice_service)
        self.view_practice.close_clicked.connect(lambda: self.switch_view(0))

        self.content_stack.addWidget(self.view_dashboard) # 0
        self.content_stack.addWidget(self.view_study)     # 1
        self.content_stack.addWidget(self.view_test)      # 2
        self.content_stack.addWidget(self.view_analytics) # 3
        self.content_stack.addWidget(self.view_subjects)  # 4
        self.content_stack.addWidget(self.view_settings)  # 5
        self.content_stack.addWidget(self.view_practice)  # 6

        # View Titles mapping
        self.view_titles = {
            0: "Dashboard",
            1: "Study Room",
            2: "Exam Center",
            3: "Analytics",
            4: "Subjects",
            5: "Settings",
            6: "Infinite Practice"
        }

        self.switch_view(0)

        # ── Status Bar ──
        self.status_bar = self.statusBar()
        config = get_config()
        self.status_bar.showMessage(
            f"Ready | DB: {config.DB_BACKEND.upper()} | Model: {config.TIER1_MODEL}"
        )

    def switch_view(self, index: int):
        self.content_stack.setCurrentIndex(index)
        self.sidebar.set_active(index)
        self.top_bar.set_title(self.view_titles.get(index, ""))
        
        # Show AI Chat only in Study Room or Exam Center (if we wanted to).
        # We can expose a method to show it from inside StudyView.
        # Actually, let's just make it only show up in Study Room for now.
        if index == 1:
            self.ai_chat_panel.show()
        else:
            self.ai_chat_panel.hide()

    def _launch_practice(self, mode: str, subject: str, unit: str, topic: str, mastery: float):
        self.switch_view(6)
        self.view_practice.open_setup(mode, subject, unit, topic, mastery)
