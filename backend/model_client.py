import json
import logging
import time
from collections.abc import Iterator

import requests


logger = logging.getLogger(__name__)


class GeminiModelClient:
    def __init__(
        self,
        api_key: str,
        generation_model: str = "gemini-3.5-flash-lite",
        embedding_model: str = "gemini-embedding-001",
        embedding_dimensions: int = 1024,
        timeout_seconds: float = 900.0,
        retry_count: int = 5,
    ):
        if not api_key:
            raise ValueError("Gemini API key is required. Set RAG_GEMINI_API_KEY in .env.")
        self.api_key = api_key
        self.generation_model = generation_model
        self.embedding_model = embedding_model
        self.embedding_dimensions = embedding_dimensions
        self.timeout_seconds = timeout_seconds
        self.retry_count = retry_count
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"

    def generate(self, prompt: str, **generation_options: object) -> str:
        body = self._post_model(
            self.generation_model,
            "generateContent",
            json=self._generate_body(prompt, generation_options),
        )
        return self._extract_text(body)

    def generate_stream(self, prompt: str, **generation_options: object) -> Iterator[str]:
        logger.info("Gemini streaming request: %s:streamGenerateContent", self.generation_model)
        try:
            response = self._request(
                "POST",
                f"{self.base_url}/models/{self.generation_model}:streamGenerateContent?alt=sse",
                json=self._generate_body(prompt, generation_options),
                stream=True,
            )
        except requests.HTTPError as error:
            if error.response is None or error.response.status_code != 404:
                raise
            logger.warning(
                "Gemini streaming is unavailable for %s; falling back to generateContent",
                self.generation_model,
            )
            yield self.generate(prompt, **generation_options)
            return
        for raw_line in response.iter_lines(decode_unicode=True):
            if not raw_line or not raw_line.startswith("data:"):
                continue
            chunk = raw_line.removeprefix("data:").strip()
            if chunk == "[DONE]":
                break
            try:
                text = self._extract_text(json.loads(chunk))
            except ValueError:
                continue
            if text:
                yield text
        logger.info("Gemini streaming response complete")

    def embed(self, texts: list[str]) -> list[list[float]]:
        embeddings: list[list[float]] = []
        for text in texts:
            body = self._post_model(
                self.embedding_model,
                "embedContent",
                json={
                    "model": f"models/{self.embedding_model}",
                    "content": {"parts": [{"text": text}]},
                    "outputDimensionality": self.embedding_dimensions,
                },
            )
            values = body.get("embedding", {}).get("values")
            if not isinstance(values, list):
                raise ValueError("Gemini embedding response does not contain embedding values")
            if len(values) != self.embedding_dimensions:
                raise ValueError(
                    "Gemini returned an unexpected embedding size: "
                    f"expected {self.embedding_dimensions}, got {len(values)}"
                )
            embeddings.append(values)
        return embeddings

    def rerank(self, query: str, documents: list[str]) -> list[float]:
        if not documents:
            return []
        vectors = self.embed([query, *documents])
        query_vector = vectors[0]
        return [self._cosine(query_vector, document_vector) for document_vector in vectors[1:]]

    def _post_model(self, model: str, action: str, **kwargs: object) -> dict:
        return self._request("POST", f"{self.base_url}/models/{model}:{action}", **kwargs).json()

    def _request(self, method: str, url: str, **kwargs: object) -> requests.Response:
        headers = {"x-goog-api-key": self.api_key}
        if "headers" in kwargs and isinstance(kwargs["headers"], dict):
            headers.update(kwargs.pop("headers"))
        for attempt in range(1, self.retry_count + 1):
            logger.info("Gemini request: %s %s (attempt %d/%d)", method, url, attempt, self.retry_count)
            try:
                response = requests.request(
                    method,
                    url,
                    headers=headers,
                    timeout=(30, self.timeout_seconds),
                    **kwargs,
                )
                if response.status_code in {502, 503, 504} and attempt < self.retry_count:
                    delay = min(30, 2 ** (attempt - 1))
                    logger.warning("Gemini returned %s; retrying in %ds", response.status_code, delay)
                    time.sleep(delay)
                    continue
                response.raise_for_status()
                logger.info("Gemini response received")
                return response
            except requests.RequestException:
                if attempt == self.retry_count:
                    raise
                delay = min(30, 2 ** (attempt - 1))
                logger.warning("Gemini request failed; retrying in %ds", delay)
                time.sleep(delay)
        raise RuntimeError("Gemini request failed")

    @staticmethod
    def _generate_body(prompt: str, generation_options: dict[str, object]) -> dict:
        generation_config: dict[str, object] = {}
        option_map = {
            "max_new_tokens": "maxOutputTokens",
            "max_output_tokens": "maxOutputTokens",
            "temperature": "temperature",
            "top_p": "topP",
            "top_k": "topK",
        }
        for source, target in option_map.items():
            value = generation_options.get(source)
            if value is not None:
                generation_config[target] = value
        body: dict[str, object] = {"contents": [{"role": "user", "parts": [{"text": prompt}]}]}
        if generation_config:
            body["generationConfig"] = generation_config
        return body

    @staticmethod
    def _extract_text(body: dict) -> str:
        pieces: list[str] = []
        for candidate in body.get("candidates", []):
            for part in candidate.get("content", {}).get("parts", []):
                text = part.get("text")
                if isinstance(text, str):
                    pieces.append(text)
        if not pieces:
            raise ValueError("Gemini response did not contain generated text")
        return "".join(pieces)

    @staticmethod
    def _cosine(left: list[float], right: list[float]) -> float:
        numerator = sum(a * b for a, b in zip(left, right))
        left_norm = sum(a * a for a in left) ** 0.5
        right_norm = sum(b * b for b in right) ** 0.5
        if not left_norm or not right_norm:
            return 0.0
        return numerator / (left_norm * right_norm)
