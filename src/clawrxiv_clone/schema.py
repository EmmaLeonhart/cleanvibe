"""Pydantic models for papers and reviews.

The Review model mirrors the live clawRxiv `GET /api/posts/:id/review` response shape
(see investigation/FINDINGS.md and investigation/samples/review_*.json): a named-tier
`rating`, a one-paragraph `summary`, lists of `pros` and `cons`, a `justification`, the
`model` that wrote it, and a `createdAt` timestamp. `id`/`postId` are attached by the API
layer, not the reviewer.
"""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class Rating(str, Enum):
    """The review rating ladder. clawRxiv exposes named tiers (not a numeric score);
    we observed Reject / Weak Reject / Weak Accept / Accept and fill in the standard
    conference ladder around them."""

    STRONG_REJECT = "Strong Reject"
    REJECT = "Reject"
    WEAK_REJECT = "Weak Reject"
    BORDERLINE = "Borderline"
    WEAK_ACCEPT = "Weak Accept"
    ACCEPT = "Accept"
    STRONG_ACCEPT = "Strong Accept"


class Paper(BaseModel):
    """A submitted paper — the reviewer's input."""

    title: str
    abstract: str
    content: str = ""  # full markdown body
    tags: list[str] = Field(default_factory=list)


class Review(BaseModel):
    """An AI peer review, matching the clawRxiv review schema.

    clawRxiv returns exactly 5 pros and 5 cons; we accept 1..8 so a real model output
    is never rejected on a count mismatch (we never pad or trim to fake the count).
    """

    rating: Rating
    summary: str
    pros: list[str] = Field(min_length=1, max_length=8)
    cons: list[str] = Field(min_length=1, max_length=8)
    justification: str
    model: str
    createdAt: str
