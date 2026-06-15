"""LLM client interface for the reviewer.

The reviewer talks to a model through this small interface so the serving method is
pluggable (and so tests inject a mock instead of calling a live model). Our reviewer
runs on **Gemma**; the default real client drives a local Ollama server.
"""

from __future__ import annotations

import abc
import json
import os
from typing import Any


class LLMClient(abc.ABC):
    """Minimal contract: turn a (system, user) prompt pair into a JSON object.

    `name` is recorded into the review's `model` field, mirroring clawRxiv's `model`.
    """

    name: str

    @abc.abstractmethod
    def complete_json(self, system: str, user: str) -> dict[str, Any]:
        """Return the model's response parsed as a JSON object."""
        raise NotImplementedError


class MockLLMClient(LLMClient):
    """Test double. Returns a fixed response and records the last prompts so tests can
    assert on prompt content (e.g. that the current date and the recent-papers
    instruction are present)."""

    def __init__(self, response: dict[str, Any] | list[dict[str, Any]],
                 name: str = "mock-model") -> None:
        self._responses = list(response) if isinstance(response, list) else [response]
        self.name = name
        self.calls = 0
        self.last_system: str | None = None
        self.last_user: str | None = None

    def complete_json(self, system: str, user: str) -> dict[str, Any]:
        self.last_system = system
        self.last_user = user
        item = self._responses[min(self.calls, len(self._responses) - 1)]
        self.calls += 1
        return json.loads(json.dumps(item))  # deep copy


class OllamaGemmaClient(LLMClient):
    """Drives a local Ollama server running Gemma. Model tag and host are configurable
    via `CLAWRXIV_REVIEW_MODEL` (default `gemma3:12b`) and `OLLAMA_HOST`
    (default `http://localhost:11434`). Not exercised in CI (no live model there)."""

    def __init__(self, model: str | None = None, host: str | None = None) -> None:
        self.name = model or os.environ.get("CLAWRXIV_REVIEW_MODEL", "gemma3:12b")
        self.host = (host or os.environ.get("OLLAMA_HOST", "http://localhost:11434")).rstrip("/")

    def complete_json(self, system: str, user: str) -> dict[str, Any]:
        import httpx  # imported lazily so the package imports without a live model

        resp = httpx.post(
            f"{self.host}/api/chat",
            json={
                "model": self.name,
                "stream": False,
                "format": "json",  # Ollama constrains output to valid JSON
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
            },
            timeout=180,
        )
        resp.raise_for_status()
        return json.loads(resp.json()["message"]["content"])
