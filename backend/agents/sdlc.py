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
        deterministic_scores = self._rank_models(factors)
        prompt = f"""You are a senior software architect for regulated banking systems.
Evaluate the requirements and recommend an SDLC approach. Consider Agile, DevSecOps,
Agile-V-Model Hybrid, V-Model, Spiral, Waterfall, and hybrid models. Use the derived
factors and deterministic ranking below, then provide project-specific explanations,
workflow phases, roles, deliverables, validation gates, security controls, compliance
checkpoints, and human approval checkpoints.
Return only valid JSON:
{{"derived_factors": {json.dumps(factors)}, "sdlc_recommendation": {{"primary_recommendation": "", "ranked_scores": [], "custom_workflow_phases": [], "approval_checkpoints": []}}}}

Target scale: {scale}
Deterministic ranked baseline:
{json.dumps(deterministic_scores, indent=2)}
Requirements:
{json.dumps(requirements, indent=2)}"""
        try:
            result = self.ask_json(prompt, generation_options)
            recommendation = result.setdefault("sdlc_recommendation", {})
            result["derived_factors"] = {**factors, **result.get("derived_factors", {})}
            llm_scores = {
                item.get("model_name", item.get("model")): item.get("justification", item.get("rationale", ""))
                for item in recommendation.get("ranked_scores", [])
                if isinstance(item, dict)
            }
            recommendation["ranked_scores"] = [
                {**item, "justification": llm_scores.get(item["model_name"], item["justification"])}
                for item in deterministic_scores
            ]
            recommendation["primary_recommendation"] = deterministic_scores[0]["model_name"]
            recommendation.setdefault("approval_checkpoints", self._approval_checkpoints(factors))
            return result
        except (ValueError, json.JSONDecodeError):
            return {
                "derived_factors": factors,
                "sdlc_recommendation": {
                    "primary_recommendation": deterministic_scores[0]["model_name"],
                    "ranked_scores": deterministic_scores,
                    "custom_workflow_phases": [],
                    "approval_checkpoints": self._approval_checkpoints(factors),
                },
            }

    @staticmethod
    def _derive_factors(requirements: list[dict[str, Any]], scale: str) -> dict[str, Any]:
        text = " ".join(json.dumps(item).lower() for item in requirements)
        count = len(requirements)
        has = lambda *terms: any(term in text for term in terms)
        regulatory = "High" if has("regulation", "compliance", "rbi", "audit") else "Medium"
        security = "High" if has("security", "privacy", "consent", "risk", "authentication") else "Medium"
        complexity = "High" if count >= 8 or has("integration", "legacy", "distributed", "microservice") else "Medium"
        return {
            "requirement_stability": "Low" if has("change frequently", "evolving", "uncertain") else "High",
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
    def _rank_models(factors: dict[str, Any]) -> list[dict[str, Any]]:
        score = {"Agile": 50, "DevSecOps": 50, "Agile-V-Model Hybrid": 50, "V-Model": 50, "Spiral": 50, "Waterfall": 50}
        if factors["requirement_stability"] == "High": score["Waterfall"] += 20; score["V-Model"] += 15
        else: score["Agile"] += 20; score["DevSecOps"] += 15
        if factors["regulatory_criticality"] == "High": score["V-Model"] += 18; score["Agile-V-Model Hybrid"] += 20
        if factors["security_risk"] == "High": score["DevSecOps"] += 20; score["Spiral"] += 12
        if factors["project_complexity"] == "High": score["Spiral"] += 18
        if factors["need_for_continuous_delivery"] == "High": score["DevSecOps"] += 22
        if factors["need_for_formal_verification"] == "High": score["V-Model"] += 22; score["Agile-V-Model Hybrid"] += 15
        if factors["consequences_of_system_failure"] == "High": score["V-Model"] += 12; score["Spiral"] += 10
        ranked = sorted(score.items(), key=lambda item: item[1], reverse=True)
        return [{"model_name": name, "suitability_percentage": min(value, 99), "justification": "Deterministic factor-based baseline"} for name, value in ranked]

    @staticmethod
    def _approval_checkpoints(factors: dict[str, Any]) -> list[str]:
        checkpoints = ["Requirements baseline and evidence approved", "Security and privacy threat assessment approved"]
        if factors["regulatory_criticality"] == "High":
            checkpoints.append("Regulatory mapping and compliance test plan approved")
        if factors["need_for_formal_verification"] == "High":
            checkpoints.append("Verification and validation evidence approved before release")
        return checkpoints