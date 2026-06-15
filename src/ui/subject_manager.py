"""
subject_manager — Subject Upload and Indexing
==============================================
Manages uploading new textbook PDFs, using AI to infer the subject name,
splitting them into chapters, and triggering RAG indexing.
"""

import logging
import os
import shutil
from pathlib import Path

import fitz
from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from src.core.config import CHAPTERS_DIR, RAW_DIR
from src.core.database import DatabaseManager
from src.core.models import ModelManager
from src.ui.workers import IndexWorker

logger = logging.getLogger(__name__)


class SubjectManager(QWidget):
    def __init__(self, db: DatabaseManager, model_manager: ModelManager, parent=None):
        super().__init__(parent)
        self.db = db
        self.model_manager = model_manager
        
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        
        # Header
        header_layout = QHBoxLayout()
        lbl_title = QLabel("Subject Management")
        lbl_title.setProperty("class", "HeaderLabel")
        header_layout.addWidget(lbl_title)
        
        header_layout.addStretch()
        
        btn_add = QPushButton("Upload New Book (PDF)")
        btn_add.setStyleSheet("background-color: #238636; color: white; padding: 8px 16px; font-weight: bold;")
        btn_add.clicked.connect(self._on_upload)
        header_layout.addWidget(btn_add)
        
        layout.addLayout(header_layout)
        
        # Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.hide()
        layout.addWidget(self.progress_bar)
        
        self.lbl_status = QLabel("")
        self.lbl_status.hide()
        layout.addWidget(self.lbl_status)
        
        # Table of Subjects
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Subject Name", "Units", "Total Chunks", "Actions"])
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table)
        
        self.refresh_table()

    def refresh_table(self):
        self.table.setRowCount(0)
        subjects = self.db.subjects.get_all()
        
        for row, sub in enumerate(subjects):
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(sub.name))
            self.table.setItem(row, 1, QTableWidgetItem(str(len(sub.units))))
            
            total_chunks = sum(u.chunk_count for u in sub.units)
            self.table.setItem(row, 2, QTableWidgetItem(str(total_chunks)))
            
            # Re-index button
            btn_reindex = QPushButton("Re-Index")
            btn_reindex.clicked.connect(lambda checked, s=sub.name: self._start_indexing(s, force=True))
            self.table.setCellWidget(row, 3, btn_reindex)

    def _on_upload(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Textbook PDF", "", "PDF Files (*.pdf)"
        )
        if not file_path:
            return
            
        path = Path(file_path)
        book_filename = path.name
        
        # Copy to data/raw if not there
        RAW_DIR.mkdir(parents=True, exist_ok=True)
        dest_path = RAW_DIR / book_filename
        if path.resolve() != dest_path.resolve():
            shutil.copy2(path, dest_path)
            
        # Extract TOC to infer subject name
        toc_text = self._extract_toc_for_prompt(dest_path)
        
        # Call AI
        self.lbl_status.setText("Asking AI to infer subject name...")
        self.lbl_status.show()
        
        import threading
        self.thread = threading.Thread(
            target=self._infer_and_confirm,
            args=(book_filename, toc_text, dest_path)
        )
        self.thread.start()

    def _extract_toc_for_prompt(self, pdf_path: Path) -> str:
        try:
            doc = fitz.open(str(pdf_path))
            toc = doc.get_toc()
            doc.close()
            
            if not toc:
                return "No TOC found."
                
            # Limit to top-level items to save tokens
            lines = [f"{item[1]}" for item in toc if item[0] == 1]
            return "\n".join(lines[:20])
        except Exception as e:
            logger.warning("Could not extract TOC: %s", e)
            return "Error extracting TOC."

    def _infer_and_confirm(self, book_filename: str, toc_text: str, pdf_path: Path):
        from src.core.prompt_manager import PromptManager
        prompt = PromptManager().get_prompt("subject_manager_toc", book_filename=book_filename, toc_text=toc_text)

        try:
            llm = self.model_manager.fast
            subject_name = llm.generate(prompt, temperature=0.1).strip()
            
            # Clean up potential artifacts
            subject_name = subject_name.replace("```", "").strip()
            
            # Trigger confirmation in main thread
            from PyQt6.QtCore import QMetaObject, Q_ARG, Qt
            QMetaObject.invokeMethod(
                self, 
                "_show_confirmation",
                Qt.ConnectionType.QueuedConnection,
                Q_ARG(str, subject_name),
                Q_ARG(str, book_filename)
            )
        except Exception as e:
            logger.error("AI inference failed: %s", e)
            # Fallback to filename
            fallback = book_filename.replace(".pdf", "").upper().replace(" ", "_")
            from PyQt6.QtCore import QMetaObject, Q_ARG, Qt
            QMetaObject.invokeMethod(
                self, 
                "_show_confirmation",
                Qt.ConnectionType.QueuedConnection,
                Q_ARG(str, fallback),
                Q_ARG(str, book_filename)
            )

    @pyqtSlot(str, str)
    def _show_confirmation(self, subject_name: str, book_filename: str):
        self.lbl_status.hide()
        
        from PyQt6.QtWidgets import QInputDialog
        final_name, ok = QInputDialog.getText(
            self,
            "Confirm Subject Name",
            "The AI suggested the following subject name based on the book.\nYou can edit it if needed:",
            text=subject_name
        )
        
        if ok and final_name.strip():
            self._process_book(final_name.strip(), book_filename)

    def _process_book(self, subject_name: str, book_filename: str):
        self.lbl_status.setText(f"Splitting {book_filename} into chapters...")
        self.lbl_status.show()
        
        # We need to run split_books in a thread to not block UI
        import threading
        def worker():
            try:
                # Rename the raw file to the confirmed subject name so splitter derives it correctly
                old_pdf_path = RAW_DIR / book_filename
                new_pdf_path = RAW_DIR / f"{subject_name}.pdf"
                if old_pdf_path.exists() and old_pdf_path != new_pdf_path:
                    old_pdf_path.rename(new_pdf_path)
                
                from splitter import split_books
                split_books(RAW_DIR, CHAPTERS_DIR, [f"{subject_name}.pdf"])
                
                # Register in DB
                from src.rag.indexer import scan_and_register_subjects
                scan_and_register_subjects(self.db)
                
                # Trigger indexing
                from PyQt6.QtCore import QMetaObject, Q_ARG, Qt
                QMetaObject.invokeMethod(
                    self, 
                    "_start_indexing",
                    Qt.ConnectionType.QueuedConnection,
                    Q_ARG(str, subject_name),
                    Q_ARG(bool, False)
                )
            except Exception as e:
                logger.error("Split error: %s", e)
                
        threading.Thread(target=worker).start()

    @pyqtSlot(str, bool)
    def _start_indexing(self, subject_name: str, force: bool = False):
        self.progress_bar.setRange(0, 0) # Indeterminate
        self.progress_bar.show()
        self.lbl_status.setText(f"Indexing '{subject_name}' ...")
        self.lbl_status.show()
        
        self.index_worker = IndexWorker(self.db, self.model_manager.embedder, subject_name, force)
        self.index_worker.progress.connect(self._on_index_progress)
        self.index_worker.finished.connect(self._on_index_finished)
        self.index_worker.error.connect(self._on_index_error)
        
        import threading
        self.thread = threading.Thread(target=self.index_worker.run)
        self.thread.start()

    @pyqtSlot(str)
    def _on_index_progress(self, msg: str):
        self.lbl_status.setText(msg)

    @pyqtSlot(int)
    def _on_index_finished(self, count: int):
        self.progress_bar.hide()
        self.lbl_status.setText(f"Indexing complete! Generated {count} chunks.")
        self.refresh_table()

    @pyqtSlot(str)
    def _on_index_error(self, error: str):
        self.progress_bar.hide()
        self.lbl_status.setText(f"Error during indexing: {error}")
        QMessageBox.critical(self, "Indexing Error", error)
