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
)

from PyQt6.QtWebEngineWidgets import QWebEngineView

from src.core.database import DatabaseManager
from src.reporting.report_builder import ReportBuilder
from src.ui.workers import ReportWorker


class AnalyticsView(QWidget):
    def __init__(self, db: DatabaseManager, parent=None):
        super().__init__(parent)
        self.db = db
        self.builder = ReportBuilder(db)
        
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        
        # Header & Controls
        header_layout = QHBoxLayout()
        lbl_title = QLabel("Analytics Dashboard")
        lbl_title.setProperty("class", "HeaderLabel")
        header_layout.addWidget(lbl_title)
        
        header_layout.addStretch()
        
        header_layout.addWidget(QLabel("Filter by Subject:"))
        self.cb_subject = QComboBox()
        self.cb_subject.currentTextChanged.connect(self._on_subject_changed)
        header_layout.addWidget(self.cb_subject)
        
        btn_refresh = QPushButton("Refresh")
        btn_refresh.clicked.connect(self.refresh_data)
        header_layout.addWidget(btn_refresh)
        
        layout.addLayout(header_layout)
        
        # Loading Bar
        self.loading_bar = QProgressBar()
        self.loading_bar.setRange(0, 0) # Indeterminate
        self.loading_bar.hide()
        layout.addWidget(self.loading_bar)
        
        # Chart Layout (Top: Trends, Bottom: Heatmap & Types)
        self.charts_layout = QVBoxLayout()
        
        # Top chart (Trends)
        self.trends_view = None
        
        # Bottom row (Heatmap + Types)
        self.bottom_charts = QHBoxLayout()
        self.heatmap_view = None
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
        
        self.worker = ReportWorker(self.builder, subject)
        import threading
        self.thread = threading.Thread(target=self.worker.run)
        self.worker.finished.connect(self._on_reports_ready)
        self.thread.start()

    @pyqtSlot(dict)
    def _on_reports_ready(self, html_strings: dict):
        self.loading_bar.hide()
        
        # Clear old canvases
        if self.trends_view:
            self.charts_layout.removeWidget(self.trends_view)
            self.trends_view.setParent(None)
        if self.heatmap_view:
            self.bottom_charts.removeWidget(self.heatmap_view)
            self.heatmap_view.setParent(None)
        if self.types_view:
            self.bottom_charts.removeWidget(self.types_view)
            self.types_view.setParent(None)

        # Create new web views
        self.trends_view = QWebEngineView()
        self.trends_view.setHtml(html_strings["trends"])
        
        self.heatmap_view = QWebEngineView()
        self.heatmap_view.setHtml(html_strings["heatmap"])
        
        self.types_view = QWebEngineView()
        self.types_view.setHtml(html_strings["types"])
        
        # Add to layouts
        self.charts_layout.insertWidget(0, self.trends_view, stretch=1)
        self.bottom_charts.addWidget(self.heatmap_view, stretch=1)
        self.bottom_charts.addWidget(self.types_view, stretch=1)
