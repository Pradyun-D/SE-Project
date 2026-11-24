from typing import Any

from pydantic import BaseModel, Field


class GenerateRequest(BaseModel):
    minimal_requirement: str = Field(min_length=1)
    scale: str = "Medium"
    use_rag: bool = True
    max_new_tokens: int = Field(default=2048, ge=1, le=8192)
    temperature: float = Field(default=0.3, ge=0, le=2)
    top_p: float = Field(default=0.95, gt=0, le=1)
    human_approved: bool = True


class GenerateResponse(BaseModel):
    response: str
    sources: list[dict[str, Any]] = Field(default_factory=list)
    extracted_requirements: list[dict[str, Any]] = Field(default_factory=list)
    quality_check: dict[str, Any] = Field(default_factory=dict)
    sdlc_factors: dict[str, Any] = Field(default_factory=dict)
    sdlc_recommendation: dict[str, Any] = Field(default_factory=dict)
    human_approved: bool = False
    stream_file: str | None = None
    response_file: str | None = None


class IngestResponse(BaseModel):
    documents: int
    chunks: int


class QualityCheckResult(BaseModel):
    is_complete: bool = False
    ambiguity_score: float = Field(default=1.0, ge=0, le=1)
    missing_aspects: list[str] = Field(default_factory=list)
    clarification_questions: list[str] = Field(default_factory=list)
    conflicts: list[dict[str, Any]] = Field(default_factory=list)
    traceability_coverage: float = Field(default=0.0, ge=0, le=1)


class SDLCRecommendation(BaseModel):
    primary_recommendation: str = "DevSecOps"
    decision_rationale: str = ""
    ranked_scores: list[dict[str, Any]] = Field(default_factory=list)
    custom_workflow_phases: list[Any] = Field(default_factory=list)
    approval_checkpoints: list[Any] = Field(default_factory=list)


class SDLCResult(BaseModel):
    derived_factors: dict[str, Any] = Field(default_factory=dict)
    sdlc_recommendation: SDLCRecommendation


