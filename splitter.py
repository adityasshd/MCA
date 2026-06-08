"""
splitter — PDF Book Chapter Splitter
=====================================
Splits PDF textbooks into individual unit/chapter PDFs.

Strategy:
  1. If the PDF has a Table of Contents (bookmarks), use the top-level (L1)
     entries to identify unit boundaries.  The real unit title is extracted
     from the first page's text for clean file naming.
  2. If no TOC is found, fall back to scanning page text for headings that
     match common patterns like "Unit XX: Title" or "Chapter XX: Title".
  3. Each unit is saved as a separate PDF inside a subfolder named after the
     book (e.g., data/processed/chapters/SOFTWARE_ENGINEERING_PRACTICES/Unit_01_Introduction_to_Software_Engineering.pdf).
"""

from __future__ import annotations

import re
from pathlib import Path

import fitz  # PyMuPDF


# ── Configuration ────────────────────────────────────────────────────────────

# Regex patterns used for the text-based fallback chapter detection.
# Each pattern is tried in order; the first match wins.
HEADING_PATTERNS: list[re.Pattern[str]] = [
    re.compile(
        r"^Unit\s+(\d+)\s*[:\-–—]\s*(.+)",
        re.IGNORECASE,
    ),
    re.compile(
        r"^Chapter\s+(\d+)\s*[:\-–—]\s*(.+)",
        re.IGNORECASE,
    ),
    re.compile(
        r"^Module\s+(\d+)\s*[:\-–—]\s*(.+)",
        re.IGNORECASE,
    ),
]


# ── Helpers ──────────────────────────────────────────────────────────────────


def sanitize_filename(name: str) -> str:
    """Remove or replace characters that are unsafe for filenames."""
    name = re.sub(r"[<>:\"/\\|?*]", "", name)
    name = re.sub(r"\s+", "_", name.strip())
    # Collapse repeated underscores
    name = re.sub(r"_+", "_", name)
    return name.strip("_")


def derive_book_folder_name(pdf_filename: str) -> str:
    """
    Turn a raw PDF filename into a clean folder name.

    Examples:
        '7930_ECAP437_SOFTWARE_ENGINEERING_PRACTICES.pdf'
        -> 'SOFTWARE_ENGINEERING_PRACTICES'

        '8414_ECAP444_Object_ Oriented_Programming_Using_C Plus Plus.pdf'
        -> 'Object_Oriented_Programming_Using_C_Plus_Plus'
    """
    stem = Path(pdf_filename).stem  # drop .pdf

    # The naming convention is:  <number>_<code>_<TITLE>
    # Strip the leading numeric ID and course code.
    parts = stem.split("_", 2)
    if len(parts) >= 3 and parts[0].isdigit():
        title = parts[2]
    else:
        title = stem

    return sanitize_filename(title)


def extract_unit_title_from_page(page: fitz.Page) -> str | None:
    """
    Try to extract a human-readable unit/chapter title from the page text.

    Looks for lines like:
        Unit 01: Introduction to Software Engineering
        Unit 02: Software process models
    """
    text = page.get_text()
    for line in text.split("\n"):
        line = line.strip()
        for pattern in HEADING_PATTERNS:
            m = pattern.match(line)
            if m:
                return line
    return None


def parse_unit_number(title: str) -> str:
    """Extract a zero-padded unit/chapter number from a title string."""
    # Try specific patterns first: "U01", "Unit 01", "Chapter 3", etc.
    m = re.search(r"(?:^|\b)U(\d+)\b", title)
    if m:
        return m.group(1).zfill(2)
    m = re.search(r"(?:Unit|Chapter|Module)\s+(\d+)", title, re.IGNORECASE)
    if m:
        return m.group(1).zfill(2)
    # Fallback to first number found.
    m = re.search(r"(\d+)", title)
    if m:
        return m.group(1).zfill(2)
    return "00"


def build_chapter_filename(unit_num: str, raw_title: str | None) -> str:
    """
    Build a clean chapter PDF filename.

    Examples:
        Unit_01_Introduction_to_Software_Engineering.pdf
    """
    if raw_title:
        clean = sanitize_filename(raw_title)
        # Remove a leading redundant "Unit_XX_" if already in the title
        clean = re.sub(r"^(?:Unit|Chapter|Module)_?\d+_?[:\-–—_]*\s*", "", clean, flags=re.IGNORECASE)
        clean = sanitize_filename(clean)  # re-sanitize after regex
        if clean:
            return f"Unit_{unit_num}_{clean}.pdf"
    return f"Unit_{unit_num}.pdf"


# ── Core splitting logic ─────────────────────────────────────────────────────


def get_chapters_from_toc(doc: fitz.Document) -> list[tuple[str, int, int]]:
    """
    Extract chapter boundaries from the PDF's Table of Contents.

    Returns a list of (title, start_page_0idx, end_page_0idx) tuples.
    Only top-level (L1) bookmark entries are treated as chapter boundaries.
    """
    toc = doc.get_toc()
    if not toc:
        return []

    # Keep only level-1 entries as chapter boundaries.
    l1_entries = [(title, page) for level, title, page in toc if level == 1]
    if not l1_entries:
        return []

    chapters: list[tuple[str, int, int]] = []
    for i, (title, start_page) in enumerate(l1_entries):
        start_idx = start_page - 1  # convert to 0-indexed
        if i + 1 < len(l1_entries):
            end_idx = l1_entries[i + 1][1] - 2  # up to (but not including) next chapter
        else:
            end_idx = len(doc) - 1  # last chapter goes to end of document

        chapters.append((title, start_idx, end_idx))

    return chapters


def get_chapters_from_text(doc: fitz.Document) -> list[tuple[str, int, int]]:
    """
    Fallback: scan page text for chapter/unit heading patterns.

    We look for pages where a heading pattern appears near the TOP of the page,
    suggesting it's the start of a new unit rather than a passing reference.
    """
    chapter_starts: list[tuple[str, int]] = []  # (title, page_0idx)

    for page_idx in range(len(doc)):
        page = doc[page_idx]
        text = page.get_text()
        lines = [l.strip() for l in text.split("\n") if l.strip()]

        # Only inspect the first ~8 lines to avoid false positives from
        # tables of contents or inline references.
        for line in lines[:8]:
            for pattern in HEADING_PATTERNS:
                m = pattern.match(line)
                if m:
                    chapter_starts.append((line, page_idx))
                    break
            else:
                continue
            break  # Found a match on this page, move on.

    if not chapter_starts:
        return []

    chapters: list[tuple[str, int, int]] = []
    for i, (title, start_idx) in enumerate(chapter_starts):
        if i + 1 < len(chapter_starts):
            end_idx = chapter_starts[i + 1][1] - 1
        else:
            end_idx = len(doc) - 1
        chapters.append((title, start_idx, end_idx))

    return chapters


def split_pdf(pdf_path: Path, output_dir: Path) -> int:
    """
    Split a single PDF into chapter files inside *output_dir*.

    Returns the number of chapters extracted.
    """
    doc = fitz.open(str(pdf_path))

    # Try TOC first, fall back to text scanning.
    chapters = get_chapters_from_toc(doc)
    method = "TOC bookmarks"

    if not chapters:
        chapters = get_chapters_from_text(doc)
        method = "text pattern matching"

    if not chapters:
        print(f"  ⚠  No chapters detected (tried bookmarks and text patterns). Skipping.")
        doc.close()
        return 0

    print(f"  📖 Found {len(chapters)} unit(s) via {method}")

    output_dir.mkdir(parents=True, exist_ok=True)
    count = 0

    for toc_title, start_idx, end_idx in chapters:
        # Derive a nice title from the actual page content when possible.
        page_title = extract_unit_title_from_page(doc[start_idx])
        unit_num = parse_unit_number(toc_title)
        filename = build_chapter_filename(unit_num, page_title or toc_title)
        out_path = output_dir / filename

        # Create a new PDF with the selected page range.
        new_doc = fitz.open()
        new_doc.insert_pdf(doc, from_page=start_idx, to_page=end_idx)
        new_doc.save(str(out_path))
        new_doc.close()

        pages = end_idx - start_idx + 1
        print(f"    ✅ {filename}  ({pages} pages)")
        count += 1

    doc.close()
    return count


# ── Public API ───────────────────────────────────────────────────────────────


def find_pdf(input_dir: Path, name: str) -> Path | None:
    """
    Find a PDF in *input_dir* by partial name match (case-insensitive).

    Returns the first matching Path, or None.
    """
    name_lower = name.lower()
    for pdf in sorted(input_dir.glob("*.pdf")):
        if name_lower in pdf.name.lower() or name_lower in pdf.stem.lower():
            return pdf
    return None


def split_books(
    input_dir: Path,
    output_dir: Path,
    names: list[str] | None = None,
) -> None:
    """
    Split one or more PDF books into chapter PDFs.

    Args:
        input_dir:  Path to the directory containing source PDF files (e.g. data/raw).
        output_dir: Path where chapter sub-folders are created (e.g. data/processed/chapters).
        names:      Optional list of book names (partial match).
                    If None or empty, all PDFs in input_dir are processed.
    """
    if not input_dir.is_dir():
        print(f"❌ Input directory not found: {input_dir}")
        return

    # Resolve which PDFs to process.
    if names:
        pdf_files: list[Path] = []
        for name in names:
            match = find_pdf(input_dir, name)
            if match:
                pdf_files.append(match)
            else:
                print(f"⚠  No PDF matching '{name}' found in {input_dir}")
        if not pdf_files:
            return
    else:
        pdf_files = sorted(input_dir.glob("*.pdf"))

    if not pdf_files:
        print(f"❌ No PDF files found in {input_dir}")
        return

    print(f"📂 Source:  {input_dir}")
    print(f"📁 Output:  {output_dir}")
    print(f"   Processing {len(pdf_files)} PDF(s)\n")

    total_chapters = 0

    for pdf_path in pdf_files:
        book_folder_name = derive_book_folder_name(pdf_path.name)
        book_output_dir = output_dir / book_folder_name

        print(f"{'─' * 60}")
        print(f"📘 {pdf_path.name}")
        print(f"   → {book_output_dir}/")

        chapters = split_pdf(pdf_path, book_output_dir)
        total_chapters += chapters
        print()

    print(f"{'─' * 60}")
    print(f"🎉 Done! Extracted {total_chapters} chapter(s) from {len(pdf_files)} book(s).")
