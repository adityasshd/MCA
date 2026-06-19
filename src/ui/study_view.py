"""
study_view — Main Learning Environment
========================================
Displays a grid of subjects and units. Clicking a unit drills down into a Markdown viewer.
"""

import logging
from pathlib import Path
import threading
import re

import fitz  # PyMuPDF
import markdown
from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
    QTextBrowser
)

from src.ui.components.flow_layout import FlowLayout
from src.agents.study_agent import StudyAgent
from src.core.database import DatabaseManager
from src.core.models import ModelManager
from src.core.schemas import Subject, UnitInfo
from src.rag.retriever import Retriever
from src.ui.workers import StudyGuideWorker

from src.ui.components.cards.subject_card import SubjectCard
from src.ui.components.cards.unit_card import UnitCard
from src.ui.theme import format_title_case

logger = logging.getLogger(__name__)

# CSS injected into Markdown
MARKDOWN_CSS = """
<style>
    body {
        font-family: 'Inter', 'Segoe UI', sans-serif;
        color: #F8FAFC;
        background-color: #0B1020;
        line-height: 1.8;
        padding: 40px;
        margin: 0 auto;
        max-width: 850px;
    }
    h1, h2, h3 { color: #3B82F6; font-weight: bold; margin-top: 1.5em; margin-bottom: 0.5em; }
    h1 { border-bottom: 1px solid rgba(255,255,255,0.08); padding-bottom: 10px; font-size: 28px; }
    h2 { font-size: 22px; }
    p { margin-bottom: 16px; font-size: 16px; color: #E2E8F0; }
    code { background-color: #1A2333; padding: 4px 6px; border-radius: 4px; font-family: 'Courier New', monospace; color: #F8FAFC; }
    pre { background-color: #1A2333; padding: 20px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.08); overflow-x: auto; }
    ul, ol { margin-bottom: 16px; font-size: 16px; color: #E2E8F0; padding-left: 20px; }
    li { margin-bottom: 10px; }
    blockquote { border-left: 4px solid #3B82F6; margin: 0; padding: 10px 20px; color: #94A3B8; background-color: rgba(59, 130, 246, 0.05); border-radius: 0 8px 8px 0; }
    img { max-width: 100%; border-radius: 12px; margin: 20px 0; border: 1px solid rgba(255,255,255,0.08); }
</style>
"""


class StudyView(QWidget):
    def __init__(self, db: DatabaseManager, model_manager: ModelManager, ai_chat_panel=None, parent=None):
        super().__init__(parent)
        self.db = db
        self.model_manager = model_manager
        self.ai_chat_panel = ai_chat_panel
        
        self.retriever = Retriever(db, model_manager.embedder)
        self.agent = StudyAgent(db, model_manager, self.retriever)
        
        self.active_session = None
        self.current_pdf_path = None
        self._guide_markdown = ""
        
        self._init_ui()
        self.refresh_subjects()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        self.stack = QStackedWidget()
        main_layout.addWidget(self.stack)
        
        # ── Page 0: Grid of Subjects ──
        self.page_subjects = QWidget()
        subjects_layout = QVBoxLayout(self.page_subjects)
        subjects_layout.setContentsMargins(40, 20, 40, 20)
        
        self.scroll_subjects = QScrollArea()
        self.scroll_subjects.setWidgetResizable(True)
        self.scroll_subjects.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_subjects.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        
        self.subjects_container = QWidget()
        self.subjects_container.setStyleSheet("background-color: transparent;")
        self.grid_subjects = FlowLayout(self.subjects_container, margin=0, hSpacing=25, vSpacing=25)
        
        self.scroll_subjects.setWidget(self.subjects_container)
        subjects_layout.addWidget(self.scroll_subjects)
        self.stack.addWidget(self.page_subjects)

        # ── Page 1: Grid of Units ──
        self.page_units = QWidget()
        units_layout = QVBoxLayout(self.page_units)
        units_layout.setContentsMargins(40, 20, 40, 20)
        
        h_units = QHBoxLayout()
        self.btn_back_sub = QPushButton("← Back to Subjects")
        self.btn_back_sub.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        self.btn_back_sub.setProperty("class", "SecondaryButton")
        self.btn_back_sub.setCursor(Qt.CursorShape.PointingHandCursor)
        h_units.addWidget(self.btn_back_sub)
        
        self.lbl_subject_title = QLabel("")
        self.lbl_subject_title.setProperty("class", "PageTitle")
        h_units.addStretch()
        h_units.addWidget(self.lbl_subject_title)
        h_units.addStretch()
        units_layout.addLayout(h_units)
        
        units_layout.addSpacing(20)
        
        self.scroll_units = QScrollArea()
        self.scroll_units.setWidgetResizable(True)
        self.scroll_units.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_units.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        
        self.units_container = QWidget()
        self.units_container.setStyleSheet("background-color: transparent;")
        self.grid_units = FlowLayout(self.units_container, margin=0, hSpacing=20, vSpacing=20)
        
        self.scroll_units.setWidget(self.units_container)
        units_layout.addWidget(self.scroll_units)
        self.stack.addWidget(self.page_units)
        
        # ── Page 2: Markdown Reader ──
        self.page_reader = QWidget()
        reader_layout = QVBoxLayout(self.page_reader)
        reader_layout.setContentsMargins(20, 10, 20, 0)
        
        header_layout = QHBoxLayout()
        self.btn_back_units = QPushButton("← Back to Units")
        self.btn_back_units.clicked.connect(lambda: self.stack.setCurrentIndex(1))
        self.btn_back_units.setProperty("class", "SecondaryButton")
        self.btn_back_units.setCursor(Qt.CursorShape.PointingHandCursor)
        header_layout.addWidget(self.btn_back_units)
        
        self.lbl_unit_title = QLabel("")
        self.lbl_unit_title.setProperty("class", "SectionTitle")
        header_layout.addStretch()
        header_layout.addWidget(self.lbl_unit_title)
        header_layout.addStretch()
        
        self.btn_view_pdf = QPushButton("View Original PDF")
        self.btn_view_pdf.clicked.connect(self._toggle_pdf_view)
        self.btn_view_pdf.setProperty("class", "PrimaryButton")
        header_layout.addWidget(self.btn_view_pdf)
        
        reader_layout.addLayout(header_layout)
        
        # Reader Content Area
        self.reader_stack = QStackedWidget()
        
        # To restrict max width to 850px and center it, we put the browser in an HBox layout
        self.reader_center_container = QWidget()
        center_hbox = QHBoxLayout(self.reader_center_container)
        center_hbox.setContentsMargins(0,0,0,0)
        
        self.content_browser = QTextBrowser()
        self.content_browser.setOpenExternalLinks(True)
        self.content_browser.setMaximumWidth(850)
        self.content_browser.setStyleSheet("background-color: #0B1020; border: none;")
        
        center_hbox.addStretch()
        center_hbox.addWidget(self.content_browser, stretch=1)
        center_hbox.addStretch()
        
        self.reader_stack.addWidget(self.reader_center_container)
        
        # PDF Viewer Area
        self.pdf_scroll = QScrollArea()
        self.pdf_scroll.setWidgetResizable(True)
        self.pdf_scroll.setStyleSheet("background-color: #0B1020; border: none;")
        self.pdf_container = QWidget()
        self.pdf_container.setStyleSheet("background-color: transparent;")
        self.pdf_layout = QVBoxLayout(self.pdf_container)
        self.pdf_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        self.pdf_scroll.setWidget(self.pdf_container)
        self.reader_stack.addWidget(self.pdf_scroll)
        
        reader_layout.addWidget(self.reader_stack, stretch=1)
        self.stack.addWidget(self.page_reader)

    def refresh_subjects(self):
        # Clear existing subjects grid
        while self.grid_subjects.count():
            child = self.grid_subjects.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
                
        subjects = self.db.subjects.get_all()
        for sub in subjects:
            card = SubjectCard(
                title=format_title_case(sub.name),
                num_units=len(sub.units),
                progress=0, # Would hook to DB progress
                last_accessed="Just now"
            )
            card.setFixedWidth(280)
            card.clicked.connect(lambda s=sub: self._show_units(s))
            self.grid_subjects.addWidget(card)

    def _show_units(self, subject: Subject):
        self.lbl_subject_title.setText(format_title_case(subject.name))
        
        # Clear existing units grid
        while self.grid_units.count():
            child = self.grid_units.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
                
        for unit in subject.units:
            card = UnitCard(
                title=format_title_case(unit.name),
                num_topics=unit.chunk_count,
                progress=0
            )
            card.setFixedWidth(300)
            card.clicked.connect(lambda s=subject.name, u=unit: self._open_unit(s, u))
            self.grid_units.addWidget(card)
                
        self.stack.setCurrentIndex(1)

    def _open_unit(self, subject_name: str, unit: UnitInfo):
        self.lbl_unit_title.setText(format_title_case(unit.name))
        self.current_pdf_path = unit.file_path
        self.pdf_loaded = False
        self.reader_stack.setCurrentIndex(0)
        self.btn_view_pdf.setText("View Original PDF")
        
        # Persistent Tracking
        from src.core.schemas import StudySession, AnalyticsEvent
        session = StudySession(subject=subject_name, unit=unit.name)
        self.db.sessions.save(session)
        self.db.analytics.log(AnalyticsEvent(
            event_type="study_started",
            subject=subject_name,
            unit=unit.name
        ))
        
        # Switch stack
        self.stack.setCurrentIndex(2)
        
        # Start Study Guide generation
        self._guide_markdown = "## Generating AI Study Guide...\n\n*Please wait while your AI Tutor synthesizes a topic-wise summary...*"
        self._update_markdown_view()
        
        if not hasattr(self, 'guide_workers'):
            self.guide_workers = []

        if hasattr(self, 'guide_worker') and self.guide_worker:
            self.guide_worker.cancel()
            self.guide_workers.append(self.guide_worker) # Prevent GC
            
        self.guide_worker = StudyGuideWorker(self.agent, subject_name, unit.name)
        self.guide_worker.chunk.connect(self._on_guide_chunk)
        self.guide_worker.done.connect(self._on_guide_done)
        self.guide_worker.error.connect(self._on_guide_error)
        
        self._guide_markdown = ""
        self.guide_thread = threading.Thread(target=self.guide_worker.run)
        self.guide_thread.start()
        
        if self.ai_chat_panel:
            self.ai_chat_panel.set_context(subject_name, unit.name)

    def _update_markdown_view(self):
        html = markdown.markdown(self._guide_markdown, extensions=['fenced_code', 'tables'])
        # Fix image paths for QTextBrowser.
        html = re.sub(r'src="(/[^"]+)"', r'src="file://\1"', html)
        final_html = f"<html><head>{MARKDOWN_CSS}</head><body>{html}</body></html>"
        self.content_browser.setHtml(final_html)

    def _toggle_pdf_view(self):
        if not self.current_pdf_path: return
        
        if self.reader_stack.currentIndex() == 0:
            self.reader_stack.setCurrentIndex(1)
            self.btn_view_pdf.setText("View Study Guide")
            if not getattr(self, 'pdf_loaded', False):
                self._load_pdf()
        else:
            self.reader_stack.setCurrentIndex(0)
            self.btn_view_pdf.setText("View Original PDF")

    def _load_pdf(self):
        # Clear existing
        while self.pdf_layout.count():
            child = self.pdf_layout.takeAt(0)
            if child.widget(): child.widget().deleteLater()
            
        try:
            doc = fitz.open(self.current_pdf_path)
            for page_num in range(len(doc)):
                page = doc[page_num]
                mat = fitz.Matrix(2, 2)
                pix = page.get_pixmap(matrix=mat)
                img = QImage(pix.samples, pix.width, pix.height, pix.stride, QImage.Format.Format_RGB888)
                qpix = QPixmap.fromImage(img)
                label = QLabel()
                label.setPixmap(qpix)
                label.setStyleSheet("border: 1px solid rgba(255,255,255,0.08); margin-bottom: 20px; border-radius: 8px;")
                self.pdf_layout.addWidget(label)
            doc.close()
            self.pdf_loaded = True
        except Exception as e:
            logger.error("Failed to load PDF: %s", e)
            err_label = QLabel(f"Could not load PDF: {e}")
            err_label.setStyleSheet("color: #F59E0B;")
            self.pdf_layout.addWidget(err_label)

    @pyqtSlot(str)
    def _on_guide_chunk(self, chunk: str):
        self._guide_markdown += chunk
        self._update_markdown_view()

    @pyqtSlot()
    def _on_guide_done(self):
        pass

    @pyqtSlot(str)
    def _on_guide_error(self, error: str):
        self._guide_markdown += f"\n\n**Error:** {error}"
        self._update_markdown_view()
