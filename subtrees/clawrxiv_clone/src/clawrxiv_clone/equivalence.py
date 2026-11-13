"""The revision-equivalence checker.

clawRxiv "verifies revisions represent the same body of work using AI." This is the third
LLM subsystem (after the reviewer and classifier): given an original paper and a revised
one, decide whether the revision is the same body of work (a legitimate revision) or a
substantially different paper. One Gemma structured-output call; re-prompt once on invalid
output; raise `EquivalenceError` rather than guessing.
"""

from __future__ import annotations

from pydantic import ValidationError

from .llm import LLMClient
from .schema import EquivalenceVerdict, Paper

_SYSTEM = (
    "You verify paper revisions. Given an ORIGINAL paper and a REVISED paper, decide whether "
    "the revision represents the SAME body of work as the original — a legitimate revision: the "
    "same core contribution, method, and results, even if reworded, reorganized, expanded, or "
    "corrected — versus a SUBSTANTIALLY DIFFERENT paper (different problem, method, or claims).\n\n"
    'Return ONLY a JSON object with exactly these keys: "equivalent" (boolean) and "reason" '
    "(one sentence explaining the decision)."
)


class EquivalenceError(Exception):
    """The model did not return a valid verdict within the allowed attempts."""


def _render(paper: Paper) -> str:
    return f"Title: {paper.title}\nAbstract: {paper.abstract}"


def build_user_prompt(original: Paper, revised: Paper) -> str:
    return f"ORIGINAL:\n{_render(original)}\n\nREVISED:\n{_render(revised)}"


def check_equivalence(original: Paper, revised: Paper, llm: LLMClient,
                      max_attempts: int = 2) -> EquivalenceVerdict:
    base_user = build_user_prompt(original, revised)
    last_error = ""
    for attempt in range(max_attempts):
        user = base_user if attempt == 0 else (
            f"{base_user}\n\nYour previous response was invalid: {last_error}. "
            'Return only the JSON object with "equivalent" (boolean) and "reason" (string).'
        )
        raw = llm.complete_json(_SYSTEM, user)
        if not isinstance(raw, dict):
            last_error = "response was not a JSON object"
            continue
        try:
            return EquivalenceVerdict(**raw)
        except ValidationError as exc:
            last_error = "; ".join(e["msg"] for e in exc.errors()) or str(exc)
    raise EquivalenceError(
        f"no valid verdict after {max_attempts} attempts: {last_error}")
