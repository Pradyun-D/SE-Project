# Regulatory Requirements Backend

This service turns a minimal requirement into an SRS/PRD using PDF context, local BM25/FAISS indexes, and model APIs hosted on Kaggle.

PDF files belong in `backend/docs`. On startup, the service loads the persistent chunks and FAISS index from `backend/data` when the PDF files are unchanged. It rebuilds the cache only when it is missing or a PDF has changed.

## Kaggle model server

Run `kaggle_server.py` in Kaggle after adding `NGROK_AUTHTOKEN` as a Kaggle Secret. Install its GPU dependencies first:

```python
!pip install fastapi uvicorn pyngrok nest-asyncio transformers bitsandbytes torch accelerate sentence-transformers -q
```

The script loads Qwen, BGE-M3, and BGE-Reranker-v2-M3 on the Kaggle GPU and exposes `/health`, `/embed`, `/rerank`, and `/generate`. Copy the printed `KAGGLE_URL` into local `.env` as `RAG_KAGGLE_URL`.

It also exposes `POST /generate/stream`, which returns generated text chunks as they are produced. The local `RemoteModelClient.generate_stream()` method consumes this endpoint with `requests` streaming enabled.

Restart the Kaggle server whenever this API contract changes. A generation-only Kaggle server will return `404` for `/embed` during local startup.

## Run

```powershell
pip install -r requirements.txt
uvicorn api.main:app --reload
```

Call `POST /ingest` once after starting the service, then call `POST /generate` with:

```json

The single local response endpoint is `POST /generate`. It runs retrieval, requirement extraction, quality review, SDLC selection, approval state, and SRS assembly. The response includes the generated SRS, extracted requirements, quality results, SDLC recommendation, source metadata, and saved stream/response file paths.

## End-to-end test

Start the local API, confirm the Kaggle URL is set in `.env`, then run:

```powershell
python test_e2e.py
```

The script checks the API, ingests the PDFs, calls the LangGraph workflow, and prints the generated SRS.

To run the complete RAG and LangGraph pipeline:

```powershell
python test_full_pipeline.py
```

This uses the cache-aware `/ingest` endpoint, retrieves regulatory context, runs the requirement, quality, SDLC, and documentation stages, then saves the cleaned SRS in `backend/responses`.

The full pipeline writes model tokens to a file instead of the terminal:

```powershell
python test_full_pipeline_stream.py
```

The live model output is written to the next numbered file in `backend/stream` while the workflow runs. The cleaned final SRS is written to the next numbered file in `backend/responses`.

To test token-by-token output directly from Kaggle:

```powershell
python test_stream.py
```

The stream is printed live, then `<think>...</think>` sections are removed and the cleaned response is saved as the next numbered file in `backend/responses`.

`POST /ingest` loads the existing cache or rebuilds it when documents changed. Use `POST /ingest?force=true` when you intentionally want to rebuild the cache.
{
  "minimal_requirement": "Users can link savings accounts and fetch statements using PAN and DOB.",
  "scale": "Medium",
  "use_rag": true
}
```

Set values in `.env` using the `RAG_` prefix. The model client sends generation, embedding, and reranking requests to Kaggle. The local machine only needs the API, lightweight `pypdf` parsing, BM25, and FAISS dependencies.