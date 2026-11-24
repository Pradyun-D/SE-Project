# Agentic Software Requirements and SDLC System

## Purpose

The application accepts a software scenario and produces a requirements specification plus a suitable SDLC recommendation. It is implemented as a local FastAPI and LangGraph backend.

## Current architecture

- `GeminiModelClient` calls Gemini REST APIs for generation, streaming generation, and embeddings.
- Qdrant is the only dense vector database. It runs locally under `backend/data/qdrant` by default or connects to a configured Qdrant server.
- BM25 provides sparse retrieval. The retrieval tool fuses sparse and dense rankings and uses Gemini embedding similarity to rerank candidates.
- `RegulatoryContextTool` is invoked by the requirement extraction agent when RAG is enabled. Retrieval is no longer a separate graph node or manually assembled input path.
- PDF chunks and their document manifest are cached under `backend/data`; the Qdrant collection stores the dense index.
- Existing logging, streaming capture, and numbered response files remain enabled.

## Workflow and feature coverage

The graph runs these stages:

1. Requirement extraction by the first agent, using the regulatory context tool when requested.
2. Requirement quality review by the second analysis agent.
3. SDLC selection based on requirement and organisation-scale factors.
4. Human approval state handling.
5. Final SRS/PRD documentation.

Extracted requirements support:

- Functional and non-functional dimensions including business, technical, security, privacy, compliance, performance, availability, auditability, and operations.
- Priorities, regulations, organisational policies, risk controls, and legacy-system constraints.
- Source evidence, citations, human approval checkpoints, and Given/When/Then acceptance criteria.
- Quality findings, derived SDLC factors, SDLC recommendation, and final documentation.

This covers the two core problem-statement responsibilities: identifying software requirements and selecting a suitable SDLC. The surrounding quality, approval, regulatory-evidence, and documentation features are preserved in the same workflow.

## Repository layout

```text
backend/
  agents/             Requirement, quality, SDLC, and documentation agents
  api/main.py         FastAPI endpoints and startup ingestion
  data/qdrant/        Persistent local Qdrant collection
  docs/               Source PDF documents
  graph/workflow.py   LangGraph workflow
  model_client.py     Gemini generation and embedding client
  rag/                Parsing, caching, Qdrant retrieval, and context tool
  stream/             Streaming capture and response persistence
```

## Configuration

Settings use the `RAG_` environment prefix. At minimum:

```text
RAG_GEMINI_API_KEY=your-key
RAG_GEMINI_GENERATION_MODEL=gemini-2.5-flash
RAG_GEMINI_EMBEDDING_MODEL=text-embedding-004
```

Use `RAG_VECTOR_DB_PATH` for local Qdrant or `RAG_VECTOR_DB_URL` with `RAG_VECTOR_DB_API_KEY` for a Qdrant server. `POST /ingest` loads the cache when the PDF manifest is current; `POST /ingest?force=true` rebuilds it.

## Running

```powershell
cd backend
pip install -r requirements.txt
uvicorn api.main:app --reload
```

The API exposes `/health`, `/ingest`, and `/generate`. See [backend/README.md](backend/README.md) for the request example and operational details.

## Removed legacy components

The project no longer depends on a Kaggle model server, ngrok, FAISS, or the deleted `kaggle_server.py`. Gemini and Qdrant are configured locally through environment settings.
