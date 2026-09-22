import json
import re
from typing import Any, Callable


class AgentBase:
    def __init__(self, generate: Callable[..., str]):
        self.generate = generate

    def ask_json(self, prompt: str, generation_options: dict[str, Any]) -> dict[str, Any]:
        response = self.generate(prompt, **generation_options)
        text = re.sub(r"<think>.*?</think>", "", response, flags=re.DOTALL).strip()
        if "```json" in text:
            text = text.split("```json", 1)[1].split("```", 1)[0].strip()
        elif "```" in text:
            text = text.split("```", 1)[1].split("```", 1)[0].strip()
        start = text.find("{")
        end = text.rfind("}")
        if start == -1 or end == -1 or end < start:
            raise ValueError("Model response did not contain a JSON object")
        value = json.loads(text[start : end + 1])
        if not isinstance(value, dict):
            raise ValueError("Model response JSON must be an object")
        return value