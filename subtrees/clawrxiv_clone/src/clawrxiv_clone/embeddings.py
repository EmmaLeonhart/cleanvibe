"""Embeddings for semantic search (clawRxiv's GET /api/search/similar).

An `EmbedClient` turns text into a vector; the default drives a local Ollama embed model.
Tests inject `MockEmbedClient`, which maps text to a deterministic keyword vector so similar
papers cluster without a live model.
"""

from __future__ import annotations

import abc
import math
import os


def embed_text(title: str, abstract: str) -> str:
    """Canonical text used to embed a post."""
    return f"{title}\n{abstract}"


def cosine(a: list[float], b: list[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if na == 0.0 or nb == 0.0:
        return 0.0
    return dot / (na * nb)


class EmbedClient(abc.ABC):
    name: str

    @abc.abstractmethod
    def embed(self, text: str) -> list[float]:
        raise NotImplementedError


class MockEmbedClient(EmbedClient):
    """Deterministic keyword vector: one dimension per keyword, 1.0 if present else 0.0.
    Lets tests make similar papers cluster without a model."""

    def __init__(self, keywords: list[str], name: str = "mock-embed") -> None:
        self.keywords = [k.lower() for k in keywords]
        self.name = name

    def embed(self, text: str) -> list[float]:
        t = text.lower()
        return [1.0 if k in t else 0.0 for k in self.keywords]


class OllamaEmbedClient(EmbedClient):
    """Drives a local Ollama embed model. Configurable via `CLAWRXIV_EMBED_MODEL`
    (default `nomic-embed-text`) and `OLLAMA_HOST`. Not exercised in CI."""

    def __init__(self, model: str | None = None, host: str | None = None) -> None:
        self.name = model or os.environ.get("CLAWRXIV_EMBED_MODEL", "nomic-embed-text")
        self.host = (host or os.environ.get("OLLAMA_HOST", "http://localhost:11434")).rstrip("/")

    def embed(self, text: str) -> list[float]:
        import httpx

        resp = httpx.post(
            f"{self.host}/api/embeddings",
            json={"model": self.name, "prompt": text},
            timeout=60,
        )
        resp.raise_for_status()
        return resp.json()["embedding"]
