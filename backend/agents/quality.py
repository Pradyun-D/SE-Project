import json
from typing import Any

from .base import AgentBase
from schemas import QualityCheckResult


class QualityCheckAgent(AgentBase):
    def run(
        self,
        user_query: str,
        requirements: list[dict[str, Any]],
        generation_options: dict[str, Any],
    ) -> dict[str, Any]:
        prompt = f"""You are a FinTech requirements quality specialist.
Review the request and extracted requirements for ambiguity, incompleteness, duplicated
requirements, contradictions between requirements, missing stakeholder viewpoints,
missing user stories/use cases, missing traceability, and missing security, consent,
privacy, retention, regulatory, and operational controls.
Return only one valid JSON object. Do not copy example values. Compute every field from the request and extracted requirements.

Field rules:
- is_complete: true only when the requirements are specific enough to implement and have no material gaps; otherwise false.
- ambiguity_score: a number from 0.0 (clear) to 1.0 (highly ambiguous).
- missing_aspects: concrete missing requirements or decisions; use an empty array only when no material aspects are missing.
- clarification_questions: specific questions needed to resolve the missing aspects; use an empty array only when no clarification is needed.
- conflicts: each contradiction must identify the requirements involved, explain the conflict, and state the decision needed.
- traceability_coverage: a number from 0.0 to 1.0 representing how much of the requirement set has source and acceptance-test links.

Required JSON shape:
{{
    "is_complete": <boolean>,
    "ambiguity_score": <number between 0.0 and 1.0>,
    "missing_aspects": ["<concrete gap>"],
    "clarification_questions": ["<specific question>"],
    "conflicts": [{{"requirements": ["REQ-001", "REQ-002"], "description": "", "resolution_needed": ""}}],
    "traceability_coverage": <number between 0.0 and 1.0>
}}

Request:
{user_query}

Extracted requirements:
{json.dumps(requirements, indent=2)}"""
        try:
            return QualityCheckResult.model_validate(self.ask_json(prompt, generation_options)).model_dump()
        except (ValueError, json.JSONDecodeError):
            return {
                "is_complete": False,
                "ambiguity_score": 1.0,
                "missing_aspects": ["Quality model response could not be parsed"],
                "clarification_questions": ["Review and clarify the extracted requirements"],
            }