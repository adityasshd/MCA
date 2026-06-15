"""
indexer — RAG Document Indexer
===============================
Extracts text and images from chapter PDFs, chunks the text, generates
embeddings, and stores everything in MongoDB Atlas for vector search.

Pipeline:
    PDF → text extraction → chunking → embedding → MongoDB chunks collection
    PDF → image extraction → data/processed/images/{subject}/{unit}/
"""

from __future__ import annotations

import logging
import re
from pathlib import Path

import fitz  # PyMuPDF

from src.core.config import CHAPTERS_DIR, IMAGES_DIR, get_config
from src.core.database import DatabaseManager
from src.core.models import BaseEmbedder, ModelManager
from src.core.schemas import Subject, TextChunk, UnitInfo

logger = logging.getLogger(__name__)


# ── Text Extraction ──────────────────────────────────────────────────────


def extract_text_from_pdf(pdf_path: Path) -> tuple[str, list[tuple[int, int]]]:
    """
    Extract all text from a PDF file.

    Returns:
        (full_text, page_ranges) — the full concatenated text and a list
        of (start_char, end_char) offsets marking where each page begins.
    """
    doc = fitz.open(str(pdf_path))
    full_text = ""
    page_ranges: list[tuple[int, int]] = []

    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text()
        start = len(full_text)
        full_text += text
        page_ranges.append((start, len(full_text)))

    doc.close()
    return full_text, page_ranges


def extract_images_from_pdf(pdf_path: Path, output_dir: Path) -> list[str]:
    """
    Extract embedded images from a PDF and save them to output_dir.

    Returns:
        List of saved image filenames.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    doc = fitz.open(str(pdf_path))
    saved_images: list[str] = []
    seen_xrefs = set()

    for page_num in range(len(doc)):
        page = doc[page_num]
        image_list = page.get_images(full=True)

        for img_idx, img_info in enumerate(image_list):
            xref = img_info[0]
            if xref in seen_xrefs:
                continue
            
            try:
                base_image = doc.extract_image(xref)
                # Ignore small icons, bullets, and watermarks
                if base_image["width"] < 100 or base_image["height"] < 100:
                    continue
                
                seen_xrefs.add(xref)
                image_bytes = base_image["image"]
                image_ext = base_image["ext"]
                filename = f"page_{page_num + 1:03d}_img_{xref}.{image_ext}"
                filepath = output_dir / filename

                with open(filepath, "wb") as f:
                    f.write(image_bytes)
                saved_images.append(filename)
            except Exception as e:
                logger.debug(
                    "Skipping image xref=%d on page %d: %s", xref, page_num, e
                )

    doc.close()
    return saved_images


# ── Chunking ─────────────────────────────────────────────────────────────


def chunk_text(
    text: str,
    page_ranges: list[tuple[int, int]],
    chunk_size: int = 800,
    overlap: int = 80,
) -> list[dict]:
    """
    Split text into overlapping chunks, respecting paragraph boundaries
    where possible.

    Returns:
        List of dicts with keys: text, chunk_index, page_range
    """
    if not text.strip():
        return []

    # Split into paragraphs first
    paragraphs = re.split(r"\n\s*\n", text)
    paragraphs = [p.strip() for p in paragraphs if p.strip()]

    chunks: list[dict] = []
    current_chunk = ""
    current_start = 0
    chunk_index = 0

    for paragraph in paragraphs:
        # If adding this paragraph would exceed chunk_size, flush
        if current_chunk and len(current_chunk) + len(paragraph) + 1 > chunk_size:
            # Find page range for this chunk
            page_range = _find_page_range(current_start, current_start + len(current_chunk), page_ranges)
            chunks.append({
                "text": current_chunk.strip(),
                "chunk_index": chunk_index,
                "page_range": page_range,
            })
            chunk_index += 1

            # Keep overlap from end of current chunk
            overlap_text = current_chunk[-overlap:] if overlap > 0 else ""
            current_start = current_start + len(current_chunk) - len(overlap_text)
            current_chunk = overlap_text

        if current_chunk:
            current_chunk += "\n\n" + paragraph
        else:
            current_chunk = paragraph

    # Flush remaining
    if current_chunk.strip():
        page_range = _find_page_range(current_start, current_start + len(current_chunk), page_ranges)
        chunks.append({
            "text": current_chunk.strip(),
            "chunk_index": chunk_index,
            "page_range": page_range,
        })

    return chunks


def _find_page_range(
    start_char: int, end_char: int, page_ranges: list[tuple[int, int]]
) -> str:
    """Find which pages a character range spans."""
    start_page = 0
    end_page = 0
    for i, (ps, pe) in enumerate(page_ranges):
        if ps <= start_char < pe:
            start_page = i + 1
        if ps < end_char <= pe:
            end_page = i + 1
    if start_page == 0:
        start_page = 1
    if end_page == 0:
        end_page = len(page_ranges)
    if start_page == end_page:
        return str(start_page)
    return f"{start_page}-{end_page}"


# ── Embedding & Storage ──────────────────────────────────────────────────


def embed_and_store_chunks(
    chunk_dicts: list[dict],
    subject: str,
    unit: str,
    embedder: BaseEmbedder,
    db: DatabaseManager,
    batch_size: int = 32,
) -> int:
    """
    Generate embeddings for chunks and store them in MongoDB.

    Returns the number of chunks stored.
    """
    total_stored = 0

    for i in range(0, len(chunk_dicts), batch_size):
        batch = chunk_dicts[i : i + batch_size]
        texts = [c["text"] for c in batch]

        # Generate embeddings
        embeddings = embedder.embed(texts)

        # Create TextChunk objects
        chunks = [
            TextChunk(
                subject=subject,
                unit=unit,
                chunk_index=c["chunk_index"],
                text=c["text"],
                page_range=c["page_range"],
                embedding=emb,
                embedding_model=embedder.model_name,
            )
            for c, emb in zip(batch, embeddings)
        ]

        stored = db.chunks.save_chunks(chunks)
        total_stored += stored

    return total_stored


# ── High-Level Indexing Functions ─────────────────────────────────────────


def index_unit(
    subject_name: str,
    unit_info: UnitInfo,
    embedder: BaseEmbedder,
    db: DatabaseManager,
    progress_callback=None,
) -> int:
    """
    Index a single unit: extract text, chunk, embed, store.

    Returns the number of chunks created.
    """
    pdf_path = Path(unit_info.file_path)
    if not pdf_path.exists():
        logger.warning("PDF not found: %s", pdf_path)
        return 0

    if progress_callback:
        progress_callback(f"Extracting text from {unit_info.name}...")

    # Extract text
    text, page_ranges = extract_text_from_pdf(pdf_path)
    if not text.strip():
        logger.warning("No text extracted from %s", pdf_path)
        return 0

    # Extract images
    image_dir = IMAGES_DIR / subject_name / unit_info.name
    extract_images_from_pdf(pdf_path, image_dir)

    if progress_callback:
        progress_callback(f"Chunking {unit_info.name}...")

    # Chunk text
    config = get_config()
    chunks = chunk_text(text, page_ranges, config.CHUNK_SIZE, config.chunk_overlap)
    if not chunks:
        return 0

    if progress_callback:
        progress_callback(f"Embedding {len(chunks)} chunks from {unit_info.name}...")

    # Delete existing chunks for this unit (re-index)
    db.chunks.delete_by_unit(subject_name, unit_info.name)

    # Embed and store
    stored = embed_and_store_chunks(chunks, subject_name, unit_info.name, embedder, db)

    return stored


def index_subject(
    subject_name: str,
    embedder: BaseEmbedder,
    db: DatabaseManager,
    progress_callback=None,
    force_reindex: bool = False,
) -> int:
    """
    Index all units for a subject.

    Returns the total number of chunks created.
    """
    subject = db.subjects.get_by_name(subject_name)
    if not subject:
        logger.warning("Subject '%s' not found in database.", subject_name)
        return 0

    total_chunks = 0
    for i, unit in enumerate(subject.units):
        if unit.indexed and not force_reindex:
            logger.info("Skipping already-indexed unit: %s", unit.name)
            continue

        if progress_callback:
            progress_callback(
                f"Indexing {unit.name} ({i + 1}/{len(subject.units)})"
            )

        count = index_unit(
            subject_name, unit, embedder, db, progress_callback
        )
        total_chunks += count

        # Update unit status
        unit.indexed = True
        unit.chunk_count = count

    # Save updated subject
    db.subjects.update(subject)

    return total_chunks


def scan_and_register_subjects(db: DatabaseManager) -> list[Subject]:
    """
    Scan the chapters directory and register all subjects in the database.
    Does not perform indexing — just creates Subject records.
    """
    registered: list[Subject] = []

    if not CHAPTERS_DIR.exists():
        logger.warning("Chapters directory not found: %s", CHAPTERS_DIR)
        return registered

    for subject_dir in sorted(CHAPTERS_DIR.iterdir()):
        if not subject_dir.is_dir():
            continue

        subject_name = subject_dir.name

        # Check if already registered
        existing = db.subjects.get_by_name(subject_name)
        if existing:
            registered.append(existing)
            continue

        # Discover unit PDFs
        units: list[UnitInfo] = []
        for pdf_file in sorted(subject_dir.glob("*.pdf")):
            units.append(
                UnitInfo(
                    name=pdf_file.stem,
                    file_path=str(pdf_file),
                    indexed=False,
                    chunk_count=0,
                )
            )

        subject = Subject(
            name=subject_name,
            folder_path=str(subject_dir),
            units=units,
        )
        subject_id = db.subjects.save(subject)
        subject.id = subject_id
        registered.append(subject)
        logger.info(
            "Registered subject '%s' with %d units.", subject_name, len(units)
        )

    return registered
