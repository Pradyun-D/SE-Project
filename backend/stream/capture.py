import re
from pathlib import Path
from typing import Any


class FileStreamingGenerator:
    def __init__(self, stream_dir: str, response_dir: str):
        self.stream_dir = Path(stream_dir)
        self.response_dir = Path(response_dir)
        self.stream_dir.mkdir(parents=True, exist_ok=True)
        self.path = self._next_path()
        self.file = self.path.open("w", encoding="utf-8")
        self.stage = 0

    def __call__(self, prompt: str, **generation_options: Any) -> str:
        self.stage += 1
        self.file.write(f"\n\n--- MODEL STAGE {self.stage} ---\n")
        self.file.flush()
        response: list[str] = []
        try:
            from config import get_settings
            from model_client import GeminiModelClient

            settings = get_settings()
            client = GeminiModelClient(
                settings.gemini_api_key,
                settings.gemini_generation_model,
                settings.gemini_embedding_model,
                settings.gemini_embedding_dimensions,
                settings.model_timeout_seconds,
                settings.model_retry_count,
            )
            for token in client.generate_stream(prompt, **generation_options):
                response.append(token)
                self.file.write(token)
                self.file.flush()
        except Exception:
            self.file.write("\n[Streaming stage failed]\n")
            self.file.flush()
            raise
        return "".join(response)

    def close(self) -> None:
        if not self.file.closed:
            self.file.flush()
            self.file.close()

    def save_response(self, text: str) -> Path:
        self.response_dir.mkdir(parents=True, exist_ok=True)
        numbers = [
            int(match.group(1))
            for path in self.response_dir.glob("response_*.md")
            if (match := re.fullmatch(r"response_(\d+)\.md", path.name))
        ]
        path = self.response_dir / f"response_{max(numbers, default=0) + 1:03d}.md"
        cleaned = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()
        path.write_text(cleaned + "\n", encoding="utf-8")
        return path

    def _next_path(self) -> Path:
        numbers = [
            int(match.group(1))
            for path in self.stream_dir.glob("stream_*.log")
            if (match := re.fullmatch(r"stream_(\d+)\.log", path.name))
        ]
        return self.stream_dir / f"stream_{max(numbers, default=0) + 1:03d}.log"
