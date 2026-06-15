"""Reviewer tests. The LLM is always mocked — no live model in CI."""

import json
import pathlib

import pytest

from clawrxiv_clone.llm import MockLLMClient
from clawrxiv_clone.reviewer import RATING_TIERS, ReviewError, generate_review
from clawrxiv_clone.schema import Paper, Rating, Review

SAMPLES = pathlib.Path(__file__).resolve().parents[1] / "investigation" / "samples"


def _mock_response() -> dict:
    return {
        "rating": "Weak Accept",
        "summary": "A study of the thing.",
        "pros": ["p1", "p2", "p3", "p4", "p5"],
        "cons": ["c1", "c2", "c3", "c4", "c5"],
        "justification": "On balance the strengths edge out the weaknesses.",
    }


def test_generate_review_returns_valid_review():
    llm = MockLLMClient(_mock_response(), name="gemma3")
    review = generate_review(Paper(title="T", abstract="A", content="body"), llm,
                             now="2026-06-14 12:00:00")
    assert isinstance(review, Review)
    assert review.rating is Rating.WEAK_ACCEPT
    assert len(review.pros) == 5 and len(review.cons) == 5
    assert review.model == "gemma3"  # stamped from llm.name when the model omits it
    assert review.createdAt == "2026-06-14 12:00:00"


def test_prompt_carries_paper_and_recent_work_policy():
    llm = MockLLMClient(_mock_response())
    generate_review(Paper(title="My Title", abstract="My Abstract", content="Body text"),
                    llm, now="2026-06-14 12:00:00")
    sys = llm.last_system.lower()
    # the recent-papers fix the user asked for:
    assert "2026-06-14" in llm.last_system          # current date injected
    assert "hallucinat" in sys                       # the policy is about hallucination
    assert "after your cutoff" in sys                # post-cutoff sources are real
    # the paper itself reaches the model:
    assert "My Title" in llm.last_user and "My Abstract" in llm.last_user


def test_review_model_accepts_live_clawrxiv_sample():
    """Our Review schema must accept the real clawRxiv review payload shape."""
    sample = json.loads((SAMPLES / "review_2604.00100.json").read_text(encoding="utf-8"))["review"]
    assert {"rating", "summary", "pros", "cons", "justification", "model",
            "createdAt"}.issubset(sample)
    review = Review(rating=sample["rating"], summary=sample["summary"], pros=sample["pros"],
                    cons=sample["cons"], justification=sample["justification"],
                    model=sample["model"], createdAt=sample["createdAt"])
    assert review.rating.value == sample["rating"]
    assert review.model == "Gemini 3 Flash"  # what the live sample recorded


def test_rating_ladder():
    for tier in ("Strong Reject", "Reject", "Weak Reject", "Weak Accept", "Accept", "Strong Accept"):
        assert tier in RATING_TIERS


_BAD = {"summary": "missing required fields"}  # no rating/pros/cons/justification


def test_retry_on_malformed_then_valid():
    llm = MockLLMClient([_BAD, _mock_response()], name="gemma3")
    review = generate_review(Paper(title="T", abstract="A"), llm, now="2026-06-14 12:00:00")
    assert review.rating is Rating.WEAK_ACCEPT
    assert llm.calls == 2  # one bad attempt, one good
    assert "previous response was not a valid review" in llm.last_user.lower()


def test_all_malformed_raises_review_error():
    llm = MockLLMClient([_BAD, _BAD], name="gemma3")
    with pytest.raises(ReviewError):
        generate_review(Paper(title="T", abstract="A"), llm, now="2026-06-14 12:00:00")
    assert llm.calls == 2  # exhausted max_attempts
