"""Live Gemma integration test. Skipped unless CLAWRXIV_LIVE=1 (needs local Ollama);
CI never runs it."""

import os

import pytest

from clawrxiv_clone.llm import OllamaGemmaClient
from clawrxiv_clone.reviewer import generate_review
from clawrxiv_clone.schema import Paper, Review

pytestmark = pytest.mark.skipif(
    not os.environ.get("CLAWRXIV_LIVE"),
    reason="set CLAWRXIV_LIVE=1 to run the live Gemma review (needs local Ollama)",
)


def test_live_gemma_review_validates():
    paper = Paper(
        title="A Tiny Stateful-Attention Note",
        abstract="We add a fixed reservoir to attention so state is carried across passes. "
                 "Cites a 2026 work (arXiv:2508.18130).",
        content="Inject a reservoir at a mid layer; read it back as a content-addressable KV prefix.",
    )
    review = generate_review(paper, OllamaGemmaClient())
    assert isinstance(review, Review)
    assert review.model.startswith("gemma")
    assert review.pros and review.cons and review.summary
