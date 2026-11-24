from typing import Any, Callable
import logging

from langgraph.graph import END, StateGraph

from agents import DocumentationAgent, QualityCheckAgent, RequirementExtractionAgent, SDLCSelectionAgent
from rag.pipeline import RegulatoryRAGPipeline
from rag.tools import RegulatoryContextTool
from state import GraphState


logger = logging.getLogger(__name__)


class FinTechRequirementsWorkflow:
    def __init__(self, pipeline: RegulatoryRAGPipeline, generate, progress: Callable[[str, str], None] | None = None):
        self.pipeline = pipeline
        self.progress = progress
        self.rag_tool = RegulatoryContextTool(pipeline)
        self.requirement_agent = RequirementExtractionAgent(generate, self.rag_tool)
        self.quality_agent = QualityCheckAgent(generate)
        self.sdlc_agent = SDLCSelectionAgent(generate)
        self.documentation_agent = DocumentationAgent(generate)
        self.app = self._build_graph()

    def extract_node(self, state: GraphState) -> dict[str, Any]:
        self._emit_progress("requirements", "Extracting requirements")
        logger.info("Workflow step 1/5: extracting requirements with regulatory context tool")
        result = self.requirement_agent.run(
            state["user_query"],
            state.get("organization_scale", "Medium"),
            state.get("use_rag", True),
            state.get("generation_options", {}),
        )
        return {
            "retrieved_context": result.get("retrieved_context", []),
            "context_str": result.get("context_str", ""),
            "extracted_requirements": result.get("extracted_requirements", []),
        }

    def quality_node(self, state: GraphState) -> dict[str, Any]:
        self._emit_progress("quality", "Reviewing requirement completeness")
        logger.info("Workflow step 2/5: checking requirement quality")
        result = self.quality_agent.run(
            state["user_query"],
            state.get("extracted_requirements", []),
            state.get("generation_options", {}),
        )
        return {"quality_check": result}

    def sdlc_node(self, state: GraphState) -> dict[str, Any]:
        self._emit_progress("sdlc", "Selecting the SDLC approach")
        logger.info("Workflow step 3/5: selecting SDLC approach")
        result = self.sdlc_agent.run(
            state.get("extracted_requirements", []),
            state.get("organization_scale", "Medium"),
            state.get("generation_options", {}),
        )
        recommendation = dict(result.get("sdlc_recommendation", {}))
        return {
            "sdlc_factors": result.get("derived_factors", {}),
            "sdlc_recommendation": recommendation,
        }

    def approval_node(self, state: GraphState) -> dict[str, Any]:
        self._emit_progress("approval", "Applying the approval checkpoint")
        logger.info("Workflow step 4/5: applying human approval state")
        return {"human_approved": state.get("human_approved", True)}

    def documentation_node(self, state: GraphState) -> dict[str, Any]:
        self._emit_progress("document", "Preparing the final SRS")
        logger.info("Workflow step 5/5: assembling final SRS")
        sdlc = state.get("sdlc_recommendation", {})
        markdown = self.documentation_agent.generate_srs_markdown(
            state["user_query"],
            state.get("organization_scale", "Medium"),
            state.get("extracted_requirements", []),
            state.get("quality_check", {}),
            sdlc,
            state.get("generation_options", {}),
        )
        return {"final_srs_markdown": markdown}

    def _build_graph(self):
        workflow = StateGraph(GraphState)
        workflow.add_node("extract_requirements", self.extract_node)
        workflow.add_node("quality_check", self.quality_node)
        workflow.add_node("sdlc_selection", self.sdlc_node)
        workflow.add_node("human_approval", self.approval_node)
        workflow.add_node("generate_documentation", self.documentation_node)
        workflow.set_entry_point("extract_requirements")
        workflow.add_edge("extract_requirements", "quality_check")
        workflow.add_edge("quality_check", "sdlc_selection")
        workflow.add_edge("sdlc_selection", "human_approval")
        workflow.add_edge("human_approval", "generate_documentation")
        workflow.add_edge("generate_documentation", END)
        return workflow.compile()

    def _emit_progress(self, step: str, message: str) -> None:
        if self.progress is not None:
            self.progress(step, message)
