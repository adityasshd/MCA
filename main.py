"""
main — Entry Point
===================
Initialises the database, model manager, and GUI.
Preserves the old CLI splitter under the --split flag.
"""

import sys
import os
import argparse
import logging
from pathlib import Path

# Disable hardware acceleration for QtWebEngine to prevent EGL/Vulkan driver crashes
os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--disable-gpu --no-sandbox"
os.environ["QT_XCB_GL_INTEGRATION"] = "none"

from src.core.config import get_config
from src.core.database import DatabaseManager
from src.core.models import ModelManager

# Configure root logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("mca_app")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="main",
        description="MCA AI Study Suite.",
    )
    parser.add_argument(
        "--gui",
        action="store_true",
        default=True,
        help="Launch the graphical interface (default).",
    )
    parser.add_argument(
        "--split",
        dest="books",
        nargs="*",
        default=None,
        metavar="BOOK",
        help="Split PDF books into individual chapter PDFs (legacy CLI).",
    )
    parser.add_argument(
        "--index",
        action="store_true",
        help="Run RAG indexing via CLI.",
    )
    return parser


def launch_gui(db: DatabaseManager, model_manager: ModelManager):
    """Launch the PyQt6 application."""
    from PyQt6.QtWidgets import QApplication
    from src.ui.theme import apply_theme
    from src.ui.main_window import MainWindow

    app = QApplication(sys.argv)
    apply_theme(app)

    window = MainWindow(db, model_manager)
    window.show()

    sys.exit(app.exec())


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.books is not None:
        # Legacy CLI splitter
        from splitter import split_books
        from src.core.config import RAW_DIR, CHAPTERS_DIR
        split_books(RAW_DIR, CHAPTERS_DIR, args.books)
        return

    # Initialize Backend
    config = get_config()
    
    logger.info("Initializing DB Manager (%s)...", config.DB_BACKEND)
    # Extract DB name from URI or config if needed, here we use default
    db = DatabaseManager.from_config(
        backend=config.DB_BACKEND, 
        uri=config.MONGODB_SERVER_URL
    )

    logger.info("Initializing Model Manager...")
    model_manager = ModelManager.from_db(db, config)

    # Initial subject scan
    from src.rag.indexer import scan_and_register_subjects
    scan_and_register_subjects(db)

    if args.index:
        # CLI Indexer
        from src.rag.indexer import index_subject
        logger.info("Starting CLI indexer...")
        subjects = db.subjects.get_all()
        for sub in subjects:
            logger.info("Indexing subject: %s", sub.name)
            index_subject(sub.name, model_manager.embedder, db, lambda msg: print(f"  {msg}"))
        return

    if args.gui:
        logger.info("Launching GUI...")
        launch_gui(db, model_manager)


if __name__ == "__main__":
    main()
