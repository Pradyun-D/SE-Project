import logging
import time
from collections.abc import Iterator

import requests


logger = logging.getLogger(__name__)


class RemoteModelClient:
    def __init__(self, base_url: str, timeout_seconds: float = 900.0, retry_count: int = 5):
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds
        self.retry_count = retry_count

    def generate(self, prompt: str, **generation_options: object) -> str:
        body = self._post(
            "/generate",
            json={"prompt": prompt, **generation_options},
        )
        result = body.get("response")
        if not isinstance(result, str):
            raise ValueError("Model response does not contain a string 'response' field")
        return result

    def generate_stream(self, prompt: str, **generation_options: object) -> Iterator[str]:
        logger.info("Kaggle streaming request: POST /generate/stream")
        response = requests.post(
            f"{self.base_url}/generate/stream",
            json={"prompt": prompt, **generation_options},
            timeout=(30, self.timeout_seconds),
            stream=True,
        )
        if response.status_code == 404:
            raise RuntimeError(
                f"Kaggle server returned 404 for {self.base_url}/generate/stream. "
                "Restart the Kaggle notebook with the updated /generate/stream endpoint."
            )
        response.raise_for_status()
        for chunk in response.iter_content(chunk_size=None, decode_unicode=True):
            if chunk:
                yield chunk
        logger.info("Kaggle streaming response complete")

    def embed(self, texts: list[str]) -> list[list[float]]:
        body = self._post("/embed", json={"texts": texts})
        embeddings = body.get("embeddings")
        if not isinstance(embeddings, list):
            raise ValueError("Model response does not contain embeddings")
        return embeddings

    def rerank(self, query: str, documents: list[str]) -> list[float]:
        body = self._post("/rerank", json={"query": query, "documents": documents})
        scores = body.get("scores")
        if not isinstance(scores, list):
            raise ValueError("Model response does not contain reranking scores")
        return scores

    def _post(self, path: str, **kwargs: object) -> dict:
        for attempt in range(1, self.retry_count + 1):
            logger.info("Kaggle request: POST %s (attempt %d/%d)", path, attempt, self.retry_count)
            try:
                response = requests.post(
                    f"{self.base_url}{path}",
                    timeout=(30, self.timeout_seconds),
                    **kwargs,
                )
                if response.status_code in {502, 503, 504} and attempt < self.retry_count:
                    delay = min(30, 2 ** (attempt - 1))
                    logger.warning("Kaggle returned %s for %s; retrying in %ds", response.status_code, path, delay)
                    time.sleep(delay)
                    continue
                if response.status_code == 404:
                    raise RuntimeError(
                        f"Kaggle server does not expose {path}. Restart it with kaggle_server.py "
                        "so /embed, /rerank, and /generate are available."
                    )
                response.raise_for_status()
                logger.info("Kaggle response received: POST %s", path)
                return response.json()
            except requests.RequestException:
                if attempt == self.retry_count:
                    raise
                delay = min(30, 2 ** (attempt - 1))
                logger.warning("Kaggle request failed for %s; retrying in %ds", path, delay)
                time.sleep(delay)
        raise RuntimeError(f"Kaggle request failed: {path}")