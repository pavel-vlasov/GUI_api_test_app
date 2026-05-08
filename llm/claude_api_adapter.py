"""Direct Claude API adapter with CLI-compatible interface."""
from __future__ import annotations

import json
from typing import Callable, List

import requests


class ClaudeApiAdapter:
    """HTTP adapter that returns commands with same contract as CLI adapter."""

    def __init__(self, api_url: str, api_key: str, model: str) -> None:
        """Initialize Claude API adapter."""

        self.api_url = api_url
        self.api_key = api_key
        self.model = model

    def generate_commands(self, prompt: str, on_stream: Callable[[str], None] | None = None) -> List[str]:
        """Generate curl command batch from Claude API response."""

        response = requests.post(
            self.api_url,
            json={"model": self.model, "messages": [{"role": "user", "content": prompt}]},
            headers={"x-api-key": self.api_key, "content-type": "application/json"},
            timeout=45,
        )
        response.raise_for_status()
        payload = response.json()
        text = payload.get("content", "[]") if isinstance(payload, dict) else "[]"
        if on_stream:
            on_stream(str(text))
        parsed = json.loads(text if isinstance(text, str) else json.dumps(text))
        return [item["command"] if isinstance(item, dict) else item for item in parsed]
