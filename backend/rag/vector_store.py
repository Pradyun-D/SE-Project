import logging
from pathlib import Path

import numpy as np
from rank_bm25 import BM25Okapi

from model_client import GeminiModelClient


logger = logging.getLogger(__name__)


class HybridVectorStore:
    def __init__(
        self,
        model_client: GeminiModelClient,
        embedding_batch_size: int = 32,
        database_path: str | None = None,
        database_url: str | None = None,
        api_key: str | None = None,
        collection_name: str = "regulatory_chunks",
    ):
        self.model_client = model_client
        self.embedding_batch_size = embedding_batch_size
        self.collection_name = collection_name
        self.chunks: list[dict] = []
        self.bm25: BM25Okapi | None = None

        try:
            from qdrant_client import QdrantClient
        except ImportError as error:
            raise RuntimeError("qdrant-client is required for vector storage") from error

        if database_url:
            self.qdrant = QdrantClient(url=database_url, api_key=api_key)
        else:
            if not database_path:
                raise ValueError("A database_path or database_url is required for Qdrant")
            Path(database_path).mkdir(parents=True, exist_ok=True)
            self.qdrant = QdrantClient(path=database_path)

    def ingest(self, chunks: list[dict]) -> None:
        if not chunks:
            raise ValueError("No document chunks were found")
        logger.info("Building BM25 and Qdrant vector index for %d chunks", len(chunks))
        self.chunks = chunks
        self.bm25 = BM25Okapi([chunk["text"].lower().split() for chunk in chunks])

        embeddings_data: list[list[float]] = []
        texts = [chunk["text"] for chunk in chunks]
        for start in range(0, len(texts), self.embedding_batch_size):
            batch = texts[start : start + self.embedding_batch_size]
            logger.info(
                "Embedding batch %d-%d of %d",
                start + 1,
                start + len(batch),
                len(texts),
            )
            embeddings_data.extend(self.model_client.embed(batch))

        embeddings = np.asarray(embeddings_data, dtype="float32")
        self._normalize(embeddings)

        from qdrant_client.models import Distance, PointStruct, VectorParams

        if self.qdrant.collection_exists(self.collection_name):
            logger.info("Replacing existing Qdrant collection '%s'", self.collection_name)
            self.qdrant.delete_collection(self.collection_name)
        self.qdrant.create_collection(
            collection_name=self.collection_name,
            vectors_config=VectorParams(size=embeddings.shape[1], distance=Distance.COSINE),
        )
        self.qdrant.upsert(
            collection_name=self.collection_name,
            points=[
                PointStruct(id=index, vector=vector.tolist(), payload={"chunk_index": index})
                for index, vector in enumerate(embeddings)
            ],
        )
        logger.info("Finished building vector indexes")

    def load_index(self, chunks: list[dict]) -> None:
        logger.info("Loading persisted Qdrant vector index")
        self.chunks = chunks
        self.bm25 = BM25Okapi([chunk["text"].lower().split() for chunk in chunks])
        if not self.qdrant.collection_exists(self.collection_name):
            raise FileNotFoundError(f"Qdrant collection '{self.collection_name}' does not exist")
        logger.info("Loaded vector indexes for %d chunks", len(chunks))

    def retrieve(self, query: str, top_k_fusion: int = 20, final_k: int = 5) -> list[dict]:
        if self.bm25 is None:
            raise RuntimeError("The vector store has not been ingested")
        limit = min(top_k_fusion, len(self.chunks))
        sparse_scores = self.bm25.get_scores(query.lower().split())
        sparse_indices = np.argsort(sparse_scores)[::-1][:limit]

        query_embedding = np.asarray(self.model_client.embed([query]), dtype="float32")
        self._normalize(query_embedding)
        if hasattr(self.qdrant, "query_points"):
            response = self.qdrant.query_points(
                collection_name=self.collection_name,
                query=query_embedding[0].tolist(),
                limit=limit,
                with_payload=True,
            )
            dense_results = response.points
        else:
            dense_results = self.qdrant.search(
                collection_name=self.collection_name,
                query_vector=query_embedding[0].tolist(),
                limit=limit,
            )
        dense_indices = [result.payload["chunk_index"] for result in dense_results]

        scores: dict[int, float] = {}
        for rank, index in enumerate(sparse_indices):
            scores[int(index)] = scores.get(int(index), 0) + 1 / (60 + rank + 1)
        for rank, index in enumerate(dense_indices):
            scores[int(index)] = scores.get(int(index), 0) + 1 / (60 + rank + 1)

        candidates = sorted(scores, key=scores.get, reverse=True)[:limit]
        reranked = self.model_client.rerank(query, [self.chunks[index]["text"] for index in candidates])
        ordered = sorted(zip(candidates, reranked), key=lambda item: item[1], reverse=True)
        return [self.chunks[index] for index, _ in ordered[:final_k]]

    @staticmethod
    def _normalize(vectors: np.ndarray) -> None:
        norms = np.linalg.norm(vectors, axis=1, keepdims=True)
        norms[norms == 0] = 1
        vectors /= norms
