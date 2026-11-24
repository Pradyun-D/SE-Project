from contextlib import asynccontextmanager
from concurrent.futures import ThreadPoolExecutor
import logging
from threading import Lock
from uuid import uuid4
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from config import get_settings
from model_client import GeminiModelClient
from rag.cache import cache_is_current, document_signature
from rag.ingest import parse_pdf_directory
from rag.pipeline import RegulatoryRAGPipeline
from graph.workflow import FinTechRequirementsWorkflow
from schemas import GenerateRequest, GenerateResponse, IngestResponse
from stream import FileStreamingGenerator


logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s - %(message)s")
logger = logging.getLogger(__name__)

settings = get_settings()
model_client = GeminiModelClient(
    settings.gemini_api_key,
    settings.gemini_generation_model,
    settings.gemini_embedding_model,
    settings.gemini_embedding_dimensions,
    settings.model_timeout_seconds,
    settings.model_retry_count,
)
pipeline = RegulatoryRAGPipeline(
    model_client,
    settings.top_k_fusion,
    settings.final_k,
    settings.embedding_batch_size,
    settings.vector_db_path,
    settings.vector_db_url,
    settings.vector_db_api_key,
    settings.vector_db_collection,
)
workflow = FinTechRequirementsWorkflow(pipeline, model_client.generate)
generation_jobs: dict[str, dict] = {}
generation_jobs_lock = Lock()
generation_executor = ThreadPoolExecutor(max_workers=2)


def initialize_pipeline(force: bool = False) -> tuple[int, int]:
    if not force and cache_is_current(
        settings.cache_dir,
        settings.data_dir,
        settings.gemini_embedding_model,
        settings.gemini_embedding_dimensions,
    ):
        logger.info("Loading the persistent document cache")
        try:
            pipeline.load(settings.cache_dir)
            return len(document_signature(settings.data_dir)), len(pipeline.store.chunks)
        except FileNotFoundError as error:
            logger.warning(
                "Persistent cache exists but its vector backend is unavailable; rebuilding the index: %s",
                error,
            )

    logger.info("Cache missing, stale, or force requested; rebuilding document index")
    chunks, document_count = parse_pdf_directory(settings.data_dir)
    pipeline.ingest(chunks)
    pipeline.save(
        settings.cache_dir,
        settings.data_dir,
        settings.gemini_embedding_model,
        settings.gemini_embedding_dimensions,
    )
    logger.info("Startup step 2/2: Document cache is ready")
    return document_count, len(chunks)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    logger.info("Starting Regulatory Requirements API")
    initialize_pipeline()
    logger.info("API startup complete")
    yield


app = FastAPI(title="Regulatory Requirements API", version="1.0.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/responses/latest")
def latest_response() -> dict[str, str]:
    response_dir = Path(settings.response_dir)
    response_files = sorted(response_dir.glob("response_*.md"))
    if not response_files:
        raise HTTPException(status_code=404, detail="No saved response is available")
    response_file = response_files[-1]
    return {
        "filename": response_file.name,
        "response": response_file.read_text(encoding="utf-8"),
    }


@app.post("/ingest", response_model=IngestResponse)
def ingest(force: bool = Query(default=False)) -> IngestResponse:
    try:
        document_count, chunk_count = initialize_pipeline(force=force)
        return IngestResponse(documents=document_count, chunks=chunk_count)
    except (FileNotFoundError, ValueError) as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(status_code=500, detail="Document ingestion failed") from error


@app.post("/generate", response_model=GenerateResponse)
def generate(request: GenerateRequest) -> GenerateResponse:
    return run_generation(request)


@app.post("/generate/async")
def generate_async(request: GenerateRequest) -> dict[str, str]:
    if request.use_rag and not pipeline.store.chunks:
        raise HTTPException(status_code=409, detail="Ingest documents before using RAG")
    job_id = uuid4().hex
    with generation_jobs_lock:
        generation_jobs[job_id] = {"status": "queued", "step": "requirements", "message": "Waiting to start"}
    generation_executor.submit(run_generation_job, job_id, request)
    return {"job_id": job_id}


@app.get("/generate/status/{job_id}")
def generation_status(job_id: str) -> dict:
    with generation_jobs_lock:
        job = generation_jobs.get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Generation job not found")
    return job


def run_generation_job(job_id: str, request: GenerateRequest) -> None:
    def progress(step: str, message: str) -> None:
        with generation_jobs_lock:
            generation_jobs[job_id].update({"status": "running", "step": step, "message": message})

    try:
        result = run_generation(request, progress)
        with generation_jobs_lock:
            generation_jobs[job_id].update({"status": "completed", "step": "complete", "message": "Analysis complete", "result": result.model_dump()})
    except Exception as error:
        logger.exception("Async generation failed")
        with generation_jobs_lock:
            generation_jobs[job_id].update({"status": "failed", "message": str(error)})


def run_generation(request: GenerateRequest, progress=None) -> GenerateResponse:
    if request.use_rag and not pipeline.store.chunks:
        raise HTTPException(status_code=409, detail="Ingest documents before using RAG")
    capture = FileStreamingGenerator(settings.stream_dir, settings.response_dir)
    streamed_workflow = FinTechRequirementsWorkflow(pipeline, capture, progress)
    try:
        result = streamed_workflow.app.invoke(
            {
                "user_query": request.minimal_requirement,
                "organization_scale": request.scale,
                "use_rag": request.use_rag,
                "human_approved": request.human_approved,
                "generation_options": {
                    "max_new_tokens": request.max_new_tokens,
                    "temperature": request.temperature,
                    "top_p": request.top_p,
                },
            }
        )
        sources = [item["meta"] for item in result.get("retrieved_context", [])]
        response = result.get("final_srs_markdown", "")
        response_file = capture.save_response(response)
        return GenerateResponse(
            response=response,
            sources=sources,
            extracted_requirements=result.get("extracted_requirements", []),
            quality_check=result.get("quality_check", {}),
            sdlc_factors=result.get("sdlc_factors", {}),
            sdlc_recommendation=result.get("sdlc_recommendation", {}),
            human_approved=result.get("human_approved", False),
            stream_file=str(capture.path),
            response_file=str(response_file),
        )
    except Exception as error:
        logger.exception("Full pipeline generation failed")
        raise HTTPException(status_code=502, detail="Model generation failed") from error
    finally:
        capture.close()
