"""
main.py
-------
FastAPI application entry point.

Startup sequence:
  1. Setup NeonDB (create tables / indexes if missing)
  2. Ingest all PDFs from resources/ into NeonDB (skips already-indexed files)
  3. Mount API routes
  4. Serve

Run locally:
    uvicorn main:app --reload --host 0.0.0.0 --port 8000

Deploy on Render:
    Start Command: uvicorn main:app --host 0.0.0.0 --port $PORT
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from database.neon_db import setup_database
from ingestion.pdf_loader import ingest_all_pdfs
from api.routes import router


# ── Lifespan (startup / shutdown) ──────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Run DB setup and PDF ingestion on startup."""
    import os
    print("\n🚀 CBSE Smart Tutor API — Starting up...")
    setup_database()
    if os.getenv("SKIP_INGESTION") != "true":
        ingest_all_pdfs()
    else:
        print("⏭️  Skipping PDF ingestion (SKIP_INGESTION=true) — Using existing NeonDB data.")
    print("🎓 API is ready to serve students!\n")
    yield
    print("👋 Server shutting down.")


# ── App Instance ───────────────────────────────────────────────────────────────

app = FastAPI(
    title="CBSE 10th Smart Tutor API",
    description="RAG-powered Q&A for CBSE Class 10 board exam preparation",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Allow Streamlit frontend (and any origin during dev)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount all routes
app.include_router(router)
