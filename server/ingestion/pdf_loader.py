"""
ingestion/pdf_loader.py
-----------------------
Handles:
  - Walking the resources/ folder
  - Extracting text from PDFs
  - Splitting into overlapping chunks
  - Embedding with SentenceTransformer
  - Storing into NeonDB (skips already-indexed files)
"""

from pathlib import Path
from typing import Optional
from PyPDF2 import PdfReader
from sentence_transformers import SentenceTransformer
from database.neon_db import source_already_indexed, insert_document_chunk

# All PDFs live inside server/resources/
RESOURCES_DIR = Path(__file__).parent.parent / "resources"

# Maps display subject name → subfolder names
SUBJECT_FOLDERS: dict = {
    "Mathematics": ["Maths Solution", "Maths Ncrt", "Maths Ncrt 2"],
    "Science":     ["Science Solution", "Science ncrt"],
    "English":     ["English Solution", "Englsih Ncrt"],
    "SST":         ["SST Solution", "sst ncrt"],
}

# Embedding model (384-dim — matches NeonDB vector(384))
_embed_model = None


def get_embed_model() -> SentenceTransformer:
    """Lazy-load the embedding model once."""
    global _embed_model
    if _embed_model is None:
        print("📦 Loading embedding model (all-MiniLM-L6-v2)…")
        _embed_model = SentenceTransformer("all-MiniLM-L6-v2")
        print("✅ Embedding model loaded.")
    return _embed_model


# ── Text Extraction ────────────────────────────────────────────────────────────

def extract_pdf_text(pdf_path: Path) -> str:
    """Extract raw text from a PDF file page by page."""
    try:
        reader = PdfReader(str(pdf_path))
        pages = []
        for page in reader.pages:
            text = page.extract_text()
            if text:
                pages.append(text)
        return "\n".join(pages)
    except Exception as e:
        print(f"  ⚠️  Could not read {pdf_path.name}: {e}")
        return ""


# ── Chunking ───────────────────────────────────────────────────────────────────

def split_into_chunks(text: str, chunk_size: int = 600, overlap: int = 100) -> list:
    """
    Split text into overlapping word-level chunks.
    chunk_size  — words per chunk
    overlap     — words shared between consecutive chunks
    """
    words = text.split()
    chunks = []
    i = 0
    while i < len(words):
        chunk = " ".join(words[i : i + chunk_size])
        if len(chunk.strip()) > 60:          # discard tiny fragments
            chunks.append(chunk)
        i += chunk_size - overlap
    return chunks


# ── Main Ingestion ─────────────────────────────────────────────────────────────

def ingest_all_pdfs():
    """
    Walk every subject folder, extract text, chunk it, embed it,
    and store into NeonDB. Skips files that are already indexed.
    """
    model = get_embed_model()
    total_new = 0

    for subject, folder_names in SUBJECT_FOLDERS.items():
        for folder_name in folder_names:
            folder = RESOURCES_DIR / folder_name
            if not folder.exists():
                print(f"  📁 Folder not found, skipping: {folder_name}")
                continue

            # Memory Optimization: Only use 1 PDF per folder for deployment
            for pdf_path in sorted(folder.glob("**/*.pdf"))[:1]:
                source_key = f"{subject}::{pdf_path.name}"

                if source_already_indexed(source_key):
                    print(f"  ⏭️  Already indexed: {pdf_path.name}")
                    continue

                print(f"  📄 Indexing [{subject}]: {pdf_path.name}")
                text = extract_pdf_text(pdf_path)
                if not text:
                    continue

                chunks = split_into_chunks(text)
                if not chunks:
                    continue

                # Batch embed all chunks at once for speed
                embeddings = model.encode(chunks, batch_size=32, show_progress_bar=False)

                for chunk, emb in zip(chunks, embeddings):
                    insert_document_chunk(subject, source_key, chunk, emb.tolist())
                    total_new += 1

    print(f"\n✅ Ingestion complete — {total_new} new chunks stored in NeonDB.")
    return total_new
