import json
import re
from typing import Any

from .base import AgentBase


class SDLCSelectionAgent(AgentBase):
    def run(
        self,
        requirements: list[dict[str, Any]],
        scale: str,
        generation_options: dict[str, Any],
    ) -> dict[str, Any]:
        factors = self._derive_factors(requirements, scale)
        prompt = f"""You are a senior software architect for regulated banking systems.
Evaluate the actual requirements and rank these approaches from most to least suitable:
Agile, DevSecOps, Agile-V-Model Hybrid, V-Model, Spiral, Waterfall. Choose the ranking
and suitability scores yourself; no preset or deterministic ranking is authoritative.
Explain every model's position with a non-empty, project-specific justification grounded
in the requirements and derived factors. Weigh adaptability, early usable features,
frequent market feedback, changing eligibility rules and partners, and regular releases.
Do not treat regulatory importance by itself as a reason to put V-Model first: Agile can
meet regulatory needs through traceability, review, testing, and approval gates within
short iterations. For these requirements, Agile is a strong candidate for the top rank;
compare it fairly with DevSecOps and Agile-V-Model Hybrid and explain the tradeoffs.
Then provide tailored workflow phases, roles, deliverables, validation gates, security
controls, compliance checkpoints, and human approval checkpoints.
Keep the JSON compact so it completes within the generation limit: include all six
models with one or two concise justification sentences each, at most three workflow
phases with concise lists, and only the most relevant approval checkpoints. Do not
omit closing brackets or fields to fit the limit.
Return only valid JSON:
{{"derived_factors": {json.dumps(factors)}, "sdlc_recommendation": {{"ranked_scores": [{{"model_name": "", "suitability_percentage": 0, "justification": "Explain the fit to the derived factors"}}], "custom_workflow_phases": [], "approval_checkpoints": []}}}}
Do not add a separate primary, preferred, or selected model field. The downstream
documentation agent will explain the top-ranked model.

Target scale: {scale}
Derived factors:
{json.dumps(factors, indent=2)}
Requirements:
{json.dumps(requirements, indent=2)}"""
        try:
            result = self.ask_json(prompt, generation_options)
        except json.JSONDecodeError as exc:
            raise ValueError(
                "SDLC model returned incomplete or invalid JSON. Its response may have "
                "reached max_new_tokens before finishing; increase the token limit or "
                "reduce the requested output size. No ranking or justification fallback was applied."
            ) from exc
        recommendation = result.get("sdlc_recommendation")
        if not isinstance(recommendation, dict):
            raise ValueError("SDLC response is missing sdlc_recommendation")
        ranked_scores = recommendation.get("ranked_scores")
        if not isinstance(ranked_scores, list) or not ranked_scores:
            raise ValueError("SDLC response is missing ranked_scores")
        for item in ranked_scores:
            if not isinstance(item, dict) or not str(item.get("justification", "")).strip():
                raise ValueError("SDLC response must include a non-empty justification for every ranked model")
        result["derived_factors"] = {**factors, **result.get("derived_factors", {})}
        recommendation.pop("primary_recommendation", None)
        recommendation.setdefault("approval_checkpoints", self._approval_checkpoints(factors))
        return result

    @staticmethod
    def _derive_factors(requirements: list[dict[str, Any]], scale: str) -> dict[str, Any]:
        text = " ".join(json.dumps(item).lower() for item in requirements)
        count = len(requirements)
        has = lambda *terms: any(term in text for term in terms)
        regulatory = "High" if has("regulation", "compliance", "rbi", "audit") else "Medium"
        security = "High" if has("security", "privacy", "consent", "risk", "authentication") else "Medium"
        complexity = "High" if count >= 8 or has("integration", "legacy", "distributed", "microservice") else "Medium"
        return {
            "requirement_stability": "Low" if has("change frequently", "frequently", "evolving", "evolve", "may change", "uncertain") else "High",
            "regulatory_criticality": regulatory,
            "security_risk": security,
            "project_complexity": complexity,
            "system_size": scale,
            "legacy_system_dependence": "High" if has("legacy", "mainframe", "existing system") else "Low",
            "frequency_of_expected_changes": "High" if has("frequent", "continuous", "iterative") else "Medium",
            "need_for_continuous_delivery": "High" if has("continuous delivery", "deploy", "release") else "Medium",
            "stakeholder_availability": "Low" if has("limited stakeholder", "unavailable") else "Medium",
            "testing_and_documentation_requirements": "High" if has("test", "documentation", "traceability") else "Medium",
            "budget_and_schedule_constraints": "High" if has("budget", "deadline", "schedule") else "Medium",
            "need_for_formal_verification": "High" if has("formal verification", "validation", "proof") else "Medium",
            "consequences_of_system_failure": "High" if has("critical", "financial", "failure", "availability") else "Medium",
        }

    @staticmethod
    def _approval_checkpoints(factors: dict[str, Any]) -> list[str]:
        checkpoints = ["Requirements baseline and evidence approved", "Security and privacy threat assessment approved"]
        if factors["regulatory_criticality"] == "High":
            checkpoints.append("Regulatory mapping and compliance test plan approved")
        if factors["need_for_formal_verification"] == "High":
            checkpoints.append("Verification and validation evidence approved before release")
        return checkpoints
