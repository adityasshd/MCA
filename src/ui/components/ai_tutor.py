from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtGui import QTextCursor
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit, 
    QLineEdit, QLabel, QGraphicsDropShadowEffect, QFrame
)
import threading

from src.agents.study_agent import StudyAgent
from src.core.database import DatabaseManager
from src.core.models import ModelManager
from src.rag.retriever import Retriever
from src.ui.workers import ChatWorker

class FloatingActionButton(QPushButton):
    def __init__(self, parent=None):
        super().__init__("💬", parent)
        self.setFixedSize(60, 60)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # Shadow
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setYOffset(4)
        shadow.setColor(Qt.GlobalColor.black)
        self.setGraphicsEffect(shadow)
        
        self.setStyleSheet("""
            QPushButton {
                font-family: "Noto Color Emoji", "Apple Color Emoji", "Segoe UI Emoji", "Twemoji", sans-serif;
                background-color: #238636;
                color: white;
                border-radius: 30px;
                font-size: 24px;
            }
            QPushButton:hover {
                background-color: #2ea043;
            }
        """)

class ChatBubble(QWidget):
    def __init__(self, text: str, is_user: bool, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.label = QLabel(text)
        self.label.setWordWrap(True)
        self.label.setMaximumWidth(280)
        self.label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        
        if is_user:
            self.label.setStyleSheet("""
                background-color: #1F6FEB;
                color: white;
                padding: 10px;
                border-radius: 12px;
                border-top-right-radius: 2px;
            """)
            layout.addStretch()
            layout.addWidget(self.label)
        else:
            self.label.setStyleSheet(f"""
                background-color: #21262D;
                color: #E6EDF3;
                padding: 10px;
                border-radius: 12px;
                border-top-left-radius: 2px;
                border: 1px solid #30363D;
            """)
            layout.addWidget(self.label)
            layout.addStretch()

    def append_text(self, chunk: str):
        self.label.setText(self.label.text() + chunk)

class ContextualActionButton(QPushButton):
    def __init__(self, action_name: str, parent=None):
        super().__init__(action_name, parent)
        self.action_name = action_name
        self.setProperty("class", "SecondaryButton")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet("""
            QPushButton {
                font-size: 11px;
                padding: 6px 12px;
                border-radius: 12px;
                background-color: #1F2937;
                color: #94A3B8;
                border: 1px solid #374151;
            }
            QPushButton:hover {
                background-color: #374151;
                color: #F8FAFC;
            }
        """)

from PyQt6.QtWidgets import QScrollArea
from PyQt6.QtCore import QTimer

class AITutorWidget(QWidget):
    def __init__(self, db: DatabaseManager, model_manager: ModelManager, parent=None):
        super().__init__(parent)
        self.db = db
        self.model_manager = model_manager
        
        self.retriever = Retriever(db, model_manager.embedder)
        self.agent = StudyAgent(db, model_manager, self.retriever)
        self.active_session = None
        
        # Ensure it acts as a floating window within the parent or standalone
        self.setWindowFlags(Qt.WindowType.Tool | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.resize(380, 500)
        self.hide()

        # Main Frame with Shadow
        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(30)
        self.shadow.setXOffset(0)
        self.shadow.setYOffset(10)
        self.shadow.setColor(Qt.GlobalColor.black)
        
        self.frame = QFrame(self)
        self.frame.setGraphicsEffect(self.shadow)
        self.frame.setStyleSheet("""
            QFrame {
                background-color: #161B22;
                border: 1px solid #30363D;
                border-radius: 12px;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.addWidget(self.frame)
        
        frame_layout = QVBoxLayout(self.frame)
        
        # Header
        header_layout = QHBoxLayout()
        header = QLabel("AI Tutor")
        header.setStyleSheet("font-size: 16px; font-weight: bold; color: white; border: none; background: transparent;")
        header_layout.addWidget(header)
        header_layout.addStretch()
        
        btn_close = QPushButton("✕")
        btn_close.setFixedSize(24, 24)
        btn_close.clicked.connect(self.hide)
        btn_close.setStyleSheet("""
            QPushButton {
                background: transparent; border: none; color: #8B949E; font-size: 14px; font-weight: bold;
            }
            QPushButton:hover { color: #F85149; }
        """)
        header_layout.addWidget(btn_close)
        frame_layout.addLayout(header_layout)
        
        # Chat History
        self.chat_scroll = QScrollArea()
        self.chat_scroll.setWidgetResizable(True)
        self.chat_scroll.setStyleSheet("QScrollArea { background-color: #0D1117; border: 1px solid #30363D; border-radius: 8px; } QScrollBar:vertical { width: 0px; }")
        
        self.chat_container = QWidget()
        self.chat_container.setStyleSheet("background-color: transparent;")
        self.chat_layout = QVBoxLayout(self.chat_container)
        self.chat_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.chat_layout.setSpacing(10)
        self.chat_layout.setContentsMargins(10, 10, 10, 10)
        
        self.chat_scroll.setWidget(self.chat_container)
        frame_layout.addWidget(self.chat_scroll)
        
        # Input Area
        input_layout = QHBoxLayout()
        self.chat_input = QLineEdit()
        self.chat_input.setPlaceholderText("Ask a question...")
        self.chat_input.returnPressed.connect(self._send_message)
        self.chat_input.setStyleSheet("background-color: #0D1117; border: 1px solid #30363D; border-radius: 15px; padding: 5px 15px; color: white;")
        input_layout.addWidget(self.chat_input)
        
        self.btn_send = QPushButton("➤")
        self.btn_send.setFixedSize(30, 30)
        self.btn_send.clicked.connect(self._send_message)
        self.btn_send.setStyleSheet("background-color: #1F6FEB; color: white; border-radius: 15px; border: none; font-size: 16px;")
        input_layout.addWidget(self.btn_send)
        
        frame_layout.addLayout(input_layout)

        # Contextual Actions Horizontal Scroll
        self.actions_scroll = QScrollArea()
        self.actions_scroll.setWidgetResizable(True)
        self.actions_scroll.setFixedHeight(45)
        self.actions_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.actions_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.actions_scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        actions_container = QWidget()
        actions_layout = QHBoxLayout(actions_container)
        actions_layout.setContentsMargins(0, 5, 0, 0)
        actions_layout.setSpacing(8)
        
        actions = ["Explain Topic", "Give Example", "Create Analogy", "Summarize", "Exam Questions"]
        for act in actions:
            btn = ContextualActionButton(act)
            btn.clicked.connect(lambda checked, a=act: self._trigger_contextual_action(a))
            actions_layout.addWidget(btn)
            
        actions_layout.addStretch()
        self.actions_scroll.setWidget(actions_container)
        
        frame_layout.addWidget(self.actions_scroll)

        self.active_session = self.agent.create_session("General", "General")
        welcome_msg = self.active_session.messages[0]
        self._append_chat_message(welcome_msg.role, welcome_msg.content)

    def set_context(self, subject: str, unit: str):
        """Update the agent's context when the user navigates."""
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

    def _trigger_contextual_action(self, action_name: str):
        if not self.active_session: return
        self.chat_input.setEnabled(False)
        self.btn_send.setEnabled(False)
        
        self._append_chat_message("user", action_name)
        self.current_ai_bubble = self._append_chat_message("assistant", "")
        
        def run_action():
            try:
                stream = self.agent.execute_contextual_action(
                    action_name, self.active_session.subject, self.active_session.unit
                )
                full_text = ""
                for chunk in stream:
                    full_text += chunk
                    # Signal chunk to UI using QMetaObject or safe signal
                    # (Simplified for now, assumes thread-safety in this specific QWidget setup or handled by _on_chat_chunk via signal)
                    # For safety in PyQt, we really should use a worker, but since we are modifying, let's reuse ChatWorker with a trick
            except Exception as e:
                pass
                
        # Better approach: Create an ActionWorker 
        from PyQt6.QtCore import pyqtSignal, QObject
        class ActionWorker(QObject):
            chunk = pyqtSignal(str)
            done = pyqtSignal(str)
            error = pyqtSignal(str)
            
            def __init__(self, agent, action, subject, unit):
                super().__init__()
                self.agent = agent
                self.action = action
                self.subject = subject
                self.unit = unit
                
            def run(self):
                try:
                    stream = self.agent.execute_contextual_action(self.action, self.subject, self.unit)
                    full = ""
                    for c in stream:
                        full += c
                        self.chunk.emit(c)
                    self.done.emit(full)
                except Exception as e:
                    self.error.emit(str(e))
                    
        self.current_worker = ActionWorker(self.agent, action_name, self.active_session.subject, self.active_session.unit)
        self.current_worker.chunk.connect(self._on_chat_chunk)
        self.current_worker.done.connect(self._on_chat_done)
        self.current_worker.error.connect(self._on_chat_error)
        
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
        self._on_chat_chunk(f"\\n[Error: {error}]")
        self._on_chat_done("")
