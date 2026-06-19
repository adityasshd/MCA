from PyQt6.QtCore import Qt, pyqtSlot, QTimer
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QLineEdit, QLabel, QFrame, QScrollArea, QSizePolicy
)
import threading

from src.agents.study_agent import StudyAgent
from src.core.database import DatabaseManager
from src.core.models import ModelManager
from src.rag.retriever import Retriever
from src.ui.workers import ChatWorker

class ChatBubble(QWidget):
    def __init__(self, text: str, is_user: bool, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.label = QLabel(text)
        self.label.setWordWrap(True)
        self.label.setMaximumWidth(260)
        self.label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        
        if is_user:
            self.label.setStyleSheet("""
                background-color: #3B82F6;
                color: white;
                padding: 10px 14px;
                border-radius: 14px;
                border-bottom-right-radius: 2px;
                font-size: 14px;
            """)
            layout.addStretch()
            layout.addWidget(self.label)
        else:
            self.label.setStyleSheet("""
                background-color: #1A2333;
                color: #F8FAFC;
                padding: 10px 14px;
                border-radius: 14px;
                border-bottom-left-radius: 2px;
                border: 1px solid rgba(255, 255, 255, 0.08);
                font-size: 14px;
            """)
            layout.addWidget(self.label)
            layout.addStretch()

    def append_text(self, chunk: str):
        self.label.setText(self.label.text() + chunk)

class AIChatPanel(QWidget):
    def __init__(self, db: DatabaseManager, model_manager: ModelManager, parent=None):
        super().__init__(parent)
        self.db = db
        self.model_manager = model_manager
        
        self.retriever = Retriever(db, model_manager.embedder)
        self.agent = StudyAgent(db, model_manager, self.retriever)
        self.active_session = None
        
        self.setObjectName("AIChatPanel")
        self.setMinimumWidth(320)
        self.setMaximumWidth(450)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Header
        header = QFrame()
        header.setStyleSheet("background-color: #1A2333; border-bottom: 1px solid rgba(255,255,255,0.08);")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(15, 15, 15, 15)
        
        lbl_title = QLabel("💬 AI Tutor")
        lbl_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #F8FAFC;")
        header_layout.addWidget(lbl_title)
        
        # Optional Context Label
        self.lbl_context = QLabel("General Context")
        self.lbl_context.setStyleSheet("font-size: 12px; color: #94A3B8;")
        header_layout.addStretch()
        header_layout.addWidget(self.lbl_context)
        
        layout.addWidget(header)
        
        # Chat History
        self.chat_scroll = QScrollArea()
        self.chat_scroll.setWidgetResizable(True)
        self.chat_scroll.setStyleSheet("QScrollArea { border: none; background-color: #0B1020; }")
        
        self.chat_container = QWidget()
        self.chat_container.setStyleSheet("background-color: transparent;")
        self.chat_layout = QVBoxLayout(self.chat_container)
        self.chat_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.chat_layout.setSpacing(12)
        self.chat_layout.setContentsMargins(15, 15, 15, 15)
        
        self.chat_scroll.setWidget(self.chat_container)
        layout.addWidget(self.chat_scroll, stretch=1)
        
        # Input Area
        input_frame = QFrame()
        input_frame.setStyleSheet("background-color: #1A2333; border-top: 1px solid rgba(255,255,255,0.08);")
        input_layout = QHBoxLayout(input_frame)
        input_layout.setContentsMargins(15, 15, 15, 15)
        
        self.chat_input = QLineEdit()
        self.chat_input.setPlaceholderText("Ask your tutor...")
        self.chat_input.returnPressed.connect(self._send_message)
        self.chat_input.setStyleSheet("""
            QLineEdit {
                background-color: #0B1020;
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 18px;
                padding: 10px 16px;
                color: #F8FAFC;
                font-size: 14px;
            }
            QLineEdit:focus { border: 1px solid #3B82F6; }
        """)
        input_layout.addWidget(self.chat_input)
        
        self.btn_send = QPushButton("➤")
        self.btn_send.setFixedSize(36, 36)
        self.btn_send.clicked.connect(self._send_message)
        self.btn_send.setStyleSheet("""
            QPushButton {
                background-color: #3B82F6;
                color: white;
                border-radius: 18px;
                border: none;
                font-size: 16px;
            }
            QPushButton:hover { background-color: #2563EB; }
            QPushButton:disabled { background-color: #334155; }
        """)
        input_layout.addWidget(self.btn_send)
        
        layout.addWidget(input_frame)

        # Initialize session
        self.active_session = self.agent.create_session("General", "General")
        welcome_msg = self.active_session.messages[0]
        self._append_chat_message(welcome_msg.role, welcome_msg.content)

    def set_context(self, subject: str, unit: str):
        """Update the agent's context when the user navigates."""
        from src.ui.theme import format_title_case
        self.lbl_context.setText(format_title_case(subject))
        
        self.active_session = self.agent.create_session(subject, unit)
        
        # Clear layout
        while self.chat_layout.count():
            child = self.chat_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
                
        welcome_msg = self.active_session.messages[0]
        self._append_chat_message(welcome_msg.role, welcome_msg.content)

    def _append_chat_message(self, role: str, content: str):
        is_user = role == "user"
        bubble = ChatBubble(content, is_user)
        self.chat_layout.addWidget(bubble)
        self._scroll_to_bottom()
        return bubble

    def _scroll_to_bottom(self):
        QTimer.singleShot(50, lambda: self.chat_scroll.verticalScrollBar().setValue(
            self.chat_scroll.verticalScrollBar().maximum()
        ))

    def _send_message(self):
        if not self.active_session: return
        text = self.chat_input.text().strip()
        if not text: return
        self.chat_input.clear()
        self.chat_input.setEnabled(False)
        self.btn_send.setEnabled(False)
        self._append_chat_message("user", text)
        
        self.current_worker = ChatWorker(self.agent, self.active_session, text)
        self.current_worker.chunk.connect(self._on_chat_chunk)
        self.current_worker.done.connect(self._on_chat_done)
        self.current_worker.error.connect(self._on_chat_error)
        
        self.current_ai_bubble = self._append_chat_message("assistant", "")
        
        self.thread = threading.Thread(target=self.current_worker.run)
        self.thread.start()

    @pyqtSlot(str)
    def _on_chat_chunk(self, chunk: str):
        if hasattr(self, 'current_ai_bubble'):
            self.current_ai_bubble.append_text(chunk)
            self._scroll_to_bottom()

    @pyqtSlot(str)
    def _on_chat_done(self, full_text: str):
        self.chat_input.setEnabled(True)
        self.btn_send.setEnabled(True)
        self.chat_input.setFocus()

    @pyqtSlot(str)
    def _on_chat_error(self, error: str):
        self._on_chat_chunk(f"\n[Error: {error}]")
        self._on_chat_done("")
