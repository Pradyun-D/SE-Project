from .vector_store import HybridVectorStore
from .cache import load_chunks, save_chunks


class RegulatoryRAGPipeline:
    def __init__(self, model_client, top_k_fusion: int, final_k: int, embedding_batch_size: int = 32):
        self.store = HybridVectorStore(model_client, embedding_batch_size)
        self.top_k_fusion = top_k_fusion
        self.final_k = final_k

    def ingest(self, chunks: list[dict]) -> None:
        self.store.ingest(chunks)

    def save(self, cache_dir: str, docs_dir: str) -> None:
        save_chunks(cache_dir, self.store.chunks, docs_dir)
        self.store.save_index(f"{cache_dir}/index.faiss")

    def load(self, cache_dir: str) -> None:
        chunks = load_chunks(cache_dir)
        self.store.load_index(f"{cache_dir}/index.faiss", chunks)

    def generate_requirement(
        self,
        minimal_requirement: str,
        scale: str,
        use_rag: bool,
        llm_callable,
        **generation_options: object,
    ) -> tuple[str, list[dict]]:
        sources: list[dict] = []
        if use_rag:
            retrieved = self.store.retrieve(
                minimal_requirement,
                top_k_fusion=self.top_k_fusion,
                final_k=self.final_k,
            )
            context = "\n\n".join(
                f"[DOCUMENT: {item['meta']['doc']} | LOCATION: {item['meta']['section']}]\n{item['text']}"
                for item in retrieved
            )
            sources = [item["meta"] for item in retrieved]
            prompt = self._rag_prompt(minimal_requirement, scale, context)
        else:
            prompt = self._baseline_prompt(minimal_requirement)
        return llm_callable(prompt, **generation_options), sources

    @staticmethod
    def _rag_prompt(minimal_requirement: str, scale: str, context: str) -> str:
        return f"""You are a Principal FinTech Product Manager and RBI/ReBIT Compliance Architect.
Transform the given Minimal Requirement into a structured Software Requirement Specification (SRS/PRD).
Target Organization Scale: {scale}

STRICT COMPLIANCE & EXPLAINABILITY RULES:
1. Base all technical, data, and security rules STRICTLY on the provided Context.
2. Every Functional, Non-Functional, Data, and Compliance item MUST include inline citation tags.
3. If a section is outside the provided context, clearly note it.

--- REGULATORY CONTEXT ---
{context}

--- MINIMAL REQUIREMENT ---
{minimal_requirement}

--- REFINED SRS/PRD SPECIFICATION ---
Generate:
1. Target Organization Scale Adjustments
2. Stakeholders & User Roles Table
3. Functional Requirements with citations
4. Scope Boundaries: In-Scope vs Out-of-Scope
5. User Stories & Acceptance Criteria in Gherkin format
6. Non-Functional Requirements: Performance, Security, Scalability
7. Data & ReBIT API Requirements: sensitivity, retention, payloads
8. Compliance & Consent Governance Matrix
9. MoSCoW Prioritization
10. Traceability & Explainability Matrix mapped to source citations"""

    @staticmethod
    def _baseline_prompt(minimal_requirement: str) -> str:
        return f"""You are a FinTech Product Manager.
Transform the given Minimal Requirement into an SRS/PRD covering Functional Requirements, NFRs, Scope, Data, Compliance, MoSCoW, and Traceability.

--- MINIMAL REQUIREMENT ---
{minimal_requirement}

--- REFINED SRS/PRD SPECIFICATION ---"""