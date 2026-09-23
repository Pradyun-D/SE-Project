import logging
from pathlib import Path

import faiss
import numpy as np
from rank_bm25 import BM25Okapi

from model_client import RemoteModelClient


logger = logging.getLogger(__name__)


class HybridVectorStore:
    def __init__(
        self,
        model_client: RemoteModelClient,
        embedding_batch_size: int = 32,
        backend: str = "faiss",
        database_path: str | None = None,
        database_url: str | None = None,
        api_key: str | None = None,
        collection_name: str = "regulatory_chunks",
    ):
        self.model_client = model_client
        self.embedding_batch_size = embedding_batch_size
        self.backend = backend.lower()
        self.database_path = database_path
        self.collection_name = collection_name
        self.chunks: list[dict] = []
        self.bm25: BM25Okapi | None = None
        self.faiss_index: faiss.Index | None = None
        self.qdrant = None

        if self.backend == "qdrant":
            try:
                from qdrant_client import QdrantClient
            except ImportError as error:
                raise RuntimeError("qdrant-client is required when vector_db_backend=qdrant") from error
            if database_url:
                self.qdrant = QdrantClient(url=database_url, api_key=api_key)
            else:
                if not database_path:
                    raise ValueError("A database_path or database_url is required for Qdrant")
                Path(database_path).mkdir(parents=True, exist_ok=True)
                self.qdrant = QdrantClient(path=database_path)
        elif self.backend != "faiss":
            raise ValueError(f"Unsupported vector database backend: {backend}")

    def ingest(self, chunks: list[dict]) -> None:
        if not chunks:
            raise ValueError("No document chunks were found")
        logger.info("Building BM25 and %s vector index for %d chunks", self.backend.upper(), len(chunks))
        self.chunks = chunks
        tokenized = [chunk["text"].lower().split() for chunk in chunks]
        self.bm25 = BM25Okapi(tokenized)
        texts = [chunk["text"] for chunk in chunks]
        embeddings_data: list[list[float]] = []
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
        faiss.normalize_L2(embeddings)
        if self.backend == "qdrant":
            from qdrant_client.models import Distance, PointStruct, VectorParams

            self.qdrant.recreate_collection(
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
        else:
            self.faiss_index = faiss.IndexFlatIP(embeddings.shape[1])
            self.faiss_index.add(embeddings)
        logger.info("Finished building vector indexes")

    def save_index(self, path: str) -> None:
        if self.backend == "qdrant":
            return
        if self.faiss_index is None:
            raise RuntimeError("The vector store has not been ingested")
        temporary_path = f"{path}.tmp"
        faiss.write_index(self.faiss_index, temporary_path)
        import os

        os.replace(temporary_path, path)

    def load_index(self, path: str, chunks: list[dict]) -> None:
        logger.info("Loading persisted %s vector index", self.backend.upper())
        self.chunks = chunks
        self.bm25 = BM25Okapi([chunk["text"].lower().split() for chunk in chunks])
        if self.backend == "qdrant":
            if not self.qdrant.collection_exists(self.collection_name):
                raise FileNotFoundError(f"Qdrant collection '{self.collection_name}' does not exist")
        else:
            self.faiss_index = faiss.read_index(path)
        logger.info("Loaded vector indexes for %d chunks", len(chunks))

    def retrieve(self, query: str, top_k_fusion: int = 20, final_k: int = 5) -> list[dict]:
        if self.bm25 is None or (self.backend == "faiss" and self.faiss_index is None):
            raise RuntimeError("The vector store has not been ingested")
        limit = min(top_k_fusion, len(self.chunks))
        sparse_scores = self.bm25.get_scores(query.lower().split())
        sparse_indices = np.argsort(sparse_scores)[::-1][:limit]
        query_embedding = np.asarray(self.model_client.embed([query]), dtype="float32")
        faiss.normalize_L2(query_embedding)
        if self.backend == "qdrant":
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
            dense_indices = [[result.payload["chunk_index"] for result in dense_results]]
        else:
            _, dense_indices = self.faiss_index.search(query_embedding, limit)
        scores: dict[int, float] = {}
        for rank, index in enumerate(sparse_indices):
            scores[int(index)] = scores.get(int(index), 0) + 1 / (60 + rank + 1)
        for rank, index in enumerate(dense_indices[0]):
            scores[int(index)] = scores.get(int(index), 0) + 1 / (60 + rank + 1)
        candidates = sorted(scores, key=scores.get, reverse=True)[:limit]
        pairs = [[query, self.chunks[index]["text"]] for index in candidates]
        reranked = self.model_client.rerank(query, [pair[1] for pair in pairs])
        ordered = sorted(zip(candidates, reranked), key=lambda item: item[1], reverse=True)
        return [self.chunks[index] for index, _ in ordered[:final_k]]