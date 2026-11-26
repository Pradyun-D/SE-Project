
# !pip install fastapi uvicorn pyngrok nest-asyncio transformers bitsandbytes torch accelerate sentence-transformers -q

import threading
import nest_asyncio
import torch
import uvicorn

from pyngrok import ngrok
from kaggle_secrets import UserSecretsClient
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sentence_transformers import CrossEncoder, SentenceTransformer
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    TextIteratorStreamer,
)

MODEL_PATH = "/kaggle/input/models/qwen-lm/qwen-3/transformers/4b/1"
EMBEDDING_MODEL = "BAAI/bge-m3"
RERANKER_MODEL = "BAAI/bge-reranker-v2-m3"

app = FastAPI(title="Regulatory Model Server")

generation_lock = threading.Lock()
embedding_lock = threading.Lock()

tokenizer = AutoTokenizer.from_pretrained(
    MODEL_PATH, local_files_only=True
)

model = AutoModelForCausalLM.from_pretrained(
    MODEL_PATH,
    quantization_config=BitsAndBytesConfig(load_in_8bit=True),
    device_map="auto",
    torch_dtype=torch.float16,
)

embedding_model = SentenceTransformer(EMBEDDING_MODEL, device="cpu")
reranker = CrossEncoder(RERANKER_MODEL, device="cpu")


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


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/embed")
def embed(request: EmbeddingRequest):
    with embedding_lock:
        vectors = embedding_model.encode(
            request.texts,
            normalize_embeddings=True,
            convert_to_numpy=True,
            show_progress_bar=False,
        )
    return {"embeddings": vectors.tolist()}


@app.post("/rerank")
def rerank(request: RerankRequest):
    pairs = [[request.query, doc] for doc in request.documents]
    scores = reranker.predict(pairs)
    return {"scores": [float(score) for score in scores]}


def generate_tokens(request: GenerationRequest):
    messages = [
        {
            "role": "system",
            "content": "You are a meticulous FinTech architectural compliance engine.",
        },
        {"role": "user", "content": request.prompt},
    ]

    prompt = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True,
        enable_thinking=False,
    )

    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)

    streamer = TextIteratorStreamer(
        tokenizer,
        skip_prompt=True,
        skip_special_tokens=True,
    )

    kwargs = {
        **inputs,
        "streamer": streamer,
        "max_new_tokens": request.max_new_tokens,
        "temperature": request.temperature,
        "top_p": request.top_p,
        "do_sample": True,
        "repetition_penalty": 1.05,
    }

    with generation_lock:
        thread = threading.Thread(target=model.generate, kwargs=kwargs)
        thread.start()

        try:
            yield from streamer
        finally:
            thread.join()


@app.post("/generate")
def generate(request: GenerationRequest):
    return {
        "status": "success",
        "response": "".join(generate_tokens(request)),
    }


@app.post("/generate/stream")
def generate_stream(request: GenerationRequest):
    return StreamingResponse(
        generate_tokens(request),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


secrets = UserSecretsClient()
ngrok.set_auth_token(secrets.get_secret("NGROK_AUTH_TOKEN"))
ngrok.kill()

public_url = ngrok.connect(8000)
print(f"API URL: {public_url.public_url}")

nest_asyncio.apply()

threading.Thread(
    target=uvicorn.run,
    args=(app,),
    kwargs={"host": "0.0.0.0", "port": 8000},
    daemon=True,
).start()
