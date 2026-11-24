import json
from typing import Any, Callable

from .base import AgentBase


class RequirementExtractionAgent(AgentBase):
    def __init__(self, generate: Callable[..., str], rag_tool=None):
        super().__init__(generate)
        self.rag_tool = rag_tool

    def run(
        self,
        user_query: str,
        scale: str,
        use_rag: bool,
        generation_options: dict[str, Any],
    ) -> dict[str, Any]:
        tool_result = {"retrieved_context": [], "context_str": ""}
        if use_rag and self.rag_tool is not None:
            tool_result = self.rag_tool.run(user_query)
        context = tool_result["context_str"]
        prompt = f"""You are a Principal FinTech Product Manager and RBI/ReBIT Compliance Architect.
    Analyse the request and regulatory context as a requirements engineer, not as a summariser.
    Extract actionable functional and non-functional requirements. Detect incomplete,
    ambiguous, duplicated, or conflicting statements before finalising the list. Treat
    customer, business, compliance, security, regulator, policy, and legacy-system concerns
    as separate stakeholder perspectives and preserve their evidence.

    Classify every requirement across business, technical, security, privacy, compliance,
    performance, availability, auditability, and operational dimensions. For each item,
    identify applicable financial regulations, organisational policies, risk controls,
    legacy-system constraints, source evidence, a human approval checkpoint, user stories,
    use-case actors and flows, and testable acceptance criteria. Include traceability from
    each requirement to its source evidence, stakeholder concern, control, and acceptance test.

    Do not invent a citation. Use "Not identified" when evidence is unavailable. Keep
    requirements atomic and uniquely numbered. Use explicit assumptions only when marked as
    assumptions. Return clarification questions for information that cannot safely be assumed.
Return only valid JSON with this shape:
    {{"analysis_summary": "", "assumptions": [], "conflicts": [{{"items": [], "description": "", "resolution_needed": ""}}], "clarification_questions": [], "extracted_requirements": [{{"req_id": "FR-AA-001", "title": "", "description": "", "category": "Functional", "priority": "Must Have", "dimensions": ["business", "technical"], "regulations": [], "organisational_policies": [], "risk_controls": [], "legacy_constraints": [], "evidence": ["[Document | Location]"], "citation": "[Document | Location]", "stakeholders": [], "user_story": "As a ... I want ... so that ...", "use_case": {{"actors": [], "preconditions": [], "main_flow": [], "alternate_flows": [], "postconditions": []}}, "traceability": [{{"source": "", "stakeholder": "", "control": "", "acceptance_test": ""}}], "human_approval_checkpoint": "", "acceptance_criteria": ["Given ... When ... Then ..."]}}]}}

Target scale: {scale}
Regulatory context:
{context}

User request:
{user_query}"""
        try:
            result = self.ask_json(prompt, generation_options)
        except (ValueError, json.JSONDecodeError):
            result = {
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
        return {**tool_result, **result}
