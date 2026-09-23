from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent


class Settings(BaseSettings):
    kaggle_url: str = "https://simplify-imaginary-hardness.ngrok-free.dev"
    model_timeout_seconds: float = 3600.0
    model_retry_count: int = 5
    embedding_batch_size: int = 8
    data_dir: str = str(BASE_DIR / "docs")
    cache_dir: str = str(BASE_DIR / "data")
    stream_dir: str = str(BASE_DIR / "stream")
    response_dir: str = str(BASE_DIR / "responses")
    top_k_fusion: int = 20
    final_k: int = 5
    vector_db_backend: str = "qdrant"
    vector_db_path: str = str(BASE_DIR / "data" / "qdrant")
    vector_db_url: str | None = None
    vector_db_api_key: str | None = None
    vector_db_collection: str = "regulatory_chunks"

    model_config = SettingsConfigDict(env_file=".env", env_prefix="RAG_", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()