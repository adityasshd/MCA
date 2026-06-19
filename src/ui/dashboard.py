from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QScrollArea, QFrame, QPushButton, QGridLayout
)

from src.core.database import DatabaseManager
from src.ui.components.shared.card import PremiumCard
from src.ui.components.shared.badge import Badge
from src.ui.components.shared.progress_ring import ProgressRing
from src.ui.components.shared.kpi_widget import KPIWidget
from src.ui.theme import COLORS

class Dashboard(QWidget):
    study_clicked = pyqtSignal()
    test_clicked = pyqtSignal()
    analytics_clicked = pyqtSignal()
    practice_clicked = pyqtSignal(str, str, str, str, float) # mode, subject, unit, topic, mastery
    subjects_clicked = pyqtSignal()

    def __init__(self, db: DatabaseManager, parent=None):
        super().__init__(parent)
        self.db = db
        
        # State for Quick Practice
        self.qp_subject = ""
        self.qp_unit = ""
        self.qp_topic = ""
        self.qp_mastery = 0.0
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        
        self.container = QWidget()
        self.container.setStyleSheet("background-color: transparent;")
        self.layout = QVBoxLayout(self.container)
        self.layout.setContentsMargins(40, 50, 40, 50)
        self.layout.setSpacing(40)
        
        # ── Header ──
        header_layout = QHBoxLayout()
        welcome_layout = QVBoxLayout()
        welcome_layout.setSpacing(4)
        
        lbl_welcome = QLabel("Good morning, Aditya")
        lbl_welcome.setProperty("class", "PageTitle")
        
        lbl_sub = QLabel("Let's hit your learning goals for this week.")
        lbl_sub.setProperty("class", "BodyText")
        
        welcome_layout.addWidget(lbl_welcome)
        welcome_layout.addWidget(lbl_sub)
        
        header_layout.addLayout(welcome_layout)
        header_layout.addStretch()
        self.layout.addLayout(header_layout)
        
        # ── KPIs ──
        self.kpi_layout = QHBoxLayout()
        self.kpi_layout.setSpacing(20)
        
        self.kpi_study = KPIWidget("0h", "Study Time this Week")
        self.kpi_exams = KPIWidget("0", "Exams Simulated")
        self.kpi_mastery = KPIWidget("0%", "Avg Mastery Score")
        self.kpi_streak = KPIWidget("0", "Day Streak")
        
        self.kpi_layout.addWidget(self.kpi_study)
        self.kpi_layout.addWidget(self.kpi_exams)
        self.kpi_layout.addWidget(self.kpi_mastery)
        self.kpi_layout.addWidget(self.kpi_streak)
        
        self.layout.addLayout(self.kpi_layout)
        
        # ── Main Content Grid ──
        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(20)
        
        # 1. Quick Practice
        self.qp_card = PremiumCard("Quick Practice", "Jump into an infinite practice session.")
        qp_layout = QVBoxLayout()
        qp_layout.setSpacing(10)
        
        self.lbl_qp = QLabel("Calculating your top priority topic...")
        self.lbl_qp.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 15px;")
        self.lbl_qp.setWordWrap(True)
        qp_layout.addWidget(self.lbl_qp)
        
        self.btn_prac_random = QPushButton("🎲 Random Practice")
        self.btn_prac_random.setProperty("class", "SecondaryButton")
        self.btn_prac_random.clicked.connect(lambda: self._on_practice_clicked("random"))
        
        self.btn_prac_subject = QPushButton("📚 Practice By Subject")
        self.btn_prac_subject.setProperty("class", "SecondaryButton")
        self.btn_prac_subject.clicked.connect(lambda: self._on_practice_clicked("subject"))

        self.btn_prac_topic = QPushButton("🎯 Practice By Topic")
        self.btn_prac_topic.setProperty("class", "SecondaryButton")
        self.btn_prac_topic.clicked.connect(lambda: self._on_practice_clicked("topic"))

        self.btn_prac_weak = QPushButton("⚠️ Practice Weak Areas")
        self.btn_prac_weak.setProperty("class", "PrimaryButton")
        self.btn_prac_weak.clicked.connect(lambda: self._on_practice_clicked("weak"))
        
        qp_layout.addWidget(self.btn_prac_random)
        qp_layout.addWidget(self.btn_prac_subject)
        qp_layout.addWidget(self.btn_prac_topic)
        qp_layout.addWidget(self.btn_prac_weak)
        
        self.qp_card.add_layout(qp_layout)
        self.grid_layout.addWidget(self.qp_card, 0, 0, 1, 2)
        
        # 2. Continue Learning
        self.continue_card = PremiumCard("Continue Learning", "Jump back into your recent subjects.")
        self.cl_layout = QVBoxLayout()
        self.cl_layout.setSpacing(12)
        self.continue_card.add_layout(self.cl_layout)
        self.grid_layout.addWidget(self.continue_card, 1, 0)
        
        # 3. Learning Insights (Weak Topics)
        self.insights_card = PremiumCard("Weak Topics", "Topics needing your attention.")
        self.in_layout = QVBoxLayout()
        self.in_layout.setSpacing(12)
        
        self.btn_view_analytics = QPushButton("View Full Mastery Map")
        self.btn_view_analytics.setProperty("class", "SecondaryButton")
        self.btn_view_analytics.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_view_analytics.clicked.connect(self.analytics_clicked.emit)
        
        self.insights_card.add_layout(self.in_layout)
        self.grid_layout.addWidget(self.insights_card, 1, 1)
        
        # 4. Recent Activity
        self.activity_card = PremiumCard("Recent Activity", "Your latest accomplishments.")
        self.act_layout = QVBoxLayout()
        self.act_layout.setSpacing(12)
        self.activity_card.add_layout(self.act_layout)
        self.grid_layout.addWidget(self.activity_card, 2, 0, 1, 2)
        
        self.grid_layout.setColumnStretch(0, 3)
        self.grid_layout.setColumnStretch(1, 2)
        
        self.layout.addLayout(self.grid_layout)
        self.layout.addStretch()
        
        self.scroll.setWidget(self.container)
        main_layout.addWidget(self.scroll)
        
        self.refresh_data()

    def refresh_data(self):
        """Fetches live data from the DatabaseManager and updates UI."""
        # Update KPIs
        exams = self.db.exams.get_all()
        self.kpi_exams.set_value(str(len(exams)))
        
        # User Stats
        stats = self.db.users.get_stats()
        if stats:
            self.kpi_study.set_value(f"{stats.total_study_hours:.1f}h")
            self.kpi_streak.set_value(str(stats.current_streak))
        else:
            self.kpi_study.set_value("0h")
            self.kpi_streak.set_value("0")
        
        # Average Mastery
        topics = self.db.weak_topics.get_weakest(limit=100)
        if topics:
            avg = sum(t.mastery_score for t in topics) / len(topics)
            self.kpi_mastery.set_value(f"{int(avg * 100)}%")
        else:
            self.kpi_mastery.set_value("0%")
            
        # Recent Activity
        while self.act_layout.count():
            w = self.act_layout.takeAt(0).widget()
            if w: w.deleteLater()
            
        events = self.db.analytics.query(limit=5)
        for event in events:
            row = QFrame()
            row.setStyleSheet(f"background-color: {COLORS['bg_surface']}; border-radius: 8px;")
            r_layout = QHBoxLayout(row)
            r_layout.setContentsMargins(12, 12, 12, 12)
            
            vbox = QVBoxLayout()
            lbl_action = QLabel(event.event_type.replace("_", " ").title())
            lbl_action.setStyleSheet("font-weight: bold; font-size: 14px;")
            lbl_subj2 = QLabel(event.subject)
            lbl_subj2.setProperty("class", "MetaText")
            
            vbox.addWidget(lbl_action)
            vbox.addWidget(lbl_subj2)
            
            r_layout.addLayout(vbox)
            r_layout.addStretch()
            r_layout.addWidget(Badge("Logged", "info"))
            self.act_layout.addWidget(row)
            
        if not events:
            self.act_layout.addWidget(QLabel("No recent activity. Start studying!"))
            
        # Weak Topics & Quick Practice
        while self.in_layout.count():
            w = self.in_layout.takeAt(0).widget()
            if w: w.deleteLater()
            
        weakest = self.db.weak_topics.get_weakest(limit=3)
        if weakest:
            top_weak = weakest[0]
            self.qp_subject = top_weak.subject
            self.qp_unit = top_weak.unit
            self.qp_topic = top_weak.topic
            self.qp_mastery = top_weak.mastery_score
            self.lbl_qp.setText(f"Our AI has identified <b>{top_weak.topic}</b> ({int(top_weak.mastery_score*100)}% mastery) as your top priority.")
        else:
            self.qp_subject = "General"
            self.qp_unit = ""
            self.qp_topic = "General Knowledge"
            self.qp_mastery = 0.5
            self.lbl_qp.setText("You don't have any weak topics yet. We'll start with general practice.")
            
        for t in weakest:
            row = QFrame()
            row.setStyleSheet(f"background-color: {COLORS['bg_surface']}; border-radius: 8px;")
            r_layout = QHBoxLayout(row)
            
            lbl_topic = QLabel(t.topic)
            lbl_topic.setProperty("class", "BodyText")
            
            r_layout.addWidget(lbl_topic)
            r_layout.addStretch()
            
            status = "danger" if t.mastery_score < 0.5 else "warning"
            r_layout.addWidget(Badge("Review Required", status))
            self.in_layout.addWidget(row)
            
        if not weakest:
            self.in_layout.addWidget(QLabel("No weak topics identified yet."))
            
        self.in_layout.addStretch()
        self.in_layout.addWidget(self.btn_view_analytics)
        
        # Continue Learning
        while self.cl_layout.count():
            w = self.cl_layout.takeAt(0).widget()
            if w: w.deleteLater()
            
        sessions = self.db.sessions.get_recent(limit=3)
        for s in sessions:
            row = QFrame()
            row.setStyleSheet(f"background-color: {COLORS['bg_surface']}; border-radius: 8px;")
            r_layout = QHBoxLayout(row)
            r_layout.setContentsMargins(12, 12, 12, 12)
            
            info_vbox = QVBoxLayout()
            lbl_subj = QLabel(s.subject)
            lbl_subj.setStyleSheet("font-weight: bold; font-size: 14px;")
            lbl_unit = QLabel(s.unit or "General")
            lbl_unit.setProperty("class", "MetaText")
            info_vbox.addWidget(lbl_subj)
            info_vbox.addWidget(lbl_unit)
            
            r_layout.addLayout(info_vbox)
            r_layout.addStretch()
            
            btn_go = QPushButton("Study")
            btn_go.setProperty("class", "SecondaryButton")
            btn_go.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_go.clicked.connect(self.study_clicked.emit)
            r_layout.addWidget(btn_go)
            
            self.cl_layout.addWidget(row)
            
        if not sessions:
            self.cl_layout.addWidget(QLabel("No recent study sessions."))

    def _on_practice_clicked(self, mode: str):
        self.practice_clicked.emit(mode, self.qp_subject, self.qp_unit, self.qp_topic, self.qp_mastery)

