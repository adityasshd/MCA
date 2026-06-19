"""
test_view — Exam Generation and Testing Environment
=====================================================
Allows users to generate ad-hoc exams via a Guided Wizard,
and take them with a modernized interface.
"""

from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtWidgets import (
    QButtonGroup, QCheckBox, QComboBox, QFrame, QHBoxLayout, QLabel, 
    QMessageBox, QPushButton, QRadioButton, QScrollArea, QSpinBox, 
    QStackedWidget, QTextEdit, QVBoxLayout, QWidget, QLineEdit, QProgressBar,
    QTextBrowser
)

from src.agents.examiner_agent import ExaminerAgent
from src.core.database import DatabaseManager
from src.core.models import ModelManager
from src.core.schemas import Exam, ExamSession, QuestionType
from src.ui.workers import ExamGenWorker, GradeWorker
from src.ui.theme import format_title_case
from src.ui.components.shared.loading_overlay import LoadingOverlay
import threading


class QuestionWidget(QFrame):
    """Widget for a single exam question during the test."""
    def __init__(self, index: int, question_data, parent=None):
        super().__init__(parent)
        self.index = index
        self.question_data = question_data
        
        # Remove CardPanel class to avoid boxy look
        self.setStyleSheet("""
            QuestionWidget {
                border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 20, 10, 40)
        layout.setSpacing(15)
        
        # Header
        header_layout = QHBoxLayout()
        lbl_num = QLabel(f"Question {index + 1}")
        lbl_num.setStyleSheet("color: #94A3B8; font-weight: bold; font-size: 14px;")
        
        lbl_type = QLabel(question_data.type.value.replace("_", " ").title())
        lbl_type.setStyleSheet("color: #3B82F6; font-size: 12px; font-weight: bold; padding: 4px 8px; background-color: rgba(59, 130, 246, 0.1); border-radius: 4px;")
        
        header_layout.addWidget(lbl_num)
        header_layout.addStretch()
        header_layout.addWidget(lbl_type)
        layout.addLayout(header_layout)
        
        # Prompt
        lbl_prompt = QTextBrowser()
        lbl_prompt.setHtml(question_data.prompt.replace('\n', '<br>'))
        lbl_prompt.setStyleSheet("font-size: 16px; color: #F8FAFC; background-color: transparent; border: none;")
        lbl_prompt.setOpenExternalLinks(True)
        lbl_prompt.document().adjustSize()
        lbl_prompt.setMinimumHeight(int(lbl_prompt.document().size().height()) + 15)
        layout.addWidget(lbl_prompt)
        
        # Answer Input
        if question_data.type == QuestionType.MCQ and question_data.options:
            self.input_group = QButtonGroup(self)
            self.radios = []
            for i, opt in enumerate(question_data.options):
                rb = QRadioButton(opt)
                rb.setStyleSheet("""
                    QRadioButton {
                        font-size: 16px; color: #E2E8F0; padding: 12px;
                        background-color: rgba(255,255,255,0.03);
                        border-radius: 8px;
                        border: 1px solid rgba(255,255,255,0.1);
                    }
                    QRadioButton::indicator { width: 18px; height: 18px; }
                    QRadioButton:hover { background-color: rgba(255,255,255,0.08); }
                    QRadioButton:checked { border: 1px solid #3B82F6; background-color: rgba(59, 130, 246, 0.1); }
                """)
                rb.setSizePolicy(rb.sizePolicy().Policy.MinimumExpanding, rb.sizePolicy().Policy.Minimum)
                self.input_group.addButton(rb, i)
                self.radios.append(rb)
                layout.addWidget(rb)
            self.answer_widget = None
        elif question_data.type == QuestionType.TRUE_FALSE:
            self.input_group = QButtonGroup(self)
            self.radios = []
            for i, opt in enumerate(["True", "False"]):
                rb = QRadioButton(opt)
                rb.setStyleSheet("font-size: 15px; color: #E2E8F0; padding: 5px;")
                self.input_group.addButton(rb, i)
                self.radios.append(rb)
                layout.addWidget(rb)
            self.answer_widget = None
        elif question_data.type == QuestionType.FILL_IN_BLANK:
            self.answer_widget = QLineEdit()
            self.answer_widget.setPlaceholderText("Type your answer here...")
            self.answer_widget.setStyleSheet("background-color: #0B1020; border: 1px solid rgba(255,255,255,0.08); border-radius: 8px; padding: 10px; color: white; font-size: 15px;")
            layout.addWidget(self.answer_widget)
        else:
            self.answer_widget = QTextEdit()
            self.answer_widget.setPlaceholderText("Type your answer here...")
            self.answer_widget.setStyleSheet("background-color: #0B1020; border: 1px solid rgba(255,255,255,0.08); border-radius: 8px; padding: 10px; color: white; font-size: 15px;")
            if question_data.type == QuestionType.SHORT_ANSWER:
                self.answer_widget.setMaximumHeight(100)
            layout.addWidget(self.answer_widget)
            
        # Feedback
        self.lbl_feedback = QLabel()
        self.lbl_feedback.setWordWrap(True)
        self.lbl_feedback.hide()
        layout.addWidget(self.lbl_feedback)

    def get_answer(self) -> str:
        if self.question_data.type in (QuestionType.MCQ, QuestionType.TRUE_FALSE):
            btn = self.input_group.checkedButton()
            return btn.text() if btn else ""
        elif self.question_data.type == QuestionType.FILL_IN_BLANK:
            return self.answer_widget.text()
        else:
            return self.answer_widget.toPlainText()

    def show_feedback(self, grade: float, feedback: str):
        color = "#22C55E" if grade > 0.7 else "#F59E0B" if grade > 0.4 else "#EF4444"
        bg_color = f"rgba({int(color[1:3], 16)}, {int(color[3:5], 16)}, {int(color[5:7], 16)}, 0.1)"
        
        self.lbl_feedback.setText(f"<b>Score: {grade*100:.1f}%</b><br><br>{feedback}")
        self.lbl_feedback.setStyleSheet(f"color: {color}; background-color: {bg_color}; padding: 15px; border-radius: 8px; margin-top: 15px;")
        self.lbl_feedback.show()
        
        # Disable inputs
        if self.question_data.type in (QuestionType.MCQ, QuestionType.TRUE_FALSE):
            for rb in self.radios:
                rb.setEnabled(False)
        else:
            self.answer_widget.setReadOnly(True)


class TestView(QWidget):
    def __init__(self, db: DatabaseManager, model_manager: ModelManager, parent=None):
        super().__init__(parent)
        self.db = db
        self.model_manager = model_manager
        
        from src.rag.retriever import Retriever
        self.retriever = Retriever(db, model_manager.embedder)
        self.agent = ExaminerAgent(db, model_manager, self.retriever)
        
        self.current_exam = None
        self.session: ExamSession | None = None
        self.question_widgets: list[QuestionWidget] = []
        
        self._init_ui()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0,0,0,0)
        
        self.stack = QStackedWidget()
        main_layout.addWidget(self.stack)
        
        self.page_config = QWidget()
        self._setup_config_page()
        self.stack.addWidget(self.page_config)
        
        self.page_exam = QWidget()
        self._setup_exam_page()
        self.stack.addWidget(self.page_exam)
        
        self.page_results = QWidget()
        self._setup_results_page()
        self.stack.addWidget(self.page_results)

        # Global loading overlay for this view
        self.loading = LoadingOverlay(self)

    def _setup_config_page(self):
        layout = QVBoxLayout(self.page_config)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        panel = QFrame()
        panel.setProperty("class", "CardPanel")
        panel.setFixedWidth(700)
        p_layout = QVBoxLayout(panel)
        p_layout.setContentsMargins(40, 40, 40, 40)
        p_layout.setSpacing(25)
        
        lbl_title = QLabel("Exam Center")
        lbl_title.setProperty("class", "PageTitle")
        lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        p_layout.addWidget(lbl_title)
        
        lbl_desc = QLabel("Select your examination mode.")
        lbl_desc.setProperty("class", "BodyText")
        lbl_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        p_layout.addWidget(lbl_desc)
        p_layout.addSpacing(10)
        
        # ── Mode Selection ──
        mode_layout = QHBoxLayout()
        mode_layout.setSpacing(15)
        
        self.btn_mode_official = QPushButton("Official Pattern")
        self.btn_mode_official.setToolTip("Uses exact DOCX template structures.")
        self.btn_mode_prediction = QPushButton("Prediction Paper")
        self.btn_mode_prediction.setToolTip("AI analyzes past weaknesses to predict questions.")
        self.btn_mode_custom = QPushButton("Custom Mock")
        
        self.mode_buttons = [self.btn_mode_official, self.btn_mode_prediction, self.btn_mode_custom]
        for btn in self.mode_buttons:
            btn.setProperty("class", "SecondaryButton")
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked, b=btn: self._select_mode(b))
            mode_layout.addWidget(btn)
            
        self.btn_mode_custom.setChecked(True)
        self._select_mode(self.btn_mode_custom)
            
        p_layout.addLayout(mode_layout)
        p_layout.addSpacing(20)
        
        # 1. Subject
        p_layout.addWidget(QLabel("1. Choose Subject"))
        self.cb_subject = QComboBox()
        self.cb_subject.setStyleSheet("padding: 8px; border-radius: 6px; background-color: #0B1020; border: 1px solid rgba(255,255,255,0.1); color: white;")
        self._populate_subjects()
        self.cb_subject.currentTextChanged.connect(self._populate_units)
        p_layout.addWidget(self.cb_subject)
        
        # 2. Scope
        p_layout.addWidget(QLabel("2. Choose Scope"))
        self.cb_unit = QComboBox()
        self.cb_unit.setStyleSheet("padding: 8px; border-radius: 6px; background-color: #0B1020; border: 1px solid rgba(255,255,255,0.1); color: white;")
        p_layout.addWidget(self.cb_unit)
        self._populate_units(self.cb_subject.currentText())
        
        # 3. Question Types
        p_layout.addWidget(QLabel("3. Question Types"))
        types_layout = QHBoxLayout()
        self.chk_mcq = QCheckBox("MCQ")
        self.chk_mcq.setChecked(True)
        self.chk_tf = QCheckBox("True/False")
        self.chk_tf.setChecked(True)
        self.chk_fib = QCheckBox("Fill Blank")
        self.chk_short = QCheckBox("Short Answer")
        
        for chk in [self.chk_mcq, self.chk_tf, self.chk_fib, self.chk_short]:
            chk.setStyleSheet("color: #E2E8F0;")
            types_layout.addWidget(chk)
            
        p_layout.addLayout(types_layout)
        
        # 4. Count
        count_layout = QHBoxLayout()
        count_layout.addWidget(QLabel("4. Number of Questions:"))
        self.spin_count = QSpinBox()
        self.spin_count.setRange(1, 20)
        self.spin_count.setValue(5)
        self.spin_count.setStyleSheet("padding: 5px; background-color: #0B1020; color: white;")
        count_layout.addWidget(self.spin_count)
        count_layout.addStretch()
        p_layout.addLayout(count_layout)
        
        p_layout.addSpacing(20)
        
        self.btn_gen = QPushButton("Generate Exam")
        self.btn_gen.setProperty("class", "PrimaryButton")
        self.btn_gen.clicked.connect(self._start_generation)
        p_layout.addWidget(self.btn_gen)
        
        layout.addWidget(panel)

    def _populate_subjects(self):
        self.cb_subject.clear()
        for s in self.db.subjects.get_all():
            self.cb_subject.addItem(format_title_case(s.name), userData=s.name)

    def _populate_units(self, display_name: str):
        self.cb_unit.clear()
        if not display_name: return
        
        idx = self.cb_subject.currentIndex()
        actual_name = self.cb_subject.itemData(idx)
        
        sub = self.db.subjects.get_by_name(actual_name)
        if sub:
            self.cb_unit.addItem("All (Full Subject)", userData="All")
            for u in sub.units:
                self.cb_unit.addItem(format_title_case(u.name), userData=u.name)

    def _select_mode(self, selected_btn: QPushButton):
        for btn in self.mode_buttons:
            if btn != selected_btn:
                btn.setChecked(False)
                btn.setStyleSheet("")
            else:
                btn.setChecked(True)
                btn.setStyleSheet("background-color: #3B82F6; color: white;")
                
    def _start_generation(self):
        sub_idx = self.cb_subject.currentIndex()
        subject = self.cb_subject.itemData(sub_idx)
        
        unit_idx = self.cb_unit.currentIndex()
        unit = self.cb_unit.itemData(unit_idx)
        count = self.spin_count.value()
        
        types = []
        if self.chk_mcq.isChecked(): types.append(QuestionType.MCQ)
        if self.chk_tf.isChecked(): types.append(QuestionType.TRUE_FALSE)
        if self.chk_fib.isChecked(): types.append(QuestionType.FILL_IN_BLANK)
        if self.chk_short.isChecked(): types.append(QuestionType.SHORT_ANSWER)
            
        if not types:
            QMessageBox.warning(self, "Error", "Select at least one question type.")
            return
            
        mode = "custom"
        if self.btn_mode_official.isChecked():
            mode = "official"
        elif self.btn_mode_prediction.isChecked():
            mode = "prediction"

        self.btn_gen.setEnabled(False)
        self.loading.show_loading("Generating Exam...\nAnalyzing syllabus\nBuilding question paper\nPreparing answer key")
        
        self.gen_worker = ExamGenWorker(self.agent, subject, unit, types, count, mode)
        self.thread = threading.Thread(target=self.gen_worker.run)
        self.gen_worker.finished.connect(self._on_generated)
        self.gen_worker.error.connect(self._on_gen_error)
        self.thread.start()

    @pyqtSlot(Exam)
    def _on_generated(self, exam: Exam):
        self.current_exam = exam
        self.session = ExamSession(
            exam_id=exam.id,
            subject=exam.subject,
            scope=exam.scope,
            questions=exam.questions,
            mode="standard"
        )
        self.btn_gen.setEnabled(True)
        self.loading.hide_loading()
        self._load_exam_ui()
        self.stack.setCurrentWidget(self.page_exam)

    @pyqtSlot(str)
    def _on_gen_error(self, error: str):
        self.btn_gen.setEnabled(True)
        self.loading.hide_loading()
        QMessageBox.critical(self, "Generation Error", error)

    def _setup_exam_page(self):
        layout = QVBoxLayout(self.page_exam)
        layout.setContentsMargins(40, 20, 40, 20)
        
        # Header
        header = QHBoxLayout()
        self.btn_exam_back = QPushButton("← Back to Exam Center")
        self.btn_exam_back.setProperty("class", "SecondaryButton")
        self.btn_exam_back.clicked.connect(self._back_to_center)
        header.addWidget(self.btn_exam_back)
        
        header.addStretch()
        
        self.lbl_exam_progress = QLabel("Question 1 / 10")
        self.lbl_exam_progress.setStyleSheet("font-weight: bold; font-size: 16px; color: #94A3B8;")
        header.addWidget(self.lbl_exam_progress)
        
        header.addStretch()
        
        self.btn_exam_exit = QPushButton("Exit Exam")
        self.btn_exam_exit.setProperty("class", "SecondaryButton")
        self.btn_exam_exit.setStyleSheet("color: #EF4444; border: 1px solid #EF4444;")
        self.btn_exam_exit.clicked.connect(self._exit_exam)
        header.addWidget(self.btn_exam_exit)
        
        layout.addLayout(header)
        layout.addSpacing(20)
        
        # Scroll Area for Questions
        self.scroll_view = QScrollArea()
        self.scroll_view.setWidgetResizable(True)
        self.scroll_view.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        
        self.scroll_content = QWidget()
        self.scroll_content.setStyleSheet("background-color: transparent;")
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        self.scroll_layout.setSpacing(20)
        self.scroll_view.setWidget(self.scroll_content)
        
        layout.addWidget(self.scroll_view, stretch=1)
        
        # Pagination Bar
        self.nav_widget = QWidget()
        nav_layout = QHBoxLayout(self.nav_widget)
        nav_layout.setContentsMargins(0, 10, 0, 0)
        
        self.btn_prev = QPushButton("← Previous")
        self.btn_prev.setProperty("class", "SecondaryButton")
        self.btn_prev.clicked.connect(self._prev_q)
        
        self.btn_next = QPushButton("Next →")
        self.btn_next.setProperty("class", "SecondaryButton")
        self.btn_next.clicked.connect(self._next_q)
        
        self.btn_finish = QPushButton("Finish Exam")
        self.btn_finish.setProperty("class", "PrimaryButton")
        self.btn_finish.setStyleSheet("background-color: #22C55E;")
        self.btn_finish.clicked.connect(self._submit_exam)
        self.btn_finish.hide()
        
        nav_layout.addStretch()
        nav_layout.addWidget(self.btn_prev)
        nav_layout.addWidget(self.btn_next)
        nav_layout.addWidget(self.btn_finish)
        nav_layout.addStretch()
        
        layout.addWidget(self.nav_widget)
        
    def _setup_results_page(self):
        layout = QVBoxLayout(self.page_results)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        panel = QFrame()
        panel.setProperty("class", "CardPanel")
        panel.setFixedWidth(600)
        p_layout = QVBoxLayout(panel)
        p_layout.setContentsMargins(40, 40, 40, 40)
        p_layout.setSpacing(25)
        
        lbl_title = QLabel("Exam Results")
        lbl_title.setProperty("class", "PageTitle")
        lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        p_layout.addWidget(lbl_title)
        
        self.lbl_score = QLabel("Score: 0%")
        self.lbl_score.setStyleSheet("font-size: 32px; font-weight: bold; color: #22C55E;")
        self.lbl_score.setAlignment(Qt.AlignmentFlag.AlignCenter)
        p_layout.addWidget(self.lbl_score)
        
        self.lbl_stats = QLabel()
        self.lbl_stats.setProperty("class", "BodyText")
        self.lbl_stats.setAlignment(Qt.AlignmentFlag.AlignCenter)
        p_layout.addWidget(self.lbl_stats)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)
        
        self.btn_review = QPushButton("Review Answers")
        self.btn_review.setProperty("class", "SecondaryButton")
        self.btn_review.clicked.connect(self._review_answers)
        
        self.btn_back_center = QPushButton("Back to Exam Center")
        self.btn_back_center.setProperty("class", "PrimaryButton")
        self.btn_back_center.clicked.connect(self._back_to_center)
        
        btn_layout.addWidget(self.btn_review)
        btn_layout.addWidget(self.btn_back_center)
        p_layout.addLayout(btn_layout)
        
        layout.addWidget(panel)

    def _load_exam_ui(self):
        for w in self.question_widgets:
            self.scroll_layout.removeWidget(w)
            w.setParent(None)
        self.question_widgets.clear()
        
        for i, q in enumerate(self.session.questions):
            w = QuestionWidget(i, q)
            w.setMinimumWidth(800)
            w.setMaximumWidth(1000)
            self.question_widgets.append(w)
            self.scroll_layout.addWidget(w)
            
        self.session.current_question_index = 0
        self.session.mode = "testing"
        self._update_visibility()

    def _update_visibility(self):
        if self.session.mode == "review":
            self.nav_widget.hide()
            self.lbl_exam_progress.setText("Review Mode")
            self.btn_exam_exit.hide()
            for w in self.question_widgets:
                w.show()
        else:
            self.nav_widget.show()
            self.btn_exam_exit.show()
            idx = self.session.current_question_index
            total = len(self.question_widgets)
            
            for i, w in enumerate(self.question_widgets):
                w.setVisible(i == idx)
                
            self.lbl_exam_progress.setText(f"Question {idx + 1} / {total}")
            
            self.btn_prev.setVisible(idx > 0)
            
            if idx == total - 1:
                self.btn_next.hide()
                self.btn_finish.show()
            else:
                self.btn_next.show()
                self.btn_finish.hide()
            
        # Ensure the layout recalculates its size
        self.scroll_content.adjustSize()
        
    def _back_to_center(self):
        self.current_exam = None
        self.session = None
        for w in self.question_widgets:
            w.deleteLater()
        self.question_widgets.clear()
        self.stack.setCurrentWidget(self.page_config)
        
    def _exit_exam(self):
        reply = QMessageBox.question(
            self, "Exit Exam", "You have not completed this exam.\nProgress will be lost.\n\nExit anyway?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self._back_to_center()

    def _prev_q(self):
        if self.session.current_question_index > 0:
            self.session.current_question_index -= 1
            self._update_visibility()

    def _next_q(self):
        if self.session.current_question_index < len(self.question_widgets) - 1:
            self.session.current_question_index += 1
            self._update_visibility()

    def _submit_exam(self):
        reply = QMessageBox.question(
            self, "Submit", "Submit exam for AI grading?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.No: return
            
        # Sync answers to session and the exam object
        for i, w in enumerate(self.question_widgets):
            ans = w.get_answer()
            self.session.answers[i] = ans
            self.current_exam.questions[i].user_answer = ans
            
        self.btn_finish.setEnabled(False)
        self.loading.show_loading("Evaluating Responses...\nChecking answers\nGenerating topic analysis")
        
        self.grade_worker = GradeWorker(self.agent, self.current_exam)
        self.thread = threading.Thread(target=self.grade_worker.run)
        self.grade_worker.finished.connect(self._on_graded)
        self.grade_worker.error.connect(self._on_grade_error)
        self.thread.start()

    @pyqtSlot(float)
    def _on_graded(self, score: float):
        self.btn_finish.setEnabled(True)
        self.loading.hide_loading()
        self.session.score = score
        self.current_exam.score = score
        
        # Persistent Storage
        from src.core.schemas import AnalyticsEvent
        self.db.exams.save(self.current_exam)
        self.db.analytics.log(AnalyticsEvent(
            event_type="exam_completed",
            subject=self.current_exam.subject,
            unit=self.current_exam.scope,
            data={"score": score, "mode": self.session.mode}
        ))
        
        # Show Results Screen
        self.lbl_score.setText(f"Score: {score*100:.1f}%")
        
        correct = sum(1 for q in self.current_exam.questions if getattr(q, 'grade', 0) > 0.5)
        total = len(self.current_exam.questions)
        self.lbl_stats.setText(f"Correct Answers: {correct} / {total}\nSubject: {self.current_exam.subject}")
        
        for i, w in enumerate(self.question_widgets):
            q_data = self.current_exam.questions[i]
            w.show_feedback(q_data.grade, q_data.feedback)
            
        self.stack.setCurrentWidget(self.page_results)

    def _review_answers(self):
        self.session.mode = "review"
        self._update_visibility()
        self.stack.setCurrentWidget(self.page_exam)

    @pyqtSlot(str)
    def _on_grade_error(self, error: str):
        self.btn_finish.setEnabled(True)
        self.loading.hide_loading()
        QMessageBox.critical(self, "Grading Error", error)

