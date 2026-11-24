from .vector_store import HybridVectorStore
from .cache import load_chunks, save_chunks


class RegulatoryRAGPipeline:
    def __init__(
        self,
        model_client,
        top_k_fusion: int,
        final_k: int,
        embedding_batch_size: int = 32,
        vector_db_path: str | None = None,
        vector_db_url: str | None = None,
        vector_db_api_key: str | None = None,
        vector_db_collection: str = "regulatory_chunks",
    ):
        self.store = HybridVectorStore(
            model_client,
            embedding_batch_size,
            database_path=vector_db_path,
            database_url=vector_db_url,
            api_key=vector_db_api_key,
            collection_name=vector_db_collection,
        )
        self.top_k_fusion = top_k_fusion
        self.final_k = final_k

    def ingest(self, chunks: list[dict]) -> None:
        self.store.ingest(chunks)

    def save(
        self,
        cache_dir: str,
        docs_dir: str,
        embedding_model: str,
        embedding_dimensions: int,
    ) -> None:
        save_chunks(
            cache_dir,
            self.store.chunks,
            docs_dir,
            embedding_model,
            embedding_dimensions,
        )

    def load(self, cache_dir: str) -> None:
        chunks = load_chunks(cache_dir)
        self.store.load_index(chunks)
