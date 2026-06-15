"""
test_view — Exam Generation and Testing Environment
=====================================================
Allows users to generate ad-hoc exams, take them in either paginated
or list mode, and get AI-graded feedback.
"""

from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtWidgets import (
    QButtonGroup,
    QCheckBox,
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QRadioButton,
    QScrollArea,
    QSpinBox,
    QStackedWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from src.agents.examiner_agent import ExaminerAgent
from src.core.database import DatabaseManager
from src.core.models import ModelManager
from src.core.schemas import Exam, QuestionType
from src.ui.workers import ExamGenWorker, GradeWorker


class QuestionWidget(QFrame):
    """Widget for a single exam question during the test."""
    def __init__(self, index: int, question_data, parent=None):
        super().__init__(parent)
        self.setProperty("class", "CardPanel")
        self.index = index
        self.question_data = question_data
        
        layout = QVBoxLayout(self)
        
        # Prompt
        lbl_prompt = QLabel(f"<b>Q{index + 1}:</b> {question_data.prompt}")
        lbl_prompt.setWordWrap(True)
        layout.addWidget(lbl_prompt)
        
        # Answer Input
        if question_data.type == QuestionType.MCQ and question_data.options:
            self.input_group = QButtonGroup(self)
            self.radios = []
            for i, opt in enumerate(question_data.options):
                rb = QRadioButton(opt)
                self.input_group.addButton(rb, i)
                self.radios.append(rb)
                layout.addWidget(rb)
            self.answer_widget = None
        elif question_data.type == QuestionType.TRUE_FALSE:
            self.input_group = QButtonGroup(self)
            self.radios = []
            for i, opt in enumerate(["True", "False"]):
                rb = QRadioButton(opt)
                self.input_group.addButton(rb, i)
                self.radios.append(rb)
                layout.addWidget(rb)
            self.answer_widget = None
        elif question_data.type == QuestionType.FILL_IN_BLANK:
            from PyQt6.QtWidgets import QLineEdit
            self.answer_widget = QLineEdit()
            self.answer_widget.setPlaceholderText("Type your answer here...")
            layout.addWidget(self.answer_widget)
        else:
            self.answer_widget = QTextEdit()
            self.answer_widget.setPlaceholderText("Type your answer here...")
            if question_data.type == QuestionType.SHORT_ANSWER:
                self.answer_widget.setMaximumHeight(80)
            layout.addWidget(self.answer_widget)
            
        # Feedback (hidden initially)
        self.lbl_feedback = QLabel()
        self.lbl_feedback.setWordWrap(True)
        self.lbl_feedback.setStyleSheet("color: #F78166;")
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
        color = "#3FB950" if grade > 0.7 else "#F78166"
        self.lbl_feedback.setText(f"<b>Score: {grade*100:.1f}%</b><br>{feedback}")
        self.lbl_feedback.setStyleSheet(f"color: {color}; margin-top: 10px;")
        self.lbl_feedback.show()
        
        # Disable inputs
        if self.question_data.type in (QuestionType.MCQ, QuestionType.TRUE_FALSE):
            for rb in self.radios:
                rb.setEnabled(False)
        else:
            self.answer_widget.setReadOnly(True)


class TestView(QWidget):
    def __init__(
        self,
        db: DatabaseManager,
        model_manager: ModelManager,
        parent=None,
    ):
        super().__init__(parent)
        self.db = db
        self.model_manager = model_manager
        
        from src.rag.retriever import Retriever
        self.retriever = Retriever(db, model_manager.embedder)
        self.agent = ExaminerAgent(db, model_manager, self.retriever)
        
        self.current_exam = None
        self.question_widgets = []
        self.current_q_index = 0
        
        self._init_ui()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        
        self.stack = QStackedWidget()
        main_layout.addWidget(self.stack)
        
        # ── Page 1: Configuration ──
        self.page_config = QWidget()
        self._setup_config_page()
        self.stack.addWidget(self.page_config)
        
        # ── Page 2: Exam Taking ──
        self.page_exam = QWidget()
        self._setup_exam_page()
        self.stack.addWidget(self.page_exam)

    def _setup_config_page(self):
        layout = QVBoxLayout(self.page_config)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        
        panel = QFrame()
        panel.setProperty("class", "CardPanel")
        panel.setFixedWidth(500)
        p_layout = QVBoxLayout(panel)
        
        lbl_title = QLabel("Generate New Exam")
        lbl_title.setProperty("class", "HeaderLabel")
        p_layout.addWidget(lbl_title)
        
        # Subject selection
        p_layout.addWidget(QLabel("Select Subject:"))
        self.cb_subject = QComboBox()
        self._populate_subjects()
        self.cb_subject.currentTextChanged.connect(self._populate_units)
        p_layout.addWidget(self.cb_subject)
        
        # Unit selection
        p_layout.addWidget(QLabel("Select Scope:"))
        self.cb_unit = QComboBox()
        p_layout.addWidget(self.cb_unit)
        self._populate_units(self.cb_subject.currentText())
        
        # Count
        p_layout.addWidget(QLabel("Number of Questions:"))
        self.spin_count = QSpinBox()
        self.spin_count.setRange(1, 20)
        self.spin_count.setValue(5)
        p_layout.addWidget(self.spin_count)
        
        # Types
        p_layout.addWidget(QLabel("Question Types:"))
        self.chk_mcq = QCheckBox("Multiple Choice")
        self.chk_mcq.setChecked(True)
        self.chk_tf = QCheckBox("True/False")
        self.chk_tf.setChecked(True)
        self.chk_fib = QCheckBox("Fill in the Blank")
        self.chk_fib.setChecked(True)
        self.chk_short = QCheckBox("Short Answer")
        self.chk_short.setChecked(True)
        self.chk_essay = QCheckBox("Essay")
        
        p_layout.addWidget(self.chk_mcq)
        p_layout.addWidget(self.chk_tf)
        p_layout.addWidget(self.chk_fib)
        p_layout.addWidget(self.chk_short)
        p_layout.addWidget(self.chk_essay)
        
        # Generate Button
        self.btn_gen = QPushButton("Generate Exam")
        self.btn_gen.setStyleSheet("background-color: #1F6FEB; color: white; padding: 8px; margin-top: 15px;")
        self.btn_gen.clicked.connect(self._start_generation)
        p_layout.addWidget(self.btn_gen)
        
        self.lbl_status = QLabel("")
        p_layout.addWidget(self.lbl_status)
        
        layout.addWidget(panel)

    def _populate_subjects(self):
        self.cb_subject.clear()
        subjects = self.db.subjects.get_all()
        for s in subjects:
            self.cb_subject.addItem(s.name)

    def _populate_units(self, subject_name: str):
        self.cb_unit.clear()
        if not subject_name:
            return
        sub = self.db.subjects.get_by_name(subject_name)
        if sub:
            self.cb_unit.addItem("All (Full Subject)")
            for u in sub.units:
                self.cb_unit.addItem(u.name)

    def _start_generation(self):
        subject = self.cb_subject.currentText()
        unit = self.cb_unit.currentText()
        if unit == "All (Full Subject)":
            unit = "All"
        count = self.spin_count.value()
        
        types = []
        if self.chk_mcq.isChecked():
            types.append(QuestionType.MCQ)
        if self.chk_tf.isChecked():
            types.append(QuestionType.TRUE_FALSE)
        if self.chk_fib.isChecked():
            types.append(QuestionType.FILL_IN_BLANK)
        if self.chk_short.isChecked():
            types.append(QuestionType.SHORT_ANSWER)
        if self.chk_essay.isChecked():
            types.append(QuestionType.ESSAY)
            
        if not types:
            QMessageBox.warning(self, "Error", "Select at least one question type.")
            return
            
        self.btn_gen.setEnabled(False)
        self.lbl_status.setText("Generating exam using reasoning model... Please wait.")
        
        self.gen_worker = ExamGenWorker(self.agent, subject, unit, types, count)
        import threading
        self.thread = threading.Thread(target=self.gen_worker.run)
        self.gen_worker.finished.connect(self._on_generated)
        self.gen_worker.error.connect(self._on_gen_error)
        self.thread.start()

    @pyqtSlot(Exam)
    def _on_generated(self, exam: Exam):
        self.current_exam = exam
        self.btn_gen.setEnabled(True)
        self.lbl_status.setText("")
        self._load_exam_ui()
        self.stack.setCurrentWidget(self.page_exam)

    @pyqtSlot(str)
    def _on_gen_error(self, error: str):
        self.btn_gen.setEnabled(True)
        self.lbl_status.setText(f"Error: {error}")
        QMessageBox.critical(self, "Generation Error", error)

    def _setup_exam_page(self):
        layout = QVBoxLayout(self.page_exam)
        
        # Header controls
        header = QHBoxLayout()
        self.lbl_exam_title = QLabel("Exam")
        self.lbl_exam_title.setProperty("class", "HeaderLabel")
        header.addWidget(self.lbl_exam_title)
        
        self.btn_toggle_mode = QPushButton("Switch to Paginated Mode")
        self.btn_toggle_mode.clicked.connect(self._toggle_view_mode)
        header.addWidget(self.btn_toggle_mode, alignment=Qt.AlignmentFlag.AlignRight)
        layout.addLayout(header)
        
        # View modes stack
        self.exam_view_stack = QStackedWidget()
        
        # Mode 1: List View (Scroll Area)
        self.scroll_view = QScrollArea()
        self.scroll_view.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scroll_view.setWidget(self.scroll_content)
        self.exam_view_stack.addWidget(self.scroll_view)
        
        # Mode 2: Paginated View
        self.page_view = QWidget()
        self.page_layout = QVBoxLayout(self.page_view)
        self.q_container = QVBoxLayout()
        self.page_layout.addLayout(self.q_container, stretch=1)
        
        nav_layout = QHBoxLayout()
        self.btn_prev = QPushButton("Previous")
        self.btn_prev.clicked.connect(self._prev_q)
        self.btn_next = QPushButton("Next")
        self.btn_next.clicked.connect(self._next_q)
        nav_layout.addWidget(self.btn_prev)
        nav_layout.addStretch()
        self.lbl_page = QLabel()
        nav_layout.addWidget(self.lbl_page)
        nav_layout.addStretch()
        nav_layout.addWidget(self.btn_next)
        self.page_layout.addLayout(nav_layout)
        self.exam_view_stack.addWidget(self.page_view)
        
        layout.addWidget(self.exam_view_stack, stretch=1)
        
        # Submit Button
        self.btn_submit = QPushButton("Submit Exam")
        self.btn_submit.setStyleSheet("background-color: #238636; color: white; padding: 10px; font-weight: bold;")
        self.btn_submit.clicked.connect(self._submit_exam)
        layout.addWidget(self.btn_submit)
        
        self.is_list_mode = True

    def _load_exam_ui(self):
        self.lbl_exam_title.setText(f"Exam: {self.current_exam.subject} - {self.current_exam.scope}")
        
        # Clear existing widgets
        for w in self.question_widgets:
            self.scroll_layout.removeWidget(w)
            w.setParent(None)
        self.question_widgets.clear()
        
        # Create new widgets
        for i, q in enumerate(self.current_exam.questions):
            w = QuestionWidget(i, q)
            self.question_widgets.append(w)
            self.scroll_layout.addWidget(w)
            
        self.btn_submit.show()
        self.btn_submit.setEnabled(True)
        self.current_q_index = 0
        self._update_pagination()
        
        # Default to List Mode
        if not self.is_list_mode:
            self._toggle_view_mode()

    def _toggle_view_mode(self):
        self.is_list_mode = not self.is_list_mode
        if self.is_list_mode:
            self.btn_toggle_mode.setText("Switch to Paginated Mode")
            # Move all widgets back to scroll layout
            for w in self.question_widgets:
                self.scroll_layout.addWidget(w)
            self.exam_view_stack.setCurrentWidget(self.scroll_view)
        else:
            self.btn_toggle_mode.setText("Switch to List Mode")
            self.exam_view_stack.setCurrentWidget(self.page_view)
            self._update_pagination()

    def _update_pagination(self):
        if not self.question_widgets:
            return
            
        # Clear container
        while self.q_container.count():
            item = self.q_container.takeAt(0)
            if item.widget():
                item.widget().setParent(None)
                
        # Add current widget
        current_w = self.question_widgets[self.current_q_index]
        self.q_container.addWidget(current_w)
        
        self.lbl_page.setText(f"Question {self.current_q_index + 1} of {len(self.question_widgets)}")
        self.btn_prev.setEnabled(self.current_q_index > 0)
        self.btn_next.setEnabled(self.current_q_index < len(self.question_widgets) - 1)

    def _prev_q(self):
        if self.current_q_index > 0:
            self.current_q_index -= 1
            self._update_pagination()

    def _next_q(self):
        if self.current_q_index < len(self.question_widgets) - 1:
            self.current_q_index += 1
            self._update_pagination()

    def _submit_exam(self):
        reply = QMessageBox.question(
            self, "Submit", "Are you sure you want to submit the exam for grading?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.No:
            return
            
        # Collect answers
        for i, w in enumerate(self.question_widgets):
            self.current_exam.questions[i].user_answer = w.get_answer()
            
        self.btn_submit.setEnabled(False)
        self.btn_submit.setText("Grading... Please wait.")
        
        self.grade_worker = GradeWorker(self.agent, self.current_exam)
        import threading
        self.thread = threading.Thread(target=self.grade_worker.run)
        self.grade_worker.finished.connect(self._on_graded)
        self.grade_worker.error.connect(self._on_grade_error)
        self.thread.start()

    @pyqtSlot(float)
    def _on_graded(self, score: float):
        self.btn_submit.hide()
        QMessageBox.information(self, "Exam Graded", f"Grading complete!\nYour score: {score*100:.1f}%")
        
        # Show feedback on all widgets
        for i, w in enumerate(self.question_widgets):
            q_data = self.current_exam.questions[i]
            w.show_feedback(q_data.grade, q_data.feedback)
            
        # Force list mode to see all feedback easily
        if not self.is_list_mode:
            self._toggle_view_mode()

    @pyqtSlot(str)
    def _on_grade_error(self, error: str):
        self.btn_submit.setEnabled(True)
        self.btn_submit.setText("Submit Exam")
        QMessageBox.critical(self, "Grading Error", error)
