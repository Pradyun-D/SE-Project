from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI, HTTPException, Query

from config import get_settings
from model_client import RemoteModelClient
from rag.cache import cache_is_current, document_signature
from rag.ingest import parse_pdf_directory
from rag.pipeline import RegulatoryRAGPipeline
from graph.workflow import FinTechRequirementsWorkflow
from schemas import GenerateRequest, GenerateResponse, IngestResponse
from stream import FileStreamingGenerator


logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s - %(message)s")
logger = logging.getLogger(__name__)

settings = get_settings()
model_client = RemoteModelClient(
    settings.kaggle_url,
    settings.model_timeout_seconds,
    settings.model_retry_count,
)
pipeline = RegulatoryRAGPipeline(
    model_client,
    settings.top_k_fusion,
    settings.final_k,
    settings.embedding_batch_size,
)
workflow = FinTechRequirementsWorkflow(pipeline, model_client.generate)


def initialize_pipeline(force: bool = False) -> tuple[int, int]:
    if not force and cache_is_current(settings.cache_dir, settings.data_dir):
        logger.info("Loading the persistent document cache")
        pipeline.load(settings.cache_dir)
        return len(document_signature(settings.data_dir)), len(pipeline.store.chunks)

    logger.info("Cache missing, stale, or force requested; rebuilding document index")
    chunks, document_count = parse_pdf_directory(settings.data_dir)
    pipeline.ingest(chunks)
    pipeline.save(settings.cache_dir, settings.data_dir)
    logger.info("Startup step 2/2: Document cache is ready")
    return document_count, len(chunks)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    logger.info("Starting Regulatory Requirements API")
    initialize_pipeline()
    logger.info("API startup complete")
    yield


app = FastAPI(title="Regulatory Requirements API", version="1.0.0", lifespan=lifespan)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


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
    if request.use_rag and not pipeline.store.chunks:
        raise HTTPException(status_code=409, detail="Ingest documents before using RAG")
    capture = FileStreamingGenerator(settings.stream_dir, settings.response_dir)
    streamed_workflow = FinTechRequirementsWorkflow(pipeline, capture)
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
