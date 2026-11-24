from typing import Any
import logging

from langgraph.graph import END, StateGraph

from agents import DocumentationAgent, QualityCheckAgent, RequirementExtractionAgent, SDLCSelectionAgent
from rag.pipeline import RegulatoryRAGPipeline
from state import GraphState


logger = logging.getLogger(__name__)


class FinTechRequirementsWorkflow:
    def __init__(self, pipeline: RegulatoryRAGPipeline, generate, on_progress=None):
        self.pipeline = pipeline
        self.on_progress = on_progress
        self.requirement_agent = RequirementExtractionAgent(generate)
        self.quality_agent = QualityCheckAgent(generate)
        self.sdlc_agent = SDLCSelectionAgent(generate)
        self.documentation_agent = DocumentationAgent(generate)
        self.app = self._build_graph()

    def retrieve_node(self, state: GraphState) -> dict[str, Any]:
        logger.info("Workflow step 1/6: retrieving regulatory context")
        if self.on_progress:
            self.on_progress("Searching PDFs, embedding the query, and reranking matches…")
        if not state.get("use_rag", True):
            return {"retrieved_context": [], "context_str": ""}
        chunks = self.pipeline.store.retrieve(
            state["user_query"],
            top_k_fusion=self.pipeline.top_k_fusion,
            final_k=self.pipeline.final_k,
        )
        context = "\n\n".join(
            f"[DOCUMENT: {item['meta']['doc']} | LOCATION: {item['meta']['section']}]\n{item['text']}"
            for item in chunks
        )
        return {"retrieved_context": chunks, "context_str": context}

    def extract_node(self, state: GraphState) -> dict[str, Any]:
        logger.info("Workflow step 2/6: extracting requirements")
        if self.on_progress:
            self.on_progress("Extracting structured requirements…")
        result = self.requirement_agent.run(
            state["user_query"],
            state.get("context_str", ""),
            state.get("organization_scale", "Medium"),
            state.get("generation_options", {}),
        )
        return {"extracted_requirements": result.get("extracted_requirements", [])}

    def quality_node(self, state: GraphState) -> dict[str, Any]:
        logger.info("Workflow step 3/6: checking requirement quality")
        if self.on_progress:
            self.on_progress("Checking completeness and ambiguity…")
        result = self.quality_agent.run(
            state["user_query"],
            state.get("extracted_requirements", []),
            state.get("generation_options", {}),
        )
        return {"quality_check": result}

    def sdlc_node(self, state: GraphState) -> dict[str, Any]:
        logger.info("Workflow step 4/6: selecting SDLC approach")
        if self.on_progress:
            self.on_progress("Choosing an SDLC approach…")
        result = self.sdlc_agent.run(
            state.get("extracted_requirements", []),
            state.get("organization_scale", "Medium"),
            state.get("generation_options", {}),
        )
        factors = result.get("derived_factors", {})
        recommendation = dict(result.get("sdlc_recommendation", {}))
        recommendation["derived_factors"] = factors
        return {
            "sdlc_factors": factors,
            "sdlc_recommendation": recommendation,
        }

    def approval_node(self, state: GraphState) -> dict[str, Any]:
        logger.info("Workflow step 5/6: applying human approval state")
        return {"human_approved": state.get("human_approved", True)}

    def documentation_node(self, state: GraphState) -> dict[str, Any]:
        logger.info("Workflow step 6/6: assembling final SRS")
        if self.on_progress:
            self.on_progress("Writing the final SRS…")
        sdlc = state.get("sdlc_recommendation", {})
        markdown = self.documentation_agent.generate_srs_markdown(
            state["user_query"],
            state.get("organization_scale", "Medium"),
            state.get("extracted_requirements", []),
            state.get("quality_check", {}),
            sdlc,
            state.get("generation_options", {}),
            state.get("context_str", ""),
        )
        return {"final_srs_markdown": markdown}

    def _build_graph(self):
        workflow = StateGraph(GraphState)
        workflow.add_node("retrieve", self.retrieve_node)
        workflow.add_node("extract_requirements", self.extract_node)
        workflow.add_node("quality_check", self.quality_node)
        workflow.add_node("sdlc_selection", self.sdlc_node)
        workflow.add_node("human_approval", self.approval_node)
        workflow.add_node("generate_documentation", self.documentation_node)
        workflow.set_entry_point("retrieve")
        workflow.add_edge("retrieve", "extract_requirements")
        workflow.add_edge("extract_requirements", "quality_check")
        workflow.add_edge("quality_check", "sdlc_selection")
        workflow.add_edge("sdlc_selection", "human_approval")
        workflow.add_edge("human_approval", "generate_documentation")
        workflow.add_edge("generate_documentation", END)
        return workflow.compile()
