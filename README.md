# notes-rag: AWS Well-Architected Q&A

![CI](https://github.com/jMiral09/notes-rag/actions/workflows/ci.yml/badge.svg)

A retrieval-augmented generation (RAG) app that answers questions about the AWS
Well-Architected Framework and cites the pillar and page each answer came from.

## Architecture
PDF -> text extraction -> chunking -> local embeddings -> ChromaDB
Question -> FastAPI -> retrieve top-k chunks -> Claude -> answer with citations

## Stack
FastAPI, ChromaDB, sentence-transformers (local embeddings), Claude API, pytest, GitHub Actions

## Setup
```bash
python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt -r requirements-dev.txt
export ANTHROPIC_API_KEY=...                        # never commit this
```

## Ingest a PDF
```bash
python -m app.ingest data/raw/security-pillar.pdf --pillar "Security"
```

## Run tests
```bash
pytest
```

## Design decisions
- _TODO: why local embeddings, why ChromaDB, why this chunk size_

## Status
- [x] Ingestion pipeline
- [ ] Retrieval + generation
- [ ] FastAPI endpoints
- [ ] Evaluation harness
