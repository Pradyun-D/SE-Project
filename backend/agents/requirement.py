import json
import re
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
Classify every requirement across business, technical, security, privacy, compliance,
performance, availability, auditability, and operational dimensions. For each item,
identify applicable financial regulations, organisational policies, risk controls,
legacy-system constraints, source evidence, and a human approval checkpoint.
Return only valid JSON with this shape:
{{"extracted_requirements": [{{"req_id": "FR-AA-001", "title": "", "description": "", "category": "Functional", "priority": "Must Have", "dimensions": ["business", "technical"], "regulations": [], "organisational_policies": [], "risk_controls": [], "legacy_constraints": [], "evidence": ["[Document | Location]"], "citation": "[Document | Location]", "human_approval_checkpoint": "", "acceptance_criteria": ["Given ... When ... Then ..."]}}]}}

Target scale: {scale}
Return at most three distinct, high-priority actionable requirements. If the request
contains three or more, select the three most important; if it contains fewer, return
only those. Do not create a generic overview or invent requirements. Keep each item
concise: short title and description, one brief acceptance criterion, and short metadata.
Assign sequential IDs and return a non-empty array.
Regulatory context:
{context}

User request:
{user_query}"""
        # Use the caller's normal output budget. If it truncates the array, recover all
        # complete requirement objects emitted before the cutoff.
        response = self.generate(prompt, **generation_options)
        text = re.sub(r"<think>.*?</think>", "", response, flags=re.DOTALL).strip()
        if "```json" in text:
            text = text.split("```json", 1)[1].split("```", 1)[0].strip()
        elif "```" in text:
            text = text.split("```", 1)[1].split("```", 1)[0].strip()

        try:
            start = text.find("{")
            end = text.rfind("}")
            if start < 0 or end < start:
                raise ValueError("Model response did not contain a complete JSON object")
            result = json.loads(text[start : end + 1])
            if not isinstance(result, dict):
                raise ValueError("Model response JSON must be an object")
            requirements = result.get("extracted_requirements")
            if isinstance(requirements, list) and requirements:
                result["extracted_requirements"] = [
                    item for item in requirements
                    if isinstance(item, dict) and (item.get("title") or item.get("description"))
                ][:3]
                if result["extracted_requirements"]:
                    return result
        except (ValueError, json.JSONDecodeError):
            requirements = self._recover_complete_requirements(text)
            if requirements:
                return {"extracted_requirements": requirements[:3]}

        # If the model still returns malformed/truncated JSON, preserve the distinct
        # statements from the user's request instead of silently collapsing them.
        statements = [part.strip(" \t\r\n-\u2022") for part in re.split(r"(?<=[.!?])\s+|\n+", user_query) if part.strip(" \t\r\n-\u2022")][:3]
        return {
            "extracted_requirements": [
                {
                    "req_id": f"REQ-{index:03d}",
                    "title": (statement[:77].rsplit(" ", 1)[0] + "...") if len(statement) > 80 else statement,
                    "description": statement,
                    "category": "Functional",
                    "priority": "Must Have",
                    "citation": "General Context",
                    "acceptance_criteria": [f"Given the system, When it handles this requirement, Then it must: {statement}"],
                }
                for index, statement in enumerate(statements, start=1)
            ]
        }

    @staticmethod
    def _recover_complete_requirements(text: str) -> list[dict[str, Any]]:
        """Decode complete array objects even when generation stops mid-JSON."""
        match = re.search(r'"extracted_requirements"\s*:\s*\[', text)
        if not match:
            return []

        decoder = json.JSONDecoder()
        requirements: list[dict[str, Any]] = []
        position = match.end()
        while position < len(text):
            while position < len(text) and (text[position].isspace() or text[position] == ","):
                position += 1
            if position >= len(text) or text[position] == "]":
                break
            if text[position] != "{":
                break
            try:
                item, next_position = decoder.raw_decode(text, position)
            except json.JSONDecodeError:
                break
            if isinstance(item, dict) and (item.get("title") or item.get("description")):
                requirements.append(item)
            position = next_position
        return requirements
