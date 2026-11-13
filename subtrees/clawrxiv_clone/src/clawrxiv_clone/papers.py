"""Parse a markdown paper into a `Paper` (shared by the review/submit CLIs).

Convention: the first `# H1` is the title; the whole body (everything after the title line)
is the content. The abstract is the text of an `## Abstract` section when the paper has one
(any heading level from 2 down, any case), else the first blank-line-separated block after
the title. Papers with an author line above `## Abstract` (latent-space-cartography) would
otherwise hand the author line to the reviewer as the abstract.
"""

from __future__ import annotations

import re

from .schema import Paper

_ABSTRACT_HEADING = re.compile(r"^#{2,6}\s+abstract\s*:?\s*$", re.IGNORECASE | re.MULTILINE)
_ANY_HEADING = re.compile(r"^#{1,6}\s", re.MULTILINE)


def _abstract_section(body: str) -> str | None:
    """Text under an `## Abstract` heading, up to the next heading; None if absent/empty."""
    m = _ABSTRACT_HEADING.search(body)
    if not m:
        return None
    rest = body[m.end():]
    nxt = _ANY_HEADING.search(rest)
    text = (rest[: nxt.start()] if nxt else rest).strip()
    return text or None


def parse_markdown_paper(md: str) -> Paper:
    lines = md.splitlines()
    title = next((ln[2:].strip() for ln in lines if ln.startswith("# ")), "Untitled")
    body = md.split("\n", 1)[1] if md.startswith("# ") else md
    abstract = _abstract_section(body)
    if abstract is None:
        blocks = [b.strip() for b in body.split("\n\n") if b.strip()]
        abstract = blocks[0] if blocks else ""
    return Paper(title=title, abstract=abstract, content=body)
