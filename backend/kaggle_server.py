import os
import threading
from collections.abc import Iterator

import nest_asyncio
import torch
import uvicorn
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from pyngrok import ngrok
from sentence_transformers import CrossEncoder, SentenceTransformer
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    TextIteratorStreamer,
)


app = FastAPI(title="Regulatory Model Server")
generation_lock = threading.Lock()
embedding_lock = threading.Lock()

MODEL_PATH = os.environ.get(
    "QWEN_MODEL_PATH",
    "/kaggle/input/models/qwen-lm/qwen-3/transformers/4b/1",
)
EMBEDDING_MODEL = os.environ.get("EMBEDDING_MODEL", "BAAI/bge-m3")
RERANKER_MODEL = os.environ.get("RERANKER_MODEL", "BAAI/bge-reranker-v2-m3")

print(f"Loading local Qwen model from: {MODEL_PATH}")
tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH, local_files_only=True)
quantization = BitsAndBytesConfig(
    load_in_8bit=True,
    bnb_8bit_compute_dtype=torch.float16,
)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_PATH,
    quantization_config=quantization,
    device_map="auto",
    torch_dtype=torch.float16,
)
print("Qwen model loaded")

print("Loading embedding and reranker models")
embedding_model = SentenceTransformer(EMBEDDING_MODEL, device="cpu")
reranker = CrossEncoder(RERANKER_MODEL, device="cpu")
print("All models are ready")


class GenerationRequest(BaseModel):
    prompt: str = Field(min_length=1)
    max_new_tokens: int = Field(default=1024, ge=1, le=8192)
    temperature: float = Field(default=0.3, ge=0, le=2)
    top_p: float = Field(default=0.95, gt=0, le=1)


class EmbeddingRequest(BaseModel):
    texts: list[str] = Field(min_length=1)


class RerankRequest(BaseModel):
    query: str = Field(min_length=1)
    documents: list[str] = Field(min_length=1)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/embed")
def embed(request: EmbeddingRequest) -> dict[str, list[list[float]]]:
    with embedding_lock:
        vectors = embedding_model.encode(
            request.texts,
            normalize_embeddings=True,
            convert_to_numpy=True,
            show_progress_bar=False,
        )
    return {"embeddings": vectors.tolist()}


@app.post("/rerank")
def rerank(request: RerankRequest) -> dict[str, list[float]]:
    pairs = [[request.query, document] for document in request.documents]
    scores = reranker.predict(pairs)
    return {"scores": [float(score) for score in scores]}


def generation_stream(request: GenerationRequest) -> Iterator[str]:
    messages = [
        {
            "role": "system",
            "content": "You are a meticulous FinTech architectural compliance engine.",
        },
        {"role": "user", "content": request.prompt},
    ]
    formatted_prompt = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True,
    )
    inputs = tokenizer(formatted_prompt, return_tensors="pt").to(model.device)
    streamer = TextIteratorStreamer(
        tokenizer,
        skip_prompt=True,
        skip_special_tokens=True,
    )
    generation_kwargs = {
        **inputs,
        "streamer": streamer,
        "max_new_tokens": request.max_new_tokens,
        "temperature": request.temperature,
        "top_p": request.top_p,
        "do_sample": True,
        "repetition_penalty": 1.05,
    }

    with generation_lock:
        thread = threading.Thread(target=model.generate, kwargs=generation_kwargs)
        thread.start()
        try:
            for text in streamer:
                yield text
        finally:
            thread.join()


@app.post("/generate")
def generate(request: GenerationRequest) -> dict[str, str]:
    return {"status": "success", "response": "".join(generation_stream(request))}


@app.post("/generate/stream")
def generate_stream(request: GenerationRequest) -> StreamingResponse:
    return StreamingResponse(
        generation_stream(request),
        media_type="text/plain",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


def start_server() -> None:
    ngrok_token = os.environ.get("NGROK_AUTHTOKEN")
    if not ngrok_token:
        raise RuntimeError("Set NGROK_AUTHTOKEN in Kaggle Secrets")
    ngrok.set_auth_token(ngrok_token)
    public_url = ngrok.connect(8000).public_url
    print(f"KAGGLE_URL={public_url}")
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    nest_asyncio.apply()
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    print("Server is running")