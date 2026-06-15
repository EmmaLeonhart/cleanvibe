"""Production app factory: wires the real Gemma + embed clients and a file-backed DB,
so the subsystems auto-run on publish/revise.

Run:  PYTHONPATH=src uvicorn clawrxiv_clone.server:production_app --factory
Env:  CLAWRXIV_DB (default clawrxiv.db), CLAWRXIV_REVIEW_MODEL (default gemma3:12b),
      CLAWRXIV_EMBED_MODEL (default nomic-embed-text), OLLAMA_HOST.
"""

from __future__ import annotations

import os

from fastapi import FastAPI

from .api import create_app
from .embeddings import OllamaEmbedClient
from .llm import OllamaGemmaClient


def production_app() -> FastAPI:
    return create_app(
        llm=OllamaGemmaClient(),
        classify_llm=OllamaGemmaClient(),
        equivalence_llm=OllamaGemmaClient(),
        embedder=OllamaEmbedClient(),
        db_path=os.environ.get("CLAWRXIV_DB", "clawrxiv.db"),
    )
