import json
import logging
from pathlib import Path


logger = logging.getLogger(__name__)


def document_signature(folder_path: str) -> list[dict[str, int | str]]:
    folder = Path(folder_path)
    return [
        {
            "name": path.name,
            "size": path.stat().st_size,
            "modified_ns": path.stat().st_mtime_ns,
        }
        for path in sorted(folder.glob("*.pdf"))
    ]


def cache_is_current(
    cache_dir: str,
    docs_dir: str,
    embedding_model: str,
    embedding_dimensions: int,
) -> bool:
    cache = Path(cache_dir)
    manifest_path = cache / "manifest.json"
    chunks_path = cache / "chunks.json"
    if not manifest_path.is_file() or not chunks_path.is_file():
        logger.info("Cache miss: persisted chunks or document manifest is missing")
        return False
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        logger.warning("Cache miss: manifest is incomplete or invalid")
        return False
    saved_documents = manifest.get("documents")
    current_documents = document_signature(docs_dir)
    if manifest.get("embedding_model") != embedding_model:
        logger.info("Cache stale: embedding model has changed")
        return False
    if manifest.get("embedding_dimensions") != embedding_dimensions:
        logger.info("Cache stale: embedding dimensions have changed")
        return False
    current = saved_documents == current_documents
    if not current:
        logger.info("Cache stale: document signature has changed")
        return False
    logger.info("Cache %s: document manifest %s", "hit" if current else "stale", cache_dir)
    return current


def save_chunks(
    cache_dir: str,
    chunks: list[dict],
    docs_dir: str,
    embedding_model: str,
    embedding_dimensions: int,
) -> None:
    cache = Path(cache_dir)
    cache.mkdir(parents=True, exist_ok=True)
    chunks_path = cache / "chunks.json"
    manifest_path = cache / "manifest.json"
    chunks_temp = cache / "chunks.json.tmp"
    manifest_temp = cache / "manifest.json.tmp"
    chunks_temp.write_text(json.dumps(chunks, ensure_ascii=False), encoding="utf-8")
    manifest_temp.write_text(
        json.dumps(
            {
                "documents": document_signature(docs_dir),
                "embedding_model": embedding_model,
                "embedding_dimensions": embedding_dimensions,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    chunks_temp.replace(chunks_path)
    manifest_temp.replace(manifest_path)
    logger.info("Persisted %d chunks and document manifest to %s", len(chunks), cache)


def load_chunks(cache_dir: str) -> list[dict]:
    return json.loads((Path(cache_dir) / "chunks.json").read_text(encoding="utf-8"))
