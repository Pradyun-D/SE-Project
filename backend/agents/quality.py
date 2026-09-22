import json
from typing import Any

from .base import AgentBase


class QualityCheckAgent(AgentBase):
    def run(
        self,
        user_query: str,
        requirements: list[dict[str, Any]],
        generation_options: dict[str, Any],
    ) -> dict[str, Any]:
        prompt = f"""You are a FinTech requirements quality specialist.
Review the request and extracted requirements for ambiguity, missing security, consent, privacy, retention, and operational controls.
Return only one valid JSON object. Do not copy example values. Compute every field from the request and extracted requirements.

Field rules:
- is_complete: true only when the requirements are specific enough to implement and have no material gaps; otherwise false.
- ambiguity_score: a number from 0.0 (clear) to 1.0 (highly ambiguous).
- missing_aspects: concrete missing requirements or decisions; use an empty array only when no material aspects are missing.
- clarification_questions: specific questions needed to resolve the missing aspects; use an empty array only when no clarification is needed.

Required JSON shape:
{{
    "is_complete": <boolean>,
    "ambiguity_score": <number between 0.0 and 1.0>,
    "missing_aspects": ["<concrete gap>"],
    "clarification_questions": ["<specific question>"]
}}

Request:
{user_query}

Extracted requirements:
{json.dumps(requirements, indent=2)}"""
        try:
            return self.ask_json(prompt, generation_options)
        except (ValueError, json.JSONDecodeError):
            return {
                "is_complete": False,
                "ambiguity_score": 1.0,
                "missing_aspects": ["Quality model response could not be parsed"],
                "clarification_questions": ["Review and clarify the extracted requirements"],
            }