from typing import Any, TypedDict


class GraphState(TypedDict, total=False):
    user_query: str
    organization_scale: str
    use_rag: bool
    generation_options: dict[str, Any]
    retrieved_context: list[dict[str, Any]]
    context_str: str
    extracted_requirements: list[dict[str, Any]]
    quality_check: dict[str, Any]
    sdlc_factors: dict[str, Any]
    sdlc_recommendation: dict[str, Any]
    human_approved: bool
    final_srs_markdown: str
    error_message: str | None