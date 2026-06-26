from PyQt6.QtCore import Qt, pyqtSignal, pyqtSlot
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QPushButton, QFrame, QButtonGroup, QRadioButton, QScrollArea, QStackedWidget, QComboBox
)
import threading
from src.services.practice_service import PracticeService
from src.core.schemas import PracticeSession
from src.ui.theme import COLORS
from src.ui.components.shared.loading_overlay import LoadingOverlay
import markdown

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  body {
    background-color: transparent;
    color: #F8FAFC;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    font-size: 15px;
    line-height: 1.6;
    margin: 0;
    padding: 0px;
  }
  ::-webkit-scrollbar { width: 8px; }
  ::-webkit-scrollbar-track { background: transparent; }
  ::-webkit-scrollbar-thumb { background: #334155; border-radius: 4px; }
  ::-webkit-scrollbar-thumb:hover { background: #475569; }
</style>
<script>
MathJax = {
  tex: {
    inlineMath: [['$', '$'], ['\\\\(', '\\\\)']],
    displayMath: [['$$', '$$'], ['\\\\[', '\\\\]']]
  },
  svg: {
    fontCache: 'global'
  }
};
</script>
<script type="text/javascript" id="MathJax-script" async
  src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-svg.js">
</script>
</head>
<body>
{content}
</body>
</html>
"""

def render_explanation(text):
    html_content = markdown.markdown(text, extensions=['fenced_code', 'tables'])
    return HTML_TEMPLATE.replace("{content}", html_content)


class InfinitePracticeView(QWidget):
    """
    A 1-by-1 adaptive UI flow for continuous practice and mastery reinforcement.
    """
    close_clicked = pyqtSignal()

    def __init__(self, practice_service: PracticeService, parent=None):
        super().__init__(parent)
        self.service = practice_service
        self.current_session: PracticeSession | None = None
        
        self.subject = ""
        self.unit = ""
        self.topic = ""
        self.mastery = 0.0
        self.reinforcement_queue: list[str] = []
        
        self._init_ui()
        
    def _init_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        
        self.stack = QStackedWidget()
        self.layout.addWidget(self.stack)
        
        self.page_config = QWidget()
        self._setup_config_page()
        self.stack.addWidget(self.page_config)
        
        self.page_practice = QWidget()
        self._setup_practice_page()
        
        self.practice_scroll = QScrollArea()
        self.practice_scroll.setWidgetResizable(True)
        self.practice_scroll.setWidget(self.page_practice)
        self.practice_scroll.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        
        self.stack.addWidget(self.practice_scroll)

        self.loading = LoadingOverlay(self)

    def _setup_config_page(self):
        layout = QVBoxLayout(self.page_config)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        panel = QFrame()
        panel.setProperty("class", "CardPanel")
        panel.setFixedWidth(600)
        p_layout = QVBoxLayout(panel)
        p_layout.setContentsMargins(40, 40, 40, 40)
        p_layout.setSpacing(25)
        
        lbl_title = QLabel("Infinite Practice Setup")
        lbl_title.setProperty("class", "PageTitle")
        lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        p_layout.addWidget(lbl_title)
        
        lbl_desc = QLabel("Select what you want to practice.")
        lbl_desc.setProperty("class", "BodyText")
        lbl_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        p_layout.addWidget(lbl_desc)
        p_layout.addSpacing(10)
        
        p_layout.addWidget(QLabel("1. Choose Subject"))
        self.cb_subject = QComboBox()
        self.cb_subject.setStyleSheet("padding: 8px; border-radius: 6px; background-color: #0B1020; border: 1px solid rgba(255,255,255,0.1); color: white;")
        self._populate_subjects()
        self.cb_subject.currentTextChanged.connect(self._populate_units)
        p_layout.addWidget(self.cb_subject)
        
        p_layout.addWidget(QLabel("2. Choose Unit"))
        self.cb_unit = QComboBox()
        self.cb_unit.setStyleSheet("padding: 8px; border-radius: 6px; background-color: #0B1020; border: 1px solid rgba(255,255,255,0.1); color: white;")
        p_layout.addWidget(self.cb_unit)
        self._populate_units(self.cb_subject.currentText())
        
        p_layout.addSpacing(20)
        
        btn_layout = QHBoxLayout()
        self.btn_back_dash = QPushButton("← Back")
        self.btn_back_dash.setProperty("class", "SecondaryButton")
        self.btn_back_dash.clicked.connect(self.close_clicked.emit)
        
        self.btn_start = QPushButton("Start Practice")
        self.btn_start.setProperty("class", "PrimaryButton")
        self.btn_start.clicked.connect(self._on_manual_start)
        
        btn_layout.addWidget(self.btn_back_dash)
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_start)
        p_layout.addLayout(btn_layout)
        
        layout.addWidget(panel)

    def _populate_subjects(self):
        from src.ui.theme import format_title_case
        self.cb_subject.clear()
        for s in self.service.db.subjects.get_all():
            self.cb_subject.addItem(format_title_case(s.name), userData=s.name)

    def _populate_units(self, display_name: str):
        from src.ui.theme import format_title_case
        self.cb_unit.clear()
        if not display_name: return
        
        idx = self.cb_subject.currentIndex()
        actual_name = self.cb_subject.itemData(idx)
        
        sub = self.service.db.subjects.get_by_name(actual_name)
        if sub:
            self.cb_unit.addItem("All (Full Subject)", userData="All")
            for u in sub.units:
                self.cb_unit.addItem(format_title_case(u.name), userData=u.name)

    def _on_manual_start(self):
        sub_idx = self.cb_subject.currentIndex()
        subject = self.cb_subject.itemData(sub_idx)
        
        unit_idx = self.cb_unit.currentIndex()
        unit = self.cb_unit.itemData(unit_idx)
        if unit == "All": unit = ""
        
        topic = ""
        
        if not subject: return
        mode = "unit" if unit else "subject"
        mastery = 0.5
            
        self._start_practice_session(mode, subject, unit, topic, mastery)

    def _setup_practice_page(self):
        layout = QVBoxLayout(self.page_practice)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Main Navigation Header
        nav_layout = QHBoxLayout()
        btn_back = QPushButton("← Back to Dashboard")
        btn_back.setProperty("class", "SecondaryButton")
        btn_back.clicked.connect(self.close_clicked.emit)
        
        btn_exit = QPushButton("Exit Practice")
        btn_exit.setProperty("class", "SecondaryButton")
        btn_exit.clicked.connect(self.close_clicked.emit)
        
        nav_layout.addWidget(btn_back)
        nav_layout.addStretch()
        nav_layout.addWidget(btn_exit)
        self.layout.addLayout(nav_layout)
        
        # Container
        self.panel = QFrame()
        self.panel.setProperty("class", "CardPanel")
        self.panel.setFixedWidth(750)
        self.panel.setMinimumHeight(600)
        
        self.p_layout = QVBoxLayout(self.panel)
        self.p_layout.setContentsMargins(30, 30, 30, 30)
        self.p_layout.setSpacing(15)
        
        # Header inside panel
        header = QHBoxLayout()
        self.lbl_topic = QLabel()
        self.lbl_topic.setProperty("class", "SectionTitle")
        self.lbl_progress = QLabel()
        self.lbl_progress.setProperty("class", "MetaText")
        
        header.addWidget(self.lbl_topic)
        header.addStretch()
        header.addWidget(self.lbl_progress)
        self.p_layout.addLayout(header)
        
        # Question Area
        self.lbl_question = QLabel("Loading your next question...")
        self.lbl_question.setProperty("class", "BodyText")
        self.lbl_question.setWordWrap(True)
        self.lbl_question.setStyleSheet("font-size: 18px; color: #F8FAFC;")
        self.p_layout.addWidget(self.lbl_question)
        
        # Options
        self.opt_group = QButtonGroup(self)
        self.opt_layout = QVBoxLayout()
        self.opt_layout.setSpacing(10)
        self.p_layout.addLayout(self.opt_layout)
        
        self.p_layout.addStretch()
        
        # Feedback Container
        self.feedback_container = QFrame()
        self.feedback_container.setObjectName("FeedbackContainer")
        self.feedback_container.setStyleSheet(f"""
            QFrame#FeedbackContainer {{
                background-color: transparent;
                border-radius: 8px;
            }}
        """)
        f_layout = QVBoxLayout(self.feedback_container)
        f_layout.setContentsMargins(15, 15, 15, 15)
        f_layout.setSpacing(5)
        
        self.lbl_feedback_title = QLabel()
        self.lbl_feedback_title.setWordWrap(True)
        self.lbl_feedback_title.setStyleSheet("font-size: 16px; font-weight: bold;")
        
        self.btn_expand_feedback = QPushButton("↕ Expand Explanation")
        self.btn_expand_feedback.setStyleSheet("color: #94A3B8; background: transparent; border: none; font-weight: bold;")
        self.btn_expand_feedback.setCursor(Qt.CursorShape.PointingHandCursor)
        
        header_layout = QHBoxLayout()
        header_layout.addWidget(self.lbl_feedback_title)
        header_layout.addStretch()
        header_layout.addWidget(self.btn_expand_feedback)
        f_layout.addLayout(header_layout)
        
        from PyQt6.QtWebEngineWidgets import QWebEngineView
        from PyQt6.QtGui import QColor
        from PyQt6.QtWidgets import QSizePolicy
        
        self.lbl_feedback = QWebEngineView()
        self.lbl_feedback.page().setBackgroundColor(QColor(Qt.GlobalColor.transparent))
        self.lbl_feedback.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        f_layout.addWidget(self.lbl_feedback)
        
        def toggle_feedback_expand(event=None):
            if self.feedback_container.height() <= 300:
                self.feedback_container.setFixedHeight(750)
                self.btn_expand_feedback.setText("↕ Collapse Explanation")
            else:
                self.feedback_container.setFixedHeight(250)
                self.btn_expand_feedback.setText("↕ Expand Explanation")
                
        self.btn_expand_feedback.clicked.connect(toggle_feedback_expand)
        self.lbl_feedback_title.mousePressEvent = toggle_feedback_expand
        
        self.feedback_container.hide()
        self.feedback_container.setFixedHeight(250)
        self.p_layout.addWidget(self.feedback_container)
        
        # Actions
        self.btn_submit = QPushButton("Check Answer")
        self.btn_submit.setProperty("class", "PrimaryButton")
        self.btn_submit.clicked.connect(self._check_answer)
        
        self.btn_next = QPushButton("Next Question")
        self.btn_next.setProperty("class", "PrimaryButton")
        self.btn_next.hide()
        self.btn_next.clicked.connect(self._load_next)
        
        act_layout = QHBoxLayout()
        act_layout.addStretch()
        act_layout.addWidget(self.btn_submit)
        act_layout.addWidget(self.btn_next)
        self.p_layout.addLayout(act_layout)
        
        layout.addWidget(self.panel)

    def open_setup(self, mode: str, subject: str, unit: str, topic: str, initial_mastery: float):
        from src.ui.theme import format_title_case
        
        if mode == "weak":
            self._start_practice_session(mode, subject, unit, topic, initial_mastery)
            return
            
        self.stack.setCurrentWidget(self.page_config)
        
        if subject:
            idx = self.cb_subject.findText(format_title_case(subject))
            if idx >= 0:
                self.cb_subject.setCurrentIndex(idx)
                
        if unit:
            idx = self.cb_unit.findText(format_title_case(unit))
            if idx >= 0:
                self.cb_unit.setCurrentIndex(idx)

    def _start_practice_session(self, mode: str, subject: str, unit: str, topic: str, initial_mastery: float):
        self.mode = mode
        self.subject = subject
        self.unit = unit
        self.topic = topic
        self.mastery = initial_mastery
        self.reinforcement_queue.clear()
        self.session_log = []
        
        self.current_session = self.service.start_practice_session(subject, unit)
        
        if mode == "random":
            self.lbl_topic.setText("Practice: Random Subject & Topic")
        elif mode == "subject":
            self.lbl_topic.setText(f"Practice: {subject} (All Topics)")
        elif mode == "unit":
            self.lbl_topic.setText(f"Practice: {unit} (All Topics)")
        elif mode == "topic":
            self.lbl_topic.setText(f"Practice: {topic}")
        elif mode == "weak":
            self.lbl_topic.setText(f"Practice Weak Area: {topic}")
        else:
            self.lbl_topic.setText(f"Practice: {topic}")
            
        self.lbl_progress.setText(f"Mastery: {int(self.mastery*100)}%")
        
        self.stack.setCurrentWidget(self.practice_scroll)
        self._load_next()

    def _start_prefetch_next(self):
        import concurrent.futures
        if not hasattr(self, 'executor'):
            self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
            
        import random
        query_subject = self.subject
        query_unit = self.unit
        query_topic = self.topic
        
        if not self.reinforcement_queue:
            if self.mode == "random":
                subjects = self.service.db.subjects.get_all()
                if subjects:
                    sub = random.choice(subjects)
                    query_subject = sub.name
                    if sub.units:
                        u = random.choice(sub.units)
                        query_unit = u.name
                        query_topic = ""
            elif self.mode == "subject":
                sub = self.service.db.subjects.get_by_name(self.subject)
                if sub and sub.units:
                    u = random.choice(sub.units)
                    query_unit = u.name
                    query_topic = ""
                    
        if self.reinforcement_queue:
            difficulty = self.reinforcement_queue[0]
        else:
            difficulty = "Medium" if self.mastery < 0.8 else "Hard"
            
        def run():
            try:
                q_data = self.service.get_practice_question(
                    query_subject, query_unit, query_topic, 
                    difficulty=difficulty,
                    exclude_ids=self.session_log
                )
                q_data["_generated_topic"] = query_topic
                q_data["_generated_unit"] = query_unit
                self.session_log.append(q_data["id"])
                q_data["_generated_subject"] = query_subject
                return q_data
            except Exception as e:
                import logging
                logging.getLogger(__name__).error(f"Failed to generate practice question: {e}")
                return {"error": str(e)}
                
        self.next_q_future = self.executor.submit(run)

    def _load_next(self):
        self._answered = False
        self.feedback_container.hide()
        self.btn_submit.show()
        self.btn_submit.setEnabled(False)
        self.btn_next.hide()
        
        if hasattr(self, 'next_q_future') and self.next_q_future is not None and not self.next_q_future.done():
            self.loading.show_loading("Thinking...\nAnalyzing context\nGenerating question")
        elif not hasattr(self, 'next_q_future') or self.next_q_future is None:
            self.loading.show_loading("Thinking...\nAnalyzing context\nGenerating question")
        
        # Update progress label for reinforcement
        if self.reinforcement_queue:
            self.reinforcement_queue.pop(0)
            rem = len(self.reinforcement_queue)
            self.lbl_progress.setText(f"Reinforcement Mode Active | Remaining Questions: {rem}")
            self.lbl_progress.setStyleSheet("color: #F59E0B; font-weight: bold;")
        else:
            self.lbl_progress.setText(f"Mastery: {int(self.mastery*100)}%")
            self.lbl_progress.setStyleSheet("color: #94A3B8; font-weight: normal;")
        
        # Clear options
        for btn in self.opt_group.buttons():
            self.opt_group.removeButton(btn)
            
        while self.opt_layout.count():
            item = self.opt_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
                
        if hasattr(self, 'next_q_future') and self.next_q_future is not None:
            self.future = self.next_q_future
            self.next_q_future = None
        else:
            self._start_prefetch_next()
            self.future = self.next_q_future
            self.next_q_future = None
        
        self.timer = self.startTimer(100)

    def timerEvent(self, event):
        if hasattr(self, 'future') and getattr(self, 'timer', None) == event.timerId():
            if self.future.done():
                self.killTimer(self.timer)
                try:
                    q_data = self.future.result()
                except Exception as e:
                    q_data = {"error": str(e)}
                    
                self.loading.hide_loading()
                
                if "error" in q_data:
                    self.lbl_question.setText(f"Error generating question: {q_data['error']}")
                    self.btn_next.setText("Retry")
                    self.btn_next.show()
                else:
                    self.btn_next.setText("Next Question")
                    self._render_question(q_data)

        if hasattr(self, 'exp_future') and getattr(self, 'exp_timer', None) == event.timerId():
            if self.exp_future.done():
                self.killTimer(self.exp_timer)
                try:
                    explanation = self.exp_future.result()
                except Exception as e:
                    explanation = f"Error generating explanation: {e}"
                
                # Update DB to cache this explanation
                self.current_q['explanation'] = explanation
                if 'id' in self.current_q and self.current_q['id']:
                    q_id = self.current_q['id']
                    q_item = self.service.db.question_bank.get_by_id(q_id)
                    if q_item:
                        q_item.explanation = explanation
                        self.service.db.question_bank.update(q_item)
                
                if getattr(self, '_answered', False):
                    self.lbl_feedback.setHtml(render_explanation(explanation))


    def _render_question(self, q_data: dict):
        self.current_q = q_data
        self.lbl_question.setText(q_data.get("question", "Error loading"))
        self.lbl_feedback_title.setText("")
        self.lbl_feedback.setHtml("")
        
        # Start pre-fetching explanation if not cached
        cached_exp = self.current_q.get('explanation')
        if not cached_exp and "Error" not in q_data.get("question", ""):
            gen_sub = self.current_q.get("_generated_subject", self.subject)
            gen_unit = self.current_q.get("_generated_unit", self.unit)
            gen_topic = self.current_q.get("_generated_topic", self.topic)
            self._start_explanation_thread(
                gen_sub, gen_unit, gen_topic, 
                self.current_q.get('question'), 
                self.current_q.get('answer'), 
                None, None, None
            )
        
        for i, opt in enumerate(q_data.get("options", [])):
            opt_container = QFrame()
            opt_container.setProperty("class", "OptionContainer")
            opt_container.setStyleSheet(f"""
                QFrame {{
                    background-color: {COLORS['bg_surface']};
                    border-radius: 8px;
                    border: 1px solid {COLORS['border']};
                }}
            """)
            opt_layout = QHBoxLayout(opt_container)
            opt_layout.setContentsMargins(12, 12, 12, 12)
            
            rb = QRadioButton()
            rb.setStyleSheet(f"QRadioButton::indicator {{ width: 18px; height: 18px; }}")
            rb.option_text = opt
            
            lbl = QLabel(opt)
            lbl.setWordWrap(True)
            lbl.setStyleSheet(f"color: {COLORS['text_primary']}; font-size: 15px; border: none; background: transparent;")
            
            opt_layout.addWidget(rb)
            opt_layout.addWidget(lbl, 1)
            
            def make_click_handler(r=rb):
                def handler(event):
                    r.setChecked(True)
                return handler
            opt_container.mousePressEvent = make_click_handler(rb)
            lbl.mousePressEvent = make_click_handler(rb)
            
            def make_toggle_handler(container=opt_container, r=rb):
                def handler(checked):
                    if checked:
                        container.setStyleSheet(f"""
                            QFrame {{
                                background-color: {COLORS['bg_surface']};
                                border-radius: 8px;
                                border: 1px solid {COLORS['primary']};
                            }}
                        """)
                    else:
                        container.setStyleSheet(f"""
                            QFrame {{
                                background-color: {COLORS['bg_surface']};
                                border-radius: 8px;
                                border: 1px solid {COLORS['border']};
                            }}
                        """)
                    self.btn_submit.setEnabled(True)
                return handler
                
            rb.toggled.connect(make_toggle_handler(opt_container, rb))
            self.opt_group.addButton(rb, i)
            self.opt_layout.addWidget(opt_container)

    def _check_answer(self):
        self._answered = True
        btn = self.opt_group.checkedButton()
        if not btn: return
        
        user_ans = getattr(btn, 'option_text', btn.text())
        correct_ans = self.current_q.get("answer", "")
        is_correct = user_ans.strip().lower() == correct_ans.strip().lower()
        
        # Update mastery for the specifically generated topic
        gen_sub = self.current_q.get("_generated_subject", self.subject)
        gen_unit = self.current_q.get("_generated_unit", self.unit)
        gen_topic = self.current_q.get("_generated_topic", self.topic)
        
        self.mastery = self.service.update_mastery(gen_sub, gen_unit, gen_topic, is_correct).mastery_score
        
        bg = f"{COLORS['success']}20" if is_correct else f"{COLORS['danger']}20"
        color = COLORS["success"] if is_correct else COLORS["danger"]
        title = "✓ Correct" if is_correct else "✗ Incorrect"
        
        if not is_correct and not self.reinforcement_queue:
            self.reinforcement_queue = ["Easy", "Easy", "Medium", "Medium", "Hard"]
            self.lbl_progress.setText(f"Reinforcement Mode Active | Remaining Questions: {len(self.reinforcement_queue)}")
            self.lbl_progress.setStyleSheet("color: #F59E0B; font-weight: bold;")
        elif is_correct:
            self.lbl_progress.setText(f"Mastery: {int(self.mastery*100)}%")
            
        self.feedback_container.setStyleSheet(f"""
            QFrame#FeedbackContainer {{ 
                background-color: {bg}; 
                border-radius: 8px; 
            }}
        """)
        self.feedback_container.show()
        
        self.lbl_feedback_title.setStyleSheet(f"color: {color}; font-weight: bold;")
        self.lbl_feedback_title.setText(title)
        
        # Check if explanation already cached (either loaded from db or pre-fetched)
        cached_exp = self.current_q.get('explanation')
        if cached_exp:
            self.lbl_feedback.setHtml(render_explanation(cached_exp))
        else:
            self.lbl_feedback.setHtml(render_explanation("_Generating detailed explanation..._"))
            # If thread isn't already running, start it
            if not (hasattr(self, 'exp_future') and not self.exp_future.done()):
                self._start_explanation_thread(gen_sub, gen_unit, gen_topic, self.current_q.get('question'), correct_ans, user_ans, title, color)
        
        self.btn_submit.hide()
        self.btn_next.show()
        
        self._start_prefetch_next()

    def _start_explanation_thread(self, subject, unit, topic, question, expected_ans, user_ans, title, color):
        import concurrent.futures
        if not hasattr(self, 'exp_executor'):
            self.exp_executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
            
        def run_exp():
            return self.service.agent.generate_explanation(subject, unit, topic, question, expected_ans, user_ans)
            
        self.exp_future = self.exp_executor.submit(run_exp)
        self.exp_timer = self.startTimer(100)
        # Pass context to timer
        self.exp_context = {"title": title, "color": color}


