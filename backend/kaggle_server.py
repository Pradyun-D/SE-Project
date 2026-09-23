# ============================================================
# 1. Install dependencies on Kaggle
# ============================================================
!pip install fastapi uvicorn pyngrok nest-asyncio transformers bitsandbytes torch accelerate sentence-transformers -q

# ============================================================
# 2. Imports
# ============================================================
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

# ============================================================
# 3. FastAPI application & Concurrency Locks
# ============================================================
app = FastAPI(title="Regulatory Model Server")

generation_lock = threading.Lock()
embedding_lock = threading.Lock()

# ============================================================
# 4. Hardcoded Model Configurations
# ============================================================
# Local path for Qwen (attached Kaggle dataset)
MODEL_PATH = "/kaggle/input/models/qwen-lm/qwen-3/transformers/4b/1"

# Hugging Face Repo IDs for automatic online download
EMBEDDING_MODEL = "BAAI/bge-m3"
RERANKER_MODEL = "BAAI/bge-reranker-v2-m3"

# ============================================================
# 5. Load Qwen model (From Local Kaggle Folder)
# ============================================================
print(f"⏳ Loading local Qwen model from: '{MODEL_PATH}'...")

tokenizer = AutoTokenizer.from_pretrained(
    MODEL_PATH,
    local_files_only=True,  # Uses local Kaggle files only
)

bnb = BitsAndBytesConfig(
    load_in_8bit=True,
    bnb_8bit_compute_dtype=torch.float16,
)

model = AutoModelForCausalLM.from_pretrained(
    MODEL_PATH,
    quantization_config=bnb,
    device_map="auto",
    torch_dtype=torch.float16,
)

print("✅ Qwen Model loaded successfully onto GPU!")

# ============================================================
# 6. Load embedding + reranker models (Auto-Downloads Online)
# ============================================================
print("⏳ Downloading and loading embedding and reranker models onto CPU...")

embedding_model = SentenceTransformer(
    EMBEDDING_MODEL,
    device="cpu",  # Loaded on CPU to save GPU RAM for Qwen
)

reranker = CrossEncoder(
    RERANKER_MODEL,
    device="cpu",  # Loaded on CPU to save GPU RAM for Qwen
)

print("✅ All models are ready!")

# ============================================================
# 7. Request schemas
# ============================================================
class GenerationRequest(BaseModel):
    prompt: str = Field(min_length=1)
    max_new_tokens: int = Field(default=4096, ge=1, le=8192)
    temperature: float = Field(default=0.3, ge=0, le=2)
    top_p: float = Field(default=0.95, gt=0, le=1)

class EmbeddingRequest(BaseModel):
    texts: list[str] = Field(min_length=1)

class RerankRequest(BaseModel):
    query: str = Field(min_length=1)
    documents: list[str] = Field(min_length=1)

# ============================================================
# 8. Health endpoint
# ============================================================
@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}

# ============================================================
# 9. Embedding endpoint (Thread-Safe)
# ============================================================
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

# ============================================================
# 10. Reranking endpoint
# ============================================================
@app.post("/rerank")
def rerank(request: RerankRequest) -> dict[str, list[float]]:
    pairs = [[request.query, document] for document in request.documents]
    scores = reranker.predict(pairs)
    return {"scores": [float(score) for score in scores]}

# ============================================================
# 11. Core Streaming Generator Function
# ============================================================
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

# ============================================================
# 12. Qwen generation endpoints (Standard + Streaming)
# ============================================================
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

# ============================================================
# 13. Configure ngrok (Hardcoded Token)
# ============================================================
NGROK_TOKEN = "3JGfV1r6M2pkOiGNp5hZeXdcL1q_5VzYpCD4wAM2y9n5qGwmR"

ngrok.set_auth_token(NGROK_TOKEN)
public_url = ngrok.connect(8000)

print(f"\n🚀 KAGGLE LLM API URL: {public_url.public_url}")
print(f"👉 Standard Endpoint: {public_url.public_url}/generate")
print(f"👉 Streaming Endpoint: {public_url.public_url}/generate/stream\n")

# ============================================================
# 14. Start Uvicorn in background
# ============================================================
def start_server():
    nest_asyncio.apply()
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
    )

server_thread = threading.Thread(
    target=start_server,
    daemon=True,
)
server_thread.start()

print("✅ Server is running in the background!")