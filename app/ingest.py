"""
Ingestion pipeline for the AWS Well-Architected RAG mini-app.

Flow:
  PDF file -> extract text (pdfplumber) -> chunk with overlap
           -> embed locally (sentence-transformers) -> store in ChromaDB

Usage:
  python -m app.ingest data/raw/security-pillar.pdf --pillar "Security"
  python -m app.ingest data/raw/cost-optimization-pillar.pdf --pillar "Cost Optimization"
"""

import argparse
from pathlib import Path

import chromadb
import pdfplumber
from sentence_transformers import SentenceTransformer

from app.chunking import build_chunks_with_metadata

# ---- Config ----
CHROMA_PATH = "data/chroma_db"
COLLECTION_NAME = "well_architected"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # local, free, 384-dim


def extract_text_by_page(pdf_path: str) -> list[tuple[int, str]]:
    """Return a list of (page_number, page_text) tuples."""
    pages = []
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages, start=1):
            text = page.extract_text() or ""
            if text.strip():
                pages.append((i, text))
    return pages


def ingest_pdf(pdf_path: str, pillar: str) -> None:
    print(f"[1/4] Extracting text from {pdf_path} ...")
    pages = extract_text_by_page(pdf_path)
    print(f"      -> {len(pages)} pages with text")

    print("[2/4] Chunking ...")
    records = build_chunks_with_metadata(pages, pillar)
    print(f"      -> {len(records)} chunks")

    print(f"[3/4] Loading local embedding model ({EMBEDDING_MODEL}) ...")
    model = SentenceTransformer(EMBEDDING_MODEL)
    texts = [r["text"] for r in records]
    embeddings = model.encode(texts, show_progress_bar=True, batch_size=32).tolist()

    print("[4/4] Storing in ChromaDB ...")
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    collection = client.get_or_create_collection(COLLECTION_NAME)

    collection.add(
        ids=[r["id"] for r in records],
        documents=texts,
        embeddings=embeddings,
        metadatas=[{"pillar": r["pillar"], "page": r["page"], "source": Path(pdf_path).name} for r in records],
    )

    print(f"Done. Collection '{COLLECTION_NAME}' now has {collection.count()} chunks total.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ingest an AWS Well-Architected PDF into ChromaDB")
    parser.add_argument("pdf_path", help="Path to the PDF file")
    parser.add_argument("--pillar", required=True, help="Pillar name, e.g. 'Security' or 'Cost Optimization'")
    args = parser.parse_args()

    ingest_pdf(args.pdf_path, args.pillar)
