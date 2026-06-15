"""The reviewer: turn a paper into a clawRxiv-style structured review.

A single LLM call per paper (mirroring clawRxiv's single Gemini-3-Flash call), graded
against a rubric adapted from the LabClaw peer-review skill skeleton + clawRxiv's four
dimensions. The system prompt bakes in the **recent-papers** fix: because Gemma's
training cutoff predates much real work, it is explicitly told not to call post-cutoff
sources hallucinated (this is the exact failure mode we observed on clawRxiv, where real
2025-2026 references were flagged as fabricated).
"""

from __future__ import annotations

from datetime import datetime, timezone

from pydantic import ValidationError

from .llm import LLMClient
from .schema import Paper, Rating, Review

RATING_TIERS: list[str] = [r.value for r in Rating]

# The dimensions clawRxiv's skill doc says its reviewer scores on.
RUBRIC_DIMENSIONS = [
    ("Originality", "Is the contribution novel relative to prior work?"),
    ("Methodology", "Is the approach sound, with appropriate controls and analysis?"),
    ("Clarity", "Is the paper clearly written and well structured?"),
    ("Significance", "Does the result matter; is the claim supported by the evidence?"),
]

# The load-bearing instruction the user asked for: do not treat recent (post-cutoff)
# work as hallucinated.
RECENT_WORK_POLICY = (
    "RECENT WORK POLICY (important). Today's date is {now}. Your training data has a cutoff "
    "and you will NOT recognize much genuine work from 2025 onward (papers, models, datasets, "
    "results, arXiv IDs). You MUST NOT label a citation, model, dataset, or result as "
    "'hallucinated', 'fabricated', 'fake', or 'made up' merely because you do not recognize it "
    "or because it postdates your knowledge. Work dated after your cutoff is very likely real. "
    "If you cannot verify a specific claim, express calibrated uncertainty ('I could not verify X') "
    "rather than asserting it is fabricated. Only raise a hallucination concern when there is "
    "concrete internal evidence (a self-contradiction, an impossible value, or a claim the paper "
    "refutes itself)."
)


def build_system_prompt(now: str) -> str:
    """Assemble the reviewer system prompt for a given current date (YYYY-MM-DD)."""
    dims = "\n".join(f"  - {name}: {q}" for name, q in RUBRIC_DIMENSIONS)
    tiers = " / ".join(RATING_TIERS)
    return (
        "You are an AI peer reviewer for clawrxiv_clone, an open archive where AI agents "
        "publish research papers. Review the submitted paper rigorously but fairly.\n\n"
        "Score the paper on these dimensions:\n"
        f"{dims}\n\n"
        f"{RECENT_WORK_POLICY.format(now=now)}\n\n"
        "Be specific and constructive: cite concrete parts of the paper. Credit honestly-reported "
        "negative results rather than penalizing the paper for disclosing them.\n\n"
        "Return ONLY a JSON object with exactly these keys:\n"
        '  "rating": one of [' + tiers + "],\n"
        '  "summary": a one-paragraph synopsis of the paper,\n'
        '  "pros": an array of exactly 5 concise strengths,\n'
        '  "cons": an array of exactly 5 concise weaknesses,\n'
        '  "justification": a paragraph weighing the pros against the cons that leads to the rating,\n'
        '  "scores": an object mapping "originality", "methodology", "clarity", and "significance"\n'
        "           each to an integer from 1 (poor) to 5 (excellent), consistent with the rating.\n"
        "Do not include any text outside the JSON object."
    )


def build_user_prompt(paper: Paper) -> str:
    """The paper itself, as the user turn."""
    parts = [f"# {paper.title}", "", f"**Abstract.** {paper.abstract}"]
    if paper.tags:
        parts.append("**Tags:** " + ", ".join(paper.tags))
    if paper.content.strip():
        parts += ["", paper.content]
    return "\n".join(parts)


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


class ReviewError(Exception):
    """The model did not return a valid review within the allowed attempts."""


_CORRECTION = (
    "\n\nYour previous response was not a valid review: {error}\n"
    "Respond again with ONLY a JSON object containing exactly the keys rating, summary, "
    "pros, cons, justification, where rating is one of the listed tiers and pros and cons "
    "are arrays of strings."
)


def generate_review(paper: Paper, llm: LLMClient, now: str | None = None,
                    max_attempts: int = 2) -> Review:
    """Produce a structured Review for `paper` using `llm`.

    `now` is the full timestamp (used for `createdAt` and the recent-work policy date);
    defaults to the current UTC time. The model name and timestamp are stamped in if the
    model omits them. If the model returns output that does not validate against `Review`
    (Gemma is less reliable than Gemini at structured JSON), we re-prompt with the
    validation error as feedback, up to `max_attempts`; we never pad/trim to fake a valid
    review. Raises `ReviewError` if no attempt validates.
    """
    timestamp = now or _now_iso()
    review_date = timestamp.split(" ")[0]
    system = build_system_prompt(review_date)
    base_user = build_user_prompt(paper)
    last_error = ""
    for attempt in range(max_attempts):
        user = base_user if attempt == 0 else base_user + _CORRECTION.format(error=last_error)
        raw = llm.complete_json(system, user)
        if not isinstance(raw, dict):
            last_error = "response was not a JSON object"
            continue
        raw.setdefault("model", llm.name)
        raw.setdefault("createdAt", timestamp)
        try:
            return Review(**raw)
        except ValidationError as exc:
            last_error = "; ".join(e["msg"] for e in exc.errors()) or str(exc)
    raise ReviewError(
        f"model did not return a valid review after {max_attempts} attempts: {last_error}")
