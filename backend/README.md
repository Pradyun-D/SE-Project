# Regulatory Requirements Backend

This local FastAPI service turns a scenario into a requirements specification and SDLC recommendation. Gemini provides generation and embeddings. Qdrant is the only dense vector store; BM25 remains the sparse retrieval component.

## Setup

```powershell
cd backend
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Create `backend/.env` and add the Gemini key:

```text
RAG_GEMINI_API_KEY=your-key
RAG_GEMINI_GENERATION_MODEL=gemini-3.5-flash-lite
RAG_GEMINI_EMBEDDING_MODEL=gemini-embedding-001
RAG_GEMINI_EMBEDDING_DIMENSIONS=1024
```

The local Qdrant database is stored in `backend/data/qdrant` by default. Set `RAG_VECTOR_DB_URL` and `RAG_VECTOR_DB_API_KEY` to use a Qdrant server instead.

## Run

```powershell
uvicorn api.main:app --reload
```

Open the standalone frontend from a second terminal at the repository root:

```powershell
cd ..
python -m http.server 5500 -d frontend
```

Then open `http://127.0.0.1:5500`. Keep the API running on port `8000`.

With the API running in another terminal, run the full integration test from `backend`:

```powershell
python test_full_pipeline_stream.py
```

The test checks health, loads or builds the cached PDF/Qdrant index, runs the Gemini workflow with RAG, and verifies that requirements, an SDLC recommendation, and saved stream/response files are returned. Embeddings are generated only when the cache is missing, documents changed, or the embedding model changed.

Ingest the PDFs in `backend/docs` before the first RAG request:

```powershell
Invoke-RestMethod -Method Post http://127.0.0.1:8000/ingest
```

Generate an SRS with `POST /generate`:

```json
{
  "minimal_requirement": "Users can link savings accounts and fetch statements using PAN and DOB.",
  "scale": "Medium",
  "use_rag": true,
  "human_approved": true
}
```

## Workflow

The workflow runs five stages: requirement extraction, quality review, SDLC selection, human-approval state, and final SRS assembly. The requirement agent invokes `RegulatoryContextTool` when RAG is enabled. That tool performs BM25 and Qdrant retrieval, fuses the candidates, reranks them with Gemini embedding similarity, and returns source metadata with the context.

Requirement extraction covers functional and non-functional dimensions, priorities, regulations, organisational policies, risk controls, legacy constraints, evidence, citations, acceptance criteria, and human approval checkpoints. The quality, SDLC, and documentation agents then carry those results through the final response.

`POST /ingest` reuses cached chunks when the PDF manifest is unchanged. Use `POST /ingest?force=true` to rebuild both the chunks and the Qdrant collection.

## Configuration

All settings use the `RAG_` environment prefix. Important values include:

- `RAG_GEMINI_API_KEY`
- `RAG_GEMINI_GENERATION_MODEL`
- `RAG_GEMINI_EMBEDDING_MODEL`
- `RAG_VECTOR_DB_PATH` or `RAG_VECTOR_DB_URL`
- `RAG_VECTOR_DB_COLLECTION`
- `RAG_TOP_K_FUSION` and `RAG_FINAL_K`

The API preserves the existing logging, streaming capture, and numbered response files under `backend/stream` and `backend/responses`.
