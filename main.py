"""
MCA Study Tools
===============
CLI entry point for MCA course utilities.

Usage:
    python -m main --split                          # split all books
    python -m main --split "SOFTWARE_ENGINEERING"   # split one book (partial match)
    python -m main --split "C_PROGRAMMING" "LINUX"  # split multiple books
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
RAW_DIR = PROJECT_ROOT / "data" / "raw"
CHAPTERS_DIR = PROJECT_ROOT / "data" / "processed" / "chapters"


def cmd_split(args: argparse.Namespace) -> None:
    """Handle the --split command."""
    from splitter import split_books

    names = args.books if args.books else None
    split_books(RAW_DIR, CHAPTERS_DIR, names)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="main",
        description="MCA Study Tools — course utility scripts.",
    )

    parser.add_argument(
        "--split",
        dest="books",
        nargs="*",
        default=None,
        metavar="BOOK",
        help=(
            "Split PDF books into individual chapter PDFs. "
            "Pass book names (partial match) to split specific books, "
            "or omit to split all."
        ),
    )

    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.books is not None:
        cmd_split(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
