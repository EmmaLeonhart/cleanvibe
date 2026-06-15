"""The classifier: assign a paper an arXiv-style category + cross-list.

A second LLM subsystem parallel to the reviewer (clawRxiv auto-classifies each paper).
One Gemma structured-output call returns a `Classification`, validated and constrained to
a fixed category set; we re-prompt once on failure and raise `ClassificationError` rather
than inventing a category.
"""

from __future__ import annotations

from pydantic import ValidationError

from .llm import LLMClient
from .schema import Classification, Paper

# A fixed arXiv-style category set the classifier must choose from.
ARXIV_CATEGORIES: list[str] = [
    "cs.AI", "cs.CL", "cs.LG", "cs.CV", "cs.NE", "cs.RO", "cs.CR", "cs.DC", "cs.DS",
    "cs.SE", "cs.IR", "cs.HC", "cs.MA", "cs.PL", "cs.SY", "stat.ML", "eess.AS",
    "eess.SP", "math.OC", "q-bio.NC",
]


class ClassificationError(Exception):
    """The model did not return a valid classification within the allowed attempts."""


def build_system_prompt() -> str:
    cats = ", ".join(ARXIV_CATEGORIES)
    return (
        "You classify research papers into arXiv-style categories. Choose the single best "
        "primary category and zero to three distinct cross-list categories, all drawn ONLY "
        f"from this set: {cats}. Do not invent categories outside the set.\n\n"
        'Return ONLY a JSON object with exactly these keys: "category" (one category string) '
        'and "cross_list" (an array of 0-3 other category strings).'
    )


def build_user_prompt(paper: Paper) -> str:
    tags = ", ".join(paper.tags) if paper.tags else "(none)"
    return f"Title: {paper.title}\n\nAbstract: {paper.abstract}\n\nTags: {tags}"


def classify_paper(paper: Paper, llm: LLMClient, max_attempts: int = 2) -> Classification:
    """Return a `Classification` for `paper`. Re-prompts once on invalid output; raises
    `ClassificationError` if no attempt yields a category in `ARXIV_CATEGORIES`."""
    system = build_system_prompt()
    base_user = build_user_prompt(paper)
    last_error = ""
    for attempt in range(max_attempts):
        user = base_user if attempt == 0 else (
            f"{base_user}\n\nYour previous response was invalid: {last_error}. "
            "Return only the JSON object with the allowed categories."
        )
        raw = llm.complete_json(system, user)
        if not isinstance(raw, dict):
            last_error = "response was not a JSON object"
            continue
        try:
            classification = Classification(**raw)
        except ValidationError as exc:
            last_error = "; ".join(e["msg"] for e in exc.errors()) or str(exc)
            continue
        if classification.category not in ARXIV_CATEGORIES:
            last_error = f"category {classification.category!r} not in the allowed set"
            continue
        # drop any cross-list entries outside the set or equal to the primary
        classification.cross_list = [
            c for c in classification.cross_list
            if c in ARXIV_CATEGORIES and c != classification.category
        ]
        return classification
    raise ClassificationError(
        f"no valid classification after {max_attempts} attempts: {last_error}")
