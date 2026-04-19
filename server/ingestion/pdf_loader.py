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

from typing import Optional
from sentence_transformers import SentenceTransformer

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
