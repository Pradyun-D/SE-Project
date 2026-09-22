from typing import Any


class DocumentationAgent:
    def generate_srs_markdown(
        self,
        user_query: str,
        scale: str,
        requirements: list[dict[str, Any]],
        quality: dict[str, Any],
        sdlc: dict[str, Any],
    ) -> str:
        recommendation = sdlc.get("primary_recommendation", "DevSecOps")
        requirement_sections = []
        for item in requirements:
            criteria = "\n".join(f"- {criterion}" for criterion in item.get("acceptance_criteria", []))
            requirement_sections.append(
                f"### {item.get('req_id', 'REQ')} - {item.get('title', 'Requirement')}\n"
                f"- Category: {item.get('category', 'Functional')}\n"
                f"- Priority: {item.get('priority', 'Must Have')}\n"
                f"- Citation: {item.get('citation', 'N/A')}\n"
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
{scores}

## Workflow Phases
{phases}

## Approval Checklist
- Requirements baseline reviewed
- Regulatory citations verified
- Security gates approved
"""

    @staticmethod
    def _format_phase(item: Any) -> str:
        if isinstance(item, str):
            return f"- {item}"
        return (
            f"- {item.get('phase_name', item.get('name', 'Phase'))}: "
            f"{item.get('key_activities', item.get('activities', ''))}; "
            f"Gate: {item.get('compliance_checkpoints', item.get('gate', ''))}"
        )

    @staticmethod
    def _format_score(item: Any) -> str:
        if not isinstance(item, dict):
            return f"- {item}"
        name = item.get("model_name", item.get("model", item.get("factor", "Model")))
        score = item.get("suitability_percentage", item.get("score", 0))
        rationale = item.get("justification", item.get("rationale", ""))
        return f"- {name}: {score}% - {rationale}"