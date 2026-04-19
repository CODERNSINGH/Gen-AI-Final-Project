"""
api/routes.py
-------------
All FastAPI route definitions.
Keeps main.py clean — only imports and mounts these routes.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from ingestion.pdf_loader import get_embed_model, SUBJECT_FOLDERS
from database.neon_db import search_similar_chunks, get_indexed_stats
from agent.groq_agent import generate_answer

router = APIRouter()


# ── Request Schema ─────────────────────────────────────────────────────────────

class QuestionRequest(BaseModel):
    question: str
    subject:  Optional[str] = None   # None = search across all subjects


# ── Health ─────────────────────────────────────────────────────────────────────

@router.get("/", tags=["Health"])
def root():
    return {
        "status":  "ok",
        "message": "CBSE 10th Smart Tutor API is running 🎓",
        "version": "1.0.0",
    }


@router.get("/health", tags=["Health"])
def health():
    return {"status": "healthy"}


# ── Metadata ───────────────────────────────────────────────────────────────────

@router.get("/subjects", tags=["Metadata"])
def list_subjects():
    """Return all available subjects."""
    return {"subjects": list(SUBJECT_FOLDERS.keys())}


@router.get("/stats", tags=["Metadata"])
def get_stats():
    """Return chunk count per subject — shown in UI sidebar."""
    stats = get_indexed_stats()
    return {"stats": stats}


# ── Core RAG Endpoint ──────────────────────────────────────────────────────────

@router.post("/ask", tags=["RAG"])
def ask_question(req: QuestionRequest):
    """
    Main RAG endpoint:
    1. Embed the question
    2. Retrieve top-k similar chunks from NeonDB
    3. Pass context to Groq agent
    4. Return formatted board-exam answer
    """
    question = req.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    # Step 1: Embed the query
    model   = get_embed_model()
    q_emb   = model.encode([question])[0].tolist()

    # Step 2: Vector similarity search in NeonDB
    chunks = search_similar_chunks(q_emb, req.subject, top_k=6)
    if not chunks:
        raise HTTPException(
            status_code=404,
            detail="No relevant content found. The knowledge base may still be indexing — try again in a moment."
        )

    # Step 3: Generate answer with Groq
    result = generate_answer(question, chunks, req.subject or "")

    return result
