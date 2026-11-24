import json
from typing import Any

from .base import AgentBase
from schemas import SDLCResult


class SDLCSelectionAgent(AgentBase):
    def run(
        self,
        requirements: list[dict[str, Any]],
        scale: str,
        generation_options: dict[str, Any],
    ) -> dict[str, Any]:
        prompt = f"""You are a senior software architect for regulated banking systems.
Evaluate the requirements and recommend an SDLC approach. Consider Agile, DevSecOps,
Agile-V-Model Hybrid, V-Model, Spiral, Waterfall, and other justified hybrid models.
Derive the decision from requirement stability, regulatory criticality, security risk,
project complexity, system size, legacy-system dependence, expected change frequency,
need for continuous delivery, stakeholder availability, testing/documentation burden,
budget/schedule constraints, need for formal verification, and consequences of failure.

For every considered model, provide a suitability score, rationale, strengths, limitations,
and risks. For the selected model, provide a project-specific workflow with ordered
phases; activities; responsible roles; inputs and outputs; deliverables; security and
privacy controls; regulatory/compliance checkpoints; validation and testing gates;
deployment/release gates; and human approval checkpoints. Do not return a generic SDLC
definition. Make the recommendation and ranking yourself.
Return only valid JSON:
{{"derived_factors": {{}}, "sdlc_recommendation": {{"primary_recommendation": "", "decision_rationale": "", "ranked_scores": [{{"model_name": "", "suitability_percentage": 0, "rationale": "", "strengths": [], "limitations": [], "risks": []}}], "custom_workflow_phases": [{{"phase_name": "", "sequence": 1, "objective": "", "activities": [], "roles": [], "inputs": [], "deliverables": [], "security_controls": [], "compliance_checkpoints": [], "validation_gates": [], "human_approval_checkpoint": ""}}], "approval_checkpoints": []}}}}

Target scale: {scale}
Requirements:
{json.dumps(requirements, indent=2)}"""
        try:
            result = self.ask_json(prompt, generation_options)
            return SDLCResult.model_validate(result).model_dump()
        except (ValueError, json.JSONDecodeError):
            factors = self._derive_fallback_factors(requirements, scale)
            return SDLCResult(
                derived_factors=factors,
                sdlc_recommendation={
                    "primary_recommendation": "Agile-V-Model Hybrid",
                    "decision_rationale": "Fallback recommendation based on regulatory and verification needs.",
                    "ranked_scores": [
                        {
                            "model_name": "Agile-V-Model Hybrid",
                            "suitability_percentage": 85,
                            "rationale": "Combines iterative delivery with formal verification and compliance gates.",
                        },
                        {
                            "model_name": "DevSecOps",
                            "suitability_percentage": 78,
                            "rationale": "Strong continuous security and delivery controls.",
                        },
                        {
                            "model_name": "V-Model",
                            "suitability_percentage": 74,
                            "rationale": "Strong traceability and verification discipline.",
                        },
                    ],
                    "custom_workflow_phases": [],
                    "approval_checkpoints": [
                        "Requirements baseline and evidence approved",
                        "Security and privacy assessment approved",
                        "Compliance validation approved before release",
                    ],
                },
            ).model_dump()

    @staticmethod
    def _derive_fallback_factors(requirements: list[dict[str, Any]], scale: str) -> dict[str, Any]:
        text = json.dumps(requirements).lower()
        return {
            "requirement_stability": "High" if "change" not in text else "Low",
            "regulatory_criticality": "High" if any(term in text for term in ("regulation", "compliance", "audit")) else "Medium",
            "security_risk": "High" if any(term in text for term in ("security", "privacy", "consent")) else "Medium",
            "project_complexity": "High" if len(requirements) >= 6 else "Medium",
            "system_size": scale,
            "legacy_system_dependence": "High" if "legacy" in text else "Low",
        }