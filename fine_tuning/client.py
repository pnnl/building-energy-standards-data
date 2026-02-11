import json
import re
from typing import Optional, Type

import requests
from enum import StrEnum


class LLMClient:
    """Handles LLM API calls."""

    def __init__(
        self,
        url: str = "http://rc-chat.pnl.gov:11434/v1/completions",
        model: str = "llama3.3:70b",
        top_p: float = 0.9,
    ):
        self.url = url
        self.model = model
        self.top_p = top_p

    def generate(self, prompt: str) -> str:
        payload = {
            "model": self.model,
            "prompt": prompt,
            "top_p": self.top_p,
        }
        headers = {"Content-Type": "application/json"}

        response = requests.post(self.url, json=payload, headers=headers)
        response.raise_for_status()

        data = response.json()
        return data["choices"][0]["text"].strip()

    @staticmethod
    def extract_json_from_text(text: str) -> Optional[dict]:
        """Extract first JSON object from text."""
        match = re.search(r"\{.*?\}", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                return None
        return None


# Module-level default client for convenience
_default_client: Optional[LLMClient] = None


def get_default_client() -> LLMClient:
    global _default_client
    if _default_client is None:
        _default_client = LLMClient()
    return _default_client


def generate(prompt: str) -> str:
    """Convenience function using default client."""
    return get_default_client().generate(prompt)