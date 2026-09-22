import json
from typing import Any, Callable

from .base import AgentBase


class RequirementExtractionAgent(AgentBase):
    def run(
        self,
        user_query: str,
        context: str,
        scale: str,
        generation_options: dict[str, Any],
    ) -> dict[str, Any]:
        prompt = f"""You are a Principal FinTech Product Manager and RBI/ReBIT Compliance Architect.
Extract actionable software requirements from the user request and regulatory context.
Return only valid JSON with this shape:
{{"extracted_requirements": [{{"req_id": "FR-AA-001", "title": "", "description": "", "category": "Functional", "priority": "Must Have", "citation": "[Document | Location]", "acceptance_criteria": ["Given ... When ... Then ..."]}}]}}

Target scale: {scale}
Regulatory context:
{context}

User request:
{user_query}"""
        try:
            return self.ask_json(prompt, generation_options)
        except (ValueError, json.JSONDecodeError):
            return {
                "extracted_requirements": [
                    {
                        "req_id": "REQ-001",
                        "title": "Requirement overview",
                        "description": user_query,
                        "category": "Functional",
                        "priority": "Must Have",
                        "citation": "General Context",
                        "acceptance_criteria": ["Given the requirement, When implemented, Then it is testable."],
                    }
                ]
            }