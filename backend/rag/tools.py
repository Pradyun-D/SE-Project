import logging
from typing import Any

from .pipeline import RegulatoryRAGPipeline


logger = logging.getLogger(__name__)


class RegulatoryContextTool:
    name = "retrieve_regulatory_context"

    def __init__(self, pipeline: RegulatoryRAGPipeline):
        self.pipeline = pipeline

    def run(self, query: str) -> dict[str, Any]:
        logger.info("RAG tool '%s': retrieving regulatory context", self.name)
        chunks = self.pipeline.store.retrieve(
            query,
            top_k_fusion=self.pipeline.top_k_fusion,
            final_k=self.pipeline.final_k,
        )
        context = "\n\n".join(
            f"[DOCUMENT: {item['meta']['doc']} | LOCATION: {item['meta']['section']}]\n{item['text']}"
            for item in chunks
        )
        return {"retrieved_context": chunks, "context_str": context}
