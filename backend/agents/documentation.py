import json
import re
from typing import Any, Callable


class DocumentationAgent:
    def __init__(self, generate: Callable[..., str] | None = None):
        self.generate = generate

    def generate_srs_markdown(
        self,
        user_query: str,
        scale: str,
        requirements: list[dict[str, Any]],
        quality: dict[str, Any],
        sdlc: dict[str, Any],
        generation_options: dict[str, Any] | None = None,
    ) -> str:
        if self.generate is not None:
            prompt = f"""You are the documentation architect for a regulated FinTech project.
Write the final Software Requirements Specification as polished Markdown.

Do not return JSON. Do not discuss this prompt. Use the supplied analysis as source
material, but choose a natural document structure and readable prose yourself.
Preserve citations and evidence exactly where provided. Do not invent regulations,
requirements, scores, or approvals. The deterministic SDLC ranking is authoritative;
explain it rather than changing it. Include requirements, quality gaps, derived SDLC
factors, ranked recommendations, workflow phases, controls, deliverables, validation
gates, compliance checkpoints, and human approval checkpoints where the data supports them.

Initial request:
{user_query}

Organization scale: {scale}

Extracted requirement analysis:
{json.dumps(requirements, indent=2)}

Quality analysis:
{json.dumps(quality, indent=2)}

SDLC analysis:
{json.dumps(sdlc, indent=2)}
"""
            try:
                rendered = self.generate(prompt, **(generation_options or {}))
                rendered = re.sub(r"<think>.*?</think>", "", rendered, flags=re.DOTALL).strip()
                if rendered.startswith("```") and rendered.endswith("```"):
                    rendered = rendered.split("\n", 1)[1].rsplit("```", 1)[0].strip()
                if rendered:
                    return rendered
            except Exception:
                pass

        recommendation = sdlc.get("primary_recommendation", "DevSecOps")
        requirement_sections = []
        for item in requirements:
            criteria = "\n".join(f"- {criterion}" for criterion in item.get("acceptance_criteria", []))
            requirement_sections.append(
                f"### {item.get('req_id', 'REQ')} - {item.get('title', 'Requirement')}\n"
                f"- Category: {item.get('category', 'Functional')}\n"
                f"- Priority: {item.get('priority', 'Must Have')}\n"
                f"- Citation: {item.get('citation', 'N/A')}\n"
                f"- Dimensions: {', '.join(item.get('dimensions', []))}\n"
                f"- Regulations and policies: {', '.join(item.get('regulations', []) + item.get('organisational_policies', [])) or 'To be confirmed'}\n"
                f"- Risk controls: {', '.join(item.get('risk_controls', [])) or 'To be confirmed'}\n"
                f"- Evidence: {', '.join(item.get('evidence', [])) or item.get('citation', 'N/A')}\n"
                f"- Human approval checkpoint: {item.get('human_approval_checkpoint', 'Requirements review')}\n"
                f"- Description: {item.get('description', '')}\n"
                f"- Acceptance criteria:\n{criteria}"
            )
        gaps = "\n".join(f"- {gap}" for gap in quality.get("missing_aspects", [])) or "- None identified"
        scores = "\n".join(
            self._format_score(item)
            for item in sdlc.get("ranked_scores", [])
        ) or "- No ranked scores returned"
        phases = "\n".join(
            self._format_phase(item)
            for item in sdlc.get("custom_workflow_phases", [])
        ) or "- No custom phases returned"
        factors = "\n".join(
            f"- {name.replace('_', ' ').title()}: {value}"
            for name, value in sdlc.get("derived_factors", {}).items()
        ) or "- No derived factors returned"
        return f"""# Software Requirements Specification

## Executive Summary
- Initial request: {user_query}
- Target organization scale: {scale}
- Recommended SDLC: {recommendation}

## Classified Requirements

{chr(10).join(requirement_sections)}

## Quality Review
- Complete: {quality.get('is_complete', True)}
- Ambiguity score: {quality.get('ambiguity_score', 0)}
- Missing aspects:
{gaps}

## SDLC Evaluation
### Derived Decision Factors
{factors}

{scores}

## Workflow Phases
{phases}

## Approval Checklist
- Requirements baseline reviewed
- Regulatory citations verified
- Security gates approved
{chr(10).join(self._format_checkpoint(checkpoint) for checkpoint in sdlc.get('approval_checkpoints', []))}
"""

    @staticmethod
    def _format_phase(item: Any) -> str:
        if isinstance(item, str):
            return f"- {item}"
        name = item.get("phase_name", item.get("name", "Phase"))
        activities = item.get("key_activities", item.get("activities", []))
        roles = item.get("roles", [])
        deliverables = item.get("deliverables", [])
        gates = item.get("validation_gates", item.get("compliance_checkpoints", item.get("gate", [])))
        return (
            f"- {name}: Activities: {DocumentationAgent._format_list(activities)}; "
            f"Roles: {DocumentationAgent._format_list(roles)}; "
            f"Deliverables: {DocumentationAgent._format_list(deliverables)}; "
            f"Gates: {DocumentationAgent._format_list(gates)}"
        )

    @staticmethod
    def _format_list(value: Any) -> str:
        if isinstance(value, list):
            return ", ".join(str(item) for item in value) or "Not specified"
        return str(value) if value else "Not specified"

    @staticmethod
    def _format_checkpoint(checkpoint: Any) -> str:
        if isinstance(checkpoint, str):
            return f"- {checkpoint}"
        if isinstance(checkpoint, dict):
            name = checkpoint.get("checkpoint_name", checkpoint.get("name", "Approval checkpoint"))
            description = checkpoint.get("description", "")
            roles = DocumentationAgent._format_list(checkpoint.get("roles", []))
            approval_type = checkpoint.get("approval_type", "Formal review")
            return f"- {name}: {description} Roles: {roles}. Type: {approval_type}."
        return f"- {checkpoint}"

    @staticmethod
    def _format_score(item: Any) -> str:
        if not isinstance(item, dict):
            return f"- {item}"
        name = item.get("model_name", item.get("model", item.get("factor", "Model")))
        score = item.get("suitability_percentage", item.get("score", 0))
        rationale = item.get("justification", item.get("rationale", ""))
        return f"- {name}: {score}% - {rationale}"