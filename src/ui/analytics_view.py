"""
analytics_view — Performance Dashboards
=========================================
Displays interactive Plotly charts summarizing exam performance.
"""

from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QFrame
)

from PyQt6.QtWebEngineWidgets import QWebEngineView

from src.core.database import DatabaseManager
from src.core.models import ModelManager
from src.reporting.report_builder import ReportBuilder
from src.ui.workers import ReportWorker, AIInsightsWorker


class AnalyticsView(QWidget):
    def __init__(self, db: DatabaseManager, model_manager: ModelManager, parent=None):
        super().__init__(parent)
        self.db = db
        self.model_manager = model_manager
        self.builder = ReportBuilder(db)
        
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        
        # Header & Controls
        header_layout = QHBoxLayout()
        lbl_title = QLabel("Performance Dashboard")
        lbl_title.setProperty("class", "PageTitle")
        header_layout.addWidget(lbl_title)
        
        header_layout.addStretch()
        
        lbl_filter = QLabel("Filter by Subject:")
        lbl_filter.setStyleSheet("color: #94A3B8; font-weight: bold;")
        header_layout.addWidget(lbl_filter)
        
        self.cb_subject = QComboBox()
        self.cb_subject.setStyleSheet("padding: 8px; border-radius: 6px; background-color: #1A2333; border: 1px solid rgba(255,255,255,0.1); color: white;")
        self.cb_subject.currentTextChanged.connect(self._on_subject_changed)
        header_layout.addWidget(self.cb_subject)
        
        btn_refresh = QPushButton("Refresh")
        btn_refresh.setProperty("class", "SecondaryButton")
        btn_refresh.clicked.connect(self.refresh_data)
        header_layout.addWidget(btn_refresh)
        
        layout.addLayout(header_layout)
        
        layout.addSpacing(20)
        
        # Loading Bar
        self.loading_bar = QProgressBar()
        self.loading_bar.setRange(0, 0) # Indeterminate
        self.loading_bar.hide()
        layout.addWidget(self.loading_bar)
        
        # AI Insight Panel
        self.insight_card = QFrame()
        self.insight_card.setStyleSheet("background-color: rgba(59, 130, 246, 0.1); border: 1px solid rgba(59, 130, 246, 0.2); border-radius: 8px;")
        insight_layout = QHBoxLayout(self.insight_card)
        insight_layout.setContentsMargins(20, 20, 20, 20)
        self.lbl_insight = QLabel("Loading insights...")
        self.lbl_insight.setWordWrap(True)
        self.lbl_insight.setStyleSheet("color: #E2E8F0; font-size: 15px; line-height: 1.5;")
        insight_layout.addWidget(self.lbl_insight)
        layout.addWidget(self.insight_card)
        layout.addSpacing(20)
        
        # Chart Layout (Top: Trends, Bottom: Heatmap & Types)
        self.charts_layout = QVBoxLayout()
        
        # Top chart (Trends)
        self.trends_view = None
        
        # Bottom row (Radar + Types)
        self.bottom_charts = QHBoxLayout()
        self.radar_view = None
        self.types_view = None
        
        self.charts_layout.addLayout(self.bottom_charts)
        layout.addLayout(self.charts_layout, stretch=1)
        
        self.refresh_subjects()

    def refresh_subjects(self):
        self.cb_subject.blockSignals(True)
        self.cb_subject.clear()
        self.cb_subject.addItem("All Subjects")
        subjects = self.db.subjects.get_all()
        for s in subjects:
            self.cb_subject.addItem(s.name)
        self.cb_subject.blockSignals(False)
        self.refresh_data()

    def _on_subject_changed(self, text: str):
        self.refresh_data()

    def refresh_data(self):
        subject = self.cb_subject.currentText()
        if subject == "All Subjects":
            subject = None
            
        self.loading_bar.show()
        self.lbl_insight.setText("Analyzing your performance data...")
        
        import threading
        self.worker = ReportWorker(self.builder, subject)
        self.thread = threading.Thread(target=self.worker.run)
        self.worker.finished.connect(self._on_reports_ready)
        self.worker.error.connect(self._on_report_error)
        self.thread.start()
        
        self.insight_worker = AIInsightsWorker(self.db, self.model_manager, subject)
        self.insight_thread = threading.Thread(target=self.insight_worker.run)
        self.insight_worker.finished.connect(self._on_insight_ready)
        self.insight_thread.start()

    @pyqtSlot(str)
    def _on_insight_ready(self, insight: str):
        self.lbl_insight.setText(f"<b>AI Tutor Insight:</b> {insight}")

    @pyqtSlot(str)
    def _on_report_error(self, error: str):
        self.loading_bar.hide()
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.warning(self, "Analytics Error", f"Failed to generate reports:\n{error}")

    @pyqtSlot(dict)
    def _on_reports_ready(self, html_strings: dict):
        self.loading_bar.hide()
        
        # Clear old canvases
        if self.trends_view:
            self.charts_layout.removeWidget(self.trends_view)
            self.trends_view.setParent(None)
        if self.radar_view:
            self.bottom_charts.removeWidget(self.radar_view)
            self.radar_view.setParent(None)
        if self.types_view:
            self.bottom_charts.removeWidget(self.types_view)
            self.types_view.setParent(None)

        # Create new web views with a transparent background wrapper trick if possible,
        # but plotly charts manage their own HTML so they will need dark layout in report_builder.py
        
        self.trends_view = QWebEngineView()
        self.trends_view.setStyleSheet("background-color: transparent; border-radius: 12px;")
        self.trends_view.setHtml(html_strings["trends"])
        
        self.radar_view = QWebEngineView()
        self.radar_view.setStyleSheet("background-color: transparent; border-radius: 12px;")
        self.radar_view.setHtml(html_strings["radar"])
        
        self.types_view = QWebEngineView()
        self.types_view.setStyleSheet("background-color: transparent; border-radius: 12px;")
        self.types_view.setHtml(html_strings["types"])
        
        # Add to layouts
        self.charts_layout.insertWidget(0, self.trends_view, stretch=1)
        self.bottom_charts.addWidget(self.radar_view, stretch=1)
        self.bottom_charts.addWidget(self.types_view, stretch=1)
