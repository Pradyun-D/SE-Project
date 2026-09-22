import json
from typing import Any

from .base import AgentBase


class SDLCSelectionAgent(AgentBase):
    def run(
        self,
        requirements: list[dict[str, Any]],
        scale: str,
        generation_options: dict[str, Any],
    ) -> dict[str, Any]:
        prompt = f"""You are a senior software architect for regulated banking systems.
Evaluate the requirements and recommend an SDLC approach. Consider DevSecOps, Agile-V-Model Hybrid, V-Model, Spiral, and Waterfall.
Return only valid JSON:
{{"derived_factors": {{"volatility": "Medium", "regulatory_criticality": "High", "security_risk": "High"}}, "sdlc_recommendation": {{"primary_recommendation": "DevSecOps", "ranked_scores": [], "custom_workflow_phases": []}}}}

Target scale: {scale}
Requirements:
{json.dumps(requirements, indent=2)}"""
        try:
            return self.ask_json(prompt, generation_options)
        except (ValueError, json.JSONDecodeError):
            return {
                "derived_factors": {
                    "volatility": "Medium",
                    "regulatory_criticality": "High",
                    "security_risk": "High",
                },
                "sdlc_recommendation": {
                    "primary_recommendation": "DevSecOps",
                    "ranked_scores": [],
                    "custom_workflow_phases": [],
                },
            }